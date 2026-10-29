# Tasks

## 1. Pacote e avaliação numérica

- [x] 1.1 Criar o pacote `prompt_roast`, entrypoint por módulo e metadados em `pyproject.toml` para Python 3.11+ sem dependências externas de runtime; verificar `python3 -m prompt_roast --help` e a execução a partir de ambiente virtual isolado.
- [x] 1.2 Implementar cálculo único com pilares 0 a 3, Butler Mode, limites de antipadrões e títulos do original; verificar testes `unittest` para máximos normal/Butler, todos os limites e entradas inválidas, inclusive na função pública.
- [x] 1.3 Expor `evaluate` com JSON em stdout e erros legíveis em stderr; verificar chamadas válidas, tipo/antipadrão desconhecidos e saída não zero sem escrita em disco.
- [x] 1.4 Documentar no README o primeiro teste numérico, a fórmula e a divisão entre interpretação do agente e cálculo Python; executar o exemplo documentado e confirmar nota 10 para três pilares de valor 3.

## 2. Histórico, sessão e tom

- [x] 2.1 Implementar identidade por agente/projeto/sessão, `session new` e diretório de estado configurável, com metadados mínimos e sem prompts brutos; verificar isolamento com dois agentes, dois projetos e duas sessões em diretórios temporários.
- [x] 2.2 Implementar `record` idempotente por evento, validação de esquema JSON e gravação atômica sob lock no Linux; verificar repetição, conflito do mesmo ID, arquivo inválido, falha durante gravação e concorrência sem perda silenciosa.
- [x] 2.3 Implementar `score`, média, cinco notas recentes e tendência conforme a especificação; verificar sessão vazia, notas 4/7/9 com média 6,7, tendência indisponível antes de três eventos e janela limitada a cinco.
- [x] 2.4 Implementar `reset` e `savage on|off` limitados à sessão; verificar preservação de outras sessões, conservação do tom após reset e nova sessão em modo normal.
- [x] 2.5 Documentar seleção/recuperação de sessão, diretório de estado, privacidade e erros de permissão; verificar os exemplos completos de criação, registro, consulta, savage e reset em estado temporário.

## 3. Skill e contrato de feedback

- [x] 3.1 Criar uma skill `prompt-roast`, rubrica e exemplos compartilhados com classificação de pedidos/perguntas, contexto de continuações, limites de antipadrões e Butler Mode; verificar casos de pedido completo, pergunta exploratória e continuação curta contra `specs/prompt-evaluation/spec.md`.
- [ ] 3.2 Instruir a skill a iniciar/reutilizar sessão, registrar uma vez por mensagem elegível e apresentar um único rodapé após a resposta final; verificar exemplos de saudação, comando administrativo, interrupção/repetição e execução bloqueada sem média inventada.
- [x] 3.3 Definir roteamento das seis operações e feedback normal/savage na mesma skill, com exemplos em português e comportamento no idioma do usuário; verificar que as duas apresentações do mesmo resultado mantêm nota e critérios.
- [x] 3.4 Documentar limites da avaliação subjetiva e o consumo adicional de contexto; verificar que README e skill não prometem medição científica, obediência perfeita nem notas iguais entre modelos.

## 4. Instalação gerenciada e runtime

- [x] 4.1 Implementar geração do runtime `.pyz` com recursos e seleção local/global, usando somente biblioteca padrão; verificar execução fora do checkout, caminho com espaços e funcionamento após remover uma cópia temporária do código-fonte.
- [x] 4.2 Implementar escrita idempotente de blocos delimitados, manifesto de propriedade e pré-validação de destinos; verificar preservação byte a byte do conteúdo externo, reinstalação, colisões, marcadores inválidos e links que escapem do destino.
- [x] 4.3 Implementar `install`, `setup-local` e `setup-global` compartilhando a mesma configuração por agente/escopo, com recursos comuns deduplicados; verificar dois installs sucessivos de `all` e seleção individual sem duplicar skill nem remover integração anterior.
- [x] 4.4 Implementar `uninstall` preservando histórico e arquivos modificados, removendo recursos comuns somente quando não forem mais usados; verificar remoção parcial de um agente, regras pessoais intactas e relatório dos arquivos preservados.
- [x] 4.5 Documentar instalação via código-fonte e pacote, destinos alterados, reinstalação e desinstalação; executar os comandos em HOME e projetos temporários, sem alterar configurações reais.

