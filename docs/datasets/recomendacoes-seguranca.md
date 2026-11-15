---
dataset:
  id: recomendacoes-seguranca
  fonte: anac
  titulo: "Recomendações de segurança aeronáutica"
  resumo: "Recomendações de segurança emitidas pelo CENIPA após investigação, com a ocorrência associada, o encaminhamento na ANAC, o prazo e a resposta."
  orgao: Agência Nacional de Aviação Civil (ANAC)
  pagina_oficial: https://www.anac.gov.br/acesso-a-informacao/dados-abertos/areas-de-atuacao/seguranca-operacional/recomendacoes-de-seguranca-aeronautica
  licenca: "Não informada pela fonte: as páginas de metadados da ANAC não trazem licença (conferido em 2026-11-15)."
  periodicidade: "semanal"
  cobertura: {inicio: "1989-11", fim: "em-curso"}
  unidade: "uma recomendação de segurança"
  granularidade: {espacial: "Brasil", temporal: "recomendação (data de recebimento)"}
  formato_bruto: "CSV (e JSON) único `RECOMENDACAO_SEGURANCA`, separador ponto e vírgula"
  lake: {estado: convertido, particoes: [], chave: [], colunas: 14}
  dados_pessoais: nenhum
  eras: []
  revisado_em: 2026-11-15
  versao_fetcher: 0.9.0
---

# Recomendações de segurança aeronáutica

## Resumo

Recomendações de segurança emitidas pelo CENIPA após investigação, com a ocorrência associada, o encaminhamento na ANAC, o prazo e a resposta.

## Ficha técnica

<!-- gerado:ficha -->

| Campo | Valor |
|---|---|
| Dataset | `anac/recomendacoes-seguranca` |
| Órgão | Agência Nacional de Aviação Civil (ANAC) |
| Página oficial | https://www.anac.gov.br/acesso-a-informacao/dados-abertos/areas-de-atuacao/seguranca-operacional/recomendacoes-de-seguranca-aeronautica |
| Licença | Não informada pela fonte: as páginas de metadados da ANAC não trazem licença (conferido em 2026-11-15). |
| Periodicidade | semanal |
| Cobertura | 1989-11 a em-curso |
| Unidade (uma linha) | uma recomendação de segurança |
| Granularidade | espacial: Brasil; temporal: recomendação (data de recebimento) |
| Formato bruto | CSV (e JSON) único `RECOMENDACAO_SEGURANCA`, separador ponto e vírgula |
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

- O fetcher baixa `Seguranca Operacional/Recomendação de Segurança/RECOMENDACAO_SEGURANCA.csv` (e o JSON); a ANAC sobrescreve o arquivo a cada atualização.
- Conferido em 2026-11-15: 3.303 linhas e 14 colunas.
- A fonte descreve o conjunto como as ocorrências e respectivas recomendações enviadas pelo CENIPA após investigação, com os encaminhamentos internos da ANAC e os prazos de realização.

## Conteúdo

- Amostra local de 3.303 linhas em 1 arquivo(s) Parquet, convertida em 2026-11-15 com o fetcher 0.9.0; a amostra não cobre toda a série publicada.
- O prazo de resposta ao CENIPA é de 120 dias a partir do recebimento da recomendação (descrição da fonte).
- `TXT_RECOM_SEGURANCA` e `TEXTO_RESPOSTA` trazem texto livre, às vezes longo.
- As datas vêm como texto `AAAA-MM-DD 00:00:00.` (com ponto no fim); `DATA_OCORRENCIA` tem 130 linhas vazias (texto vazio, não nulo) e a data de ocorrência mais antiga é 1989-11-28.
- `STATUS_ANAC_RECOMENDACAO` na amostra: `Cumprida` (2.929), `Não Aplicável` (255), `Não Cumprida` (9), `Respondida, mas aguardando atualização` (5) e outros.

## Variáveis

As descrições vêm da página de metadados do conjunto no portal da ANAC (14 de 14 colunas); as demais ficam como "Sem descrição oficial".

