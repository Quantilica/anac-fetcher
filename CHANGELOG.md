# Changelog

Todas as mudanças notáveis deste projeto serão documentadas neste arquivo.

O formato segue [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/),
e este projeto adere ao [Semantic Versioning](https://semver.org/lang/pt-BR/).

## [Não lançado]

### Alterado
- `cli.py` protege o import do plugin; sem o host a CLI standalone sai com
  código 1 e orienta `quantilica install <fonte>`.
- `reader.decompress` agora delega a descompressão de arquivos brutos para `quantilica.core.files.decompress_archive`, eliminando lógica local duplicada.
- `cli.py` ganha o bloco `if __name__ == "__main__": main()` (paridade com
  `bcb-sgs-fetcher`).
- `reader.py`, `contracts.py` e `wrangling.py`: imports de `polars`/
  `quantilica.analytics` agora falham com mensagem acionável orientando o
  extra `analysis` (`pip install 'anac-fetcher[analysis]'`).
- Extra `analysis` declara `polars>=1.0.0` explicitamente.

## [0.4.1] - 2026-10-02

### Alterado

- **Onda 3A (padronização/deduplicação):** `reader.normalize_dtypes` delega a
  conversão de números brasileiros a
  `quantilica.analytics.reader.normalize_brazilian_numbers` (eliminada a
  reimplantação local de vírgula decimal/sentinela).
- **Onda 3A:** `reader.write_parquet` delega ao
  `quantilica.analytics.writer.to_parquet` canônico — escrita atômica
  (write-temp-rename) e, com manifest do download reconstruído do sidecar do
  arquivo bruto, proveniência `quantilica.*` injetada no Parquet + sidecar
  `.manifest.json` escrito ao lado do destino.
- **Onda 3A:** `plugin.py` usa o resolver canônico `make_resolve_groups`
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
