---
dataset:
  id: aero-heliponto-privado
  fonte: anac
  titulo: "Aeródromos privados: helipontos"
  resumo: "Helipontos privados cadastrados, com localização, rampa, formato e dimensões da área de pouso, pavimento, luzes e portaria."
  orgao: Agência Nacional de Aviação Civil (ANAC)
  pagina_oficial: https://www.anac.gov.br/acesso-a-informacao/dados-abertos/areas-de-atuacao/aerodromos/lista-de-aerodromos-privados-v2
  licenca: "Não informada pela fonte: as páginas de metadados da ANAC não trazem licença (conferido em 2026-11-15)."
  periodicidade: "aproximadamente a cada 40 dias"
  cobertura: {inicio: "2026-11", fim: "em-curso"}
  unidade: "um heliponto privado"
  granularidade: {espacial: "Brasil (aeródromo)", temporal: "cadastro vigente (sem série)"}
  formato_bruto: "CSV (e JSON e XLS) `Helipontos`, separador ponto e vírgula, com a primeira linha \"Criado em: AAAA-MM-DD\""
  lake: {estado: parcial, particoes: [], chave: [], colunas: null}
  dados_pessoais: nenhum
  eras: []
  revisado_em: 2026-11-15
  versao_fetcher: 0.9.0
---

# Aeródromos privados: helipontos

## Resumo

Helipontos privados cadastrados, com localização, rampa, formato e dimensões da área de pouso, pavimento, luzes e portaria. Por ser um conjunto sem série, a cobertura registra a data da coleta.

## Ficha técnica

<!-- gerado:ficha -->

| Campo | Valor |
|---|---|
| Dataset | `anac/aero-heliponto-privado` |
| Órgão | Agência Nacional de Aviação Civil (ANAC) |
| Página oficial | https://www.anac.gov.br/acesso-a-informacao/dados-abertos/areas-de-atuacao/aerodromos/lista-de-aerodromos-privados-v2 |
| Licença | Não informada pela fonte: as páginas de metadados da ANAC não trazem licença (conferido em 2026-11-15). |
| Periodicidade | aproximadamente a cada 40 dias |
| Cobertura | 2026-11 a em-curso |
| Unidade (uma linha) | um heliponto privado |
| Granularidade | espacial: Brasil (aeródromo); temporal: cadastro vigente (sem série) |
| Formato bruto | CSV (e JSON e XLS) `Helipontos`, separador ponto e vírgula, com a primeira linha "Criado em: AAAA-MM-DD" |
| Estado no lake | parcial |
| Partições | — |
| Chave | — |
| Colunas | — |
| Unidades de medida | — |
| Dados pessoais | nenhum |
| Eras | nenhuma |
| Revisado em | 2026-11-15 |
| Versão do fetcher | 0.9.0 |

## Origem e coleta

- O fetcher baixa o arquivo estático do diretório `Aerodromos/` do servidor de dados abertos da ANAC; o servidor sobrescreve o arquivo a cada atualização, sem versões anteriores.
- Conferido em 2026-11-15: 1.626 registros e 27 colunas no CSV.

## Conteúdo

- Amostra local de 1.626 linhas em 1 arquivo(s) Parquet, convertida em 2026-11-15 com o fetcher 0.9.0; a amostra não cobre toda a série publicada.

## Variáveis

As descrições vêm da página de metadados do conjunto no portal da ANAC (17 de 27 colunas); as demais ficam como "Sem descrição oficial". **Atenção:** o conversor atual lê este arquivo com uma única coluna (veja Cuidados de uso); a tabela abaixo lista as colunas do cabeçalho real do CSV, que o lake terá quando a leitura for corrigida.

