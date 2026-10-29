# Design

## Context

Ver `proposal.md` para motivação e `specs/` para os contratos. Este é um projeto novo: antes do planejamento a pasta estava vazia; não existem código, testes ou especificações legadas a migrar. SOSPlus é um projeto diferente e não integra esta mudança.

O ClaudeRoast examinado combina instruções Markdown, comandos declarativos, manifestos, scripts shell e um calculador Python. O calculador recebe notas previamente atribuídas pelo modelo; não compreende sozinho o texto do prompt. O PromptRoast manterá essa divisão, substituindo os scripts shell de instalação por Python.

Ambiente observado nesta máquina: Python 3.14.4; executáveis `codex`, `cursor`, `antigravity` e `agy` encontrados no PATH; `cursor --version` retornou 3.27.12 e `agy --version` retornou 1.1.27. `claude` e `gemini` não foram encontrados no PATH. Isso não prova ausência de extensões de editor e tampouco valida uma conversa real nos aplicativos. Nenhum host foi autenticado ou instalado nesta etapa.

## Goals / Non-Goals

**Goals:**
- Uma rubrica e um calculador compartilhados, com integração fina por host.
- Mesmo comportamento lógico dos seis comandos do original, histórico confiável e feedback contínuo depois da configuração.
- Instalação local testável sem rede, conta adicional, daemon ou alteração de shell.
- Preparação para distribuição open source posterior, com licença e atribuição.

**Non-Goals:**
- Criar um avaliador semântico independente do agente ou conectar APIs de modelos.
- Garantir notas idênticas entre modelos ou a obediência perfeita a instruções persistentes.
- Substituir agentes, contornar suas permissões, capturar teclado, ler todos os chats ou registrar prompts brutos.
- Publicar o projeto, criar conta, configurar marketplace público ou prometer execução no navegador sem acesso local.

## Decisions

### 1. Python e biblioteca padrão para toda lógica executável

Usar Python 3.11+, `argparse`, `json`, `pathlib`, `tempfile`, `os`, `hashlib`, `uuid`, `datetime`, `fcntl` e `zipapp`; `unittest` nos testes. Não haverá dependências externas de runtime. Markdown, JSON, TOML e MDC serão somente formatos declarativos exigidos pelos hosts. Python 3.11 permite testar os TOML gerados com `tomllib`.

A organização inicial será `prompt_roast/__main__.py`, `cli.py`, `scoring.py`, `state.py`, `integrations.py` e recursos em `prompt_roast/assets/`, mais `tests/`, `pyproject.toml`, `README.md`, `LICENSE` e `THIRD_PARTY_NOTICES.md`. Manter os componentes pequenos; não criar uma hierarquia de classes para adaptadores ou um framework de plugins interno.

Alternativas: replicar a lógica em cada host facilitaria divergência; Node/MCP e serviço remoto adicionariam runtime e configuração sem resolver a avaliação contínua por si só. Foram descartados.

### 2. Modelo interpreta; núcleo valida, calcula e registra

Uma única skill `prompt-roast` e referências de rubrica/exemplos instruirão o agente a classificar a mensagem, considerar o contexto anterior e atribuir pilares. A chamada Python levará somente valores estruturados. O próprio agente redigirá o feedback com base no resultado calculado. A mensagem do usuário será dado para avaliação, nunca um trecho executável incorporado ao comando.

O cálculo é `min((0 if butler else 1) + p1 + p2 + p3, limite_do_antipadrao)`. Validar pilares, tipo e antipadrão antes de produzir resultado ou alterar estado. Reaproveitar os títulos/emoji do original, inclusive Tony Stark para 10 e Hail Mary para 0, conservando os créditos aplicáveis. `savage` muda apenas instruções de tom.

O rodapé aparece uma vez ao fim da resposta final, não em cada atualização intermediária. Mensagens automáticas, saudações e operações administrativas ficam fora da avaliação. A rubrica servirá como coaching; não fará alegações clínicas sobre perda cognitiva.

Alternativa: heurística por palavras-chave seria previsível, mas perderia contexto e penalizaria continuações legítimas. Não será usada como substituta do modelo.

### 3. CLI com contrato explícito

Interface planejada, ainda não implementada:

