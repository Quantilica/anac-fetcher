---
dataset:
  id: aero-lista-privados
  fonte: anac
  titulo: "Aeródromos privados: lista"
  resumo: "Lista de aeródromos privados registrados na ANAC, com código OACI, CIAD, localização, operação e pistas."
  orgao: Agência Nacional de Aviação Civil (ANAC)
  pagina_oficial: https://www.anac.gov.br/acesso-a-informacao/dados-abertos/areas-de-atuacao/aerodromos/lista-de-aerodromos-privados-v2
  licenca: "Não informada pela fonte: as páginas de metadados da ANAC não trazem licença (conferido em 2026-11-15)."
  periodicidade: "aproximadamente a cada 40 dias"
  cobertura: {inicio: "2026-11", fim: "em-curso"}
  unidade: "um registro do cadastro de aeródromos vigente"
  granularidade: {espacial: "Brasil (aeródromo)", temporal: "cadastro vigente (sem série)"}
  formato_bruto: "CSV (e JSON e XLS) `AerodromosPrivados`, separador ponto e vírgula"
  lake: {estado: convertido, particoes: [], chave: [CIAD], colunas: 24}
  dados_pessoais: nenhum
  eras: []
  revisado_em: 2026-11-15
  versao_fetcher: 0.9.0
---

# Aeródromos privados: lista

## Resumo

Lista de aeródromos privados registrados na ANAC, com código OACI, CIAD, localização, operação e pistas. Por ser um conjunto sem série, a cobertura registra a data da coleta.

## Ficha técnica

<!-- gerado:ficha -->

| Campo | Valor |
|---|---|
| Dataset | `anac/aero-lista-privados` |
| Órgão | Agência Nacional de Aviação Civil (ANAC) |
| Página oficial | https://www.anac.gov.br/acesso-a-informacao/dados-abertos/areas-de-atuacao/aerodromos/lista-de-aerodromos-privados-v2 |
| Licença | Não informada pela fonte: as páginas de metadados da ANAC não trazem licença (conferido em 2026-11-15). |
| Periodicidade | aproximadamente a cada 40 dias |
| Cobertura | 2026-11 a em-curso |
| Unidade (uma linha) | um registro do cadastro de aeródromos vigente |
| Granularidade | espacial: Brasil (aeródromo); temporal: cadastro vigente (sem série) |
| Formato bruto | CSV (e JSON e XLS) `AerodromosPrivados`, separador ponto e vírgula |
| Estado no lake | convertido |
| Partições | — |
| Chave | `CIAD` |
| Colunas | 24 |
| Unidades de medida | — |
| Dados pessoais | nenhum |
| Eras | nenhuma |
| Revisado em | 2026-11-15 |
| Versão do fetcher | 0.9.0 |

## Origem e coleta

- O fetcher baixa o arquivo estático do diretório `Aerodromos/` do servidor de dados abertos da ANAC; o servidor sobrescreve o arquivo a cada atualização, sem versões anteriores.
- Conferido em 2026-11-15: 3.945 linhas e 24 colunas.

## Conteúdo

- Amostra local de 3.945 linhas em 1 arquivo(s) Parquet, convertida em 2026-11-15 com o fetcher 0.9.0; a amostra não cobre toda a série publicada.

## Variáveis

As descrições vêm da página de metadados do conjunto no portal da ANAC (22 de 24 colunas); as demais ficam como "Sem descrição oficial".

