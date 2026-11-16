"""Brutos sintéticos da ANAC e retrato do lake, para as provas de equivalência.

``build_raw`` monta, em três meses de ``atrasos-cancelamentos``, os anexos como o
fetcher os grava (``<base>_<AAAA-MM>_anexo-<i|ii|iii>@<data>.csv``), e os casos
que o bruto real tem:

* anexos com esquemas diferentes (I tem 10 colunas, II 9, III 8) e, em 2026-10,
  os três com as mesmas 10 colunas (como em 2022-08 na fonte);
* o arquivo SEM sufixo de anexo (``<base>_<AAAA-MM>@<data>.csv``), que as versões
  antigas do fetcher gravavam e que é byte a byte igual a um dos anexos;
* o gêmeo em JSON de um anexo;
* um mês só com o Anexo III (como 2002-10 na fonte);
* um ``vra`` mensal e um ``rab`` sem partição, que a mudança não toca.

``snapshot`` descreve o lake por arquivo de origem (a chave do bruto, que no
layout antigo é o nome do Parquet e no agrupado é ``_origem``): linhas, colunas
com tipo e conteúdo ordenado. ``golden/lake_antes_do_agrupamento.json`` foi gerado
pelo conversor de um Parquet por arquivo bruto, antes da mudança:

    uv run --no-sync python -m tests.lake_fixtures --escrever-golden
"""

from __future__ import annotations

import json
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Any

from anac_fetcher.storage import _GROUP_DIRS

GOLDEN = Path(__file__).parent / "golden" / "lake_antes_do_agrupamento.json"

BASE = "atrasos-cancelamentos"
_COLUNAS_I = [
    "Empresa_Aerea",
    "N_Voo",
    "Aeroporto_Origem_Designador_OACI",
    "Aeroporto_Origem_Nome_UF_Pais ",  # o espaço no fim vem da fonte
    "Aeroporto_Destino_Designador_OACI",
    "Aeroporto_Destino_Nome_UF_Pais",
    "Etapas_Previstas",
    "Percentuais_de_Cancelamentos",
    "Percentuais_de_Atrasos_superiores_a_30_minutos",
    "Percentuais_de_Atrasos_superiores_a_60_minutos",
]
COLUNAS = {
    "i": _COLUNAS_I,
    "ii": [c for c in _COLUNAS_I if c != "N_Voo"],
    "iii": [c for c in _COLUNAS_I if c not in ("N_Voo", "Empresa_Aerea")],
}
_ESPECIAIS = ["AZUL LINHAS AÉREAS", "D'AVILA;ZE", 'O "GRANDE" VOO', "SÃO PAULO - SP"]


def _csv(anexo: str, mes: str, n: int, colunas: list[str]) -> bytes:
    linhas = [";".join(colunas)]
    for i in range(n):
        campos = []
        for j, nome in enumerate(colunas):
            if "Percentuais" in nome:
                campos.append(f"{(i * 7 + j) % 100},{(i * 13 + j) % 10000:04d}")
            elif (i + j) % 4 == 0:
                campos.append(_ESPECIAIS[(i + j) % len(_ESPECIAIS)])
            else:
                campos.append(f"{nome[:6]}-{anexo}-{mes}-{i}")
        linhas.append(";".join(f'"{c}"' if ";" in c else c for c in campos))
    return ("\n".join(linhas) + "\n").encode("latin-1")


