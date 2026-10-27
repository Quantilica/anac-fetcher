"""Typer plugin for quantilica-cli integration."""

from __future__ import annotations

import datetime as dt
from pathlib import Path
from typing import Any

import typer
from quantilica.cli.sdk import FetcherApp, make_resolve_groups

from .catalog import GROUP_ALIASES, GROUPS, list_datasets
from .storage import DataRepository

# Resolver canônico — make_resolve_groups espera alias -> lista de ids canônicos.
resolve_groups = make_resolve_groups(
    GROUPS, {alias: [canon] for alias, canon in GROUP_ALIASES.items()}
)


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


def _resolve_groups(groups: list[str] | None) -> list[str]:
    """Resolve nomes de grupo/aliases para ids canônicos; None → todos.

    Delega ao ``make_resolve_groups`` canônico do ``quantilica.cli.sdk``.

    Args:
        groups (list[str] | None): Nomes ou aliases de grupo informados na CLI.

    Returns:
        list[str]: Ids canônicos dos grupos.

    Raises:
        typer.BadParameter: Se um grupo não for reconhecido.
    """
    try:
        return resolve_groups(groups)
    except ValueError as exc:
        raise typer.BadParameter(str(exc)) from None


fetcher = FetcherApp(
    name="anac-fetcher",
    help="Dados da ANAC (Agência Nacional de Aviação Civil).",
    groups_dict=GROUPS,
    aliases_dict=GROUP_ALIASES,
    list_datasets=list_datasets,
    path_builder=path_builder,
)


def convert(
    input_dir: Path,
    lake_dir: Path,
    *,
    dataset: list[str] | None = None,
    force: bool = False,
) -> Any:
    """Converte arquivos brutos da ANAC para o lake Hive (Parquet)."""
    from anac_fetcher import lake

    return lake.converter.convert(input_dir, lake_dir, datasets=dataset, force=force)


fetcher.command_convert(convert)
fetcher.command_pipeline(convert)

app = fetcher.app
