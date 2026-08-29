"""Extração e leitura tipada de arquivos brutos da ANAC.

Camada de conversão de dados coletados para Polars/Parquet, no padrão do
``anp-fetcher``/``pdet-fetcher`` (reader + wrangling). Lê CSV (latin-1/utf-8,
separador ``;``, decimal vírgula), JSON tabular, XLS/XLSX (via
``pl.read_excel`` + fastexcel) e arquivos ZIP/7z, normaliza dtypes e escreve
Parquet com metadados de proveniência extraídos do sidecar ``DownloadManifest``.
"""

from __future__ import annotations

import json
import logging
import re
import subprocess
import tempfile
from pathlib import Path
from typing import Any

import polars as pl
from quantilica.analytics.reader import read_brazilian_csv

logger = logging.getLogger(__name__)

# Layouts do storage do anac-fetcher (o stamp @YYYYMMDD é opcional — ausente
# quando o servidor não reporta Last-Modified):
#   {base_id}[@{YYYYMMDD}].{ext}                   (estático)
#   {base_id}_{year}[@{YYYYMMDD}].{ext}            (anual)
#   {base_id}_{year}-{part:02d}[@{YYYYMMDD}].{ext} (mensal/semestral)
_FILENAME_RE = re.compile(
    r"^(?P<base_id>.+?)"
    r"(?:_(?P<year>\d{4})(?:-(?P<part>\d{2}))?)?"
    r"(?:@(?P<mod>\d{8}))?"
    r"\.(?P<ext>[a-z0-9]+)$"
)

_DECOMPRESSIBLE = {".zip", ".7z"}


def parse_filename(path: Path) -> dict[str, Any]:
    """Extrai metadados de um arquivo no padrão de nome do storage ANAC.

    Args:
        path (Path): O caminho do arquivo bruto.

    Returns:
        dict[str, Any]: Metadados com ``base_id``, ``year``, ``part``,
            ``partition`` (string de partição ou None), ``modification``
            (YYYYMMDD) e ``ext``.
    """
    m = _FILENAME_RE.match(path.name)
    if not m:
        return {
            "filepath": path,
            "filename": path.name,
            "base_id": path.stem,
            "year": None,
            "part": None,
            "partition": None,
            "modification": None,
            "ext": path.suffix.lstrip("."),
        }
    g = m.groupdict()
    year = int(g["year"]) if g["year"] else None
    part = int(g["part"]) if g["part"] else None
    mod = int(g["mod"]) if g["mod"] else None
    if part is not None:
        partition = f"{year}-{part:02d}"
    elif year is not None:
        partition = str(year)
    else:
        partition = None
    return {
        "filepath": path,
        "filename": path.name,
        "base_id": g["base_id"],
        "year": year,
        "part": part,
        "partition": partition,
        "modification": mod,
        "ext": g["ext"],
    }


def decompress(path: Path) -> Path:
    """Descompacta um arquivo ZIP/7z e retorna o primeiro arquivo de dados.

    Args:
        path (Path): O caminho do arquivo compactado.

    Returns:
        Path: O caminho do arquivo extraído (primeiro csv/xls/xlsx/json).

    Raises:
        RuntimeError: Se o 7z falhar ou não produzir arquivos.
    """
    logger.info("Descompactando %s", path)
    tmp_dir = Path(tempfile.mkdtemp(prefix="anac_"))
    command = ["7z", "e", str(path), f"-o{tmp_dir}"]
    result = subprocess.run(command, capture_output=True)
    if result.returncode != 0:
        raise RuntimeError(
            f"7z falhou ao descompactar {path}: "
            f"{result.stderr.decode(errors='replace')}"
        )
    extracted = [p for p in tmp_dir.iterdir() if p.is_file()]
    if not extracted:
        raise RuntimeError(f"7z não produziu arquivos de {path}")
    data_file = next(
        (
            p
            for p in extracted
            if p.suffix.lower() in (".csv", ".xls", ".xlsx", ".json")
        ),
        extracted[0],
    )
    return data_file