| Coluna no lake | Na fonte | Tipo | Descrição | Unidade / códigos | Período |
|---|---|---|---|---|---|
| `Código OACI` | `Código OACI` | texto | Código de 4 letras utilizado internacionalmente para identificação de um aeródromo, conforme regras da Organização de Aviação Civil Internacional (OACI). No Brasil, são utilizados os códigos que iniciam com as letras SB, SD, SI, SJ, SN, SS e SW. | — | todo |
| `CIAD` | `CIAD` | texto | O Código de Identificação do Aeródromo se trata de um identificador único de aeródromos civis, e é formado pela junção de dois caracteres e quatro dígitos, sendo que os caracteres são referentes à unidade da federação onde o aeródromo se localiza e os dígitos são atribuídos de forma sequencial (formato UF0000). | — | todo |
| `Nome` | `Nome` | texto | Denominação do aeródromo. | — | todo |
| `Município` | `Município` | texto | Município onde se localiza o aeródromo, considerando as coordenadas de referência do mesmo. | — | todo |
| `UF` | `UF` | texto | Unidade da federação do município onde se localiza o aeródromo. | — | todo |
| `Tipo` | `Tipo` | texto | O tipo de área de pouso e decolagem de helicópteros indica se está no nível do solo ou elevada. Área elevada significa que permite o trânsito de pessoas abaixo de sua estrutura ou no entorno imediatamente subjacente à projeção de sua estrutura sobre o solo. | — | todo |
| `LATGEOPOINT` | `LATGEOPOINT` | texto | Sem descrição oficial. | — | todo |
| `LONGEOPOINT` | `LONGEOPOINT` | texto | Sem descrição oficial. | — | todo |
| `Latitude` | `Latitude` | texto | Latitude do ponto de referência do aeródromo. A coordenada geográfica é fornecida em graus, minutos e segundos, o sistema de referência é WGS-84. | — | todo |
| `Longitude` | `Longitude` | texto | Longitude do ponto de referência do aeródromo. A coordenada geográfica é fornecida em graus, minutos e segundos, o sistema de referência é WGS-84. | — | todo |
| `Altitude` | `Altitude` | texto | Altitude do ponto de referência mais elevado na área de pouso, em metros. | — | todo |
| `Operação Diurna` | `Operação Diurna` | texto | Tipo de operação do período diurno para o qual o aeródromo está habilitado, considerando as regras de voo (VFR – Visual, IFR – Instrumento). | — | todo |
| `Operação Noturna` | `Operação Noturna` | texto | Tipo de operação do período noturno para o qual o aeródromo está habilitado, considerando as regras de voo (VFR – Visual, IFR – Instrumento). | — | todo |
| `Rampa de Aproximação` | `Rampa de Aproximação` | texto | Identificação da orientação para pouso e decolagem na área de pouso exclusiva de helicópteros, que é definida conforme orientação magnética da superfície de aproximação, representada por número de dois dígitos, sendo o número inteiro mais próximo de um décimo do azimute magnético. | — | todo |
| `Formato da Área de Pouso` | `Formato da Área de Pouso` | texto | Forma geométrica que representa a área de aproximação final e decolagem de helicópteros (área de pouso). | — | todo |
| `Dimensões` | `Dimensões` | texto | Comprimento e largura da área de aproximação final e decolagem de helicópteros. Deve ser o diâmetro inscrito na área, caso o formato do heliponto seja circular, ou um polígono irregular. | — | todo |
| `Resistência do Pavimento` | `Resistência do Pavimento` | texto | Sem descrição oficial. | — | todo |
| `Superfície` | `Superfície` | texto | Tipo de material da superfície do pavimento da área de pouso e decolagem de helicópteros. | — | todo |
| `Portaria de Registro` | `Portaria de Registro` | texto | Número e ano da última Portaria de cadastro do aeródromo dentro da validade, ou seja, o ato que dá regularidade cadastral à infraestrutura. A Portaria é indicada no formato PAxxxx-yyyy, onde PA representa Portaria ANAC, xxxx é o ano de publicação e yyyy é o número da Portaria. | — | todo |
| `Link Portaria` | `Link Portaria` | texto | Link para acesso direto ao arquivo .pdf da portaria de cadastro do aeródromo. Helidecks | — | todo |
| `Luzes de Aproximação` | `Luzes de Aproximação` | texto | Sem descrição oficial. | — | todo |
| `Luzes de Área de Toque e Elevação Inicial (TLOF)` | `Luzes de Área de Toque e Elevação Inicial (TLOF)` | texto | Sem descrição oficial. | — | todo |
| `Indicador Visual de Rampa de Aproximação` | `Indicador Visual de Rampa de Aproximação` | texto | Sem descrição oficial. | — | todo |
| `Luzes Indicadoras de Área de Aproximação Final de Decolagem (FATO)` | `Luzes Indicadoras de Área de Aproximação Final de Decolagem (FATO)` | texto | Sem descrição oficial. | — | todo |
| `Luzes de Obstáculo` | `Luzes de Obstáculo` | texto | Sem descrição oficial. | — | todo |
| `Luzes de Ponto de Visada de Heliponto` | `Luzes de Ponto de Visada de Heliponto` | texto | Sem descrição oficial. | — | todo |
| `TIPO_USO` | `TIPO_USO` | texto | Sem descrição oficial. | — | todo |

## No lake

- Dataset `anac/aero-heliponto-privado`, sem partições. Estado atual do lake: **parcial**, porque o arquivo sai com uma única coluna.
- O conversor escolhe um arquivo por conteúdo (CSV antes de JSON antes de XLS, salvo grupos que preferem JSON) e lê todas as colunas como texto, exceto onde o JSON traz números.
- Colunas que repetem a partição (`ano`, `mes`) saem do Parquet; o valor fica no caminho.

## Cuidados de uso

- **Texto.** Coordenadas, altitude, comprimentos e datas chegam como texto, em formatos mistos (por exemplo, coordenadas decimais com vírgula).
- **Cadastro vigente.** O arquivo é a fotografia atual do cadastro; o lake guarda só a conversão mais recente.

## Exemplos

Depois que o conversor ler o cabeçalho certo, a contagem por UF será:

```python
import duckdb

duckdb.sql("""
    SELECT UF, count(*) AS helipontos
    FROM read_parquet('lake/anac/aero-heliponto-privado/*.parquet')
    GROUP BY ALL ORDER BY helipontos DESC
""").show()
```

## Referências

- Página do conjunto de dados: https://www.anac.gov.br/acesso-a-informacao/dados-abertos/areas-de-atuacao/aerodromos/lista-de-aerodromos-privados-v2
- Servidor de dados abertos da ANAC: https://sistemas.anac.gov.br/dadosabertos/
