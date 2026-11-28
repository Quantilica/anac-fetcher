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

# Defasagem da publicação: o VRA de um mês sai cerca de 2 meses depois, então o
# catálogo vai até o mês de hoje menos 2 (``_LAG_MONTHS``). Como a defasagem
# oscila de um mês para o outro, os 2 últimos meses gerados (``_PENDING_MONTHS``)
# levam ``pending_publication``: se a fonte ainda não os publicou, o 404 é "ainda
# não publicado", não erro; os mais antigos, que já deveriam existir, seguem
# falhando em 404.
_LAG_MONTHS = 2
_PENDING_MONTHS = 2


def _vra_entry(
    year: int, month: int, ext: str, *, pending: bool = False
) -> DatasetEntry:
    month_dir = quote(_MESES_PT[month], safe="")
    url = f"{_BASE}/{year}/{month_dir}/VRA_{year}{month}.{ext}"
    entry = DatasetEntry(
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
    if pending:
        entry["pending_publication"] = True
    return entry


def _month_index(year: int, month: int) -> int:
    return year * 12 + (month - 1)


def _vra_entries_list(today: dt.date | None = None) -> list[DatasetEntry]:
    """Entradas do VRA de 2000-01 até ``today`` menos a defasagem.

    Na virada do ano a conta atravessa o ano (em janeiro o último mês é novembro
    do ano anterior), em vez de gerar um mês do ano corrente que não existe.
    """
    today = today or dt.date.today()
    last = _month_index(today.year, today.month) - _LAG_MONTHS
    first_pending = last - (_PENDING_MONTHS - 1)
    entries: list[DatasetEntry] = []
    _missing_months = {(2014, 6), (2014, 7)}
    for index in range(_month_index(2000, 1), last + 1):
        year, month = divmod(index, 12)
        month += 1
        if (year, month) in _missing_months:
            continue
        for ext in ("csv", "json"):
            entries.append(_vra_entry(year, month, ext, pending=index >= first_pending))
    return entries


_vra_entries: list[DatasetEntry] = _vra_entries_list()

GROUPS_VRA: dict[str, GroupInfo] = {
    "vra": {"name": "Voo Regular Ativo (VRA)", "entries": _vra_entries},
}

GROUP_ALIASES_VRA: dict[str, str] = {
    "voo-regular-ativo": "vra",
}
