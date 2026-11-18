"""O build sem mudança não extrai ZIP/7z nem lê o bruto: só sidecar e rodapé."""

from __future__ import annotations

import hashlib
import json
import zipfile
from pathlib import Path

import pytest

pytest.importorskip("quantilica.analytics.lake")
pytest.importorskip("duckdb")
import quantilica.core.manifests as manifests  # noqa: E402

import anac_fetcher.lake as lake_mod  # noqa: E402
from anac_fetcher.lake import converter  # noqa: E402
from anac_fetcher.storage import _GROUP_DIRS  # noqa: E402

from .lake_fixtures import build_raw  # noqa: E402

CSV = "Empresa;Numero do Voo;Codigo DI;Codigo Tipo Linha\n{empresa};1234;0;N\n"
TABELAS = "atrasos-cancelamentos"


def _sidecar(arquivo: Path) -> None:
    dados = arquivo.read_bytes()
    arquivo.with_name(arquivo.name + ".manifest.json").write_text(
        json.dumps(
            {"sha256": hashlib.sha256(dados).hexdigest(), "size_bytes": len(dados)}
        ),
        encoding="utf-8",
    )


def _sidecars(raw: Path) -> None:
    for f in raw.rglob("*"):
        if f.is_file() and not f.name.endswith(".manifest.json"):
            _sidecar(f)


def _bruto(tmp_path: Path) -> Path:
    raw = tmp_path / "raw"
    vra = raw / _GROUP_DIRS["vra"]
    vra.mkdir(parents=True)
    with zipfile.ZipFile(vra / "vra_2024-05@20240601.zip", "w") as zf:
        zf.writestr("pasta/dados.csv", CSV.format(empresa="LATAM"))
    (vra / "vra_2024-06@20240701.csv").write_text(
        CSV.format(empresa="AZUL"), encoding="utf-8"
    )
    return raw


@pytest.fixture
def leituras(monkeypatch: pytest.MonkeyPatch) -> list[str]:
    """Extrações de ZIP/7z e leituras de dados feitas pelo conversor."""
    vistas: list[str] = []
    for nome in ("extracted_data", "read_file", "_read_table"):
        original = getattr(lake_mod, nome)

        def espia(*args, _o=original, _n=nome, **kwargs):  # noqa: ANN002, ANN003
            vistas.append(f"{_n}:{Path(args[2] if _n == '_read_table' else args[0])}")
            return _o(*args, **kwargs)

        monkeypatch.setattr(lake_mod, nome, espia)
    return vistas


@pytest.fixture
def sem_hash_por_leitura(monkeypatch: pytest.MonkeyPatch) -> None:
    def falha(path):  # noqa: ANN001, ANN202
        raise AssertionError(f"bruto lido para o sha256: {path}")

    monkeypatch.setattr(manifests, "sha256_file", falha)


def test_segunda_rodada_nao_extrai_zip_nem_le_dados(
    tmp_path: Path, leituras: list[str], sem_hash_por_leitura: None
) -> None:
    raw, lake = _bruto(tmp_path), tmp_path / "lake"
    _sidecars(raw)
    res = converter.convert(raw, lake, datasets=["vra"])
    assert not res.errors, res.errors
    assert res.converted == 2 and res.skipped == 0
    assert any(v.startswith("extracted_data:") for v in leituras)

    leituras.clear()
    res2 = converter.convert(raw, lake, datasets=["vra"])
    assert not res2.errors, res2.errors
    assert res2.converted == 0 and res2.skipped == 2
    assert leituras == []


def test_zip_novo_extrai_e_converte(tmp_path: Path, leituras: list[str]) -> None:
    raw, lake = _bruto(tmp_path), tmp_path / "lake"
    converter.convert(raw, lake, datasets=["vra"])
    with zipfile.ZipFile(
        raw / _GROUP_DIRS["vra"] / "vra_2024-05@20240801.zip", "w"
    ) as zf:
        zf.writestr("pasta/dados.csv", CSV.format(empresa="GOL"))

    leituras.clear()
    res = converter.convert(raw, lake, datasets=["vra"])
    assert not res.errors, res.errors
    assert res.converted == 1 and res.skipped == 1
    assert [v.split(":")[0] for v in leituras] == ["extracted_data", "read_file"]


def test_force_extrai_e_reconverte(tmp_path: Path, leituras: list[str]) -> None:
    raw, lake = _bruto(tmp_path), tmp_path / "lake"
    converter.convert(raw, lake, datasets=["vra"])
    leituras.clear()
    res = converter.convert(raw, lake, datasets=["vra"], force=True)
    assert not res.errors, res.errors
    assert res.converted == 2 and res.skipped == 0
    assert any(v.startswith("extracted_data:") for v in leituras)


def test_tabelas_em_dia_nao_leem_bruto_nem_o_hasheiam(
    tmp_path: Path, leituras: list[str], sem_hash_por_leitura: None
) -> None:
    raw, lake = tmp_path / "raw", tmp_path / "lake"
    build_raw(raw)
    _sidecars(raw)
    res = converter.convert(raw, lake, datasets=[TABELAS])
    assert not res.errors, res.errors
    assert res.converted > 0

    leituras.clear()
    res2 = converter.convert(raw, lake, datasets=[TABELAS])
    assert not res2.errors, res2.errors
    assert res2.converted == 0 and res2.skipped == res.converted
    assert leituras == []
