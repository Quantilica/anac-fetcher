"""ANAC Percentuais de atrasos e cancelamentos catalog.

Percentuais de atrasos e cancelamentos de cada etapa de voo, divulgados
individualmente pelas empresas. Arquivos mensais, um por ano/mês, com 3
anexos (I, II e III), publicados em ``sistemas.anac.gov.br/dadosabertos``
desde 2000.

Layout no servidor:
``.../Percentuais de atrasos e cancelamentos/{year}/{month:02d} - {MêsPT}
/Anexo {I|II|III}.{ext}`` (meses em pt-BR minúsculo, ex.: ``03 - marco``).
"""

import datetime as dt
from urllib.parse import quote

from ._catalog_base import DatasetEntry, GroupInfo, slugify_filename

_SOURCE = "anac-dadosabertos"
_ROOT = "https://sistemas.anac.gov.br/dadosabertos"
_ATRASOS_DIR = quote(
    "Voos e operações aéreas/Percentuais de atrasos e cancelamentos",
    safe="/()",
)
_BASE = f"{_ROOT}/{_ATRASOS_DIR}"

_MESES_PT = {
    1: "janeiro",
    2: "fevereiro",
    3: "marco",
    4: "abril",
    5: "maio",
    6: "junho",
    7: "julho",
    8: "agosto",
    9: "setembro",
    10: "outubro",
    11: "novembro",
    12: "dezembro",
}

_ANEXOS = ("I", "II", "III")

# Meses em que a ANAC não publicou os dados (confirmado via HTTP 404 no
# servidor): junho e julho de 2014 (Copa do Mundo no Brasil).
_MISSING_MONTHS = {(2014, 6), (2014, 7)}

# Defasagem da publicação: o mês sai cerca de um a dois meses depois (medido em
# 2026-11-28: ``2026-09`` publicado em 2-nov; os diretórios de outubro a dezembro
# existem vazios). O catálogo vai até hoje menos ``_LAG_MONTHS`` meses,
# atravessando a virada do ano, e os ``_PENDING_MONTHS`` últimos levam
# ``pending_publication`` (404 = "ainda não publicado"); os mais antigos, que já
# deveriam existir, seguem falhando em 404.
_LAG_MONTHS = 2
_PENDING_MONTHS = 2


def _atraso_entry(
    year: int, month: int, anexo: str, ext: str, *, pending: bool = False
) -> DatasetEntry:
    month_dir = quote(f"{month:02d} - {_MESES_PT[month]}", safe="")
    source_name = f"Anexo {anexo}.{ext}"
    url = f"{_BASE}/{year}/{month_dir}/Anexo%20{anexo}.{ext}"
    entry = DatasetEntry(
        id=f"atrasos-{year}-{month:02d}-anexo-{anexo.lower()}-{ext}",
        base_id="atrasos-cancelamentos",
        slug=slugify_filename(source_name),
        name=f"Percentuais de atrasos e cancelamentos — Anexo {anexo} — "
        f"{_MESES_PT[month]}/{year}",
        url=url,
        ext=ext,
        group="atrasos-cancelamentos",
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


def _atrasos_entries_list(today: dt.date | None = None) -> list[DatasetEntry]:
    """Entradas de 2000-01 até ``today`` menos a defasagem.

    Na virada do ano a conta atravessa o ano (em janeiro o último mês é novembro
    do ano anterior), em vez de gerar um mês do ano corrente que não existe.
    """
    today = today or dt.date.today()
    last = _month_index(today.year, today.month) - _LAG_MONTHS
    first_pending = last - (_PENDING_MONTHS - 1)
    entries: list[DatasetEntry] = []
    for index in range(_month_index(2000, 1), last + 1):
        year, month = divmod(index, 12)
        month += 1
        if (year, month) in _MISSING_MONTHS:
            continue
        for anexo in _ANEXOS:
            for ext in ("csv", "json"):
                entries.append(
                    _atraso_entry(
                        year, month, anexo, ext, pending=index >= first_pending
                    )
                )
    return entries


_atrasos_entries: list[DatasetEntry] = _atrasos_entries_list()

GROUPS_ATRASOS: dict[str, GroupInfo] = {
    "atrasos-cancelamentos": {
        "name": "Percentuais de Atrasos e Cancelamentos",
        "entries": _atrasos_entries,
    },
}

GROUP_ALIASES_ATRASOS: dict[str, str] = {
    "atrasos": "atrasos-cancelamentos",
}
