---
dataset:
  id: ocorrencias
  fonte: anac
  titulo: "Ocorrências aeronáuticas (CENIPA)"
  resumo: "Ocorrências aeronáuticas (acidentes e incidentes graves) enviadas pelo CENIPA à ANAC, com local, aeronave, operador, tipo, fase da operação, danos e lesões."
  orgao: Agência Nacional de Aviação Civil (ANAC)
  pagina_oficial: https://www.anac.gov.br/acesso-a-informacao/dados-abertos/areas-de-atuacao/seguranca-operacional/ocorrencias-aeronauticas
  licenca: "Não informada pela fonte: as páginas de metadados da ANAC não trazem licença (conferido em 2026-11-15)."
  periodicidade: "diária"
  cobertura: {inicio: "1959-01", fim: "em-curso"}
  unidade: "uma aeronave envolvida em uma ocorrência aeronáutica (o número da ocorrência se repete)"
  granularidade: {espacial: "local da ocorrência (município, UF, coordenadas)", temporal: "data da ocorrência"}
  formato_bruto: "CSV (e JSON) único `V_OCORRENCIA_AMPLA`, separador ponto e vírgula, atualizado diariamente"
  lake: {estado: convertido, particoes: [], chave: [], colunas: 45}
  dados_pessoais: nenhum
  eras: []
  revisado_em: 2026-11-15
  versao_fetcher: 0.9.0
---

# Ocorrências aeronáuticas (CENIPA)

## Resumo

Ocorrências aeronáuticas (acidentes e incidentes graves) enviadas pelo CENIPA à ANAC, com local, aeronave, operador, tipo, fase da operação, danos e lesões.

## Ficha técnica

<!-- gerado:ficha -->

| Campo | Valor |
|---|---|
| Dataset | `anac/ocorrencias` |
| Órgão | Agência Nacional de Aviação Civil (ANAC) |
| Página oficial | https://www.anac.gov.br/acesso-a-informacao/dados-abertos/areas-de-atuacao/seguranca-operacional/ocorrencias-aeronauticas |
| Licença | Não informada pela fonte: as páginas de metadados da ANAC não trazem licença (conferido em 2026-11-15). |
| Periodicidade | diária |
| Cobertura | 1959-01 a em-curso |
| Unidade (uma linha) | uma aeronave envolvida em uma ocorrência aeronáutica (o número da ocorrência se repete) |
| Granularidade | espacial: local da ocorrência (município, UF, coordenadas); temporal: data da ocorrência |
| Formato bruto | CSV (e JSON) único `V_OCORRENCIA_AMPLA`, separador ponto e vírgula, atualizado diariamente |
| Estado no lake | convertido |
| Partições | — |
| Chave | — |
| Colunas | 45 |
| Unidades de medida | — |
| Dados pessoais | nenhum |
| Eras | nenhuma |
| Revisado em | 2026-11-15 |
| Versão do fetcher | 0.9.0 |

## Origem e coleta

- O fetcher baixa `Seguranca Operacional/Ocorrencia/V_OCORRENCIA_AMPLA.csv` (e o JSON); a ANAC sobrescreve o arquivo a cada atualização.
- Conferido em 2026-11-15: 5.021 linhas e 45 colunas, de 1959-01-11 a 2024-06-22 em `Data_da_Ocorrencia`.
- A fonte descreve o conjunto como as ocorrências enviadas pela Força Aérea Brasileira, por meio do CENIPA, acrescidas de informações enriquecidas pela ANAC.

## Conteúdo

- Amostra local de 5.021 linhas em 1 arquivo(s) Parquet, convertida em 2026-11-15 com o fetcher 0.9.0; a amostra não cobre toda a série publicada.
- `Classificacao_da_Ocorrencia` vale `Acidente` (3.704) ou `Incidente Grave` (1.317).
- `Data_da_Ocorrencia` e `Hora_da_Ocorrencia` estão em UTC, segundo a fonte.
- 5.021 linhas para 4.301 números de ocorrência distintos (3.291 fichas): o mesmo número de ocorrência aparece em mais de uma linha, e há linhas repetidas por inteiro; `Numero_da_Ocorrencia` não é chave.
- As colunas de lesões (fatais, graves, leves, ilesos, desconhecidas, por tripulantes, passageiros e terceiros) são contagens, guardadas como texto.

## Variáveis

As descrições vêm da página de metadados do conjunto no portal da ANAC (45 de 45 colunas); as demais ficam como "Sem descrição oficial".

