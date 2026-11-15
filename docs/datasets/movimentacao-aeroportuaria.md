---
dataset:
  id: movimentacao-aeroportuaria
  fonte: anac
  titulo: "Dados de movimentação aeroportuária"
  resumo: "Movimentos de pouso e decolagem dos aeroportos concedidos e dos de movimentação relevante da Infraero, com aeronave, voo, horários, cabeceira, posição e passageiros, carga e correio."
  orgao: Agência Nacional de Aviação Civil (ANAC)
  pagina_oficial: https://www.anac.gov.br/acesso-a-informacao/dados-abertos/areas-de-atuacao/operador-aeroportuario/dados-de-movimentacao-aeroportuaria
  licenca: "Não informada pela fonte: as páginas de metadados da ANAC não trazem licença (conferido em 2026-11-15)."
  periodicidade: "mensal"
  cobertura: {inicio: "2019-03", fim: "2025-12"}
  unidade: "um movimento (pouso ou decolagem) de uma aeronave em um aeroporto"
  granularidade: {espacial: "aeroporto (código ICAO)", temporal: "movimento (data e hora)"}
  formato_bruto: "CSV mensal `Movimentacoes_Aeroportuarias_<AAAAMM>.csv`, separador ponto e vírgula, um arquivo por mês"
  lake: {estado: convertido, particoes: [ano, mes], chave: [], colunas: 24}
  dados_pessoais: nenhum
  eras: []
  revisado_em: 2026-11-15
  versao_fetcher: 0.9.0
---

# Dados de movimentação aeroportuária

## Resumo

Movimentos de pouso e decolagem dos aeroportos concedidos e dos de movimentação relevante da Infraero, com aeronave, voo, horários, cabeceira, posição e passageiros, carga e correio.

## Ficha técnica

<!-- gerado:ficha -->

| Campo | Valor |
|---|---|
| Dataset | `anac/movimentacao-aeroportuaria` |
| Órgão | Agência Nacional de Aviação Civil (ANAC) |
| Página oficial | https://www.anac.gov.br/acesso-a-informacao/dados-abertos/areas-de-atuacao/operador-aeroportuario/dados-de-movimentacao-aeroportuaria |
| Licença | Não informada pela fonte: as páginas de metadados da ANAC não trazem licença (conferido em 2026-11-15). |
| Periodicidade | mensal |
| Cobertura | 2019-03 a 2025-12 |
| Unidade (uma linha) | um movimento (pouso ou decolagem) de uma aeronave em um aeroporto |
| Granularidade | espacial: aeroporto (código ICAO); temporal: movimento (data e hora) |
| Formato bruto | CSV mensal `Movimentacoes_Aeroportuarias_<AAAAMM>.csv`, separador ponto e vírgula, um arquivo por mês |
| Estado no lake | convertido |
| Partições | `ano`, `mes` |
| Chave | — |
| Colunas | 24 |
| Unidades de medida | — |
| Dados pessoais | nenhum |
| Eras | nenhuma |
| Revisado em | 2026-11-15 |
| Versão do fetcher | 0.9.0 |

## Origem e coleta

- O fetcher baixa um CSV por mês de `Operador Aeroportuário/Dados de Movimentação Aeroportuárias/<ano>/`, de 2019-03 (a publicação só começou nesse mês) a 2025-12, o último publicado no servidor na data da última conferência do catálogo (2026-11-05).
- Só o CSV é catalogado: o JSON mensal tem cerca de 240 MB.
- Conferido em 2026-11-15: 2019-03 (128.508 linhas), 2022-08 (161.821) e 2025-06 (194.271) têm as mesmas 24 colunas.
- Os dados derivam do Relatório de Informações de Movimentação Aeroportuária (RIMA, Resolução ANAC 464/2018, Portaria 1.017/SRA/SIA) e vêm como enviados pelos administradores, sem as correções e interpolações dos indicadores contratuais; podem ser atualizados por eles.

## Conteúdo