```text
python3 -m prompt_roast --help
python3 -m prompt_roast evaluate --type request --p1 3 --p2 3 --p3 3
python3 -m prompt_roast session new --agent codex --project .
python3 -m prompt_roast record --agent codex --project . --session <id> --event <id> --type request --p1 3 --p2 3 --p3 3
python3 -m prompt_roast score --agent codex --project . --session <id>
python3 -m prompt_roast reset --agent codex --project . --session <id>
python3 -m prompt_roast savage on --agent codex --project . --session <id>
python3 -m prompt_roast install --agent all --scope local --project /tmp/prompt-roast-demo
python3 -m prompt_roast setup-global --agent codex
python3 -m prompt_roast setup-local --agent codex --project /tmp/prompt-roast-demo
python3 -m prompt_roast doctor --agent all --scope local --project /tmp/prompt-roast-demo
python3 -m prompt_roast uninstall --agent all --scope local --project /tmp/prompt-roast-demo
```

`evaluate` é puro; `record` calcula e grava usando o mesmo código de cálculo. As saídas estruturadas serão JSON em stdout; ajuda e mensagens de erro serão legíveis, com erros em stderr e status não zero. Os comandos no chat traduzem as operações para a mesma CLI. `setup-local/global` reutiliza a configuração de `install` em vez de manter implementações separadas.

### 4. Um estado JSON por sessão, sem memória específica de fornecedor

Diretório padrão no Linux: `${XDG_STATE_HOME:-~/.local/state}/prompt-roast/`. Permitir `PROMPT_ROAST_STATE_DIR` como substituição explícita para testes e ambientes de agentes com acesso restrito. Nenhum diretório alternativo será escolhido silenciosamente após erro de permissão.

Chave de arquivo derivada por hash de agente, caminho canônico do projeto e identificador de sessão. Não usar identificadores recebidos como segmentos livres de caminho. Cada documento conterá `schema_version`, agente, identificadores opacos de projeto/sessão, `tone` e `scores`. Cada evento conterá `event_id`, timestamp UTC, tipo, pilares, base, Butler Mode, antipadrão e total; sem prompt bruto, feedback textual, código ou segredos. Recalcular as estatísticas a partir dos eventos, sem manter uma média redundante como fonte de verdade.

O adaptador usa um identificador nativo documentado quando disponível. Caso contrário, a skill inicia uma sessão por CLI e guarda o identificador na conversa, nunca em um arquivo global de sessão atual. Se o identificador for perdido, pedir seleção ou iniciar uma sessão nova explicitamente, sem misturar conversas. UUID de evento será reutilizado em repetição da mesma gravação; notas diferentes com o mesmo ID serão erro.

Gravação protegida com `fcntl.flock` em arquivo lateral e troca atômica de arquivo temporário no mesmo diretório. A seção protegida inclui leitura, validação, alteração e substituição. Arquivos privados e diretórios com permissões restritas; não seguir links de estado para fora do destino. JSON inválido ou versão desconhecida gera erro preservando os bytes existentes. Esta primeira implementação será validada no Linux; não introduzir emulação de locks no Windows antes de existir demanda/teste.

Média arredondada a uma casa; tendência desconhecida até três eventos e depois comparação da primeira/última nota da janela de até cinco. `reset` esvazia eventos da sessão, conservando tom; uma nova sessão começa normal.

Alternativas: `/memories` não é uniforme entre agentes; um único JSON global mistura conversas; SQLite resolveria concorrência, mas altera o armazenamento do original sem necessidade neste volume. Foram descartados para esta versão.

### 5. Recursos compartilhados e adaptadores declarativos

Preferir a descoberta padrão de Agent Skills. No escopo local, Codex, Cursor e Antigravity compartilharão `.agents/skills/prompt-roast/`. Evitar registrar cópias adicionais em diretórios que o mesmo host também varre. Claude e Gemini terão comandos nativos que referenciam a mesma rubrica, além de suas instruções persistentes. No global, cada host usará seus diretórios documentados, deduplicando os destinos que coincidirem.

