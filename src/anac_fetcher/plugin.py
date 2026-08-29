"""Typer plugin for quantilica-cli integration."""

from __future__ import annotations

import datetime as dt
from pathlib import Path
from typing import Annotated, Any

import typer
from quantilica.cli.sdk import FetcherApp

from .catalog import GROUP_ALIASES, GROUPS, list_datasets, resolve_group
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


def _resolve_groups(groups: list[str] | None) -> list[str]:
    """Resolve nomes de grupo/aliases para ids canônicos; None → todos.

    Args:
        groups (list[str] | None): Nomes ou aliases de grupo informados na CLI.

    Returns:
        list[str]: Ids canônicos dos grupos.

    Raises:
        typer.BadParameter: Se um grupo não for reconhecido.
    """
    if groups is None:
        return list(GROUPS)
    resolved: list[str] = []
    for name in groups:
        canon = resolve_group(name)
        if canon is None:
            raise typer.BadParameter(f"Grupo desconhecido: {name!r}")
        resolved.append(canon)
    return resolved


fetcher = FetcherApp(
    name="anac-fetcher",
    help="Dados da ANAC (Agência Nacional de Aviação Civil).",
    groups_dict=GROUPS,
    aliases_dict=GROUP_ALIASES,
    list_datasets=list_datasets,
    path_builder=path_builder,
)

app = fetcher.app


@app.command("convert")
def cmd_convert(
    groups: Annotated[
        list[str] | None,
        typer.Argument(help="Grupos a converter. Use 'list'. Omitir para todos."),
    ] = None,
    input: Annotated[
        Path,
        typer.Option("-i", "--input", help="Diretório de origem com arquivos brutos"),
    ] = Path("/data/anac"),
    output: Annotated[
        Path,
        typer.Option("-o", "--output", help="Diretório de destino para Parquet"),
    ] = Path("/data/anac"),
    verbose: Annotated[bool, typer.Option("--verbose", help="Logs detalhados")] = False,
) -> None:
    """Converter arquivos brutos da ANAC para Parquet.

    Args:
        groups (list[str] | None): Groups to convert.
        input (Path): Origin directory with raw files.
        output (Path): Destination directory for Parquet files.
        verbose (bool): Enable verbose logging.

    Raises:
        typer.Exit: If the analysis extras are not installed.
    """
    from quantilica.cli.ui import setup_rich_logging

    setup_rich_logging(
        verbose,
        console=fetcher.app.console if hasattr(fetcher.app, "console") else None,
    )

    try:
        from .wrangling import convert_group
    except ImportError:
        from quantilica.cli.ui import get_console

        get_console().print(
            "[red]Erro:[/red] convert requer extras de análise: "
            "pip install anac-fetcher[analysis]"
        )
        raise typer.Exit(1) from None

    target_groups = _resolve_groups(groups)
    converted = convert_group(target_groups, input, output)

    from quantilica.cli.ui import get_console

    get_console().print(
        f"[green]✓[/green] Conversão concluída: [bold]{converted}[/bold] "
        f"Parquet(s) em [dim]{output}[/dim]."
    )


@app.command("pipeline")
def cmd_pipeline(
    ctx: typer.Context,
    groups: Annotated[
        list[str] | None,
        typer.Argument(
            help="Grupos a baixar. Use 'list' para ver disponíveis. Omitir para todos."
        ),
    ] = None,
    output: Annotated[
        Path | None, typer.Option("-o", "--output", help="Diretório de saída")
    ] = None,
    parquet_dir: Annotated[
        Path | None,
        typer.Option(
            "--parquet-dir",
            help="Diretório para os Parquet (padrão: igual a --output)",
        ),
    ] = None,
    dry_run: Annotated[
        bool, typer.Option("--dry-run", help="Listar arquivos sem baixar")
    ] = False,
    workers: Annotated[int, typer.Option("--workers", help="Downloads paralelos")] = 4,
    verbose: Annotated[bool, typer.Option("--verbose", help="Logs detalhados")] = False,
) -> None:
    """Pipeline completo: sync seguido de convert.

    Args:
        ctx (typer.Context): The Typer context.
        groups (list[str] | None): Groups to download.
        output (Path | None): Output directory for raw files.
        parquet_dir (Path | None): Output directory for Parquet files.
        dry_run (bool): If True, only lists files without downloading.
        workers (int): Number of parallel downloads.
        verbose (bool): Enable verbose logging.

    Raises:
        typer.Exit: If the analysis extras are not installed.
    """
    from quantilica.cli.ui import get_console, setup_rich_logging
    from rich.rule import Rule

    console = get_console()
    setup_rich_logging(verbose, console=console)

    parquet_out = parquet_dir or output or Path("/data/anac")

    console.print(Rule("[bold]Passo 1/2: Download[/bold]"))
    sync_cmd = next(c.callback for c in app.registered_commands if c.name == "sync")
    ctx.invoke(
        sync_cmd,
        groups=groups,
        output=output,
        dry_run=dry_run,
        workers=workers,
        verbose=verbose,
    )

    if dry_run:
        return

    console.print(Rule("[bold]Passo 2/2: Conversão[/bold]"))

    try:
        from .wrangling import convert_group
    except ImportError:
        console.print(
            "[red]Erro:[/red] pipeline (conversão) requer extras de análise: "
            "pip install anac-fetcher[analysis]"
        )
        raise typer.Exit(1) from None

    target_groups = _resolve_groups(groups)
    converted = convert_group(target_groups, output or Path("/data/anac"), parquet_out)
    console.print(
        f"[green]✓[/green] {converted} Parquet(s) salvo(s) em [dim]{parquet_out}[/dim]"
    )
