"""ANAC Aeródromos catalog.

Infraestrutura de aeródromos públicos e privados: características gerais,
pistas, pátios, posições de estacionamento, áreas de pouso de helicóptero,
PZRs (planos de zoneamento de ruído) e planos diretores aeroportuários. Cada
subcategoria é um pequeno grupo próprio (snapshot único, sem partição
temporal); o alias de macro ``aerodromos`` expande para todos eles, no mesmo
espírito do alias ``shpc`` do anp-fetcher.
"""

from urllib.parse import quote

from ._catalog_base import DatasetEntry, GroupInfo, _static

_SOURCE = "anac-dadosabertos"
_ROOT = "https://sistemas.anac.gov.br/dadosabertos/Aerodromos"


def _enc(path: str) -> str:
    return quote(path, safe="/()")


_PUBLICOS = f"{_ROOT}/{_enc('Aeródromos Públicos')}"
_PRIVADOS_LISTA = f"{_ROOT}/{_enc('Aeródromos Privados/Lista de aeródromos privados')}"
_PZR = f"{_ROOT}/{_enc('Lista de PZRs Registrados')}"
_PLANO_DIRETOR = f"{_ROOT}/{_enc('PlanoDiretorAeroportuário')}"

# (group_id, group_name, base_url, [(dataset_suffix, filename_stem, exts)])
_SPECS: list[tuple[str, str, str, list[tuple[str, str, list[str]]]]] = [
    (
        "aero-lista-publicos",
        "Aeródromos Públicos — Lista",
        f"{_PUBLICOS}/{_enc('Lista de aeródromos públicos')}",
        [("lista", "AerodromosPublicos", ["csv", "json", "xls"])],
    ),
    (
        "aero-caracteristicas",
        "Aeródromos Públicos — Características Gerais",
        f"{_PUBLICOS}/{_enc('Características Gerais')}",
        [
            (
                "caracteristicas",
                "pda_aerodromos_publicos_caracteristicas_gerais",
                ["csv"],
            )
        ],
    ),
    (
        "aero-pistas-pouso",
        "Aeródromos Públicos — Pistas de Pouso e Decolagem",
        f"{_PUBLICOS}/{_enc('Pistas de Pouso e Decolagem')}",
        [
            (
                "pistas-pouso",
                "pda_aerodromos_publicos_pistas_pouso_decolagem",
                ["csv", "json"],
            )
        ],
    ),
    (
        "aero-pistas-taxi",
        "Aeródromos Públicos — Pistas de Táxi",
        f"{_PUBLICOS}/{_enc('Pistas de Táxi')}",
        [("pistas-taxi", "pda_aerodromos_publicos_pistas_de_taxi", ["csv"])],
    ),
    (
        "aero-patio",
        "Aeródromos Públicos — Dados de Pátio",
        f"{_PUBLICOS}/{_enc('Dados Pátio')}",
        [("patio", "V_AERODROMO_PUBLICO_DADOS_PATIO", ["csv", "json"])],
    ),
    (
        "aero-posicoes-estacionamento",
        "Aeródromos Públicos — Posições de Estacionamento",
        f"{_PUBLICOS}/Posicoes_Estacionamento",
        [
            (
                "posicoes-estacionamento",
                "pda_aerodromos_publicos_posicoes_estacionamento",
                ["csv", "json"],
            )
        ],
    ),
    (
        "aero-helipontos-publicos",
        "Aeródromos Públicos — Áreas de Pouso e Decolagem de Helicópteros",
        f"{_PUBLICOS}/{_enc('Áreas de Pouso e Decolagem de Helicópteros')}",
        [
            (
                "helipontos",
                _enc("Aerodromos Publicos Areas de Pouso e Decolagem de Helicopteros"),
                ["csv", "json"],
            )
        ],
    ),
    (
        "aero-excluidos",
        "Aeródromos Públicos — Excluídos",
        f"{_PUBLICOS}/{_enc('Aerodromos Excluidos')}",
        [("excluidos", "Aerodromos_Publicos_Excluidos", ["csv", "json"])],
    ),
    (
        "aero-seguranca",
        "Aeródromos Públicos — Programa de Segurança Aeroportuária",
        f"{_PUBLICOS}/{_enc('Programa de Seguranca Aeroportuaria')}",
        [("seguranca", "Psa", ["csv", "json"])],
    ),
    (
        "aero-lista-privados",
        "Aeródromos Privados — Lista",
        f"{_PRIVADOS_LISTA}/{_enc('Aerodromos Privados')}",
        [("lista-privados", "AerodromosPrivados", ["csv", "json", "xls"])],
    ),
    (
        "aero-helideck",
        "Aeródromos Privados — Helidecks",
        f"{_PRIVADOS_LISTA}/Helideck",
        [("helideck", "Helidecks", ["csv", "json", "xls"])],
    ),
    (
        "aero-heliponto-privado",
        "Aeródromos Privados — Helipontos",
        f"{_PRIVADOS_LISTA}/Heliponto",
        [("heliponto-privado", "Helipontos", ["csv", "json", "xls"])],
    ),
    (
        "aero-pzr",
        "Planos de Zoneamento de Ruído (PZR) Registrados",
        _PZR,
        [
            ("pzr-pbzr", "PZR_PBZR_Registrados", ["csv", "json"]),
            ("pzr-pezr", "PZR_PEZR_Registrados", ["csv", "json"]),
        ],
    ),
    (
        "aero-plano-diretor",
        "Planos Diretores Aeroportuários",
        _PLANO_DIRETOR,
        [
            (
                "plano-diretor-aprovados",
                _enc("Plano Diretor Aeroportuario Aprovados"),
                ["csv", "json"],
            ),
            (
                "plano-diretor-validados",
                _enc("Plano Diretor Aeroportuario Validados"),
                ["csv"],
            ),
        ],
    ),
]

AERODROMO_GROUP_KEYS: list[str] = [spec[0] for spec in _SPECS]

GROUPS_AERODROMOS: dict[str, GroupInfo] = {}
GROUP_ALIASES_AERODROMOS: dict[str, str] = {}

for _group_id, _group_name, _base_url, _files in _SPECS:
    _entries: list[DatasetEntry] = []
    for _suffix, _stem, _exts in _files:
        for _ext in _exts:
            _entries.append(
                _static(
                    _group_id,
                    _SOURCE,
                    f"{_group_id}-{_suffix}-{_ext}",
                    f"{_group_name} ({_ext.upper()})",
                    f"{_base_url}/{_stem}.{_ext}",
                    _ext,
                )
            )
    GROUPS_AERODROMOS[_group_id] = {"name": _group_name, "entries": _entries}
