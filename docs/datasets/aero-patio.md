---
dataset:
  id: aero-patio
  fonte: anac
  titulo: "Aeródromos públicos: pátios de estacionamento"
  resumo: "Pátios de estacionamento de aeronaves em aeródromos públicos, com identificação, pavimento e resistência."
  orgao: Agência Nacional de Aviação Civil (ANAC)
  pagina_oficial: https://www.anac.gov.br/acesso-a-informacao/dados-abertos/areas-de-atuacao/aerodromos/aerodromos-publicos-patios-de-estacionamento
  licenca: "Não informada pela fonte: as páginas de metadados da ANAC não trazem licença (conferido em 2026-11-15)."
  periodicidade: "semanal"
  cobertura: {inicio: "2026-11", fim: "em-curso"}
  unidade: "um pátio de aeronaves de um aeródromo"
  granularidade: {espacial: "Brasil (aeródromo)", temporal: "cadastro vigente (sem série)"}
  formato_bruto: "CSV (e JSON) `V_AERODROMO_PUBLICO_DADOS_PATIO`, separador ponto e vírgula"
  lake: {estado: convertido, particoes: [], chave: [], colunas: 5}
  dados_pessoais: nenhum
  eras: []
  revisado_em: 2026-11-15
  versao_fetcher: 0.9.0
---

# Aeródromos públicos: pátios de estacionamento

## Resumo

Pátios de estacionamento de aeronaves em aeródromos públicos, com identificação, pavimento e resistência. Por ser um conjunto sem série, a cobertura registra a data da coleta.

## Ficha técnica

<!-- gerado:ficha -->

| Campo | Valor |
|---|---|
| Dataset | `anac/aero-patio` |
| Órgão | Agência Nacional de Aviação Civil (ANAC) |
| Página oficial | https://www.anac.gov.br/acesso-a-informacao/dados-abertos/areas-de-atuacao/aerodromos/aerodromos-publicos-patios-de-estacionamento |
| Licença | Não informada pela fonte: as páginas de metadados da ANAC não trazem licença (conferido em 2026-11-15). |
| Periodicidade | semanal |
| Cobertura | 2026-11 a em-curso |
| Unidade (uma linha) | um pátio de aeronaves de um aeródromo |
| Granularidade | espacial: Brasil (aeródromo); temporal: cadastro vigente (sem série) |
| Formato bruto | CSV (e JSON) `V_AERODROMO_PUBLICO_DADOS_PATIO`, separador ponto e vírgula |
| Estado no lake | convertido |
| Partições | — |
| Chave | — |
| Colunas | 5 |
| Unidades de medida | — |
| Dados pessoais | nenhum |
| Eras | nenhuma |
| Revisado em | 2026-11-15 |
| Versão do fetcher | 0.9.0 |

## Origem e coleta

- O fetcher baixa o arquivo estático do diretório `Aerodromos/` do servidor de dados abertos da ANAC; o servidor sobrescreve o arquivo a cada atualização, sem versões anteriores.
- Conferido em 2026-11-15: 1.083 linhas e 5 colunas.

## Conteúdo

- Amostra local de 1.083 linhas em 1 arquivo(s) Parquet, convertida em 2026-11-15 com o fetcher 0.9.0; a amostra não cobre toda a série publicada.

## Variáveis

As descrições vêm da página de metadados do conjunto no portal da ANAC (4 de 5 colunas); as demais ficam como "Sem descrição oficial".

| Coluna no lake | Na fonte | Tipo | Descrição | Unidade / códigos | Período |
|---|---|---|---|---|---|
| `CIAD` | `CIAD` | texto | O CIAD (Código de Identificação do Aeródromo), que é definido pela Agência no caso dos aeródromos civis, é um código formado pela junção dos dois caracteres referentes à unidade da federação onde o aeródromo se localiza e um número sequencial de 4 dígitos (formato UF0000). | — | todo |
| `NMAERODROMO` | `NMAERODROMO` | texto | Sem descrição oficial. | — | todo |
| `IDENTIFICACAO` | `IDENTIFICACAO` | texto | Designação do Pátio de Aeronaves. | — | todo |
| `SUPERFICIEPAVIMENTO` | `SUPERFICIEPAVIMENTO` | texto | Natureza ou tipo da superfície do pátio de aeronaves. | — | todo |
| `RESISTENCIAVALOR` | `RESISTENCIAVALOR` | texto | Valor da resistência, notificada pelo peso máximo(Kg)/pressão dos pneus (MPa), ou pelo PCN (código que utiliza, nesta ordem, os seguintes elementos: Valor numérico do PCN / tipo de pavimento / resistência do subleito / pressão de pneus / método de determinação) | — | todo |

## No lake

- Dataset `anac/aero-patio`, sem partições; um Parquet por arquivo de origem (1 na amostra).
- O conversor escolhe um arquivo por conteúdo (CSV antes de JSON antes de XLS, salvo grupos que preferem JSON) e lê todas as colunas como texto, exceto onde o JSON traz números.
- Colunas que repetem a partição (`ano`, `mes`) saem do Parquet; o valor fica no caminho.

## Cuidados de uso

- **Texto.** Coordenadas, altitude, comprimentos e datas chegam como texto, em formatos mistos (por exemplo, coordenadas decimais com vírgula).
- **Cadastro vigente.** O arquivo é a fotografia atual do cadastro; o lake guarda só a conversão mais recente.

## Exemplos

Contagem de linhas e de valores distintos de `CIAD`:

```python
import duckdb

duckdb.sql("""
    SELECT count(*) AS linhas, count(DISTINCT CIAD) AS distintos
    FROM read_parquet('lake/anac/aero-patio/*.parquet', union_by_name = true)
""").show()
```

## Referências

- Página do conjunto de dados: https://www.anac.gov.br/acesso-a-informacao/dados-abertos/areas-de-atuacao/aerodromos/aerodromos-publicos-patios-de-estacionamento
- Servidor de dados abertos da ANAC: https://sistemas.anac.gov.br/dadosabertos/
