"""Tests for anac_fetcher.catalog."""

import pytest

from anac_fetcher.catalog import (
    ALL_GROUP_KEYS,
    GROUPS,
    expand_group,
    list_datasets,
    resolve_group,
)
from anac_fetcher.catalog_aerodromos import AERODROMO_GROUP_KEYS

_NON_AERODROMO_GROUPS = {
    "vra",
    "rab",
    "ocorrencias",
    "dados-estatisticos",
    "drones",
    "atrasos-cancelamentos",
    "empresas-aereas",
    "movimentacao-aeroportuaria",
    "recomendacoes-seguranca",
}


def test_all_groups_present():
    assert _NON_AERODROMO_GROUPS <= set(GROUPS)
    assert set(AERODROMO_GROUP_KEYS) <= set(GROUPS)
    assert set(ALL_GROUP_KEYS) == set(GROUPS)


def test_each_group_has_name_and_entries():
    for key, info in GROUPS.items():
        assert info["name"], f"Group {key!r} missing name"
        assert len(info["entries"]) > 0, f"Group {key!r} has no entries"


def test_entry_fields_complete():
    required = {
        "id",
        "base_id",
        "name",
        "url",
        "ext",
        "group",
        "source",
        "year",
        "semester",
        "month",
    }
    for entry in list_datasets():
        missing = required - entry.keys()
        assert not missing, f"Entry {entry['id']!r} missing fields: {missing}"


def test_entry_urls_start_with_https():
    for entry in list_datasets():
        assert entry["url"].startswith("https://"), (
            f"Entry {entry['id']!r} has non-https URL: {entry['url']}"
        )


def test_entry_urls_have_no_raw_spaces_or_accents():
    for entry in list_datasets():
        for ch in entry["url"]:
            assert ch.isascii(), (
                f"Entry {entry['id']!r} has a non-ASCII char in URL: {entry['url']}"
            )
        assert " " not in entry["url"], f"Entry {entry['id']!r} has a raw space"


def test_no_duplicate_ids():
    all_entries = list_datasets()
    ids = [e["id"] for e in all_entries]
    assert len(ids) == len(set(ids)), "Duplicate entry IDs found"


def test_no_duplicate_urls_within_group():
    for group_id, info in GROUPS.items():
        urls = [e["url"] for e in info["entries"]]
        assert len(urls) == len(set(urls)), f"Duplicate URLs in group {group_id!r}"


# ---------------------------------------------------------------------------
# VRA
# ---------------------------------------------------------------------------


def test_vra_entries_have_month_and_ext():
    for entry in GROUPS["vra"]["entries"]:
        assert entry["month"] in range(1, 13)
        assert entry["semester"] is None
        assert entry["year"] is not None
        assert entry["ext"] in ("csv", "json")


def test_vra_covers_year_2000():
    years = {e["year"] for e in GROUPS["vra"]["entries"]}
    assert 2000 in years


def test_vra_url_pattern():
    entry = next(
        e
        for e in GROUPS["vra"]["entries"]
        if e["year"] == 2015 and e["month"] == 11 and e["ext"] == "csv"
    )
    assert entry["url"].endswith("VRA_201511.csv")


def test_vra_alias():
    assert resolve_group("voo-regular-ativo") == "vra"


# ---------------------------------------------------------------------------
# RAB
# ---------------------------------------------------------------------------


def test_rab_current_snapshot_entries():
    static = [e for e in GROUPS["rab"]["entries"] if e["year"] is None]
    assert len(static) == 3
    exts = {e["ext"] for e in static}
    assert exts == {"csv", "json", "xls"}


def test_rab_historical_entries_have_month():
    hist = [e for e in GROUPS["rab"]["entries"] if e["year"] is not None]
    assert len(hist) > 0
    for e in hist:
        assert e["month"] in range(1, 13)
        assert e["semester"] is None


def test_rab_missing_month_excluded():
    assert not any(
        e["year"] == 2019 and e["month"] == 5 for e in GROUPS["rab"]["entries"]
    )


