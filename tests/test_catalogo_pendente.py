"""Catálogos que geram o período recente marcam ``pending_publication`` (sem rede)."""

from __future__ import annotations

import datetime as dt
from pathlib import Path

import httpx2
import pytest

from anac_fetcher import catalog_atrasos as atrasos
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


def _atrasos(today: dt.date):
    return atrasos._atrasos_entries_list(today)


@pytest.mark.parametrize(
    ("today", "ultimo"),
    [
        (D(2027, 1, 15), (2026, 11)),  # janeiro: não gera 2027-01
        (D(2027, 2, 3), (2026, 12)),  # fevereiro: não gera 2027-01/02
        (D(2027, 3, 1), (2027, 1)),
        (D(2026, 11, 28), (2026, 9)),
    ],
)
def test_atrasos_vai_ate_hoje_menos_a_defasagem_atravessando_o_ano(
    today, ultimo
) -> None:
    meses = _months(_atrasos(today))
    assert meses[-1] == ultimo
    assert all(ym <= ultimo for ym in meses)


def test_atrasos_marca_so_os_dois_ultimos_meses_e_mantem_a_lacuna_de_2014() -> None:
    entries = _atrasos(D(2027, 1, 15))  # último mês gerado: 2026-11
    pendentes = {
        (e["year"], e["month"]) for e in entries if e.get("pending_publication")
    }
    assert pendentes == {(2026, 10), (2026, 11)}
    assert all(
        e["pending_publication"]
        for e in entries
        if (e["year"], e["month"]) == (2026, 11)
    )
    meses = _months(entries)
    assert (2014, 5) in meses and (2014, 8) in meses
    assert (2014, 6) not in meses and (2014, 7) not in meses


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
    assert pendentes == [(2026, m) for m in range(6, 12)]
    firmes = [ym for ym in meses if ym <= mov.LAST_PUBLISHED]
    assert firmes[-1] == (2026, 5)
    assert not any(
        "pending_publication" in e
        for e in entries
        if (e["year"], e["month"]) <= mov.LAST_PUBLISHED
    )


def _pendentes_mov(today: dt.date) -> list[tuple[int, int]]:
    return [
        (e["year"], e["month"])
        for e in mov._movimentacao_entries_list(today)
        if e.get("pending_publication")
    ]


def test_movimentacao_folga_acaba_no_limite_e_o_404_volta_a_ser_erro() -> None:
    assert mov.PENDING_MAX_MONTHS == 18
    # 2026-06 tem 18 meses em 2027-12: ainda pendente
    assert _pendentes_mov(D(2027, 12, 15))[0] == (2026, 6)
    # um mês depois ele tem 19: a marca cai e o 404 passa a ser erro
    depois = _pendentes_mov(D(2028, 1, 1))
    assert depois[0] == (2026, 7)
    assert (2026, 6) not in depois
    entries = mov._movimentacao_entries_list(D(2028, 1, 1))
    junho = next(e for e in entries if (e["year"], e["month"]) == (2026, 6))
    assert "pending_publication" not in junho
    # a janela anda: sempre PENDING_MAX_MONTHS + 1 meses até o corrente
    assert len(depois) == mov.PENDING_MAX_MONTHS + 1


def test_movimentacao_virada_do_ano_nao_gera_mes_inexistente() -> None:
    for hoje, ultimo in [
        (D(2026, 12, 31), (2026, 12)),
        (D(2027, 1, 1), (2027, 1)),
        (D(2027, 1, 31), (2027, 1)),
    ]:
        entries = mov._movimentacao_entries_list(hoje)
        meses = [(e["year"], e["month"]) for e in entries]
        assert meses[-1] == ultimo
        assert len(meses) == len(set(meses))
        assert all(1 <= m <= 12 for _, m in meses)
    # a contagem da folga atravessa o ano: em 2027-01, 2026-06 tem 7 meses
    assert _pendentes_mov(D(2027, 1, 10)) == [
        *[(2026, m) for m in range(6, 13)],
        (2027, 1),
    ]


def test_movimentacao_com_constante_atrasada_so_os_meses_velhos_viram_erro() -> None:
    """Se ninguém subir ``LAST_PUBLISHED`` por mais de 18 meses, a fonte sem
    publicar aparece como erro, não como 'pendente' para sempre."""
    entries = mov._movimentacao_entries_list(D(2028, 7, 10))
    sem_marca = [
        (e["year"], e["month"])
        for e in entries
        if (e["year"], e["month"]) > mov.LAST_PUBLISHED
        and not e.get("pending_publication")
    ]
    assert sem_marca[0] == (2026, 6)
    assert sem_marca[-1] == (2026, 12)  # 2027-01 tem 18 meses: ainda na janela


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
    pendente = next(e for e in entries if (e["year"], e["month"]) == (2026, 8))
    firme = next(e for e in entries if (e["year"], e["month"]) == (2026, 5))
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
