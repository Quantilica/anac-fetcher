"""CENIPA — Ocorrências Aeronáuticas catalog.

Tabela consolidada ("wide") de ocorrências aeronáuticas investigadas pelo
CENIPA, publicada por ``sistemas.anac.gov.br/dadosabertos`` e atualizada
diariamente.
"""

from ._catalog_base import DatasetEntry, GroupInfo, _static

_SOURCE = "anac-dadosabertos"
_BASE = "https://sistemas.anac.gov.br/dadosabertos/Seguranca%20Operacional/Ocorrencia"

_ocorrencias_entries: list[DatasetEntry] = [
    _static(
        "ocorrencias",
        _SOURCE,
        "ocorrencias-csv",
        "Ocorrências Aeronáuticas — CENIPA (CSV)",
        f"{_BASE}/V_OCORRENCIA_AMPLA.csv",
        "csv",
    ),
    _static(
        "ocorrencias",
        _SOURCE,
        "ocorrencias-json",
        "Ocorrências Aeronáuticas — CENIPA (JSON)",
        f"{_BASE}/V_OCORRENCIA_AMPLA.json",
        "json",
    ),
]

GROUPS_OCORRENCIAS: dict[str, GroupInfo] = {
    "ocorrencias": {
        "name": "Ocorrências Aeronáuticas (CENIPA)",
        "entries": _ocorrencias_entries,
    },
}

GROUP_ALIASES_OCORRENCIAS: dict[str, str] = {
    "cenipa": "ocorrencias",
    "acidentes": "ocorrencias",
}
