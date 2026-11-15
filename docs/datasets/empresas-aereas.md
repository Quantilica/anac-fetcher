---
dataset:
  id: empresas-aereas
  fonte: anac
  titulo: "Empresas aéreas nacionais"
  resumo: "Cadastro de empresas aéreas nacionais aptas a operar no Brasil, com razão social, CNPJ, sede, contatos, serviços aéreos e decisão operacional."
  orgao: Agência Nacional de Aviação Civil (ANAC)
  pagina_oficial: https://www.anac.gov.br/acesso-a-informacao/dados-abertos/areas-de-atuacao/operador-aereo/empresas-aereas-nacionais
  licenca: "Não informada pela fonte: as páginas de metadados da ANAC não trazem licença (conferido em 2026-11-15)."
  periodicidade: "diária"
  cobertura: {inicio: "2026-11", fim: "em-curso"}
  unidade: "uma empresa aérea nacional no cadastro vigente"
  granularidade: {espacial: "Brasil (sede da empresa)", temporal: "cadastro vigente (sem série)"}
  formato_bruto: "JSON em linhas (NDJSON) de `pda_empresas_aereas_nacionais`; o CSV da fonte vem quebrado e não é usado"
  lake: {estado: convertido, particoes: [], chave: [], colunas: 24}
  unidades_de_medida:
    id_empresa_aerea: "sem unidade (identificador)"
  dados_pessoais: 
    - {coluna: email, categoria: "contato de empresa"}
    - {coluna: telefone, categoria: "contato de empresa"}
  eras: []
  revisado_em: 2026-11-15
  versao_fetcher: 0.9.0
---

# Empresas aéreas nacionais

## Resumo

Cadastro de empresas aéreas nacionais aptas a operar no Brasil, com razão social, CNPJ, sede, contatos, serviços aéreos e decisão operacional. Por ser um conjunto sem série, a cobertura registra a data da coleta.

## Ficha técnica

<!-- gerado:ficha -->

| Campo | Valor |
|---|---|
| Dataset | `anac/empresas-aereas` |
| Órgão | Agência Nacional de Aviação Civil (ANAC) |
| Página oficial | https://www.anac.gov.br/acesso-a-informacao/dados-abertos/areas-de-atuacao/operador-aereo/empresas-aereas-nacionais |
| Licença | Não informada pela fonte: as páginas de metadados da ANAC não trazem licença (conferido em 2026-11-15). |
| Periodicidade | diária |
| Cobertura | 2026-11 a em-curso |
| Unidade (uma linha) | uma empresa aérea nacional no cadastro vigente |
| Granularidade | espacial: Brasil (sede da empresa); temporal: cadastro vigente (sem série) |
| Formato bruto | JSON em linhas (NDJSON) de `pda_empresas_aereas_nacionais`; o CSV da fonte vem quebrado e não é usado |
| Estado no lake | convertido |
| Partições | — |
| Chave | — |
| Colunas | 24 |
| Unidades de medida | `id_empresa_aerea`: sem unidade (identificador) |
| Dados pessoais | `email` (contato de empresa); `telefone` (contato de empresa) |
| Eras | nenhuma |
| Revisado em | 2026-11-15 |
| Versão do fetcher | 0.9.0 |

## Origem e coleta

- O fetcher baixa `Operador Aéreo/pda_empresas_aereas_nacionais` em CSV e JSON; o CSV da fonte vem com o separador `\"` literal e o cabeçalho repetido a cada registro, e por isso o conversor lê o JSON (NDJSON).
- O arquivo JSON completo tem cerca de 509 MB; conferido em 2026-11-15 com uma amostra local dos primeiros 25 MB (26.853 registros, 24 campos). O restante do arquivo não foi examinado.
- A ANAC sobrescreve o arquivo a cada atualização.

## Conteúdo

- Amostra local de 26.853 linhas em 1 arquivo(s) Parquet, convertida em 2026-11-15 com o fetcher 0.9.0; a amostra não cobre toda a série publicada.
- Cada registro é uma empresa; os campos `MCDA`, `Título`, `Fonte`, `Data`, `ConjuntoDado`, `ReferenciaData` e `Data da última Ingestão` parecem metadados da publicação (a fonte não os documenta).
- 26.853 registros para 652 `id_empresa_aerea` (651 CNPJ) distintos: cada empresa aparece em muitos registros, com `Data` de publicação diferente; `id_empresa_aerea` não é chave. `situacao` vale `ATIVA` em todos os registros da amostra.
- `Título` é um texto que repete ICAO, CNPJ, razão social, atividades e UF; `icao` está vazio na maior parte das empresas (20 valores distintos).

## Variáveis

As descrições vêm da página de metadados do conjunto no portal da ANAC (14 de 24 colunas); as demais ficam como "Sem descrição oficial".

