---
dataset:
  id: aero-caracteristicas
  fonte: anac
  titulo: "Aeródromos públicos: características gerais"
  resumo: "Características gerais de aeródromos públicos: identificação, localização, uso, duas pistas, classes RBAC, certificação e restrições."
  orgao: Agência Nacional de Aviação Civil (ANAC)
  pagina_oficial: https://www.anac.gov.br/acesso-a-informacao/dados-abertos/areas-de-atuacao/aerodromos/aerodromos-publicos-caracteristicas-gerais
  licenca: "Não informada pela fonte: as páginas de metadados da ANAC não trazem licença (conferido em 2026-11-15)."
  periodicidade: "quinzenal"
  cobertura: {inicio: "2026-11", fim: "em-curso"}
  unidade: "um registro do cadastro de aeródromos vigente"
  granularidade: {espacial: "Brasil (aeródromo)", temporal: "cadastro vigente (sem série)"}
  formato_bruto: "CSV `pda_aerodromos_publicos_caracteristicas_gerais`, separador ponto e vírgula"
  lake: {estado: convertido, particoes: [], chave: [], colunas: 50}
  dados_pessoais: nenhum
  eras: []
  revisado_em: 2026-11-15
  versao_fetcher: 0.9.0
---

# Aeródromos públicos: características gerais

## Resumo

Características gerais de aeródromos públicos: identificação, localização, uso, duas pistas, classes RBAC, certificação e restrições. Por ser um conjunto sem série, a cobertura registra a data da coleta.

## Ficha técnica

<!-- gerado:ficha -->

| Campo | Valor |
|---|---|
| Dataset | `anac/aero-caracteristicas` |
| Órgão | Agência Nacional de Aviação Civil (ANAC) |
| Página oficial | https://www.anac.gov.br/acesso-a-informacao/dados-abertos/areas-de-atuacao/aerodromos/aerodromos-publicos-caracteristicas-gerais |
| Licença | Não informada pela fonte: as páginas de metadados da ANAC não trazem licença (conferido em 2026-11-15). |
| Periodicidade | quinzenal |
| Cobertura | 2026-11 a em-curso |
| Unidade (uma linha) | um registro do cadastro de aeródromos vigente |
| Granularidade | espacial: Brasil (aeródromo); temporal: cadastro vigente (sem série) |
| Formato bruto | CSV `pda_aerodromos_publicos_caracteristicas_gerais`, separador ponto e vírgula |
| Estado no lake | convertido |
| Partições | — |
| Chave | — |
| Colunas | 50 |
| Unidades de medida | — |
| Dados pessoais | nenhum |
| Eras | nenhuma |
| Revisado em | 2026-11-15 |
| Versão do fetcher | 0.9.0 |

## Origem e coleta

- O fetcher baixa o arquivo estático do diretório `Aerodromos/` do servidor de dados abertos da ANAC; o servidor sobrescreve o arquivo a cada atualização, sem versões anteriores.
- Conferido em 2026-11-15: 6.881 linhas e 50 colunas (6.852 CIAD distintos e 22 vazios), do arquivo de 2023-09 que o servidor ainda publica.
- `Tipo de Cadastro` na amostra: `Aeródromo em Terras Brasileiras` (6.655), `Aeródromo em Águas Brasileiras` (204) e `Aeródromo Estrangeiro` (22).

## Conteúdo

- Amostra local de 6.881 linhas em 1 arquivo(s) Parquet, convertida em 2026-11-15 com o fetcher 0.9.0; a amostra não cobre toda a série publicada.

## Variáveis

As descrições vêm da página de metadados do conjunto no portal da ANAC (10 de 50 colunas); as demais ficam como "Sem descrição oficial".

