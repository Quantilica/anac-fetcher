# Changelog

Todas as mudanças notáveis deste projeto serão documentadas neste arquivo.

O formato segue [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/),
e este projeto adere ao [Semantic Versioning](https://semver.org/lang/pt-BR/).

## [0.11.1] - 2026-11-28

### Corrigido

- **Movimentação aeroportuária: cinco meses sem coleta.** `LAST_PUBLISHED` ficara em 2025-12 e a ANAC já publicara 2026-01 a 2026-05 (todos juntos, em 2026-11-17). Sobe para 2026-05. A folga dos meses seguintes passa a ser limitada: só levam `pending_publication` os meses a até 18 meses de hoje (`PENDING_MAX_MONTHS`); passado isso o 404 volta a ser erro, em vez de "pendente" para sempre. A constante só fixa até onde o 404 é erro desde o primeiro dia; um mês novo é coletado sem editá-la. **O valor 18 vem de uma observação só**: um lote publicado com atraso de cerca de 6 (2026-05) a cerca de 10 meses (2026-01), e o diretório de cada ano fechado perto de 1.º de junho do ano seguinte. Deve ser revisto quando houver um segundo lote.
- **`discover` coerente com o catálogo.** Compara a fonte com o que o catálogo gera, não com a constante: `new_months` traz só os meses publicados que a coleta não cobre (hoje nenhum). Os que já entram como pendentes aparecem no campo novo `ahead_of_confirmed` (informativo; não conta como novidade nem muda `has_changes`).
- **`discover` acusa arquivo de nome fora do padrão.** Campo novo `unclassified`: todo link dos índices (raiz e todos os anos) que não é o CSV mensal, o JSON mensal (ignorado de propósito), o link para o diretório pai, a ordenação do índice ou um extra já conhecido (hoje só `2019/Movimentacoes_Aeroportuarias_201912.csv.csv`) conta em `has_changes`. Fecha o ponto cego da folga: o `sync` só tenta o nome esperado e tolera o 404 dos pendentes, então um mês publicado como `_v2`, `.zip`, arquivo anual ou em outro diretório passaria em silêncio. Conferido contra os índices reais de 2026-11-28: `unclassified` vazio.
- **Aviso de período pendente sem publicação sobe de 6 para 15 meses** (`PENDING_WARN_MONTHS`): a fonte já esperou dez meses por um mês, então seis avisaria em operação normal; o aviso vem antes de a folga (18) acabar.
- **Percentuais de atrasos e cancelamentos não gera mais mês inexistente na virada do ano.** Em janeiro e fevereiro o catálogo incluía o mês corrente (404 diário e saída 3). O fim agora é hoje menos 2 meses atravessando o ano, e os dois últimos meses gerados passam a levar a marca `pending_publication`, como no `vra`: o 404 deles deixa de ser erro ("ainda não publicado"); só os meses mais antigos seguem falhando em 404.

## [0.11.0] - 2026-11-28

### Corrigido

- **Contrato de colunas que falha é erro do arquivo.** `_apply_contract` só avisava e o arquivo era gravado sem cast. Agora levanta `ContractError` (`wrangling.convert_one`; `convert_group` converte os demais e levanta no fim) e, no conversor do lake, vira erro do arquivo no `ConvertResult` (o host sai com 1), com as colunas esperadas e as encontradas na mensagem. O arquivo não é gravado.
- **Leitura tolerante conta o que descarta.** O CSV é lido primeiro de forma estrita; só se uma linha tem mais campos que o cabeçalho ele é relido com `truncate_ragged_lines` (inclusive no recuo sem aspas), as linhas que perderam conteúdo (campo a mais não vazio; separador sobrando no fim da linha não conta) são contadas num segundo passo e registradas em WARNING com o arquivo. No recuo `ignore_errors` do NDJSON contam-se os valores trocados por nulo por tipo incompatível. Acima de 1% (`MAX_DROPPED_FRACTION`) vira `DroppedRowsError`, erro do arquivo (no lake, erro do `ConvertResult`). Antes, nada era contado.
- **VRA não gera mais mês que não existe na virada do ano.** Em janeiro e fevereiro o catálogo incluía o mês corrente (404 diário e saída 3). O fim agora é hoje menos 2 meses atravessando o ano, e os dois últimos meses gerados levam `pending_publication` (a defasagem real oscila): se a fonte ainda não os publicou, o 404 é "ainda não publicado".
- **Movimentação aeroportuária não congela mais a coleta.** `LAST_PUBLISHED` continua sendo o último mês confirmado (não deriva do relógio), mas os meses depois dele, até o mês corrente, passam a ser gerados com `pending_publication`: os que a ANAC já publicou são coletados sem esperar a constante subir; os que não existem viram "ainda não publicado". `discover` segue apontando o que passa de `LAST_PUBLISHED`.

- **Preâmbulo "Criado em:" reconhecido; `aero-heliponto-privado` passa de 1 para 27 colunas.** O leitor só conhecia a linha `Atualizado em: ...` antes do cabeçalho; o CSV de `aero-heliponto-privado` começa por `Criado em: ...` e a linha virava o cabeçalho de uma coluna só (o Parquet gravado até a 0.10.1 tem UMA coluna, com o texto do preâmbulo). É correção de dado errado: o esquema muda de 1 para 27 colunas porque o antigo estava errado. O `convert` reconverte esse grupo uma vez (os grupos sem versão de conversor no rodapé declaram a saída, `origin_outputs`, e o Parquet sem a declaração não é pulado); nas rodadas seguintes o arquivo é pulado. O "xls" de texto do `aero-helideck` tem o mesmo preâmbulo e é lido pelo mesmo caminho. Conferidos os primeiros bytes dos CSV mais recentes de cada grupo do bruto: não há outra variante de preâmbulo; ficam fora desta correção, por serem outro problema, os CSV de `aero-pistas-pouso` e `aero-posicoes-estacionamento` (2024), que não têm linha de cabeçalho.
- **Período pendente sem publicação há meses emite aviso.** As entradas `pending_publication` não dão erro no 404; para que um arquivo renomeado não fique "pendente" para sempre, o `sync` e o `check` (inclusive no modo de plano) emitem UM WARNING por execução quando o período pendente mais antigo que deu 404 está a mais de 6 meses de hoje (`PENDING_WARN_MONTHS`), dizendo desde quando não há publicação e sugerindo conferir o endereço ou rodar `discover`. O código de saída não muda.

### Alterado

- A fixture `sem_contratos` (testes de mecânica com CSVs sintéticos) é pedida só pelos testes que precisam, em vez de valer para a suíte toda.
- Requer `quantilica-analytics>=0.15.0` no extra `analysis` (saída declarada, `origin_outputs`).
- Requer `quantilica-cli>=0.30.0` (marca `pending_publication`). Com host anterior a marca é ignorada e o 404 desses meses volta a ser erro.
- A suíte roda sem os DataContracts (a conftest os desliga), salvo nos testes marcados `contrato_real`.

## [0.10.1] - 2026-11-19

### Alterado

- **Build do lake sem mudança não lê o bruto.** Um arquivo (inclusive ZIP/7z) que já está no lake com o mesmo sha256 é pulado antes de ser extraído ou lido, e o sha256 vem do sidecar `.manifest.json` (`quantilica.analytics.lake.sha256_file`) em vez de uma leitura completa; vale também para os anexos de `atrasos-cancelamentos`. Planilha de várias abas, que grava uma chave por aba, ainda é lida para saber as abas.
- Piso do `quantilica-analytics` em 0.14.0 (sha256 pelo sidecar).

### Corrigido

- A conferência de "já está no lake" (`is_current`) fica dentro do tratamento de erro: um erro de E/S ao calcular o sha256 do bruto (montagem de rede) não derruba mais o `convert`; o arquivo segue para o caminho completo, que reporta o erro dele. O mesmo vale para o sha256 dos anexos de `atrasos-cancelamentos` e para o roteamento do grupo (que hasheia os arquivos sem sufixo de anexo): viram erro de arquivo em `errors`.
- CI e infraestrutura alinhados ao template (fetcher-template v0.2.1).

## [0.10.0] - 2026-11-16
### Alterado
- **Quebra de layout no lake: `atrasos-cancelamentos` passa a um Parquet por anexo e mês, com proveniência.** Os anexos (I, II e III) têm esquemas e granularidades diferentes (10, 9 e 8 colunas na maioria dos meses), então não são juntados: o agrupamento é por tabela. Em `anac/atrasos-cancelamentos/ano=AAAA/mes=MM/`:
  - antes: `atrasos-cancelamentos_AAAA-MM_anexo-i.parquet`, `..._anexo-ii.parquet`, `..._anexo-iii.parquet` e, nos meses baixados por versões antigas, também `atrasos-cancelamentos_AAAA-MM.parquet` (4 arquivos por mês);
  - depois: `atrasos-cancelamentos_AAAAMM_anexo-i.parquet`, `..._anexo-ii.parquet`, `..._anexo-iii.parquet` (3 por mês), cada um com a coluna `_origem` (o arquivo bruto de origem) e o rodapé `quantilica.members` (sha256 e linhas).
  - As pastas `ano=`/`mes=` não mudam. Na reconversão, o Parquet antigo do anexo e o da cópia sem sufixo saem sozinhos depois que o novo é publicado (só se o sha256 de origem for o do anexo); o que sobrar com o nome antigo é resíduo e pode ser apagado.
- O arquivo bruto sem sufixo de anexo (`atrasos-cancelamentos_AAAA-MM@data.csv`), gravado por versões antigas do fetcher, é byte a byte igual a um dos anexos (conferido pelo sha256 dos manifests de 284 meses). Deixa de ser convertido: o lake antigo guardava as linhas desse anexo duas vezes. O inventário o devolve como `gemeo`. Numa partição que tem anexos, o arquivo sem sufixo cujo sha256 não é o de nenhum anexo é versão antiga de um anexo revisado: não é convertido, o inventário o dá como `superado` e o log avisa; o Parquet antigo dele, se existir, vai para `errors` para ser removido. Só numa partição sem nenhum anexo o arquivo sem sufixo é uma tabela.
- Um anexo novo ou alterado reescreve só o Parquet do seu mês; os que já estão no lake são pulados sem ler o bruto. `contract_version` (1) e `converter_version` ("1") ficam no rodapé: mudar a normalização ou a leitura e subir uma delas reconverte.
- Parquet antigo mantido na migração (sha256 de origem diferente do anexo atual, por exemplo um anexo revisado depois da última conversão) vai para `errors`, com o caminho: as linhas dele ficam duplicadas até você apagá-lo. O sha256 de cada arquivo é calculado uma vez e passado ao `write_group`.
- Exige `quantilica-analytics>=0.12.0` no extra `analysis` (`write_group`). Os outros grupos continuam com um Parquet por arquivo bruto.
- Documentação dos dados de `atrasos-cancelamentos`: seção "No lake" e cuidados de uso.

### Adicionado
- Testes de equivalência do agrupamento: o conteúdo do lake por arquivo de origem (linhas, colunas e tipos, linhas ordenadas) é igual ao do conversor anterior (`tests/golden/lake_antes_do_agrupamento.json`, gerado antes da mudança), mais segunda execução sem reescrita, migração do layout antigo sem linhas duplicadas, inventário e `lake_audit` limpo.

## [0.9.1] - 2026-11-15
### Adicionado
- Documentação dos dados em `docs/`, conforme a norma de documentação dos dados: página da fonte e página de cada um dos 23 datasets, com o dicionário de todas as colunas (descrição oficial da ANAC onde existe) e esquema de referência. Um teste a verifica. `aero-heliponto-privado` está como `parcial` (veja a página).

### Corrigido
- CI: o pyproject declara o PyPI antes do índice Quantilica (`[[tool.uv.index]]`), e o workflow perde `--index` e `--index-strategy`. Com a estratégia padrão `first-index`, o `uv sync` só consulta o índice para o que não está no PyPI (`quantilica-analytics`) e deixa de receber o 503 intermitente que o GitHub Pages devolve a caminhos inexistentes.
- `reader`: os fallbacks de leitura (CSV em codificação alternativa, NDJSON relido com `ignore_errors`, JSON de páginas unidas e `from_dicts` com tipos mistos) registram em log o motivo da falha, em vez de engolir o erro em silêncio. Sem mudança de comportamento.

## [0.9.0] - 2026-11-14

### Corrigido
- `convert_one` (`wrangling`) não deixa mais a pasta `quantilica_extract_*` no temp do sistema quando o ZIP tem subpasta: removia só a pasta do arquivo extraído, não a raiz da extração.
- `lake build`: a limpeza da extração rodava sobre um `tmp_dir` que nunca era atribuído (sempre `None`), então toda extração de ZIP/7z ficava no temp. A extração passa a ficar sob um gerenciador de contexto (`extracted_data`, novo em `anac_fetcher.reader`), que remove a raiz inteira em sucesso, em erro e em interrupção. Nenhum caminho do fetcher chama mais `decompress` (que cria a pasta sozinho e que o core 0.22.0 passa a avisar com `DeprecationWarning`).

### Alterado
- Depende de `quantilica-core>=0.22.0` (era `>=0.19.0`), que traz `extracted_archive`.

### Adicionado
- `anac_fetcher.reader.extracted_data(path)`: gerenciador de contexto que descompacta um ZIP/7z e sempre remove a raiz da extração; falhas sobem como `RuntimeError`, como em `decompress`.
- Testes: ZIP com subpasta sem resíduo de `quantilica_extract_*` no `TMPDIR` (`convert_one` e `lake build`) e sem `DeprecationWarning` do core.
- Testes: identidade do registro conferida.

## [0.8.0] - 2026-11-14

### Corrigido
- `aero-pistas-pouso` e `aero-posicoes-estacionamento` passam a ser lidos do JSON publicado junto (o CSV vem sem linha de cabeçalho: a primeira linha de dados virava os nomes das colunas). O arquivo do lake muda de `...-csv.parquet` para `...-json.parquet`: apague o antigo antes do `lake build --force`.
- Nomes de coluna inválidos (vazio, controle, quebra de linha, acima de 128 caracteres, repetido) são corrigidos na leitura; espaços nas pontas e `__UNNAMED__N` não mudam.

### Adicionado
- O fetcher declara os fatos da fonte (`FetcherInfo`: id canônico, apelidos, órgão, licença, página e cadência) para o registro de fetchers da Quantilica.

### Alterado
- Requer `quantilica-core>=0.19.0` (e `quantilica-cli>=0.17.0` como host).
- `FetcherInfo.licenca` passa a declarar a licença da fonte: Sem licença declarada; dados públicos pela Lei 12.527/2011 (LAI) e Decreto 8.777/2016.

## [0.7.1] - 2026-11-06

### Alterado
- O comando `discover` imprime pelo console Rich compartilhado em vez de `typer.echo`; as mensagens e a saída `--json` (JSON puro) não mudam.

## [0.7.0] - 2026-11-05

### Adicionado

- Comando `discover`: lista meses de `movimentacao` publicados no servidor além do
  último catalogado (`--json`, `--fail-on-change`).

### Corrigido

- `movimentacao`: o catálogo deixa de gerar meses sem arquivo no servidor
  (2026-01 a 2026-09 davam 404, pois a ANAC só publicou até 2025-12). O fim do
  catálogo é a constante `LAST_PUBLISHED`.

## [0.6.3] - 2026-11-04

### Corrigido
- Sem o extra `analysis`, o comando `convert` termina com código 1 e a instrução de instalação (`quantilica install anac --extra analysis`), sem traceback.

### Alterado
- O diretório de saída padrão (`/data/anac`) passa a ser declarado explicitamente no plugin; o valor não muda.

## [0.6.2] - 2026-11-04

### Corrigido
- Política de frescor volta a F2 (`HEAD_FALLBACK_GET`): `REMOTE_ONLY` (F3, para fontes sem validadores) causava re-download diário de fontes com Last-Modified/ETag, porque descartava o Last-Modified e o nome do arquivo caía em `@hoje`.
- A movimentação aeroportuária deixa de perder a primeira linha de dados nos CSV que
  começam direto pelo cabeçalho (sem a linha "Atualizado em"): antes essa linha virava
  o nome das colunas no Parquet. A linha de abertura só é descartada quando é mesmo
  "Atualizado em", com ou sem marca de ordem de bytes (BOM).
- `convert` não repete no Parquet as colunas que já são partição (`ANO` e `MES` na
  movimentação aeroportuária). Repetidas, elas sombreavam a partição `ano`/`mes` e o
  DuckDB devolvia valor nulo; a verificação do lake acusava a divergência.

### Alterado
- Exige `quantilica-core>=0.16.0`.

## [0.6.1] - 2026-10-30

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
