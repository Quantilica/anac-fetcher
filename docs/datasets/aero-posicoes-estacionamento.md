---
dataset:
  id: aero-posicoes-estacionamento
  fonte: anac
  titulo: "Aeródromos públicos: posições de estacionamento"
  resumo: "Posições de estacionamento de aeronaves em aeródromos públicos, com pátio, identificação, aeronave crítica e sistema de orientação."
  orgao: Agência Nacional de Aviação Civil (ANAC)
  pagina_oficial: https://www.anac.gov.br/acesso-a-informacao/dados-abertos/areas-de-atuacao/aerodromos/aerodromos-publicos-posicoes-de-estacionamento
  licenca: "Não informada pela fonte: as páginas de metadados da ANAC não trazem licença (conferido em 2026-11-15)."
  periodicidade: "quinzenal"
  cobertura: {inicio: "2026-11", fim: "em-curso"}
  unidade: "uma posição de estacionamento de aeronaves"
  granularidade: {espacial: "Brasil (aeródromo)", temporal: "cadastro vigente (sem série)"}
  formato_bruto: "JSON em linhas (NDJSON) `pda_aerodromos_publicos_posicoes_estacionamento`; o CSV da fonte vem sem cabeçalho e não é usado"
  lake: {estado: convertido, particoes: [], chave: [], colunas: 9}
  unidades_de_medida:
    id_aerodromo: "sem unidade (identificador)"
    id_pista: "sem unidade (identificador)"
    id_estacionamento_aeronaves_configuracao: "sem unidade (identificador)"
    id_estacionamento_aeronaves_posicao: "sem unidade (identificador)"
  dados_pessoais: nenhum
  eras: []
  revisado_em: 2026-11-15
  versao_fetcher: 0.9.0
---

# Aeródromos públicos: posições de estacionamento

## Resumo

Posições de estacionamento de aeronaves em aeródromos públicos, com pátio, identificação, aeronave crítica e sistema de orientação. Por ser um conjunto sem série, a cobertura registra a data da coleta.

## Ficha técnica

<!-- gerado:ficha -->

| Campo | Valor |
|---|---|
| Dataset | `anac/aero-posicoes-estacionamento` |
| Órgão | Agência Nacional de Aviação Civil (ANAC) |
| Página oficial | https://www.anac.gov.br/acesso-a-informacao/dados-abertos/areas-de-atuacao/aerodromos/aerodromos-publicos-posicoes-de-estacionamento |
| Licença | Não informada pela fonte: as páginas de metadados da ANAC não trazem licença (conferido em 2026-11-15). |
| Periodicidade | quinzenal |
| Cobertura | 2026-11 a em-curso |
| Unidade (uma linha) | uma posição de estacionamento de aeronaves |
| Granularidade | espacial: Brasil (aeródromo); temporal: cadastro vigente (sem série) |
| Formato bruto | JSON em linhas (NDJSON) `pda_aerodromos_publicos_posicoes_estacionamento`; o CSV da fonte vem sem cabeçalho e não é usado |
| Estado no lake | convertido |
| Partições | — |
| Chave | — |
| Colunas | 9 |
| Unidades de medida | `id_aerodromo`: sem unidade (identificador); `id_pista`: sem unidade (identificador); `id_estacionamento_aeronaves_configuracao`: sem unidade (identificador); `id_estacionamento_aeronaves_posicao`: sem unidade (identificador) |
| Dados pessoais | nenhum |
| Eras | nenhuma |
| Revisado em | 2026-11-15 |
| Versão do fetcher | 0.9.0 |

## Origem e coleta

- O fetcher baixa o arquivo estático do diretório `Aerodromos/` do servidor de dados abertos da ANAC; o servidor sobrescreve o arquivo a cada atualização, sem versões anteriores.
- Conferido em 2026-11-15: 8.824 registros e 9 campos no JSON.

## Conteúdo

- Amostra local de 8.824 linhas em 1 arquivo(s) Parquet, convertida em 2026-11-15 com o fetcher 0.9.0; a amostra não cobre toda a série publicada.

## Variáveis

As descrições vêm da página de metadados do conjunto no portal da ANAC (3 de 9 colunas); as demais ficam como "Sem descrição oficial".

| Coluna no lake | Na fonte | Tipo | Descrição | Unidade / códigos | Período |
|---|---|---|---|---|---|
| `MCDA` | `MCDA` | texto | Sem descrição oficial. | valores nas amostras: `Aeródromos` | todo |
| `id_aerodromo` | `id_aerodromo` | inteiro | Sem descrição oficial. | — | todo |
| `nm_sistema_orientacao_estacionamento` | `nm_sistema_orientacao_estacionamento` | texto | Sistema que indica, por auxílios visuais, o posicionamento preciso de uma aeronave no estacionamento. (campo `SISTEMA DE ORIENTAÇÃO DE ESTACIONAMENTO` da documentação) | valores nas amostras: `Não existente` | todo |
| `nm_codigo_referencia` | `nm_codigo_referencia` | texto | Código da aeronave crítica em operação, ou com previsão de operar em um aeródromo, que demande os maiores requisitos em termos de configuração e dimensionamento da posição de estacionamento. (campo `CÓDIGO DE REFERÊNCIA AERONAVE CRÍTICA` da documentação) | — | todo |
| `ConjuntoDado` | `ConjuntoDado` | texto | Sem descrição oficial. | — | todo |
| `id_pista` | `id_pista` | inteiro | Sem descrição oficial. | — | todo |
| `id_estacionamento_aeronaves_configuracao` | `id_estacionamento_aeronaves_configuracao` | inteiro | Sem descrição oficial. | — | todo |
| `id_estacionamento_aeronaves_posicao` | `id_estacionamento_aeronaves_posicao` | inteiro | Sem descrição oficial. | — | todo |
| `nm_identificacao` | `nm_identificacao` | texto | Designação da Posição de Estacionamento de Aeronaves. (campo `IDENTIFICAÇÃO POS ESTACIONAMENTO` da documentação) | — | todo |

## No lake

- Dataset `anac/aero-posicoes-estacionamento`, sem partições; um Parquet por arquivo de origem (1 na amostra).
- O conversor escolhe um arquivo por conteúdo (CSV antes de JSON antes de XLS, salvo grupos que preferem JSON) e lê todas as colunas como texto, exceto onde o JSON traz números.
- Colunas que repetem a partição (`ano`, `mes`) saem do Parquet; o valor fica no caminho.

## Cuidados de uso

- **Texto.** Coordenadas, altitude, comprimentos e datas chegam como texto, em formatos mistos (por exemplo, coordenadas decimais com vírgula).
- **Cadastro vigente.** O arquivo é a fotografia atual do cadastro; o lake guarda só a conversão mais recente.

## Exemplos

Contagem de linhas e de valores distintos de `MCDA`:

```python
import duckdb

duckdb.sql("""
    SELECT count(*) AS linhas, count(DISTINCT MCDA) AS distintos
    FROM read_parquet('lake/anac/aero-posicoes-estacionamento/*.parquet', union_by_name = true)
""").show()
```

## Referências

- Página do conjunto de dados: https://www.anac.gov.br/acesso-a-informacao/dados-abertos/areas-de-atuacao/aerodromos/aerodromos-publicos-posicoes-de-estacionamento
- Servidor de dados abertos da ANAC: https://sistemas.anac.gov.br/dadosabertos/
