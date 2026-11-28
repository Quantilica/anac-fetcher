"""Prova de equivalência: o lake tem o mesmo conteúdo antes e depois do agrupamento.

``golden/lake_antes_do_agrupamento.json`` foi gerado pelo conversor de um Parquet
por arquivo bruto (commit anterior à mudança). Aqui o conversor atual lê os mesmos
brutos e o retrato do lake, por arquivo de origem (linhas, colunas e tipos,
conteúdo ordenado), tem de ser o mesmo.

A única diferença admitida é a dos arquivos SEM sufixo de anexo
(``atrasos-cancelamentos_2026-09``): as versões antigas do fetcher gravavam esse
nome e ele é byte a byte igual a um dos anexos, então o lake antigo guardava as
linhas duas vezes. O teste prova, no golden, que o conteúdo desse arquivo é
exatamente o do anexo gêmeo; o lake novo guarda uma cópia só.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

pytest.importorskip("quantilica.analytics.lake")

from anac_fetcher.lake import converter  # noqa: E402

from .lake_fixtures import GOLDEN, build_raw, snapshot  # noqa: E402

_SEM_SUFIXO = re.compile(
    r"^atrasos-cancelamentos/\d{4}/\d{2}/atrasos-cancelamentos_\d{4}-\d{2}$"
)


def _golden() -> dict:
    return json.loads(GOLDEN.read_text(encoding="utf-8"))


def _viaje_json(obj: dict) -> dict:
    return json.loads(json.dumps(obj, ensure_ascii=False))


def test_arquivo_sem_sufixo_do_golden_e_copia_exata_de_um_anexo() -> None:
    lake = _golden()["lake"]
    gemeos = [k for k in lake if _SEM_SUFIXO.match(k)]
    assert gemeos  # as fixtures têm o caso
    for chave in gemeos:
        copias = [
            k
            for k in lake
            if k.startswith(chave + "_anexo-") and lake[k] == lake[chave]
        ]
        assert len(copias) == 1, chave


@pytest.mark.usefixtures("sem_contratos")
def test_conteudo_do_lake_igual_ao_do_conversor_anterior(tmp_path: Path) -> None:
    build_raw(tmp_path / "raw")
    res = converter.convert(tmp_path / "raw", tmp_path / "lake")
    assert not res.errors

    atual = _viaje_json(snapshot(tmp_path / "lake"))
    golden = _golden()["lake"]

    esperadas = sorted(k for k in golden if not _SEM_SUFIXO.match(k))
    assert sorted(k for k in atual if not _SEM_SUFIXO.match(k)) == esperadas
    for chave in esperadas:
        assert atual[chave]["linhas"] == golden[chave]["linhas"], chave
        assert atual[chave]["colunas"] == golden[chave]["colunas"], chave
        assert atual[chave]["conteudo"] == golden[chave]["conteudo"], chave
