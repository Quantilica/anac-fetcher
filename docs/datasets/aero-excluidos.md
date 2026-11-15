---
dataset:
  id: aero-excluidos
  fonte: anac
  titulo: "Aeródromos públicos: excluídos"
  resumo: "Aeródromos públicos excluídos do cadastro, com a portaria de exclusão."
  orgao: Agência Nacional de Aviação Civil (ANAC)
  pagina_oficial: https://www.anac.gov.br/acesso-a-informacao/dados-abertos/areas-de-atuacao/aerodromos
  licenca: "Não informada pela fonte: as páginas de metadados da ANAC não trazem licença (conferido em 2026-11-15)."
  periodicidade: "não informada"
  cobertura: {inicio: "2026-11", fim: "em-curso"}
  unidade: "um registro do cadastro de aeródromos vigente"
  granularidade: {espacial: "Brasil (aeródromo)", temporal: "cadastro vigente (sem série)"}
  formato_bruto: "CSV (e JSON) `Aerodromos_Publicos_Excluidos`, separador ponto e vírgula"
  lake: {estado: convertido, particoes: [], chave: [CIAD], colunas: 7}
  dados_pessoais: nenhum
  eras: []
  revisado_em: 2026-11-15
  versao_fetcher: 0.9.0
---

# Aeródromos públicos: excluídos

## Resumo

Aeródromos públicos excluídos do cadastro, com a portaria de exclusão. Por ser um conjunto sem série, a cobertura registra a data da coleta.

## Ficha técnica

<!-- gerado:ficha -->

| Campo | Valor |
|---|---|
| Dataset | `anac/aero-excluidos` |
| Órgão | Agência Nacional de Aviação Civil (ANAC) |
| Página oficial | https://www.anac.gov.br/acesso-a-informacao/dados-abertos/areas-de-atuacao/aerodromos |
| Licença | Não informada pela fonte: as páginas de metadados da ANAC não trazem licença (conferido em 2026-11-15). |
| Periodicidade | não informada |
| Cobertura | 2026-11 a em-curso |
| Unidade (uma linha) | um registro do cadastro de aeródromos vigente |
| Granularidade | espacial: Brasil (aeródromo); temporal: cadastro vigente (sem série) |
| Formato bruto | CSV (e JSON) `Aerodromos_Publicos_Excluidos`, separador ponto e vírgula |
| Estado no lake | convertido |
| Partições | — |
| Chave | `CIAD` |
| Colunas | 7 |
| Unidades de medida | — |
| Dados pessoais | nenhum |
| Eras | nenhuma |
| Revisado em | 2026-11-15 |
| Versão do fetcher | 0.9.0 |

## Origem e coleta

- O fetcher baixa o arquivo estático do diretório `Aerodromos/` do servidor de dados abertos da ANAC; o servidor sobrescreve o arquivo a cada atualização, sem versões anteriores.
- Conferido em 2026-11-15: 64 linhas e 7 colunas. A ANAC não publica página de metadados para este arquivo.

## Conteúdo

- Amostra local de 64 linhas em 1 arquivo(s) Parquet, convertida em 2026-11-15 com o fetcher 0.9.0; a amostra não cobre toda a série publicada.

## Variáveis

A ANAC não publica página de metadados nem dicionário para este arquivo; as colunas ficam como "Sem descrição oficial".

| Coluna no lake | Na fonte | Tipo | Descrição | Unidade / códigos | Período |
|---|---|---|---|---|---|
| `CIAD` | `CIAD` | texto | Sem descrição oficial. | — | todo |
| `NOME` | `NOME` | texto | Sem descrição oficial. | — | todo |
| `UF` | `UF` | texto | Sem descrição oficial. | — | todo |
| `MUNICIPIO` | `MUNICIPIO` | texto | Sem descrição oficial. | — | todo |
| `LATITUDE` | `LATITUDE` | texto | Sem descrição oficial. | — | todo |
| `LONGITUDE` | `LONGITUDE` | texto | Sem descrição oficial. | — | todo |
| `PORTARIA DE EXCLUSAO` | `PORTARIA DE EXCLUSAO` | texto | Sem descrição oficial. | — | todo |

## No lake

- Dataset `anac/aero-excluidos`, sem partições; um Parquet por arquivo de origem (1 na amostra).
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
    FROM read_parquet('lake/anac/aero-excluidos/*.parquet', union_by_name = true)
""").show()
```

## Referências

- Página do conjunto de dados: https://www.anac.gov.br/acesso-a-informacao/dados-abertos/areas-de-atuacao/aerodromos
- Servidor de dados abertos da ANAC: https://sistemas.anac.gov.br/dadosabertos/