def build_raw(root: Path) -> dict[str, Path]:
    """Cria o bruto sob ``root`` e devolve ``{descrição: caminho}`` dos arquivos."""
    pasta = root / _GROUP_DIRS[BASE]
    pasta.mkdir(parents=True)
    feitos: dict[str, Path] = {}

    def gravar(nome: str, conteudo: bytes) -> Path:
        caminho = pasta / nome
        caminho.write_bytes(conteudo)
        feitos[nome] = caminho
        return caminho

    # 2026-09: esquemas diferentes por anexo; o arquivo sem sufixo é cópia do III.
    for anexo, n in (("i", 9), ("ii", 5), ("iii", 4)):
        dados = _csv(anexo, "2026-09", n, COLUNAS[anexo])
        gravar(f"{BASE}_2026-09_anexo-{anexo}@20261101.csv", dados)
        if anexo == "iii":
            gravar(f"{BASE}_2026-09@20261101.csv", dados)
    # 2026-10: os três com as 10 colunas; o sem sufixo é cópia do I; o II tem JSON.
    for anexo, n in (("i", 6), ("ii", 5), ("iii", 4)):
        dados = _csv(anexo, "2026-10", n, COLUNAS["i"])
        gravar(f"{BASE}_2026-10_anexo-{anexo}@20261101.csv", dados)
        if anexo == "i":
            gravar(f"{BASE}_2026-10@20261101.csv", dados)
    gravar(
        f"{BASE}_2026-10_anexo-ii@20261101.json",
        json.dumps(
            [
                dict(zip(COLUNAS["i"], ["x"] * 10, strict=True)),
            ]
        ).encode("utf-8"),
    )
    # 2026-08: só o Anexo III, sem cópia.
    gravar(
        f"{BASE}_2026-08_anexo-iii@20261001.csv",
        _csv("iii", "2026-08", 3, COLUNAS["iii"]),
    )

    vra = root / _GROUP_DIRS["vra"]
    vra.mkdir(parents=True)
    (vra / "vra_2026-10@20261101.csv").write_text(
        "Empresa;Numero do Voo\nLATAM;1234\nAZUL;99\n", encoding="utf-8"
    )
    rab = root / _GROUP_DIRS["rab"]
    rab.mkdir(parents=True)
    (rab / "rab_dados@20261101.csv").write_text(
        "Marca;Modelo\nPT-ABC;PA-28\n", encoding="utf-8"
    )
    return feitos


def snapshot(lake_dir: Path) -> dict[str, Any]:
    """Retrato do lake por arquivo de origem: linhas, colunas e conteúdo ordenado.

    A chave é ``<dataset>/<partição>/<chave do bruto>``; a chave do bruto é o nome
    do Parquet no layout de um arquivo por bruto e a coluna ``_origem`` no agrupado.
    """
    import polars as pl

    saida: dict[str, Any] = {}
    base = lake_dir / "anac"
    for arquivo in sorted(base.rglob("*.parquet")):
        relativo = arquivo.relative_to(base)
        dataset = relativo.parts[0]
        particao = "/".join(p.split("=", 1)[1] for p in relativo.parts[1:-1])
        frame = pl.read_parquet(arquivo, hive_partitioning=False)
        if "_origem" in frame.columns:
            partes = [
                (str(chave[0]), parte.drop("_origem"))
                for chave, parte in frame.group_by("_origem", maintain_order=True)
            ]
        else:
            partes = [(arquivo.stem, frame)]
        for chave, parte in partes:
            saida[f"{dataset}/{particao}/{chave}"] = {
                "linhas": parte.height,
                "colunas": [[c, str(t)] for c, t in parte.schema.items()],
                "conteudo": sorted(
                    ["" if v is None else str(v) for v in linha]
                    for linha in parte.rows()
                ),
            }
    return dict(sorted(saida.items()))


def arquivos_por_mes(lake_dir: Path) -> dict[str, int]:
    """Parquets por ``<dataset>/<partição>``: o que a mudança reduz."""
    contagem: dict[str, int] = {}
    base = lake_dir / "anac"
    for arquivo in sorted(base.rglob("*.parquet")):
        relativo = arquivo.relative_to(base)
        chave = "/".join(
            [relativo.parts[0], *(p.split("=", 1)[1] for p in relativo.parts[1:-1])]
        )
        contagem[chave] = contagem.get(chave, 0) + 1
    return contagem


def _escrever_golden() -> None:
    from anac_fetcher.lake import converter

    with tempfile.TemporaryDirectory(prefix="anac-golden-") as tmp:
        raiz = Path(tmp)
        build_raw(raiz / "raw")
        resultado = converter.convert(raiz / "raw", raiz / "lake")
        assert not resultado.errors, resultado.errors
        GOLDEN.parent.mkdir(parents=True, exist_ok=True)
        GOLDEN.write_text(
            json.dumps(
                {
                    "arquivos_por_mes": arquivos_por_mes(raiz / "lake"),
                    "lake": snapshot(raiz / "lake"),
                },
                ensure_ascii=False,
                indent=1,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )
        shutil.rmtree(raiz / "lake")
    print(f"golden escrito em {GOLDEN}")


if __name__ == "__main__":
    if "--escrever-golden" not in sys.argv:
        raise SystemExit(__doc__)
    _escrever_golden()
