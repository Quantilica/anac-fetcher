"""Tests for anac_fetcher.storage."""

import datetime as dt

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


def test_path_for_atrasos_entry(tmp_path):
    repo = DataRepository(tmp_path)
    entry = next(
        e
        for e in list_datasets("atrasos-cancelamentos")
        if e["year"] == 2026 and e["month"] == 6 and e["ext"] == "csv"
    )
    date = dt.date(2026, 8, 5)
    path = repo.path_for_entry(entry, last_modified=date)
    assert path.parent.name == "atrasos-cancelamentos"
    assert "atrasos-cancelamentos_2026-06@20260805" in path.name


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
