"""ANAC Empresas Aéreas catalog.

Registro de empresas aéreas nacionais e estrangeiras autorizadas a operar
no Brasil, publicado por ``sistemas.anac.gov.br/dadosabertos``. Arquivos
estáticos substituídos periodicamente.
"""

from ._catalog_base import DatasetEntry, GroupInfo, _static

_SOURCE = "anac-dadosabertos"
_ROOT = "https://sistemas.anac.gov.br/dadosabertos"
_BASE = f"{_ROOT}/Operador%20A%C3%A9reo"

_empresas_aereas_entries: list[DatasetEntry] = [
    _static(
        "empresas-aereas",
        _SOURCE,
        "empresas-aereas-nacionais-csv",
        "Empresas Aéreas Nacionais (CSV)",
        f"{_BASE}/pda_empresas_aereas_nacionais.csv",
        "csv",
    ),
    _static(
        "empresas-aereas",
        _SOURCE,
        "empresas-aereas-nacionais-json",
        "Empresas Aéreas Nacionais (JSON)",
        f"{_BASE}/pda_empresas_aereas_nacionais.json",
        "json",
    ),
]

GROUPS_EMPRESAS_AEREAS: dict[str, GroupInfo] = {
    "empresas-aereas": {
        "name": "Empresas Aéreas Nacionais",
        "entries": _empresas_aereas_entries,
    },
}

GROUP_ALIASES_EMPRESAS_AEREAS: dict[str, str] = {
    "empresas": "empresas-aereas",
    "operadores-aereos": "empresas-aereas",
}
