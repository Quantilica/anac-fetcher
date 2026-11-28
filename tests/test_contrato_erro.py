"""Contrato de colunas que falha é erro do arquivo, não aviso com dado sem cast."""

from __future__ import annotations

from pathlib import Path

import pytest

pytest.importorskip("quantilica.analytics.lake")
pytest.importorskip("duckdb")
import polars as pl  # noqa: E402

from anac_fetcher.contracts import CONTRACTS  # noqa: E402
from anac_fetcher.lake import converter  # noqa: E402
from anac_fetcher.storage import _GROUP_DIRS  # noqa: E402
from anac_fetcher.wrangling import (  # noqa: E402
    ContractError,
    convert_group,
    convert_one,
)

COLUNAS_VRA = [f.name for f in CONTRACTS["vra"].fields]
BOM = ";".join(COLUNAS_VRA) + "\n" + ";".join(["1"] * len(COLUNAS_VRA)) + "\n"
RUIM = "Empresa;Numero do Voo\nLATAM;1234\n"


def _bruto(tmp_path: Path, conteudos: dict[str, str]) -> Path:
    raw = tmp_path / "raw"
    pasta = raw / _GROUP_DIRS["vra"]
    pasta.mkdir(parents=True)
    for nome, texto in conteudos.items():
        (pasta / nome).write_text(texto, encoding="utf-8")
    return raw


def test_convert_one_com_colunas_fora_do_contrato_levanta_e_nao_grava(
    tmp_path: Path,
) -> None:
    raw = _bruto(tmp_path, {"vra_2024-05@20240601.csv": RUIM})
    arquivo = raw / _GROUP_DIRS["vra"] / "vra_2024-05@20240601.csv"
    with pytest.raises(ContractError) as info:
        convert_one("vra", arquivo, tmp_path / "out")
    mensagem = str(info.value)
    assert "vra_2024-05@20240601.csv" in mensagem
    assert "colunas esperadas" in mensagem and "ICAO Empresa Aérea" in mensagem
    assert "colunas encontradas: ['Empresa', 'Numero do Voo']" in mensagem
    assert not list((tmp_path / "out").rglob("*.parquet"))


def test_convert_one_com_colunas_do_contrato_casta_e_grava(tmp_path: Path) -> None:
    raw = _bruto(tmp_path, {"vra_2024-05@20240601.csv": BOM})
    arquivo = raw / _GROUP_DIRS["vra"] / "vra_2024-05@20240601.csv"
    (alvo,) = convert_one("vra", arquivo, tmp_path / "out")
    frame = pl.read_parquet(alvo)
    assert set(frame.schema.values()) == {pl.Utf8}


def test_convert_group_converte_os_bons_e_levanta_no_fim(tmp_path: Path) -> None:
    raw = _bruto(
        tmp_path,
        {"vra_2024-05@20240601.csv": RUIM, "vra_2024-06@20240701.csv": BOM},
    )
    with pytest.raises(ContractError, match="1 arquivo"):
        convert_group(["vra"], raw, tmp_path / "out")
    assert [p.name for p in (tmp_path / "out").rglob("*.parquet")] == [
        "vra_2024-06@20240701.parquet"
    ]


def test_lake_contrato_que_falha_e_erro_no_convert_result(tmp_path: Path) -> None:
    raw = _bruto(
        tmp_path,
        {"vra_2024-05@20240601.csv": RUIM, "vra_2024-06@20240701.csv": BOM},
    )
    lake = tmp_path / "lake"
    result = converter.convert(raw, lake, datasets=["vra"])
    assert result.converted == 1
    assert len(result.errors) == 1
    erro = result.errors[0]
    assert "vra_2024-05@20240601.csv" in erro
    assert "colunas esperadas" in erro and "colunas encontradas" in erro
    assert "Numero do Voo" in erro
