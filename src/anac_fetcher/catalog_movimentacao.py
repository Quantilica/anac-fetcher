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

# Último mês publicado no servidor (snapshot de 2026-11-05: o diretório
# ``2026/`` não existe; o índice termina em ``202512``). A ANAC não segue
# defasagem fixa, então o fim dos meses CONFIRMADOS NÃO deriva da data de hoje:
# gerar meses por relógio, como erro, produzia 404 em todo o ano seguinte. Para
# avançar, rode ``anac-fetcher discover`` e atualize esta constante.
#
# Os meses DEPOIS dele, até o mês corrente, também entram no catálogo, mas com
# ``pending_publication``: os que a fonte já publicou passam a ser coletados sem
# esperar a constante subir, e os que ainda não existem viram "ainda não
# publicado" (404 tolerado pelo host), sem erro.
LAST_PUBLISHED: tuple[int, int] = (2025, 12)


def _movimentacao_entry(
    year: int, month: int, *, pending: bool = False
) -> DatasetEntry:
    url = f"{_BASE}/{year}/Movimentacoes_Aeroportuarias_{year}{month:02d}.csv"
    entry = DatasetEntry(
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
    if pending:
        entry["pending_publication"] = True
    return entry


def _movimentacao_entries_list(today: dt.date | None = None) -> list[DatasetEntry]:
    """Meses de 2019-03 até ``LAST_PUBLISHED`` e, marcados como pendentes, os
    seguintes até o mês de ``today`` (inclusive)."""
    today = today or dt.date.today()
    last_year, last_month = LAST_PUBLISHED
    entries: list[DatasetEntry] = []
    for year in range(_START_YEAR, max(last_year, today.year) + 1):
        # A publicação só iniciou em 2019-03; 2019-01/02 retornam 404.
        start_month = 3 if year == _START_YEAR else 1
        for month in range(start_month, 13):
            if (year, month) > (today.year, today.month):
                break
            pending = (year, month) > LAST_PUBLISHED
            entries.append(_movimentacao_entry(year, month, pending=pending))
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
