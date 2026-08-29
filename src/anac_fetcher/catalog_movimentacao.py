"""ANAC Dados de Movimentação Aeroportuária catalog.

Movimentação de passageiros, carga e aeronaves por aeroporto, publicada por
``sistemas.anac.gov.br/dadosabertos``. Arquivos mensais, um por ano/mês,
desde 2019.

Layout no servidor:
``.../Dados de Movimentação Aeroportuárias/{year}/``
``Movimentacoes_Aeroportuarias_{YYYYMM}.csv``

Apenas CSV é catalogado por padrão (JSON por mês ~240 MB; o histórico
completo em CSV+JSON ultrapassaria ~23 GB).
"""

import datetime as dt
from urllib.parse import quote

from ._catalog_base import DatasetEntry, GroupInfo

_SOURCE = "anac-dadosabertos"
_ROOT = "https://sistemas.anac.gov.br/dadosabertos"
_MOV_DIR = quote(
    "Operador Aeroportuário/Dados de Movimentação Aeroportuárias",
    safe="/()",
)
_BASE = f"{_ROOT}/{_MOV_DIR}"

_START_YEAR = 2019  # primeiro ano publicado (confirmado via servidor)

_LAST_YEAR = dt.date.today().year
_LAST_MONTH = dt.date.today().month


def _movimentacao_entry(year: int, month: int) -> DatasetEntry:
    url = f"{_BASE}/{year}/Movimentacoes_Aeroportuarias_{year}{month:02d}.csv"
    return DatasetEntry(
        id=f"movimentacao-{year}-{month:02d}-csv",
        base_id="movimentacao-aeroportuaria",
        name=f"Movimentação Aeroportuária — {year}-{month:02d}",
        url=url,
        ext="csv",
        group="movimentacao-aeroportuaria",
        source=_SOURCE,
        year=year,
        semester=None,
        month=month,
    )


def _movimentacao_entries_list() -> list[DatasetEntry]:
    entries: list[DatasetEntry] = []
    for year in range(_START_YEAR, _LAST_YEAR + 1):
        if year == _LAST_YEAR:
            max_month = max(1, _LAST_MONTH - 2)  # ~2 months lag
        else:
            max_month = 12
        for month in range(1, max_month + 1):
            entries.append(_movimentacao_entry(year, month))
    return entries


_movimentacao_entries: list[DatasetEntry] = _movimentacao_entries_list()

GROUPS_MOVIMENTACAO: dict[str, GroupInfo] = {
    "movimentacao-aeroportuaria": {
        "name": "Dados de Movimentação Aeroportuária",
        "entries": _movimentacao_entries,
    },
}

GROUP_ALIASES_MOVIMENTACAO: dict[str, str] = {
    "movimentacao": "movimentacao-aeroportuaria",
}
