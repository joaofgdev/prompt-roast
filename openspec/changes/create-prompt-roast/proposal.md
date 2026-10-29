# Proposal

## Why

O ClaudeRoast oferece feedback sobre a clareza dos prompts, mas sua distribuição é voltada ao Claude Code. O PromptRoast levará a mesma experiência a Claude Code, Codex, Cursor, Gemini CLI e Antigravity, com instalação local, comandos equivalentes e um único núcleo Python.

## What Changes

- Criar o projeto independente `prompt-roast`, começando pelo Linux desta máquina, com Python 3.11+, biblioteca padrão, Markdown e manifestos JSON/TOML próprios dos agentes.
- Reproduzir os critérios de pedidos e perguntas: três pilares de 0 a 3, ponto base, Butler Mode, limites por antipadrão, títulos por nota e feedback curto que nunca bloqueia a tarefa.
- Fazer o modelo do agente interpretar o prompt; usar Python para validar os pontos, calcular a nota e manter histórico local por agente, projeto e sessão. Nenhuma API adicional ou chave será exigida.
- Entregar operações `score`, `reset`, `help`, `setup-global`, `setup-local` e `savage on|off`, com aliases nativos onde suportados e uma skill `prompt-roast` com subcomandos nos demais agentes.
- Permitir instalação por agente ou para todos, configuração local/global, diagnóstico e desinstalação preservando instruções existentes e dados do usuário. Declarar passos manuais quando o host não oferecer configuração global por arquivos documentados.
- Preparar documentação em português, comandos reproduzíveis de teste, licença MIT e atribuição ao ClaudeRoast quando houver reaproveitamento. Publicação no GitHub ficará para outra etapa.

## Capabilities

### New Capabilities

- `prompt-evaluation`: critérios compartilhados, cálculo validado, feedback normal/savage e apresentação da nota ao final da resposta.
- `session-feedback`: identificação de sessões, histórico local, estatísticas, reinício e estado de tom isolados.
- `agent-installation`: CLI Python, adaptadores dos cinco agentes, configuração reversível, diagnóstico e instruções de instalação/teste.

### Modified Capabilities

Nenhuma; o projeto foi criado vazio e não possui especificações anteriores.

## Impact

- Novos componentes planejados: pacote Python `prompt_roast`, skill e referências compartilhadas, templates de integração, testes com `unittest` e documentação.
- Instalação afetará somente os destinos escolhidos explicitamente: regras e skills dos agentes e diretório privado de dados do PromptRoast. Não haverá alterações no SOSPlus nem edição automática de arquivos do shell.
- A avaliação semântica depende do modelo e das permissões do agente. A mesma entrada de pontos deverá produzir a mesma nota em todos os adaptadores; notas idênticas para interpretações de modelos diferentes não são garantidas.
- Fora do escopo inicial: serviço web, painel, MCP, modelo próprio, telemetria, publicação em marketplaces/PyPI/GitHub e certificação de Windows/macOS. Compatibilidade universal significa estes cinco agentes locais, não os sites de chat sem acesso ao computador.
