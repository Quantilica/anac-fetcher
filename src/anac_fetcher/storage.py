"""File location management for anac-fetcher.

Filenames follow the ecosystem convention:
    {base_id}@{YYYYMMDD}.{ext}                     — static files
    {base_id}_{year}-{month:02d}@{YYYYMMDD}.{ext}  — monthly series
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
}


class DataRepository(BaseDataRepository):
    """Manages local storage for anac-fetcher files."""

    def __init__(self, root: Path | str):
        super().__init__(root)

    def path_for_entry(
        self,
        entry: DatasetEntry,
        *,
        last_modified: dt.date | None = None,
    ) -> Path:
        """Compute the local path for a dataset entry."""
        group_dir = _GROUP_DIRS[entry["group"]]
        ext = entry["ext"]
        base_id = entry["base_id"]
        year = entry["year"]
        month = entry["month"]

        if year is None:
            filename = stamp_filename(base_id, ext, last_modified)
        elif month is not None:
            partition = f"{year}-{month:02d}"
            filename = build_stamped_filename(
                base_id, partition, ext=ext, timestamp=last_modified
            )
        else:
            filename = build_stamped_filename(
                base_id, year, ext=ext, timestamp=last_modified
            )

        return self.storage.path_for(f"{group_dir}/{filename}")