| Coluna no lake | Na fonte | Tipo | Descrição | Unidade / códigos | Período |
|---|---|---|---|---|---|
| `Numero_da_Ocorrencia` | `Numero_da_Ocorrencia` | texto | Número da Ocorrência Aeronáutica | — | todo |
| `Numero_da_Ficha` | `Numero_da_Ficha` | texto | Número da ficha cadastrada pelo CENIPA para a ocorrência. | — | todo |
| `Operador_Padronizado` | `Operador_Padronizado` | texto | Nome do operador/empresa, padronizado pelo sistema, responsável pela aeronave na época da ocorrência. | — | todo |
| `Classificacao_da_Ocorrencia` | `Classificacao_da_Ocorrencia` | texto | Classificação da Ocorrência Aeronáutica | valores nas amostras: `Acidente`, `Incidente Grave` | todo |
| `Data_da_Ocorrencia` | `Data_da_Ocorrencia` | texto | Data (UTC) da Ocorrência Aeronáutica | — | todo |
| `Hora_da_Ocorrencia` | `Hora_da_Ocorrencia` | texto | Hora (UTC) da Ocorrência Aeronáutica | — | todo |
| `Municipio` | `Municipio` | texto | Município do local da Ocorrência, quando aplicável | — | todo |
| `UF` | `UF` | texto | UF do local da Ocorrência, quando aplicável | — | todo |
| `Regiao` | `Regiao` | texto | Região do País relacionada ao campo UF. | valores nas amostras: `Centro-Oeste`, `Nordeste`, `Norte`, `Sudeste`, `Sul`, `null` | todo |
| `Descricao_do_Tipo` | `Descricao_do_Tipo` | texto | Descrição do tipo da ocorrência (campo `Descrição Tipo` da documentação) | — | todo |
| `ICAO` | `ICAO` | texto | Código ICAO do aeródromo onde houve a ocorrência. | — | todo |
| `Latitude` | `Latitude` | texto | Latitude do local onde houve a ocorrência | — | todo |
| `Longitude` | `Longitude` | texto | Longitude do local onde houve a ocorrência | — | todo |
| `Tipo_de_Aerodromo` | `Tipo_de_Aerodromo` | texto | Tipo de Aeródromo em que houve a ocorrência, quando aplicável. | valores nas amostras: `APUA`, `Aeródromo Militar`, `Privado`, `Público`, `null` | todo |
| `Historico` | `Historico` | texto | Descrição sobre a ocorrência | — | todo |
| `Matricula` | `Matricula` | texto | Matrícula da Aeronave associada à Ocorrência Aeronáutica | — | todo |
| `Categoria_da_Aeronave` | `Categoria_da_Aeronave` | texto | Categoria da Aeronave associada à Ocorrência Aeronáutica | — | todo |
| `Operador` | `Operador` | texto | Operador da Aeronave associada à Ocorrência Aeronáutica | — | todo |
| `Tipo_de_Ocorrencia` | `Tipo_de_Ocorrencia` | texto | Tipo de Ocorrência de acordo com a taxonomia ADREP | — | todo |
| `Fase_da_Operacao` | `Fase_da_Operacao` | texto | Fase da Operação da Aeronave quando da Ocorrência Aeronáutica | — | todo |
| `Operacao` | `Operacao` | texto | Tipo de Operação da Aeronave no momento da Ocorrência Aeronáutica | — | todo |
| `Danos_a_Aeronave` | `Danos_a_Aeronave` | texto | Danos à Aeronave associada à Ocorrência Aeronáutica | valores nas amostras: `Desconhecida`, `Destruída`, `Leve`, `Nenhum`, `Substancial`, `null` | todo |
| `Aerodromo_de_Destino` | `Aerodromo_de_Destino` | texto | Indicador de Localidade ICAO do Aeródromo de Destino da Aeronave associada à Ocorrência Aeronáutica | — | todo |
| `Aerodromo_de_Origem` | `Aerodromo_de_Origem` | texto | Indicador de Localidade ICAO do Aeródromo de Origem da Aeronave associada à Ocorrência Aeronáutica | — | todo |
| `Lesoes_Fatais_Tripulantes` | `Lesoes_Fatais_Tripulantes` | texto | Número de Tripulantes com lesões fatais na Aeronave associada à Ocorrência Aeronáutica | valores nas amostras: `0`, `1`, `2`, `3`, `4`, `6`, `null` | todo |
| `Lesoes_Fatais_Passageiros` | `Lesoes_Fatais_Passageiros` | texto | Número de Passageiros com lesões fatais na Aeronave associada à Ocorrência Aeronáutica | — | todo |
| `Lesoes_Fatais_Terceiros` | `Lesoes_Fatais_Terceiros` | texto | Número de Terceiros com lesões fatais causadas pela Aeronave associada à Ocorrência Aeronáutica | valores nas amostras: `0`, `1`, `12`, `2`, `6`, `null` | todo |
| `Lesoes_Graves_Tripulantes` | `Lesoes_Graves_Tripulantes` | texto | Número de Tripulantes com lesões graves na Aeronave associada à Ocorrência Aeronáutica | valores nas amostras: `0`, `1`, `2`, `null` | todo |
| `Lesoes_Graves_Passageiros` | `Lesoes_Graves_Passageiros` | texto | Número de Passageiros com lesões graves na Aeronave associada à Ocorrência Aeronáutica | valores nas amostras: `0`, `1`, `2`, `3`, `4`, `6`, `null` | todo |
| `Lesoes_Graves_Terceiros` | `Lesoes_Graves_Terceiros` | texto | Número de Terceiros com lesões graves causadas pela Aeronave associada à Ocorrência Aeronáutica | valores nas amostras: `0`, `1`, `2`, `null` | todo |
| `Lesoes_Leves_Tripulantes` | `Lesoes_Leves_Tripulantes` | texto | Número de Tripulantes com lesões leves na Aeronave associada à Ocorrência Aeronáutica | valores nas amostras: `0`, `1`, `2`, `3`, `4`, `5`, `null` | todo |
| `Lesoes_Leves_Passageiros` | `Lesoes_Leves_Passageiros` | texto | Número de Passageiros com lesões leves na Aeronave associada à Ocorrência Aeronáutica | — | todo |
| `Lesoes_Leves_Terceiros` | `Lesoes_Leves_Terceiros` | texto | Número de Terceiros com lesões leves causadas pela Aeronave associada à Ocorrência Aeronáutica | valores nas amostras: `0`, `1`, `2`, `3`, `4`, `null` | todo |
| `Ilesos_Tripulantes` | `Ilesos_Tripulantes` | texto | Número de Tripulantes ilesos na Aeronave associada à Ocorrência Aeronáutica | — | todo |
| `Ilesos_Passageiros` | `Ilesos_Passageiros` | texto | Número de Passageiros ilesos na Aeronave associada à Ocorrência Aeronáutica | — | todo |
| `Lesoes_Desconhecidas_Tripulantes` | `Lesoes_Desconhecidas_Tripulantes` | texto | Número de Tripulantes com lesões desconhecida na Aeronave associada à Ocorrência Aeronáutica | valores nas amostras: `0`, `1`, `2`, `null` | todo |
| `Lesoes_Desconhecidas_Passageiros` | `Lesoes_Desconhecidas_Passageiros` | texto | Número de Passageiros com lesões desconhecida na Aeronave associada à Ocorrência Aeronáutica | valores nas amostras: `0`, `1`, `2`, `3`, `4`, `7`, `null` | todo |
| `Lesoes_Desconhecidas_Terceiros` | `Lesoes_Desconhecidas_Terceiros` | texto | Número de Terceiros com lesões desconhecida causadas pela Aeronave associada à Ocorrência Aeronáutica | valores nas amostras: `0`, `1`, `2`, `3`, `4`, `null` | todo |
| `Modelo` | `Modelo` | texto | Descrição do Modelo da Aeronave | — | todo |
| `CLS` | `CLS` | texto | Código que identifica o tipo da aeronave. | — | todo |
| `Tipo_ICAO` | `Tipo_ICAO` | texto | Código de identificação da aeronave segundo a ICAO. | — | todo |
| `PMD` | `PMD` | texto | Peso máximo de Decolagem da aeronave | — | todo |
| `Numero_de_Assentos` | `Numero_de_Assentos` | texto | Quantidade de assentos disponíveis na aeronave. | — | todo |
| `Nome_do_Fabricante` | `Nome_do_Fabricante` | texto | Nome da empresa fabricante da aeronave. | — | todo |
| `PSSO` | `PSSO` | texto | A ocorrência é considerada nos indicadores do Programa de Supervisão da Segurança Operacional (PSSO) | valores nas amostras: `falso`, `verdadeiro` | todo |

