"""ANAC Dados Estatísticos do Transporte Aéreo catalog.

Série histórica consolidada de dados estatísticos do transporte aéreo
(doméstico e internacional), publicada por
``sistemas.anac.gov.br/dadosabertos``. Arquivos estáticos substituídos
periodicamente (snapshot completo + JSON por década).
"""

from ._catalog_base import DatasetEntry, GroupInfo, _static

_SOURCE = "anac-dadosabertos"
_ROOT = "https://sistemas.anac.gov.br/dadosabertos"
_BASE = (
    f"{_ROOT}/Voos%20e%20opera%C3%A7%C3%B5es%20a%C3%A9reas/"
    "Dados%20Estat%C3%ADsticos%20do%20Transporte%20A%C3%A9reo"
)

_dados_estatisticos_entries: list[DatasetEntry] = [
    _static(
        "dados-estatisticos",
        _SOURCE,
        "dados-estatisticos-csv",
        "Dados Estatísticos do Transporte Aéreo — histórico completo (CSV)",
        f"{_BASE}/Dados_Estatisticos.csv",
        "csv",
    ),
    _static(
        "dados-estatisticos",
        _SOURCE,
        "dados-estatisticos-2000-2010-json",
        "Dados Estatísticos do Transporte Aéreo — 2000 a 2010 (JSON)",
        f"{_BASE}/Dados_Estatisticos_2000_a_2010.json",
        "json",
    ),
    _static(
        "dados-estatisticos",
        _SOURCE,
        "dados-estatisticos-2011-2020-json",
        "Dados Estatísticos do Transporte Aéreo — 2011 a 2020 (JSON)",
        f"{_BASE}/Dados_Estatisticos_2011_a_2020.json",
        "json",
    ),
    _static(
        "dados-estatisticos",
        _SOURCE,
        "dados-estatisticos-2021-2030-json",
        "Dados Estatísticos do Transporte Aéreo — 2021 a 2030 (JSON)",
        f"{_BASE}/Dados_Estatisticos_2021_a_2030.json",
        "json",
    ),
]

GROUPS_DADOS_ESTATISTICOS: dict[str, GroupInfo] = {
    "dados-estatisticos": {
        "name": "Dados Estatísticos do Transporte Aéreo",
        "entries": _dados_estatisticos_entries,
    },
}

GROUP_ALIASES_DADOS_ESTATISTICOS: dict[str, str] = {
    "estatisticas": "dados-estatisticos",
}
