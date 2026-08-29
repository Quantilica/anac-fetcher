"""ANAC unified dataset catalog.

Aggregates all groups from all catalog modules:
- catalog_vra:                  Voo Regular Ativo (voos, atrasos, cancelamentos)
- catalog_rab:                   Registro Aeronáutico Brasileiro (cadastro de aeronaves)
- catalog_ocorrencias:            Ocorrências Aeronáuticas (CENIPA)
- catalog_aerodromos:              Infraestrutura de aeródromos
- catalog_dados_estatisticos:      Dados Estatísticos do Transporte Aéreo
- catalog_drones:                  Drones cadastrados (SISANT)
- catalog_atrasos:                 Percentuais de atrasos e cancelamentos
- catalog_empresas_aereas:         Empresas Aéreas Nacionais
- catalog_movimentacao:            Dados de Movimentação Aeroportuária
- catalog_recomendacoes:           Recomendações de Segurança Aeronáutica

Public API is stable across future waves (mais grupos podem ser adicionados
sem quebrar esta interface).
"""

from ._catalog_base import DatasetEntry, GroupInfo
from .catalog_aerodromos import (
    AERODROMO_GROUP_KEYS,
    GROUP_ALIASES_AERODROMOS,
    GROUPS_AERODROMOS,
)
from .catalog_atrasos import GROUP_ALIASES_ATRASOS, GROUPS_ATRASOS
from .catalog_dados_estatisticos import (
    GROUP_ALIASES_DADOS_ESTATISTICOS,
    GROUPS_DADOS_ESTATISTICOS,
)
from .catalog_drones import GROUP_ALIASES_DRONES, GROUPS_DRONES
from .catalog_empresas_aereas import (
    GROUP_ALIASES_EMPRESAS_AEREAS,
    GROUPS_EMPRESAS_AEREAS,
)
from .catalog_movimentacao import GROUP_ALIASES_MOVIMENTACAO, GROUPS_MOVIMENTACAO
from .catalog_ocorrencias import GROUP_ALIASES_OCORRENCIAS, GROUPS_OCORRENCIAS
from .catalog_rab import GROUP_ALIASES_RAB, GROUPS_RAB
from .catalog_recomendacoes import (
    GROUP_ALIASES_RECOMENDACOES,
    GROUPS_RECOMENDACOES,
)
from .catalog_vra import GROUP_ALIASES_VRA, GROUPS_VRA

__all__ = [
    "DatasetEntry",
    "GroupInfo",
    "GROUPS",
    "GROUP_ALIASES",
    "ALL_GROUP_KEYS",
    "AERODROMO_GROUP_KEYS",
    "resolve_group",
    "expand_group",
    "list_datasets",
]

GROUPS: dict[str, GroupInfo] = {
    **GROUPS_VRA,
    **GROUPS_RAB,
    **GROUPS_OCORRENCIAS,
    **GROUPS_AERODROMOS,
    **GROUPS_DADOS_ESTATISTICOS,
    **GROUPS_DRONES,
    **GROUPS_ATRASOS,
    **GROUPS_EMPRESAS_AEREAS,
    **GROUPS_MOVIMENTACAO,
    **GROUPS_RECOMENDACOES,
}

GROUP_ALIASES: dict[str, str] = {
    **GROUP_ALIASES_VRA,
    **GROUP_ALIASES_RAB,
    **GROUP_ALIASES_OCORRENCIAS,
    **GROUP_ALIASES_AERODROMOS,
    **GROUP_ALIASES_DADOS_ESTATISTICOS,
    **GROUP_ALIASES_DRONES,
    **GROUP_ALIASES_ATRASOS,
    **GROUP_ALIASES_EMPRESAS_AEREAS,
    **GROUP_ALIASES_MOVIMENTACAO,
    **GROUP_ALIASES_RECOMENDACOES,
}

ALL_GROUP_KEYS: list[str] = list(GROUPS)

# Macro-aliases that expand to a list of canonical group ids (analogous to
# the "shpc" macro-alias in anp-fetcher).
_MACRO_GROUPS: dict[str, list[str]] = {
    "aerodromos": AERODROMO_GROUP_KEYS,
}


def resolve_group(key: str) -> str | None:
    """Resolve a group key or alias to a canonical group id.

    Does not resolve macro-aliases (see :func:`expand_group`), since those
    map to multiple groups.

    Args:
        key: The group key or alias to resolve.

    Returns:
        The canonical group id if found, otherwise None.
    """
    if key in GROUPS:
        return key
    return GROUP_ALIASES.get(key)


def expand_group(key: str) -> list[str]:
    """Expand a group key, alias, or macro-alias to canonical group id(s).

    Args:
        key: The group key, alias, or macro-alias to expand.

    Returns:
        A list of canonical group ids. Returns an empty list if the key
        is not recognized.
    """
    if key in _MACRO_GROUPS:
        return list(_MACRO_GROUPS[key])
    canon = resolve_group(key)
    return [canon] if canon is not None else []


def list_datasets(group: str | None = None) -> list[DatasetEntry]:
    """Return all dataset entries, optionally filtered by group.

    Args:
        group: The canonical group id or alias to filter datasets by.
            If None, returns all datasets across all groups.

    Returns:
        A list of DatasetEntry objects.

    Raises:
        ValueError: If a group is specified but not found in the catalog.
    """
    if group is not None:
        canon = resolve_group(group)
        if canon is None:
            raise ValueError(f"Unknown group: {group!r}")
        return list(GROUPS[canon]["entries"])
    return [entry for info in GROUPS.values() for entry in info["entries"]]
