"""Linhas cortadas pela leitura tolerante: aviso até 1%, erro do arquivo acima."""

from __future__ import annotations

from pathlib import Path

import pytest

pytest.importorskip("quantilica.analytics.lake")
pytest.importorskip("duckdb")
from anac_fetcher.lake import converter  # noqa: E402
from anac_fetcher.storage import _GROUP_DIRS  # noqa: E402


def _bruto(tmp_path: Path, nome: str, texto: str) -> Path:
    raw = tmp_path / "raw"
    pasta = raw / _GROUP_DIRS["vra"]
    pasta.mkdir(parents=True)
    (pasta / nome).write_text(texto, encoding="utf-8")
    return raw


@pytest.mark.usefixtures("sem_contratos")
def test_poucas_linhas_cortadas_convertem_com_aviso(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    raw = _bruto(tmp_path, "vra_2024-05@20240601.csv", "a;b\n1;2;3\n" + "7;8\n" * 299)
    with caplog.at_level("WARNING", logger="anac_fetcher.reader"):
        result = converter.convert(raw, tmp_path / "lake", datasets=["vra"])
    assert (result.converted, result.errors) == (1, [])
    assert any("1 de 300 linhas" in r.getMessage() for r in caplog.records)


def test_muitas_linhas_cortadas_viram_erro_do_arquivo(tmp_path: Path) -> None:
    raw = _bruto(
        tmp_path, "vra_2024-05@20240601.csv", "a;b\n" + "1;2;3\n" * 5 + "7;8\n" * 95
    )
    result = converter.convert(raw, tmp_path / "lake", datasets=["vra"])
    assert result.converted == 0
    assert len(result.errors) == 1
    assert "5 de 100 linhas" in result.errors[0]
    assert "vra_2024-05@20240601.csv" in result.errors[0]
