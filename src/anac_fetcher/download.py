"""Download functions for anac-fetcher."""

import concurrent.futures
import contextlib
import datetime as dt
import time
from collections.abc import Callable
from pathlib import Path

from quantilica.core.http import HttpClient, ProgressCallback
from quantilica.core.logging import get_logger
from quantilica.core.progress import file_progress

from .catalog import DatasetEntry, expand_group, list_datasets
from .storage import DataRepository

logger = get_logger(__name__)

# (entry, exception) pairs for datasets that failed to download.
DownloadError = tuple[DatasetEntry, Exception]

client = HttpClient(
    timeout=180.0,
    verify=True,
    attempts=5,
    retry_base_delay=2.0,
    headers={
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/142.0.0.0 Safari/537.36"
        ),
    },
)


def _safe_head_date(url: str) -> dt.date | None:
    with contextlib.suppress(Exception):
        return client.head_last_modified_date(url)
    return None


def download_file(
    url: str,
    output: Path,
    *,
    progress: ProgressCallback | None = None,
) -> Path:
    """Download a single file, writing atomically with a manifest."""
    dataset_id = output.parent.name
    return client.download_with_manifest(
        url,
        output,
        source_id="anac",
        dataset_id=dataset_id,
        producer="anac-fetcher",
        progress=progress,
    )


def download_entry(
    entry: DatasetEntry,
    repo: DataRepository,
    *,
    dry_run: bool = False,
    show_progress: bool = False,
    progress: ProgressCallback | None = None,
) -> Path:
    """Download one dataset entry and return the destination path."""
    last_modified = _safe_head_date(entry["url"])
    output = repo.path_for_entry(entry, last_modified=last_modified)
    if dry_run:
        return output
    if progress is not None:
        return download_file(entry["url"], output, progress=progress)
    if show_progress:
        with file_progress(output.name) as progress_cb:
            return download_file(entry["url"], output, progress=progress_cb)
    return download_file(entry["url"], output)


def download_group(
    group_id: str,
    output: Path,
    *,
    dry_run: bool = False,
    show_progress: bool = False,
    errors: list[DownloadError] | None = None,
    sleep: float = 0.0,
    workers: int = 4,
    on_bytes: Callable[[str, int, int], None] | None = None,
) -> list[Path]:
    """Download all datasets for one group (sequential or parallel if workers>1)."""
    return download_all(
        output,
        groups=[group_id],
        dry_run=dry_run,
        show_progress=show_progress,
        errors=errors,
        sleep=sleep,
        workers=workers,
        on_bytes=on_bytes,
    )


def download_all(
    output: Path,
    *,
    groups: list[str] | None = None,
    dry_run: bool = False,
    show_progress: bool = False,
    errors: list[DownloadError] | None = None,
    sleep: float = 0.0,
    workers: int = 4,
    on_bytes: Callable[[str, int, int], None] | None = None,
) -> list[Path]:
    """Download all (or selected) groups, in parallel."""
    from .catalog import ALL_GROUP_KEYS

    target_groups = groups if groups is not None else ALL_GROUP_KEYS
    resolved: list[str] = []
    for g in target_groups:
        expanded = expand_group(g)
        if not expanded:
            raise ValueError(f"Unknown group: {g!r}")
        for canon in expanded:
            if canon not in resolved:
                resolved.append(canon)

    entries = [e for g in resolved for e in list_datasets(g)]
    repo = DataRepository(output)
    paths: list[Path] = []

    def _do_download(i: int, entry: DatasetEntry) -> Path | None:
        if sleep > 0 and i > 0 and not dry_run:
            time.sleep(sleep)
        try:
            progress_cb = None
            if on_bytes is not None:

                def progress_cb(dl: int, tot: int) -> None:
                    on_bytes(entry["id"], dl, tot)

            # fallback to legacy show_progress if no on_bytes given
            # if we are parallelizing and show_progress is true
            # (from raw cli), it will be messy,
            # but usually cli uses rich now.
            if progress_cb is not None:
                return download_entry(
                    entry, repo, dry_run=dry_run, progress=progress_cb
                )
            elif show_progress:
                return download_entry(
                    entry, repo, dry_run=dry_run, show_progress=show_progress
                )
            else:
                return download_entry(entry, repo, dry_run=dry_run)
        except Exception as exc:
            logger.warning("Failed to download %s: %s", entry["id"], exc)
            if errors is not None:
                errors.append((entry, exc))
            return None

    # Handle single worker cleanly (e.g. maybe progress bars rely on it)
    if workers <= 1:
        for i, entry in enumerate(entries):
            res = _do_download(i, entry)
            if res:
                paths.append(res)
        return paths

    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        future_to_entry = {
            executor.submit(_do_download, i, entry): entry
            for i, entry in enumerate(entries)
        }
        for future in concurrent.futures.as_completed(future_to_entry):
            res = future.result()
            if res:
                paths.append(res)

    return paths
