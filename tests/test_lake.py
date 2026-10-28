"""Tests for Hive lake conversion of ANAC open data."""

from __future__ import annotations

from importlib.metadata import entry_points
from pathlib import Path

import pytest

pytest.importorskip("quantilica.analytics.lake")
pytest.importorskip("duckdb")

from quantilica.analytics.lake import check_dataset, scan_dataset  # noqa: E402
from typer.testing import CliRunner  # noqa: E402

from anac_fetcher.lake import (  # noqa: E402
    SOURCE_ID,
    converter,
    resolve_partitions,
)
from anac_fetcher.plugin import app  # noqa: E402
from anac_fetcher.storage import _GROUP_DIRS  # noqa: E402


def test_entry_point_registered() -> None:
    eps = entry_points(group="quantilica.lake")
    matches = [ep for ep in eps if ep.name == "anac"]
    assert len(matches) == 1
    loaded = matches[0].load()
    assert loaded is converter
    assert loaded.source_id == SOURCE_ID


def test_resolve_partitions() -> None:
    keys_ym, vals_ym = resolve_partitions({"partition": "2024-05"})
    assert keys_ym == ["ano", "mes"]
    assert vals_ym == {"ano": "2024", "mes": "05"}

    keys_y, vals_y = resolve_partitions({"partition": "2024"})
    assert keys_y == ["ano"]
    assert vals_y == {"ano": "2024"}

    keys_empty, vals_empty = resolve_partitions({})
    assert keys_empty == []
    assert vals_empty == {}


def test_converter_datasets() -> None:
    datasets = converter.datasets()
    assert "vra" in datasets
    assert "rab" in datasets
    assert "dados-estatisticos" in datasets


def test_convert_end_to_end(tmp_path: Path) -> None:
    raw_dir = tmp_path / "raw"
    # Create VRA fixture
    vra_dir = raw_dir / _GROUP_DIRS["vra"]
    vra_dir.mkdir(parents=True)
    vra_csv = vra_dir / "vra_2024-05@20240601.csv"
    vra_csv.write_text(
        "Empresa;Numero do Voo;Codigo DI;Codigo Tipo Linha\nLATAM;1234;0;N\n",
        encoding="utf-8",
    )

    # Create unpartitioned RAB fixture
    rab_dir = raw_dir / _GROUP_DIRS["rab"]
    rab_dir.mkdir(parents=True)
    rab_csv = rab_dir / "rab_dados@20240601.csv"
    rab_csv.write_text(
        "Marca;Modelo;Fabricante\nPT-ABC;PA-28;PIPER\n",
        encoding="utf-8",
    )

    lake_dir = tmp_path / "lake"
    res = converter.convert(raw_dir, lake_dir)
    assert not res.errors, res.errors
    assert res.converted == 2
    assert res.skipped == 0

    # Verify VRA (partitioned by ano/mes)
    vra_lake = lake_dir / SOURCE_ID / "vra"
    assert check_dataset(vra_lake) == []
    df_vra = scan_dataset(vra_lake).collect()
    assert df_vra.height == 1
    assert "ano" in df_vra.columns
    assert "mes" in df_vra.columns
    assert df_vra["ano"][0] == "2024"
    assert df_vra["mes"][0] == "05"

    # Verify RAB (unpartitioned)
    rab_lake = lake_dir / SOURCE_ID / "rab"
    assert check_dataset(rab_lake) == []
    df_rab = scan_dataset(rab_lake).collect()
    assert df_rab.height == 1
    assert "Marca" in df_rab.columns

    # Second pass skips
    res2 = converter.convert(raw_dir, lake_dir)
    assert not res2.errors
    assert res2.converted == 0
    assert res2.skipped == 2


def test_cli_convert(tmp_path: Path) -> None:
    raw_dir = tmp_path / "raw"
    vra_dir = raw_dir / _GROUP_DIRS["vra"]
    vra_dir.mkdir(parents=True)
    (vra_dir / "vra_2024-05@20240601.csv").write_text(
        "Empresa;Numero do Voo\nLATAM;1234\n",
        encoding="utf-8",
    )

    lake_dir = tmp_path / "lake"
    runner = CliRunner()
    result = runner.invoke(
        app,
        ["convert", "-i", str(raw_dir), "--lake", str(lake_dir), "--dataset", "vra"],
    )
    assert result.exit_code == 0, result.output
    assert (lake_dir / SOURCE_ID / "vra").exists()


def test_pick_one_format_prefers_csv_and_latest(tmp_path: Path) -> None:
    from anac_fetcher.lake import pick_one_format

    names = [
        "empresas-aereas-nacionais-csv@20261026.csv",
        "empresas-aereas-nacionais-json@20261026.json",
        "rab-hist-csv_2024-09@20240901.csv",
        "rab-hist-csv_2024-09@20241001.csv",
        "rab-hist-json_2024-09@20241001.json",
        "rab-hist-xls_2024-09@20241001.xls",
        "atrasos_2025-10_anexo-ii@20260527.json",
    ]
    chosen = [p.name for p in pick_one_format([tmp_path / n for n in names])]
    assert chosen == [
        "atrasos_2025-10_anexo-ii@20260527.json",
        "empresas-aereas-nacionais-csv@20261026.csv",
        "rab-hist-csv_2024-09@20241001.csv",
    ]


def test_read_json_latin1(tmp_path: Path) -> None:
    from anac_fetcher.reader import read_json

    src = tmp_path / "anexo.json"
    src.write_bytes('[{"Situação": "CANCELADO", "Código": "É1"}]'.encode("latin-1"))
    df = read_json(src)
    assert df.row(0) == ("CANCELADO", "É1")


def test_read_csv_unbalanced_quotes(tmp_path: Path) -> None:
    from anac_fetcher.reader import read_csv

    src = tmp_path / "rab.csv"
    src.write_text(
        '"MARCA";"PROPRIETARIO";"MODELO"\n'
        '"PT-ABC";"SERGIO LUIZ LOUSADA JR"";"PLAN"\n'
        '"PT-XYZ";"MARIA";"PA-28"\n',
        encoding="latin-1",
    )
    df = read_csv(src, {})
    assert df.columns == ["MARCA", "PROPRIETARIO", "MODELO"]
    assert df["MARCA"].to_list() == ["PT-ABC", "PT-XYZ"]


def test_read_json_ndjson(tmp_path: Path) -> None:
    from anac_fetcher.reader import read_json

    src = tmp_path / "empresas.json"
    src.write_text(
        '{"cnpj": "11.478.447/0001-97", "atividades_aereas": ["AEROAGRÍCOLA"]}\r\n'
        '{"cnpj": "47.298.916/0001-33", "atividades_aereas": ["A", "B"]}\r\n',
        encoding="utf-8",
    )
    df = read_json(src)
    assert df["atividades_aereas"].to_list() == ["AEROAGRÍCOLA", "A; B"]


def test_pick_one_format_respects_group_preference(tmp_path: Path) -> None:
    from anac_fetcher.lake import pick_one_format

    names = [
        "empresas-aereas-nacionais-csv@20261026.csv",
        "empresas-aereas-nacionais-json@20261026.json",
    ]
    chosen = pick_one_format([tmp_path / n for n in names], (".json", ".csv"))
    assert [p.name for p in chosen] == [names[1]]


def test_read_csv_refuses_giant_line(tmp_path: Path) -> None:
    from anac_fetcher.reader import read_csv

    src = tmp_path / "quebrado.csv"
    src.write_bytes(b'a\\""b\\""' * 200_000)
    with pytest.raises(ValueError, match="CSV quebrado"):
        read_csv(src, {})
