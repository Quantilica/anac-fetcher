"""Cabeçalhos de arquivos da ANAC que viravam nomes de coluna inválidos no lake."""

from pathlib import Path

import pytest

pl = pytest.importorskip("polars")
pytest.importorskip("fastexcel")

from anac_fetcher.lake import LakeConverter, pick_one_format  # noqa: E402
from anac_fetcher.reader import MAX_COLUMN_NAME, read_csv, read_file  # noqa: E402
from anac_fetcher.storage import _GROUP_DIRS  # noqa: E402
from anac_fetcher.wrangling import spec_for  # noqa: E402


def _valid(names: list[str]) -> bool:
    return all(
        n.strip()
        and len(n) <= MAX_COLUMN_NAME
        and not any(ord(c) < 32 or 127 <= ord(c) <= 159 for c in n)
        for n in names
    ) and len(names) == len(set(names))


def test_delimitador_sobrando_no_cabecalho_descarta_coluna_vazia(
    tmp_path: Path,
) -> None:
    src = tmp_path / "x.csv"
    src.write_text("a;b;\n1;2;\n3;4;\n", encoding="latin-1")
    df = read_csv(src, {})
    assert df.columns == ["a", "b"]
    assert df.height == 2


def test_coluna_de_nome_vazio_com_dados_ganha_nome_estavel(tmp_path: Path) -> None:
    src = tmp_path / "x.csv"
    src.write_text("a;;c\n1;2;3\n", encoding="latin-1")
    assert read_csv(src, {}).columns == ["a", "coluna_2", "c"]


def test_nome_com_controle_e_muito_longo(tmp_path: Path) -> None:
    longo = "y" * 200
    src = tmp_path / "x.csv"
    src.write_text(f'a;"b\nc";{longo}\n1;2;3\n', encoding="utf-8")
    cols = read_csv(src, {}).columns
    assert cols[:2] == ["a", "b c"]
    assert _valid(cols)


def test_read_file_json_e_planilha_passam_pela_limpeza(tmp_path: Path) -> None:
    src = tmp_path / "x.json"
    src.write_text('{"a\\nb": 1}\r\n{"a\\nb": 2}\r\n', encoding="utf-8")
    assert read_file(src, {}).columns == ["a b"]


def test_csv_sem_cabecalho_prefere_o_json_gemeo() -> None:
    # aero-pistas-pouso e aero-posicoes-estacionamento: o CSV não tem cabeçalho
    for group in ("aero-pistas-pouso", "aero-posicoes-estacionamento"):
        assert spec_for(group)["formatos"] == (".json", ".csv")


def test_lake_converte_o_json_dos_aerodromos_sem_cabecalho(tmp_path: Path) -> None:
    src = tmp_path / "raw" / _GROUP_DIRS["aero-pistas-pouso"]
    src.mkdir(parents=True)
    csv = src / "aero-pistas-pouso-pistas-pouso-csv@20240105.csv"
    csv.write_text(
        "Aeródromos,Aeródromos privados,700,3423,,0.2e2\n"
        "Aeródromos,Aeródromos privados,2982,4204,,0.19e2\n",
        encoding="utf-8",
    )
    js = src / "aero-pistas-pouso-pistas-pouso-json@20240105.json"
    js.write_text(
        '{"MCDA":"Aeródromos","id_aerodromo":700,"id_pista":3423}\n'
        '{"MCDA":"Aeródromos","id_aerodromo":2982,"id_pista":4204}\n',
        encoding="utf-8",
    )
    spec = spec_for("aero-pistas-pouso")
    chosen = pick_one_format([csv, js], spec["formatos"])
    assert [p.name for p in chosen] == [js.name]

    lake = tmp_path / "lake"
    result = LakeConverter().convert(
        tmp_path / "raw", lake, datasets=["aero-pistas-pouso"]
    )
    assert not result.errors
    parquets = list((lake / "anac" / "aero-pistas-pouso").rglob("*.parquet"))
    assert len(parquets) == 1
    names = pl.read_parquet(parquets[0]).columns
    assert set(names) == {"MCDA", "id_aerodromo", "id_pista"}
    assert _valid(names)
