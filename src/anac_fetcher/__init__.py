"""anac-fetcher — Download de dados abertos da ANAC (aviação civil)."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("anac-fetcher")
except PackageNotFoundError:
    __version__ = "0.0.0"

from .catalog import (
    GROUPS,
    DatasetEntry,
    GroupInfo,
    expand_group,
    list_datasets,
    resolve_group,
)
from .storage import DataRepository

__all__ = [
    "__version__",
    "GROUPS",
    "DatasetEntry",
    "GroupInfo",
    "DataRepository",
    "expand_group",
    "list_datasets",
    "resolve_group",
]