def _preamble_rows(path: Path) -> int:
    """Conta linhas de preâmbulo no topo de arquivos CSV da ANAC.

    Os arquivos de dados abertos têm uma linha "Atualizado em: ..." (com BOM
    opcional) antes do cabeçalho real.

    Args:
        path (Path): O caminho do arquivo.

    Returns:
        int: Quantidade de linhas de preâmbulo (0 ou 1).
    """
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            count = 0
            line = f.readline()
            while line.startswith("\ufeff") or line.startswith("Atualizado em:"):
                count += 1
                line = f.readline()
        return count
    except OSError:
        return 0


def _sniff_separator(path: Path, skip_rows: int = 0) -> str:
    """Detecta o separador da primeira linha de dados (após o preâmbulo).

    A ANAC publica CSVs com separadores diferentes (a lista de aeródromos
    em ``.xls`` é `,`; o mesmo dado em ``.csv`` é `;`).

    Args:
        path (Path): O caminho do arquivo.
        skip_rows (int, optional): Linhas de preâmbulo a pular.

    Returns:
        str: O separador mais frequente entre ``;``, `,` e ``\\t``.
    """
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            for _ in range(skip_rows):
                next(f, None)
            first_line = f.readline()
    except OSError:
        return ";"
    counts = {sep: first_line.count(sep) for sep in (";", "\t", ",")}
    return max(counts, key=counts.__getitem__) or ";"


def read_csv(path: Path, spec: dict[str, Any]) -> pl.DataFrame:
    """Lê um CSV da ANAC (utf-8 com fallback latin-1, separador sniffado).

    Args:
        path (Path): Caminho do arquivo CSV.
        spec (dict[str, Any]): Especificação de processamento do grupo.

    Returns:
        pl.DataFrame: O DataFrame lido com tipos inferidos.
    """
    kwargs: dict[str, Any] = {}
    skip = spec.get("skip_rows", 0) + _preamble_rows(path)
    kwargs["separator"] = spec.get("separator") or _sniff_separator(path, skip)
    kwargs["infer_schema_length"] = spec.get("infer_schema_length", 0)
    kwargs["truncate_ragged_lines"] = True
    if skip:
        kwargs["skip_rows"] = skip
    encoding = spec.get("encoding")
    try:
        return read_brazilian_csv(
            path, encoding=encoding or "utf-8", decimal=",", **kwargs
        )
    except Exception as exc:  # fallback latin-1
        if encoding is not None:
            raise
        logger.debug("UTF-8 falhou (%s); tentando latin-1", exc)
        return read_brazilian_csv(path, encoding="latin-1", decimal=",", **kwargs)


def read_json(path: Path) -> pl.DataFrame:
    """Lê um JSON tabular (array de objetos) como DataFrame.

    Arquivos da ANAC têm BOM (utf-8-sig). Fallback para ``json.loads`` +
    ``pl.from_dicts`` quando o parser do polars falha por tipos mistos
    (ex.: ``"0"`` string vs. null numa mesma coluna).

    Args:
        path (Path): Caminho do arquivo JSON.

    Returns:
        pl.DataFrame: O DataFrame lido.
    """
    import json as _json
    from io import BytesIO

    text = path.read_text(encoding="utf-8-sig")
    try:
        return pl.read_json(BytesIO(text.encode("utf-8")))
    except Exception:
        data = _json.loads(text)
        try:
            return pl.from_dicts(data)
        except Exception:
            # Tipos mistos na mesma coluna (ex.: "0" string vs. null) — força
            # String para não perder registros (o CSV geminado tem tipos).
            overrides = {col: pl.Utf8 for col in data[0]}
            return pl.from_dicts(data, schema_overrides=overrides)


def read_excel(
    path: Path, spec: dict[str, Any]
) -> pl.DataFrame | dict[str, pl.DataFrame]:
    """Lê uma planilha XLS/XLSX.

    Args:
        path (Path): Caminho do arquivo de planilha.
        spec (dict[str, Any]): Especificação de processamento. ``sheet=None``
            lê a primeira aba; ``sheet=0`` lê todas as abas (dict); ``sheet=N``
            lê a N-ésima aba.

    Returns:
        pl.DataFrame | dict[str, pl.DataFrame]: DataFrame único ou dict de
            DataFrames por nome de aba.
    """
    sheet = spec.get("sheet")
    if sheet == "all":
        frames = pl.read_excel(path, sheet_id=0)
        assert isinstance(frames, dict), "sheet_id=0 deve retornar dict"
        return frames
    if sheet is None:
        return pl.read_excel(path, sheet_id=None)
    return pl.read_excel(path, sheet_id=sheet)


