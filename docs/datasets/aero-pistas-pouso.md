---
dataset:
  id: aero-pistas-pouso
  fonte: anac
  titulo: "Aeródromos públicos: pistas de pouso e decolagem"
  resumo: "Pistas de pouso e decolagem de aeródromos públicos, com dimensões, pavimento, resistência, luzes e regras de voo por cabeceira."
  orgao: Agência Nacional de Aviação Civil (ANAC)
  pagina_oficial: https://www.anac.gov.br/acesso-a-informacao/dados-abertos/areas-de-atuacao/aerodromos/aerodromos-publicos-pistas-de-pouso-e-decolagem
  licenca: "Não informada pela fonte: as páginas de metadados da ANAC não trazem licença (conferido em 2026-11-15)."
  periodicidade: "semanal"
  cobertura: {inicio: "2026-11", fim: "em-curso"}
  unidade: "uma pista de pouso e decolagem de um aeródromo"
  granularidade: {espacial: "Brasil (aeródromo)", temporal: "cadastro vigente (sem série)"}
  formato_bruto: "JSON em linhas (NDJSON) `pda_aerodromos_publicos_pistas_pouso_decolagem`; o CSV da fonte vem sem cabeçalho e não é usado"
  lake: {estado: convertido, particoes: [], chave: [], colunas: 16}
  unidades_de_medida:
    id_aerodromo: "sem unidade (identificador)"
    qt_comprimento: "m"
    fg_luz_borda_pista: "indicador 0 ou 1"
    qt_largura: "m"
    fg_luz_eixo_pista: "indicador 0 ou 1"
    id_pista: "sem unidade (identificador)"
    id_pista_cabeceira_menor: "sem unidade (identificador)"
    id_pista_cabeceira_maior: "sem unidade (identificador)"
  dados_pessoais: nenhum
  eras: []
  revisado_em: 2026-11-15
  versao_fetcher: 0.9.0
---

# Aeródromos públicos: pistas de pouso e decolagem

## Resumo

Pistas de pouso e decolagem de aeródromos públicos, com dimensões, pavimento, resistência, luzes e regras de voo por cabeceira. Por ser um conjunto sem série, a cobertura registra a data da coleta.

## Ficha técnica

<!-- gerado:ficha -->

| Campo | Valor |
|---|---|
| Dataset | `anac/aero-pistas-pouso` |
| Órgão | Agência Nacional de Aviação Civil (ANAC) |
| Página oficial | https://www.anac.gov.br/acesso-a-informacao/dados-abertos/areas-de-atuacao/aerodromos/aerodromos-publicos-pistas-de-pouso-e-decolagem |
| Licença | Não informada pela fonte: as páginas de metadados da ANAC não trazem licença (conferido em 2026-11-15). |
| Periodicidade | semanal |
| Cobertura | 2026-11 a em-curso |
| Unidade (uma linha) | uma pista de pouso e decolagem de um aeródromo |
| Granularidade | espacial: Brasil (aeródromo); temporal: cadastro vigente (sem série) |
| Formato bruto | JSON em linhas (NDJSON) `pda_aerodromos_publicos_pistas_pouso_decolagem`; o CSV da fonte vem sem cabeçalho e não é usado |
| Estado no lake | convertido |
| Partições | — |
| Chave | — |
| Colunas | 16 |
| Unidades de medida | `id_aerodromo`: sem unidade (identificador); `qt_comprimento`: m; `fg_luz_borda_pista`: indicador 0 ou 1; `qt_largura`: m; `fg_luz_eixo_pista`: indicador 0 ou 1; `id_pista`: sem unidade (identificador); `id_pista_cabeceira_menor`: sem unidade (identificador); `id_pista_cabeceira_maior`: sem unidade (identificador) |
| Dados pessoais | nenhum |
| Eras | nenhuma |
| Revisado em | 2026-11-15 |
| Versão do fetcher | 0.9.0 |

## Origem e coleta

- O fetcher baixa o arquivo estático do diretório `Aerodromos/` do servidor de dados abertos da ANAC; o servidor sobrescreve o arquivo a cada atualização, sem versões anteriores.
- Conferido em 2026-11-15: 31.806 registros e 16 campos no JSON.

## Conteúdo

- Amostra local de 31.806 linhas em 1 arquivo(s) Parquet, convertida em 2026-11-15 com o fetcher 0.9.0; a amostra não cobre toda a série publicada.

## Variáveis

As descrições vêm da página de metadados do conjunto no portal da ANAC (7 de 16 colunas); as demais ficam como "Sem descrição oficial".

