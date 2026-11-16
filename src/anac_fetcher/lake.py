"""Convert raw ANAC open data into the Hive-partitioned lake.

Each raw file lands in
``<lake>/anac/<group>/[ano=<ano>/][mes=<mes>/]<file_key>.parquet``.
Files with monthly partition (e.g. VRA, Dados Estatísticos) are partitioned by
``ano=/mes=``; annual files by ``ano=``; and static datasets (e.g. RAB, Aeródromos)
are stored unpartitioned. Data contracts are validated when available.

The groups in ``_GRUPOS_POR_TABELA`` (``atrasos-cancelamentos``) have several raw
files per month, one per table (the three annexes, each with its own columns).
Each table is written by ``LakeWriter.write_group`` as
``<group>_<AAAAMM>[_<anexo>].parquet``, with ``_origem`` and the footer
``quantilica.members``. Annexes are never merged with each other (different
schemas and granularity). The file with no annex suffix that old versions of the
fetcher wrote is byte for byte a copy of one annex: it is that annex's twin, not a
table, and the old Parquet of the copy is removed when the annex is converted.
"""

from __future__ import annotations

import re
from collections import defaultdict
from contextlib import ExitStack
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import TYPE_CHECKING, Any

try:
    import polars as pl
    from quantilica.analytics.lake import GroupMember, LakeError, LakeWriter
    from quantilica.core.files import sha256_file
    from quantilica.core.lake import (
        DatasetDescriptor,
        composite_file_key,
        file_key,
        partition_types_for,
    )
except ImportError as exc:
    raise ImportError(
        "anac_fetcher.lake requer o extra 'analysis': "
        "uv add 'anac-fetcher[analysis]' "
        "--index https://index.quantilica.com/simple/"
    ) from exc

from anac_fetcher import __version__
from anac_fetcher.catalog import ALL_GROUP_KEYS, resolve_group
from anac_fetcher.reader import (
    extracted_data,
    normalize_dtypes,
    parse_filename,
    read_file,
)
from anac_fetcher.storage import _GROUP_DIRS
from anac_fetcher.wrangling import _apply_contract, spec_for

if TYPE_CHECKING:  # só tipagem: o core publicado antes do contrato não tem Planned
    from quantilica.core.lake import Planned

SOURCE_ID = "anac"

# Grupos com vários arquivos brutos por mês, um por tabela (anexo): cada tabela
# vira um Parquet por mês, por ``write_group``. Versões gravadas nos membros do
# rodapé: suba CONTRACT_VERSION se a normalização das colunas mudar e
# CONVERTER_VERSION se mudar a leitura; o mês é reconvertido.
_GRUPOS_POR_TABELA = frozenset({"atrasos-cancelamentos"})
CONTRACT_VERSION = 1
CONVERTER_VERSION = "1"

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


def drop_partition_columns(frame: pl.DataFrame, part_keys: list[str]) -> pl.DataFrame:
    """Tira do payload as colunas que repetem uma chave de partição Hive.

    O valor já está no caminho (``ano=2022/mes=07``). O DuckDB não diferencia
    maiúsculas: uma coluna ``ANO`` no arquivo sombreia a partição ``ano`` e a
    leitura devolve nulo. O lake não duplica colunas de partição no Parquet.
    """
    keys = {k.lower() for k in part_keys}
    drop = [c for c in frame.columns if c.lower() in keys]
    return frame.drop(drop) if drop else frame


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
    # Arquivos byte a byte iguais a este, que não são tabela própria (ver
    # :func:`fold_twins`): o conversor não os lê e o inventário os dá como gêmeos.
    twins: tuple[Path, ...] = ()


def fold_twins(routed: list[Routed]) -> tuple[list[Routed], list[Path]]:
    """Separa os arquivos sem sufixo de anexo que copiam um anexo da mesma partição.

    Versões antigas do fetcher gravavam os anexos de uma partição no mesmo nome
    (``<base>_<AAAA-MM>``, sem o slug): o que ficou é o último baixado, byte a
    byte igual a um dos anexos (conferido pelo sha256 dos manifests de 284 meses).
    Convertê-lo duplica as linhas desse anexo no lake. Um arquivo sem sufixo cujo
    sha256 não é o de nenhum anexo continua sendo uma tabela.

    Returns:
        Os itens que ficam (cada anexo com seus ``twins``) e os gêmeos.
    """
    by_partition: dict[tuple[str, tuple], list[Routed]] = defaultdict(list)
    for item in routed:
        key = (item.dataset_id, tuple(item.partition_values.items()))
        by_partition[key].append(item)

    kept: list[Routed] = []
    twins: list[Path] = []
    for items in by_partition.values():
        annexes = [i for i in items if parse_filename(i.path)["slug"]]
        bare = [i for i in items if not parse_filename(i.path)["slug"]]
        if not annexes or not bare:
            kept.extend(items)
            continue
        owners: dict[str, Routed] = {}
        for item in sorted(annexes, key=lambda i: i.path):
            owners.setdefault(sha256_file(item.path), item)
        folded: dict[Path, list[Path]] = defaultdict(list)
        for item in bare:
            owner = owners.get(sha256_file(item.path))
            if owner is None:
                kept.append(item)
            else:
                folded[owner.path].append(item.path)
                twins.append(item.path)
        kept.extend(replace(i, twins=tuple(folded.get(i.path, ()))) for i in annexes)
    return sorted(kept, key=lambda i: i.path), sorted(twins)


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
    (versão anterior do mesmo formato). Nos grupos por tabela, o arquivo sem
    sufixo de anexo que copia um anexo também volta como ``"gemeo"``.
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

    folded: list[Path] = []
    if group in _GRUPOS_POR_TABELA:
        routed, folded = fold_twins(routed)

    routed_paths = {item.path for item in routed}
    folded_paths = set(folded)
    ignored: list[tuple[Path, str]] = [(path, "gemeo") for path in folded]
    for path in files:
        if path in routed_paths or path in folded_paths:
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


