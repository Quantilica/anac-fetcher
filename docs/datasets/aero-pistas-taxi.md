---
dataset:
  id: aero-pistas-taxi
  fonte: anac
  titulo: "Aeródromos públicos: pistas de táxi"
  resumo: "Pistas de táxi de aeródromos públicos, com dimensões, pavimento, resistência e cabeceiras de referência."
  orgao: Agência Nacional de Aviação Civil (ANAC)
  pagina_oficial: https://www.anac.gov.br/acesso-a-informacao/dados-abertos/areas-de-atuacao/aerodromos/aerodromos-publicos-pistas-de-taxi
  licenca: "Não informada pela fonte: as páginas de metadados da ANAC não trazem licença (conferido em 2026-11-15)."
  periodicidade: "quinzenal"
  cobertura: {inicio: "2026-11", fim: "em-curso"}
  unidade: "uma pista de táxi de um aeródromo"
  granularidade: {espacial: "Brasil (aeródromo)", temporal: "cadastro vigente (sem série)"}
  formato_bruto: "CSV `pda_aerodromos_publicos_pistas_de_taxi`, separador ponto e vírgula"
  lake: {estado: convertido, particoes: [], chave: [], colunas: 14}
  dados_pessoais: nenhum
  eras: []
  revisado_em: 2026-11-15
  versao_fetcher: 0.9.0
---

# Aeródromos públicos: pistas de táxi

## Resumo

Pistas de táxi de aeródromos públicos, com dimensões, pavimento, resistência e cabeceiras de referência. Por ser um conjunto sem série, a cobertura registra a data da coleta.

## Ficha técnica

<!-- gerado:ficha -->

| Campo | Valor |
|---|---|
| Dataset | `anac/aero-pistas-taxi` |
| Órgão | Agência Nacional de Aviação Civil (ANAC) |
| Página oficial | https://www.anac.gov.br/acesso-a-informacao/dados-abertos/areas-de-atuacao/aerodromos/aerodromos-publicos-pistas-de-taxi |
| Licença | Não informada pela fonte: as páginas de metadados da ANAC não trazem licença (conferido em 2026-11-15). |
| Periodicidade | quinzenal |
| Cobertura | 2026-11 a em-curso |
| Unidade (uma linha) | uma pista de táxi de um aeródromo |
| Granularidade | espacial: Brasil (aeródromo); temporal: cadastro vigente (sem série) |
| Formato bruto | CSV `pda_aerodromos_publicos_pistas_de_taxi`, separador ponto e vírgula |
| Estado no lake | convertido |
| Partições | — |
| Chave | — |
| Colunas | 14 |
| Unidades de medida | — |
| Dados pessoais | nenhum |
| Eras | nenhuma |
| Revisado em | 2026-11-15 |
| Versão do fetcher | 0.9.0 |

## Origem e coleta

- O fetcher baixa o arquivo estático do diretório `Aerodromos/` do servidor de dados abertos da ANAC; o servidor sobrescreve o arquivo a cada atualização, sem versões anteriores.
- Conferido em 2026-11-15: 3.862 linhas e 14 colunas.

## Conteúdo

- Amostra local de 3.862 linhas em 1 arquivo(s) Parquet, convertida em 2026-11-15 com o fetcher 0.9.0; a amostra não cobre toda a série publicada.

## Variáveis

As descrições vêm da página de metadados do conjunto no portal da ANAC (6 de 14 colunas); as demais ficam como "Sem descrição oficial".

| Coluna no lake | Na fonte | Tipo | Descrição | Unidade / códigos | Período |
|---|---|---|---|---|---|
| `ID_AERODROMO` | `ID_AERODROMO` | texto | Sem descrição oficial. | — | todo |
| `ID_PISTA` | `ID_PISTA` | texto | Sem descrição oficial. | — | todo |
| `NM_PISTA` | `NM_PISTA` | texto | Denominação da pista de táxi. (campo `IDENTIFICAÇÃO` da documentação) | — | todo |
| `QT_COMPRIMENTO` | `QT_COMPRIMENTO` | texto | Comprimento da pista de táxi. Dado apresentado em metros. (campo `COMPRIMENTO` da documentação) | — | todo |
| `QT_LARGURA` | `QT_LARGURA` | texto | Largura da pista de táxi. Dado apresentado em metros. (campo `LARGURA` da documentação) | — | todo |
| `DS_RESISTENCIA` | `DS_RESISTENCIA` | texto | Sem descrição oficial. | — | todo |
| `NM_PAVIMENTO_TIPO` | `NM_PAVIMENTO_TIPO` | texto | Tipo de material da superfície da pista de táxi. (campo `SUPERFICIE PAVIMENTO` da documentação) | — | todo |
| `CODIGO_REFERENCIA` | `CODIGO_REFERENCIA` | texto | Sem descrição oficial. | valores nas amostras: `2B`, `2C`, `3C`, `4C`, `4D`, `4E`, `Asfalto` | todo |
| `ID_PISTA_CABECEIRA_MENOR` | `ID_PISTA_CABECEIRA_MENOR` | texto | Sem descrição oficial. | — | todo |
| `CAB_MENOR_REGRA_VOO` | `CAB_MENOR_REGRA_VOO` | texto | Sem descrição oficial. | — | todo |
| `ID_PISTA_CABECEIRA_MAIOR` | `ID_PISTA_CABECEIRA_MAIOR` | texto | Sem descrição oficial. | — | todo |
| `CAB_MAIOR_REGRA_VOO` | `CAB_MAIOR_REGRA_VOO` | texto | Sem descrição oficial. | — | todo |
| `FG_LUZ_EIXO_PISTA` | `FG_LUZ_EIXO_PISTA` | texto | Sinalização luminosa na cor verde situada ao longo do eixo da pista de táxi. (campo `LUZ DE EIXO DE PISTA DE TAXI` da documentação) | valores nas amostras: `0`, `1`, `31 - Visual`, `32 - Visual` | todo |
| `FG_LUZ_BORDA_PISTA` | `FG_LUZ_BORDA_PISTA` | texto | Sinalização luminosa na cor azul localizada ao longo da borda da pista de táxi. (campo `LUZ DE BORDA DE PISTA DE TAXI` da documentação) | valores nas amostras: `0`, `1` | todo |

## No lake

- Dataset `anac/aero-pistas-taxi`, sem partições; um Parquet por arquivo de origem (1 na amostra).
- O conversor escolhe um arquivo por conteúdo (CSV antes de JSON antes de XLS, salvo grupos que preferem JSON) e lê todas as colunas como texto, exceto onde o JSON traz números.
- Colunas que repetem a partição (`ano`, `mes`) saem do Parquet; o valor fica no caminho.

## Cuidados de uso

- **Texto.** Coordenadas, altitude, comprimentos e datas chegam como texto, em formatos mistos (por exemplo, coordenadas decimais com vírgula).
- **Cadastro vigente.** O arquivo é a fotografia atual do cadastro; o lake guarda só a conversão mais recente.

## Exemplos

Contagem de linhas e de valores distintos de `ID_AERODROMO`:

```python
import duckdb

duckdb.sql("""
    SELECT count(*) AS linhas, count(DISTINCT ID_AERODROMO) AS distintos
    FROM read_parquet('lake/anac/aero-pistas-taxi/*.parquet', union_by_name = true)
""").show()
```

## Referências

- Página do conjunto de dados: https://www.anac.gov.br/acesso-a-informacao/dados-abertos/areas-de-atuacao/aerodromos/aerodromos-publicos-pistas-de-taxi
- Servidor de dados abertos da ANAC: https://sistemas.anac.gov.br/dadosabertos/