## No lake

- Dataset `anac/ocorrencias`, sem partições; um Parquet por arquivo de origem (1 na amostra).
- O conversor escolhe um arquivo por conteúdo (CSV antes de JSON antes de XLS, salvo grupos que preferem JSON) e lê todas as colunas como texto, exceto onde o JSON traz números.
- Colunas que repetem a partição (`ano`, `mes`) saem do Parquet; o valor fica no caminho.

## Cuidados de uso

- **Contagens como texto.** As colunas `Lesoes_*` e `Ilesos_*`, `PMD` e `Numero_de_Assentos` chegam como texto.
- **A fonte documenta campos que o arquivo não traz.** A página de metadados lista `CPF_CNPJ` do operador e `Ilícito`, que não existem nas 45 colunas do CSV conferido.

## Exemplos

Contagem de linhas e de valores distintos de `Numero_da_Ocorrencia`:

```python
import duckdb

duckdb.sql("""
    SELECT count(*) AS linhas, count(DISTINCT Numero_da_Ocorrencia) AS distintos
    FROM read_parquet('lake/anac/ocorrencias/*.parquet', union_by_name = true)
""").show()
```

## Referências

- Página do conjunto de dados: https://www.anac.gov.br/acesso-a-informacao/dados-abertos/areas-de-atuacao/seguranca-operacional/ocorrencias-aeronauticas
- Servidor de dados abertos da ANAC: https://sistemas.anac.gov.br/dadosabertos/
