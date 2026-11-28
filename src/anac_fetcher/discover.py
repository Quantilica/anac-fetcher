"""Descoberta de meses novos da Movimentação Aeroportuária frente ao catálogo.

O servidor da ANAC é um índice de diretório (``{ano}/`` com
``Movimentacoes_Aeroportuarias_{YYYYMM}.csv``). Esta rotina lê o índice raiz e o
dos anos a partir do último confirmado e informa os meses publicados que o
catálogo NÃO coleta. O catálogo gera os meses depois de
:data:`anac_fetcher.catalog_movimentacao.LAST_PUBLISHED` até o mês corrente
(marcados ``pending_publication``), então um mês novo dentro dessa janela já é
coletado e não é achado; ele aparece só em ``ahead_of_confirmed``, como lembrete
de subir a constante.
"""

from __future__ import annotations

import datetime as dt
import re
from collections.abc import Callable
from dataclasses import asdict, dataclass, field
from typing import Any

from .catalog_movimentacao import _BASE, LAST_PUBLISHED, _movimentacao_entries_list

__all__ = ["DiscoverReport", "discover", "parse_months", "parse_years"]

_YEAR_RE = re.compile(r'href="(\d{4})/"')
_MONTH_RE = re.compile(r'href="Movimentacoes_Aeroportuarias_(\d{4})(\d{2})\.csv"')


def parse_years(html: str) -> list[int]:
    """Anos (subdiretórios) listados no índice raiz."""
    return sorted({int(y) for y in _YEAR_RE.findall(html)})


def parse_months(html: str) -> list[tuple[int, int]]:
    """Pares ``(ano, mês)`` dos CSV listados no índice de um ano."""
    return sorted({(int(y), int(m)) for y, m in _MONTH_RE.findall(html)})


@dataclass
class DiscoverReport:
    """Resultado de :func:`discover`."""

    last_published_catalog: str = ""
    new_months: list[str] = field(default_factory=list)
    ahead_of_confirmed: list[str] = field(default_factory=list)

    @property
    def has_changes(self) -> bool:
        """Há meses publicados que o catálogo não coleta (``new_months``)."""
        return bool(self.new_months)

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
        pendentes (só informativo, não conta como novidade).
    """
    last_year, last_month = LAST_PUBLISHED
    report = DiscoverReport(last_published_catalog=f"{last_year}-{last_month:02d}")
    root = fetch(f"{_BASE}/")
    if root is None:
        raise RuntimeError("Índice da Movimentação Aeroportuária não encontrado.")
    found: set[tuple[int, int]] = set()
    for year in parse_years(root):
        if year < last_year:
            continue
        html = fetch(f"{_BASE}/{year}/")
        if html is not None:
            found.update(parse_months(html))
    covered = {(e["year"], e["month"]) for e in _movimentacao_entries_list(today)}
    report.new_months = [f"{y}-{m:02d}" for y, m in sorted(found - covered)]
    report.ahead_of_confirmed = [
        f"{y}-{m:02d}" for y, m in sorted(found & covered) if (y, m) > LAST_PUBLISHED
    ]
    return report
