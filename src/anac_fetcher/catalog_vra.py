"""ANAC VRA (Voo Regular Ativo) catalog.

Voos, atrasos, cancelamentos e pontualidade de empresas de transporte aéreo
regular. Arquivos mensais, um por ano/mês, publicados em
``sistemas.anac.gov.br/dadosabertos`` desde 2000.

Layout no servidor: ``.../VRA/{year}/{month:02d} - {MêsPT}/VRA_{year}{month}.{ext}``
(sem zero à esquerda no mês dentro do nome do arquivo — confirmado para
2000-01 → ``VRA_20001.csv``, 2015-11 → ``VRA_201511.csv``, 2024-10 →
``VRA_202410.csv``).
"""

import datetime as dt
from urllib.parse import quote

from ._catalog_base import DatasetEntry, GroupInfo

_SOURCE = "anac-dadosabertos"
_ROOT = "https://sistemas.anac.gov.br/dadosabertos"
_VRA_DIR = quote("Voos e operações aéreas/Voo Regular Ativo (VRA)", safe="/()")
_BASE = f"{_ROOT}/{_VRA_DIR}"

_MESES_PT = {
    1: "01 - Janeiro",
    2: "02 - Fevereiro",
    3: "03 - Março",
    4: "04 - Abril",
    5: "05 - Maio",
    6: "06 - Junho",
    7: "07 - Julho",
    8: "08 - Agosto",
    9: "09 - Setembro",
    10: "10 - Outubro",
    11: "11 - Novembro",
    12: "12 - Dezembro",
}

# Última competência conhecida no catálogo (dados de meses recentes podem
# ainda não estar publicados; falhas de download individuais não interrompem
# o restante da sincronização — ver download.download_group).
_LAST_YEAR = dt.date.today().year
_LAST_MONTH = dt.date.today().month


def _vra_entry(year: int, month: int, ext: str) -> DatasetEntry:
    month_dir = quote(_MESES_PT[month], safe="")
    url = f"{_BASE}/{year}/{month_dir}/VRA_{year}{month}.{ext}"
    return DatasetEntry(
        id=f"vra-{year}-{month:02d}-{ext}",
        base_id="vra",
        name=f"Voo Regular Ativo — {_MESES_PT[month][5:]}/{year}",
        url=url,
        ext=ext,
        group="vra",
        source=_SOURCE,
        year=year,
        semester=None,
        month=month,
    )


def _vra_entries_list() -> list[DatasetEntry]:
    entries: list[DatasetEntry] = []
    for year in range(2000, _LAST_YEAR + 1):
        max_month = _LAST_MONTH if year == _LAST_YEAR else 12
        for month in range(1, max_month + 1):
            for ext in ("csv", "json"):
                entries.append(_vra_entry(year, month, ext))
    return entries


_vra_entries: list[DatasetEntry] = _vra_entries_list()

GROUPS_VRA: dict[str, GroupInfo] = {
    "vra": {"name": "Voo Regular Ativo (VRA)", "entries": _vra_entries},
}

GROUP_ALIASES_VRA: dict[str, str] = {
    "voo-regular-ativo": "vra",
}
