---
dataset:
  id: aero-helipontos-publicos
  fonte: anac
  titulo: "Aeródromos públicos: áreas de pouso e decolagem de helicópteros"
  resumo: "Áreas de pouso e decolagem de helicópteros de aeródromos públicos, com localização, pavimento, resistência e luzes."
  orgao: Agência Nacional de Aviação Civil (ANAC)
  pagina_oficial: https://www.anac.gov.br/acesso-a-informacao/dados-abertos/areas-de-atuacao/aerodromos
  licenca: "Não informada pela fonte: as páginas de metadados da ANAC não trazem licença (conferido em 2026-11-15)."
  periodicidade: "não informada"
  cobertura: {inicio: "2026-11", fim: "em-curso"}
  unidade: "um registro do cadastro de aeródromos vigente"
  granularidade: {espacial: "Brasil (aeródromo)", temporal: "cadastro vigente (sem série)"}
  formato_bruto: "CSV (e JSON) `Aerodromos Publicos Areas de Pouso e Decolagem de Helicopteros`, separador ponto e vírgula"
  lake: {estado: convertido, particoes: [], chave: [CIAD], colunas: 18}
  dados_pessoais: nenhum
  eras: []
  revisado_em: 2026-11-15
  versao_fetcher: 0.9.0
---

# Aeródromos públicos: áreas de pouso e decolagem de helicópteros

## Resumo

Áreas de pouso e decolagem de helicópteros de aeródromos públicos, com localização, pavimento, resistência e luzes. Por ser um conjunto sem série, a cobertura registra a data da coleta.

## Ficha técnica

<!-- gerado:ficha -->

| Campo | Valor |
|---|---|
| Dataset | `anac/aero-helipontos-publicos` |
| Órgão | Agência Nacional de Aviação Civil (ANAC) |
| Página oficial | https://www.anac.gov.br/acesso-a-informacao/dados-abertos/areas-de-atuacao/aerodromos |
| Licença | Não informada pela fonte: as páginas de metadados da ANAC não trazem licença (conferido em 2026-11-15). |
| Periodicidade | não informada |
| Cobertura | 2026-11 a em-curso |
| Unidade (uma linha) | um registro do cadastro de aeródromos vigente |
| Granularidade | espacial: Brasil (aeródromo); temporal: cadastro vigente (sem série) |
| Formato bruto | CSV (e JSON) `Aerodromos Publicos Areas de Pouso e Decolagem de Helicopteros`, separador ponto e vírgula |
| Estado no lake | convertido |
| Partições | — |
| Chave | `CIAD` |
| Colunas | 18 |
| Unidades de medida | — |
| Dados pessoais | nenhum |
| Eras | nenhuma |
| Revisado em | 2026-11-15 |
| Versão do fetcher | 0.9.0 |

## Origem e coleta

- O fetcher baixa o arquivo estático do diretório `Aerodromos/` do servidor de dados abertos da ANAC; o servidor sobrescreve o arquivo a cada atualização, sem versões anteriores.
- Conferido em 2026-11-15: 6 linhas e 18 colunas. A ANAC não publica página de metadados para este arquivo.

## Conteúdo

- Amostra local de 6 linhas em 1 arquivo(s) Parquet, convertida em 2026-11-15 com o fetcher 0.9.0; a amostra não cobre toda a série publicada.

## Variáveis

A ANAC não publica página de metadados nem dicionário para este arquivo; as colunas ficam como "Sem descrição oficial".

