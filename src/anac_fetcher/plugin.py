"""Typer plugin for quantilica-cli integration."""

from __future__ import annotations

import datetime as dt
from pathlib import Path
from typing import Any

from quantilica.cli.sdk import FetcherApp

from .catalog import GROUP_ALIASES, GROUPS, list_datasets
from .storage import DataRepository


def path_builder(
    output_dir: Path, entry: dict[str, Any], last_modified: dt.date | None
) -> Path:
    """Build the local storage path for a dataset entry.

    Args:
        output_dir: The base output directory for downloaded files.
        entry: The dataset entry metadata dict.
        last_modified: Optional date representing when the remote file was
            last modified.

    Returns:
        The absolute Path where the file should be saved.
    """
    return DataRepository(output_dir).path_for_entry(entry, last_modified=last_modified)


fetcher = FetcherApp(
    name="anac-fetcher",
    help="Dados da ANAC (Agência Nacional de Aviação Civil).",
    groups_dict=GROUPS,
    aliases_dict=GROUP_ALIASES,
    list_datasets=list_datasets,
    path_builder=path_builder,
)

app = fetcher.app
