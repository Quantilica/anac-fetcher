"""Aviso de período pendente sem publicação há meses (sync e check)."""

from __future__ import annotations

import datetime as dt
import logging
from pathlib import Path

import httpx2
import pytest

from anac_fetcher import catalog_movimentacao as mov
from anac_fetcher.pending import PENDING_WARN_MONTHS, stale_pending_message

D = dt.date


def _pend(year: int, month: int, group: str = "movimentacao-aeroportuaria") -> dict:
    return {"group": group, "year": year, "month": month, "pending_publication": True}


def test_aviso_vem_antes_da_folga_do_catalogo_acabar() -> None:
    assert PENDING_WARN_MONTHS == 10
    assert PENDING_WARN_MONTHS < mov.PENDING_MAX_MONTHS


def test_sem_aviso_ate_dez_meses() -> None:
    # 2026-01 a 2026-11: 10 meses
    assert stale_pending_message([_pend(2026, 1)], D(2026, 11, 28)) is None
    assert stale_pending_message([], D(2026, 11, 28)) is None


def test_aviso_acima_de_dez_meses_diz_desde_quando() -> None:
    msg = stale_pending_message(
        [_pend(2026, 1), _pend(2025, 12), _pend(2026, 2)], D(2026, 11, 28)
    )
    assert msg is not None
    assert "movimentacao-aeroportuaria" in msg
    assert "desde 2025-12 (11 meses)" in msg
    assert "2026-05" in msg  # último confirmado
    assert "discover" in msg


def test_grupo_recente_nao_avisa_e_uma_linha_so() -> None:
    msg = stale_pending_message(
        [_pend(2025, 12), _pend(2026, 9, "vra")], D(2026, 11, 28)
    )
    assert msg is not None and msg.count("sem publicação desde") == 1
    assert "vra" not in msg


def _app_404():
    pytest.importorskip("quantilica.cli.sdk")
    from quantilica.core.http import HttpClient

    from anac_fetcher.plugin import AnacFetcherApp

    sdk = pytest.importorskip("quantilica.cli.sdk")
    if not hasattr(sdk, "PENDING_PUBLICATION_KEY"):
        pytest.skip("host sem pending_publication")
    from anac_fetcher.catalog import GROUP_ALIASES, GROUPS, list_datasets

    client = HttpClient(
        transport=httpx2.MockTransport(lambda request: httpx2.Response(404)),
        attempts=1,
        retry_base_delay=0,
    )
    return AnacFetcherApp(
        name="anac-fetcher",
        groups_dict=GROUPS,
        aliases_dict={alias: [canon] for alias, canon in GROUP_ALIASES.items()},
        list_datasets=list_datasets,
        path_builder=lambda out, entry, lm: out / (entry["id"] + ".csv"),
        client=client,
    )


# 2027-05: o pendente mais antigo (2026-06) tem 11 meses, acima do limite do aviso.
HOJE = D(2027, 5, 15)


@pytest.fixture(autouse=True)
def _hoje_fixo(monkeypatch: pytest.MonkeyPatch) -> None:
    from anac_fetcher import plugin

    monkeypatch.setattr(
        plugin,
        "stale_pending_message",
        lambda entries: stale_pending_message(entries, HOJE),
    )


def _pendentes() -> list[dict]:
    entries = mov._movimentacao_entries_list(HOJE)
    return [dict(e) for e in entries if e.get("pending_publication")]


def test_sync_com_pendentes_em_404_avisa_uma_vez(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    app = _app_404()
    entries = _pendentes()
    assert len(entries) > 1
    with caplog.at_level(logging.WARNING, logger="anac_fetcher.plugin"):
        _, _, errors = app.download_datasets(entries, tmp_path, workers=2)
    assert errors == []  # o código de saída não muda
    avisos = [r for r in caplog.records if "sem publicação desde" in r.getMessage()]
    assert len(avisos) == 1
    assert "desde 2026-06 (11 meses)" in avisos[0].getMessage()


def test_check_no_modo_de_plano_tambem_avisa_uma_vez(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    app = _app_404()
    with caplog.at_level(logging.WARNING, logger="anac_fetcher.plugin"):
        plan = app.check_datasets(_pendentes(), tmp_path, workers=2)
    assert {i.reason for i in plan.items} == {"pending-publication"}
    avisos = [r for r in caplog.records if "sem publicação desde" in r.getMessage()]
    assert len(avisos) == 1
