---
dataset:
  id: aero-lista-publicos
  fonte: anac
  titulo: "Aeródromos públicos: lista"
  resumo: "Lista de aeródromos públicos registrados na ANAC, com código OACI, CIAD, localização, operação diurna e noturna, pistas e portaria de registro."
  orgao: Agência Nacional de Aviação Civil (ANAC)
  pagina_oficial: https://www.anac.gov.br/acesso-a-informacao/dados-abertos/areas-de-atuacao/aerodromos/lista-de-aerodromos-publicos
  licenca: "Não informada pela fonte: as páginas de metadados da ANAC não trazem licença (conferido em 2026-11-15)."
  periodicidade: "aproximadamente a cada 40 dias"
  cobertura: {inicio: "2026-11", fim: "em-curso"}
  unidade: "um registro do cadastro de aeródromos vigente"
  granularidade: {espacial: "Brasil (aeródromo)", temporal: "cadastro vigente (sem série)"}
  formato_bruto: "CSV (e JSON e XLS) `AerodromosPublicos`, separador ponto e vírgula"
  lake: {estado: convertido, particoes: [], chave: [CIAD], colunas: 18}
  dados_pessoais: nenhum
  eras: []
  revisado_em: 2026-11-15
  versao_fetcher: 0.9.0
---

# Aeródromos públicos: lista

## Resumo

Lista de aeródromos públicos registrados na ANAC, com código OACI, CIAD, localização, operação diurna e noturna, pistas e portaria de registro. Por ser um conjunto sem série, a cobertura registra a data da coleta.

## Ficha técnica

<!-- gerado:ficha -->

| Campo | Valor |
|---|---|
| Dataset | `anac/aero-lista-publicos` |
| Órgão | Agência Nacional de Aviação Civil (ANAC) |
| Página oficial | https://www.anac.gov.br/acesso-a-informacao/dados-abertos/areas-de-atuacao/aerodromos/lista-de-aerodromos-publicos |
| Licença | Não informada pela fonte: as páginas de metadados da ANAC não trazem licença (conferido em 2026-11-15). |
| Periodicidade | aproximadamente a cada 40 dias |
| Cobertura | 2026-11 a em-curso |
| Unidade (uma linha) | um registro do cadastro de aeródromos vigente |
| Granularidade | espacial: Brasil (aeródromo); temporal: cadastro vigente (sem série) |
| Formato bruto | CSV (e JSON e XLS) `AerodromosPublicos`, separador ponto e vírgula |
| Estado no lake | convertido |
| Partições | — |
| Chave | `CIAD` |
| Colunas | 18 |
| Unidades de medida | — |
| Dados pessoais | nenhum |
| Eras | nenhuma |
| Revisado em | 2026-11-15 |
| Versão do fetcher | 0.9.0 |

## Origem e coleta

- O fetcher baixa o arquivo estático do diretório `Aerodromos/` do servidor de dados abertos da ANAC; o servidor sobrescreve o arquivo a cada atualização, sem versões anteriores.
- Conferido em 2026-11-15: 496 linhas e 18 colunas.

## Conteúdo

- Amostra local de 496 linhas em 1 arquivo(s) Parquet, convertida em 2026-11-15 com o fetcher 0.9.0; a amostra não cobre toda a série publicada.

## Variáveis

As descrições vêm da página de metadados do conjunto no portal da ANAC (16 de 18 colunas); as demais ficam como "Sem descrição oficial".

