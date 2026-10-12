"""Tests for anac_fetcher.storage."""

import datetime as dt
from pathlib import Path

from anac_fetcher.catalog import GROUPS, list_datasets
from anac_fetcher.storage import _GROUP_DIRS, DataRepository


def test_group_dirs_cover_all_groups():
    assert set(_GROUP_DIRS) == set(GROUPS)


def test_path_for_rab_static_snapshot(tmp_path):
    repo = DataRepository(tmp_path)
    entry = next(e for e in list_datasets("rab") if e["id"] == "rab-atual-csv")
    path = repo.path_for_entry(entry)
    assert path.parent.name == "registro-aeronautico-brasileiro"
    assert path.name.startswith("rab-atual-csv")
    assert path.suffix == ".csv"


def test_path_for_rab_static_snapshot_with_date(tmp_path):
    repo = DataRepository(tmp_path)
    entry = next(e for e in list_datasets("rab") if e["id"] == "rab-atual-json")
    date = dt.date(2026, 7, 21)
    path = repo.path_for_entry(entry, last_modified=date)
    assert "rab-atual-json@20260721" in path.name
    assert path.suffix == ".json"


def test_path_for_rab_historical_entry(tmp_path):
    repo = DataRepository(tmp_path)
    entry = next(
        e
        for e in list_datasets("rab")
        if e["ext"] == "xls" and e["year"] == 2020 and e["month"] == 3
    )
    date = dt.date(2026, 6, 1)
    path = repo.path_for_entry(entry, last_modified=date)
    assert path.parent.name == "registro-aeronautico-brasileiro"
    assert "rab-hist-xls_2020-03@20260601" in path.name


def test_path_for_vra_entry(tmp_path):
    repo = DataRepository(tmp_path)
    entry = next(
        e
        for e in list_datasets("vra")
        if e["year"] == 2015 and e["month"] == 11 and e["ext"] == "csv"
    )
    date = dt.date(2026, 1, 15)
    path = repo.path_for_entry(entry, last_modified=date)
    assert path.parent.name == "voo-regular-ativo"
    assert "vra_2015-11@20260115" in path.name
    assert path.suffix == ".csv"


def test_path_for_ocorrencias_entry(tmp_path):
    repo = DataRepository(tmp_path)
    entry = next(e for e in list_datasets("ocorrencias") if e["ext"] == "csv")
    path = repo.path_for_entry(entry)
    assert path.parent.name == "ocorrencias-cenipa"
    assert path.suffix == ".csv"


def test_path_for_aerodromo_entry(tmp_path):
    repo = DataRepository(tmp_path)
    entry = list_datasets("aero-lista-publicos")[0]
    path = repo.path_for_entry(entry)
    assert path.parent.name == "aerodromos-lista-publicos"


def test_path_for_dados_estatisticos_entry(tmp_path):
    repo = DataRepository(tmp_path)
    entry = next(
        e
        for e in list_datasets("dados-estatisticos")
        if e["id"] == "dados-estatisticos-csv"
    )
    date = dt.date(2026, 8, 9)
    path = repo.path_for_entry(entry, last_modified=date)
    assert path.parent.name == "dados-estatisticos-transporte-aereo"
    assert "dados-estatisticos-csv@20260809" in path.name
    assert path.suffix == ".csv"


def test_path_for_drones_hist_entry(tmp_path):
    repo = DataRepository(tmp_path)
    entry = next(
        e
        for e in list_datasets("drones")
        if e["year"] == 2024 and e["month"] == 3 and e["ext"] == "csv"
    )
    date = dt.date(2026, 8, 1)
    path = repo.path_for_entry(entry, last_modified=date)
    assert path.parent.name == "drones-sisant"
    assert "drones-hist_2024-03@20260801" in path.name


def test_path_for_static_entry_ignores_slug(tmp_path):
    repo = DataRepository(tmp_path)
    entry = dict(
        next(e for e in list_datasets("rab") if e["ext"] == "csv"),
    )
    entry["slug"] = "anexo-i"
    date = dt.date(2026, 6, 1)
    path = repo.path_for_entry(entry, last_modified=date)
    assert "rab-atual-csv@20260601.csv" in path.name
    assert "anexo-i" not in path.name


