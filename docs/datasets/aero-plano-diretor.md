---
dataset:
  id: aero-plano-diretor
  fonte: anac
  titulo: "Planos diretores aeroportuários"
  resumo: "Aeródromos com plano diretor aeroportuário aprovado ou validado pela ANAC, com a portaria e o link."
  orgao: Agência Nacional de Aviação Civil (ANAC)
  pagina_oficial: https://www.anac.gov.br/acesso-a-informacao/dados-abertos/areas-de-atuacao/aerodromos
  licenca: "Não informada pela fonte: as páginas de metadados da ANAC não trazem licença (conferido em 2026-11-15)."
  periodicidade: "não informada"
  cobertura: {inicio: "2026-11", fim: "em-curso"}
  unidade: "um aeródromo com plano diretor aprovado ou validado"
  granularidade: {espacial: "Brasil (aeródromo)", temporal: "cadastro vigente (sem série)"}
  formato_bruto: "dois CSVs (e JSONs), `Plano Diretor Aeroportuario Aprovados` e `Plano Diretor Aeroportuario Validados`, separador ponto e vírgula"
  lake: {estado: convertido, particoes: [], chave: [CIAD], colunas: 7}
  dados_pessoais: nenhum
  eras: []
  revisado_em: 2026-11-15
  versao_fetcher: 0.9.0
---

# Planos diretores aeroportuários

## Resumo

Aeródromos com plano diretor aeroportuário aprovado ou validado pela ANAC, com a portaria e o link. Por ser um conjunto sem série, a cobertura registra a data da coleta.

## Ficha técnica

<!-- gerado:ficha -->

| Campo | Valor |
|---|---|
| Dataset | `anac/aero-plano-diretor` |
| Órgão | Agência Nacional de Aviação Civil (ANAC) |
| Página oficial | https://www.anac.gov.br/acesso-a-informacao/dados-abertos/areas-de-atuacao/aerodromos |
| Licença | Não informada pela fonte: as páginas de metadados da ANAC não trazem licença (conferido em 2026-11-15). |
| Periodicidade | não informada |
| Cobertura | 2026-11 a em-curso |
| Unidade (uma linha) | um aeródromo com plano diretor aprovado ou validado |
| Granularidade | espacial: Brasil (aeródromo); temporal: cadastro vigente (sem série) |
| Formato bruto | dois CSVs (e JSONs), `Plano Diretor Aeroportuario Aprovados` e `Plano Diretor Aeroportuario Validados`, separador ponto e vírgula |
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
- Conferido em 2026-11-15: aprovados com 92 linhas e 7 colunas, validados com 35 linhas e 5 colunas; os dois arquivos vão para o mesmo dataset.

## Conteúdo

- Amostra local de 127 linhas em 2 arquivo(s) Parquet, convertida em 2026-11-15 com o fetcher 0.9.0; a amostra não cobre toda a série publicada.

## Variáveis

A ANAC não publica página de metadados nem dicionário para este arquivo; as colunas ficam como "Sem descrição oficial".

| Coluna no lake | Na fonte | Tipo | Descrição | Unidade / códigos | Período |
|---|---|---|---|---|---|
| `CIAD` | `CIAD` | texto | Sem descrição oficial. | — | todo |
| `OACI` | `OACI` | texto | Sem descrição oficial. | — | todo |
| `AERODROMO` | `AERODROMO` | texto | Sem descrição oficial. | — | todo |
| `MUNICIPIO` | `MUNICIPIO` | texto | Sem descrição oficial. | — | todo |
| `UF` | `UF` | texto | Sem descrição oficial. | — | todo |
| `LINK` | `LINK` | texto | Sem descrição oficial. | — | todo |
| `PORTARIA` | `PORTARIA` | texto | Sem descrição oficial. | — | todo |

## No lake

- Dataset `anac/aero-plano-diretor`, sem partições; um Parquet por arquivo de origem (2 na amostra).
- O conversor escolhe um arquivo por conteúdo (CSV antes de JSON antes de XLS, salvo grupos que preferem JSON) e lê todas as colunas como texto, exceto onde o JSON traz números.
- Colunas que repetem a partição (`ano`, `mes`) saem do Parquet; o valor fica no caminho.

## Cuidados de uso

- **Texto.** Coordenadas, altitude, comprimentos e datas chegam como texto, em formatos mistos (por exemplo, coordenadas decimais com vírgula).
- **Cadastro vigente.** O arquivo é a fotografia atual do cadastro; o lake guarda só a conversão mais recente.
- **Duas tabelas em um dataset.** `LINK` e `PORTARIA` só existem no arquivo de aprovados.

## Exemplos

Contagem de linhas e de valores distintos de `CIAD`:

```python
import duckdb

duckdb.sql("""
    SELECT count(*) AS linhas, count(DISTINCT CIAD) AS distintos
    FROM read_parquet('lake/anac/aero-plano-diretor/*.parquet', union_by_name = true)
""").show()
```

## Referências

- Página do conjunto de dados: https://www.anac.gov.br/acesso-a-informacao/dados-abertos/areas-de-atuacao/aerodromos
- Servidor de dados abertos da ANAC: https://sistemas.anac.gov.br/dadosabertos/
