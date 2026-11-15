---
dataset:
  id: dados-estatisticos
  fonte: anac
  titulo: "Dados Estatísticos do Transporte Aéreo"
  resumo: "Série histórica do transporte aéreo por etapa de voo e empresa: passageiros, carga, correio, distância, combustível, assentos e indicadores de oferta e demanda (ASK, RPK, ATK, RTK)."
  orgao: Agência Nacional de Aviação Civil (ANAC)
  pagina_oficial: https://www.anac.gov.br/acesso-a-informacao/dados-abertos/areas-de-atuacao/voos-e-operacoes-aereas/dados-estatisticos-do-transporte-aereo
  licenca: "Não informada pela fonte: as páginas de metadados da ANAC não trazem licença (conferido em 2026-11-15)."
  periodicidade: "mensal; as empresas enviam os dados até o dia 10 do mês seguinte e a ANAC os revisa"
  cobertura: {inicio: "2000-01", fim: "em-curso"}
  unidade: "uma etapa de voo (origem, destino) de uma empresa em um mês, por natureza e grupo de voo"
  granularidade: {espacial: "Brasil e exterior (etapa entre dois aeródromos)", temporal: "mês"}
  formato_bruto: "CSV único `Dados_Estatisticos.csv` com o histórico completo (e JSON por década), separador ponto e vírgula"
  lake: {estado: convertido, particoes: [], chave: [], colunas: 38}
  dados_pessoais: nenhum
  eras: []
  revisado_em: 2026-11-15
  versao_fetcher: 0.9.0
---

# Dados Estatísticos do Transporte Aéreo

## Resumo

Série histórica do transporte aéreo por etapa de voo e empresa: passageiros, carga, correio, distância, combustível, assentos e indicadores de oferta e demanda (ASK, RPK, ATK, RTK).

## Ficha técnica

<!-- gerado:ficha -->

| Campo | Valor |
|---|---|
| Dataset | `anac/dados-estatisticos` |
| Órgão | Agência Nacional de Aviação Civil (ANAC) |
| Página oficial | https://www.anac.gov.br/acesso-a-informacao/dados-abertos/areas-de-atuacao/voos-e-operacoes-aereas/dados-estatisticos-do-transporte-aereo |
| Licença | Não informada pela fonte: as páginas de metadados da ANAC não trazem licença (conferido em 2026-11-15). |
| Periodicidade | mensal; as empresas enviam os dados até o dia 10 do mês seguinte e a ANAC os revisa |
| Cobertura | 2000-01 a em-curso |
| Unidade (uma linha) | uma etapa de voo (origem, destino) de uma empresa em um mês, por natureza e grupo de voo |
| Granularidade | espacial: Brasil e exterior (etapa entre dois aeródromos); temporal: mês |
| Formato bruto | CSV único `Dados_Estatisticos.csv` com o histórico completo (e JSON por década), separador ponto e vírgula |
| Estado no lake | convertido |
| Partições | — |
| Chave | — |
| Colunas | 38 |
| Unidades de medida | — |
| Dados pessoais | nenhum |
| Eras | nenhuma |
| Revisado em | 2026-11-15 |
| Versão do fetcher | 0.9.0 |

## Origem e coleta

- O fetcher baixa `Dados_Estatisticos.csv` (cerca de 360 MB) e três arquivos JSON por década (2000 a 2010, 2011 a 2020 e 2021 a 2030); o conversor lê só o CSV.
- O servidor sobrescreve o arquivo a cada atualização, sem versões anteriores.
- Conferido em 2026-11-15: a documentação aqui vem do cabeçalho do CSV e de uma amostra local dos primeiros 6 MB (19.613 linhas, todas de 2000-01); as linhas posteriores não foram examinadas.
- A fonte regulamenta o envio pela Resolução ANAC 191/2011 e pelas Portarias 1.189 e 1.190/SRE/2011, e avisa que os dados estão sujeitos a revisões, correções e alterações.

