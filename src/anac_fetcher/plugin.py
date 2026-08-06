"""Typer plugin for quantilica-cli integration."""

from __future__ import annotations

import threading
from pathlib import Path
from typing import Annotated

import typer
from quantilica.core.cli import (
    get_console,
    make_batch_progress,
    make_download_progress,
    setup_rich_logging,
)
from rich.console import Group
from rich.live import Live
from rich.table import Table

from .catalog import ALL_GROUP_KEYS, GROUP_ALIASES, GROUPS, expand_group, list_datasets
from .download import download_entry
from .storage import DataRepository

app = typer.Typer(help="Dados da ANAC (Agência Nacional de Aviação Civil).")
console = get_console()

_DEFAULT_OUTPUT = Path("/data/anac")

_ALL_KEYS = ALL_GROUP_KEYS + list(GROUP_ALIASES) + ["aerodromos"]


@app.command("sync")
def sync(
    groups: Annotated[
        list[str] | None,
        typer.Argument(
            help=(
                "Grupos a baixar: vra, rab, ocorrencias, aerodromos (todos os "
                "grupos de aeródromos) ou um grupo específico de aeródromo "
                "(aero-lista-publicos, aero-pistas-pouso, ...). Padrão: todos."
            ),
        ),
    ] = None,
    output: Annotated[
        Path, typer.Option("-o", "--output", help="Diretório de saída")
    ] = _DEFAULT_OUTPUT,
    dry_run: Annotated[
        bool, typer.Option("--dry-run", help="Listar arquivos sem baixar")
    ] = False,
    sleeptime: Annotated[
        float,
        typer.Option(
            "--sleeptime",
            help=(
                "Pausa (segundos) entre downloads dentro de um grupo, "
                "como cortesia ao servidor em lotes grandes (ex.: grupo "
                "rab, ~250 arquivos)."
            ),
        ),
    ] = 0.3,
    workers: Annotated[int, typer.Option("--workers", help="Downloads paralelos")] = 4,
    verbose: Annotated[bool, typer.Option("--verbose", help="Logs detalhados")] = False,
) -> None:
    """Sincronizar dados da ANAC (VRA, RAB, ocorrências, aeródromos)."""
    setup_rich_logging(verbose, console=console)

    target_groups: list[str] = []
    for g in groups or ALL_GROUP_KEYS:
        expanded = expand_group(g)
        if not expanded:
            console.print(f"[red]Grupo desconhecido: {g!r}[/red]")
            console.print(f"Grupos válidos: {', '.join(_ALL_KEYS)}")
            raise typer.Exit(1)
        for canon in expanded:
            if canon not in target_groups:
                target_groups.append(canon)

    entries = [e for g in target_groups for e in list_datasets(g)]
    total = len(entries)

    if dry_run:
        table = Table("Grupo", "ID", "URL", title="Arquivos a baixar (dry-run)")
        for e in entries:
            table.add_row(e["group"], e["id"], e["url"])
        console.print(table)
        console.print(f"\n[bold]{total}[/bold] arquivo(s) listado(s).")
        return

    repo = DataRepository(output)
    lock = threading.Lock()
    download_errors: list[tuple[str, str]] = []

    overall = make_batch_progress(console)
    file_prog = make_download_progress(console)
    overall_task = overall.add_task("[cyan]Baixando...[/cyan]", total=total)

    worker_task_ids = [
        file_prog.add_task("[dim]Inativo[/dim]", total=1) for _ in range(workers)
    ]
    available_tasks = worker_task_ids.copy()

    import concurrent.futures
    import time

    def _worker(i: int, entry: dict) -> bool:
        if sleeptime > 0 and i > 0 and not dry_run:
            time.sleep(sleeptime)

        with lock:
            task_id = available_tasks.pop(0)

        def cb(downloaded_bytes: int, total_bytes: int) -> None:
            if downloaded_bytes == 0 and total_bytes == 0:
                file_prog.update(task_id, completed=0)
                return
            file_prog.update(
                task_id,
                description=f"[cyan]{entry['id']}[/cyan]",
                completed=downloaded_bytes,
                total=total_bytes or None,
            )

        try:
            download_entry(entry, repo, dry_run=dry_run, progress=cb)
            return True
        except Exception as exc:
            with lock:
                download_errors.append((entry["id"], str(exc)))
            return False
        finally:
            with lock:
                file_prog.update(
                    task_id, description="[dim]Inativo[/dim]", completed=0, total=1
                )
                available_tasks.append(task_id)

    downloaded = 0
    try:
        with Live(Group(overall, file_prog), console=console, refresh_per_second=10):
            with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
                futures = {
                    executor.submit(_worker, i, entry): entry
                    for i, entry in enumerate(entries)
                }
                for future in concurrent.futures.as_completed(futures):
                    overall.update(overall_task, advance=1)
                    if future.result():
                        downloaded += 1

        errors = download_errors

    except KeyboardInterrupt:
        console.print("\n[yellow]Interrompido.[/yellow]")
        raise typer.Exit(130) from None

    console.print(
        f"\n[green]Concluído:[/green] {downloaded}/{total} arquivo(s) baixado(s)."
    )
    if errors:
        console.print(f"[red]{len(errors)} erro(s):[/red]")
        for eid, emsg in errors:
            console.print(f"  {eid}: {emsg}")


@app.command("list")
def cmd_list(
    verbose: Annotated[bool, typer.Option("--verbose", help="Logs detalhados")] = False,
) -> None:
    """Listar todos os datasets disponíveis no catálogo."""
    setup_rich_logging(verbose, console=console)

    for group_id, group_info in GROUPS.items():
        table = Table(
            "ID",
            "Partição",
            "Extensão",
            "URL",
            title=f"[bold]{group_id}[/bold] — {group_info['name']}",
        )
        for entry in group_info["entries"]:
            if entry["month"] is not None:
                partition = f"{entry['year']}-{entry['month']:02d}"
            elif entry["year"] is not None:
                partition = str(entry["year"])
            else:
                partition = "—"
            table.add_row(entry["id"], partition, entry["ext"], entry["url"])
        console.print(table)

    total = sum(len(g["entries"]) for g in GROUPS.values())
    console.print(f"\n[bold]{total}[/bold] dataset(s) no catálogo.")
