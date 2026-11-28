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

# Último mês CONFIRMADO no servidor (snapshot de 2026-11-28: ``2026/`` tem de
# ``202601`` a ``202605``; os cinco apareceram juntos em 2026-11-17). Não deriva
# do relógio: a ANAC publica em lotes, sem defasagem fixa (``2026-01`` esperou
# cerca de dez meses). Esta constante só diz até onde o 404 é erro desde o
# primeiro dia; NÃO é preciso editá-la para a coleta enxergar um mês novo.
#
# Os meses DEPOIS dela, até o mês corrente, também entram no catálogo, com
# ``pending_publication``: os que a fonte já publicou são coletados sem esperar a
# constante subir, e os que ainda não existem viram "ainda não publicado" (404
# tolerado pelo host). A folga é limitada: um mês pendente com mais de
# ``PENDING_MAX_MONTHS`` meses de calendário deixa de levar a marca, e o seu 404
# volta a ser erro (a fonte parou de publicar ou renomeou o arquivo).
LAST_PUBLISHED: tuple[int, int] = (2026, 5)

# Folga, em meses de calendário contados do mês do arquivo até hoje, em que o
# 404 de um mês depois de ``LAST_PUBLISHED`` ainda é "não publicado". O valor vem
# de UMA observação só (2026-11-28): a fonte publicou em lote, em 2026-11-17,
# meses com atraso de cerca de 6 (``2026-05``) a cerca de 10 (``2026-01``), e o
# diretório de cada ano só foi fechado perto de 1.º de junho do ano seguinte.
# Se o lote seguinte sair com o mesmo atraso, 12 viraria erro (saída parcial toda
# noite) antes da publicação; 18 dá mais de seis meses de margem sobre o pior
# caso visto, e o ponto cego da folga maior (arquivo publicado com outro nome) é
# coberto pelo ``unclassified`` do ``discover``. REVER este valor quando houver um
# segundo lote publicado.
PENDING_MAX_MONTHS = 18


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


def _month_index(year: int, month: int) -> int:
    return year * 12 + (month - 1)


def _movimentacao_entries_list(today: dt.date | None = None) -> list[DatasetEntry]:
    """Meses de 2019-03 até o mês de ``today`` (inclusive).

    Os meses até ``LAST_PUBLISHED`` são firmes. Os seguintes levam
    ``pending_publication`` enquanto estiverem a no máximo ``PENDING_MAX_MONTHS``
    meses de ``today`` (a virada do ano conta como mês corrido); mais antigos que
    isso, o 404 volta a ser erro.
    """
    today = today or dt.date.today()
    now = _month_index(today.year, today.month)
    entries: list[DatasetEntry] = []
    for year in range(_START_YEAR, max(LAST_PUBLISHED[0], today.year) + 1):
        # A publicação só iniciou em 2019-03; 2019-01/02 retornam 404.
        start_month = 3 if year == _START_YEAR else 1
        for month in range(start_month, 13):
            index = _month_index(year, month)
            if index > now:
                break
            pending = (year, month) > LAST_PUBLISHED and (
                now - index <= PENDING_MAX_MONTHS
            )
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
