# PromptRoast

Feedback local sobre a clareza de pedidos para agentes de IA. O modelo interpreta a conversa e atribui os três pilares; o Python valida os valores e calcula a nota. A avaliação é subjetiva e depende do modelo e das instruções disponíveis.

Requer Python 3.11 ou posterior, sem dependências externas de execução. Na pasta do projeto, teste o cálculo:

```bash
python3 -m prompt_roast evaluate --type request --p1 3 --p2 3 --p3 3
```

O resultado JSON contém `"score": 10`. A fórmula soma um ponto base aos três pilares (0 a 3); no modo Butler a base é zero. Antipadrões podem limitar a nota final. O cálculo não envia dados para serviços externos.

```bash
python3 -m unittest discover -s tests -v
```

## Histórico de sessão

Cada conversa usa um identificador próprio, associado ao agente e ao caminho do projeto. A sessão retorna um identificador: guarde-o para consultar ou retomar a conversa. O histórico contém somente as notas e seus metadados, sem o texto do prompt ou código.

Exemplo com estado temporário (Linux):

```bash
export PROMPT_ROAST_STATE_DIR=/tmp/prompt-roast-estado
SESSION_ID=$(python3 -m prompt_roast session new --agent codex --project . | python3 -c 'import json,sys; print(json.load(sys.stdin)["session"])')
python3 -m prompt_roast record --agent codex --project . --session "$SESSION_ID" --event exemplo-1 --type request --p1 2 --p2 3 --p3 2
python3 -m prompt_roast score --agent codex --project . --session "$SESSION_ID"
python3 -m prompt_roast savage on --agent codex --project . --session "$SESSION_ID"
python3 -m prompt_roast savage off --agent codex --project . --session "$SESSION_ID"
python3 -m prompt_roast reset --agent codex --project . --session "$SESSION_ID"
```

Sem `PROMPT_ROAST_STATE_DIR`, o estado fica em `${XDG_STATE_HOME:-~/.local/state}/prompt-roast`. Se o agente não tiver acesso de escrita ao diretório, autorize um diretório adequado e informe-o explicitamente por essa variável; falhas de acesso não produzem média fictícia. O reset apaga as notas apenas da sessão informada.

A avaliação não é uma medida científica nem garantia de que modelos diferentes atribuam a mesma nota; as regras adicionam contexto e podem consumir tokens. O agente continua responsável por interpretar o pedido e pode falhar em seguir as instruções.

## Instalação global no Codex

Para usar o PromptRoast em qualquer projeto do seu usuário, execute no terminal:

```bash
cd /caminho/para/prompt-roast
python3 -m prompt_roast setup-global --agent codex
python3 -m prompt_roast doctor --agent codex --scope global
```

Substitua o caminho acima pela pasta onde o PromptRoast foi baixado. Abra uma nova conversa no Codex, em qualquer projeto, envie um pedido e depois use `$prompt-roast score` na conversa. O diagnóstico confirma os arquivos instalados, mas a resposta do agente precisa ser testada na conversa.

Para preparar as integrações globais de todos os agentes, use `python3 -m prompt_roast setup-global --agent all`. No Cursor, é necessário também cadastrar a regra exibida pelo instalador nas User Rules. As integrações de outros agentes ainda precisam de testes reais.

## Instalação local e diagnóstico

Para preparar o Codex em um projeto específico, execute na pasta do código-fonte:

```bash
mkdir -p /tmp/prompt-roast-demo
python3 -m prompt_roast install --agent codex --scope local --project /tmp/prompt-roast-demo
python3 -m prompt_roast doctor --agent codex --scope local --project /tmp/prompt-roast-demo
```

A instalação local cria a skill em `.agents/skills/prompt-roast`, acrescenta um bloco delimitado a `AGENTS.md` e coloca o executável em `.prompt-roast/runtime`. Ela preserva instruções existentes e pode ser repetida. Para remover somente a integração do Codex desse projeto:

```bash
python3 -m prompt_roast uninstall --agent codex --scope local --project /tmp/prompt-roast-demo
```

O histórico e arquivos alterados pelo usuário são preservados. Use `--agent all` para preparar as cinco integrações. Para um teste em todos os projetos do seu usuário, `python3 -m prompt_roast setup-global --agent codex` configura a skill no diretório pessoal e adiciona a regra ao `AGENTS.md` global do Codex; `uninstall --agent codex --scope global` desfaz a integração. Confira o diagnóstico e abra uma nova conversa para que as instruções sejam carregadas.

A instalação do pacote Python convencional pode usar um ambiente virtual e `pip install .`; o runtime instalado nas integrações é autocontido e não modifica o Python global. `doctor` informa arquivos preparados e não afirma que o agente foi testado em uma conversa real.

## Opções no menu dos agentes

Depois de instalar ou atualizar a integração, abra uma nova conversa. No Codex, digite `$prompt-roast-` e selecione uma opção, como `$prompt-roast-score`, `$prompt-roast-reset`, `$prompt-roast-help`, `$prompt-roast-savage-on` ou `$prompt-roast-savage-off`. As opções de instalação `setup-global` e `setup-local` também aparecem. A opção selecionada é enviada como mensagem ao agente.

