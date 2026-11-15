---
dataset:
  id: rab
  fonte: anac
  titulo: "Registro Aeronáutico Brasileiro (RAB), histórico mensal"
  resumo: "Fotografias mensais do cadastro de aeronaves do Registro Aeronáutico Brasileiro, com marca, proprietário, operador, modelo, fabricante, situação de aeronavegabilidade e cancelamento."
  orgao: Agência Nacional de Aviação Civil (ANAC)
  pagina_oficial: https://www.anac.gov.br/acesso-a-informacao/dados-abertos/areas-de-atuacao/aeronaves/registro-aeronautico-brasileiro
  licenca: "Não informada pela fonte: as páginas de metadados da ANAC não trazem licença (conferido em 2026-11-15)."
  periodicidade: "mensal"
  cobertura: {inicio: "2017-01", fim: "em-curso"}
  unidade: "uma aeronave matriculada, na fotografia de um mês"
  granularidade: {espacial: "Brasil (aeronave)", temporal: "mês"}
  formato_bruto: "um arquivo por mês `<AAAA-MM>` em CSV (desde 2024-09), JSON e XLS, separador ponto e vírgula; mais o cadastro vigente `dados_aeronaves`"
  lake: {estado: convertido, particoes: [ano, mes], chave: [], colunas: 66}
  dados_pessoais: 
    - {coluna: PROPRIETARIO, categoria: "nome ou razão social do proprietário"}
    - {coluna: OUTROSPROPRIETARIOS, categoria: "nomes dos demais proprietários"}
    - {coluna: OUTROS_PROPRIETARIOS, categoria: "nomes dos demais proprietários"}
    - {coluna: CPFCNPJ, categoria: "CPF ou CNPJ do proprietário"}
    - {coluna: CPF_CNPJ, categoria: "CPF ou CNPJ do proprietário"}
    - {coluna: NMOPERADOR, categoria: "nome ou razão social do operador"}
    - {coluna: NM_OPERADOR, categoria: "nome ou razão social do operador"}
    - {coluna: OUTROSOPERADORES, categoria: "nomes dos demais operadores"}
    - {coluna: OUTROS_OPERADORES, categoria: "nomes dos demais operadores"}
    - {coluna: CPFCGC, categoria: "CPF ou CNPJ do operador"}
    - {coluna: CPF_CGC, categoria: "CPF ou CNPJ do operador"}
  eras: 
    - {desde: 2022-09, mudanca: "nos meses sem JSON o conversor lê o XLS, cujos nomes de coluna têm sublinhado (`NR_CERT_MATRICULA`, em vez de `NRCERTMATRICULA` no JSON)"}
    - {desde: 2024-09, mudanca: "o CSV passa a ser publicado, com os nomes com sublinhado e três colunas novas (`TP_POUSO`, `QT_MOTOR`, `TP_MOTOR`)"}
  revisado_em: 2026-11-15
  versao_fetcher: 0.9.0
---

# Registro Aeronáutico Brasileiro (RAB), histórico mensal

## Resumo

Fotografias mensais do cadastro de aeronaves do Registro Aeronáutico Brasileiro, com marca, proprietário, operador, modelo, fabricante, situação de aeronavegabilidade e cancelamento.

## Ficha técnica

<!-- gerado:ficha -->

