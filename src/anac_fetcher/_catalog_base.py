"""Shared types and helper constructors for ANAC dataset catalogs."""

from typing import TypedDict


class DatasetEntry(TypedDict):
    id: str
    base_id: str
    name: str
    url: str
    ext: str
    group: str
    source: str
    year: int | None
    semester: int | None  # 1 or 2 — for semestral series
    month: int | None  # 1-12 — for monthly series


class GroupInfo(TypedDict):
    name: str
    entries: list[DatasetEntry]


def _static(
    group: str,
    source: str,
    id_: str,
    name: str,
    url: str,
    ext: str,
) -> DatasetEntry:
    return DatasetEntry(
        id=id_,
        base_id=id_,
        name=name,
        url=url,
        ext=ext,
        group=group,
        source=source,
        year=None,
        semester=None,
        month=None,
    )
