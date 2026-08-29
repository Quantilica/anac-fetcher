"""ANAC Recomendações de Segurança Aeronáutica catalog.

Recomendações de segurança emitidas pelo CENIPA, publicadas por
``sistemas.anac.gov.br/dadosabertos`` e atualizadas diariamente.
"""

from ._catalog_base import DatasetEntry, GroupInfo, _static

_SOURCE = "anac-dadosabertos"
_BASE = "https://sistemas.anac.gov.br/dadosabertos/Seguranca%20Operacional/Recomenda%C3%A7%C3%A3o%20de%20Seguran%C3%A7a"

_recomendacoes_entries: list[DatasetEntry] = [
    _static(
        "recomendacoes-seguranca",
        _SOURCE,
        "recomendacoes-seguranca-csv",
        "Recomendações de Segurança Aeronáutica (CSV)",
        f"{_BASE}/RECOMENDACAO_SEGURANCA.csv",
        "csv",
    ),
    _static(
        "recomendacoes-seguranca",
        _SOURCE,
        "recomendacoes-seguranca-json",
        "Recomendações de Segurança Aeronáutica (JSON)",
        f"{_BASE}/RECOMENDACAO_SEGURANCA.json",
        "json",
    ),
]

GROUPS_RECOMENDACOES: dict[str, GroupInfo] = {
    "recomendacoes-seguranca": {
        "name": "Recomendações de Segurança Aeronáutica",
        "entries": _recomendacoes_entries,
    },
}

GROUP_ALIASES_RECOMENDACOES: dict[str, str] = {
    "recomendacoes": "recomendacoes-seguranca",
    "rsa": "recomendacoes-seguranca",
}
