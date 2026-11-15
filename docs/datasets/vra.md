---
dataset:
  id: vra
  fonte: anac
  titulo: "Voo Regular Ativo (VRA)"
  resumo: "Etapas de voos regulares do transporte aéreo, uma linha por etapa, com partida e chegada previstas e realizadas e a situação do voo (realizado ou cancelado)."
  orgao: Agência Nacional de Aviação Civil (ANAC)
  pagina_oficial: https://www.anac.gov.br/acesso-a-informacao/dados-abertos/areas-de-atuacao/voos-e-operacoes-aereas/voo-regular-ativo-vra
  licenca: "Não informada pela fonte: as páginas de metadados da ANAC não trazem licença (conferido em 2026-11-15)."
  periodicidade: "mensal; arquivo mensal com cerca de 2 meses de defasagem"
  cobertura: {inicio: "2000-01", fim: "em-curso"}
  unidade: "uma etapa de voo regular prevista para o mês (ou realizada, se não prevista)"
  granularidade: {espacial: "Brasil (etapa entre dois aeródromos)", temporal: "mês"}
  formato_bruto: "CSV (e JSON) mensal `VRA_<AAAA><M>.csv`, separador ponto e vírgula; um arquivo por mês desde 2000-01, exceto 2014-06 e 2014-07"
  lake: {estado: convertido, particoes: [ano, mes], chave: [], colunas: 12}
  dados_pessoais: nenhum
  eras: []
  revisado_em: 2026-11-15
  versao_fetcher: 0.9.0
---

# Voo Regular Ativo (VRA)

## Resumo

Etapas de voos regulares do transporte aéreo, uma linha por etapa, com partida e chegada previstas e realizadas e a situação do voo (realizado ou cancelado).

## Ficha técnica

<!-- gerado:ficha -->

| Campo | Valor |
|---|---|
| Dataset | `anac/vra` |
| Órgão | Agência Nacional de Aviação Civil (ANAC) |
| Página oficial | https://www.anac.gov.br/acesso-a-informacao/dados-abertos/areas-de-atuacao/voos-e-operacoes-aereas/voo-regular-ativo-vra |
| Licença | Não informada pela fonte: as páginas de metadados da ANAC não trazem licença (conferido em 2026-11-15). |
| Periodicidade | mensal; arquivo mensal com cerca de 2 meses de defasagem |
| Cobertura | 2000-01 a em-curso |
| Unidade (uma linha) | uma etapa de voo regular prevista para o mês (ou realizada, se não prevista) |
| Granularidade | espacial: Brasil (etapa entre dois aeródromos); temporal: mês |
| Formato bruto | CSV (e JSON) mensal `VRA_<AAAA><M>.csv`, separador ponto e vírgula; um arquivo por mês desde 2000-01, exceto 2014-06 e 2014-07 |
| Estado no lake | convertido |
| Partições | `ano`, `mes` |
| Chave | — |
| Colunas | 12 |
| Unidades de medida | — |
| Dados pessoais | nenhum |
| Eras | nenhuma |
| Revisado em | 2026-11-15 |
| Versão do fetcher | 0.9.0 |

## Origem e coleta

- O fetcher baixa um arquivo por mês de `Voos e operações aéreas/Voo Regular Ativo (VRA)/<ano>/<mês>/` no servidor de dados abertos da ANAC; o catálogo cobre 2000-01 em diante e pula 2014-06 e 2014-07, meses sem publicação.
- Cada mês sai em CSV e em JSON, com o mesmo conteúdo; o conversor lê o CSV.
- Conferido em 2026-11-15: arquivos de 2000-01, 2010-06, 2017-01 e 2025-06 têm as mesmas 12 colunas.
- Segundo a fonte, o conjunto combina os voos planejados (do conjunto "Registro de serviços aéreos") com os voos realizados e, desde abril de 2020, os voos realizados vêm do conjunto "Dados Estatísticos do Transporte Aéreo"; a situação do voo é derivada do cruzamento das duas bases.

## Conteúdo

- Amostra local de 348.995 linhas em 4 arquivo(s) Parquet, convertida em 2026-11-15 com o fetcher 0.9.0; a amostra não cobre toda a série publicada.
- Cada mês se refere às etapas com decolagem prevista no mês ou, para etapas não previstas, às decolagens realizadas no mês (nota da fonte).
- `Situação Voo` traz `REALIZADO` ou `CANCELADO` nas amostras (2025-06: 78.810 e 2.164 de 80.974 etapas).
- `Código Tipo Linha` na amostra de 2025-06: `N` (65.474), `I` (12.454), `G` (1.761), `C` (1.238) e 47 nulos; a fonte não publica a legenda.
- `Código Justificativa` vale `N/A` em todas as linhas das amostras examinadas.
- Datas e horas vêm como texto `AAAA-MM-DD HH:MM:SS`, às vezes com fração de segundo (`2025-06-07 11:35:00.100000000`), em horário de Brasília (descrição da fonte).

