---
dataset:
  id: aero-seguranca
  fonte: anac
  titulo: "Aeródromos públicos: Programa de Segurança Aeroportuária"
  resumo: "Aeródromos com Programa de Segurança Aeroportuária, com emenda do RBAC 107, revisão da IS 107 e portaria."
  orgao: Agência Nacional de Aviação Civil (ANAC)
  pagina_oficial: https://www.anac.gov.br/acesso-a-informacao/dados-abertos/areas-de-atuacao/aerodromos
  licenca: "Não informada pela fonte: as páginas de metadados da ANAC não trazem licença (conferido em 2026-11-15)."
  periodicidade: "não informada"
  cobertura: {inicio: "2026-11", fim: "em-curso"}
  unidade: "um registro do cadastro de aeródromos vigente"
  granularidade: {espacial: "Brasil (aeródromo)", temporal: "cadastro vigente (sem série)"}
  formato_bruto: "CSV (e JSON) `Psa`, separador ponto e vírgula"
  lake: {estado: convertido, particoes: [], chave: [CIAD], colunas: 9}
  dados_pessoais: nenhum
  eras: []
  revisado_em: 2026-11-15
  versao_fetcher: 0.9.0
---

# Aeródromos públicos: Programa de Segurança Aeroportuária

## Resumo

Aeródromos com Programa de Segurança Aeroportuária, com emenda do RBAC 107, revisão da IS 107 e portaria. Por ser um conjunto sem série, a cobertura registra a data da coleta.

## Ficha técnica

<!-- gerado:ficha -->

| Campo | Valor |
|---|---|
| Dataset | `anac/aero-seguranca` |
| Órgão | Agência Nacional de Aviação Civil (ANAC) |
| Página oficial | https://www.anac.gov.br/acesso-a-informacao/dados-abertos/areas-de-atuacao/aerodromos |
| Licença | Não informada pela fonte: as páginas de metadados da ANAC não trazem licença (conferido em 2026-11-15). |
| Periodicidade | não informada |
| Cobertura | 2026-11 a em-curso |
| Unidade (uma linha) | um registro do cadastro de aeródromos vigente |
| Granularidade | espacial: Brasil (aeródromo); temporal: cadastro vigente (sem série) |
| Formato bruto | CSV (e JSON) `Psa`, separador ponto e vírgula |
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
- Conferido em 2026-11-15: 103 linhas e 9 colunas. A ANAC não publica página de metadados para este arquivo.

## Conteúdo

- Amostra local de 103 linhas em 1 arquivo(s) Parquet, convertida em 2026-11-15 com o fetcher 0.9.0; a amostra não cobre toda a série publicada.

## Variáveis

A ANAC não publica página de metadados nem dicionário para este arquivo; as colunas ficam como "Sem descrição oficial".

| Coluna no lake | Na fonte | Tipo | Descrição | Unidade / códigos | Período |
|---|---|---|---|---|---|
| `OACI` | `OACI` | texto | Sem descrição oficial. | — | todo |
| `CIAD` | `CIAD` | texto | Sem descrição oficial. | — | todo |
| `Nome` | `Nome` | texto | Sem descrição oficial. | — | todo |
| `Emenda RBAC107` | `Emenda RBAC107` | texto | Sem descrição oficial. | valores nas amostras: `02`, `04`, `05`, `07`, `08`, `09`, `10` | todo |
| `Revisao IS107` | `Revisao IS107` | texto | Sem descrição oficial. | valores nas amostras: `D`, `E`, `F`, `H`, `I`, `J`, `K`, `L` | todo |
| `Capacidade aeronave` | `Capacidade aeronave` | texto | Sem descrição oficial. | valores nas amostras: `Superior a 60 assentos`, `null` | todo |
| `Servicos Aereos` | `Servicos Aereos` | texto | Sem descrição oficial. | valores nas amostras: `voos domésticos`, `voos domésticos e internacionais` | todo |
| `Número da Portaria` | `Número da Portaria` | texto | Sem descrição oficial. | — | todo |
| `Data de Publicação` | `Data de Publicação` | texto | Sem descrição oficial. | — | todo |

## No lake

- Dataset `anac/aero-seguranca`, sem partições; um Parquet por arquivo de origem (1 na amostra).
- O conversor escolhe um arquivo por conteúdo (CSV antes de JSON antes de XLS, salvo grupos que preferem JSON) e lê todas as colunas como texto, exceto onde o JSON traz números.
- Colunas que repetem a partição (`ano`, `mes`) saem do Parquet; o valor fica no caminho.

## Cuidados de uso

- **Texto.** Coordenadas, altitude, comprimentos e datas chegam como texto, em formatos mistos (por exemplo, coordenadas decimais com vírgula).
- **Cadastro vigente.** O arquivo é a fotografia atual do cadastro; o lake guarda só a conversão mais recente.

## Exemplos

Contagem de linhas e de valores distintos de `OACI`:

```python
import duckdb

duckdb.sql("""
    SELECT count(*) AS linhas, count(DISTINCT OACI) AS distintos
    FROM read_parquet('lake/anac/aero-seguranca/*.parquet', union_by_name = true)
""").show()
```

## Referências

- Página do conjunto de dados: https://www.anac.gov.br/acesso-a-informacao/dados-abertos/areas-de-atuacao/aerodromos
- Servidor de dados abertos da ANAC: https://sistemas.anac.gov.br/dadosabertos/
