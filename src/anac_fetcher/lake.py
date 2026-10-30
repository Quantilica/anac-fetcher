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
from typing import TYPE_CHECKING, Any

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

if TYPE_CHECKING:  # só tipagem: o core publicado antes do contrato não tem Planned
    from quantilica.core.lake import Planned

SOURCE_ID = "anac"

_YM = re.compile(r"^(?P<ano>\d{4})-(?P<mes>\d{2})$")
# A ANAC publica o mesmo conteúdo em vários formatos ("...-csv@data.csv",
# "...-json@data.json"); só um vira Parquet, nesta ordem de preferência.
_FORMAT_TAG = re.compile(r"-(csv|json|xlsx?)(?=_|$)", re.IGNORECASE)
_FORMAT_RANK = {".csv": 0, ".zip": 1, ".7z": 1, ".xlsx": 2, ".xls": 3, ".json": 4}
_Y = re.compile(r"^(?P<ano>\d{4})$")
# Formatos que o conversor sabe ler: direto (csv/json/xls/xlsx) ou depois de
# descompactar (zip/7z com um deles dentro). O resto é documentação, mapa ou
# imagem — o leitor não abre.
_TABULAR_SUFFIXES = frozenset({".csv", ".json", ".xls", ".xlsx", ".zip", ".7z"})
# Sidecar de manifest e resto de escrita interrompida: nunca dados brutos.
_MANIFEST_SUFFIX = ".manifest.json"
_TEMP_SUFFIX = ".tmp"


@dataclass
class ConvertResult:
    """Counts of a conversion run; ``errors`` holds one message per failure."""

    converted: int = 0
    skipped: int = 0
    errors: list[str] = field(default_factory=list)


def is_tabular(path: Path) -> bool:
    """Se o conversor consegue ler o arquivo (``read_file`` ou ``decompress``)."""
    return path.suffix.lower() in _TABULAR_SUFFIXES


def _is_sidecar(path: Path) -> bool:
    """Se o arquivo é sidecar de manifest ou resto ``.tmp``, não dado bruto."""
    return path.name.endswith(_MANIFEST_SUFFIX) or path.name.endswith(_TEMP_SUFFIX)


def raw_files(src_group_dir: Path) -> list[Path]:
    """Arquivos de um diretório de grupo, sem sidecars nem restos ``.tmp``.

    É a descoberta compartilhada por :meth:`LakeConverter.convert` e
    :meth:`LakeConverter.inventory`, para os dois enxergarem o mesmo conjunto.
    """
    return sorted(
        p for p in src_group_dir.iterdir() if p.is_file() and not _is_sidecar(p)
    )


def _format_rank(
    path: Path, preferred: tuple[str, ...] | None = None
) -> tuple[str, int, str]:
    """``(base, rank, stamp)`` de um arquivo: o conteúdo, o formato e a versão."""
    base = _FORMAT_TAG.sub("", path.name.split("@", 1)[0].rsplit(".", 1)[0])
    stamp = path.name.split("@", 1)[1] if "@" in path.name else ""
    suffix = path.suffix.lower()
    if preferred and suffix in preferred:
        rank = preferred.index(suffix) - len(preferred)  # antes da ordem padrão
    else:
        rank = _FORMAT_RANK.get(suffix, 5)
    return base, rank, stamp


def _best_by_base(
    files: list[Path], preferred: tuple[str, ...] | None = None
) -> dict[str, tuple[int, str, Path]]:
    """Arquivo escolhido de cada conteúdo: ``base -> (rank, stamp, path)``."""
    best: dict[str, tuple[int, str, Path]] = {}
    for path in files:
        base, rank, stamp = _format_rank(path, preferred)
        current = best.get(base)
        # Formato preferido primeiro; no mesmo formato, a versão mais recente.
        if current is None or (rank, current[1]) < (current[0], stamp):
            best[base] = (rank, stamp, path)
    return best


def pick_one_format(
    files: list[Path], preferred: tuple[str, ...] | None = None
) -> list[Path]:
    """Um arquivo por conteúdo: o formato preferido, na versão mais recente.

    Arquivos da mesma pasta que diferem só no formato (sufixo ``-csv``/``-json``
    na base e extensão) são o mesmo dado; converter todos duplica linhas no lake
    (bases diferentes) ou faz um sobrescrever o outro (mesma base). O JSON de
    ``empresas-aereas`` (471 MB) ainda levava o leitor a ~190 GB de memória.
    """
    best = _best_by_base(files, preferred)
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