def read_file(
    path: Path, spec: dict[str, Any]
) -> pl.DataFrame | dict[str, pl.DataFrame]:
    """Lê um arquivo bruto conforme o formato e a especificação do grupo.

    Args:
        path (Path): Caminho do arquivo (csv, json, xls ou xlsx).
        spec (dict[str, Any]): Especificação de processamento do grupo.

    Returns:
        pl.DataFrame | dict[str, pl.DataFrame]: Dados lidos.

    Raises:
        ValueError: Se o formato não for suportado.
    """
    suffix = path.suffix.lower()
    if suffix == ".csv":
        return read_csv(path, spec)
    if suffix == ".json":
        return read_json(path)
    if suffix in (".xls", ".xlsx"):
        try:
            return read_excel(path, spec)
        except Exception:
            # ANAC publica alguns "xls" que são na verdade CSV-texto (ex.:
            # listas de aeródromos). Fallback para leitura CSV.
            logger.debug("Excel falhou em %s; tentando como CSV", path.name)
            return read_csv(path, spec)
    raise ValueError(f"Formato não suportado: {suffix}")


def normalize_dtypes(df: pl.DataFrame, spec: dict[str, Any]) -> pl.DataFrame:
    """Normaliza dtypes: números com vírgula decimal e strings sem espaços.

    Args:
        df (pl.DataFrame): O DataFrame a normalizar.
        spec (dict[str, Any]): Especificação com ``numeric_columns``.

    Returns:
        pl.DataFrame: O DataFrame normalizado.
    """
    numeric = set(spec.get("numeric_columns", []))
    df = df.with_columns(
        [
            pl.col(col)
            .str.replace_all(r"\.", "")
            .str.replace_all(",", ".")
            .cast(pl.Float64, strict=False)
            for col in numeric
            if col in df.columns and df[col].dtype == pl.Utf8
        ]
    )
    df = df.with_columns(
        [
            pl.col(col).str.strip_chars()
            for col in df.columns
            if col not in numeric and df[col].dtype == pl.Utf8
        ]
    )
    return df


def provenance_metadata(path: Path) -> dict[str, str]:
    """Lê o sidecar ``{path}.manifest.json`` e devolve metadados de proveniência.

    Args:
        path (Path): Caminho do arquivo de dados bruto.

    Returns:
        dict[str, str]: Metadados ``quantilica.*`` vazios se não houver manifest.
    """
    manifest_path = path.with_suffix(path.suffix + ".manifest.json")
    if not manifest_path.exists():
        return {}
    try:
        data = json.loads(manifest_path.read_text())
    except (json.JSONDecodeError, OSError) as exc:
        logger.warning("Manifest inválido %s: %s", manifest_path, exc)
        return {}
    return {
        "quantilica.source_id": str(data.get("source_id", "")),
        "quantilica.dataset_id": str(data.get("dataset_id", "")),
        "quantilica.origin_url": str(data.get("url", "")),
        "quantilica.origin_sha256": str(data.get("sha256", "")),
        "quantilica.fetched_at": str(data.get("fetched_at", "")),
        "quantilica.producer": str(data.get("producer", "")),
    }


def write_parquet(
    df: pl.DataFrame,
    target: Path,
    *,
    source_path: Path | None = None,
) -> Path:
    """Escreve um DataFrame como Parquet (zstd) com proveniência opcional.

    Args:
        df (pl.DataFrame): O DataFrame a escrever.
        target (Path): Caminho de destino do Parquet.
        source_path (Path | None, optional): Arquivo bruto de origem, para
            injetar os metadados do manifest sidecar.

    Returns:
        Path: O caminho do Parquet escrito.
    """
    target.parent.mkdir(parents=True, exist_ok=True)
    metadata = provenance_metadata(source_path) if source_path else {}
    df.write_parquet(target, compression="zstd", metadata=metadata)
    return target