def test_rab_csv_only_since_2024_09():
    csv_entries = [
        e
        for e in GROUPS["rab"]["entries"]
        if e["ext"] == "csv" and e["year"] is not None
    ]
    assert all((e["year"], e["month"]) >= (2024, 9) for e in csv_entries)


def test_rab_alias():
    assert resolve_group("aeronaves") == "rab"


# ---------------------------------------------------------------------------
# Ocorrências (CENIPA)
# ---------------------------------------------------------------------------


def test_ocorrencias_count():
    entries = GROUPS["ocorrencias"]["entries"]
    assert len(entries) == 2
    exts = {e["ext"] for e in entries}
    assert exts == {"csv", "json"}
    assert all(e["year"] is None for e in entries)


def test_ocorrencias_alias():
    assert resolve_group("cenipa") == "ocorrencias"


# ---------------------------------------------------------------------------
# Aeródromos
# ---------------------------------------------------------------------------


def test_aerodromo_group_count():
    assert len(AERODROMO_GROUP_KEYS) == 14


def test_aerodromo_groups_all_static():
    for group_id in AERODROMO_GROUP_KEYS:
        for e in GROUPS[group_id]["entries"]:
            assert e["year"] is None
            assert e["semester"] is None
            assert e["month"] is None


def test_expand_group_macro_aerodromos():
    expanded = expand_group("aerodromos")
    assert set(expanded) == set(AERODROMO_GROUP_KEYS)
    for group_id in expanded:
        assert len(list_datasets(group_id)) > 0


def test_aero_pzr_has_two_datasets():
    entries = GROUPS["aero-pzr"]["entries"]
    ids = {e["base_id"] for e in entries}
    assert ids == {
        "aero-pzr-pzr-pbzr-csv",
        "aero-pzr-pzr-pbzr-json",
        "aero-pzr-pzr-pezr-csv",
        "aero-pzr-pzr-pezr-json",
    }


# ---------------------------------------------------------------------------
# Dados Estatísticos do Transporte Aéreo
# ---------------------------------------------------------------------------


def test_dados_estatisticos_count():
    entries = GROUPS["dados-estatisticos"]["entries"]
    assert len(entries) == 4
    assert all(e["year"] is None for e in entries)
    assert {e["ext"] for e in entries} == {"csv", "json"}


def test_dados_estatisticos_url_pattern():
    csv = next(e for e in GROUPS["dados-estatisticos"]["entries"] if e["ext"] == "csv")
    assert csv["url"].endswith("Dados_Estatisticos.csv")
    decade = next(
        e for e in GROUPS["dados-estatisticos"]["entries"] if "2000_a_2010" in e["url"]
    )
    assert decade["ext"] == "json"


def test_dados_estatisticos_alias():
    assert resolve_group("estatisticas") == "dados-estatisticos"


# ---------------------------------------------------------------------------
# Drones (SISANT)
# ---------------------------------------------------------------------------


def test_drones_has_snapshot_and_historical():
    entries = GROUPS["drones"]["entries"]
    static = [e for e in entries if e["year"] is None]
    assert len(static) == 2
    assert {e["ext"] for e in static} == {"csv", "json"}

    hist = [e for e in entries if e["year"] is not None]
    assert len(hist) > 0
    assert min((e["year"], e["month"]) for e in hist) == (2022, 8)


def test_drones_hist_url_pattern():
    entry = next(
        e
        for e in GROUPS["drones"]["entries"]
        if e["year"] == 2024 and e["month"] == 3 and e["ext"] == "csv"
    )
    assert entry["url"].endswith("Historico/SISANT_032024.csv")


def test_drones_alias():
    assert resolve_group("sisant") == "drones"


# ---------------------------------------------------------------------------
# Atrasos e cancelamentos
# ---------------------------------------------------------------------------


def test_atrasos_covers_year_2000_and_has_three_anexos():
    entries = GROUPS["atrasos-cancelamentos"]["entries"]
    years = {e["year"] for e in entries}
    assert 2000 in years

    jan_2000 = [e for e in entries if e["year"] == 2000 and e["month"] == 1]
    assert len(jan_2000) == 6  # 3 anexos × csv/json
    anexos = {e["name"].split("Anexo ")[1].split(" ")[0] for e in jan_2000}
    assert anexos == {"I", "II", "III"}


