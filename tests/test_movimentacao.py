"""Movimentação aeroportuária: CSV com e sem a linha "Atualizado em" no topo.

Os arquivos antigos da ANAC trazem o preâmbulo (com BOM) e o cabeçalho na segunda
linha, entre aspas; os novos começam direto pelo cabeçalho (também com BOM), sem
aspas e com outra ordem de colunas. As fixtures são recortes de 10 linhas dos dois.
"""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest

pytest.importorskip("quantilica.analytics.lake")
pytest.importorskip("duckdb")

import duckdb  # noqa: E402
import polars as pl  # noqa: E402
from quantilica.analytics.lake import check_dataset  # noqa: E402

from anac_fetcher.lake import converter  # noqa: E402
from anac_fetcher.reader import _preamble_rows, read_csv  # noqa: E402
from anac_fetcher.storage import _GROUP_DIRS  # noqa: E402

FIXTURES = Path(__file__).parent / "fixtures"
COM = FIXTURES / "movimentacao_2022-06_com_preambulo.csv"
SEM = FIXTURES / "movimentacao_2022-07_sem_preambulo.csv"
GROUP = "movimentacao-aeroportuaria"

COLUMNS = {
    "ANO",
    "MES",
    "NR_AEROPORTO_REFERENCIA",
    "NR_MOVIMENTO_TIPO",
    "NR_AERONAVE_MARCAS",
    "NR_AERONAVE_TIPO",
    "NR_AERONAVE_OPERADOR",
    "NR_VOO_OUTRO_AEROPORTO",
    "NR_VOO_NUMERO",
    "NR_SERVICE_TYPE",
    "NR_NATUREZA",
    "DT_PREVISTO",
    "HH_PREVISTO",
    "DT_CALCO",
    "HH_CALCO",
    "DT_TOQUE",
    "HH_TOQUE",
    "NR_CABECEIRA",
    "NR_BOX",
    "NR_PONTE_CONECTOR_REMOTO",
    "NR_TERMINAL",
    "QT_PAX_LOCAL",
    "QT_PAX_CONEXAO_DOMESTICO",
    "QT_PAX_CONEXAO_INTERNACIONAL",
    "QT_CORREIO",
    "QT_CARGA",
}


def test_preamble_rows_counts_only_atualizado_em() -> None:
    assert _preamble_rows(COM) == 1
    # O BOM sozinho, no cabeçalho, não é preâmbulo.
    assert _preamble_rows(SEM) == 0


@pytest.mark.parametrize("path", [COM, SEM], ids=["com_preambulo", "sem_preambulo"])
def test_read_csv_header_is_the_real_header(path: Path) -> None:
    df = read_csv(path, {})
    assert set(df.columns) == COLUMNS
    assert df.height == 10


def test_both_formats_same_schema_and_values_by_column() -> None:
    com = read_csv(COM, {})
    sem = read_csv(SEM, {})
    assert set(com.columns) == set(sem.columns)
    assert com.schema == {c: sem.schema[c] for c in com.columns}

    first_com = com.row(0, named=True)
    assert first_com["ANO"] == "2022"
    assert first_com["MES"] == "6"
    assert first_com["NR_AEROPORTO_REFERENCIA"] == "SBAR"
    assert first_com["NR_MOVIMENTO_TIPO"] == "D"
    assert first_com["NR_AERONAVE_MARCAS"] == "PRLCV"
    assert first_com["DT_TOQUE"] == "2022-06-02"
    assert first_com["QT_PAX_LOCAL"] == "0"

    first_sem = sem.row(0, named=True)
    assert first_sem["ANO"] == "2022"
    assert first_sem["MES"] == "7"
    assert first_sem["NR_AEROPORTO_REFERENCIA"] == "SBRD"
    assert first_sem["NR_MOVIMENTO_TIPO"] == "P"
    assert first_sem["NR_AERONAVE_MARCAS"] == "PRAUE"
    assert first_sem["NR_VOO_NUMERO"] == "4388"
    assert first_sem["QT_PAX_LOCAL"] == "81"
    assert first_sem["QT_CARGA"] == "227"
    # Colunas que mudam de posição entre os formatos seguem o nome, não a posição.
    assert first_sem["NR_BOX"] == "B1"
    assert first_sem["NR_PONTE_CONECTOR_REMOTO"] == "3"
    assert first_sem["QT_PAX_CONEXAO_INTERNACIONAL"] == "0"
    assert first_sem["NR_CABECEIRA"] == "02"
    last_com = com.row(9, named=True)
    assert last_com["NR_BOX"] == "T2"
    assert last_com["NR_TERMINAL"] == "1"
    assert last_com["QT_PAX_LOCAL"] == "149"
    assert last_com["QT_PAX_CONEXAO_DOMESTICO"] == "4"
    assert last_com["QT_CARGA"] == "345"


def test_convert_lake_is_readable_with_hive_partitions(tmp_path: Path) -> None:
    raw = tmp_path / "raw" / _GROUP_DIRS[GROUP]
    raw.mkdir(parents=True)
    shutil.copy(COM, raw / "movimentacao-aeroportuaria_2022-06@20240116.csv")
    shutil.copy(SEM, raw / "movimentacao-aeroportuaria_2022-07@20230404.csv")
    lake = tmp_path / "lake"

    res = converter.convert(tmp_path / "raw", lake, datasets=[GROUP])
    assert not res.errors, res.errors
    assert res.converted == 2

    dataset_dir = lake / "anac" / GROUP
    # ANO/MES vivem na partição; repeti-los no Parquet sombreia a partição no DuckDB.
    for parquet in dataset_dir.rglob("*.parquet"):
        columns = pl.read_parquet_schema(parquet).keys()
        assert not {"ANO", "MES"} & set(columns)
        assert COLUMNS - {"ANO", "MES"} == set(columns)
    assert check_dataset(dataset_dir) == []

    rows = duckdb.sql(
        f"SELECT ano, mes, NR_AEROPORTO_REFERENCIA, count(*) "
        f"FROM read_parquet('{dataset_dir}/**/*.parquet', hive_partitioning=true, "
        f"union_by_name=true, hive_types={{'ano': 'VARCHAR', 'mes': 'VARCHAR'}}) "
        f"GROUP BY ALL ORDER BY mes"
    ).fetchall()
    assert rows == [("2022", "06", "SBAR", 10), ("2022", "07", "SBRD", 10)]
