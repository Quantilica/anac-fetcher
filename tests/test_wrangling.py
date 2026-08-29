"""Tests for anac_fetcher.wrangling."""

from pathlib import Path

import polars as pl

from anac_fetcher.wrangling import (
    convert_group,
    convert_one,
    extract_schema,
    spec_for,
)


def _make_group_input(tmp_path: Path, group_dir: str, files: dict[str, str]) -> Path:
    src = tmp_path / "input" / group_dir
    src.mkdir(parents=True, exist_ok=True)
    for name, content in files.items():
        (src / name).write_text(content, encoding="utf-8")
    return tmp_path / "input"


def test_spec_for_defaults():
    spec = spec_for("vra")
    assert spec["separator"] is None  # None = sniffa separador
    assert spec["encoding"] is None
    assert spec["numeric_columns"] == []


def test_convert_one_writes_partitioned_parquet(tmp_path):
    src = _make_group_input(
        tmp_path,
        "voo-regular-ativo",
        {"vra_2025-05@20250601.csv": "Empresa;Numero\nLATAM;1234\n"},
    )
    raw = src / "voo-regular-ativo" / "vra_2025-05@20250601.csv"
    written = convert_one("vra", raw, tmp_path / "output")
    assert len(written) == 1
    target = tmp_path / "output" / "voo-regular-ativo" / "vra_2025-05@20250601.parquet"
    assert written[0] == target
    assert pl.read_parquet(target).shape == (1, 2)


def test_convert_one_json(tmp_path):
    src = _make_group_input(
        tmp_path,
        "ocorrencias-cenipa",
        {
            "ocorrencias-json@20260829.json": (
                '[{"codigo": 1, "classificacao": "ACIDENTE"}]'
            )
        },
    )
    raw = src / "ocorrencias-cenipa" / "ocorrencias-json@20260829.json"
    written = convert_one("ocorrencias", raw, tmp_path / "output")
    assert len(written) == 1
    df = pl.read_parquet(written[0])
    assert df["classificacao"][0] == "ACIDENTE"


def test_convert_one_skips_existing(tmp_path):
    src = _make_group_input(
        tmp_path,
        "voo-regular-ativo",
        {"vra_2025-05@20250601.csv": "Empresa;Numero\nLATAM;1\n"},
    )
    raw = src / "voo-regular-ativo" / "vra_2025-05@20250601.csv"
    first = convert_one("vra", raw, tmp_path / "output")
    second = convert_one("vra", raw, tmp_path / "output")
    assert len(first) == 1
    assert second == []


def test_convert_group_ignores_manifest_sidecar(tmp_path):
    src = _make_group_input(
        tmp_path,
        "voo-regular-ativo",
        {
            "vra_2025-05@20250601.csv": "Empresa;Numero\nLATAM;1\n",
            "vra_2025-05@20250601.csv.manifest.json": '{"source_id": "anac"}',
        },
    )
    converted = convert_group(["vra"], src, tmp_path / "output")
    assert converted == 1


def test_convert_group_unknown_group(tmp_path):
    assert (
        convert_group(["grupo-inexistente"], tmp_path / "input", tmp_path / "out") == 0
    )


def test_extract_schema(tmp_path):
    src = _make_group_input(
        tmp_path,
        "voo-regular-ativo",
        {"vra_2025-05@20250601.csv": "Empresa;Numero\nLATAM;1\n"},
    )
    out_csv = tmp_path / "schema.csv"
    extract_schema(["vra"], src, out_csv)
    lines = out_csv.read_text().strip().splitlines()
    assert len(lines) == 3  # header + 2 colunas
    assert "vra" in lines[1]
