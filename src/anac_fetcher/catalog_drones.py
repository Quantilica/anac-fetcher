"""ANAC Drones cadastrados (SISANT) catalog.

Cadastro de drones registrados no sistema SISANT, publicado por
``sistemas.anac.gov.br/dadosabertos``. Um snapshot "atual" (``SISANT.*``,
sempre o estado mais recente) mais um histórico mensal em
``.../Historico/SISANT_{MM}{YYYY}.{ext}`` desde 2022-08.
"""

import datetime as dt

from ._catalog_base import DatasetEntry, GroupInfo, _static

_SOURCE = "anac-dadosabertos"
_ROOT = "https://sistemas.anac.gov.br/dadosabertos/Aeronaves/drones%20cadastrados"
_HIST = f"{_ROOT}/Historico"

_START_YEAR = 2022
_START_MONTH = 8  # histórico mensal começa em 2022-08 (confirmado via servidor)

_LAST_YEAR = dt.date.today().year
_LAST_MONTH = dt.date.today().month

_drones_current_entries: list[DatasetEntry] = [
    _static(
        "drones",
        _SOURCE,
        "drones-atual-csv",
        "Drones cadastrados (SISANT) — snapshot atual (CSV)",
        f"{_ROOT}/SISANT.csv",
        "csv",
    ),
    _static(
        "drones",
        _SOURCE,
        "drones-atual-json",
        "Drones cadastrados (SISANT) — snapshot atual (JSON)",
        f"{_ROOT}/SISANT.json",
        "json",
    ),
]


def _drones_hist_entry(year: int, month: int, ext: str) -> DatasetEntry:
    url = f"{_HIST}/SISANT_{month:02d}{year}.{ext}"
    return DatasetEntry(
        id=f"drones-hist-{year}-{month:02d}-{ext}",
        base_id="drones-hist",
        name=f"Drones cadastrados (SISANT) — {year}-{month:02d}",
        url=url,
        ext=ext,
        group="drones",
        source=_SOURCE,
        year=year,
        semester=None,
        month=month,
    )


def _drones_hist_entries_list() -> list[DatasetEntry]:
    entries: list[DatasetEntry] = []
    for year in range(_START_YEAR, _LAST_YEAR + 1):
        start_month = _START_MONTH if year == _START_YEAR else 1
        end_month = 12 if year < _LAST_YEAR else _LAST_MONTH
        for month in range(start_month, end_month + 1):
            for ext in ("csv", "json"):
                entries.append(_drones_hist_entry(year, month, ext))
    return entries


_drones_hist_entries: list[DatasetEntry] = _drones_hist_entries_list()

GROUPS_DRONES: dict[str, GroupInfo] = {
    "drones": {
        "name": "Drones cadastrados (SISANT)",
        "entries": _drones_current_entries + _drones_hist_entries,
    },
}

GROUP_ALIASES_DRONES: dict[str, str] = {
    "sisant": "drones",
}