## Conteúdo

- Amostra local de 19.613 linhas em 1 arquivo(s) Parquet, convertida em 2026-11-15 com o fetcher 0.9.0; a amostra não cobre toda a série publicada.
- Cada linha é uma etapa básica (flight stage) de uma empresa, com aeroporto de origem e de destino e variáveis de transporte (passageiros, carga, correio, bagagem) e de operação (distância, horas, combustível, decolagens, assentos, payload).
- Na amostra, `NATUREZA` vale `DOMÉSTICA` (15.826) ou `INTERNACIONAL` (3.787); `GRUPO_DE_VOO` vale `REGULAR` (13.486), `NÃO REGULAR` (5.003), `IMPRODUTIVO` (1.123) ou nulo (1); `EMPRESA_NACIONALIDADE` vale `BRASILEIRA` (16.086) ou `ESTRANGEIRA` (3.527).
- Os aeroportos de origem e de destino vêm com sigla, nome, UF, região, país e continente; as colunas de origem ficam nulas em 316 linhas da amostra, todas de empresas estrangeiras.

## Variáveis

As descrições vêm da página de metadados do conjunto no portal da ANAC (26 de 38 colunas); as demais ficam como "Sem descrição oficial".

| Coluna no lake | Na fonte | Tipo | Descrição | Unidade / códigos | Período |
|---|---|---|---|---|---|
| `EMPRESA_SIGLA` | `EMPRESA_SIGLA` | texto | Empresa Aérea responsável por operar as etapas (sigla); corresponde ao campo EMPRESA (SIGLA). | — | todo |
| `EMPRESA_NOME` | `EMPRESA_NOME` | texto | Empresa Aérea responsável por operar as etapas (nome); corresponde ao campo EMPRESA (NOME). | — | todo |
| `EMPRESA_NACIONALIDADE` | `EMPRESA_NACIONALIDADE` | texto | Empresa Aérea responsável por operar as etapas (nacionalidade); corresponde ao campo EMPRESA (NACIONALIDADE). | valores nas amostras: `BRASILEIRA`, `ESTRANGEIRA` | todo |
| `ANO` | `ANO` | texto | Ano da data prevista para o início da primeira etapa de cada voo (campo "Ano e Mês"). | valores nas amostras: `2000` | todo |
| `MES` | `MES` | texto | Mês da data prevista para o início da primeira etapa de cada voo (campo "Ano e Mês"). | — | todo |
| `AEROPORTO_DE_ORIGEM_SIGLA` | `AEROPORTO_DE_ORIGEM_SIGLA` | texto | Sem descrição oficial. | — | todo |
| `AEROPORTO_DE_ORIGEM_NOME` | `AEROPORTO_DE_ORIGEM_NOME` | texto | Sem descrição oficial. | — | todo |
| `AEROPORTO_DE_ORIGEM_UF` | `AEROPORTO_DE_ORIGEM_UF` | texto | Sem descrição oficial. | — | todo |
| `AEROPORTO_DE_ORIGEM_REGIAO` | `AEROPORTO_DE_ORIGEM_REGIAO` | texto | Sem descrição oficial. | valores nas amostras: `CENTRO-OESTE`, `NORDESTE`, `NORTE`, `SUDESTE`, `SUL` | todo |
| `AEROPORTO_DE_ORIGEM_PAIS` | `AEROPORTO_DE_ORIGEM_PAIS` | texto | Sem descrição oficial. | — | todo |
| `AEROPORTO_DE_ORIGEM_CONTINENTE` | `AEROPORTO_DE_ORIGEM_CONTINENTE` | texto | Sem descrição oficial. | valores nas amostras: `AMÉRICA CENTRAL`, `AMÉRICA DO NORTE`, `AMÉRICA DO SUL`, `EUROPA`, `NÃO IDENTIFICADO`, `ÁFRICA`, `ÁSIA` | todo |
| `AEROPORTO_DE_DESTINO_SIGLA` | `AEROPORTO_DE_DESTINO_SIGLA` | texto | Sem descrição oficial. | — | todo |
| `AEROPORTO_DE_DESTINO_NOME` | `AEROPORTO_DE_DESTINO_NOME` | texto | Sem descrição oficial. | — | todo |
| `AEROPORTO_DE_DESTINO_UF` | `AEROPORTO_DE_DESTINO_UF` | texto | Sem descrição oficial. | — | todo |
| `AEROPORTO_DE_DESTINO_REGIAO` | `AEROPORTO_DE_DESTINO_REGIAO` | texto | Sem descrição oficial. | valores nas amostras: `CENTRO-OESTE`, `NORDESTE`, `NORTE`, `SUDESTE`, `SUL` | todo |
| `AEROPORTO_DE_DESTINO_PAIS` | `AEROPORTO_DE_DESTINO_PAIS` | texto | Sem descrição oficial. | — | todo |
| `AEROPORTO_DE_DESTINO_CONTINENTE` | `AEROPORTO_DE_DESTINO_CONTINENTE` | texto | Sem descrição oficial. | valores nas amostras: `AMÉRICA CENTRAL`, `AMÉRICA DO NORTE`, `AMÉRICA DO SUL`, `EUROPA`, `NÃO IDENTIFICADO`, `ÁFRICA`, `ÁSIA` | todo |
| `NATUREZA` | `NATUREZA` | texto | Natureza das etapas: "Doméstico" se pouso e decolagem ocorrem no Brasil com empresa brasileira, "Internacional" caso contrário (campo "Natureza do Voo"). | valores nas amostras: `DOMÉSTICA`, `INTERNACIONAL` | todo |
| `GRUPO_DE_VOO` | `GRUPO_DE_VOO` | texto | Tipo de operação das etapas: improdutivas, regulares ou não regulares (campo "Tipo de Voo"). | valores nas amostras: `IMPRODUTIVO`, `NÃO REGULAR`, `REGULAR` | todo |
| `PASSAGEIROS_PAGOS` | `PASSAGEIROS_PAGOS` | texto | Passageiros que ocupam assentos comercializados ao público e geram receita à empresa aérea. | — | todo |
| `PASSAGEIROS_GRATIS` | `PASSAGEIROS_GRATIS` | texto | Passageiros que ocupam assentos comercializados ao público mas não geram receita à empresa aérea. | — | todo |
| `CARGA_PAGA_KG` | `CARGA_PAGA_KG` | texto | Quantidade total, em quilogramas, de bens transportados (exceto correio e bagagem) que geraram receita direta ou indireta (campo "Carga Paga"). | — | todo |
| `CARGA_GRATIS_KG` | `CARGA_GRATIS_KG` | texto | Quantidade total, em quilogramas, de bens transportados (exceto correio e bagagem) que não geraram receita (campo "Carga Grátis"). | — | todo |
| `CORREIO_KG` | `CORREIO_KG` | texto | Quantidade de objetos de rede postal transportados, em quilogramas (campo "Correio"). | — | todo |
| `ASK` | `ASK` | texto | Indicador de oferta (assentos-quilômetro oferecidos), citado na visão geral da fonte; sem definição detalhada na página de metadados. | — | todo |
| `RPK` | `RPK` | texto | Indicador de demanda (passageiros-quilômetro transportados), citado na visão geral da fonte; sem definição detalhada na página de metadados. | — | todo |
| `ATK` | `ATK` | texto | Volume de tonelada-quilômetro oferecida: soma do produto entre o payload (em kg) e a distância das etapas, dividido por 1.000. | — | todo |
| `RTK` | `RTK` | texto | Volume de toneladas-quilômetros transportadas: soma do produto entre os quilogramas carregados pagos (75 kg por passageiro) e a distância das etapas, dividido por 1.000. | — | todo |
| `COMBUSTIVEL_LITROS` | `COMBUSTIVEL_LITROS` | texto | Combustível consumido na etapa, em litros; só existe para empresas brasileiras. | — | todo |
| `DISTANCIA_VOADA_KM` | `DISTANCIA_VOADA_KM` | texto | Distância entre os aeródromos de origem e destino da etapa, em quilômetros, considerando a curvatura da Terra (campo "Distância"). | — | todo |
| `DECOLAGENS` | `DECOLAGENS` | texto | Número de decolagens entre os aeródromos de origem e destino da etapa. | — | todo |
| `CARGA_PAGA_KM` | `CARGA_PAGA_KM` | texto | Volume de carga paga em cada quilômetro: soma do produto entre a carga paga (kg) e a distância das etapas. | — | todo |
| `CARGA_GRATIS_KM` | `CARGA_GRATIS_KM` | texto | Volume de carga grátis em cada quilômetro: soma do produto entre a carga grátis (kg) e a distância das etapas. | — | todo |
| `CORREIO_KM` | `CORREIO_KM` | texto | Volume de correio em cada quilômetro: soma do produto entre o correio (kg) e a distância das etapas. | — | todo |
| `ASSENTOS` | `ASSENTOS` | texto | Número de assentos disponíveis em cada etapa, conforme a configuração da aeronave. | — | todo |
| `PAYLOAD` | `PAYLOAD` | texto | Capacidade total de peso da aeronave, em quilogramas, disponível para passageiros, carga e correio (payload). | — | todo |
| `HORAS_VOADAS` | `HORAS_VOADAS` | texto | Número de horas de voo entre os aeródromos de origem e destino da etapa. | — | todo |
| `BAGAGEM_KG` | `BAGAGEM_KG` | texto | Quantidade total de bagagem despachada, em quilogramas (campo "Bagagem"). | — | todo |

