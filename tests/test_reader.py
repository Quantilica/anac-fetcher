"""Tests for anac_fetcher.reader."""

import json
import zipfile
from pathlib import Path

import polars as pl

from anac_fetcher.reader import (
    decompress,
    normalize_dtypes,
    parse_filename,
    provenance_metadata,
    read_csv,
    read_excel,
    read_json,
    write_parquet,
)


def test_parse_filename_static():
    meta = parse_filename(Path("/data/anac/ocorrencias/ocorrencias-csv@20260829.csv"))
    assert meta["base_id"] == "ocorrencias-csv"
    assert meta["partition"] is None
    assert meta["modification"] == 20260829
    assert meta["ext"] == "csv"


def test_parse_filename_monthly():
    meta = parse_filename(Path("vra_2025-05@20250601.csv"))
    assert meta["base_id"] == "vra"
    assert meta["year"] == 2025
    assert meta["part"] == 5
    assert meta["partition"] == "2025-05"
    assert meta["ext"] == "csv"


def test_parse_filename_unstamped_monthly():
    meta = parse_filename(Path("vra_2025-05.csv"))
    assert meta["partition"] == "2025-05"
    assert meta["modification"] is None


def test_parse_filename_unrecognized():
    meta = parse_filename(Path("arquivo_estranho.json"))
    assert meta["base_id"] == "arquivo_estranho"
    assert meta["partition"] is None


def test_normalize_dtypes():
    df = pl.DataFrame(
        {
            "Valor": ["1.234,56", "2,5", "abc"],
            "Municipio": ["  SAO PAULO ", "  RIO  ", "  SP  "],
            "Ano": [2020, 2021, 2022],
        }
    )
    out = normalize_dtypes(df, {"numeric_columns": ["Valor"]})
    assert out["Valor"].dtype == pl.Float64
    assert out["Valor"].to_list() == [1234.56, 2.5, None]
    assert out["Municipio"].to_list() == ["SAO PAULO", "RIO", "SP"]


def test_read_csv_utf8(tmp_path):
    path = tmp_path / "dados.csv"
    path.write_text("produto;valor\nGasolina;5,49\n", encoding="utf-8")
    df = read_csv(path, {"encoding": "utf-8"})
    assert df.shape == (1, 2)
    assert df["valor"].dtype == pl.Utf8  # infer_schema_length=0 mantém String


def test_read_csv_latin1_fallback(tmp_path):
    path = tmp_path / "dados.csv"
    path.write_bytes("produto;valor\nGasolina;5,49\n".encode("latin-1"))
    df = read_csv(path, {})
    assert df["produto"][0] == "Gasolina"


def test_read_csv_skips_preamble(tmp_path):
    path = tmp_path / "dados.csv"
    path.write_text(
        "\ufeffAtualizado em: 2026-08-29\r\nproduto;valor\nGasolina;5,49\n",
        encoding="utf-8",
    )
    df = read_csv(path, {})
    assert df.columns == ["produto", "valor"]
    assert df.shape == (1, 2)


def test_read_csv_sniffs_separator(tmp_path):
    path = tmp_path / "dados.csv"
    path.write_text("produto,valor\nGasolina,5,49\n")
    df = read_csv(path, {})
    assert df.shape == (1, 2)
    assert df.columns == ["produto", "valor"]


def test_read_csv_truncates_ragged(tmp_path):
    path = tmp_path / "dados.csv"
    path.write_text("a;b\n1;2\n3;4;5\n")
    df = read_csv(path, {})
    assert df.shape == (2, 2)


def test_read_json_mixed_types(tmp_path):
    path = tmp_path / "dados.json"
    path.write_text('[{"id": 1, "v": null}, {"id": "0", "v": "x"}]')
    df = read_json(path)
    assert df.shape == (2, 2)
    assert df["id"].dtype == pl.Utf8  # tipos mistos -> String no fallback


def test_read_json(tmp_path):
    path = tmp_path / "dados.json"
    path.write_text('[{"ano": 2020, "valor": 10.5}, {"ano": 2021, "valor": 20.5}]')
    df = read_json(path)
    assert df.shape == (2, 2)
    assert df["ano"].to_list() == [2020, 2021]


def test_read_excel_all_sheets(tmp_path):
    import openpyxl

    wb = openpyxl.Workbook()
    ws1 = wb.active
    ws1.title = "Abas_2020"
    ws1.append(["ano", "valor"])
    ws1.append([2020, 10.5])
    ws2 = wb.create_sheet("Abas_2021")
    ws2.append(["ano", "valor"])
    ws2.append([2021, 20.5])
    path = tmp_path / "multi.xlsx"
    wb.save(path)
    frames = read_excel(path, {"sheet": "all"})
    assert isinstance(frames, dict)
    assert set(frames) == {"Abas_2020", "Abas_2021"}


def test_decompress_zip(tmp_path):
    raw = tmp_path / "arquivo.zip"
    inner = tmp_path / "dados.xlsx"
    inner.write_bytes(b"\xd0\xcf\x11\xe0 fake-xlsx")
    with zipfile.ZipFile(raw, "w") as zf:
        zf.write(inner, "dados.xlsx")
    extracted = decompress(raw)
    assert extracted.suffix == ".xlsx"


def test_provenance_metadata(tmp_path):
    raw = tmp_path / "dados.csv"
    raw.write_text("a;b\n")
    manifest = tmp_path / "dados.csv.manifest.json"
    manifest.write_text(
        json.dumps(
            {
                "source_id": "anac",
                "dataset_id": "ocorrencias",
                "url": "https://example.org/x.csv",
                "sha256": "abc123",
                "fetched_at": "2026-01-01T00:00:00Z",
                "producer": "anac-fetcher",
            }
        )
    )
    meta = provenance_metadata(raw)
    assert meta["quantilica.dataset_id"] == "ocorrencias"
    assert meta["quantilica.origin_sha256"] == "abc123"


def test_provenance_metadata_missing(tmp_path):
    raw = tmp_path / "dados.csv"
    raw.write_text("a;b\n")
    assert provenance_metadata(raw) == {}


def test_write_parquet(tmp_path):
    df = pl.DataFrame({"a": [1, 2], "b": ["x", "y"]})
    target = tmp_path / "out" / "dados@20260101.parquet"
    result = write_parquet(df, target)
    assert result.exists()
    assert pl.read_parquet(target).shape == (2, 2)