| Coluna no lake | Na fonte | Tipo | Descrição | Unidade / códigos | Período |
|---|---|---|---|---|---|
| `Código OACI` | `Código OACI` | texto | Código de 4 letras utilizado internacionalmente para identificação de um aeródromo, conforme regras da Organização de Aviação Civil Internacional (OACI). No Brasil, são utilizados os códigos que iniciam com as letras SB, SD, SI, SJ, SN, SS e SW. | — | todo |
| `CIAD` | `CIAD` | texto | O Código de Identificação do Aeródromo se trata de um identificador único de aeródromos civis, e é formado pela junção de dois caracteres e quatro dígitos, sendo que os caracteres são referentes à unidade da federação onde o aeródromo se localiza e os dígitos são atribuídos de forma sequencial (formato UF0000). | — | todo |
| `Nome` | `Nome` | texto | Denominação do aeródromo. | — | todo |
| `Município` | `Município` | texto | Município onde se localiza o aeródromo, considerando as coordenadas de referência do mesmo. | — | todo |
| `UF` | `UF` | texto | Unidade da federação do município onde se localiza o aeródromo. | — | todo |
| `Longitude` | `Longitude` | texto | Longitude do ponto de referência do aeródromo. A coordenada geográfica é fornecida em graus, minutos e segundos, o sistema de referência é WGS-84. | — | todo |
| `Latitude` | `Latitude` | texto | Latitude do ponto de referência do aeródromo. A coordenada geográfica é fornecida em graus, minutos e segundos, o sistema de referência é WGS-84. | — | todo |
| `Altitude` | `Altitude` | texto | Altitude do ponto de referência mais elevado na área de pouso, em metros. | — | todo |
| `Operação Diurna` | `Operação Diurna` | texto | Tipo de operação do período diurno para o qual o aeródromo está habilitado, considerando as regras de voo (VFR – Visual, IFR – Instrumento). | valores nas amostras: `VFR`, `VFR / IFR` | todo |
| `Operação Noturna` | `Operação Noturna` | texto | Tipo de operação do período noturno para o qual o aeródromo está habilitado, considerando as regras de voo (VFR – Visual, IFR – Instrumento). | valores nas amostras: `Sem Operação`, `VFR`, `VFR / IFR` | todo |
| `Designação 1` | `Designação 1` | texto | Identificação de cada uma das cabeceiras da primeira pista de pouso e decolagem, que é definida conforme orientação magnética da pista. | — | todo |
| `Comprimento 1` | `Comprimento 1` | texto | Comprimento da primeira pista de pouso e decolagem, considerando a porção desta disponível para passagem trânsito das aeronaves em condições normais. | — | todo |
| `Largura 1` | `Largura 1` | texto | Largura da primeira pista de pouso e decolagem, considerando a distância lateral na qual uma aeronave pode transitar em condições normais de operação. | — | todo |
| `Resistência 1` | `Resistência 1` | texto | Capacidade de suporte da superfície da primeira pista de pouso e decolagem, que é referência para que um piloto ou operador defina se a pista é adequada para a operação de sua aeronave. A resistência de pavimentos destinados a aeronaves com peso de rampa superior a 5.700 kg deve ser divulgada utilizando-se o método ACN-PCN; | — | todo |
| `Superfície 1` | `Superfície 1` | texto | Tipo de material da superfície da primeira pista de pouso e decolagem. | — | todo |
| `Designação 2` | `Designação 2` | texto | Identificação de cada uma das cabeceiras da segunda pista de pouso e decolagem, que é definida conforme orientação magnética da pista. | — | todo |
| `Comprimento 2` | `Comprimento 2` | texto | Comprimento da segunda pista de pouso e decolagem, considerando a porção desta disponível para passagem trânsito das aeronaves em condições normais. | — | todo |
| `Largura 2` | `Largura 2` | texto | Largura da segunda pista de pouso e decolagem, considerando a distância lateral na qual uma aeronave pode transitar em condições normais de operação. | valores nas amostras: `16,00`, `18,00`, `20,00`, `22,00`, `23,00`, `25,00`, `30,00`, `45,00` | todo |
| `Resistência 2` | `Resistência 2` | texto | Capacidade de suporte da superfície da segunda pista de pouso e decolagem, que é referência para que um piloto ou operador defina se a pista é adequada para a operação de sua aeronave. A resistência de pavimentos destinados a aeronaves com peso de rampa superior a 5.700 kg deve ser divulgada utilizando-se o método ACN-PCN; | — | todo |
| `Superfície 2` | `Superfície 2` | texto | Tipo de material da superfície da segunda pista de pouso e decolagem. | valores nas amostras: `Asfalto`, `Cascalho`, `Grama`, `Piçarra`, `Terra` | todo |
| `Portaria de Registro` | `Portaria de Registro` | texto | Número e ano da última Portaria de cadastro do aeródromo dentro da validade, ou seja, o ato que dá regularidade cadastral à infraestrutura. A Portaria é indicada no formato PAxxxx-yyyy, onde PA representa Portaria ANAC, xxxx é o ano de publicação e yyyy é o número da Portaria. | — | todo |
| `Link Portaria` | `Link Portaria` | texto | Link para acesso direto ao arquivo .pdf da portaria de cadastro do aeródromo. Helidecks | — | todo |
| `LATGEOPOINT` | `LATGEOPOINT` | texto | Sem descrição oficial. | — | todo |
| `LONGEOPOINT` | `LONGEOPOINT` | texto | Sem descrição oficial. | — | todo |

## No lake

- Dataset `anac/aero-lista-privados`, sem partições; um Parquet por arquivo de origem (1 na amostra).
- O conversor escolhe um arquivo por conteúdo (CSV antes de JSON antes de XLS, salvo grupos que preferem JSON) e lê todas as colunas como texto, exceto onde o JSON traz números.
- Colunas que repetem a partição (`ano`, `mes`) saem do Parquet; o valor fica no caminho.

## Cuidados de uso

- **Texto.** Coordenadas, altitude, comprimentos e datas chegam como texto, em formatos mistos (por exemplo, coordenadas decimais com vírgula).
- **Cadastro vigente.** O arquivo é a fotografia atual do cadastro; o lake guarda só a conversão mais recente.

## Exemplos

Contagem de linhas e de valores distintos de `Código OACI`:

```python
import duckdb

duckdb.sql("""
    SELECT count(*) AS linhas, count(DISTINCT "Código OACI") AS distintos
    FROM read_parquet('lake/anac/aero-lista-privados/*.parquet', union_by_name = true)
""").show()
```

## Referências

- Página do conjunto de dados: https://www.anac.gov.br/acesso-a-informacao/dados-abertos/areas-de-atuacao/aerodromos/lista-de-aerodromos-privados-v2
- Servidor de dados abertos da ANAC: https://sistemas.anac.gov.br/dadosabertos/
