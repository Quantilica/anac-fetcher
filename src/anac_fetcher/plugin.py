"""Typer plugin for quantilica-cli integration."""

from __future__ import annotations

import datetime as dt
from pathlib import Path
from typing import Any

import typer
from quantilica.cli.sdk import FetcherApp, make_resolve_groups
from quantilica.cli.ui import get_console
from quantilica.core.registry import FetcherInfo
from quantilica.core.sync import FreshnessPolicy

from .catalog import GROUP_ALIASES, GROUPS, list_datasets
from .storage import DataRepository

console = get_console()


def _out(text: str) -> None:
    """Imprime texto literal no console Rich compartilhado (sem markup/quebra)."""
    console.print(text, markup=False, highlight=False, emoji=False, soft_wrap=True)


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
    info=FetcherInfo(
        id="anac",
        nome="ANAC - Dados Abertos",
        orgao="Agência Nacional de Aviação Civil (ANAC)",
        homepage="https://www.gov.br/anac/",
        cadencia="daily",
        dominio="transporte",
    ),
    groups_dict=GROUPS,
    aliases_dict=GROUP_ALIASES,
    list_datasets=list_datasets,
    path_builder=path_builder,
    default_output=Path("/data/anac"),
    freshness_policy=FreshnessPolicy.HEAD_FALLBACK_GET,
)


def convert(
    input_dir: Path,
    lake_dir: Path,
    *,
    dataset: list[str] | None = None,
    force: bool = False,
) -> Any:
    """Converte arquivos brutos da ANAC para o lake Hive (Parquet)."""
    try:
        from anac_fetcher import lake
    except ImportError as exc:
        raise ImportError(
            "Conversão para o lake requer o extra 'analysis'. "
            "Instale com: quantilica install anac --extra analysis"
        ) from exc

    return lake.converter.convert(input_dir, lake_dir, datasets=dataset, force=force)


def discover_cmd(
    as_json: bool = typer.Option(False, "--json", help="Saída em JSON"),
    fail_on_change: bool = typer.Option(
        False, "--fail-on-change", help="Sai com código 1 se houver novidade"
    ),
) -> None:
    """Detecta meses de movimentação publicados além do catálogo."""
    import json

    from .discover import discover

    report = discover()
    if as_json:
        _out(json.dumps(report.to_dict(), ensure_ascii=False, indent=2))
    else:
        _out(f"Catálogo vai até {report.last_published_catalog}.")
        for month in report.new_months:
            _out(f"NOVO     movimentacao-{month}")
        if not report.has_changes:
            _out("Sem novidades em relação ao catálogo.")
    if fail_on_change and report.has_changes:
        raise typer.Exit(1)


fetcher.attach_command(discover_cmd, name="discover")
fetcher.command_convert(convert)
fetcher.command_pipeline(convert)

app = fetcher.app
