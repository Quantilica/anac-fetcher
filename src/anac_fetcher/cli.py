"""Standalone command-line interface for anac-fetcher."""

import argparse
import logging
import sys
from pathlib import Path

from quantilica.core.logging import configure_cli_logging

from . import __version__
from .catalog import ALL_GROUP_KEYS, GROUP_ALIASES, expand_group, list_datasets
from .download import DownloadError, download_all

_DEFAULT_OUTPUT = Path("/data/anac")
_ALL_KEYS = ALL_GROUP_KEYS + list(GROUP_ALIASES) + ["aerodromos"]


def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="anac-fetcher",
        description="Download de dados abertos da ANAC (aviação civil).",
    )
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )

    subparsers = parser.add_subparsers(dest="command", metavar="COMMAND")

    # sync
    sync_parser = subparsers.add_parser("sync", help="Sincronizar datasets")
    sync_parser.add_argument(
        "groups",
        nargs="*",
        metavar="GRUPO",
        help=(
            "Grupos a baixar: vra, rab, ocorrencias, aerodromos (todos os "
            "grupos de aeródromos) ou um grupo específico de aeródromo "
            "(aero-lista-publicos, aero-pistas-pouso, ...). Padrão: todos."
        ),
    )
    sync_parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=_DEFAULT_OUTPUT,
        metavar="DIR",
        help="Diretório de saída (padrão: /data/anac)",
    )
    sync_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Listar arquivos sem baixar",
    )
    sync_parser.add_argument(
        "--sleeptime",
        type=float,
        default=0.3,
        metavar="SEGUNDOS",
        help=(
            "Pausa entre downloads dentro de um grupo (padrão: 0.3s), "
            "como cortesia ao servidor em lotes grandes (ex.: grupo rab, "
            "~250 arquivos)."
        ),
    )
    sync_parser.add_argument(
        "--verbose",
        action="store_true",
        help="Logs detalhados",
    )

    # list
    list_parser = subparsers.add_parser("list", help="Listar datasets no catálogo")
    list_parser.add_argument(
        "--verbose",
        action="store_true",
        help="Logs detalhados",
    )

    return parser


def _expand_groups(keys: list[str]) -> list[str]:
    result: list[str] = []
    for key in keys:
        for canon in expand_group(key):
            if canon not in result:
                result.append(canon)
    return result


def _handle_sync(args: argparse.Namespace) -> None:
    configure_cli_logging(args.verbose)
    if not args.verbose:
        logging.getLogger("quantilica.core").setLevel(logging.WARNING)
        logging.getLogger("anac_fetcher").setLevel(logging.WARNING)

    raw_groups: list[str] = args.groups or []
    if raw_groups:
        for g in raw_groups:
            if not expand_group(g):
                print(f"Erro: grupo desconhecido: {g!r}", file=sys.stderr)
                print(f"Grupos válidos: {', '.join(_ALL_KEYS)}", file=sys.stderr)
                sys.exit(1)
        groups = _expand_groups(raw_groups)
    else:
        groups = None

    if args.dry_run:
        entries = (
            list_datasets()
            if groups is None
            else [e for g in groups for e in list_datasets(g)]
        )
        for e in entries:
            print(f"{e['group']}\t{e['id']}\t{e['url']}")
        print(f"\n{len(entries)} arquivo(s) listado(s).")
        return

    errors: list[DownloadError] = []
    paths = download_all(
        args.output,
        groups=groups,
        show_progress=True,
        errors=errors,
        sleep=args.sleeptime,
    )

    print(f"\n{len(paths)}/{len(paths) + len(errors)} arquivo(s) baixado(s).")
    if errors:
        print(f"{len(errors)} erro(s):", file=sys.stderr)
        for entry, exc in errors:
            print(f"  {entry['id']}: {exc}", file=sys.stderr)
        sys.exit(1)


def _handle_list(args: argparse.Namespace) -> None:
    configure_cli_logging(args.verbose)
    if not args.verbose:
        logging.getLogger("quantilica.core").setLevel(logging.WARNING)
        logging.getLogger("anac_fetcher").setLevel(logging.WARNING)
    from .catalog import GROUPS

    for group_id, group_info in GROUPS.items():
        print(f"\n=== {group_id} — {group_info['name']} ===")
        for entry in group_info["entries"]:
            if entry["month"] is not None:
                partition = f"{entry['year']}-{entry['month']:02d}"
            elif entry["year"] is not None:
                partition = str(entry["year"])
            else:
                partition = "—"
            print(
                f"  {entry['id']:40s}  {partition:10s}  "
                f"[{entry['ext']}]  {entry['url']}"
            )
    total = sum(len(g["entries"]) for g in GROUPS.values())
    print(f"\n{total} dataset(s) no catálogo.")


def main(argv: list[str] | None = None) -> None:
    parser = get_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "sync":
            _handle_sync(args)
        elif args.command == "list":
            _handle_list(args)
        else:
            parser.print_help()
            sys.exit(1)
    except KeyboardInterrupt:
        sys.exit(130)
