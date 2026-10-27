"""Convert raw ANAC open data into the Hive-partitioned lake.

Each raw file lands in
``<lake>/anac/<group>/[ano=<ano>/][mes=<mes>/]<file_key>.parquet``.
Files with monthly partition (e.g. VRA, Dados Estatísticos) are partitioned by
``ano=/mes=``; annual files by ``ano=``; and static datasets (e.g. RAB, Aeródromos)
are stored unpartitioned. Data contracts are validated when available.
"""

from __future__ import annotations

import re
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

try:
    import polars as pl
    from quantilica.analytics.lake import LakeError, LakeWriter
    from quantilica.core.lake import DatasetDescriptor
except ImportError as exc:
    raise ImportError(
        "anac_fetcher.lake requer o extra 'analysis': "
        "uv add 'anac-fetcher[analysis]' "
        "--index https://index.quantilica.com/simple/"
    ) from exc

from anac_fetcher import __version__
from anac_fetcher.catalog import ALL_GROUP_KEYS, resolve_group
from anac_fetcher.reader import (
    decompress,
    normalize_dtypes,
    parse_filename,
    read_file,
)
from anac_fetcher.storage import _GROUP_DIRS
from anac_fetcher.wrangling import _apply_contract, spec_for

SOURCE_ID = "anac"

_YM = re.compile(r"^(?P<ano>\d{4})-(?P<mes>\d{2})$")
_Y = re.compile(r"^(?P<ano>\d{4})$")


@dataclass
class ConvertResult:
    """Counts of a conversion run; ``errors`` holds one message per failure."""

    converted: int = 0
    skipped: int = 0
    errors: list[str] = field(default_factory=list)


def resolve_partitions(meta: dict[str, Any]) -> tuple[list[str], dict[str, str]]:
    """Determine partition keys and values from filename metadata."""
    partition = meta.get("partition")
    if not partition:
        return [], {}

    m_ym = _YM.match(partition)
    if m_ym:
        return ["ano", "mes"], {"ano": m_ym["ano"], "mes": m_ym["mes"]}

    m_y = _Y.match(partition)
    if m_y:
        return ["ano"], {"ano": m_y["ano"]}

    return ["particao"], {"particao": partition}


class LakeConverter:
    """Converter registered under the ``quantilica.lake`` entry point."""

    source_id = SOURCE_ID

    def datasets(self) -> list[str]:
        """Dataset ids this converter writes to the lake."""
        return sorted(k for k in ALL_GROUP_KEYS if k in _GROUP_DIRS)

    def convert(
        self,
        input_dir: Path,
        lake_dir: Path,
        *,
        datasets: list[str] | None = None,
        force: bool = False,
    ) -> ConvertResult:
        """Convert raw ANAC files into ``lake_dir``.

        Args:
            input_dir: Root directory containing raw ANAC files.
            lake_dir: Root of the lake.
            datasets: Optional list of group names or aliases to convert.
            force: Reconvert even if sha256 already matches in the lake.

        Returns:
            ConvertResult: Files converted, skipped, and error messages.
        """
        input_dir = Path(input_dir)
        lake_dir = Path(lake_dir)
        result = ConvertResult()
        if not input_dir.is_dir():
            result.errors.append(f"diretório '{input_dir}' não existe")
            return result

        target_groups: list[str] = []
        if datasets:
            for d in datasets:
                resolved = resolve_group(d) or d
                if resolved in _GROUP_DIRS and resolved not in target_groups:
                    target_groups.append(resolved)
                elif resolved not in _GROUP_DIRS:
                    result.errors.append(f"dataset desconhecido: {d}")
            if result.errors:
                return result
        else:
            target_groups = self.datasets()

        writers: dict[str, LakeWriter] = {}

        for group in target_groups:
            group_dir = _GROUP_DIRS[group]
            src_group_dir = input_dir / group_dir
            if not src_group_dir.exists():
                continue

            spec = spec_for(group)

            raw_files = sorted(
                p
                for p in src_group_dir.iterdir()
                if p.is_file() and not p.name.endswith(".manifest.json")
            )

            for raw_file in raw_files:
                meta = parse_filename(raw_file)
                part_keys, part_vals = resolve_partitions(meta)

                writer_key = f"{group}:" + ",".join(part_keys)
                if writer_key not in writers:
                    writers[writer_key] = LakeWriter(
                        lake_dir / SOURCE_ID / group,
                        DatasetDescriptor(
                            source_id=SOURCE_ID,
                            dataset_id=group,
                            alias=group,
                            partition_keys=part_keys,
                            partition_types={k: "varchar" for k in part_keys},
                        ),
                        force=force,
                    )
                writer = writers[writer_key]

                # Decompress if compressed
                source_path = raw_file
                tmp_dir: tempfile.TemporaryDirectory[str] | None = None
                if raw_file.suffix.lower() in (".zip", ".7z"):
                    try:
                        inner = decompress(raw_file)
                        source_path = inner
                    except Exception as exc:
                        result.errors.append(
                            f"{raw_file.name}: erro na descompressão: {exc}"
                        )
                        continue

                try:
                    data = read_file(source_path, spec)
                    frames = (
                        list(data.items()) if isinstance(data, dict) else [(None, data)]
                    )

                    for sheet, frame in frames:
                        norm = normalize_dtypes(frame, spec)
                        norm = _apply_contract(group, norm, raw_file.name)
                        # Use sheet as file_key suffix if multi-sheet
                        file_key_override = None
                        if sheet is not None:
                            file_key_override = f"{raw_file.stem}_{sheet}"

                        written = writer.write_polars(
                            norm,
                            raw_file,
                            partitions=part_vals,
                            file_key_name=file_key_override,
                            converter=f"anac-fetcher {__version__}",
                        )
                        if written.status == "skipped":
                            result.skipped += 1
                        else:
                            result.converted += 1

                except (
                    LakeError,
                    OSError,
                    pl.exceptions.PolarsError,
                    Exception,
                ) as exc:
                    message = str(exc).strip()
                    first_line = message.splitlines()[0] if message else repr(exc)
                    result.errors.append(f"{raw_file.name}: {first_line}")
                    continue
                finally:
                    if tmp_dir is not None:
                        tmp_dir.cleanup()

        return result


converter = LakeConverter()
