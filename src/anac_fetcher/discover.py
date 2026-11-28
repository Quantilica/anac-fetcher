"""Descoberta de meses novos da Movimentação Aeroportuária frente ao catálogo.

O servidor da ANAC é um índice de diretório (``{ano}/`` com
``Movimentacoes_Aeroportuarias_{YYYYMM}.csv``). Esta rotina lê o índice raiz e o
dos anos a partir do último confirmado e informa os meses publicados que o
catálogo NÃO coleta. O catálogo gera os meses depois de
:data:`anac_fetcher.catalog_movimentacao.LAST_PUBLISHED` até o mês corrente
(marcados ``pending_publication``), então um mês novo dentro dessa janela já é
coletado e não é achado; ele aparece só em ``ahead_of_confirmed``, como lembrete
de subir a constante.

O ponto cego do catálogo é o arquivo publicado com nome fora do padrão (``_v2``,
``.zip``, arquivo anual, outro diretório): o ``sync`` só tenta o nome esperado e
tolera o 404 dos pendentes. Todo link dos índices que não é o CSV mensal, o JSON
mensal (ignorado de propósito), o link para o diretório pai, a ordenação do
índice ou um extra já conhecido vai para ``unclassified`` e conta em
``has_changes``.
"""

from __future__ import annotations

import datetime as dt
import html as html_lib
import re
from collections.abc import Callable
from dataclasses import asdict, dataclass, field
from typing import Any

from .catalog_movimentacao import _BASE, LAST_PUBLISHED, _movimentacao_entries_list

__all__ = [
    "DiscoverReport",
    "discover",
    "parse_months",
    "parse_unclassified",
    "parse_years",
]

_YEAR_RE = re.compile(r'href="(\d{4})/"')
_MONTH_RE = re.compile(r'href="Movimentacoes_Aeroportuarias_(\d{4})(\d{2})\.csv"')
_HREF_RE = re.compile(r'href="([^"]*)"')
# Padrões conhecidos de um índice: o link para o diretório pai, a ordenação do
# índice (``?C=N;O=D``), o CSV e o JSON mensais (o catálogo só coleta o CSV).
_KNOWN_YEAR_DIR_RE = re.compile(r"\d{4}/")
_KNOWN_MONTH_FILE_RE = re.compile(r"Movimentacoes_Aeroportuarias_\d{6}\.(csv|json)")
# Arquivos fixos que já existem na fonte e que o catálogo não coleta de propósito
# (conferido em 2026-11-28). ``201912.csv.csv`` é uma cópia de 2019-12 publicada
# em 2023 com nome duplicado; o catálogo coleta o ``201912.csv``.
_KNOWN_EXTRAS = frozenset({"2019/Movimentacoes_Aeroportuarias_201912.csv.csv"})


def parse_years(html: str) -> list[int]:
    """Anos (subdiretórios) listados no índice raiz."""
    return sorted({int(y) for y in _YEAR_RE.findall(html)})


def parse_months(html: str) -> list[tuple[int, int]]:
    """Pares ``(ano, mês)`` dos CSV listados no índice de um ano."""
    return sorted({(int(y), int(m)) for y, m in _MONTH_RE.findall(html)})


def parse_unclassified(html: str, year: int | None = None) -> list[str]:
    """Links de um índice que não casam com nenhum padrão conhecido.

    Args:
        html: Índice do diretório.
        year: Ano do índice de ano (prefixa o nome no resultado e na lista de
            extras conhecidos); ``None`` para o índice raiz, onde só os
            subdiretórios de ano são conhecidos.

    Returns:
        Os links, ordenados e sem repetição (``AAAA/nome`` num índice de ano).
    """
    known = _KNOWN_YEAR_DIR_RE if year is None else _KNOWN_MONTH_FILE_RE
    found: set[str] = set()
    for raw in _HREF_RE.findall(html):
        href = html_lib.unescape(raw).strip()
        if href in ("", "../", "./", "/") or href.startswith(("?", "#")):
            continue
        if known.fullmatch(href):
            continue
        name = href if year is None else f"{year}/{href}"
        if name in _KNOWN_EXTRAS:
            continue
        found.add(name)
    return sorted(found)


@dataclass
class DiscoverReport:
    """Resultado de :func:`discover`."""

    last_published_catalog: str = ""
    new_months: list[str] = field(default_factory=list)
    ahead_of_confirmed: list[str] = field(default_factory=list)
    unclassified: list[str] = field(default_factory=list)

    @property
    def has_changes(self) -> bool:
        """Há mês que o catálogo não coleta ou arquivo de nome desconhecido."""
        return bool(self.new_months or self.unclassified)

    def to_dict(self) -> dict[str, Any]:
        """Converte o relatório em dict serializável."""
        data = asdict(self)
        data["has_changes"] = self.has_changes
        return data


def _fetch_index(url: str) -> str | None:
    """GET do índice; ``None`` quando o diretório não existe (404)."""
    from quantilica.core.http import HttpClient, HttpStatusError

    with HttpClient(timeout=30.0, emulate_browser=True) as client:
        try:
            return client.get(url).text
        except HttpStatusError as exc:
            if exc.status_code == 404:
                return None
            raise


def discover(
    fetch: Callable[[str], str | None] = _fetch_index,
    today: dt.date | None = None,
) -> DiscoverReport:
    """Compara o índice da ANAC com o que o catálogo coleta.

    Args:
        fetch: Função ``url -> html | None`` (``None`` = 404); injetável em testes.
        today: Data de referência do catálogo (testes); padrão hoje.

    Returns:
        DiscoverReport: ``new_months`` traz os meses ``AAAA-MM`` publicados que o
        catálogo não gera (fora da janela até o mês corrente); ``ahead_of_confirmed``,
        os publicados depois de ``LAST_PUBLISHED`` que o catálogo já coleta como
        pendentes (só informativo, não conta como novidade); ``unclassified``, os
        links dos índices fora de todo padrão conhecido (nome estranho, arquivo
        anual, subdiretório), que contam como novidade.
    """
    last_year, last_month = LAST_PUBLISHED
    report = DiscoverReport(last_published_catalog=f"{last_year}-{last_month:02d}")
    root = fetch(f"{_BASE}/")
    if root is None:
        raise RuntimeError("Índice da Movimentação Aeroportuária não encontrado.")
    found: set[tuple[int, int]] = set()
    strange = set(parse_unclassified(root))
    # Todos os anos, não só os recentes: um arquivo de nome estranho num ano
    # antigo também é publicação que o catálogo não coleta.
    for year in parse_years(root):
        html = fetch(f"{_BASE}/{year}/")
        if html is not None:
            found.update(parse_months(html))
            strange.update(parse_unclassified(html, year))
    report.unclassified = sorted(strange)
    covered = {(e["year"], e["month"]) for e in _movimentacao_entries_list(today)}
    report.new_months = [f"{y}-{m:02d}" for y, m in sorted(found - covered)]
    report.ahead_of_confirmed = [
        f"{y}-{m:02d}" for y, m in sorted(found & covered) if (y, m) > LAST_PUBLISHED
    ]
    return report
