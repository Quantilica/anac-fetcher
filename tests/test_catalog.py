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

_NON_AERODROMO_GROUPS = {"vra", "rab", "ocorrencias"}


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