## Variáveis

As descrições vêm da página de metadados do conjunto no portal da ANAC (11 de 12 colunas); as demais ficam como "Sem descrição oficial".

| Coluna no lake | Na fonte | Tipo | Descrição | Unidade / códigos | Período |
|---|---|---|---|---|---|
| `ICAO Empresa Aérea` | `ICAO Empresa Aérea` | texto | Sigla/Designador ICAO Empresa Aérea (campo `Sigla ICAO Empresa Aérea` da documentação) | — | todo |
| `Número Voo` | `Número Voo` | texto | Numeração do voo | — | todo |
| `Código Autorização (DI)` | `Código Autorização (DI)` | texto | Caractere usado para identificar o Dígito Identificador (DI) para cada etapa de voo (campo `Código DI` da documentação) | — | todo |
| `Código Tipo Linha` | `Código Tipo Linha` | texto | Caractere usado para identificar o Tipo de Linha realizada para cada etapa de voo | — | todo |
| `ICAO Aeródromo Origem` | `ICAO Aeródromo Origem` | texto | Sigla/Designador ICAO Aeroporto de Origem (campo `Sigla ICAO Aeroporto Origem` da documentação) | — | todo |
| `ICAO Aeródromo Destino` | `ICAO Aeródromo Destino` | texto | Sigla/Designador ICAO Aeroporto de Destino (campo `Sigla ICAO Aeroporto Destino` da documentação) | — | todo |
| `Partida Prevista` | `Partida Prevista` | texto | Data e horário da partida prevista informada pela empresa aérea, em horário de Brasília | — | todo |
| `Partida Real` | `Partida Real` | texto | Data e horário da partida realizada informada pela empresa aérea, em horário de Brasília | — | todo |
| `Chegada Prevista` | `Chegada Prevista` | texto | Data e horário da chegada prevista informada pela empresa aérea, em horário de Brasília | — | todo |
| `Chegada Real` | `Chegada Real` | texto | Data e horário da chegada realizada, informada pela empresa aérea, em horário de Brasília | — | todo |
| `Situação Voo` | `Situação Voo` | texto | Campo informando a situação do voo: realizado, cancelado ou não informado. (campo `Situação do voo` da documentação) | valores nas amostras: `CANCELADO`, `REALIZADO` | todo |
| `Código Justificativa` | `Código Justificativa` | texto | Sem descrição oficial. | — | todo |
| `ano` | — (partição) | texto | Partição do lake: ano do arquivo de origem, tirado do nome do arquivo. | — | todo |
| `mes` | — (partição) | texto | Partição do lake: mês do arquivo de origem, tirado do nome do arquivo. | — | todo |

## No lake

- Dataset `anac/vra`, particionado por `ano`, `mes`; um Parquet por arquivo de origem.
- O conversor escolhe um arquivo por conteúdo (CSV antes de JSON antes de XLS, salvo grupos que preferem JSON) e lê todas as colunas como texto, exceto onde o JSON traz números.
- Colunas que repetem a partição (`ano`, `mes`) saem do Parquet; o valor fica no caminho.

## Cuidados de uso

- **Tudo é texto.** O conversor mantém todas as colunas como texto; converta datas, `Número Voo` e `Código Autorização (DI)` antes de calcular.
- **Texto `null`.** Nos voos cancelados, `Partida Real` e `Chegada Real` trazem o texto `null` (2.164 linhas em 2025-06), não nulo de verdade; trate-o antes de converter para data.
- **Cobertura do catálogo.** A ANAC publica o mês corrente com defasagem de cerca de 2 meses; o catálogo não gera os 2 últimos meses.

## Exemplos

Linhas por mês de partição:

```python
import duckdb

duckdb.sql("""
    SELECT ano, mes, count(*) AS linhas
    FROM read_parquet('lake/anac/vra/**/*.parquet', hive_partitioning = true, union_by_name = true)
    GROUP BY ALL ORDER BY ano, mes
""").show()
```

## Referências

- Página do conjunto de dados: https://www.anac.gov.br/acesso-a-informacao/dados-abertos/areas-de-atuacao/voos-e-operacoes-aereas/voo-regular-ativo-vra
- Servidor de dados abertos da ANAC: https://sistemas.anac.gov.br/dadosabertos/
