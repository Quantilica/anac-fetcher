"""Tests for the optional lake inventory (``LakeConverter.inventory``)."""

from __future__ import annotations

from pathlib import Path

import pytest

pytest.importorskip("quantilica.analytics.lake")

core_lake = pytest.importorskip("quantilica.core.lake")
if not hasattr(core_lake, "Planned"):
    pytest.skip(
        "quantilica-core ainda sem o contrato do inventário (Planned)",
        allow_module_level=True,
    )

from anac_fetcher.lake import converter  # noqa: E402
from anac_fetcher.storage import _GROUP_DIRS  # noqa: E402

Planned = core_lake.Planned
converter_inventory = core_lake.converter_inventory

VRA_CSV = "Empresa;Numero do Voo;Codigo DI\nLATAM;1234;0\n"
RAB_CSV = "Marca;Modelo;Fabricante\nPT-ABC;PA-28;PIPER\n"


def _by_name(items: list[Planned]) -> dict[str, Planned]:
    return {Path(item.path).name: item for item in items}


def _write(path: Path, content: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def test_inventory_routes_files_to_their_datasets(tmp_path: Path) -> None:
    raw = tmp_path / "raw"
    _write(raw / _GROUP_DIRS["vra"] / "vra_2024-05@20240601.csv", VRA_CSV)
    _write(raw / _GROUP_DIRS["rab"] / "rab_dados@20240601.csv", RAB_CSV)

    items = _by_name(converter.inventory(raw))

    assert items["vra_2024-05@20240601.csv"].dataset == "vra"
    assert items["vra_2024-05@20240601.csv"].skip_reason is None
    assert items["rab_dados@20240601.csv"].dataset == "rab"
    assert items["rab_dados@20240601.csv"].skip_reason is None


def test_inventory_marks_twin_and_superseded(tmp_path: Path) -> None:
    raw = tmp_path / "raw"
    group_dir = raw / _GROUP_DIRS["rab"]
    _write(group_dir / "rab-hist-csv_2024-09@20240901.csv", RAB_CSV)
    _write(group_dir / "rab-hist-csv_2024-09@20241001.csv", RAB_CSV)
    _write(group_dir / "rab-hist-json_2024-09@20241001.json", "[]")
    _write(group_dir / "rab-hist_2024-09@20241001.zip", "PK")

    items = _by_name(converter.inventory(raw))

    assert items["rab-hist-csv_2024-09@20241001.csv"].dataset == "rab"
    # Mesmo conteúdo em outro formato: o conversor fica com o CSV.
    assert items["rab-hist-json_2024-09@20241001.json"].skip_reason == "gemeo"
    assert items["rab-hist_2024-09@20241001.zip"].skip_reason == "gemeo"
    # Mesmo formato, versão anterior.
    assert items["rab-hist-csv_2024-09@20240901.csv"].skip_reason == "superado"


def test_inventory_marks_non_tabular_and_skips_leftovers(tmp_path: Path) -> None:
    raw = tmp_path / "raw"
    group_dir = raw / _GROUP_DIRS["aero-plano-diretor"]
    _write(group_dir / "plano@20240601.csv", "A;B\n1;2\n")
    (group_dir / "layout@20240601.pdf").write_bytes(b"%PDF-1.4\n")
    (group_dir / "plano@20240601.csv.manifest.json").write_text("{}", encoding="utf-8")
    (group_dir / ".plano@20240601.csv.abc123.tmp").write_text("resto", encoding="utf-8")

    items = _by_name(converter.inventory(raw))

    assert set(items) == {"plano@20240601.csv", "layout@20240601.pdf"}
    assert items["plano@20240601.csv"].dataset == "aero-plano-diretor"
    assert items["layout@20240601.pdf"].skip_reason == "nao_tabular"
    assert items["layout@20240601.pdf"].dataset is None


def test_inventory_separates_mixed_granularities(tmp_path: Path) -> None:
    raw = tmp_path / "raw"
    group_dir = raw / _GROUP_DIRS["drones"]
    _write(group_dir / "drones-hist_2022-08@20220801.csv", "ID;Modelo\n1;DJI\n")
    _write(group_dir / "drones-atual-csv@20261021.csv", "ID;Modelo\n2;DJI\n")

    items = _by_name(converter.inventory(raw))

    assert items["drones-hist_2022-08@20220801.csv"].dataset == "drones"
    assert items["drones-atual-csv@20261021.csv"].dataset == "drones-atual"


def test_inventory_matches_convert(tmp_path: Path) -> None:
    raw = tmp_path / "raw"
    group_dir = raw / _GROUP_DIRS["vra"]
    _write(group_dir / "vra_2024-05@20240601.csv", VRA_CSV)
    _write(group_dir / "vra_2024-05@20240601.json", "[]")
    (group_dir / "leia-me.pdf").write_bytes(b"%PDF-1.4\n")
    lake = tmp_path / "lake"

    items = converter.inventory(raw)
    res = converter.convert(raw, lake)
    # O PDF entra na descoberta do conversor e falha na leitura: não gera Parquet,
    # que é o que o inventário declara com "nao_tabular".
    assert res.converted == 1
    assert [e.split(":", 1)[0] for e in res.errors] == ["leia-me.pdf"]

    planned = {item.dataset for item in items if item.dataset}
    written = {p.name for p in (lake / "anac").iterdir() if p.is_dir()}
    assert planned == written == {"vra"}


def test_inventory_is_the_optional_contract_member(tmp_path: Path) -> None:
    raw = tmp_path / "raw"
    _write(raw / _GROUP_DIRS["vra"] / "vra_2024-05@20240601.csv", VRA_CSV)

    items = converter_inventory(converter, raw)

    assert items is not None
    assert [Path(item.path).name for item in items] == ["vra_2024-05@20240601.csv"]


def test_inventory_covers_files_outside_group_dirs(tmp_path: Path) -> None:
    raw = tmp_path / "raw"
    _write(raw / "solto" / "dados.csv", "A;B\n1;2\n")
    (raw / "solto" / "manual.pdf").write_bytes(b"%PDF-1.4\n")

    items = _by_name(converter.inventory(raw))

    # O conversor não procura fora dos diretórios de grupo: o tabular fica sem
    # destino (a auditoria aponta a lacuna) e o documento é não tabular.
    assert items["dados.csv"].dataset is None
    assert items["dados.csv"].skip_reason is None
    assert items["manual.pdf"].skip_reason == "nao_tabular"


def test_inventory_of_missing_directory_is_empty(tmp_path: Path) -> None:
    assert converter.inventory(tmp_path / "nao-existe") == []
