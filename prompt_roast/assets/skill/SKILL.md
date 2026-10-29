---
name: prompt-roast
description: Avalia a clareza de prompts e oferece feedback, histórico e comandos PromptRoast quando instalado ou solicitado.
---

# PromptRoast

Avalie mensagens elegíveis com a [rubrica](references/framework.md). Considere o contexto da conversa; uma continuação curta pode ser clara. Responda à tarefa do usuário normalmente. A nota é feedback subjetivo, não julgamento da pessoa. Não avalie saudações, comandos PromptRoast ou saídas automáticas de ferramentas.

Para cada mensagem elegível, classifique como `request` ou `question`, atribua três inteiros de 0 a 3 e identifique Butler e antipadrões conforme a rubrica. Use o núcleo Python configurado na instalação para calcular e gravar a nota; ele não recebe o texto do prompt. Crie uma sessão para o agente e projeto com `session new`, mantendo o ID na conversa; reutilize ID nativo quando disponível. Gere um ID de evento por mensagem e reutilize-o ao tentar novamente. Execute `record` com agente, projeto, sessão, evento, tipo, pilares e opções; use `score` para a média e o tom. Consulte `--help` para os parâmetros. Se a sessão for perdida, peça seleção ou crie uma nova, sem misturar conversas.

No fim da resposta final, inclua uma vez `📊 PromptRoast: X/10 [emoji] [título]`, média da sessão e `📝` seguido de feedback breve no idioma do usuário. Seja honesto e específico: justifique a nota com evidências do pedido ou do contexto, aponte a principal lacuna quando houver e sugira como preenchê-la. Não invente requisitos, falhas ou elogios; se não houver melhoria relevante, diga o que está claro sem superlativos. Não favoreça o usuário nem infle a nota. Em Butler Mode, identifique-o no rodapé. Em modo savage, use tom brincalhão de instrutor militar, sem mudar cálculo ou critérios. Não bloqueie nem desvie a tarefa.

Se Python ou o estado estiver inacessível, informe que a avaliação não foi registrada e não invente média; ainda responda normalmente.

## Operações

- `score`: consulte as estatísticas da sessão atual.
- `reset`: limpe apenas as notas da sessão atual.
- `savage on|off`: altere o tom da sessão atual.
- `help`: explique critérios, comandos e sintaxe do host.
- `setup-local` e `setup-global`: configure o escopo solicitado pelo usuário com o instalador, preservando seus arquivos.

Esses comandos são administrativos e não recebem nota. A invocação depende do agente: `$prompt-roast score` no Codex; `/prompt-roast score` no Cursor e Antigravity; `/prompt-roast:score` no Claude Code e Gemini CLI. Para executar o núcleo, use o caminho de runtime registrado na regra de ativação ou informado pelo instalador.
