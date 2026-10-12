"""File location management for anac-fetcher.

Filenames follow the ecosystem convention:
    {base_id}@{YYYYMMDD}.{ext}                     — static files
    {base_id}_{year}-{month:02d}@{YYYYMMDD}.{ext}  — monthly series

Quando a entrada tem ``slug`` (grupo com vários arquivos remotos na mesma
partição, ex.: os anexos de ``atrasos-cancelamentos``), o slug entra após a
partição:
    {base_id}_{year}-{month:02d}_{slug}@{YYYYMMDD}.{ext}
"""

import datetime as dt
from pathlib import Path

from quantilica.core.storage import (
    BaseDataRepository,
    build_stamped_filename,
    stamp_filename,
)

from .catalog import DatasetEntry

_GROUP_DIRS: dict[str, str] = {
    "vra": "voo-regular-ativo",
    "rab": "registro-aeronautico-brasileiro",
    "ocorrencias": "ocorrencias-cenipa",
    "aero-lista-publicos": "aerodromos-lista-publicos",
    "aero-caracteristicas": "aerodromos-caracteristicas",
    "aero-pistas-pouso": "aerodromos-pistas-pouso",
    "aero-pistas-taxi": "aerodromos-pistas-taxi",
    "aero-patio": "aerodromos-patio",
    "aero-posicoes-estacionamento": "aerodromos-posicoes-estacionamento",
    "aero-helipontos-publicos": "aerodromos-helipontos-publicos",
    "aero-excluidos": "aerodromos-excluidos",
    "aero-seguranca": "aerodromos-seguranca",
    "aero-lista-privados": "aerodromos-lista-privados",
    "aero-helideck": "aerodromos-helideck",
    "aero-heliponto-privado": "aerodromos-heliponto-privado",
    "aero-pzr": "aerodromos-pzr",
    "aero-plano-diretor": "aerodromos-plano-diretor",
    "dados-estatisticos": "dados-estatisticos-transporte-aereo",
    "drones": "drones-sisant",
    "atrasos-cancelamentos": "atrasos-cancelamentos",
    "empresas-aereas": "empresas-aereas",
    "movimentacao-aeroportuaria": "movimentacao-aeroportuaria",
    "recomendacoes-seguranca": "recomendacoes-seguranca",
}


class DataRepository(BaseDataRepository):
    """Manages local storage for anac-fetcher files."""

    def __init__(self, root: Path | str):
        """Initialize the repository.

        Args:
            root: Base directory where downloaded files will be stored.
        """
        super().__init__(root)

    def path_for_entry(
        self,
        entry: DatasetEntry,
        *,
        last_modified: dt.date | None = None,
    ) -> Path:
        """Compute the local path for a dataset entry.

        O ``slug`` opcional da entrada (nome do arquivo remoto) é inserido
        após a partição, tornando o caminho único quando o grupo tem vários
        arquivos remotos por partição (ex.: anexos de ``atrasos-cancelamentos``).

        Args:
            entry: The dataset entry dict containing metadata like group, ext,
                base_id, slug.
            last_modified: Optional timestamp of the remote file, used to version
                the local file.

        Returns:
            The absolute Path where the file should be saved.
        """
        group_dir = _GROUP_DIRS[entry["group"]]
        ext = entry["ext"]
        base_id = entry["base_id"]
        year = entry["year"]
        month = entry["month"]
        slug = entry.get("slug")

        if year is None:
            filename = stamp_filename(base_id, ext, last_modified)
        elif month is not None:
            partition = f"{year}-{month:02d}"
            if slug:
                partition = f"{partition}_{slug}"
            filename = build_stamped_filename(
                base_id, partition, ext=ext, timestamp=last_modified
            )
        else:
            partition = str(year)
            if slug:
                partition = f"{partition}_{slug}"
            filename = build_stamped_filename(
                base_id, partition, ext=ext, timestamp=last_modified
            )

        return self.storage.path_for(f"{group_dir}/{filename}")