| Coluna no lake | Na fonte | Tipo | Descrição | Unidade / códigos | Período |
|---|---|---|---|---|---|
| `Id do Aeródromo` | `Id do Aeródromo` | texto | Sem descrição oficial. | — | todo |
| `CIAD` | `CIAD` | texto | O CIAD (Código de Identificação do Aeródromo), que é definido pela Agência no caso dos aeródromos civis, é um código formado pela junção dos dois caracteres referentes à unidade da federação onde o aeródromo se localiza e um número sequencial de 4 dígitos (formato UF0000). | — | todo |
| `Código OACI` | `Código OACI` | texto | Código de 4 letras utilizado internacionalmente para identificação de um aeródromo, conforme regras da Organização de Aviação Civil Internacional (OACI). No Brasil, são utilizados os códigos que iniciam com as letras SB, SD, SI, SJ, SN, SS e SW | — | todo |
| `Id to Tipo de Uso` | `Id to Tipo de Uso` | texto | Sem descrição oficial. | valores nas amostras: `1`, `2` | todo |
| `Tipo de Uso` | `Tipo de Uso` | texto | Sem descrição oficial. | valores nas amostras: `Privado`, `Público` | todo |
| `Nome` | `Nome` | texto | Denominação do aeródromo | — | todo |
| `Município` | `Município` | texto | Município onde se localiza o aeródromo, considerando as coordenadas de referência do mesmo. Município onde se localiza o aeródromo, considerando as coordenadas de referência do mesmo. Município onde se localiza o aeródromo, considerando as coordenadas de referência do mesmo. | — | todo |
| `UF` | `UF` | texto | Unidade da federação do município onde se localiza o aeródromo. Unidade da federação do município onde se localiza o aeródromo. Unidade da federação do município onde se localiza o aeródromo. | — | todo |
| `País` | `País` | texto | Sem descrição oficial. | — | todo |
| `Município Servido` | `Município Servido` | texto | Sem descrição oficial. | — | todo |
| `UF Servido` | `UF Servido` | texto | Sem descrição oficial. | — | todo |
| `Latitude` | `Latitude` | texto | Latitude do ponto de referência do aeródromo. A coordenada geográfica é fornecida em graus, minutos e segundos, o sistema de referência é WGS-84 | — | todo |
| `Longitude` | `Longitude` | texto | Longitude do ponto de referência do aeródromo. A coordenada geográfica é fornecida em graus, minutos e segundos, o sistema de referência é WGS-84 | — | todo |
| `Altitude` | `Altitude` | texto | Altitude do ponto de referência mais elevado na área de pouso. Dado apresentado em metros. (campo `ELEVAÇÃO` da documentação) | — | todo |
| `Operação Diurna` | `Operação Diurna` | texto | Sem descrição oficial. | valores nas amostras: `VFR`, `VFR / IFR` | todo |
| `Operação Noturna` | `Operação Noturna` | texto | Sem descrição oficial. | valores nas amostras: `IFR`, `Sem Operação`, `VFR`, `VFR / IFR` | todo |
| `Id da Pista 1` | `Id da Pista 1` | texto | Sem descrição oficial. | — | todo |
| `Designação (Pista 1)` | `Designação (Pista 1)` | texto | Sem descrição oficial. | — | todo |
| `Comprimento (Pista 1)` | `Comprimento (Pista 1)` | texto | Sem descrição oficial. | — | todo |
| `Largura (Pista 1)` | `Largura (Pista 1)` | texto | Sem descrição oficial. | — | todo |
| `Resistência (Pista 1)` | `Resistência (Pista 1)` | texto | Sem descrição oficial. | — | todo |
| `Superfície (Pista 1)` | `Superfície (Pista 1)` | texto | Sem descrição oficial. | — | todo |
| `Aeronave Crítica (Pista 1)` | `Aeronave Crítica (Pista 1)` | texto | Sem descrição oficial. | valores nas amostras: `2B`, `2C`, `3C`, `4C`, `4D`, `4E` | todo |
| `Tipo Operação por Cabeceira (Pista 1)` | `Tipo Operação por Cabeceira (Pista 1)` | texto | Sem descrição oficial. | — | todo |
| `Luzes de Eixo de Pista (Pista 1)` | `Luzes de Eixo de Pista (Pista 1)` | texto | Sem descrição oficial. | valores nas amostras: `0`, `1` | todo |
| `Luzes de Borda de Pista (Pista 1)` | `Luzes de Borda de Pista (Pista 1)` | texto | Sem descrição oficial. | valores nas amostras: `0`, `1` | todo |
| `Id da Pista 2` | `Id da Pista 2` | texto | Sem descrição oficial. | — | todo |
| `Designação (Pista 2)` | `Designação (Pista 2)` | texto | Sem descrição oficial. | — | todo |
| `Comprimento (Pista 2)` | `Comprimento (Pista 2)` | texto | Sem descrição oficial. | — | todo |
| `Largura (Pista 2)` | `Largura (Pista 2)` | texto | Sem descrição oficial. | — | todo |
| `Resistência (Pista 2)` | `Resistência (Pista 2)` | texto | Sem descrição oficial. | — | todo |
| `Superfície (Pista 2)` | `Superfície (Pista 2)` | texto | Sem descrição oficial. | valores nas amostras: `Asfalto`, `Cascalho`, `Grama`, `Piçarra`, `Terra` | todo |
| `Aeronave Crítica (Pista 2)` | `Aeronave Crítica (Pista 2)` | texto | Sem descrição oficial. | valores nas amostras: `3C`, `4C`, `4D`, `4E` | todo |
| `Tipo Operação por Cabeceira (Pista 2)` | `Tipo Operação por Cabeceira (Pista 2)` | texto | Sem descrição oficial. | — | todo |
| `Luzes de Eixo de Pista (Pista 2)` | `Luzes de Eixo de Pista (Pista 2)` | texto | Sem descrição oficial. | valores nas amostras: `0`, `1` | todo |
| `Luzes de Borda de Pista (Pista 2)` | `Luzes de Borda de Pista (Pista 2)` | texto | Sem descrição oficial. | valores nas amostras: `0`, `1` | todo |
| `Tipo de Cadastro` | `Tipo de Cadastro` | texto | Sem descrição oficial. | valores nas amostras: `Aeródromo Estrangeiro`, `Aeródromo em Terras Brasileiras`, `Aeródromo em Águas Brasileiras` | todo |
| `Situação` | `Situação` | texto | Sem descrição oficial. | valores nas amostras: `Autorizado`, `Cadastrado`, `Interditado` | todo |
| `Classe RBAC 153` | `Classe RBAC 153` | texto | Todo aeródromo civil público brasileiro é classificado pelo RBAC 153 com vistas a definir os requisitos do Regulamento que lhe são obrigatórios, baseados no processamento do número de passageiros e o tipo de voo que o aeródromo processa no ano corrente. (campo `CLASSIFICAÇÃO RBAC 153` da documentação) | valores nas amostras: `1`, `2`, `3`, `4` | todo |
| `Perfil Operacional RBAC 153` | `Perfil Operacional RBAC 153` | texto | Sem descrição oficial. | valores nas amostras: `Outras Operações`, `RBAC 121`, `RBAC 135 Regular` | todo |
| `Classe RBAC 107` | `Classe RBAC 107` | texto | Classificação definida pelo RBAC 107 para os aeródromos, de acordo com o tipo de serviço aéreo em operação e o número de passageiros processados. (campo `CLASSIFICAÇÃO RBAC 107` da documentação) | valores nas amostras: `AP-0`, `AP-1`, `AP-2`, `AP-3` | todo |
| `Tipo de Operação Internacional (nomenclatura OACI)` | `Tipo de Operação Internacional (nomenclatura OACI)` | texto | Sem descrição oficial. | valores nas amostras: `Público Regular ou Charter (RS)`, `Público Táxi Aéreo e Aviação Geral (RNS)` | todo |
| `Tipo de Operação Internacional (conforme AIP BRASIL)` | `Tipo de Operação Internacional (conforme AIP BRASIL)` | texto | Sem descrição oficial. | valores nas amostras: `INTL CARGA`, `INTL PAX`, `INTL PAX/CARGA`, `INTL PAX/CARGA.` | todo |
| `Certificação Operacional` | `Certificação Operacional` | texto | Sem descrição oficial. | valores nas amostras: `não`, `sim` | todo |
| `Portaria de Certificação` | `Portaria de Certificação` | texto | Sem descrição oficial. | — | todo |
| `Validade do Cadastro` | `Validade do Cadastro` | texto | Sem descrição oficial. | — | todo |
| `Portaria de Cadastro` | `Portaria de Cadastro` | texto | Sem descrição oficial. | — | todo |
| `Restrição` | `Restrição` | texto | Sem descrição oficial. | — | todo |
| `Referência Cautelar` | `Referência Cautelar` | texto | Sem descrição oficial. | — | todo |
| `Amazônia Legal` | `Amazônia Legal` | texto | Sem descrição oficial. | valores nas amostras: `N/A`, `não`, `sim` | todo |

