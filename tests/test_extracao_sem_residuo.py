"""A extração de ZIP/7z não deixa pasta no temp do sistema (``quantilica_extract_*``).

O ZIP tem subpasta: a raiz da extração não é o ``parent`` do arquivo devolvido,
e era essa raiz que ficava para trás.
"""

from __future__ import annotations

import tempfile
import warnings
import zipfile
from collections.abc import Iterator
from pathlib import Path

import polars as pl
import pytest

pytest.importorskip("quantilica.analytics.lake")
pytest.importorskip("duckdb")

from anac_fetcher.lake import SOURCE_ID, converter  # noqa: E402
from anac_fetcher.reader import decompress, extracted_data  # noqa: E402
from anac_fetcher.storage import _GROUP_DIRS  # noqa: E402
from anac_fetcher.wrangling import convert_one  # noqa: E402

# O aviso do core quando ``decompress_archive`` cria a pasta sozinho.
SEM_AVISO_DO_CORE = r".*decompress_archive\(\)"

CSV = "Empresa;Numero do Voo;Codigo DI;Codigo Tipo Linha\nLATAM;1234;0;N\n"


@pytest.fixture
def temp_isolado(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[Path]:
    """TMPDIR só deste teste; o ``tempfile`` esquece o cache do temp anterior."""
    temp = tmp_path / "tmpdir"
    temp.mkdir()
    monkeypatch.setenv("TMPDIR", str(temp))
    monkeypatch.setattr(tempfile, "tempdir", None)
    assert Path(tempfile.gettempdir()) == temp
    yield temp


@pytest.fixture
def sem_aviso_do_core() -> Iterator[None]:
    with warnings.catch_warnings():
        warnings.filterwarnings(
            "error", category=DeprecationWarning, message=SEM_AVISO_DO_CORE
        )
        yield


def _zip_com_subpasta(path: Path, member: str = "pasta/interna/dados.csv") -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "w") as zf:
        zf.writestr(member, CSV)
    return path


def _sobras(temp: Path) -> list[str]:
    return sorted(p.name for p in temp.iterdir())


@pytest.mark.usefixtures("sem_aviso_do_core")
def test_extracted_data_remove_a_raiz_com_subpasta(
    tmp_path: Path, temp_isolado: Path
) -> None:
    raw = _zip_com_subpasta(tmp_path / "raw.zip")
    with extracted_data(raw) as inner:
        assert inner.name == "dados.csv"
        assert inner.parent != temp_isolado  # está numa subpasta da raiz
        assert inner.read_text() == CSV
        assert _sobras(temp_isolado)  # existe dentro do with
    assert _sobras(temp_isolado) == []


@pytest.mark.usefixtures("sem_aviso_do_core")
def test_extracted_data_remove_a_raiz_em_excecao(
    tmp_path: Path, temp_isolado: Path
) -> None:
    raw = _zip_com_subpasta(tmp_path / "raw.zip")
    with pytest.raises(ValueError, match="boom"):
        with extracted_data(raw):
            raise ValueError("boom")
    assert _sobras(temp_isolado) == []


@pytest.mark.usefixtures("sem_aviso_do_core")
def test_extracted_data_converte_storage_error_em_runtime_error(
    tmp_path: Path, temp_isolado: Path
) -> None:
    ruim = tmp_path / "ruim.zip"
    ruim.write_bytes(b"isto nao e um zip")
    with pytest.raises(RuntimeError, match="falha ao descompactar"):
        with extracted_data(ruim):
            pass
    assert _sobras(temp_isolado) == []


@pytest.mark.usefixtures("sem_aviso_do_core")
@pytest.mark.usefixtures("sem_contratos")
def test_wrangling_convert_one_zip_com_subpasta_nao_deixa_residuo(
    tmp_path: Path, temp_isolado: Path
) -> None:
    raw = _zip_com_subpasta(tmp_path / "in" / "vra_2024-05@20240601.zip")
    written = convert_one("vra", raw, tmp_path / "out")
    assert len(written) == 1
    assert pl.read_parquet(written[0]).height == 1
    assert _sobras(temp_isolado) == []


@pytest.mark.usefixtures("sem_aviso_do_core")
def test_wrangling_zip_sem_dados_nao_deixa_residuo(
    tmp_path: Path, temp_isolado: Path
) -> None:
    raw = tmp_path / "in" / "vra_2024-05@20240601.zip"
    raw.parent.mkdir()
    with zipfile.ZipFile(raw, "w") as zf:
        zf.writestr("sub/leia-me.txt", "sem dados")  # nenhum csv/xls/json
    assert convert_one("vra", raw, tmp_path / "out") == []
    assert _sobras(temp_isolado) == []


@pytest.mark.usefixtures("sem_aviso_do_core")
@pytest.mark.usefixtures("sem_contratos")
def test_lake_build_zip_com_subpasta_nao_deixa_residuo(
    tmp_path: Path, temp_isolado: Path
) -> None:
    _zip_com_subpasta(
        tmp_path / "raw" / _GROUP_DIRS["vra"] / "vra_2024-05@20240601.zip"
    )
    res = converter.convert(tmp_path / "raw", tmp_path / "lake")
    assert not res.errors, res.errors
    assert res.converted == 1
    assert (tmp_path / "lake" / SOURCE_ID / "vra").exists()
    assert _sobras(temp_isolado) == []


@pytest.mark.usefixtures("sem_aviso_do_core")
def test_lake_build_zip_ilegivel_vira_erro_e_nao_deixa_residuo(
    tmp_path: Path, temp_isolado: Path
) -> None:
    raw = tmp_path / "raw" / _GROUP_DIRS["vra"] / "vra_2024-05@20240601.zip"
    raw.parent.mkdir(parents=True)
    with zipfile.ZipFile(raw, "w") as zf:
        zf.writestr("sub/leia-me.txt", "sem dados")
    res = converter.convert(tmp_path / "raw", tmp_path / "lake")
    assert res.errors and "erro na descompressão" in res.errors[0]
    assert _sobras(temp_isolado) == []


def test_decompress_legado_avisa_que_a_pasta_fica_por_conta_do_chamador(
    tmp_path: Path, temp_isolado: Path
) -> None:
    raw = _zip_com_subpasta(tmp_path / "raw.zip")
    with pytest.warns(DeprecationWarning, match=SEM_AVISO_DO_CORE):
        decompress(raw)
