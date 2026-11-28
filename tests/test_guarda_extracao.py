"""A guarda de sessão (``conftest.py``) confere as sobras ``quantilica_extract_*``.

Este teste de propósito não isola o ``TMPDIR`` (como faz
``test_extracao_sem_residuo.py``): usa o da sessão, e a guarda falha a suíte ao fim
se a conversão do ZIP com subpasta deixar a raiz da extração para trás.
"""

from __future__ import annotations

import tempfile
import zipfile
from pathlib import Path

import pytest

pytest.importorskip("quantilica.analytics.lake")
pytest.importorskip("duckdb")

from anac_fetcher.wrangling import convert_one  # noqa: E402

CSV = "Empresa;Numero do Voo;Codigo DI;Codigo Tipo Linha\nLATAM;1234;0;N\n"


@pytest.mark.usefixtures("sem_contratos")
def test_convert_one_zip_com_subpasta_no_temp_da_sessao(
    tmp_path: Path, guarda_extracao_sem_residuo: Path
) -> None:
    assert Path(tempfile.gettempdir()) == guarda_extracao_sem_residuo
    raw = tmp_path / "in" / "vra_2024-05@20240601.zip"
    raw.parent.mkdir()
    with zipfile.ZipFile(raw, "w") as zf:
        zf.writestr("pasta/interna/dados.csv", CSV)
    assert len(convert_one("vra", raw, tmp_path / "out")) == 1
