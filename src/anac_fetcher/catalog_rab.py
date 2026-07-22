"""ANAC RAB (Registro Aeronáutico Brasileiro) catalog.

Cadastro de aeronaves registradas no Brasil. Um snapshot "atual" (sempre o
estado mais recente) mais um histórico mensal em
``.../Aeronaves/RAB/Historico_RAB/{YYYY-MM}.{ext}`` desde 2017-01.

O formato ``csv`` só passou a ser publicado no histórico a partir de
2024-09 (confirmado via listagem do servidor); antes disso só ``json``/``xls``
estão disponíveis. O mês 2019-05 não existe em nenhum formato. Outras lacunas
pontuais (ex.: alguns meses de 2022 sem ``json``) não foram mapeadas
individualmente — falhas de download por arquivo não interrompem a
sincronização (ver ``download.download_group``).
"""

import datetime as dt

from ._catalog_base import DatasetEntry, GroupInfo, _static

_SOURCE = "anac-dadosabertos"
_ROOT = "https://sistemas.anac.gov.br/dadosabertos/Aeronaves/RAB"
_HIST = f"{_ROOT}/Historico_RAB"

_MISSING_MONTHS = {(2019, 5)}
_CSV_SINCE = (2024, 9)

_LAST_YEAR = dt.date.today().year
_LAST_MONTH = dt.date.today().month

_rab_current_entries: list[DatasetEntry] = [
    _static(
        "rab",
        _SOURCE,
        "rab-atual-csv",
        "Registro Aeronáutico Brasileiro — snapshot atual (CSV)",
        f"{_ROOT}/dados_aeronaves.csv",
        "csv",
    ),
    _static(
        "rab",
        _SOURCE,
        "rab-atual-json",
        "Registro Aeronáutico Brasileiro — snapshot atual (JSON)",
        f"{_ROOT}/dados_aeronaves.json",
        "json",
    ),
    _static(
        "rab",
        _SOURCE,
        "rab-atual-xls",
        "Registro Aeronáutico Brasileiro — snapshot atual (XLS)",
        f"{_ROOT}/dados_aeronaves.xls",
        "xls",
    ),
]


def _rab_hist_entry(year: int, month: int, ext: str) -> DatasetEntry:
    return DatasetEntry(
        id=f"rab-hist-{year}-{month:02d}-{ext}",
        base_id=f"rab-hist-{ext}",
        name=f"Registro Aeronáutico Brasileiro — {year}-{month:02d} ({ext.upper()})",
        url=f"{_HIST}/{year}-{month:02d}.{ext}",
        ext=ext,
        group="rab",
        source=_SOURCE,
        year=year,
        semester=None,
        month=month,
    )


def _rab_hist_entries_list() -> list[DatasetEntry]:
    entries: list[DatasetEntry] = []
    for year in range(2017, _LAST_YEAR + 1):
        max_month = _LAST_MONTH if year == _LAST_YEAR else 12
        for month in range(1, max_month + 1):
            if (year, month) in _MISSING_MONTHS:
                continue
            for ext in ("json", "xls"):
                entries.append(_rab_hist_entry(year, month, ext))
            if (year, month) >= _CSV_SINCE:
                entries.append(_rab_hist_entry(year, month, "csv"))
    return entries


_rab_entries: list[DatasetEntry] = _rab_current_entries + _rab_hist_entries_list()

GROUPS_RAB: dict[str, GroupInfo] = {
    "rab": {"name": "Registro Aeronáutico Brasileiro (RAB)", "entries": _rab_entries},
}

GROUP_ALIASES_RAB: dict[str, str] = {
    "registro-aeronautico-brasileiro": "rab",
    "aeronaves": "rab",
}