| Campo | Valor |
|---|---|
| Dataset | `anac/rab` |
| Órgão | Agência Nacional de Aviação Civil (ANAC) |
| Página oficial | https://www.anac.gov.br/acesso-a-informacao/dados-abertos/areas-de-atuacao/aeronaves/registro-aeronautico-brasileiro |
| Licença | Não informada pela fonte: as páginas de metadados da ANAC não trazem licença (conferido em 2026-11-15). |
| Periodicidade | mensal |
| Cobertura | 2017-01 a em-curso |
| Unidade (uma linha) | uma aeronave matriculada, na fotografia de um mês |
| Granularidade | espacial: Brasil (aeronave); temporal: mês |
| Formato bruto | um arquivo por mês `<AAAA-MM>` em CSV (desde 2024-09), JSON e XLS, separador ponto e vírgula; mais o cadastro vigente `dados_aeronaves` |
| Estado no lake | convertido |
| Partições | `ano`, `mes` |
| Chave | — |
| Colunas | 66 |
| Unidades de medida | — |
| Dados pessoais | `PROPRIETARIO` (nome ou razão social do proprietário); `OUTROSPROPRIETARIOS` (nomes dos demais proprietários); `OUTROS_PROPRIETARIOS` (nomes dos demais proprietários); `CPFCNPJ` (CPF ou CNPJ do proprietário); `CPF_CNPJ` (CPF ou CNPJ do proprietário); `NMOPERADOR` (nome ou razão social do operador); `NM_OPERADOR` (nome ou razão social do operador); `OUTROSOPERADORES` (nomes dos demais operadores); `OUTROS_OPERADORES` (nomes dos demais operadores); `CPFCGC` (CPF ou CNPJ do operador); `CPF_CGC` (CPF ou CNPJ do operador) |
| Eras | 2022-09: nos meses sem JSON o conversor lê o XLS, cujos nomes de coluna têm sublinhado (`NR_CERT_MATRICULA`, em vez de `NRCERTMATRICULA` no JSON); 2024-09: o CSV passa a ser publicado, com os nomes com sublinhado e três colunas novas (`TP_POUSO`, `QT_MOTOR`, `TP_MOTOR`) |
| Revisado em | 2026-11-15 |
| Versão do fetcher | 0.9.0 |

## Origem e coleta

- O fetcher baixa, de `Aeronaves/RAB/Historico_RAB/<AAAA-MM>.<ext>`, uma fotografia por mês desde 2017-01 (2019-05 não existe em nenhum formato); o CSV só existe desde 2024-09, e o JSON e o XLS têm lacunas pontuais (por exemplo, JSON ausente em vários meses de 2022 e 2023).
- O conversor escolhe um formato por mês: CSV, depois JSON, depois XLS. Assim, até 2024-08 a fotografia vem do JSON (ou do XLS, onde falta o JSON) e, a partir de 2024-09, do CSV.
- O cadastro vigente (`dados_aeronaves.csv`) fica em outro dataset, `rab-atual`, sem partição (veja Conteúdo).
- Conferido em 2026-11-15, com amostras de 2017-01, 2019-03 e 2022-08 (JSON, 33 colunas sem sublinhado, como `NRCERTMATRICULA`), 2023-01 (XLS, 33 colunas com sublinhado, como `NR_CERT_MATRICULA`) e 2024-10 (CSV, as mesmas 33 mais `TP_POUSO`, `QT_MOTOR` e `TP_MOTOR`).

## Conteúdo

- Amostra local de 149.926 linhas em 5 arquivo(s) Parquet, convertida em 2026-11-15 com o fetcher 0.9.0; a amostra não cobre toda a série publicada.
- Amostras: 2019-03 (JSON) com 29.558 linhas e 33 colunas; 2024-10 (CSV) com 31.895 linhas e 36 colunas; o cadastro vigente tem 35.161 linhas e 34 colunas.
- `CD_INTERDICAO` (situação de aeronavegabilidade) usa estes códigos (tabela da fonte): `R` reserva de marcas, `N` situação normal, `S` certificado de aeronavegabilidade suspenso, `C` certificado cancelado, `V` certificado vencido, `X` aeronave interditada, `U` aeronave ultraleve (situação normal), `Z` aeronave experimental (situação normal), `P` situação punitiva em vigor, `M` matrícula cancelada.
- Os motivos de suspensão da aeronavegabilidade (tabela da fonte): `1` aeronave avariada por acidentes ou incidentes, `3` pendências judiciais, `4` situação irregular no RAB, `6` situação técnica irregular, `7` não cumprimento de NCIA, `8` CVA vencida.
- O cadastro vigente (`rab-atual`, fora da lista de datasets do conversor) tem 34 colunas, entre elas `MARCAS`, `PROPRIETARIOS` e `OPERADORES` no plural e colunas que a fonte não documenta (`TP_CA`, `CD_PROPOSITO_CAVE`, `NM_PROPOSITO_CAVE`, `CF_OPERACIONAL`, `DS_CATEGORIA_HOMOLOGACAO`, `TP_OPERACAO`, `DT_VENDA`, `DS_MOEDA`, `NR_PRECO_VENDA`).

