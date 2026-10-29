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
# A ANAC publica o mesmo conteúdo em vários formatos ("...-csv@data.csv",
# "...-json@data.json"); só um vira Parquet, nesta ordem de preferência.
_FORMAT_TAG = re.compile(r"-(csv|json|xlsx?)(?=_|$)", re.IGNORECASE)
_FORMAT_RANK = {".csv": 0, ".zip": 1, ".7z": 1, ".xlsx": 2, ".xls": 3, ".json": 4}
_Y = re.compile(r"^(?P<ano>\d{4})$")


@dataclass
class ConvertResult:
    """Counts of a conversion run; ``errors`` holds one message per failure."""

    converted: int = 0
    skipped: int = 0
    errors: list[str] = field(default_factory=list)


def pick_one_format(
    files: list[Path], preferred: tuple[str, ...] | None = None
) -> list[Path]:
    """Um arquivo por conteúdo: o formato preferido, na versão mais recente.

    Arquivos da mesma pasta que diferem só no formato (sufixo ``-csv``/``-json``
    na base e extensão) são o mesmo dado; converter todos duplica linhas no lake
    (bases diferentes) ou faz um sobrescrever o outro (mesma base). O JSON de
    ``empresas-aereas`` (471 MB) ainda levava o leitor a ~190 GB de memória.
    """
    best: dict[str, tuple[int, str, Path]] = {}
    for path in files:
        base = _FORMAT_TAG.sub("", path.name.split("@", 1)[0].rsplit(".", 1)[0])
        stamp = path.name.split("@", 1)[1] if "@" in path.name else ""
        suffix = path.suffix.lower()
        if preferred and suffix in preferred:
            rank = preferred.index(suffix) - len(preferred)  # antes da ordem padrão
        else:
            rank = _FORMAT_RANK.get(suffix, 5)
        current = best.get(base)
        # Formato preferido primeiro; no mesmo formato, a versão mais recente.
        if current is None or (rank, current[1]) < (current[0], stamp):
            best[base] = (rank, stamp, path)
    return sorted(path for _, _, path in best.values())


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


_COARSER_SUFFIX = {("ano",): "-anual", (): "-atual"}


def dataset_for_granularity(group: str, part_keys: list[str], finest: int) -> str:
    """Dataset de um arquivo num grupo que mistura granularidades.

    Uma tabela Hive precisa da mesma profundidade de partições em todos os arquivos.
    Em ``drones`` e ``rab`` o histórico é mensal (``_2022-08``) e o cadastro vigente
    (``-atual-csv``) não tem período: o histórico fica com o nome do grupo e o
    cadastro vai para ``<grupo>-atual``.
    """
    if len(part_keys) >= finest:
        return group
    suffix = _COARSER_SUFFIX.get(tuple(part_keys), "-" + "-".join(part_keys))
    return group + suffix


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

            raw_files = pick_one_format(
                [
                    p
                    for p in src_group_dir.iterdir()
                    if p.is_file() and not p.name.endswith(".manifest.json")
                ],
                spec.get("formatos"),
            )

            resolved = [(f, *resolve_partitions(parse_filename(f))) for f in raw_files]
            finest = max((len(keys) for _, keys, _ in resolved), default=0)

            for raw_file, part_keys, part_vals in resolved:
                dataset_id = dataset_for_granularity(group, part_keys, finest)

                writer_key = f"{dataset_id}:" + ",".join(part_keys)
                if writer_key not in writers:
                    writers[writer_key] = LakeWriter(
                        lake_dir / SOURCE_ID / dataset_id,
                        DatasetDescriptor(
                            source_id=SOURCE_ID,
                            dataset_id=dataset_id,
                            alias=dataset_id,
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