def test_atrasos_url_pattern():
    entry = next(
        e
        for e in GROUPS["atrasos-cancelamentos"]["entries"]
        if e["year"] == 2026 and e["month"] == 6 and e["ext"] == "json"
    )
    assert "Percentuais%20de%20atrasos%20e%20cancelamentos" in entry["url"]
    assert "06%20-%20junho" in entry["url"]
    assert entry["url"].endswith(".json")


def test_atrasos_alias():
    assert resolve_group("atrasos") == "atrasos-cancelamentos"


# ---------------------------------------------------------------------------
# Empresas Aéreas
# ---------------------------------------------------------------------------


def test_empresas_aereas_count():
    entries = GROUPS["empresas-aereas"]["entries"]
    assert len(entries) == 2
    assert {e["ext"] for e in entries} == {"csv", "json"}
    assert all(e["year"] is None for e in entries)


def test_empresas_aereas_url_pattern():
    csv = next(e for e in GROUPS["empresas-aereas"]["entries"] if e["ext"] == "csv")
    assert csv["url"].endswith("pda_empresas_aereas_nacionais.csv")


def test_empresas_aereas_alias():
    assert resolve_group("empresas") == "empresas-aereas"


# ---------------------------------------------------------------------------
# Movimentação Aeroportuária
# ---------------------------------------------------------------------------


def test_movimentacao_csv_only_and_starts_2019():
    entries = GROUPS["movimentacao-aeroportuaria"]["entries"]
    assert len(entries) > 0
    assert all(e["ext"] == "csv" for e in entries)
    assert min(e["year"] for e in entries) == 2019
    assert all(e["month"] in range(1, 13) for e in entries)


def test_movimentacao_url_pattern():
    entry = next(
        e
        for e in GROUPS["movimentacao-aeroportuaria"]["entries"]
        if e["year"] == 2025 and e["month"] == 7
    )
    assert entry["url"].endswith("2025/Movimentacoes_Aeroportuarias_202507.csv")


def test_movimentacao_alias():
    assert resolve_group("movimentacao") == "movimentacao-aeroportuaria"


# ---------------------------------------------------------------------------
# Recomendações de Segurança
# ---------------------------------------------------------------------------


def test_recomendacoes_count():
    entries = GROUPS["recomendacoes-seguranca"]["entries"]
    assert len(entries) == 2
    assert {e["ext"] for e in entries} == {"csv", "json"}
    assert all(e["year"] is None for e in entries)


def test_recomendacoes_url_pattern():
    csv = next(
        e for e in GROUPS["recomendacoes-seguranca"]["entries"] if e["ext"] == "csv"
    )
    assert csv["url"].endswith("RECOMENDACAO_SEGURANCA.csv")


def test_recomendacoes_alias():
    assert resolve_group("recomendacoes") == "recomendacoes-seguranca"


# ---------------------------------------------------------------------------
# resolve_group / expand_group / list_datasets
# ---------------------------------------------------------------------------


def test_resolve_canonical_keys():
    for key in ALL_GROUP_KEYS:
        assert resolve_group(key) == key


def test_resolve_unknown_returns_none():
    assert resolve_group("nonexistent") is None


def test_expand_group_unknown_returns_empty():
    assert expand_group("nonexistent") == []


def test_expand_group_single_group_is_singleton_list():
    assert expand_group("vra") == ["vra"]


def test_list_datasets_all():
    all_entries = list_datasets()
    assert len(all_entries) > 0
    groups_present = {e["group"] for e in all_entries}
    assert groups_present == set(ALL_GROUP_KEYS)


def test_list_datasets_filtered():
    entries = list_datasets("ocorrencias")
    assert all(e["group"] == "ocorrencias" for e in entries)
    assert len(entries) == 2

    via_alias = list_datasets("cenipa")
    assert entries == via_alias


def test_list_datasets_unknown_group_raises():
    with pytest.raises(ValueError, match="Unknown group"):
        list_datasets("bogus")