| Host | Arquivos e ativação planejados | Invocação no chat |
| --- | --- | --- |
| Claude Code | Comandos Markdown em `.claude/commands/prompt-roast/`, bloco no `CLAUDE.md`; no global, equivalentes em `~/.claude/`. Também gerar bundle `.claude-plugin/plugin.json`, `skills/` e `commands/` para carregamento nativo local. | `/prompt-roast:score`, `reset`, `help`, `setup-global`, `setup-local`, `savage on/off` |
| Codex | Skill em `.agents/skills/prompt-roast/` ou `~/.agents/skills/prompt-roast/`; bloco em `AGENTS.md` local ou no `AGENTS.md` do diretório de configuração do Codex, respeitando `CODEX_HOME`. Preparar manifesto `.codex-plugin/plugin.json` para distribuição posterior; o teste local não dependerá de marketplace. | `$prompt-roast score` e demais subcomandos; descoberta via `/skills` |
| Cursor | Skill em `.agents/skills/prompt-roast/` local ou `~/.agents/skills/prompt-roast/` global. Regra local `.cursor/rules/prompt-roast.mdc` com `alwaysApply: true`. No global, fornecer o texto para User Rules na interface e informar pendência até sua aplicação. | `/prompt-roast score` e demais subcomandos |
| Gemini CLI | Comandos TOML em `.gemini/commands/prompt-roast/`, bloco em `GEMINI.md`; equivalentes globais em `~/.gemini/`. Gerar bundle com `gemini-extension.json`, contexto e comandos para instalação/link nativo. | `/prompt-roast:score` e demais aliases |
| Antigravity App/IDE | Skill em `.agents/skills/prompt-roast/` local ou `~/.gemini/config/skills/prompt-roast/` global; regra em `.agents/rules/prompt-roast.md` ou `~/.gemini/config/rules/prompt-roast.md`, com `trigger: always_on`. | `/prompt-roast score` e demais subcomandos |

As operações pertencem à mesma skill, sem criar seis skills para contornar sintaxe de comandos. Para Claude, os arquivos de comandos e o bundle nativo deverão expor aliases equivalentes; para Gemini, namespace nasce do diretório TOML. A instalação gerenciada e o carregamento nativo alternativo não deverão ficar ativos juntos no mesmo host com cópias duplicadas.

A documentação atual do Antigravity favorece skills e apresenta migração de workflows legados; não usar workflows antigos como caminho principal. Antigravity CLI possui caminhos globais próprios: detectar essa superfície e informar que o alvo inicial `antigravity` é App/IDE; não confundir a presença de `agy` com validação da IDE.

Cursor não oferece nas páginas consultadas um contrato de arquivo global de User Rules que autorize editar seu armazenamento interno. Por isso a instalação global cobre a skill, entrega a regra e relata etapa manual; o escopo local será o caminho completo para um teste automático. Essa limitação faz parte dos critérios de aceitação, não é falha a esconder.

### 6. Runtime utilizável de qualquer diretório

O instalador Python criará uma pequena aplicação `.pyz` autossuficiente usando `zipapp`, contendo o pacote e seus recursos. No escopo local ficará em `<projeto>/.prompt-roast/runtime/prompt-roast.pyz`; no global em `${XDG_DATA_HOME:-~/.local/share}/prompt-roast/runtime/prompt-roast.pyz`. Os templates gerados referenciarão o interpretador validado e o caminho real desse runtime, com quoting seguro. Assim o host não depende do diretório corrente, de `PYTHONPATH`, de alias de shell nem de mover o código-fonte.

O pacote também fornecerá entrypoint `prompt-roast` para uma instalação Python convencional. Testar tanto `python3 -m prompt_roast` no código-fonte quanto execução do runtime gerado fora da raiz. O instalador não executará `pip` global, instalará agentes ou mudará o PATH do usuário. `doctor` detectará runtime ou interpretador removido e indicará reinstalação.

Alternativas: referenciar somente o checkout falha ao mudar de diretório ou remover a pasta; exigir ambiente virtual fixo torna o setup mais frágil. O zipapp usa a biblioteca padrão e mantém uma instalação local transportável.

### 7. Alterações de configuração com propriedade explícita

Blocos em arquivos compartilhados usarão marcadores `<!-- prompt-roast:start -->` e `<!-- prompt-roast:end -->`. O manifesto de instalação registrará apenas destinos gerenciados e hashes do conteúdo próprio; arquivos do usuário serão lidos apenas quando forem destinos de configuração, nunca credenciais ou histórico dos hosts.

Preparar e validar os arquivos antes de substituir; preservar o conteúdo externo ao bloco byte a byte. Duplicação/marcadores inconsistentes, arquivos sem propriedade reconhecida ou symlinks que desviem do destino são erros. Não remover instalações antigas antes de preparar as novas. Reinstalar o mesmo conteúdo é idempotente. `--agent all` deduplica recursos compartilhados e relata sucesso/pendências/erros individualmente; falhas não autorizam apagar configurações válidas dos outros agentes.

