---
dataset:
  id: drones
  fonte: anac
  titulo: "Drones cadastrados (SISANT), histórico mensal"
  resumo: "Fotografias mensais do cadastro de aeronaves não tripuladas do SISANT, com código, validade, operador, fabricante, modelo, peso e ramo de atividade."
  orgao: Agência Nacional de Aviação Civil (ANAC)
  pagina_oficial: https://www.anac.gov.br/acesso-a-informacao/dados-abertos/areas-de-atuacao/aeronaves/drones-cadastrados
  licenca: "Não informada pela fonte: as páginas de metadados da ANAC não trazem licença (conferido em 2026-11-15)."
  periodicidade: "diária (arquivo vigente); histórico mensal"
  cobertura: {inicio: "2022-08", fim: "em-curso"}
  unidade: "um drone cadastrado, na fotografia de um mês"
  granularidade: {espacial: "Brasil (aeronave não tripulada)", temporal: "mês"}
  formato_bruto: "CSV (e JSON) `SISANT_<MM><AAAA>` mensal e `SISANT.csv` vigente, separador ponto e vírgula, aspas duplas em todos os campos, primeira linha \"Atualizado em: AAAA-MM-DD\""
  lake: {estado: convertido, particoes: [ano, mes], chave: [], colunas: 10}
  dados_pessoais: 
    - {coluna: OPERADOR, categoria: "nome da pessoa física ou razão social"}
    - {coluna: CPF_CNPJ, categoria: "CPF (mascarado em parte) ou CNPJ"}
  eras: []
  revisado_em: 2026-11-15
  versao_fetcher: 0.9.0
---

# Drones cadastrados (SISANT), histórico mensal

## Resumo

Fotografias mensais do cadastro de aeronaves não tripuladas do SISANT, com código, validade, operador, fabricante, modelo, peso e ramo de atividade.

## Ficha técnica

<!-- gerado:ficha -->

| Campo | Valor |
|---|---|
| Dataset | `anac/drones` |
| Órgão | Agência Nacional de Aviação Civil (ANAC) |
| Página oficial | https://www.anac.gov.br/acesso-a-informacao/dados-abertos/areas-de-atuacao/aeronaves/drones-cadastrados |
| Licença | Não informada pela fonte: as páginas de metadados da ANAC não trazem licença (conferido em 2026-11-15). |
| Periodicidade | diária (arquivo vigente); histórico mensal |
| Cobertura | 2022-08 a em-curso |
| Unidade (uma linha) | um drone cadastrado, na fotografia de um mês |
| Granularidade | espacial: Brasil (aeronave não tripulada); temporal: mês |
| Formato bruto | CSV (e JSON) `SISANT_<MM><AAAA>` mensal e `SISANT.csv` vigente, separador ponto e vírgula, aspas duplas em todos os campos, primeira linha "Atualizado em: AAAA-MM-DD" |
| Estado no lake | convertido |
| Partições | `ano`, `mes` |
| Chave | — |
| Colunas | 10 |
| Unidades de medida | — |
| Dados pessoais | `OPERADOR` (nome da pessoa física ou razão social); `CPF_CNPJ` (CPF (mascarado em parte) ou CNPJ) |
| Eras | nenhuma |
| Revisado em | 2026-11-15 |
| Versão do fetcher | 0.9.0 |

## Origem e coleta

- O fetcher baixa o histórico `Aeronaves/drones cadastrados/Historico/SISANT_<MM><AAAA>.csv` (2022-08 em diante) e o cadastro vigente `SISANT.csv`.
- O histórico mensal grava no dataset `drones` (partições `ano` e `mes`); o cadastro vigente, sem período, grava em `drones-atual`, que o conversor não declara em `datasets()` (mesmas 10 colunas).
- Os arquivos começam com uma linha de preâmbulo "Atualizado em: AAAA-MM-DD" antes do cabeçalho; o conversor a descarta.
- Conferido em 2026-11-15: 2022-08 e 2024-10 (histórico) e o cadastro vigente (193.458 linhas) têm as mesmas 10 colunas.
- Os dados vêm do SISANT, onde se cadastram as aeronaves não tripuladas de uso recreativo (aeromodelos) e não recreativo, conforme o RBAC-E 94.

## Conteúdo

