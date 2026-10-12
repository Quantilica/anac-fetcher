"""Shared types and helper constructors for ANAC dataset catalogs."""

import re
import unicodedata
from typing import NotRequired, TypedDict


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

    # Chave opcional em tempo de execução (leitura via ``entry.get("slug")``):
    # slug do nome do arquivo remoto, usado quando um mesmo grupo/partição
    # tem vários arquivos de origem (ex.: os anexos I, II e III de cada mês
    # de ``atrasos-cancelamentos``). Garante um caminho local distinto por
    # arquivo, no formato ``{base_id}_{partição}_{slug}@{carimbo}.{ext}``.
    slug: NotRequired[str | None]


class GroupInfo(TypedDict):
    """Represents a logical group of dataset entries.

    Attributes:
        name: Human-readable name for the group.
        entries: List of dataset entries belonging to this group.
    """

    name: str
    entries: list[DatasetEntry]


def slugify_filename(filename: str) -> str:
    """Slugify o nome de um arquivo remoto.

    Minúsculas, sem acentos, espaços/símbolos → ``-``, sem a extensão.

    Args:
        filename: Nome do arquivo remoto (ex.: ``"Anexo II.csv"``).

    Returns:
        O slug (ex.: ``"anexo-ii"``).

    Raises:
        ValueError: Se o slug resultante for vazio (nome sem caracteres
            alfanuméricos).
    """
    stem = filename.rsplit(".", 1)[0] if "." in filename else filename
    decomposed = unicodedata.normalize("NFKD", stem)
    ascii_lower = decomposed.encode("ascii", "ignore").decode("ascii").lower()
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_lower).strip("-")
    if not slug:
        raise ValueError(f"slugify_filename não consegue derivar slug de: {filename!r}")
    return slug


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