| Coluna no lake | Na fonte | Tipo | Descrição | Unidade / códigos | Período |
|---|---|---|---|---|---|
| `NUMERO_OCORRENCIA` | `NUMERO_OCORRENCIA` | texto | Número da Ocorrência associada à Recomendação de Segurança (campo `Número da Ocorrência` da documentação) | — | todo |
| `NUMERO_PROCESSO` | `NUMERO_PROCESSO` | texto | Número do Processo SEI com as informações da Recomendação de Segurança (campo `Número do Processo` da documentação) | — | todo |
| `CATEGORIA_OCORRENCIA` | `CATEGORIA_OCORRENCIA` | texto | Categoria da Ocorrência Aeronáutica. Pode ser associada a uma ocorrência ou a algum documento do CENIPA (campo `Categoria da Ocorrência` da documentação) | valores nas amostras: `Acidente`, `Incidente`, `Incidente Grave` | todo |
| `MATRICULA` | `MATRICULA` | texto | Matrícula da Aeronave associada à Recomendação de Segurança | — | todo |
| `DATA_OCORRENCIA` | `DATA_OCORRENCIA` | texto | Data da Ocorrência associada à Recomendação de Segurança (campo `Data da Ocorrência` da documentação) | — | todo |
| `NRO_RECOM_SEGURANCA` | `NRO_RECOM_SEGURANCA` | texto | Número da Recomendação de Segurança (campo `Número da Recomendação de Segurança` da documentação) | — | todo |
| `TXT_RECOM_SEGURANCA` | `TXT_RECOM_SEGURANCA` | texto | Descrição da Recomendação de Segurança (campo `Texto da Recomendação de Segurança` da documentação) | — | todo |
| `CLASS_RECOM_SEGURANCA` | `CLASS_RECOM_SEGURANCA` | texto | Classificação dada pela ANAC a Recomendação de Segurança (campo `Classificação da Recomendação de Segurança` da documentação) | valores nas amostras: `Certificação`, `Fiscalização`, `Outros`, `Promoção`, `Regulamentação` | todo |
| `DATA_RECEBIMENTO_RECOM` | `DATA_RECEBIMENTO_RECOM` | texto | Data que a Recomendação de Segurança foi recebida na ANAC (campo `Data do Recebimento da Recomendação` da documentação) | — | todo |
| `AREA_COMPETENTE` | `AREA_COMPETENTE` | texto | Área da ANAC responsável por analisar e fornecer informações para resposta da Recomendação de Segurança | valores nas amostras: `ASSOP`, `OUTRA`, `SAR`, `SFI`, `SIA`, `SPL`, `SPO` | todo |
| `STATUS_ANAC_RECOMENDACAO` | `STATUS_ANAC_RECOMENDACAO` | texto | Status da Recomendação de Segurança na ANAC (campo `Status ANAC da Recomendação` da documentação) | valores nas amostras: `Aberta`, `Cancelada`, `Cumprida`, `Não Aplicável`, `Não Cumprida`, `Respondida, mas aguardando atualização` | todo |
| `PRAZO_RESPOSTA_RECOM_SEGURANCA` | `PRAZO_RESPOSTA_RECOM_SEGURANCA` | texto | Prazo de resposta da Recomendação de Segurança ao CENIPA. O prazo é de 120 dias a partir do recebimento da Recomendação de Segurança (campo `Prazo da Resposta da Recomendação de Segurança` da documentação) | — | todo |
| `TEXTO_RESPOSTA` | `TEXTO_RESPOSTA` | texto | Texto da Resposta da ANAC para a Recomendação de Segurança (campo `Texto da Resposta` da documentação) | — | todo |
| `DATA_RESPOSTA` | `DATA_RESPOSTA` | texto | Data da Resposta da ANAC para a Recomendação de Segurança (campo `Data da Resposta` da documentação) | — | todo |

## No lake

- Dataset `anac/recomendacoes-seguranca`, sem partições; um Parquet por arquivo de origem (1 na amostra).
- O conversor escolhe um arquivo por conteúdo (CSV antes de JSON antes de XLS, salvo grupos que preferem JSON) e lê todas as colunas como texto, exceto onde o JSON traz números.
- Colunas que repetem a partição (`ano`, `mes`) saem do Parquet; o valor fica no caminho.

## Cuidados de uso

- **Texto livre.** As colunas de texto livre podem ter quebras de linha e aspas; use um leitor de CSV completo.
- **Datas como texto.** As datas chegam como texto.

## Exemplos

Contagem de linhas e de valores distintos de `NUMERO_OCORRENCIA`:

```python
import duckdb

duckdb.sql("""
    SELECT count(*) AS linhas, count(DISTINCT NUMERO_OCORRENCIA) AS distintos
    FROM read_parquet('lake/anac/recomendacoes-seguranca/*.parquet', union_by_name = true)
""").show()
```

## Referências

- Página do conjunto de dados: https://www.anac.gov.br/acesso-a-informacao/dados-abertos/areas-de-atuacao/seguranca-operacional/recomendacoes-de-seguranca-aeronautica
- Servidor de dados abertos da ANAC: https://sistemas.anac.gov.br/dadosabertos/
