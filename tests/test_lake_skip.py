"""O build sem mudança não extrai ZIP/7z nem lê o bruto: só sidecar e rodapé."""

from __future__ import annotations

import builtins
import hashlib
import io
import json
import zipfile
from pathlib import Path

import pytest

pytest.importorskip("quantilica.analytics.lake")
pytest.importorskip("duckdb")
import quantilica.analytics.lake as analytics_lake  # noqa: E402
import quantilica.core.manifests as manifests  # noqa: E402
from quantilica.analytics.lake import LakeWriter  # noqa: E402

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


@pytest.mark.usefixtures("sem_contratos")
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


@pytest.mark.usefixtures("sem_contratos")
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


@pytest.mark.usefixtures("sem_contratos")
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


@pytest.fixture
def sem_abrir_bruto(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):  # noqa: ANN201
    """Devolve ``armar()``: depois dela, nenhum arquivo do bruto é aberto
    (``builtins.open``, ``io.open`` ou ``Path.open``), nem ZIP; sidecars podem."""
    raiz = str((tmp_path / "raw").resolve())

    def vigia(original):  # noqa: ANN001, ANN202
        def aberto(file, *args, **kwargs):  # noqa: ANN001, ANN002, ANN003, ANN202
            nome = str(file) if isinstance(file, str | Path) else ""
            if nome.startswith(raiz) and not nome.endswith(".manifest.json"):
                raise AssertionError(f"bruto aberto: {nome}")
            return original(file, *args, **kwargs)

        return aberto

    def armar() -> None:
        monkeypatch.setattr(builtins, "open", vigia(builtins.open))
        monkeypatch.setattr(io, "open", vigia(io.open))
        original_path_open = Path.open

        def path_open(self, *args, **kwargs):  # noqa: ANN001, ANN002, ANN003, ANN202
            return vigia(lambda f, *a, **k: original_path_open(Path(f), *a, **k))(
                self, *args, **kwargs
            )

        monkeypatch.setattr(Path, "open", path_open)

    return armar


@pytest.mark.usefixtures("sem_contratos")
def test_segunda_rodada_nao_abre_nenhum_arquivo_do_bruto(
    tmp_path: Path, sem_abrir_bruto, sem_hash_por_leitura: None
) -> None:
    raw, lake = _bruto(tmp_path), tmp_path / "lake"
    _sidecars(raw)
    assert not converter.convert(raw, lake, datasets=["vra"]).errors
    sem_abrir_bruto()
    res = converter.convert(raw, lake, datasets=["vra"])
    assert (res.converted, res.skipped, res.errors) == (0, 2, [])


@pytest.mark.usefixtures("sem_contratos")
def test_sha256_com_erro_de_es_vira_erro_do_arquivo_e_nao_derruba_o_convert(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    raw, lake = _bruto(tmp_path), tmp_path / "lake"
    converter.convert(raw, lake, datasets=["vra"])
    original = analytics_lake.sha256_file

    def sha(path):  # noqa: ANN001, ANN202
        if str(path).endswith("vra_2024-06@20240701.csv"):
            raise OSError(5, "Input/output error")
        return original(path)

    monkeypatch.setattr(analytics_lake, "sha256_file", sha)

    res = converter.convert(raw, lake, datasets=["vra"])  # não levanta

    assert res.skipped == 1  # o ZIP segue em dia
    assert len(res.errors) == 1 and "vra_2024-06" in res.errors[0]


def test_tabelas_com_erro_de_es_no_sha256_reportam_e_nao_derrubam(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    raw, lake = tmp_path / "raw", tmp_path / "lake"
    build_raw(raw)

    def falha(path):  # noqa: ANN001, ANN202
        raise OSError(5, "Input/output error")

    monkeypatch.setattr(lake_mod, "sha256_file", falha)

    res = converter.convert(raw, lake, datasets=[TABELAS])  # não levanta

    assert res.errors


def test_conversao_interrompida_numa_tabela_e_completada(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    raw, lake = tmp_path / "raw", tmp_path / "lake"
    build_raw(raw)
    _sidecars(raw)
    original = LakeWriter.write_group
    chamadas: list[str] = []

    def cai_na_terceira(self, group_key, members, **kw):  # noqa: ANN001, ANN003, ANN202
        chamadas.append(group_key)
        if len(chamadas) == 3:
            raise RuntimeError("kill")
        return original(self, group_key, members, **kw)

    with monkeypatch.context() as m:
        m.setattr(LakeWriter, "write_group", cai_na_terceira)
        r1 = converter.convert(raw, lake, datasets=[TABELAS])
    assert len(r1.errors) == 1

    r2 = converter.convert(raw, lake, datasets=[TABELAS])
    assert not r2.errors, r2.errors
    assert r2.converted == 1 and r2.skipped == r1.converted
    r3 = converter.convert(raw, lake, datasets=[TABELAS])
    assert (r3.converted, r3.errors) == (0, [])
    assert r3.skipped == r1.converted + 1


@pytest.mark.usefixtures("sem_contratos")
def test_arquivo_interrompido_no_zip_e_completado(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    raw, lake = _bruto(tmp_path), tmp_path / "lake"
    original = LakeWriter.write_polars

    def cai_no_csv(self, data, src, **kw):  # noqa: ANN001, ANN003, ANN202
        if Path(src).suffix == ".csv":
            raise RuntimeError("sem espaço em disco")
        return original(self, data, src, **kw)

    with monkeypatch.context() as m:
        m.setattr(LakeWriter, "write_polars", cai_no_csv)
        r1 = converter.convert(raw, lake, datasets=["vra"])
    assert (r1.converted, len(r1.errors)) == (1, 1)

    r2 = converter.convert(raw, lake, datasets=["vra"])
    assert (r2.converted, r2.skipped, r2.errors) == (1, 1, [])
