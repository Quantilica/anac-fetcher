"""Preâmbulo "Criado em:" (aerodromos-heliponto-privado): 27 colunas, não 1.

O recorte (4 primeiras linhas) é do bruto real de 2026-11-20: a linha
"Criado em: ..." vinha antes do cabeçalho e, sem ser reconhecida, virava o
cabeçalho de uma coluna só.
"""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest

pytest.importorskip("quantilica.analytics.lake")
pytest.importorskip("duckdb")
import polars as pl  # noqa: E402
from quantilica.analytics.lake import LakeWriter  # noqa: E402
from quantilica.core.lake import DatasetDescriptor  # noqa: E402

import anac_fetcher.lake as lake_mod  # noqa: E402
from anac_fetcher.lake import converter  # noqa: E402
from anac_fetcher.reader import _preamble_rows, read_csv  # noqa: E402
from anac_fetcher.storage import _GROUP_DIRS  # noqa: E402

FIXTURE = Path(__file__).parent / "fixtures" / "heliponto_privado_criado_em.csv"
GROUP = "aero-heliponto-privado"
NOME = "aero-heliponto-privado-heliponto-privado-csv@20261120.csv"


def test_criado_em_e_preambulo() -> None:
    assert _preamble_rows(FIXTURE) == 1


def test_preambulo_aceita_os_dois_marcadores_e_o_bom(tmp_path: Path) -> None:
    for linha in (
        "Criado em: 2026-11-20",
        "﻿Criado em: 2026-11-20",
        "Atualizado em: 2026-11-20",
        "﻿Atualizado em: 2026-11-20",
    ):
        path = tmp_path / "a.csv"
        path.write_text(linha + "\na;b\n1;2\n", encoding="utf-8")
        assert _preamble_rows(path) == 1
        assert read_csv(path, {}).columns == ["a", "b"]
    path.write_text("a;b\n1;2\n", encoding="utf-8")
    assert _preamble_rows(path) == 0


def test_recorte_real_do_heliponto_privado_tem_27_colunas() -> None:
    df = read_csv(FIXTURE, {})
    assert df.width == 27
    assert df.height == 2
    assert df.columns[:3] == ["Código OACI", "CIAD", "Nome"]
    assert not any(c.startswith("Criado em") for c in df.columns)


def _bruto(tmp_path: Path) -> Path:
    raw = tmp_path / "raw"
    pasta = raw / _GROUP_DIRS[GROUP]
    pasta.mkdir(parents=True)
    shutil.copy(FIXTURE, pasta / NOME)
    return raw


def _parquets(lake: Path) -> list[Path]:
    return sorted((lake / "anac" / GROUP).rglob("*.parquet"))


def _gravar_como_antes(raw: Path, lake: Path) -> None:
    """Reproduz o Parquet de produção: uma coluna, com o texto do preâmbulo."""
    writer = LakeWriter(
        lake / "anac" / GROUP,
        DatasetDescriptor(
            source_id="anac", dataset_id=GROUP, alias=GROUP, partition_keys=[]
        ),
    )
    errado = pl.DataFrame(
        {"Criado em: 2026-11-20": ["Código OACI;CIAD", "SNBO;CE0134"]}
    )
    writer.write_polars(
        errado, raw / _GROUP_DIRS[GROUP] / NOME, converter="anac-fetcher 0.10.1"
    )


def test_lake_converte_com_27_colunas(tmp_path: Path) -> None:
    raw, lake = _bruto(tmp_path), tmp_path / "lake"
    res = converter.convert(raw, lake, datasets=[GROUP])
    assert (res.converted, res.errors) == (1, [])
    (parquet,) = _parquets(lake)
    assert pl.read_parquet(parquet).width == 27


def test_parquet_antigo_de_uma_coluna_e_reconvertido_uma_vez(tmp_path: Path) -> None:
    raw, lake = _bruto(tmp_path), tmp_path / "lake"
    _gravar_como_antes(raw, lake)
    (antigo,) = _parquets(lake)
    assert pl.read_parquet(antigo).width == 1

    res = converter.convert(raw, lake, datasets=[GROUP])
    assert (res.converted, res.skipped, res.errors) == (1, 0, [])
    (novo,) = _parquets(lake)
    assert novo == antigo
    assert pl.read_parquet(novo).width == 27

    # na rodada seguinte a declaração confere e o arquivo é pulado
    res2 = converter.convert(raw, lake, datasets=[GROUP])
    assert (res2.converted, res2.skipped, res2.errors) == (0, 1, [])


def test_outro_grupo_nao_e_reconvertido(tmp_path: Path) -> None:
    assert lake_mod._saidas_declaradas("vra", Path("x.csv"), {}) is None
    assert lake_mod._saidas_declaradas(GROUP, Path("x.csv"), {}) == ["x"]