- Amostra local de 484.600 linhas em 3 arquivo(s) Parquet, convertida em 2026-11-15 com o fetcher 0.9.0; a amostra não cobre toda a série publicada.
- Em 2025-06, `NR_MOVIMENTO_TIPO` tem `P` (pouso, 97.200) e `D` (decolagem, 97.071); `NR_NATUREZA`, `D` (doméstica, 180.340) e `I` (internacional, 13.931).
- `NR_SERVICE_TYPE` usa os códigos de tipo de serviço da IATA (por exemplo `J` serviço regular normal); a fonte publica a tabela completa.
- O arquivo da fonte também traz `ANO` e `MES`, que o conversor tira do payload porque já estão na partição.

## Variáveis

As descrições vêm da página de metadados do conjunto no portal da ANAC (24 de 24 colunas); as demais ficam como "Sem descrição oficial".

| Coluna no lake | Na fonte | Tipo | Descrição | Unidade / códigos | Período |
|---|---|---|---|---|---|
| `NR_AEROPORTO_REFERENCIA` | `NR_AEROPORTO_REFERENCIA` | texto | Código ICAO do aeroporto de referência dos dados. (campo `NR_AEROPORTO` da documentação) | — | todo |
| `NR_MOVIMENTO_TIPO` | `NR_MOVIMENTO_TIPO` | texto | Tipo de movimento: Pouso ou Decolagem. | valores nas amostras: `D`, `P` | todo |
| `NR_AERONAVE_MARCAS` | `NR_AERONAVE_MARCAS` | texto | Marcas de nacionalidade e matrícula da aeronave. | — | todo |
| `NR_AERONAVE_TIPO` | `NR_AERONAVE_TIPO` | texto | Código ICAO do modelo da aeronave. | — | todo |
| `NR_AERONAVE_OPERADOR` | `NR_AERONAVE_OPERADOR` | texto | Código ICAO do operador da aeronave ou “GERAL" caso o movimento não seja de aviação comercial. | — | todo |
| `NR_VOO_OUTRO_AEROPORTO` | `NR_VOO_OUTRO_AEROPORTO` | texto | Código ICAO do aeroporto de destino em operações de decolagem ou do aeroporto de origem em operações de pouso. | — | todo |
| `NR_VOO_NUMERO` | `NR_VOO_NUMERO` | texto | Número do voo (registro de voo) atribuído ao movimento. | — | todo |
| `NR_SERVICE_TYPE` | `NR_SERVICE_TYPE` | texto | Tipo de serviço (regular; serviço; fretamento; charter; táxi-aéreo; aviação geral; governamental; militar) conforme definido pela IATA (Ver tabela a seguir). | — | todo |
| `NR_NATUREZA` | `NR_NATUREZA` | texto | Natureza da operação: Doméstica ou Internacional. | valores nas amostras: `D`, `I`, `N`, `null` | todo |
| `DT_PREVISTO` | `DT_PREVISTO` | texto | Data prevista (registro de voo) para a realização do movimento. | — | todo |
| `HH_PREVISTO` | `HH_PREVISTO` | texto | Hora prevista (registro de voo) para a realização do movimento. | — | todo |
| `DT_CALCO` | `DT_CALCO` | texto | Data efetiva da realização do calço (pouso) ou descalço (decolagem) da aeronave. | — | todo |
| `HH_CALCO` | `HH_CALCO` | texto | Hora efetiva da realização do calço (pouso) ou descalço (decolagem) da aeronave. | — | todo |
| `DT_TOQUE` | `DT_TOQUE` | texto | Data efetiva da realização do pouso ou decolagem da aeronave, conforme o critério de toque de rodas em pista. | — | todo |
| `HH_TOQUE` | `HH_TOQUE` | texto | Hora efetiva da realização do pouso ou decolagem da aeronave, conforme o critério de toque de rodas em pista. | — | todo |
| `NR_CABECEIRA` | `NR_CABECEIRA` | texto | Identificador da cabeceira de pista de pouso ou decolagem por onde ocorreu o movimento informado. | — | todo |
| `NR_BOX` | `NR_BOX` | texto | Identificador da posição de pátio onde ocorreu o calço (pouso) ou descalço (decolagem) da aeronave. | — | todo |
| `NR_PONTE_CONECTOR_REMOTO` | `NR_PONTE_CONECTOR_REMOTO` | texto | Tipo de instrumento utilizado para o embarque ou desembarque de passageiros (ponte de embarque e desembarque; conector de embarque e desembarque; embarque e desembarque remoto). | valores nas amostras: `0`, `1`, `2`, `3`, `4` | todo |
| `NR_TERMINAL` | `NR_TERMINAL` | texto | Identificador do terminal de passageiros utilizado para o embarque ou desembarque de passageiros. | — | todo |
| `QT_PAX_LOCAL` | `QT_PAX_LOCAL` | texto | Quantidade de passageiros embarcados como origem (decolagem) ou desembarcados como destino (pouso). | — | todo |
| `QT_PAX_CONEXAO_DOMESTICO` | `QT_PAX_CONEXAO_DOMESTICO` | texto | Quantidade de passageiros embarcados provenientes de conexão doméstica (decolagem) ou desembarcados para conexão doméstica (pouso). | — | todo |
| `QT_PAX_CONEXAO_INTERNACIONAL` | `QT_PAX_CONEXAO_INTERNACIONAL` | texto | Quantidade de passageiros embarcados provenientes de conexão internacional (decolagem) ou desembarcados para conexão internacional (pouso). | — | todo |
| `QT_CORREIO` | `QT_CORREIO` | texto | Quantidade embarcada (decolagem) ou desembarcada (pouso) de correspondências e outros objetos confiados pelas administrações postais à empresa aérea, expresso em quilogramas. | — | todo |
| `QT_CARGA` | `QT_CARGA` | texto | Quantidade embarcada (decolagem) ou desembarcada (pouso) de todos bens transportados na aeronave, expressa em quilogramas, excluindo correio, provisões de bordo, bagagens de mão e bagagens despachadas. Descrição dos códigos Service Type (Como definido pela IATA) | — | todo |
| `ano` | — (partição) | texto | Partição do lake: ano do arquivo de origem, tirado do nome do arquivo. | — | todo |
| `mes` | — (partição) | texto | Partição do lake: mês do arquivo de origem, tirado do nome do arquivo. | — | todo |

