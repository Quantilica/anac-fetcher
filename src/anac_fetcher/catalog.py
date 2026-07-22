"""ANAC unified dataset catalog.

Aggregates all groups from all catalog modules:
- catalog_vra:          Voo Regular Ativo (voos, atrasos, cancelamentos)
- catalog_rab:           Registro Aeronáutico Brasileiro (cadastro de aeronaves)
- catalog_ocorrencias:    Ocorrências Aeronáuticas (CENIPA)
- catalog_aerodromos:      Infraestrutura de aeródromos

Public API is stable across future waves (mais grupos podem ser adicionados
sem quebrar esta interface).
"""

from ._catalog_base import DatasetEntry, GroupInfo
from .catalog_aerodromos import (
    AERODROMO_GROUP_KEYS,
    GROUP_ALIASES_AERODROMOS,
    GROUPS_AERODROMOS,
)
from .catalog_ocorrencias import GROUP_ALIASES_OCORRENCIAS, GROUPS_OCORRENCIAS
from .catalog_rab import GROUP_ALIASES_RAB, GROUPS_RAB
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
}

GROUP_ALIASES: dict[str, str] = {
    **GROUP_ALIASES_VRA,
    **GROUP_ALIASES_RAB,
    **GROUP_ALIASES_OCORRENCIAS,
    **GROUP_ALIASES_AERODROMOS,
}

ALL_GROUP_KEYS: list[str] = list(GROUPS)

# Macro-aliases that expand to a list of canonical group ids (analogous to
# the "shpc" macro-alias in anp-fetcher).
_MACRO_GROUPS: dict[str, list[str]] = {
    "aerodromos": AERODROMO_GROUP_KEYS,
}


def resolve_group(key: str) -> str | None:
    """Resolve a group key or alias to a canonical group id.

    Returns None if not found. Does not resolve macro-aliases (see
    :func:`expand_group`), since those map to multiple groups.
    """
    if key in GROUPS:
        return key
    return GROUP_ALIASES.get(key)


def expand_group(key: str) -> list[str]:
    """Expand a group key, alias, or macro-alias to canonical group id(s).

    Returns an empty list if the key is not recognized.
    """
    if key in _MACRO_GROUPS:
        return list(_MACRO_GROUPS[key])
    canon = resolve_group(key)
    return [canon] if canon is not None else []


def list_datasets(group: str | None = None) -> list[DatasetEntry]:
    """Return all dataset entries, optionally filtered by group."""
    if group is not None:
        canon = resolve_group(group)
        if canon is None:
            raise ValueError(f"Unknown group: {group!r}")
        return list(GROUPS[canon]["entries"])
    return [entry for info in GROUPS.values() for entry in info["entries"]]