@dataclass(frozen=True)
class Routed:
    """Um arquivo bruto e o dataset/partição que ``convert`` lhe dá."""

    path: Path
    dataset_id: str
    partition_keys: list[str]
    partition_values: dict[str, str]


def route_group(
    group: str, src_group_dir: Path
) -> tuple[list[Routed], list[tuple[Path, str]]]:
    """Roteia os arquivos de um grupo: os convertidos e os ignorados, com motivo.

    Regra única de :meth:`LakeConverter.convert` e :meth:`LakeConverter.inventory`:
    um arquivo por conteúdo (:func:`pick_one_format`), partições pelo nome
    (:func:`resolve_partitions`) e dataset pela granularidade do grupo
    (:func:`dataset_for_granularity`). Os arquivos descartados voltam com o
    motivo do inventário: ``"gemeo"`` (mesmo conteúdo em outro formato),
    ``"nao_tabular"`` (formato que o leitor não abre) ou ``"superado"``
    (versão anterior do mesmo formato).
    """
    preferred = spec_for(group).get("formatos")
    files = raw_files(src_group_dir)
    best = _best_by_base(files, preferred)

    chosen = sorted(path for _, _, path in best.values())
    resolved = [(f, *resolve_partitions(parse_filename(f))) for f in chosen]
    finest = max((len(keys) for _, keys, _ in resolved), default=0)
    routed = [
        Routed(
            path=path,
            dataset_id=dataset_for_granularity(group, keys, finest),
            partition_keys=keys,
            partition_values=vals,
        )
        for path, keys, vals in resolved
    ]

    routed_paths = {item.path for item in routed}
    ignored: list[tuple[Path, str]] = []
    for path in files:
        if path in routed_paths:
            continue
        if not is_tabular(path):
            ignored.append((path, "nao_tabular"))
            continue
        chosen_path = best[_format_rank(path, preferred)[0]][2]
        reason = (
            "gemeo" if chosen_path.suffix.lower() != path.suffix.lower() else "superado"
        )
        ignored.append((path, reason))
    return routed, ignored


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
            src_group_dir = input_dir / _GROUP_DIRS[group]
            if not src_group_dir.exists():
                continue

            spec = spec_for(group)
            routed, _ = route_group(group, src_group_dir)

            for item in routed:
                raw_file = item.path
                part_keys = item.partition_keys
                part_vals = item.partition_values
                dataset_id = item.dataset_id

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

    def inventory(self, input_dir: Path) -> list[Planned]:
        """Um ``Planned`` por arquivo bruto: o dataset ou o motivo de ignorar.

        Espelha a descoberta de :meth:`convert` (mesmas funções de roteamento):
        um arquivo por conteúdo e um dataset por granularidade. Arquivos que o
        leitor não abre (PDF, imagens, documentos, mapas) vêm como
        ``"nao_tabular"``; os gêmeos de outro formato como ``"gemeo"``; as
        versões anteriores do mesmo formato como ``"superado"``. Sidecars
        ``*.manifest.json`` e restos ``*.tmp`` não entram no inventário.

        Args:
            input_dir: Raiz dos arquivos brutos da ANAC (a mesma de ``convert``).

        Returns:
            list[Planned]: Um item por arquivo, na ordem dos grupos.
        """
        # Import local: o core publicado antes do contrato não tem ``Planned``.
        from quantilica.core.lake import Planned

        input_dir = Path(input_dir)
        if not input_dir.is_dir():
            return []

        planned: list[Planned] = []
        covered: set[Path] = set()
        for group in self.datasets():
            src_group_dir = input_dir / _GROUP_DIRS[group]
            if not src_group_dir.is_dir():
                continue
            routed, ignored = route_group(group, src_group_dir)
            for item in routed:
                covered.add(item.path)
                if is_tabular(item.path):
                    planned.append(Planned(item.path, dataset=item.dataset_id))
                else:
                    planned.append(Planned(item.path, skip_reason="nao_tabular"))
            for path, reason in ignored:
                covered.add(path)
                planned.append(Planned(path, skip_reason=reason))

        # Fora dos diretórios de grupo o conversor não procura nada. O não
        # tabular é documentação; o tabular fica sem destino para a auditoria
        # apontar a lacuna em vez de supor um Parquet que nunca existirá.
        for path in sorted(input_dir.rglob("*")):
            if not path.is_file() or path in covered or _is_sidecar(path):
                continue
            planned.append(
                Planned(path, skip_reason=None if is_tabular(path) else "nao_tabular")
            )
        return planned


converter = LakeConverter()