def _read_table(
    group: str, spec: dict[str, Any], raw_file: Path, part_keys: list[str]
) -> pl.DataFrame:
    """O arquivo bruto de uma tabela como DataFrame pronto para o Parquet.

    Os mesmos passos de :meth:`LakeConverter.convert` para os outros grupos:
    leitura, tipos, contrato e retirada das colunas de partição.
    """
    with ExitStack() as stack:
        source_path = raw_file
        if raw_file.suffix.lower() in (".zip", ".7z"):
            source_path = stack.enter_context(extracted_data(raw_file))
        data = read_file(source_path, spec)
        if isinstance(data, dict):
            raise LakeError(f"{raw_file.name}: várias abas não cabem numa tabela só")
        norm = normalize_dtypes(data, spec)
        norm = _apply_contract(group, norm, raw_file.name)
        return drop_partition_columns(norm, part_keys)


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

            if group in _GRUPOS_POR_TABELA:
                self._convert_tables(group, spec, routed, lake_dir, force, result)
                continue

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
                            partition_types=partition_types_for(part_keys),
                        ),
                        force=force,
                    )
                writer = writers[writer_key]

                # A pasta de extração (a raiz, subpastas incluídas) some ao
                # sair do ``with``, em sucesso e em erro.
                with ExitStack() as stack:
                    source_path = raw_file
                    if raw_file.suffix.lower() in (".zip", ".7z"):
                        try:
                            source_path = stack.enter_context(extracted_data(raw_file))
                        except Exception as exc:
                            result.errors.append(
                                f"{raw_file.name}: erro na descompressão: {exc}"
                            )
                            continue

                    try:
                        data = read_file(source_path, spec)
                        frames = (
                            list(data.items())
                            if isinstance(data, dict)
                            else [(None, data)]
                        )

                        for sheet, frame in frames:
                            norm = normalize_dtypes(frame, spec)
                            norm = _apply_contract(group, norm, raw_file.name)
                            norm = drop_partition_columns(norm, part_keys)
                            # Use sheet as file_key suffix if multi-sheet
                            file_key_override = None
                            if sheet is not None:
                                file_key_override = composite_file_key(raw_file, sheet)

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

        return result

    @staticmethod
    def _convert_tables(
        group: str,
        spec: dict[str, Any],
        routed: list[Routed],
        lake_dir: Path,
        force: bool,
        result: ConvertResult,
    ) -> None:
        """Escreve cada tabela (anexo) do mês como um grupo de ``write_group``.

        Um anexo é um membro só: o grupo existe para ter o arquivo do mês com
        proveniência (``_origem``, rodapé) e para trocar, na migração, os
        Parquets antigos (o do próprio anexo e o da cópia sem sufixo) pelo novo.
        """
        writers: dict[str, LakeWriter] = {}
        for item in routed:
            raw_file = item.path
            writer_key = f"{item.dataset_id}:" + ",".join(item.partition_keys)
            if writer_key not in writers:
                writers[writer_key] = LakeWriter(
                    lake_dir / SOURCE_ID / item.dataset_id,
                    DatasetDescriptor(
                        source_id=SOURCE_ID,
                        dataset_id=item.dataset_id,
                        alias=item.dataset_id,
                        partition_keys=item.partition_keys,
                        partition_types=partition_types_for(item.partition_keys),
                    ),
                    force=force,
                )
            writer = writers[writer_key]

            meta = parse_filename(raw_file)
            period = "".join(item.partition_values.values())
            slug = meta["slug"]
            group_key = "_".join(
                part for part in (item.dataset_id, period, slug) if part
            )
            # Parquets de um por arquivo bruto que este grupo substitui: o do
            # anexo, o de cada cópia e o do nome sem sufixo, que as versões
            # antigas gravavam. Só saem se o sha256 de origem for o do anexo.
            replaces = {file_key(raw_file), *(file_key(t) for t in item.twins)}
            if slug and meta["year"] and meta["part"]:
                replaces.add(f"{meta['base_id']}_{meta['year']}-{meta['part']:02d}")
            # Só os que existem: o writer avisa no log de cada chave sem Parquet.
            folder = writer.dataset_dir.joinpath(
                *(f"{k}={v}" for k, v in item.partition_values.items())
            )
            replaces = {k for k in replaces if (folder / f"{k}.parquet").is_file()}

            def frame(raw_file: Path = raw_file, item: Routed = item):
                return _read_table(group, spec, raw_file, item.partition_keys)

            member = GroupMember(raw_file, frame)
            options = {
                "partitions": item.partition_values,
                "contract_version": CONTRACT_VERSION,
                "converter_version": CONVERTER_VERSION,
            }
            try:
                # Sem decodificar nada quando o mês já está no lake.
                current = writer.is_current_group(group_key, [member], **options)
                written = writer.write_group(
                    group_key,
                    [member],
                    converter=f"anac-fetcher {__version__}",
                    replaces=sorted(replaces),
                    **options,
                )
            except Exception as exc:
                message = str(exc).strip()
                first_line = message.splitlines()[0] if message else repr(exc)
                result.errors.append(f"{raw_file.name}: {first_line}")
                continue
            if current or written.status == "skipped":
                result.skipped += 1
            else:
                result.converted += len(written.written)
                result.skipped += len(written.kept)

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
