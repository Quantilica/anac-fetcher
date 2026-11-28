"""Typer plugin for quantilica-cli integration."""

from __future__ import annotations

import datetime as dt
import logging
from pathlib import Path
from typing import Any

import typer
from quantilica.cli.sdk import (
    PENDING_PUBLICATION_REASON,
    CheckPlan,
    FetcherApp,
    make_resolve_groups,
)
from quantilica.cli.ui import get_console
from quantilica.core.registry import FetcherInfo
from quantilica.core.sync import FreshnessPolicy

from .catalog import GROUP_ALIASES, GROUPS, list_datasets
from .pending import stale_pending_message
from .storage import DataRepository

console = get_console()
logger = logging.getLogger(__name__)


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


class AnacFetcherApp(FetcherApp):
    """``FetcherApp`` que avisa quando um período pendente está sem publicação há meses.

    As entradas ``pending_publication`` não dão erro no 404, então um nome que a
    ANAC mudou ficaria "pendente" para sempre. Um WARNING por execução (``sync`` e
    ``check``, inclusive no modo de plano) diz desde quando não há publicação; o
    código de saída não muda.
    """

    def download_datasets(
        self,
        entries: list[dict[str, Any]],
        output_dir: Path,
        workers: int = 4,
        *,
        force: bool = False,
    ) -> tuple[int, int, list[tuple[str, str]]]:
        """Baixa e avisa dos períodos pendentes que deram 404."""
        if force:
            result = super().download_datasets(
                entries, output_dir, workers=workers, force=True
            )
        else:
            result = super().download_datasets(entries, output_dir, workers=workers)
        stats = self.last_download_stats
        skipped = (
            {
                eid
                for eid, why in stats.skipped_items
                if why == PENDING_PUBLICATION_REASON
            }
            if stats is not None
            else set()
        )
        self._warn_stale([e for e in entries if str(e.get("id")) in skipped])
        return result

    def check_datasets(
        self, entries: list[dict[str, Any]], output_dir: Path, workers: int = 4
    ) -> CheckPlan:
        """Verifica o frescor e avisa dos períodos pendentes que deram 404."""
        plan = super().check_datasets(entries, output_dir, workers=workers)
        self._warn_stale(
            [
                dict(item.entry or {})
                for item in plan.items
                if item.reason == PENDING_PUBLICATION_REASON
            ]
        )
        return plan

    @staticmethod
    def _warn_stale(pending_404: list[dict[str, Any]]) -> None:
        message = stale_pending_message(pending_404)
        if message is not None:
            logger.warning("%s", message)


fetcher = AnacFetcherApp(
    name="anac-fetcher",
    help="Dados da ANAC (Agência Nacional de Aviação Civil).",
    info=FetcherInfo(
        id="anac",
        nome="ANAC - Dados Abertos",
        orgao="Agência Nacional de Aviação Civil (ANAC)",
        licenca=(
            "Sem licença declarada; dados públicos pela Lei 12.527/2011 (LAI) "
            "e Decreto 8.777/2016"
        ),
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