## 5. Adaptadores e comandos dos cinco agentes

- [x] 5.1 Implementar integração Claude Code com comandos Markdown, bloco em `CLAUDE.md` e bundle nativo com `.claude-plugin/plugin.json`; verificar os seis aliases `/prompt-roast:<operação>`, caminhos internos e chamada do runtime com fixtures. Documentar a escolha entre instalação gerenciada e `--plugin-dir`, evitando ativação duplicada.
- [x] 5.2 Implementar integração Codex com skill na descoberta `.agents/skills`, bloco local/global em `AGENTS.md` e manifesto `.codex-plugin/plugin.json`; verificar respeito ao diretório configurado do Codex e comandos `$prompt-roast <operação>` em fixtures. Documentar reinício/descoberta sem depender de marketplace nesta etapa.
- [x] 5.3 Implementar integração Cursor com skill compartilhada e regra local `.mdc`; verificar `alwaysApply: true`, ausência de cópias duplicadas e pendência explícita de User Rules na instalação global. Documentar o texto e o caminho da etapa manual, sem editar preferências internas do editor.
- [x] 5.4 Implementar integração Gemini CLI com seis comandos TOML, bloco em `GEMINI.md` e bundle `gemini-extension.json`; verificar parsing por `tomllib`/JSON, namespaces e chamada do mesmo núcleo. Documentar instalação ou link local da extensão como alternativa, com comandos confirmados na documentação oficial.
- [x] 5.5 Implementar integração Antigravity App/IDE com skill e regra `trigger: always_on`, nos destinos locais/globais documentados; verificar frontmatter e descoberta estrutural com fixtures. Documentar `/prompt-roast <operação>` e distinguir a IDE do CLI `agy`, sem depender de workflows legados.
- [x] 5.6 Implementar `doctor` para os cinco alvos, runtime, acesso ao estado, arquivos e pendências; verificar cenários de agente ausente, runtime ausente, Cursor global pendente e instalação estrutural sem teste real, sem resultados falsos de sucesso.

## 6. Licença e teste integrado local

- [x] 6.1 Adicionar MIT e avisos/atribuição de trechos reaproveitados do ClaudeRoast; verificar que a distribuição inclui licença e `THIRD_PARTY_NOTICES.md`, sem dados da máquina ou arquivos de estado.
- [x] 6.2 Executar `python3 -m unittest discover -s tests -v` e um fluxo completo em projeto temporário: instalar `all`, diagnosticar, avaliar, registrar, consultar, mudar tom, reiniciar e desinstalar; verificar JSON, preservação de conteúdo e ausência de modificações nos projetos SOSPlus.
- [x] 6.3 Preparar o projeto próprio de demonstração e uma instalação real para os agentes escolhidos pelo usuário, listando destinos e passos manuais; verificar o diagnóstico sem confundir geração de arquivos com descoberta na interface.
- [ ] 6.4 Executar o roteiro funcional nos hosts disponíveis: descoberta do comando/skill, duas mensagens avaliáveis, saudação sem nota, estatísticas, savage on/off e reset; registrar versão, resultado e pendências de cada host. Onde faltar executável ou autenticação, entregar o roteiro e declarar o teste pendente sem eliminar o adaptador.
- [x] 6.5 Entregar uma tabela final de compatibilidade e comandos exatos de instalação, teste e remoção que correspondam à implementação entregue; verificar cada comando local reproduzível e distinguir os comandos a executar dentro do chat dos comandos do terminal.

## Workflow follow-up

- Avaliar com o usuário o nome definitivo, a disponibilidade em registros públicos e a publicação open source no GitHub após validar o uso local.
- Arquivar esta mudança somente depois da implementação, verificação e revisão solicitadas pelo usuário.
