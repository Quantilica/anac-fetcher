---
dataset:
  id: atrasos-cancelamentos
  fonte: anac
  titulo: "Percentuais de atrasos e cancelamentos"
  resumo: "Percentuais mensais de cancelamentos e de atrasos (acima de 30 e de 60 minutos) por empresa, voo e trecho, divulgados nos três anexos da Portaria SAS 3.838/2017."
  orgao: Agência Nacional de Aviação Civil (ANAC)
  pagina_oficial: https://www.anac.gov.br/acesso-a-informacao/dados-abertos/areas-de-atuacao/voos-e-operacoes-aereas/percentuais-de-atrasos-e-cancelamentos
  licenca: "Não informada pela fonte: as páginas de metadados da ANAC não trazem licença (conferido em 2026-11-15)."
  periodicidade: "mensal, com os dados do mês anterior"
  cobertura: {inicio: "2000-01", fim: "em-curso"}
  unidade: "um trecho (origem e destino), de uma empresa e voo no Anexo I, em um mês, com os percentuais do mês"
  granularidade: {espacial: "trecho entre dois aeroportos", temporal: "mês"}
  formato_bruto: "três arquivos por mês (Anexo I, II e III), CSV (e JSON), separador ponto e vírgula"
  lake: {estado: convertido, particoes: [ano, mes], chave: [], colunas: 10}
  dados_pessoais: nenhum
  eras: []
  revisado_em: 2026-11-15
  versao_fetcher: 0.9.0
---

# Percentuais de atrasos e cancelamentos

## Resumo

Percentuais mensais de cancelamentos e de atrasos (acima de 30 e de 60 minutos) por empresa, voo e trecho, divulgados nos três anexos da Portaria SAS 3.838/2017.

## Ficha técnica

<!-- gerado:ficha -->

| Campo | Valor |
|---|---|
| Dataset | `anac/atrasos-cancelamentos` |
| Órgão | Agência Nacional de Aviação Civil (ANAC) |
| Página oficial | https://www.anac.gov.br/acesso-a-informacao/dados-abertos/areas-de-atuacao/voos-e-operacoes-aereas/percentuais-de-atrasos-e-cancelamentos |
| Licença | Não informada pela fonte: as páginas de metadados da ANAC não trazem licença (conferido em 2026-11-15). |
| Periodicidade | mensal, com os dados do mês anterior |
| Cobertura | 2000-01 a em-curso |
| Unidade (uma linha) | um trecho (origem e destino), de uma empresa e voo no Anexo I, em um mês, com os percentuais do mês |
| Granularidade | espacial: trecho entre dois aeroportos; temporal: mês |
| Formato bruto | três arquivos por mês (Anexo I, II e III), CSV (e JSON), separador ponto e vírgula |
| Estado no lake | convertido |
| Partições | `ano`, `mes` |
| Chave | — |
| Colunas | 10 |
| Unidades de medida | — |
| Dados pessoais | nenhum |
| Eras | nenhuma |
| Revisado em | 2026-11-15 |
| Versão do fetcher | 0.9.0 |

## Origem e coleta

- O fetcher baixa, para cada mês, os arquivos `Anexo I`, `Anexo II` e `Anexo III` de `Voos e operações aéreas/Percentuais de atrasos e cancelamentos/<ano>/<mês>/`; o catálogo cobre 2000-01 em diante e pula 2014-06 e 2014-07, que a fonte não publicou (Copa do Mundo, Resolução 316/2014).
- Cada anexo vira um arquivo Parquet próprio na partição do mês, com sufixo `anexo-i`, `anexo-ii` ou `anexo-iii`; os três ficam no mesmo dataset. Os anexos não são juntados: têm esquemas e granularidades diferentes. O arquivo bruto sem sufixo de anexo que versões antigas do fetcher gravaram é cópia exata de um dos anexos e não é convertido.
- Conferido em 2026-11-15: o Anexo I tem 10 colunas; os Anexos II e III têm 9 e 8 colunas em 2000-01, 2017-01, 2019-03 e 2024-10 (sem `N_Voo` e, no III, sem `Empresa_Aerea`), mas 10 colunas nos três anexos em 2022-08.
- A fonte descreve os metadados do Anexo I (Resolução ANAC 218/2012 e Portaria SAS 3.838/2017).

## Conteúdo

- Amostra local de 268.417 linhas em 15 arquivo(s) Parquet, convertida em 2026-11-15 com o fetcher 0.9.0; a amostra não cobre toda a série publicada.
- Amostras locais (linhas por anexo): 2024-10 com 12.841, 1.525 e 1.101 (I, II, III); 2022-08 com 216.411, 7.275 e 5.432; 2019-03 com 7.718, 1.712 e 1.147; 2000-01 com 2.945, 1.715 e 1.009.
- Os percentuais vêm como texto com vírgula decimal e quatro casas (por exemplo `0,0000`).

## Variáveis