| Coluna no lake | Na fonte | Tipo | Descrição | Unidade / códigos | Período |
|---|---|---|---|---|---|
| `ds_resistencia` | `ds_resistencia` | texto | Sem descrição oficial. | — | todo |
| `cab_maior_regra_voo` | `cab_maior_regra_voo` | texto | Operação por Regras de Voo Visual (VFR) e/ou Regras de Voo por Instrumentos (IFR), diurno e/ou noturno, por cabeceira. (campo `TIPO DE OPERAÇÃO (CABECEIRA MAIOR)` da documentação) | — | todo |
| `MCDA` | `MCDA` | texto | Sem descrição oficial. | valores nas amostras: `Aeródromos` | todo |
| `codigo_referencia` | `codigo_referencia` | texto | Sem descrição oficial. | valores nas amostras: `2B`, `2C`, `3C`, `4C`, `4D`, `4E` | todo |
| `id_aerodromo` | `id_aerodromo` | inteiro | Sem descrição oficial. | — | todo |
| `qt_comprimento` | `qt_comprimento` | inteiro | Comprimento da pista de pouso e decolagem, considerando a porção desta disponível para passagem trânsito das aeronaves em condições normais. Dado apresentado em metros. (campo `COMPRIMENTO` da documentação) | — | todo |
| `cab_menor_regra_voo` | `cab_menor_regra_voo` | texto | Operação por Regras de Voo Visual (VFR) e/ou Regras de Voo por Instrumentos (IFR), diurno e/ou noturno, por cabeceira. (campo `TIPO DE OPERAÇÃO (CABECEIRA MENOR)` da documentação) | — | todo |
| `fg_luz_borda_pista` | `fg_luz_borda_pista` | inteiro | Indicação se existe ou não (Sim/Não) Sinalização Luminosa localizada ao longo dos limites laterais da pista de pouso e decolagem. (campo `LUZ BORDA DE PISTA` da documentação) | — | todo |
| `ConjuntoDado` | `ConjuntoDado` | texto | Sem descrição oficial. | — | todo |
| `qt_largura` | `qt_largura` | decimal | Largura da pista de pouso e decolagem, considerando a distância lateral na qual uma aeronave pode transitar em condições normais de operação. Dado apresentado em metros. (campo `LARGURA` da documentação) | — | todo |
| `nm_pavimento_tipo` | `nm_pavimento_tipo` | texto | Natureza ou tipo da superfície da pista de pouso e decolagem (campo `SUPERFICIE PAVIMENTO` da documentação) | — | todo |
| `nm_pista` | `nm_pista` | texto | Sem descrição oficial. | — | todo |
| `fg_luz_eixo_pista` | `fg_luz_eixo_pista` | inteiro | Indicação se existe ou não (Sim/Não) Sinalização Luminosa de eixo de pista de pouso e decolagem, sendo embutida no pavimento por toda a extensão. (campo `LUZ EIXO DE PISTA` da documentação) | — | todo |
| `id_pista` | `id_pista` | inteiro | Sem descrição oficial. | — | todo |
| `id_pista_cabeceira_menor` | `id_pista_cabeceira_menor` | inteiro | Sem descrição oficial. | — | todo |
| `id_pista_cabeceira_maior` | `id_pista_cabeceira_maior` | inteiro | Sem descrição oficial. | — | todo |

## No lake

- Dataset `anac/aero-pistas-pouso`, sem partições; um Parquet por arquivo de origem (1 na amostra).
- O conversor escolhe um arquivo por conteúdo (CSV antes de JSON antes de XLS, salvo grupos que preferem JSON) e lê todas as colunas como texto, exceto onde o JSON traz números.
- Colunas que repetem a partição (`ano`, `mes`) saem do Parquet; o valor fica no caminho.

## Cuidados de uso

- **Texto.** Coordenadas, altitude, comprimentos e datas chegam como texto, em formatos mistos (por exemplo, coordenadas decimais com vírgula).
- **Cadastro vigente.** O arquivo é a fotografia atual do cadastro; o lake guarda só a conversão mais recente.
- **Documentação desatualizada.** A página de metadados descreve cerca de 60 campos com nomes como `TORA (CABECEIRA MENOR)`, mas o JSON publica 16 campos com nomes técnicos (`qt_comprimento`, `fg_luz_eixo_pista`); só os de equivalência evidente têm descrição oficial aqui.
- **Muitos registros por pista.** 31.806 registros para 4.001 `id_pista` distintos: cada pista aparece cerca de oito vezes; `id_pista` não é chave, e a fonte não explica a repetição.
- **Rótulo contraditório.** `ConjuntoDado` vale `Aeródromos privados - pistas de pouso e decolagem` em todas as linhas, embora o arquivo esteja na pasta de aeródromos públicos.

## Exemplos

Contagem de linhas e de valores distintos de `ds_resistencia`:

```python
import duckdb

duckdb.sql("""
    SELECT count(*) AS linhas, count(DISTINCT ds_resistencia) AS distintos
    FROM read_parquet('lake/anac/aero-pistas-pouso/*.parquet', union_by_name = true)
""").show()
```

## Referências

- Página do conjunto de dados: https://www.anac.gov.br/acesso-a-informacao/dados-abertos/areas-de-atuacao/aerodromos/aerodromos-publicos-pistas-de-pouso-e-decolagem
- Servidor de dados abertos da ANAC: https://sistemas.anac.gov.br/dadosabertos/
