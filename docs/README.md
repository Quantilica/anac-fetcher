# ANAC — dados abertos (`anac`)

O `anac-fetcher` coleta os dados abertos da Agência Nacional de Aviação Civil (ANAC) publicados no servidor `sistemas.anac.gov.br/dadosabertos` e os converte para o lake em Parquet. A fonte reúne, num só servidor, conjuntos de áreas diferentes: voos e operações aéreas, aeronaves, segurança operacional, operador aéreo, operador aeroportuário e o cadastro de aeródromos. O conversor declara 23 datasets, um por grupo do catálogo.

| Dataset | O que é | Atualização na fonte | Página |
|---|---|---|---|
| `vra` | Voo Regular Ativo (VRA) | mensal; arquivo mensal com cerca de 2 meses de defasagem | [vra](datasets/vra.md) |
| `atrasos-cancelamentos` | Percentuais de atrasos e cancelamentos | mensal, com os dados do mês anterior | [atrasos-cancelamentos](datasets/atrasos-cancelamentos.md) |
| `dados-estatisticos` | Dados Estatísticos do Transporte Aéreo | mensal; as empresas enviam os dados até o dia 10 do mês seguinte e a ANAC os revisa | [dados-estatisticos](datasets/dados-estatisticos.md) |
| `movimentacao-aeroportuaria` | Dados de movimentação aeroportuária | mensal | [movimentacao-aeroportuaria](datasets/movimentacao-aeroportuaria.md) |
| `rab` | Registro Aeronáutico Brasileiro (RAB), histórico mensal | mensal | [rab](datasets/rab.md) |
| `drones` | Drones cadastrados (SISANT), histórico mensal | diária (arquivo vigente); histórico mensal | [drones](datasets/drones.md) |
| `ocorrencias` | Ocorrências aeronáuticas (CENIPA) | diária | [ocorrencias](datasets/ocorrencias.md) |
| `recomendacoes-seguranca` | Recomendações de segurança aeronáutica | semanal | [recomendacoes-seguranca](datasets/recomendacoes-seguranca.md) |
| `empresas-aereas` | Empresas aéreas nacionais | diária | [empresas-aereas](datasets/empresas-aereas.md) |
| `aero-lista-publicos` | Aeródromos públicos: lista | aproximadamente a cada 40 dias | [aero-lista-publicos](datasets/aero-lista-publicos.md) |
| `aero-lista-privados` | Aeródromos privados: lista | aproximadamente a cada 40 dias | [aero-lista-privados](datasets/aero-lista-privados.md) |
| `aero-caracteristicas` | Aeródromos públicos: características gerais | quinzenal | [aero-caracteristicas](datasets/aero-caracteristicas.md) |
| `aero-patio` | Aeródromos públicos: pátios de estacionamento | semanal | [aero-patio](datasets/aero-patio.md) |
| `aero-pistas-pouso` | Aeródromos públicos: pistas de pouso e decolagem | semanal | [aero-pistas-pouso](datasets/aero-pistas-pouso.md) |
| `aero-pistas-taxi` | Aeródromos públicos: pistas de táxi | quinzenal | [aero-pistas-taxi](datasets/aero-pistas-taxi.md) |
| `aero-posicoes-estacionamento` | Aeródromos públicos: posições de estacionamento | quinzenal | [aero-posicoes-estacionamento](datasets/aero-posicoes-estacionamento.md) |
| `aero-helipontos-publicos` | Aeródromos públicos: áreas de pouso e decolagem de helicópteros | não informada | [aero-helipontos-publicos](datasets/aero-helipontos-publicos.md) |
| `aero-excluidos` | Aeródromos públicos: excluídos | não informada | [aero-excluidos](datasets/aero-excluidos.md) |
| `aero-seguranca` | Aeródromos públicos: Programa de Segurança Aeroportuária | não informada | [aero-seguranca](datasets/aero-seguranca.md) |
| `aero-helideck` | Aeródromos privados: helidecks | aproximadamente a cada 40 dias | [aero-helideck](datasets/aero-helideck.md) |
| `aero-heliponto-privado` | Aeródromos privados: helipontos | aproximadamente a cada 40 dias | [aero-heliponto-privado](datasets/aero-heliponto-privado.md) |
| `aero-pzr` | Planos de Zoneamento de Ruído registrados | não informada | [aero-pzr](datasets/aero-pzr.md) |
| `aero-plano-diretor` | Planos diretores aeroportuários | não informada | [aero-plano-diretor](datasets/aero-plano-diretor.md) |

## Como a ANAC publica

- Os arquivos ficam em um servidor de diretórios, sem versionamento: cada atualização sobrescreve o arquivo (o fetcher guarda cada versão baixada com a data no nome). Os conjuntos mensais (VRA, atrasos, movimentação, RAB, drones) têm um arquivo por mês; os demais, um arquivo único.
- A maior parte dos arquivos sai em mais de um formato (CSV, JSON, XLS) com o mesmo conteúdo. O conversor escolhe um por conteúdo: CSV, depois JSON, depois XLS. Três grupos preferem o JSON porque o CSV está quebrado: `empresas-aereas` (separador `\"` literal e cabeçalho repetido), `aero-pistas-pouso` e `aero-posicoes-estacionamento` (CSV sem linha de cabeçalho).
- Cada conjunto tem uma página de metadados no portal da ANAC, com área de contato, periodicidade e, em quase todos, um dicionário de campos. As páginas não informam licença (conferido em 2026-11-15). Para alguns arquivos de aeródromos (helipontos públicos, excluídos, segurança aeroportuária, PZR, plano diretor) não há página de metadados.
- Várias páginas descrevem uma versão anterior do arquivo: o cadastro de aeródromos públicos traz 50 colunas e a página lista 38; as pistas de pouso e decolagem trazem 16 campos técnicos e a página lista cerca de 60. As colunas sem correspondência ficam como "Sem descrição oficial" nas páginas dos datasets.
- Os arquivos de texto vêm em UTF-8 ou Windows-1252 e, em vários, com uma primeira linha de preâmbulo ("Atualizado em: AAAA-MM-DD" ou "Criado em: AAAA-MM-DD") antes do cabeçalho.

## Partições e granularidade

- `ano` e `mes`: `vra`, `atrasos-cancelamentos`, `movimentacao-aeroportuaria`, `rab` e `drones` (histórico mensal).
- Sem partição: os demais, que são fotografias do cadastro vigente.
- `rab` e `drones` também têm o cadastro vigente, sem período, que o conversor grava em `rab-atual` e `drones-atual`. Esses dois datasets não constam em `datasets()` e por isso não têm página nem esquema de referência aqui (as colunas de `drones-atual` são as de `drones`; as de `rab-atual` estão descritas na página de `rab`).

## Dados pessoais

- `drones`: nome e CPF/CNPJ do operador (o CPF vem mascarado em parte dos registros).
- `rab`: nome e CPF/CNPJ de proprietários e operadores.
- `empresas-aereas`: e-mail e telefone de empresas.
- Os demais conjuntos não trazem dados pessoais. O fetcher e o lake preservam os campos como a fonte publica.

## Quebras que valem para mais de um conjunto

| Desde | Mudança | Afeta |
|---|---|---|
| 2024-09 | O RAB passa a publicar CSV e os nomes de coluna ganham sublinhado (de `NRCERTMATRICULA` para `NR_CERT_MATRICULA`) | `rab` |