As descrições vêm da página de metadados do conjunto no portal da ANAC (10 de 10 colunas); as demais ficam como "Sem descrição oficial".

| Coluna no lake | Na fonte | Tipo | Descrição | Unidade / códigos | Período |
|---|---|---|---|---|---|
| `Empresa_Aerea` | `Empresa_Aerea` | texto | Sigla OACI da empresa seguida do nome da empresa | — | todo |
| `N_Voo` | `N_Voo` | texto | Numeração do voo (campo `Nº Voo` da documentação) | — | todo |
| `Aeroporto_Origem_Designador_OACI` | `Aeroporto_Origem_Designador_OACI` | texto | Sigla OACI do aeroporto de origem | — | todo |
| `Aeroporto_Origem_Nome_UF_Pais ` | `Aeroporto_Origem_Nome_UF_Pais ` | texto | Nome do aeroporto de origem com a respectiva unidade da federação e país | — | todo |
| `Aeroporto_Destino_Designador_OACI` | `Aeroporto_Destino_Designador_OACI` | texto | Sigla OACI do aeroporto de destino | — | todo |
| `Aeroporto_Destino_Nome_UF_Pais` | `Aeroporto_Destino_Nome_UF_Pais` | texto | Nome do aeroporto de destino com a respectiva unidade da federação e país | — | todo |
| `Etapas_Previstas` | `Etapas_Previstas` | texto | Quantidade de etapas previstas para o mês em questão | — | todo |
| `Percentuais_de_Cancelamentos` | `Percentuais_de_Cancelamentos` | texto | Percentual de etapas canceladas em relação às etapas previstas (campo `% de Cancelamentos` da documentação) | — | todo |
| `Percentuais_de_Atrasos_superiores_a_30_minutos` | `Percentuais_de_Atrasos_superiores_a_30_minutos` | texto | Percentual de atrasos superiores a 30 minutos em relação às etapas realizadas (campo `% de Atrasos superiores a 30 minutos` da documentação) | — | todo |
| `Percentuais_de_Atrasos_superiores_a_60_minutos` | `Percentuais_de_Atrasos_superiores_a_60_minutos` | texto | Percentual de atrasos superiores a 60 minutos em relação às etapas realizadas (campo `% de Atrasos superiores a 60 minutos` da documentação) | — | todo |
| `ano` | — (partição) | texto | Partição do lake: ano do arquivo de origem, tirado do nome do arquivo. | — | todo |
| `mes` | — (partição) | texto | Partição do lake: mês do arquivo de origem, tirado do nome do arquivo. | — | todo |

## No lake

- Dataset `anac/atrasos-cancelamentos`, particionado por `ano`, `mes`; um Parquet por anexo e mês (`atrasos-cancelamentos_AAAAMM_anexo-i.parquet`, `..._anexo-ii.parquet`, `..._anexo-iii.parquet`), com a coluna `_origem` (arquivo bruto de origem) e, no rodapé, o sha256 e o número de linhas do arquivo.
- O conversor escolhe um arquivo por conteúdo (CSV antes de JSON antes de XLS, salvo grupos que preferem JSON) e lê todas as colunas como texto, exceto onde o JSON traz números.
- Colunas que repetem a partição (`ano`, `mes`) saem do Parquet; o valor fica no caminho.

## Cuidados de uso

- **Três tabelas em um dataset.** Os anexos têm granularidades diferentes (Anexo I por voo e trecho; II por empresa e trecho; III por trecho); não some linhas entre anexos. Os arquivos Parquet se distinguem pelo sufixo `anexo-*` no nome e pela coluna `_origem`.
- **Esquema varia por anexo e mês.** Anexos II e III não têm `N_Voo`/`Empresa_Aerea` na maioria dos meses, e em 2022-08 os três têm as 10 colunas; ao ler com `union_by_name`, as colunas ausentes ficam nulas.
- **Nome de coluna com espaço no fim.** A coluna `Aeroporto_Origem_Nome_UF_Pais` tem um espaço no fim do nome na fonte, preservado no Parquet. O esquema de referência (`atrasos-cancelamentos.schema.json`) e esta tabela a registram sem o espaço, porque a verificação da documentação aplica `strip` aos nomes; no DuckDB, cite o nome com o espaço.
- **Texto.** Os percentuais e as quantidades são texto; converta antes de calcular.

## Exemplos

Linhas por mês de partição:

```python
import duckdb

duckdb.sql("""
    SELECT ano, mes, count(*) AS linhas
    FROM read_parquet('lake/anac/atrasos-cancelamentos/**/*.parquet', hive_partitioning = true, union_by_name = true)
    GROUP BY ALL ORDER BY ano, mes
""").show()
```

## Referências

- Página do conjunto de dados: https://www.anac.gov.br/acesso-a-informacao/dados-abertos/areas-de-atuacao/voos-e-operacoes-aereas/percentuais-de-atrasos-e-cancelamentos
- Servidor de dados abertos da ANAC: https://sistemas.anac.gov.br/dadosabertos/
