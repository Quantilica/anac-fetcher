"""Tests for anac_fetcher.download."""

from pathlib import Path
from unittest.mock import patch

import pytest

from anac_fetcher.catalog import list_datasets
from anac_fetcher.download import (
    DownloadError,
    download_all,
    download_entry,
    download_group,
)
from anac_fetcher.storage import DataRepository


def test_download_entry_dry_run(tmp_path):
    """Dry-run must not call download_file and must return a valid path."""
    repo = DataRepository(tmp_path)
    entry = list_datasets("ocorrencias")[0]

    with patch("anac_fetcher.download._safe_head_date", return_value=None):
        path = download_entry(entry, repo, dry_run=True)

    assert isinstance(path, Path)
    assert not path.exists()


def test_download_entry_calls_download_with_manifest(tmp_path):
    """Verify download_entry delegates to client.download_with_manifest."""
    repo = DataRepository(tmp_path)
    entry = list_datasets("ocorrencias")[0]
    fake_path = tmp_path / "ocorrencias-cenipa" / "ocorrencias-csv.csv"

    with (
        patch("anac_fetcher.download._safe_head_date", return_value=None),
        patch(
            "anac_fetcher.download.client.download_with_manifest",
            return_value=fake_path,
        ) as mock_dl,
    ):
        download_entry(entry, repo)

    mock_dl.assert_called_once()
    call_kwargs = mock_dl.call_args
    assert call_kwargs.args[0] == entry["url"]
    assert call_kwargs.kwargs["source_id"] == "anac"
    assert call_kwargs.kwargs["producer"] == "anac-fetcher"


def test_download_all_dry_run_returns_paths(tmp_path):
    """download_all dry-run should return one path per entry without downloading."""
    with patch("anac_fetcher.download._safe_head_date", return_value=None):
        paths = download_all(tmp_path, groups=["ocorrencias"], dry_run=True)

    entries = list_datasets("ocorrencias")
    assert len(paths) == len(entries)
    for path in paths:
        assert not path.exists()


def test_download_all_unknown_group_raises(tmp_path):
    with pytest.raises(ValueError, match="Unknown group"):
        download_all(tmp_path, groups=["nonexistent"])


def test_download_group_unknown_group_raises(tmp_path):
    with pytest.raises(ValueError, match="Unknown group"):
        download_group("nonexistent", tmp_path)


def test_download_all_alias_accepted(tmp_path):
    """Group aliases (e.g., 'cenipa') should work in download_all."""
    with patch("anac_fetcher.download._safe_head_date", return_value=None):
        paths = download_all(tmp_path, groups=["cenipa"], dry_run=True)

    assert len(paths) == len(list_datasets("ocorrencias"))


def test_download_all_macro_alias_aerodromos(tmp_path):
    """The 'aerodromos' macro-alias should expand to every aero-* group."""
    from anac_fetcher.catalog_aerodromos import AERODROMO_GROUP_KEYS

    with patch("anac_fetcher.download._safe_head_date", return_value=None):
        paths = download_all(tmp_path, groups=["aerodromos"], dry_run=True)

    expected = sum(len(list_datasets(g)) for g in AERODROMO_GROUP_KEYS)
    assert len(paths) == expected


def test_download_group_macro_alias(tmp_path):
    """download_group itself should also accept a macro-alias."""
    from anac_fetcher.catalog_aerodromos import AERODROMO_GROUP_KEYS

    with patch("anac_fetcher.download._safe_head_date", return_value=None):
        paths = download_group("aerodromos", tmp_path, dry_run=True)

    expected = sum(len(list_datasets(g)) for g in AERODROMO_GROUP_KEYS)
    assert len(paths) == expected


def test_download_group_continues_after_entry_failure(tmp_path):
    """A failing entry must not abort the rest of the group (regression:
    previously one bad URL aborted every remaining file in the group)."""
    entries = list_datasets("ocorrencias")
    assert len(entries) == 2
    call_count = 0

    def fake_download(url, output, **kwargs):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            raise RuntimeError("boom")
        return output

    errors: list[DownloadError] = []
    with (
        patch("anac_fetcher.download._safe_head_date", return_value=None),
        patch(
            "anac_fetcher.download.client.download_with_manifest",
            side_effect=fake_download,
        ),
    ):
        paths = download_group("ocorrencias", tmp_path, errors=errors)

    assert len(paths) == 1
    assert len(errors) == 1
    assert errors[0][0]["id"] == entries[0]["id"]
    assert isinstance(errors[0][1], RuntimeError)


def test_download_all_continues_after_group_failure(tmp_path):
    """A group where every entry fails must not stop subsequent groups."""
    with (
        patch("anac_fetcher.download._safe_head_date", return_value=None),
        patch(
            "anac_fetcher.download.client.download_with_manifest",
            side_effect=RuntimeError("boom"),
        ),
    ):
        errors: list[DownloadError] = []
        paths = download_all(
            tmp_path, groups=["ocorrencias", "aero-lista-publicos"], errors=errors
        )

    assert paths == []
    assert len(errors) == len(list_datasets("ocorrencias")) + len(
        list_datasets("aero-lista-publicos")
    )


def test_download_group_without_errors_list_does_not_raise(tmp_path):
    """Without an ``errors`` list, a failing entry is skipped, not raised."""
    with (
        patch("anac_fetcher.download._safe_head_date", return_value=None),
        patch(
            "anac_fetcher.download.client.download_with_manifest",
            side_effect=RuntimeError("boom"),
        ),
    ):
        paths = download_group("aero-lista-publicos", tmp_path)

    assert paths == []