| Coluna no lake | Na fonte | Tipo | Descrição | Unidade / códigos | Período |
|---|---|---|---|---|---|
| `CIAD` | `CIAD` | texto | Sem descrição oficial. | valores nas amostras: `RJ0028`, `RJ0321`, `RS0046`, `RS0052`, `SP0007`, `SP0049` | todo |
| `IDENTIFICAÇÃO` | `IDENTIFICAÇÃO` | texto | Sem descrição oficial. | valores nas amostras: `Campo de Marte`, `Capão da Canoa`, `Farol de São Tomé`, `HELIO ALVES DE OLIVEIRA`, `Porto do Açu`, `Rio Claro` | todo |
| `LATITUDE` | `LATITUDE` | texto | Sem descrição oficial. | valores nas amostras: `21°48'05S;041°06'09W`, `22°01'50S;041°04'07W`, `22°25'54S;047°33'45W`, `23°30'33S;046°38'15W`, `29°43'11S;051°29'20W`, `29°45'49S;050°02'13W` | todo |
| `LONGITUDE` | `LONGITUDE` | texto | Sem descrição oficial. | valores nas amostras: `10.0`, `2.0`, `24.0`, `5.0`, `600.0`, `723.0` | todo |
| `ELEVAÇÃO` | `ELEVAÇÃO` | texto | Sem descrição oficial. | valores nas amostras: `No solo` | todo |
| `TIPO` | `TIPO` | texto | Sem descrição oficial. | valores nas amostras: `IFR / VFR`, `VFR` | todo |
| `OPERAÇÃO DIURNA` | `OPERAÇÃO DIURNA` | texto | Sem descrição oficial. | valores nas amostras: `IFR / VFR`, `Sem Operação`, `VFR` | todo |
| `OPERAÇÃO NOTURNA` | `OPERAÇÃO NOTURNA` | texto | Sem descrição oficial. | valores nas amostras: `Asfalto`, `Grama`, `Paralelepípedo` | todo |
| `SUPERFICIE PAVIMENTO` | `SUPERFICIE PAVIMENTO` | texto | Sem descrição oficial. | valores nas amostras: `15.00`, `3.00`, `4.00`, `4.50` | todo |
| `RESISTÊNCIA` | `RESISTÊNCIA` | texto | Sem descrição oficial. | valores nas amostras: `Quadrado`, `Retangular` | todo |
| `FATO - FORMATO` | `FATO - FORMATO` | texto | Sem descrição oficial. | valores nas amostras: `18 m`, `20 m`, `21 m`, `25 m`, `31.5 m x 380 m`, `31.5 m x 580 m` | todo |
| `FATO - DIMENSÕES` | `FATO - DIMENSÕES` | texto | Sem descrição oficial. | valores nas amostras: `Não`, `Sim` | todo |
| `LUZ DE APROXIMAÇÃO DE HELIPONTO` | `LUZ DE APROXIMAÇÃO DE HELIPONTO` | texto | Sem descrição oficial. | valores nas amostras: `Não`, `Sim` | todo |
| `LUZ DE TLOF` | `LUZ DE TLOF` | texto | Sem descrição oficial. | valores nas amostras: `Não` | todo |
| `INDICADOR VISUAL DE RAMPA DE APROXIMAÇÃO` | `INDICADOR VISUAL DE RAMPA DE APROXIMAÇÃO` | texto | Sem descrição oficial. | valores nas amostras: `Sim` | todo |
| `LUZ INDICADORA DE FATO` | `LUZ INDICADORA DE FATO` | texto | Sem descrição oficial. | valores nas amostras: `Não`, `Sim` | todo |
| `LUZ DE PONTO DE VISADA` | `LUZ DE PONTO DE VISADA` | texto | Sem descrição oficial. | valores nas amostras: `Não` | todo |
| `LUZ DE OBSTÁCULO` | `LUZ DE OBSTÁCULO` | texto | Sem descrição oficial. | — | todo |

## No lake

- Dataset `anac/aero-helipontos-publicos`, sem partições; um Parquet por arquivo de origem (1 na amostra).
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
    FROM read_parquet('lake/anac/aero-helipontos-publicos/*.parquet', union_by_name = true)
""").show()
```

## Referências

- Página do conjunto de dados: https://www.anac.gov.br/acesso-a-informacao/dados-abertos/areas-de-atuacao/aerodromos
- Servidor de dados abertos da ANAC: https://sistemas.anac.gov.br/dadosabertos/