## Variáveis

As descrições vêm da página de metadados do conjunto no portal da ANAC (61 de 66 colunas); as demais ficam como "Sem descrição oficial".

| Coluna no lake | Na fonte | Tipo | Descrição | Unidade / códigos | Período |
|---|---|---|---|---|---|
| `MARCA` | `MARCA` | texto | Conjunto alfanumérico de marcas de nacionalidade e matrícula; no Brasil só letras: nacionalidade PP, PR, PT, PS ou PU e as três últimas letras de matrícula (campo `MARCAS` da documentação). | — | todo |
| `PROPRIETARIO` | `PROPRIETARIO` | texto | Nome ou Razão Social do Proprietário registrado da aeronave | — | todo |
| `OUTROSPROPRIETARIOS` | `OUTROSPROPRIETARIOS` | texto | Nome ou Razão Social dos demais proprietários da aeronave | — | só nos arquivos JSON |
| `SGUF` | `SGUF` | texto | Estado da Federação da residência declarada pelo Proprietário (campo `UF` da documentação) | — | só nos arquivos JSON |
| `CPFCNPJ` | `CPFCNPJ` | texto | Identidade de Pessoa Física ou Jurídica do Proprietário | — | só nos arquivos JSON |
| `NMOPERADOR` | `NMOPERADOR` | texto | Nome ou Razão Social do Operador registrado da aeronave (campo `OPERADOR` da documentação) | — | só nos arquivos JSON |
| `OUTROSOPERADORES` | `OUTROSOPERADORES` | texto | Nome ou Razão Social dos demais Operadores da aeronave | — | só nos arquivos JSON |
| `UFOPERADOR` | `UFOPERADOR` | texto | Estado da Federação da residência declarada pelo Operador. | — | só nos arquivos JSON |
| `CPFCGC` | `CPFCGC` | texto | Identidade de Pessoa Física ou Jurídica do Operador. | — | só nos arquivos JSON |
| `NRCERTMATRICULA` | `NRCERTMATRICULA` | texto | Número atribuído pelo Registro em uma sequência cronológica quando da matrícula da aeronave na emissão do CM (Certificado de Matrícula). (campo `MATRÍCULA` da documentação) | — | só nos arquivos JSON |
| `NRSERIE` | `NRSERIE` | texto | Número de série atribuído pelo Fabricante – único para cada aeronave (campo `NÚM. SÉRIE` da documentação) | — | só nos arquivos JSON |
| `CDCATEGORIA` | `CDCATEGORIA` | texto | Classificação das aeronaves de acordo com a natureza do Operador (Privado ou Público) e com o tipo de operação como instrução, aero agrícola, transporte de passageiros, etc. (campo `CATEGORIA` da documentação) | — | só nos arquivos JSON |
| `CDTIPO` | `CDTIPO` | texto | Treinamento e habilitação para pilotos para determinados modelos de aeronaves. (campo `TIPO CERT` da documentação) | — | só nos arquivos JSON |
| `DSMODELO` | `DSMODELO` | texto | Modelo de produto aeronáutico, reconhecido mediante certificação pela ANAC. (campo `MODELO` da documentação) | — | só nos arquivos JSON |
| `NMFABRICANTE` | `NMFABRICANTE` | texto | Nome do Fabricante da Aeronave (campo `NOME FABRICANTE` da documentação) | — | só nos arquivos JSON |
| `CDCLS` | `CDCLS` | texto | Classificação baseada em características como: Tipo de Pouso, Tipo e Número de motores – prevista no RBAC 21 (campo `CLASSE` da documentação) | — | só nos arquivos JSON |
| `NRPMD` | `NRPMD` | texto | Peso Máximo de Decolagem (campo `PMD` da documentação) | — | só nos arquivos JSON |
| `CDTIPOICAO` | `CDTIPOICAO` | texto | Agrupamento de modelos de aeronaves que geram os mesmos impactos na operação de um aeródromo. (campo `TIPO_ICAO` da documentação) | — | só nos arquivos JSON |
| `NRTRIPULACAOMIN` | `NRTRIPULACAOMIN` | texto | Tripulação mínima (campo `TRIP. MÍN.` da documentação) | — | só nos arquivos JSON |
| `NRPASSAGEIROSMAX` | `NRPASSAGEIROSMAX` | texto | Número máximo de passageiros (campo `PAX MAX` da documentação) | — | só nos arquivos JSON |
| `NRASSENTOS` | `NRASSENTOS` | texto | Número de assentos (campo `ASSENTOS` da documentação) | — | só nos arquivos JSON |
| `NRANOFABRICACAO` | `NRANOFABRICACAO` | texto | Ano de Fabricação da aeronave (campo `ANO FAB` da documentação) | — | só nos arquivos JSON |
| `DTVALIDADEIAM` | `DTVALIDADEIAM` | texto | Sem descrição oficial. | — | só nos arquivos JSON |
| `DTVALIDADECA` | `DTVALIDADECA` | texto | Data de validade do CA (campo `VAL CA` da documentação) | — | só nos arquivos JSON |
| `DTCANC` | `DTCANC` | texto | Data de cancelamento da Matrícula da Aeronave (campo `DATA CANC` da documentação) | — | só nos arquivos JSON |
| `DSMOTIVOCANC` | `DSMOTIVOCANC` | texto | Motivo do cancelamento da Matrícula (campo `MOTIVO` da documentação) | — | só nos arquivos JSON |
| `CDINTERDICAO` | `CDINTERDICAO` | texto | Situação de Aeronavegabilidade (Normal, suspensa, etc.) | — | só nos arquivos JSON |
| `CDMARCANAC1` | `CDMARCANAC1` | texto | Marcas Nacionais anteriores – se houver (campo `MARCA NAC 1` da documentação) | — | só nos arquivos JSON |
| `CDMARCANAC2` | `CDMARCANAC2` | texto | Marcas Nacionais anteriores – se houver (campo `MARCA NAC 2` da documentação) | — | só nos arquivos JSON |
| `CDMARCANAC3` | `CDMARCANAC3` | texto | Marcas Nacionais anteriores – se houver (campo `MARCA NAC 3` da documentação) | valores nas amostras: ``, `1`, `3402`, `7`, `PPEOM`, `PTAVZ`, `U206C` | só nos arquivos JSON |
| `CDMARCAESTRANGEIRA` | `CDMARCAESTRANGEIRA` | texto | Marcas estrangeiras anteriores (campo `MARCA EST` da documentação) | — | só nos arquivos JSON |
| `DSGRAVAME` | `DSGRAVAME` | texto | Descrição de restrições de Direitos Reais sobre a aeronave (campo `DESCRIÇÃO DO GRAVAME` da documentação) | — | só nos arquivos JSON |
| `DT_MATRICULA` | `DT_MATRICULA` | texto | Sem descrição oficial. | — | todo |
| `OUTROS_PROPRIETARIOS` | `OUTROS_PROPRIETARIOS` | texto | Nome ou Razão Social dos demais proprietários da aeronave | — | arquivos XLS e CSV |
| `SG_UF` | `SG_UF` | texto | Estado da Federação da residência declarada pelo Proprietário (campo `UF` da documentação) | — | arquivos XLS e CSV |
| `CPF_CNPJ` | `CPF_CNPJ` | texto | Identidade de Pessoa Física ou Jurídica do Proprietário | — | arquivos XLS e CSV |
| `NM_OPERADOR` | `NM_OPERADOR` | texto | Nome ou Razão Social do Operador registrado da aeronave (campo `OPERADOR` da documentação) | — | arquivos XLS e CSV |
| `OUTROS_OPERADORES` | `OUTROS_OPERADORES` | texto | Nome ou Razão Social dos demais Operadores da aeronave | — | arquivos XLS e CSV |
| `UF_OPERADOR` | `UF_OPERADOR` | texto | Estado da Federação da residência declarada pelo Operador. | — | arquivos XLS e CSV |
| `CPF_CGC` | `CPF_CGC` | texto | Identidade de Pessoa Física ou Jurídica do Operador. | — | arquivos XLS e CSV |
| `NR_CERT_MATRICULA` | `NR_CERT_MATRICULA` | texto | Número atribuído pelo Registro em uma sequência cronológica quando da matrícula da aeronave na emissão do CM (Certificado de Matrícula). (campo `MATRÍCULA` da documentação) | — | arquivos XLS e CSV |
| `NR_SERIE` | `NR_SERIE` | texto | Número de série atribuído pelo Fabricante – único para cada aeronave (campo `NÚM. SÉRIE` da documentação) | — | arquivos XLS e CSV |
| `CD_CATEGORIA` | `CD_CATEGORIA` | texto | Classificação das aeronaves de acordo com a natureza do Operador (Privado ou Público) e com o tipo de operação como instrução, aero agrícola, transporte de passageiros, etc. (campo `CATEGORIA` da documentação) | — | arquivos XLS e CSV |
| `CD_TIPO` | `CD_TIPO` | texto | Treinamento e habilitação para pilotos para determinados modelos de aeronaves. (campo `TIPO CERT` da documentação) | — | arquivos XLS e CSV |
| `DS_MODELO` | `DS_MODELO` | texto | Modelo de produto aeronáutico, reconhecido mediante certificação pela ANAC. (campo `MODELO` da documentação) | — | arquivos XLS e CSV |
| `NM_FABRICANTE` | `NM_FABRICANTE` | texto | Nome do Fabricante da Aeronave (campo `NOME FABRICANTE` da documentação) | — | arquivos XLS e CSV |
| `CD_CLS` | `CD_CLS` | texto | Classificação baseada em características como: Tipo de Pouso, Tipo e Número de motores – prevista no RBAC 21 (campo `CLASSE` da documentação) | — | arquivos XLS e CSV |
| `NR_PMD` | `NR_PMD` | texto | Peso Máximo de Decolagem (campo `PMD` da documentação) | — | arquivos XLS e CSV |
| `CD_TIPO_ICAO` | `CD_TIPO_ICAO` | texto | Agrupamento de modelos de aeronaves que geram os mesmos impactos na operação de um aeródromo. (campo `TIPO_ICAO` da documentação) | — | arquivos XLS e CSV |
| `NR_TRIPULACAO_MIN` | `NR_TRIPULACAO_MIN` | texto | Tripulação mínima (campo `TRIP. MÍN.` da documentação) | — | arquivos XLS e CSV |
| `NR_PASSAGEIROS_MAX` | `NR_PASSAGEIROS_MAX` | texto | Número máximo de passageiros (campo `PAX MAX` da documentação) | — | arquivos XLS e CSV |
| `NR_ASSENTOS` | `NR_ASSENTOS` | texto | Número de assentos (campo `ASSENTOS` da documentação) | — | arquivos XLS e CSV |
| `NR_ANO_FABRICACAO` | `NR_ANO_FABRICACAO` | texto | Ano de Fabricação da aeronave (campo `ANO FAB` da documentação) | — | arquivos XLS e CSV |
| `DT_VALIDADE_CVA` | `DT_VALIDADE_CVA` | texto | Data de validade do Certificado de Verificação de Aeronavegabilidade (campo `VAL CAV` da documentação) | — | arquivos XLS e CSV |
| `DT_VALIDADE_CA` | `DT_VALIDADE_CA` | texto | Data de validade do CA (campo `VAL CA` da documentação) | — | arquivos XLS e CSV |
| `DT_CANC` | `DT_CANC` | texto | Data de cancelamento da Matrícula da Aeronave (campo `DATA CANC` da documentação) | — | arquivos XLS e CSV |
| `DS_MOTIVO_CANC` | `DS_MOTIVO_CANC` | texto | Motivo do cancelamento da Matrícula (campo `MOTIVO` da documentação) | — | arquivos XLS e CSV |
| `CD_INTERDICAO` | `CD_INTERDICAO` | texto | Situação de Aeronavegabilidade (Normal, suspensa, etc.) | — | arquivos XLS e CSV |
| `CD_MARCA_NAC1` | `CD_MARCA_NAC1` | texto | Marcas Nacionais anteriores – se houver (campo `MARCA NAC 1` da documentação) | — | arquivos XLS e CSV |
| `CD_MARCA_NAC2` | `CD_MARCA_NAC2` | texto | Marcas Nacionais anteriores – se houver (campo `MARCA NAC 2` da documentação) | — | arquivos XLS e CSV |
| `CD_MARCA_NAC3` | `CD_MARCA_NAC3` | texto | Marcas Nacionais anteriores – se houver (campo `MARCA NAC 3` da documentação) | valores nas amostras: `1`, `3402`, `7`, `PPEOM`, `PTAVZ`, `U206C`, `null` | arquivos XLS e CSV |
| `CD_MARCA_ESTRANGEIRA` | `CD_MARCA_ESTRANGEIRA` | texto | Marcas estrangeiras anteriores (campo `MARCA EST` da documentação) | — | arquivos XLS e CSV |
| `DS_GRAVAME` | `DS_GRAVAME` | texto | Descrição de restrições de Direitos Reais sobre a aeronave (campo `DESCRIÇÃO DO GRAVAME` da documentação) | — | arquivos XLS e CSV |
| `TP_POUSO` | `TP_POUSO` | texto | Sem descrição oficial. | valores nas amostras: `ANFIBIO`, `DRONE (RPAS)`, `GIROCOPTERO`, `HELICOPTERO`, `POUSO CONVECIONAL`, `POUSO EM TERRA`, `POUSO NA AGUA`, `null` | só nos arquivos CSV (desde 2024-09) |
| `QT_MOTOR` | `QT_MOTOR` | texto | Sem descrição oficial. | valores nas amostras: `0`, `1`, `2`, `3`, `4`, `null` | só nos arquivos CSV (desde 2024-09) |
| `TP_MOTOR` | `TP_MOTOR` | texto | Sem descrição oficial. | — | só nos arquivos CSV (desde 2024-09) |
| `ano` | — (partição) | texto | Partição do lake: ano do arquivo de origem, tirado do nome do arquivo. | — | todo |
| `mes` | — (partição) | texto | Partição do lake: mês do arquivo de origem, tirado do nome do arquivo. | — | todo |