## No lake

- Dataset `anac/dados-estatisticos`, sem partições; um Parquet por arquivo de origem (1 na amostra).
- O conversor escolhe um arquivo por conteúdo (CSV antes de JSON antes de XLS, salvo grupos que preferem JSON) e lê todas as colunas como texto, exceto onde o JSON traz números.
- Colunas que repetem a partição (`ano`, `mes`) saem do Parquet; o valor fica no caminho.

## Cuidados de uso

- **Texto, não número.** Todas as colunas, inclusive `ANO`, `MES` e as quantidades, chegam como texto; converta antes de calcular.
- **Dados revisáveis.** A ANAC revisa o histórico; o lake guarda só o arquivo mais recente.
- **Empresas estrangeiras.** As variáveis RPK, RTK, Carga Paga Km, Carga Grátis Km e Correio Km das empresas estrangeiras são computadas pelas etapas combinadas; ao desagregar por aeroporto ou rota e compará-las com a oferta (ASK, ATK), taxas de aproveitamento (load factor) podem passar de 100% (nota da fonte).
- **Combustível** só existe para empresas brasileiras (nota da fonte).
- **Sem partição.** O conversor grava o arquivo único sem partição por ano e mês, apesar de ser uma série mensal; filtre por `ANO` e `MES`.

## Exemplos

Contagem de linhas e de valores distintos de `EMPRESA_SIGLA`:

```python
import duckdb

duckdb.sql("""
    SELECT count(*) AS linhas, count(DISTINCT EMPRESA_SIGLA) AS distintos
    FROM read_parquet('lake/anac/dados-estatisticos/*.parquet', union_by_name = true)
""").show()
```

## Referências

- Página do conjunto de dados: https://www.anac.gov.br/acesso-a-informacao/dados-abertos/areas-de-atuacao/voos-e-operacoes-aereas/dados-estatisticos-do-transporte-aereo
- Servidor de dados abertos da ANAC: https://sistemas.anac.gov.br/dadosabertos/
