"""Atrasos-cancelamentos por tabela: segunda execução, migração, auditoria, gêmeos."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import pyarrow.parquet as pq
import pytest

pytest.importorskip("quantilica.analytics.lake")

from quantilica.analytics import lake_audit  # noqa: E402
from quantilica.analytics.lake import (  # noqa: E402
    META_MEMBERS,
    LakeWriter,
    check_dataset,
    scan_dataset,
)
from quantilica.core.lake import DatasetDescriptor, partition_types_for  # noqa: E402

import anac_fetcher.lake as lake_mod  # noqa: E402
from anac_fetcher.lake import SOURCE_ID, converter, fold_twins, route_group  # noqa: E402
from anac_fetcher.reader import parse_filename  # noqa: E402
from anac_fetcher.storage import _GROUP_DIRS  # noqa: E402
from anac_fetcher.wrangling import spec_for  # noqa: E402

from .lake_fixtures import BASE, arquivos_por_mes, build_raw, snapshot  # noqa: E402

DATASET = "atrasos-cancelamentos"


def _legacy_convert(raw: Path, lake: Path) -> None:
    """O conversor anterior: um Parquet por CSV bruto, o sem sufixo inclusive."""
    pasta = raw / _GROUP_DIRS[DATASET]
    for path in sorted(pasta.glob("*.csv")):
        meta = parse_filename(path)
        keys = ["ano", "mes"]
        writer = LakeWriter(
            lake / SOURCE_ID / DATASET,
            DatasetDescriptor(
                source_id=SOURCE_ID,
                dataset_id=DATASET,
                alias=DATASET,
                partition_keys=keys,
                partition_types=partition_types_for(keys),
            ),
        )
        frame = lake_mod._read_table(DATASET, spec_for(DATASET), path, keys)
        writer.write_polars(
            frame,
            path,
            partitions={"ano": str(meta["year"]), "mes": f"{meta['part']:02d}"},
            converter="anac-fetcher legado",
        )


def _parquets(lake: Path) -> list[Path]:
    return sorted((lake / SOURCE_ID).rglob("*.parquet"))


@pytest.fixture
def raw(tmp_path: Path) -> Path:
    build_raw(tmp_path / "raw")
    return tmp_path / "raw"


def test_um_parquet_por_anexo_e_mes_e_o_sem_sufixo_nao_vira_tabela(
    raw: Path, tmp_path: Path
) -> None:
    lake = tmp_path / "lake"
    res = converter.convert(raw, lake)

    assert not res.errors
    # 7 anexos + vra + rab; as 2 cópias sem sufixo e o JSON não são convertidos.
    assert (res.converted, res.skipped) == (9, 0)
    nomes = sorted(p.name for p in _parquets(lake) if DATASET in p.parts)
    assert nomes == [
        "atrasos-cancelamentos_202608_anexo-iii.parquet",
        "atrasos-cancelamentos_202609_anexo-i.parquet",
        "atrasos-cancelamentos_202609_anexo-ii.parquet",
        "atrasos-cancelamentos_202609_anexo-iii.parquet",
        "atrasos-cancelamentos_202610_anexo-i.parquet",
        "atrasos-cancelamentos_202610_anexo-ii.parquet",
        "atrasos-cancelamentos_202610_anexo-iii.parquet",
    ]
    assert arquivos_por_mes(lake) == {
        "atrasos-cancelamentos/2026/08": 1,
        "atrasos-cancelamentos/2026/09": 3,
        "atrasos-cancelamentos/2026/10": 3,
        "rab": 1,
        "vra/2026/10": 1,
    }
    dados = lake / SOURCE_ID / DATASET
    assert check_dataset(dados) == []
    arquivo = dados / "ano=2026/mes=09/atrasos-cancelamentos_202609_anexo-i.parquet"
    meta = pq.ParquetFile(arquivo).metadata.metadata
    membros = json.loads(meta[META_MEMBERS.encode()])
    assert list(membros) == ["atrasos-cancelamentos_2026-09_anexo-i"]
    assert membros[list(membros)[0]]["converter_version"] == "1"


def test_anexos_de_esquemas_diferentes_nao_sao_juntados(
    raw: Path, tmp_path: Path
) -> None:
    lake = tmp_path / "lake"
    converter.convert(raw, lake)
    pasta = lake / SOURCE_ID / DATASET / "ano=2026/mes=09"
    colunas = {
        p.name.split("_")[-1]: len(pq.ParquetFile(p).schema_arrow.names) - 1
        for p in pasta.glob("*.parquet")
    }  # -1: _origem
    assert colunas == {
        "anexo-i.parquet": 10,
        "anexo-ii.parquet": 9,
        "anexo-iii.parquet": 8,
    }


def test_segunda_execucao_pula_tudo_sem_reescrever_nem_ler(
    raw: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    lake = tmp_path / "lake"
    assert converter.convert(raw, lake).converted == 9
    antes = {p: (p.stat().st_mtime_ns, p.stat().st_ino) for p in _parquets(lake)}

    def nao_ler(*args, **kwargs):
        raise AssertionError("leu um anexo que já estava no lake")

    monkeypatch.setattr(lake_mod, "_read_table", nao_ler)
    res = converter.convert(raw, lake)

    assert not res.errors
    # Os dois grupos de vra e rab usam write_polars e se pulam pelo sha.
    assert res.converted == 0
    assert {
        p: (p.stat().st_mtime_ns, p.stat().st_ino) for p in _parquets(lake)
    } == antes


def test_anexo_alterado_reescreve_so_o_seu_mes(raw: Path, tmp_path: Path) -> None:
    lake = tmp_path / "lake"
    converter.convert(raw, lake)
    outro = lake / SOURCE_ID / DATASET / "ano=2026/mes=09"
    outro = outro / "atrasos-cancelamentos_202609_anexo-i.parquet"
    mtime = outro.stat().st_mtime_ns
    anexo = (
        raw
        / _GROUP_DIRS[DATASET]
        / "atrasos-cancelamentos_2026-10_anexo-ii@20261101.csv"
    )
    linhas = anexo.read_bytes().splitlines()
    anexo.write_bytes(b"\n".join(linhas[:2]) + b"\n")

    res = converter.convert(raw, lake)

    assert not res.errors and res.converted == 1
    assert outro.stat().st_mtime_ns == mtime
    df = scan_dataset(lake / SOURCE_ID / DATASET).collect()
    por_origem = dict(df.group_by("_origem").len().rows())
    assert por_origem["atrasos-cancelamentos_2026-10_anexo-ii"] == 1


def test_migracao_remove_os_parquets_antigos_inclusive_a_copia_sem_sufixo(
    raw: Path, tmp_path: Path
) -> None:
    lake = tmp_path / "lake"
    _legacy_convert(raw, lake)
    antigos = sorted(p.name for p in _parquets(lake))
    assert len(antigos) == 9  # 7 anexos + 2 cópias sem sufixo
    assert "atrasos-cancelamentos_2026-09.parquet" in antigos
    antes = snapshot(lake)

    res = converter.convert(raw, lake)

    assert not res.errors
    nomes = [p.name for p in _parquets(lake) if DATASET in p.parts]
    assert len(nomes) == 7 and all("_2026-" not in n for n in nomes)
    depois = snapshot(lake)
    # Nenhuma linha duplicada: cada anexo tem as linhas de antes, e as cópias
    # sem sufixo (idênticas a um anexo) deixaram de existir.
    for chave, dados in depois.items():
        if chave.startswith(DATASET):
            assert dados == antes[chave], chave
    sobrou = sorted(set(antes) - set(depois))
    assert sobrou == [
        f"{DATASET}/2026/09/{BASE}_2026-09",
        f"{DATASET}/2026/10/{BASE}_2026-10",
    ]
    total = scan_dataset(lake / SOURCE_ID / DATASET).collect().height
    assert total == sum(d["linhas"] for k, d in depois.items() if k.startswith(DATASET))
    # Segunda passada: nada a fazer.
    assert converter.convert(raw, lake).converted == 0


def _sem_sufixo_diferente(raw: Path) -> Path:
    """Arquivo sem sufixo em 2026-08 (que tem o Anexo III) que não copia o anexo."""
    pasta = raw / _GROUP_DIRS[DATASET]
    antigo = pasta / "atrasos-cancelamentos_2026-08@20261001.csv"
    antigo.write_text("A;B\n1;2\n", encoding="utf-8")
    return antigo


def test_sem_sufixo_que_nao_copia_anexo_num_mes_com_anexos_e_superado(
    raw: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    antigo = _sem_sufixo_diferente(raw)
    avisos: list[str] = []
    monkeypatch.setattr(
        lake_mod.logger, "warning", lambda msg, *a: avisos.append(msg % a)
    )
    lake = tmp_path / "lake"

    res = converter.convert(raw, lake)

    assert not res.errors and res.converted == 9
    pasta = lake / SOURCE_ID / DATASET / "ano=2026/mes=08"
    assert [p.name for p in pasta.glob("*.parquet")] == [
        "atrasos-cancelamentos_202608_anexo-iii.parquet"
    ]
    assert any(antigo.name in a and "revisado" in a for a in avisos)
    itens = {Path(i.path).name: i for i in converter.inventory(raw)}
    assert itens[antigo.name].skip_reason == "superado"
    assert itens[antigo.name].dataset is None


def test_auditoria_nao_acusa_o_sem_sufixo_superado(raw: Path, tmp_path: Path) -> None:
    entrada = tmp_path / "entrada"
    shutil.copytree(raw, entrada / SOURCE_ID)
    _sem_sufixo_diferente(entrada / SOURCE_ID)
    lake = tmp_path / "lake"
    assert not converter.convert(entrada / SOURCE_ID, lake).errors

    report = lake_audit(
        lake, input_dir=entrada, converters={SOURCE_ID: converter}, rehash=True
    )

    assert report.ok, report.to_text()
    assert not [f for f in report.findings if f.category == "sem_parquet"]


def test_sem_sufixo_num_mes_sem_anexos_e_tabela_propria(
    raw: Path, tmp_path: Path
) -> None:
    pasta = raw / _GROUP_DIRS[DATASET]
    (pasta / "atrasos-cancelamentos_2026-07@20261001.csv").write_text(
        "A;B\n1;2\n", encoding="utf-8"
    )

    res = converter.convert(raw, tmp_path / "lake")

    assert not res.errors and res.converted == 10
    mes = tmp_path / "lake" / SOURCE_ID / DATASET / "ano=2026/mes=07"
    assert [p.name for p in mes.glob("*.parquet")] == [
        "atrasos-cancelamentos_202607.parquet"
    ]


def test_parquet_antigo_do_sem_sufixo_superado_e_acusado(
    raw: Path, tmp_path: Path
) -> None:
    antigo = _sem_sufixo_diferente(raw)
    lake = tmp_path / "lake"
    _legacy_convert(raw, lake)
    assert (
        lake
        / SOURCE_ID
        / DATASET
        / "ano=2026/mes=08"
        / "atrasos-cancelamentos_2026-08.parquet"
    ).exists()

    res = converter.convert(raw, lake)

    assert any("atrasos-cancelamentos_2026-08.parquet" in e for e in res.errors)
    assert antigo.exists()


def test_anexo_revisado_acusa_o_parquet_antigo_que_ficou(
    raw: Path, tmp_path: Path
) -> None:
    lake = tmp_path / "lake"
    _legacy_convert(raw, lake)
    anexo = (
        raw
        / _GROUP_DIRS[DATASET]
        / "atrasos-cancelamentos_2026-09_anexo-i@20261101.csv"
    )
    anexo.write_bytes(b"\n".join(anexo.read_bytes().splitlines()[:3]) + b"\n")

    res = converter.convert(raw, lake)

    assert len(res.errors) >= 1
    assert any(
        "atrasos-cancelamentos_202609_anexo-i" in e
        and "atrasos-cancelamentos_2026-09_anexo-i.parquet" in e
        for e in res.errors
    )
    antigo = lake / SOURCE_ID / DATASET / "ano=2026/mes=09"
    assert (antigo / "atrasos-cancelamentos_2026-09_anexo-i.parquet").exists()


def test_sha_calculado_uma_vez_por_arquivo(
    raw: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    chamadas: list[str] = []
    original = lake_mod.sha256_file
    monkeypatch.setattr(
        lake_mod,
        "sha256_file",
        lambda p, *a, **k: chamadas.append(p.name) or original(p, *a, **k),
    )
    import quantilica.analytics.lake as analytics_lake

    analytics_calls: list[str] = []
    original_a = analytics_lake.sha256_file
    monkeypatch.setattr(
        analytics_lake,
        "sha256_file",
        lambda p, *a, **k: (
            analytics_calls.append(Path(p).name) or original_a(p, *a, **k)
        ),
    )

    converter.convert(raw, tmp_path / "lake")

    # O analytics não recalcula: recebe o sha256 no GroupMember.
    anexos = [c for c in analytics_calls if "atrasos-cancelamentos_" in c]
    assert anexos == []
    assert all(chamadas.count(n) == 1 for n in set(chamadas))


def test_inventario_da_copia_sem_sufixo_e_gemeo(raw: Path) -> None:
    core = pytest.importorskip("quantilica.core.lake")
    if not hasattr(core, "Planned"):
        pytest.skip("core sem Planned")
    itens = {Path(i.path).name: i for i in converter.inventory(raw)}

    assert itens["atrasos-cancelamentos_2026-09@20261101.csv"].skip_reason == "gemeo"
    assert itens["atrasos-cancelamentos_2026-10@20261101.csv"].skip_reason == "gemeo"
    assert (
        itens["atrasos-cancelamentos_2026-10_anexo-ii@20261101.json"].skip_reason
        == "gemeo"
    )
    anexo = itens["atrasos-cancelamentos_2026-09_anexo-i@20261101.csv"]
    assert anexo.skip_reason is None and anexo.dataset == DATASET


def test_fold_twins_so_dobra_copia_exata_de_anexo_da_mesma_particao(
    raw: Path,
) -> None:
    pasta = raw / _GROUP_DIRS[DATASET]
    routed, _ = route_group(DATASET, pasta)
    caminhos = {r.path.name: r for r in routed}
    assert "atrasos-cancelamentos_2026-09@20261101.csv" not in caminhos
    iii = caminhos["atrasos-cancelamentos_2026-09_anexo-iii@20261101.csv"]
    assert [t.name for t in iii.twins] == ["atrasos-cancelamentos_2026-09@20261101.csv"]
    i10 = caminhos["atrasos-cancelamentos_2026-10_anexo-i@20261101.csv"]
    assert [t.name for t in i10.twins] == ["atrasos-cancelamentos_2026-10@20261101.csv"]
    # Idempotente sobre o resultado.
    assert fold_twins(routed)[1] == []


def test_auditoria_do_lake_agrupado_e_do_migrado(raw: Path, tmp_path: Path) -> None:
    for migrado in (False, True):
        base = tmp_path / ("m" if migrado else "n")
        entrada = base / "entrada"
        shutil.copytree(raw, entrada / SOURCE_ID)
        lake = base / "lake"
        if migrado:
            _legacy_convert(entrada / SOURCE_ID, lake)
        res = converter.convert(entrada / SOURCE_ID, lake)
        assert not res.errors

        report = lake_audit(
            lake, input_dir=entrada, converters={SOURCE_ID: converter}, rehash=True
        )
        assert report.ok, report.to_text()
