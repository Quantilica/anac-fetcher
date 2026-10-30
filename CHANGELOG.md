# Changelog

Todas as mudanças notáveis deste projeto serão documentadas neste arquivo.

O formato segue [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/),
e este projeto adere ao [Semantic Versioning](https://semver.org/lang/pt-BR/).

## [Não lançado]

### Adicionado
- Método opcional `inventory()` no conversor do lake: para cada arquivo bruto, informa
  o dataset que o `convert` vai alimentar ou o motivo de ignorá-lo — gêmeo de outro
  formato, arquivo não tabular (PDF, imagem, documento, mapa) ou versão anterior do
  mesmo formato. Ferramentas de auditoria de cobertura passam a usar esse mapa em vez
  de heurísticas por extensão e nome.

### Corrigido
- A descoberta de arquivos brutos ignora restos `.tmp` de escrita interrompida, que
  podiam ser lidos como se fossem dados.

## [0.6.0] - 2026-10-29

### Corrigido
- `convert` separa o cadastro vigente do histórico mensal em `drones` e `rab`: o
  histórico fica com o nome do grupo e o cadastro (`-atual-csv`) vai para `<grupo>-atual`.
  Antes, partições de profundidades diferentes no mesmo dataset impediam o DuckDB de
  ler o lake ("Hive partition mismatch").
- `read_json` lê os JSON com várias páginas concatenadas (`[...][...]`, em
  `dados-estatisticos`), que antes falhavam com "Extra data".
- `convert` converte um só formato de cada conteúdo publicado em vários (`-csv`,
  `-json`, `-xls`): CSV, depois XLSX, XLS e JSON, na versão mais recente. Antes os
  formatos geravam linhas duplicadas no lake ou se sobrescreviam, e o JSON de 471 MB de
  `empresas-aereas` levava o leitor a ~190 GB de memória.
- `read_json` lê JSON em Latin-1 (anexos de `atrasos-cancelamentos`) e NDJSON (um
  objeto por linha, como `empresas-aereas` e `aerodromos-*`), em streaming; listas viram
  texto separado por `; `.
- `empresas-aereas` usa o JSON: o CSV vem quebrado da origem. `read_csv` recusa de
  imediato um CSV com linha de mais de 1 MB, que antes levava o leitor a dezenas de GB.
- `read_csv` lê CSV com aspas desbalanceadas (RAB) como último recurso, sem tratar
  aspas e removendo-as das pontas dos valores.

## [0.5.0] - 2026-10-27

### Adicionado
- Módulo `anac_fetcher.lake` e entry point `quantilica.lake`: conversão direta dos arquivos abertos da ANAC para o lake Parquet particionado no formato Hive (`ano=/mes=` para VRA e Dados Estatísticos, `ano=` para anuais e sem partição para cadastros estáticos).
- Comandos CLI `convert` e `pipeline` integrados via SDK do `FetcherApp`, com suporte a `--lake`, `--dataset` e `--force`.
- Extra `analysis` atualizado para `quantilica-analytics>=0.5.0`.
- Dependência `quantilica-core` atualizada para `>=0.13.0`, primeira versão com o contrato do lake.

## [0.4.3] - 2026-10-20

### Alterado
- `reader`: delega leitura de manifest sidecar a `quantilica-core` (`read_manifest_sidecar`).
- Dependências atualizadas: `quantilica-core>=0.12.0` e `quantilica-analytics>=0.4.0`.
- Atualização de docstrings e limpeza interna.

## [0.4.2] - 2026-10-14

### Corrigido

- `plugin.py`: a dica de instalação do extra `analysis` mandava `pip install anac-fetcher[analysis]`, que não funciona para fetchers do Fluxo B (fora do PyPI), e o Rich ainda engolia o `[analysis]` por tratá-lo como marcação, deixando só `pip install anac-fetcher`. Agora a mensagem é `quantilica install anac --extra analysis`. Nos guards de `reader.py`, `wrangling.py` e `contracts.py`, que atendem quem importa o pacote, a mensagem é `uv add 'anac-fetcher[analysis]' --index https://index.quantilica.com/simple/`.

### Alterado
- `README.md`: a seção de instalação deixa de mandar `pip install` (fetchers do Fluxo B não estão no PyPI) e passa a mostrar `quantilica install anac` (com `--extra analysis`) e `uv add --index` para uso como biblioteca.
- `cli.py` protege o import do plugin; sem o host a CLI standalone sai com
  código 1 e orienta `quantilica install <fonte>`.
- `reader.decompress` agora delega a descompressão de arquivos brutos para `quantilica.core.files.decompress_archive`, eliminando lógica local duplicada.
- `cli.py` ganha o bloco `if __name__ == "__main__": main()` (paridade com
  `bcb-sgs-fetcher`).
- `reader.py`, `contracts.py` e `wrangling.py`: imports de `polars`/
  `quantilica.analytics` agora falham com mensagem acionável orientando o
  extra `analysis` (`uv add 'anac-fetcher[analysis]' --index https://index.quantilica.com/simple/`).
- Extra `analysis` declara `polars>=1.0.0` explicitamente.

## [0.4.1] - 2026-10-02

### Alterado

- **Padronização/deduplicação:** `reader.normalize_dtypes` delega a
  conversão de números brasileiros a
  `quantilica.analytics.reader.normalize_brazilian_numbers` (eliminada a
  reimplantação local de vírgula decimal/sentinela).
- **Padronização/deduplicação:** `reader.write_parquet` delega ao
  `quantilica.analytics.writer.to_parquet` canônico — escrita atômica
  (write-temp-rename) e, com manifest do download reconstruído do sidecar do
  arquivo bruto, proveniência `quantilica.*` injetada no Parquet + sidecar
  `.manifest.json` escrito ao lado do destino.
- **Padronização/deduplicação:** `plugin.py` usa o resolver canônico `make_resolve_groups`
  (`quantilica.cli.sdk`); removido o loop duplicado de resolução de grupos.
- Extra `[analysis]`: pin elevado para `quantilica-analytics>=0.3.0`
  (`normalize_brazilian_numbers` + `to_parquet` + `manifest_to_metadata`).

## [0.4.0] - 2026-08-29

### Adicionado

- Camada de extração e tratamento de dados (padrão `pdet-fetcher`/`anp-fetcher`):
  `reader.py` (leitura tipada de CSV/XLS/XLSX/JSON — preâmbulo "Atualizado em:"
  e separador auto-detectados, linhas ragged truncadas, BOM/modos mistos de
  JSON tolerados; Parquet com proveniência `quantilica.*` do manifest sidecar)
  e `wrangling.py` (`convert_group` idempotente por grupo + `extract_schema`).
  Comando `convert` agora aceita `[GROUPS]...` e o `pipeline` repassa a seleção
  ao passo de conversão. Extra `[analysis]` ganhou `quantilica-analytics` e
  `fastexcel`. Grupos-chave (`ocorrencias`, `recomendacoes-seguranca`, `vra`,
  `aero-lista-publicos`) validados por `DataContract`.
- 6 novos grupos de dados: `dados-estatisticos` (Dados Estatísticos do
  Transporte Aéreo), `drones` (cadastro SISANT, snapshot + histórico mensal
  desde 2022-08), `atrasos-cancelamentos` (percentuais de atrasos e
  cancelamentos, mensal desde 2000), `empresas-aereas` (empresas aéreas
  nacionais), `movimentacao-aeroportuaria` (movimentação aeroportuária,
  mensal desde 2019, apenas CSV) e `recomendacoes-seguranca` (recomendações
  de segurança aeronáutica) — ampliando o catálogo de 4 para 10 grupos e de
  ~700 para ~3.0k datasets.

## [0.3.0] - 2026-08-07
### Alterado
- Refatoração arquitetural: Remoção de dependências (`quantilica-cli` e `quantilica-catalog`) e limpeza de imports. Os fetchers agora são pacotes de extração puros, dependendo estritamente do `quantilica-core`.

## [0.1.0] - 2026-07-21

### Adicionado

- Catálogo inicial com 4 grupos de dados: `vra` (Voo Regular Ativo, mensal
  desde 2000), `rab` (Registro Aeronáutico Brasileiro, snapshot atual +
  histórico mensal desde 2017), `ocorrencias` (Ocorrências Aeronáuticas do
  CENIPA) e 13 subgrupos de `aerodromos` (infraestrutura de aeródromos
  públicos e privados), todos servidos por
  `sistemas.anac.gov.br/dadosabertos`.
- CLI standalone (`anac-fetcher`, `argparse`) e plugin Typer/Rich para
  `quantilica-cli` (`quantilica anac`), com os comandos `sync` e `discover`.
- Manifestos de proveniência (`DownloadManifest`) via `quantilica-core` em
  todo download.
- Flag `--sleeptime` (padrão 0.3s) em `sync`, aplicando uma pequena pausa
  entre downloads dentro de um grupo — cortesia ao servidor em lotes
  grandes (ex.: grupo `rab`, ~250 arquivos).

### Corrigido

- `cli.py` não suprimia os loggers verbosos de terceiros (`quantilica.core`,
  `httpx` via `log_step`) fora do modo `--verbose`, conforme
  `docs/docs/normas/cli-fetchers.md` §2.6 — padronizado com os demais
  fetchers do ecossistema.