| Coluna no lake | Na fonte | Tipo | Descrição | Unidade / códigos | Período |
|---|---|---|---|---|---|
| `Título` | `Título` | texto | Sem descrição oficial. | — | todo |
| `MCDA` | `MCDA` | texto | Sem descrição oficial. | valores nas amostras: `Operador Aéreo` | todo |
| `atividades_aereas` | `atividades_aereas` | texto | Atividades desempenhadas por empresas aéreas mediante remuneração, que abrange o disposto no art. 175 da Lei nº 7565, de 19 de dezembro de 1986, que dispõe sobre o Código Brasileiro de Aeronáutica. São exemplos de atividades aéreas o transporte aéreo regular, transporte aéreo não-regular e serviços aéreos especializados. | — | todo |
| `icao` | `icao` | texto | Designador de 3 letras fornecidos pela Organização de Aviação Civil Internacional (OACI) às empresas aéreas. | — | todo |
| `cidade` | `cidade` | texto | Cidade em que a empresa aérea está sediada. | — | todo |
| `cnpj` | `cnpj` | texto | Cadastro Nacional de Pessoa Jurídica mantido pela RFB. | — | todo |
| `email` | `email` | texto | Correio eletrônico da empresa aérea. | — | todo |
| `situacao` | `situacao` | texto | Sem descrição oficial. | valores nas amostras: `ATIVA` | todo |
| `Fonte` | `Fonte` | texto | Sem descrição oficial. | valores nas amostras: `Base de dados` | todo |
| `razao_social` | `razao_social` | texto | Nome de registro da empresa constante em seu ato constitutivo. | — | todo |
| `Data` | `Data` | texto | Sem descrição oficial. | — | todo |
| `cep` | `cep` | texto | CEP em que a empresa aérea está sediada. | — | todo |
| `validade_operacional` | `validade_operacional` | texto | Data de expiração da decisão operacional | — | todo |
| `iata` | `iata` | texto | Sem descrição oficial. | — | todo |
| `uf` | `uf` | texto | UF em que a empresa aérea está sediada. | — | todo |
| `endereco_sede` | `endereco_sede` | texto | Endereço da sede que consta no Contrato ou Estatuto Social da empresa aérea. | — | todo |
| `decisao_operacional` | `decisao_operacional` | texto | Instrumento legal que autoriza, mediante autorização ou concessão, a exploração dos serviços aéreos públicos. | — | todo |
| `Data da última Ingestão` | `Data da última Ingestão` | texto | Sem descrição oficial. | — | todo |
| `ConjuntoDado` | `ConjuntoDado` | texto | Sem descrição oficial. | valores nas amostras: `Empresas Aéreas nacionais` | todo |
| `id_empresa_aerea` | `id_empresa_aerea` | inteiro | Empresas, nacionais ou internacionais, que exploram serviços aéreos públicos mediante prévia concessão ou autorização, conforme disciplinado pelo art.180 da Lei nº 7565, de 19 de dezembro de 1986, que dispõe sobre o Código Brasileiro de Aeronáutica. | — | todo |
| `data_decisao_operacional` | `data_decisao_operacional` | texto | Data em que a Decisão Operacional é publicada no Diário Oficial da União. | — | todo |
| `uf_iso` | `uf_iso` | texto | Sem descrição oficial. | — | todo |
| `ReferenciaData` | `ReferenciaData` | texto | Sem descrição oficial. | valores nas amostras: `data_decisao_operacional` | todo |
| `telefone` | `telefone` | texto | Contato telefônico da empresa aérea. | — | todo |

## No lake

- Dataset `anac/empresas-aereas`, sem partições; um Parquet por arquivo de origem (1 na amostra).
- O conversor escolhe um arquivo por conteúdo (CSV antes de JSON antes de XLS, salvo grupos que preferem JSON) e lê todas as colunas como texto, exceto onde o JSON traz números.
- Colunas que repetem a partição (`ano`, `mes`) saem do Parquet; o valor fica no caminho.

## Cuidados de uso

- **CSV da fonte inutilizável.** Use o JSON; o fetcher já o prefere.
- **Amostra limitada.** O esquema aqui vem dos primeiros registros do JSON.
- **Contatos.** `email` e `telefone` são contatos de empresas, não de pessoas físicas, mas confira antes de redistribuir.

## Exemplos

Contagem de linhas e de valores distintos de `Título`:

```python
import duckdb

duckdb.sql("""
    SELECT count(*) AS linhas, count(DISTINCT "Título") AS distintos
    FROM read_parquet('lake/anac/empresas-aereas/*.parquet', union_by_name = true)
""").show()
```

## Referências

- Página do conjunto de dados: https://www.anac.gov.br/acesso-a-informacao/dados-abertos/areas-de-atuacao/operador-aereo/empresas-aereas-nacionais
- Servidor de dados abertos da ANAC: https://sistemas.anac.gov.br/dadosabertos/
