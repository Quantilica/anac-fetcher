---
dataset:
  id: aero-helideck
  fonte: anac
  titulo: "Aeródromos privados: helidecks"
  resumo: "Helidecks cadastrados, com código OACI, CIAD, altitude, resistência, maior helicóptero a operar e portaria de registro."
  orgao: Agência Nacional de Aviação Civil (ANAC)
  pagina_oficial: https://www.anac.gov.br/acesso-a-informacao/dados-abertos/areas-de-atuacao/aerodromos/lista-de-aerodromos-privados-v2
  licenca: "Não informada pela fonte: as páginas de metadados da ANAC não trazem licença (conferido em 2026-11-15)."
  periodicidade: "aproximadamente a cada 40 dias"
  cobertura: {inicio: "2026-11", fim: "em-curso"}
  unidade: "um helideck"
  granularidade: {espacial: "Brasil (aeródromo)", temporal: "cadastro vigente (sem série)"}
  formato_bruto: "CSV (e JSON e XLS) `Helidecks`, separador ponto e vírgula"
  lake: {estado: convertido, particoes: [], chave: [CIAD], colunas: 9}
  dados_pessoais: nenhum
  eras: []
  revisado_em: 2026-11-15
  versao_fetcher: 0.9.0
---

# Aeródromos privados: helidecks

## Resumo

Helidecks cadastrados, com código OACI, CIAD, altitude, resistência, maior helicóptero a operar e portaria de registro. Por ser um conjunto sem série, a cobertura registra a data da coleta.

## Ficha técnica

<!-- gerado:ficha -->

| Campo | Valor |
|---|---|
| Dataset | `anac/aero-helideck` |
| Órgão | Agência Nacional de Aviação Civil (ANAC) |
| Página oficial | https://www.anac.gov.br/acesso-a-informacao/dados-abertos/areas-de-atuacao/aerodromos/lista-de-aerodromos-privados-v2 |
| Licença | Não informada pela fonte: as páginas de metadados da ANAC não trazem licença (conferido em 2026-11-15). |
| Periodicidade | aproximadamente a cada 40 dias |
| Cobertura | 2026-11 a em-curso |
| Unidade (uma linha) | um helideck |
| Granularidade | espacial: Brasil (aeródromo); temporal: cadastro vigente (sem série) |
| Formato bruto | CSV (e JSON e XLS) `Helidecks`, separador ponto e vírgula |
| Estado no lake | convertido |
| Partições | — |
| Chave | `CIAD` |
| Colunas | 9 |
| Unidades de medida | — |
| Dados pessoais | nenhum |
| Eras | nenhuma |
| Revisado em | 2026-11-15 |
| Versão do fetcher | 0.9.0 |

## Origem e coleta

- O fetcher baixa o arquivo estático do diretório `Aerodromos/` do servidor de dados abertos da ANAC; o servidor sobrescreve o arquivo a cada atualização, sem versões anteriores.
- Conferido em 2026-11-15: 208 linhas e 9 colunas.

## Conteúdo

- Amostra local de 208 linhas em 1 arquivo(s) Parquet, convertida em 2026-11-15 com o fetcher 0.9.0; a amostra não cobre toda a série publicada.

## Variáveis

As descrições vêm da página de metadados do conjunto no portal da ANAC (9 de 9 colunas); as demais ficam como "Sem descrição oficial".

| Coluna no lake | Na fonte | Tipo | Descrição | Unidade / códigos | Período |
|---|---|---|---|---|---|
| `CÓDIGO OACI` | `CÓDIGO OACI` | texto | Código de 4 letras utilizado internacionalmente para identificação de um aeródromo, conforme regras da Organização de Aviação Civil Internacional (OACI). No Brasil, são utilizados os códigos que iniciam com as letras SB, SD, SI, SJ, SN, SS e SW. | — | todo |
| `CIAD` | `CIAD` | texto | O Código de Identificação do Aeródromo se trata de um identificador único de aeródromos civis, e é formado pela junção de dois caracteres e quatro dígitos, sendo que os caracteres são referentes à unidade da federação onde o aeródromo se localiza e os dígitos são atribuídos de forma sequencial (formato UF0000). | — | todo |
| `NOME` | `NOME` | texto | Denominação do aeródromo. | — | todo |
| `ALTITUDE` | `ALTITUDE` | texto | Altitude do ponto de referência mais elevado na área de pouso, em metros. | — | todo |
| `RESISTÊNCIA` | `RESISTÊNCIA` | texto | Capacidade de suporte da superfície e estrutura do helideck, que é referência para que um piloto ou operador defina se o heliponto é adequado para a operação de seu helicóptero. É notificada pelo peso máximo permitido do helicóptero, em toneladas. | — | todo |
| `COMPRIMENTO DO MAIOR HELICÓPTERO A OPERAR` | `COMPRIMENTO DO MAIOR HELICÓPTERO A OPERAR` | texto | Maior dimensão do maior helicóptero cuja operação é prevista no helideck. Dado apresentado em metros. | — | todo |
| `VALIDADE DO CADASTRO` | `VALIDADE DO CADASTRO` | texto | Data de validade do cadastro do helideck, que pode ser renovada mediante requerimento prévio, desde que estejam mantidas as condições técnicas para as quais o aeródromo foi aberto ao tráfego aéreo. | — | todo |
| `PORTARIA DE REGISTRO` | `PORTARIA DE REGISTRO` | texto | Número e ano da última Portaria de cadastro do aeródromo dentro da validade, ou seja, o ato que dá regularidade cadastral à infraestrutura. A Portaria é indicada no formato PAxxxx-yyyy, onde PA representa Portaria ANAC, xxxx é o ano de publicação e yyyy é o número da Portaria. | — | todo |
| `LINK PORTARIA` | `LINK PORTARIA` | texto | Link para acesso direto ao arquivo .pdf da portaria de cadastro do aeródromo. Helidecks | — | todo |

## No lake

- Dataset `anac/aero-helideck`, sem partições; um Parquet por arquivo de origem (1 na amostra).
- O conversor escolhe um arquivo por conteúdo (CSV antes de JSON antes de XLS, salvo grupos que preferem JSON) e lê todas as colunas como texto, exceto onde o JSON traz números.
- Colunas que repetem a partição (`ano`, `mes`) saem do Parquet; o valor fica no caminho.

## Cuidados de uso

- **Texto.** Coordenadas, altitude, comprimentos e datas chegam como texto, em formatos mistos (por exemplo, coordenadas decimais com vírgula).
- **Cadastro vigente.** O arquivo é a fotografia atual do cadastro; o lake guarda só a conversão mais recente.

## Exemplos

Contagem de linhas e de valores distintos de `CÓDIGO OACI`:

```python
import duckdb

duckdb.sql("""
    SELECT count(*) AS linhas, count(DISTINCT "CÓDIGO OACI") AS distintos
    FROM read_parquet('lake/anac/aero-helideck/*.parquet', union_by_name = true)
""").show()
```

## Referências

- Página do conjunto de dados: https://www.anac.gov.br/acesso-a-informacao/dados-abertos/areas-de-atuacao/aerodromos/lista-de-aerodromos-privados-v2
- Servidor de dados abertos da ANAC: https://sistemas.anac.gov.br/dadosabertos/
