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

from ._catalog_base import DatasetEntry, GroupInfo

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

# Última competência conhecida no catálogo (dados de meses recentes podem
# ainda não estar publicados; falhas de download individuais não interrompem
# o restante da sincronização — ver download.download_group).
_LAST_YEAR = dt.date.today().year
_LAST_MONTH = dt.date.today().month


def _atraso_entry(year: int, month: int, anexo: str, ext: str) -> DatasetEntry:
    month_dir = quote(f"{month:02d} - {_MESES_PT[month]}", safe="")
    url = f"{_BASE}/{year}/{month_dir}/Anexo%20{anexo}.{ext}"
    return DatasetEntry(
        id=f"atrasos-{year}-{month:02d}-anexo-{anexo.lower()}-{ext}",
        base_id="atrasos-cancelamentos",
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


def _atrasos_entries_list() -> list[DatasetEntry]:
    entries: list[DatasetEntry] = []
    for year in range(2000, _LAST_YEAR + 1):
        if year == _LAST_YEAR:
            max_month = max(1, _LAST_MONTH - 2)  # ~2 months lag
        else:
            max_month = 12
        for month in range(1, max_month + 1):
            for anexo in _ANEXOS:
                for ext in ("csv", "json"):
                    entries.append(_atraso_entry(year, month, anexo, ext))
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
