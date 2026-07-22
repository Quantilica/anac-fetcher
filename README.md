# anac-fetcher: Coletor de dados abertos da ANAC

![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg?style=flat-square) ![Python](https://img.shields.io/badge/python-3.12+-blue.svg?style=flat-square)

Utilitário de linha de comando para baixar dados públicos da [ANAC](https://www.gov.br/anac/) (Agência Nacional de Aviação Civil): voos regulares (VRA), cadastro de aeronaves (RAB), ocorrências aeronáuticas investigadas pelo CENIPA e infraestrutura de aeródromos. Descobre datasets a partir de um catálogo declarativo e faz o download organizado por grupo, com manifestos de proveniência via `quantilica-core`.

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
anac-fetcher discover
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

O `sync` aplica uma pausa de 0.3s entre downloads por padrão (cortesia ao
servidor em grupos grandes como `rab`, com ~250 arquivos); ajuste com
`--sleeptime SEGUNDOS` se necessário. Falhas pontuais (404 de meses ainda
não publicados, ou de formatos que não existem para aquele mês) são
normais, não interrompem a sincronização e aparecem no resumo final — rode
`sync` de novo para tentar só o que faltou.

Grupos disponíveis: `vra` (Voo Regular Ativo), `rab` (Registro Aeronáutico
Brasileiro), `ocorrencias` (Ocorrências Aeronáuticas — CENIPA) e os grupos de
aeródromos (`aero-lista-publicos`, `aero-pistas-pouso`, `aero-pistas-taxi`,
`aero-patio`, `aero-posicoes-estacionamento`, `aero-helipontos-publicos`,
`aero-excluidos`, `aero-seguranca`, `aero-lista-privados`, `aero-helideck`,
`aero-heliponto-privado`, `aero-pzr`, `aero-plano-diretor`), agrupáveis via
`aerodromos`.

### Integração com `quantilica-cli`

Se o `quantilica-cli` estiver instalado no mesmo ambiente, o `anac-fetcher` é
detectado automaticamente como plugin:

```bash
quantilica anac discover
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