## No lake

- Dataset `anac/aero-caracteristicas`, sem partições; um Parquet por arquivo de origem (1 na amostra).
- O conversor escolhe um arquivo por conteúdo (CSV antes de JSON antes de XLS, salvo grupos que preferem JSON) e lê todas as colunas como texto, exceto onde o JSON traz números.
- Colunas que repetem a partição (`ano`, `mes`) saem do Parquet; o valor fica no caminho.

## Cuidados de uso

- **Texto.** Coordenadas, altitude, comprimentos e datas chegam como texto, em formatos mistos (por exemplo, coordenadas decimais com vírgula).
- **Cadastro vigente.** O arquivo é a fotografia atual do cadastro; o lake guarda só a conversão mais recente.
- **Documentação desatualizada.** A página de metadados da ANAC descreve 38 campos de uma versão anterior (por exemplo `CÓDIGO POSTAL`, `FAROL DE AERÓDROMO`), e a maior parte das 50 colunas do arquivo atual não consta nela.

## Exemplos

Contagem de linhas e de valores distintos de `Id do Aeródromo`:

```python
import duckdb

duckdb.sql("""
    SELECT count(*) AS linhas, count(DISTINCT "Id do Aeródromo") AS distintos
    FROM read_parquet('lake/anac/aero-caracteristicas/*.parquet', union_by_name = true)
""").show()
```

## Referências

- Página do conjunto de dados: https://www.anac.gov.br/acesso-a-informacao/dados-abertos/areas-de-atuacao/aerodromos/aerodromos-publicos-caracteristicas-gerais
- Servidor de dados abertos da ANAC: https://sistemas.anac.gov.br/dadosabertos/
