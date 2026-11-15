---
dataset:
  id: aero-pzr
  fonte: anac
  titulo: "Planos de Zoneamento de Ruído registrados"
  resumo: "Lista de aeródromos com plano de zoneamento de ruído registrado, nas duas modalidades: básico (PBZR) e específico (PEZR)."
  orgao: Agência Nacional de Aviação Civil (ANAC)
  pagina_oficial: https://www.anac.gov.br/acesso-a-informacao/dados-abertos/areas-de-atuacao/aerodromos/lista-pzr
  licenca: "Não informada pela fonte: as páginas de metadados da ANAC não trazem licença (conferido em 2026-11-15)."
  periodicidade: "não informada"
  cobertura: {inicio: "2026-11", fim: "em-curso"}
  unidade: "um aeródromo com PZR registrado, em uma das duas modalidades"
  granularidade: {espacial: "Brasil (aeródromo)", temporal: "cadastro vigente (sem série)"}
  formato_bruto: "dois CSVs (e JSONs), `PZR_PBZR_Registrados` e `PZR_PEZR_Registrados`, separador ponto e vírgula"
  lake: {estado: convertido, particoes: [], chave: [CIAD], colunas: 7}
  dados_pessoais: nenhum
  eras: []
  revisado_em: 2026-11-15
  versao_fetcher: 0.9.0
---

# Planos de Zoneamento de Ruído registrados

## Resumo

Lista de aeródromos com plano de zoneamento de ruído registrado, nas duas modalidades: básico (PBZR) e específico (PEZR). Por ser um conjunto sem série, a cobertura registra a data da coleta.

## Ficha técnica

<!-- gerado:ficha -->

| Campo | Valor |
|---|---|
| Dataset | `anac/aero-pzr` |
| Órgão | Agência Nacional de Aviação Civil (ANAC) |
| Página oficial | https://www.anac.gov.br/acesso-a-informacao/dados-abertos/areas-de-atuacao/aerodromos/lista-pzr |
| Licença | Não informada pela fonte: as páginas de metadados da ANAC não trazem licença (conferido em 2026-11-15). |
| Periodicidade | não informada |
| Cobertura | 2026-11 a em-curso |
| Unidade (uma linha) | um aeródromo com PZR registrado, em uma das duas modalidades |
| Granularidade | espacial: Brasil (aeródromo); temporal: cadastro vigente (sem série) |
| Formato bruto | dois CSVs (e JSONs), `PZR_PBZR_Registrados` e `PZR_PEZR_Registrados`, separador ponto e vírgula |
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
- Conferido em 2026-11-15: PBZR com 404 linhas e 6 colunas, PEZR com 73 linhas e 6 colunas; os dois arquivos vão para o mesmo dataset (Parquet separado de cada um).

## Conteúdo

- Amostra local de 477 linhas em 2 arquivo(s) Parquet, convertida em 2026-11-15 com o fetcher 0.9.0; a amostra não cobre toda a série publicada.

## Variáveis

A ANAC não publica página de metadados nem dicionário para este arquivo; as colunas ficam como "Sem descrição oficial".

| Coluna no lake | Na fonte | Tipo | Descrição | Unidade / códigos | Período |
|---|---|---|---|---|---|
| `OACI` | `OACI` | texto | Sem descrição oficial. | — | todo |
| `CIAD` | `CIAD` | texto | Sem descrição oficial. | — | todo |
| `AERÓDROMO` | `AERÓDROMO` | texto | Sem descrição oficial. | — | todo |
| `MUNICÍPIO` | `MUNICÍPIO` | texto | Sem descrição oficial. | — | todo |
| `UF` | `UF` | texto | Sem descrição oficial. | — | todo |
| `CLASSE PBZR` | `CLASSE PBZR` | texto | Sem descrição oficial. | valores nas amostras: `1`, `2`, `3`, `4` | todo |
| `LINK` | `LINK` | texto | Sem descrição oficial. | — | todo |

## No lake

- Dataset `anac/aero-pzr`, sem partições; um Parquet por arquivo de origem (2 na amostra).
- O conversor escolhe um arquivo por conteúdo (CSV antes de JSON antes de XLS, salvo grupos que preferem JSON) e lê todas as colunas como texto, exceto onde o JSON traz números.
- Colunas que repetem a partição (`ano`, `mes`) saem do Parquet; o valor fica no caminho.

## Cuidados de uso

- **Texto.** Coordenadas, altitude, comprimentos e datas chegam como texto, em formatos mistos (por exemplo, coordenadas decimais com vírgula).
- **Cadastro vigente.** O arquivo é a fotografia atual do cadastro; o lake guarda só a conversão mais recente.
- **Duas tabelas em um dataset.** `CLASSE PBZR` só existe no arquivo PBZR e `LINK` só no PEZR; ao ler com `union_by_name`, as colunas ausentes ficam nulas.

## Exemplos

Contagem de linhas e de valores distintos de `OACI`:

```python
import duckdb

duckdb.sql("""
    SELECT count(*) AS linhas, count(DISTINCT OACI) AS distintos
    FROM read_parquet('lake/anac/aero-pzr/*.parquet', union_by_name = true)
""").show()
```

## Referências

- Página do conjunto de dados: https://www.anac.gov.br/acesso-a-informacao/dados-abertos/areas-de-atuacao/aerodromos/lista-pzr
- Servidor de dados abertos da ANAC: https://sistemas.anac.gov.br/dadosabertos/