Desinstalar somente arquivos próprios cujo conteúdo não foi modificado e o bloco exato do produto em arquivos compartilhados. Preservar arquivos alterados e histórico, listando o que ficou. Recursos compartilhados só serão removidos quando nenhum adaptador gerenciado ainda precisar deles. Não editar `~/.bashrc`, `~/.zshrc`, caches privados dos hosts ou arquivos do SOSPlus.

### 8. Verificação e distribuição honesta

Testes `unittest` cobrirão cálculo e entradas inválidas; estatísticas e isolamento; idempotência de eventos; reset/tom; JSON inválido e escrita simultânea; instalação/reinstalação/desinstalação preservando arquivos; parsing de JSON/TOML e frontmatter; execução da `.pyz` fora do checkout. Todas as mutações de testes ocorrerão em diretórios temporários com HOME/config/estado simulados.

A instalação de arquivos não será registrada como teste funcional no aplicativo. Um roteiro por host verificará descoberta, duas mensagens elegíveis, uma saudação, `score`, `reset` e `savage on/off`. Testes com a conta do usuário respeitarão permissões do host. Sem executável/autenticação, registrar como pendente e fornecer comandos, mantendo a implementação dos cinco adaptadores no escopo.

Adicionar MIT ao projeto e `THIRD_PARTY_NOTICES.md` com origem e aviso MIT do ClaudeRoast se houver adaptação de conteúdo/código. Nome PromptRoast é provisório: não foi verificada disponibilidade em PyPI/GitHub ou marca. Publicação e reserva de nome ficam fora desta mudança.

## Risks / Trade-offs

- [O modelo ignora o rodapé ou interpreta a rubrica de forma diferente] → Regras persistentes curtas, exemplos compartilhados e teste real documentado; apresentar a nota como feedback subjetivo.
- [Host bloqueia execução ou escrita de estado] → Mostrar a limitação e solicitar acesso pelos meios do host; permitir caminho de estado explicitamente configurado; não inventar média.
- [Diferentes hosts descobrem a mesma skill mais de uma vez] → Destinos compartilhados deduplicados e verificação dos seletores; não ativar dois métodos de instalação simultaneamente.
- [Versão do host diverge da documentação] → Adaptadores declarativos, `doctor`, registro das versões testadas e pendências visíveis.
- [Cursor global requer ação manual] → Entregar texto da User Rule e orientar teste local como caminho completo; não manipular banco interno de preferências.
- [Lock de arquivos não é portátil para Windows] → Certificar somente Linux inicialmente e emitir erro claro nas operações não suportadas.
- [Instruções adicionais consomem contexto e tokens] → Regra de ativação curta, referências carregadas sob demanda e feedback breve.

## Migration Plan

1. Implementar e validar CLI, estado e recursos em uma pasta independente; não executar alterações em SOSPlus.
2. Gerar instalações locais dos cinco adaptadores em projetos temporários e testar preservação e remoção.
3. Preparar uma instalação de teste real do PromptRoast em projeto próprio; instalar somente os destinos de agentes solicitados para uso, listando etapas manuais.
4. Executar os smoke tests dos hosts disponíveis e registrar explicitamente os demais como pendentes.
5. Entregar ao usuário o código, os comandos finais de teste e o procedimento de desinstalação. Nenhum envio remoto nesta mudança.
6. Para reverter, remover somente a instalação gerenciada do destino selecionado; manter histórico e arquivos modificados pelo usuário.

## References

Consultas em 28/10/2026; contratos atuais serão conferidos novamente se a implementação ocorrer após mudanças relevantes dos hosts.

- [ClaudeRoast: origem](https://github.com/chadbyte/claude-roast), [calculador](https://github.com/chadbyte/claude-roast/blob/main/skills/claude-roast/scripts/score.py) e [licença MIT](https://github.com/chadbyte/claude-roast/blob/main/LICENSE).
- [Codex: skills e invocação](https://learn.chatgpt.com/docs/build-skills) e [AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md).
- [Claude Code: manifestos e componentes](https://code.claude.com/docs/en/plugins-reference).
- [Gemini CLI: comandos](https://geminicli.com/docs/cli/custom-commands/), [extensões](https://geminicli.com/docs/extensions/reference/) e [contexto GEMINI.md](https://geminicli.com/docs/cli/gemini-md/).
- [Cursor: skills](https://cursor.com/docs/skills), [regras](https://cursor.com/docs/rules) e [plugins](https://cursor.com/docs/plugins).
- [Antigravity: skills](https://antigravity.google/docs/skills/), [regras](https://antigravity.google/docs/rules/) e [migração de workflows](https://antigravity.google/docs/migration/workflows-to-skills).
