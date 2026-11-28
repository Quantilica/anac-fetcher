"""Testes do catálogo de movimentação limitado ao publicado e do ``discover``."""

from __future__ import annotations

import datetime as dt

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


HOJE = dt.date(2026, 11, 28)


def test_catalogo_confirma_ate_2026_05_e_o_resto_e_pendente() -> None:
    """Depois de ``LAST_PUBLISHED`` só entram meses pendentes (404 tolerado)."""
    entries = list_datasets("movimentacao-aeroportuaria")
    firmes = [e for e in entries if not e.get("pending_publication")]
    assert (
        firmes[-1]["id"]
        == f"movimentacao-{LAST_PUBLISHED[0]}-{LAST_PUBLISHED[1]:02d}-csv"
    )
    depois = [e for e in entries if (e["year"], e["month"]) > LAST_PUBLISHED]
    assert all(e["pending_publication"] for e in depois)
    assert LAST_PUBLISHED == (2026, 5)


def test_parse_indices() -> None:
    assert parse_years(ROOT_HTML) == [2025, 2026]
    assert parse_months(_month_html("202511", "202512")) == [(2025, 11), (2025, 12)]


def test_discover_sem_novidades_quando_o_catalogo_cobre_o_que_a_fonte_tem() -> None:
    """A fonte de 2026-11-28: de 2026-01 a 2026-05, exatamente o catálogo."""
    pages = {
        f"{_BASE}/": ROOT_HTML,
        f"{_BASE}/2025/": _month_html("202511", "202512"),
        f"{_BASE}/2026/": _month_html(*(f"2026{m:02d}" for m in range(1, 6))),
    }
    report = discover(lambda url: pages.get(url), today=HOJE)
    assert not report.has_changes
    assert report.new_months == []
    assert report.ahead_of_confirmed == []


def test_discover_mes_novo_dentro_da_janela_ja_e_coletado_e_nao_e_achado() -> None:
    """2026-06 e 2026-07 são pendentes no catálogo: já entram na coleta."""
    pages = {
        f"{_BASE}/": ROOT_HTML,
        f"{_BASE}/2026/": _month_html("202605", "202606", "202607"),
    }
    report = discover(lambda url: pages.get(url), today=HOJE)
    assert not report.has_changes
    assert report.ahead_of_confirmed == ["2026-06", "2026-07"]


def test_discover_acha_o_que_o_catalogo_nao_gera() -> None:
    """Mês fora da janela (futuro, ou antes do início do catálogo) é achado."""
    pages = {
        f"{_BASE}/": ROOT_HTML + '<a href="2027/">2027/</a>',
        f"{_BASE}/2026/": _month_html("202605", "202612"),
        f"{_BASE}/2027/": _month_html("202701"),
    }
    report = discover(lambda url: pages.get(url), today=HOJE)
    assert report.new_months == ["2026-12", "2027-01"]
    assert report.has_changes


def test_discover_na_virada_do_ano_o_mes_publicado_entra_na_janela() -> None:
    pages = {
        f"{_BASE}/": ROOT_HTML + '<a href="2027/">2027/</a>',
        f"{_BASE}/2026/": _month_html("202605", "202612"),
        f"{_BASE}/2027/": _month_html("202701"),
    }
    report = discover(lambda url: pages.get(url), today=dt.date(2027, 1, 20))
    assert report.new_months == []
    assert report.ahead_of_confirmed == ["2026-12", "2027-01"]


def _run_discover(monkeypatch, capsys, args: list[str]):
    """Executa o comando ``discover`` com a rede substituída por um relatório fixo."""
    from typer.testing import CliRunner

    from anac_fetcher import discover as discover_module
    from anac_fetcher.plugin import app

    report = discover_module.DiscoverReport(
        last_published_catalog="2026-05",
        new_months=["2026-01"],
        ahead_of_confirmed=["2026-06"],
    )
    monkeypatch.setattr(discover_module, "discover", lambda *a, **k: report)
    return CliRunner().invoke(app, ["discover", *args])


def test_comando_discover_json_e_json_puro(monkeypatch, capsys) -> None:
    import json

    result = _run_discover(monkeypatch, capsys, ["--json"])
    assert result.exit_code == 0
    data = json.loads(result.stdout)
    assert data["new_months"] == ["2026-01"]


def test_comando_discover_texto_preserva_mensagens(monkeypatch, capsys) -> None:
    result = _run_discover(monkeypatch, capsys, [])
    assert "Catálogo vai até 2026-05." in result.stdout
    assert "Já coletados como pendentes (suba LAST_PUBLISHED): 2026-06" in result.stdout
    assert "NOVO     movimentacao-2026-01" in result.stdout


def test_comando_discover_fail_on_change(monkeypatch, capsys) -> None:
    result = _run_discover(monkeypatch, capsys, ["--fail-on-change"])
    assert result.exit_code == 1
