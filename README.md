# anac-fetcher: Coletor de dados abertos da ANAC

![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg?style=flat-square) ![Python](https://img.shields.io/badge/python-3.12+-blue.svg?style=flat-square)

Utilitário de linha de comando para baixar dados públicos da [ANAC](https://www.gov.br/anac/) (Agência Nacional de Aviação Civil): voos regulares (VRA), dados estatísticos do transporte aéreo, percentuais de atrasos e cancelamentos, cadastro de aeronaves (RAB), drones (SISANT), empresas aéreas, movimentação aeroportuária, ocorrências e recomendações de segurança aeronáutica, e infraestrutura de aeródromos. Descobre datasets a partir de um catálogo declarativo e faz o download organizado por grupo, com manifestos de proveniência via `quantilica-core`.

Para a documentação completa, consulte a [Documentação Oficial do Quantilica](https://docs.quantilica.com).
## Instalação

```bash
pip install anac-fetcher
```

Com [uv](https://github.com/astral-sh/uv):

```bash
uv add anac-fetcher
```

**Requisitos:** Python 3.12+

## Uso

### Listar os datasets disponíveis

```bash
anac-fetcher list
```

### Sincronizar (baixar) datasets

```bash
# Baixar todos os grupos
anac-fetcher sync

# Baixar grupos específicos
anac-fetcher sync vra rab -o ./dados/anac

# Baixar todos os grupos de aeródromos de uma vez
anac-fetcher sync aerodromos

# Listar os arquivos que seriam baixados, sem baixar
anac-fetcher sync --dry-run
```

O `sync` baixa em paralelo (`--workers`, padrão 4) e pula o que já está
atualizado. Falhas pontuais (404 de meses ainda não publicados, ou de
formatos que não existem para aquele mês) são normais, não interrompem a
sincronização e aparecem no resumo final — rode `sync` de novo para tentar
só o que faltou.

Grupos disponíveis:

- `vra` (Voo Regular Ativo) · `atrasos-cancelamentos` (percentuais de
  atrasos e cancelamentos, desde 2000) · `dados-estatisticos` (dados
  estatísticos do transporte aéreo)
- `rab` (Registro Aeronáutico Brasileiro) · `drones` (cadastro de drones —
  SISANT, snapshot + histórico mensal desde 2022-08) · `empresas-aereas`
  (empresas aéreas nacionais)
- `ocorrencias` (Ocorrências Aeronáuticas — CENIPA) ·
  `recomendacoes-seguranca` (recomendações de segurança aeronáutica)
- `movimentacao-aeroportuaria` (movimentação de passageiros, carga e
  aeronaves por aeroporto, desde 2019 — apenas CSV, o JSON mensal é muito
  volumoso)
- grupos de aeródromos (`aero-lista-publicos`, `aero-pistas-pouso`,
  `aero-pistas-taxi`, `aero-patio`, `aero-posicoes-estacionamento`,
  `aero-helipontos-publicos`, `aero-excluidos`, `aero-seguranca`,
  `aero-lista-privados`, `aero-helideck`, `aero-heliponto-privado`,
  `aero-pzr`, `aero-plano-diretor`), agrupáveis via `aerodromos`

Use `anac-fetcher list` para ver os nomes canônicos e aliases.

### Converter para Parquet

Após o `sync`, os dados brutos podem ser convertidos para Parquet (requer o
extra `[analysis]`):

```bash
# Converter todos os grupos
anac-fetcher convert -i ./dados/anac -o ./dados/anac

# Converter grupos específicos (aceita aliases)
anac-fetcher convert ocorrencias vra -i ./dados/anac -o ./dados/anac

# Pipeline completo: sync + convert dos grupos escolhidos
anac-fetcher pipeline ocorrencias -o ./dados/anac
```

A conversão é **idempotente** (pula o que já foi convertido), lê CSV/XLS/XLSX/JSON
(com preâmbulo "Atualizado em:" e separador auto-detectados, linhas ragged
truncadas) e injeta a proveniência do `DownloadManifest` nos metadados do
Parquet (`quantilica.*`). Grupos-chave (`ocorrencias`, `recomendacoes-seguranca`,
`vra`, `aero-lista-publicos`) têm `DataContract` de validação aplicado.

### Integração com `quantilica-cli`

Se o `quantilica-cli` estiver instalado no mesmo ambiente, o `anac-fetcher` é
detectado automaticamente como plugin:

```bash
quantilica anac list
```

## API Python

```python
from anac_fetcher.catalog import list_datasets

for entry in list_datasets(group="vra"):
    print(entry["id"], entry["url"])
```

## Desenvolvimento

```bash
git clone https://github.com/Quantilica/anac-fetcher.git
cd anac-fetcher
uv sync --group dev
uv run ruff check src/ tests/
uv run pytest
```

## Licença

MIT — veja [LICENSE](LICENSE).
