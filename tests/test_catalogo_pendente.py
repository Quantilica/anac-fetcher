"""Catálogos que geram o período recente marcam ``pending_publication`` (sem rede)."""

from __future__ import annotations

import datetime as dt
from pathlib import Path

import httpx2
import pytest

from anac_fetcher import catalog_movimentacao as mov
from anac_fetcher import catalog_vra as vra

D = dt.date


def _vra(today: dt.date):
    return vra._vra_entries_list(today)


def _months(entries) -> list[tuple[int, int]]:
    return sorted({(e["year"], e["month"]) for e in entries})


@pytest.mark.parametrize(
    ("today", "ultimo"),
    [
        (D(2027, 1, 15), (2026, 11)),  # janeiro: não gera 2027-01
        (D(2027, 2, 3), (2026, 12)),  # fevereiro: não gera 2027-01/02
        (D(2027, 3, 1), (2027, 1)),
        (D(2026, 11, 28), (2026, 9)),
    ],
)
def test_vra_vai_ate_hoje_menos_a_defasagem_atravessando_o_ano(today, ultimo) -> None:
    meses = _months(_vra(today))
    assert meses[-1] == ultimo
    assert all(ym <= ultimo for ym in meses)


def test_vra_marca_so_os_dois_ultimos_meses_gerados() -> None:
    entries = _vra(D(2027, 1, 15))  # último mês gerado: 2026-11
    pendentes = {
        (e["year"], e["month"]) for e in entries if e.get("pending_publication")
    }
    assert pendentes == {(2026, 10), (2026, 11)}
    # csv e json do mesmo mês levam a marca
    por_mes = [e for e in entries if (e["year"], e["month"]) == (2026, 11)]
    assert {e["ext"] for e in por_mes} == {"csv", "json"}
    assert all(e["pending_publication"] for e in por_mes)
    antigos = [e for e in entries if (e["year"], e["month"]) < (2026, 10)]
    assert antigos and not any("pending_publication" in e for e in antigos)


def test_vra_mantem_as_lacunas_conhecidas_de_2014() -> None:
    meses = _months(_vra(D(2026, 11, 28)))
    assert (2014, 5) in meses and (2014, 8) in meses
    assert (2014, 6) not in meses and (2014, 7) not in meses


def test_movimentacao_gera_ate_o_mes_corrente_com_pendentes_depois_do_ultimo() -> None:
    entries = mov._movimentacao_entries_list(D(2026, 11, 28))
    meses = [(e["year"], e["month"]) for e in entries]
    assert meses[0] == (2019, 3)
    assert meses[-1] == (2026, 11)
    assert len(meses) == len(set(meses))
    pendentes = [
        (e["year"], e["month"]) for e in entries if e.get("pending_publication")
    ]
    assert pendentes == [(2026, m) for m in range(1, 12)]
    firmes = [ym for ym in meses if ym <= mov.LAST_PUBLISHED]
    assert firmes[-1] == (2025, 12)
    assert not any(
        "pending_publication" in e
        for e in entries
        if (e["year"], e["month"]) <= (2025, 12)
    )


def test_movimentacao_com_hoje_dentro_do_publicado_nao_gera_alem_de_hoje() -> None:
    entries = mov._movimentacao_entries_list(D(2025, 6, 10))
    assert (entries[-1]["year"], entries[-1]["month"]) == (2025, 6)
    assert not any(e.get("pending_publication") for e in entries)


def test_catalogo_do_modulo_traz_a_marca_no_proximo_mes_ainda_inexistente() -> None:
    hoje = dt.date.today()
    entries = mov._movimentacao_entries_list()
    ultimo = entries[-1]
    assert (ultimo["year"], ultimo["month"]) == max(
        mov.LAST_PUBLISHED, (hoje.year, hoje.month)
    )


def test_host_trata_404_de_entrada_pendente_como_pulada(tmp_path: Path) -> None:
    sdk = pytest.importorskip("quantilica.cli.sdk")
    if not hasattr(sdk, "PENDING_PUBLICATION_KEY"):
        pytest.skip("host sem pending_publication (quantilica-cli < 0.30.0)")
    from quantilica.core.http import HttpClient

    from anac_fetcher.catalog import GROUPS, list_datasets
    from anac_fetcher.plugin import fetcher

    entries = mov._movimentacao_entries_list(D(2026, 11, 28))
    pendente = next(e for e in entries if (e["year"], e["month"]) == (2026, 3))
    firme = next(e for e in entries if (e["year"], e["month"]) == (2025, 12))
    assert GROUPS and list_datasets
    client = HttpClient(
        transport=httpx2.MockTransport(lambda request: httpx2.Response(404)),
        attempts=1,
        retry_base_delay=0,
    )
    fetcher.client = client
    _, _, errors = fetcher.download_datasets([dict(pendente)], tmp_path, workers=1)
    assert errors == []
    stats = fetcher.last_download_stats
    assert stats is not None
    assert stats.skipped_items == [(pendente["id"], "pending-publication")]
    # a mesma 404 numa entrada firme continua erro
    _, _, errors = fetcher.download_datasets([dict(firme)], tmp_path, workers=1)
    assert [eid for eid, _ in errors] == [firme["id"]]