No Cursor e no Antigravity, digite `/prompt-roast-` para escolher uma opção equivalente. No Claude Code e no Gemini CLI, digite `/prompt-roast:` para encontrar os comandos, incluindo `score`, `reset`, `help`, `savage-on` e `savage-off`. A apresentação e a descoberta dependem da versão de cada aplicativo; esses menus precisam ser verificados em conversas reais. No Cursor global, as User Rules continuam sendo necessárias para a avaliação automática.

Para atualizar uma instalação já existente do Codex, execute novamente `python3 -m prompt_roast setup-global --agent codex` na pasta do projeto. Para os demais agentes, substitua `codex` pelo nome do agente ou use `all`.

## Comandos nos agentes

Depois de instalar a integração e iniciar uma nova conversa no projeto escolhido, use:

| Agente | Estatísticas | Outras operações |
| --- | --- | --- |
| Codex | `$prompt-roast score` | `$prompt-roast reset`, `help`, `savage on`, `savage off`, `setup-local`, `setup-global` |
| Cursor | `/prompt-roast score` | `/prompt-roast reset`, `help`, `savage on`, `savage off`, `setup-local`, `setup-global` |
| Antigravity App/IDE | `/prompt-roast score` | `/prompt-roast reset`, `help`, `savage on`, `savage off`, `setup-local`, `setup-global` |
| Claude Code | `/prompt-roast:score` | `/prompt-roast:reset`, `help`, `savage on`, `savage off`, `setup-local`, `setup-global` |
| Gemini CLI | `/prompt-roast:score` | `/prompt-roast:reset`, `help`, `savage on`, `savage off`, `setup-local`, `setup-global` |

Para Claude e Gemini, os nomes abreviados na última coluna também usam o prefixo `/prompt-roast:`. A skill deve avaliar mensagens elegíveis automaticamente depois de a regra ser carregada; os comandos acima são para consultar e controlar o comportamento.

O instalador também prepara pacotes nativos em `.prompt-roast/bundles/<agente>/prompt-roast`. Para testar o Claude Code como plugin em uma conversa separada, use `claude --plugin-dir /caminho/do/projeto/.prompt-roast/bundles/claude/prompt-roast`. Para Gemini, é possível fazer `gemini extensions link /caminho/do/projeto/.prompt-roast/bundles/gemini/prompt-roast` e reiniciar o Gemini CLI. Os caminhos devem apontar para o projeto onde os arquivos foram preparados; mantenha-os disponíveis enquanto a extensão estiver vinculada. Para evitar comandos duplicados, use esse teste em um projeto sem a integração gerenciada já ativa.

O Antigravity listado é o aplicativo/IDE, que usa skills e regras; o executável `agy` tem caminhos próprios e sua presença não prova que a IDE foi testada. No Cursor global, cadastre nas User Rules o texto exibido pelo instalador; o diagnóstico informará a etapa pendente. O modo local usa `.cursor/rules/prompt-roast.mdc`.

## Roteiro de teste no Codex

A instalação global prepara os arquivos; é necessário testar a resposta do agente em uma conversa. Abra a pasta `demo/` deste projeto em uma nova conversa do Codex e:

1. Envie um pedido com objetivo e contexto, por exemplo: “Explique o que é uma função em Python e mostre um exemplo curto.” Verifique a resposta e o rodapé PromptRoast.
2. Envie outro pedido com critérios claros e confira se a média mudou.
3. Envie somente “Olá” e verifique que não há nova nota.
4. Na conversa, envie `$prompt-roast score`; depois use `$prompt-roast savage on`, `$prompt-roast savage off` e `$prompt-roast reset`. Verifique que o reset limpa apenas a sessão atual.

Os quatro comandos acima são mensagens para o agente, não comandos do terminal. O terminal pode ser usado para verificar o pacote e sua instalação:

```bash
cd /caminho/para/prompt-roast
python3 -m unittest discover -s tests -v
python3 -m prompt_roast doctor --agent codex --scope global
```

Para remover a instalação global do Codex e conservar o histórico:

```bash
python3 -m prompt_roast uninstall --agent codex --scope global
```

## Situação das integrações nesta máquina

| Agente | Verificação nesta etapa |
| --- | --- |
| Codex | Instalação global e manifesto verificados; uma avaliação foi gravada na conversa atual. O roteiro completo em nova sessão está pendente: o Codex CLI retornou `model_not_found` antes de responder. |
| Cursor | Arquivos, regra local e comandos validados em diretório temporário; conversa real pendente. User Rules global exige etapa manual. |
| Antigravity App/IDE | Skill e regra `always_on` validadas em diretório temporário; conversa real pendente. A presença do CLI não confirma o teste da IDE. |
| Claude Code | Manifesto, hook e comandos validados estruturalmente; executável não encontrado no PATH e conversa real pendente. |
| Gemini CLI | Manifesto e TOMLs validados estruturalmente; executável não encontrado no PATH e conversa real pendente. |

Os testes estruturais não comprovam que cada modelo seguirá as instruções nem que cada versão do aplicativo exponha os comandos da mesma forma. Esta versão foi testada no Linux; Windows e macOS ainda não foram certificados.