def test_path_for_atrasos_entry(tmp_path):
    repo = DataRepository(tmp_path)
    entry = next(
        e
        for e in list_datasets("atrasos-cancelamentos")
        if e["year"] == 2026
        and e["month"] == 6
        and e["ext"] == "csv"
        and "anexo-ii" in e["id"]
    )
    date = dt.date(2026, 8, 5)
    path = repo.path_for_entry(entry, last_modified=date)
    assert path.parent.name == "atrasos-cancelamentos"
    assert "atrasos-cancelamentos_2026-06_anexo-ii@20260805.csv" in path.name


def test_path_for_movimentacao_entry(tmp_path):
    repo = DataRepository(tmp_path)
    entry = next(
        e
        for e in list_datasets("movimentacao-aeroportuaria")
        if e["year"] == 2025 and e["month"] == 7
    )
    date = dt.date(2026, 8, 1)
    path = repo.path_for_entry(entry, last_modified=date)
    assert path.parent.name == "movimentacao-aeroportuaria"
    assert "movimentacao-aeroportuaria_2025-07@20260801" in path.name
    assert path.suffix == ".csv"


def test_path_for_recomendacoes_entry(tmp_path):
    repo = DataRepository(tmp_path)
    entry = next(
        e for e in list_datasets("recomendacoes-seguranca") if e["ext"] == "csv"
    )
    date = dt.date(2026, 8, 1)
    path = repo.path_for_entry(entry, last_modified=date)
    assert path.parent.name == "recomendacoes-seguranca"
    assert "recomendacoes-seguranca-csv@20260801" in path.name


def test_paths_are_absolute(tmp_path):
    repo = DataRepository(tmp_path)
    for entry in list_datasets("ocorrencias"):
        path = repo.path_for_entry(entry)
        assert path.is_absolute()


def test_different_entries_produce_different_paths(tmp_path):
    repo = DataRepository(tmp_path)
    entries = list_datasets("rab")
    date = dt.date(2026, 6, 1)
    paths = [repo.path_for_entry(e, last_modified=date) for e in entries]
    assert len(paths) == len(set(paths)), "Duplicate paths in rab group"


def test_vra_entries_produce_different_paths(tmp_path):
    repo = DataRepository(tmp_path)
    entries = list_datasets("vra")
    date = dt.date(2026, 6, 1)
    paths = [repo.path_for_entry(e, last_modified=date) for e in entries]
    assert len(paths) == len(set(paths)), "Duplicate paths in vra group"


def test_atrasos_anexo_variants_produce_six_distinct_stable_paths(tmp_path):
    repo = DataRepository(tmp_path)
    date = dt.date(2026, 8, 5)
    month_entries = [
        e
        for e in list_datasets("atrasos-cancelamentos")
        if e["year"] == 2001 and e["month"] == 5
    ]
    assert len(month_entries) == 6  # 3 anexos × csv/json
    names = [repo.path_for_entry(e, last_modified=date).name for e in month_entries]
    assert len(names) == len(set(names)), "Duplicate paths for atrasos anexo variants"
    for expected in (
        "atrasos-cancelamentos_2001-05_anexo-i@20260805.csv",
        "atrasos-cancelamentos_2001-05_anexo-ii@20260805.csv",
        "atrasos-cancelamentos_2001-05_anexo-iii@20260805.csv",
        "atrasos-cancelamentos_2001-05_anexo-i@20260805.json",
        "atrasos-cancelamentos_2001-05_anexo-ii@20260805.json",
        "atrasos-cancelamentos_2001-05_anexo-iii@20260805.json",
    ):
        assert expected in names


def test_all_groups_unique_local_paths(tmp_path):
    """Guarda-chuva: nenhum par de entradas any grupo pode colidir no disco.

    Observação do slug: os grupos com várias fontes por partição (como
    ``atrasos-cancelamentos``) precisam declarar ``slug`` na entrada;
    caso contrário, o caminho local colide e este teste falha.
    """
    repo = DataRepository(tmp_path)
    date = dt.date(2026, 6, 1)
    all_entries = list_datasets()
    paths = [repo.path_for_entry(e, last_modified=date) for e in all_entries]
    seen: dict[Path, str] = {}
    for entry, path in zip(all_entries, paths, strict=True):
        assert path not in seen, (
            f"Caminhos idênticos {entry['url']} e {seen[path]} → {path}"
        )
        seen[path] = entry["url"]