## No lake

- Dataset `anac/movimentacao-aeroportuaria`, particionado por `ano`, `mes`; um Parquet por arquivo de origem.
- O conversor escolhe um arquivo por conteúdo (CSV antes de JSON antes de XLS, salvo grupos que preferem JSON) e lê todas as colunas como texto, exceto onde o JSON traz números.
- Colunas que repetem a partição (`ano`, `mes`) saem do Parquet; o valor fica no caminho.

## Cuidados de uso

- **Tudo é texto**, inclusive datas, horas e quantidades; converta antes de calcular.
- **Dados do administrador.** A fonte avisa que os dados são os enviados pelos administradores, sem correções, e que podem ser atualizados por eles.
- **Cobertura.** Só aeroportos sob concessão federal e os de movimentação relevante da Infraero.

## Exemplos

Linhas por mês de partição:

```python
import duckdb

duckdb.sql("""
    SELECT ano, mes, count(*) AS linhas
    FROM read_parquet('lake/anac/movimentacao-aeroportuaria/**/*.parquet', hive_partitioning = true, union_by_name = true)
    GROUP BY ALL ORDER BY ano, mes
""").show()
```

## Referências

- Página do conjunto de dados: https://www.anac.gov.br/acesso-a-informacao/dados-abertos/areas-de-atuacao/operador-aeroportuario/dados-de-movimentacao-aeroportuaria
- Servidor de dados abertos da ANAC: https://sistemas.anac.gov.br/dadosabertos/