- Amostra local de 261.480 linhas em 2 arquivo(s) Parquet, convertida em 2026-11-15 com o fetcher 0.9.0; a amostra não cobre toda a série publicada.
- Amostras do histórico: 2022-08 (CSV com 100.456 registros) e 2024-10 (169.556); o cadastro vigente em 2026-11-15 tinha 193.458 registros.
- `TIPO_USO` vale `Básico` ou `Avançado`; `CPF_CNPJ` vem com prefixo `CPF:` ou `CNPJ:` e, em parte dos registros, com o CPF mascarado.

## Variáveis

As descrições vêm da página de metadados do conjunto no portal da ANAC (10 de 10 colunas); as demais ficam como "Sem descrição oficial".

| Coluna no lake | Na fonte | Tipo | Descrição | Unidade / códigos | Período |
|---|---|---|---|---|---|
| `CODIGO_AERONAVE` | `CODIGO_AERONAVE` | texto | Código da aeronave: `PR-` + 9 dígitos para uso recreativo (aeromodelo), `PP-` para uso não recreativo básico (RPA classe 3 em linha de visada abaixo de 400 pés) e `PS-` para uso avançado (RPA classe 2 e demais classe 3). | — | todo |
| `DATA_VALIDADE` | `DATA_VALIDADE` | texto | Data de validade do cadastro, igual à data do cadastro ou da renovação mais 2 anos. | — | todo |
| `OPERADOR` | `OPERADOR` | texto | Nome do responsável pela operação do drone. | — | todo |
| `CPF_CNPJ` | `CPF_CNPJ` | texto | Número do CPF ou do CNPJ do responsável pela operação do drone (mascarado em parte dos registros). | — | todo |
| `TIPO_USO` | `TIPO_USO` | texto | Básico: aeromodelos ou RPA classe 3 operada exclusivamente na linha de visada visual abaixo de 400 pés AGL. Avançado: RPA classe 2 ou demais RPA classe 3. | valores nas amostras: `Avançado`, `Básico`, `CPF: ****903.256***` | todo |
| `FABRICANTE` | `FABRICANTE` | texto | Nome do fabricante da aeronave. | — | todo |
| `MODELO` | `MODELO` | texto | Nome do modelo da aeronave. | — | todo |
| `NUMERO_SERIE` | `NUMERO_SERIE` | texto | Número de série da aeronave. | — | todo |
| `PESO_MAXIMO_DECOLAGEM_KG` | `PESO_MAXIMO_DECOLAGEM_KG` | texto | Peso máximo de decolagem, numérico com 2 casas decimais, em kg. | — | todo |
| `RAMO_ATIVIDADE` | `RAMO_ATIVIDADE` | texto | Recreativo (aeromodelos), Experimental (avançada, só para operações experimentais) ou outros ramos declarados pelo cadastrante. | — | todo |
| `ano` | — (partição) | texto | Partição do lake: ano do arquivo de origem, tirado do nome do arquivo. | — | todo |
| `mes` | — (partição) | texto | Partição do lake: mês do arquivo de origem, tirado do nome do arquivo. | — | todo |

## No lake

- Dataset `anac/drones`, particionado por `ano`, `mes`; um Parquet por arquivo de origem.
- O conversor escolhe um arquivo por conteúdo (CSV antes de JSON antes de XLS, salvo grupos que preferem JSON) e lê todas as colunas como texto, exceto onde o JSON traz números.
- Colunas que repetem a partição (`ano`, `mes`) saem do Parquet; o valor fica no caminho.

## Cuidados de uso

- **Dados pessoais.** `OPERADOR` e `CPF_CNPJ` identificam pessoas físicas (o CPF vem mascarado em parte dos registros); trate como dado pessoal.
- **Texto.** Datas (`dd/mm/aaaa`) e peso chegam como texto.

## Exemplos

Linhas por mês de partição:

```python
import duckdb

duckdb.sql("""
    SELECT ano, mes, count(*) AS linhas
    FROM read_parquet('lake/anac/drones/**/*.parquet', hive_partitioning = true, union_by_name = true)
    GROUP BY ALL ORDER BY ano, mes
""").show()
```

## Referências

- Página do conjunto de dados: https://www.anac.gov.br/acesso-a-informacao/dados-abertos/areas-de-atuacao/aeronaves/drones-cadastrados
- Servidor de dados abertos da ANAC: https://sistemas.anac.gov.br/dadosabertos/