## No lake

- Dataset `anac/rab`, particionado por `ano`, `mes`; um Parquet por arquivo de origem.
- O conversor escolhe um arquivo por conteúdo (CSV antes de JSON antes de XLS, salvo grupos que preferem JSON) e lê todas as colunas como texto, exceto onde o JSON traz números.
- Colunas que repetem a partição (`ano`, `mes`) saem do Parquet; o valor fica no caminho.

## Cuidados de uso

- **Nomes de coluna por formato de origem.** O mesmo atributo tem nome sem sublinhado nos arquivos JSON (`NRCERTMATRICULA`) e com sublinhado nos XLS e CSV (`NR_CERT_MATRICULA`). Como o conversor lê o JSON quando existe, a escolha depende do mês: o JSON falta de 2022-09 a 2023-12 (exceto 2023-04 e 2023-11) e em 2019-12. Ao ler várias partições, una as colunas pelo conceito (a tabela de variáveis tem os dois nomes) antes de empilhar.
- **Texto `null`.** Alguns campos trazem o texto `null` em vez de vazio.
- **Tudo é texto.** Datas, ano de fabricação, PMD e assentos chegam como texto.
- **Dados pessoais.** O RAB traz nome e CPF/CNPJ de proprietários e operadores, como a fonte publica.
- **Meses sem dado.** Não há 2019-05, e há lacunas de JSON e XLS em 2019-12 e entre 2022-09 e 2023-12 que o conversor cobre com o outro formato quando existe.
- **Dois datasets por causa da granularidade.** O cadastro vigente, sem período, grava em `rab-atual`, que o conversor não declara em `datasets()` e portanto não tem página nem esquema de referência.

## Exemplos

Linhas por mês de partição:

```python
import duckdb

duckdb.sql("""
    SELECT ano, mes, count(*) AS linhas
    FROM read_parquet('lake/anac/rab/**/*.parquet', hive_partitioning = true, union_by_name = true)
    GROUP BY ALL ORDER BY ano, mes
""").show()
```

## Referências

- Página do conjunto de dados: https://www.anac.gov.br/acesso-a-informacao/dados-abertos/areas-de-atuacao/aeronaves/registro-aeronautico-brasileiro
- Servidor de dados abertos da ANAC: https://sistemas.anac.gov.br/dadosabertos/
