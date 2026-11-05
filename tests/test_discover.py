"""Testes do catálogo de movimentação limitado ao publicado e do ``discover``."""

from __future__ import annotations

from anac_fetcher.catalog import list_datasets
from anac_fetcher.catalog_movimentacao import _BASE, LAST_PUBLISHED
from anac_fetcher.discover import discover, parse_months, parse_years

ROOT_HTML = '<a href="../">../</a><a href="2025/">2025/</a><a href="2026/">2026/</a>'


def _month_html(*yyyymm: str) -> str:
    return "".join(
        f'<a href="Movimentacoes_Aeroportuarias_{m}.csv">x</a>'
        f'<a href="Movimentacoes_Aeroportuarias_{m}.json">x</a>'
        for m in yyyymm
    )


def test_catalogo_nao_gera_meses_alem_do_publicado() -> None:
    ids = [
        e["id"] if isinstance(e, dict) else e.id
        for e in list_datasets("movimentacao-aeroportuaria")
    ]
    assert ids[-1] == "movimentacao-2025-12-csv"
    assert not any("-2026-" in i for i in ids)
    assert LAST_PUBLISHED == (2025, 12)


def test_parse_indices() -> None:
    assert parse_years(ROOT_HTML) == [2025, 2026]
    assert parse_months(_month_html("202511", "202512")) == [(2025, 11), (2025, 12)]


def test_discover_sem_novidades_quando_2026_nao_existe() -> None:
    pages = {
        f"{_BASE}/": ROOT_HTML.replace('<a href="2026/">2026/</a>', ""),
        f"{_BASE}/2025/": _month_html("202511", "202512"),
    }
    report = discover(lambda url: pages.get(url))
    assert not report.has_changes


def test_discover_detecta_mes_novo() -> None:
    pages = {
        f"{_BASE}/": ROOT_HTML,
        f"{_BASE}/2025/": _month_html("202512"),
        f"{_BASE}/2026/": _month_html("202601", "202602"),
    }
    report = discover(lambda url: pages.get(url))
    assert report.new_months == ["2026-01", "2026-02"]
    assert report.has_changes