| Coluna no lake | Na fonte | Tipo | Descrição | Unidade / códigos | Período |
|---|---|---|---|---|---|
| `Código OACI` | `Código OACI` | texto | Código de 4 letras utilizado internacionalmente para identificação de um aeródromo, conforme regras da Organização de Aviação Civil Internacional (OACI). No Brasil, são utilizados os códigos que iniciam com as letras SB, SD, SI, SJ, SN, SS e SW. | — | todo |
| `CIAD` | `CIAD` | texto | O Código de Identificação do Aeródromo se trata de um identificador único de aeródromos civis, e é formado pela junção de dois caracteres e quatro dígitos, sendo que os caracteres são referentes à unidade da federação onde o aeródromo se localiza e os dígitos são atribuídos de forma sequencial (formato UF0000). | — | todo |
| `Nome` | `Nome` | texto | Denominação do aeródromo. | — | todo |
| `Município` | `Município` | texto | Município onde se localiza o aeródromo, considerando as coordenadas de referência do mesmo. | — | todo |
| `UF` | `UF` | texto | Unidade da federação do município onde se localiza o aeródromo. | — | todo |
| `Município Servido` | `Município Servido` | texto | Município principal servido pelo aeródromo. | — | todo |
| `UF Servido` | `UF Servido` | texto | Unidade da federação do município servido. | — | todo |
| `LATGEOPOINT` | `LATGEOPOINT` | texto | Sem descrição oficial. | — | todo |
| `LONGEOPOINT` | `LONGEOPOINT` | texto | Sem descrição oficial. | — | todo |
| `Latitude` | `Latitude` | texto | Latitude do ponto de referência do aeródromo. A coordenada geográfica é fornecida em graus, minutos e segundos, o sistema de referência é WGS-84. | — | todo |
| `Longitude` | `Longitude` | texto | Longitude do ponto de referência do aeródromo. A coordenada geográfica é fornecida em graus, minutos e segundos, o sistema de referência é WGS-84. | — | todo |
| `Altitude` | `Altitude` | texto | Altitude do ponto de referência mais elevado na área de pouso, em metros. | — | todo |
| `Operação Diurna` | `Operação Diurna` | texto | Tipo de operação do período diurno para o qual o aeródromo está habilitado, considerando as regras de voo (VFR – Visual, IFR – Instrumento). | valores nas amostras: `VFR`, `VFR / IFR - CAT I`, `VFR / IFR - CAT II`, `VFR / IFR - CAT III A`, `VFR / IFR Não Precisão` | todo |
| `Operação Noturna` | `Operação Noturna` | texto | Tipo de operação do período noturno para o qual o aeródromo está habilitado, considerando as regras de voo (VFR – Visual, IFR – Instrumento). | valores nas amostras: `IFR Não Precisão`, `Sem Operação`, `VFR`, `VFR / IFR - CAT I`, `VFR / IFR - CAT II`, `VFR / IFR - CAT III A`, `VFR / IFR Não Precisão` | todo |
| `Situação` | `Situação` | texto | Indicação de eventual medida administrativa aplicada pela ANAC ao aeródromo, em geral constituindo-se em algum tipo de restrição operacional. | valores nas amostras: `Cadastrado`, `Interditado` | todo |
| `Validade do Registro` | `Validade do Registro` | texto | Data de validade do cadastro do aeródromo, que pode ser renovada mediante requerimento prévio, desde que estejam mantidas as condições técnicas para as quais o aeródromo foi aberto ao tráfego aéreo. (campo `VALIDADE DO CADASTRO` da documentação) | — | todo |
| `Portaria de Registro` | `Portaria de Registro` | texto | Número e ano da última Portaria de cadastro do aeródromo dentro da validade, ou seja, o ato que dá regularidade cadastral à infraestrutura. A Portaria é indicada no formato PAxxxx-yyyy, onde PA representa Portaria ANAC, xxxx é o ano de publicação e yyyy é o número da Portaria. (campo `PORTARIA DE CADASTRO` da documentação) | — | todo |
| `Link Portaria` | `Link Portaria` | texto | Link para acesso direto ao arquivo .pdf da portaria de cadastro do aeródromo. | — | todo |

## No lake

- Dataset `anac/aero-lista-publicos`, sem partições; um Parquet por arquivo de origem (1 na amostra).
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
    FROM read_parquet('lake/anac/aero-lista-publicos/*.parquet', union_by_name = true)
""").show()
```

## Referências

- Página do conjunto de dados: https://www.anac.gov.br/acesso-a-informacao/dados-abertos/areas-de-atuacao/aerodromos/lista-de-aerodromos-publicos
- Servidor de dados abertos da ANAC: https://sistemas.anac.gov.br/dadosabertos/
