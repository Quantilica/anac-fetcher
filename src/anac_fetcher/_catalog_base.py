"""Shared types and helper constructors for ANAC dataset catalogs."""

from typing import TypedDict


class DatasetEntry(TypedDict):
    """Represents a single dataset entry to be downloaded.

    Attributes:
        id: Unique identifier for this exact file.
        base_id: The base identifier for the dataset series.
        name: Human-readable name for the dataset.
        url: The download URL.
        ext: File extension (e.g., 'csv', 'json').
        group: The logical group this entry belongs to.
        source: The data source origin.
        year: Year of the dataset (if applicable).
        semester: Semester of the dataset (1 or 2, if applicable).
        month: Month of the dataset (1-12, if applicable).
    """

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
    """Represents a logical group of dataset entries.

    Attributes:
        name: Human-readable name for the group.
        entries: List of dataset entries belonging to this group.
    """

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
