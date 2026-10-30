# 🔥 PromptRoast

Avalie a clareza dos seus pedidos para agentes de IA e receba sugestões diretas para melhorá-los. O feedback é uma estimativa do agente, não uma medida científica.

## 1. Prepare sua máquina

Você precisa de **Git**, **Python 3.11 ou mais recente** e do agente que deseja usar instalado e autenticado. Execute os comandos no terminal, um bloco por vez.

### 🐧 Linux

No Ubuntu ou Debian, instale Git e Python:

```bash
sudo apt update
sudo apt install -y git python3
python3 --version
git --version
```

Se a versão mostrada for inferior a 3.11, instale uma versão mais recente do Python. Em outras distribuições, instale Git e Python pelo gerenciador de pacotes da sua distribuição.

Baixe o PromptRoast e entre na pasta:

```bash
git clone https://github.com/joaofgdev/prompt-roast.git
cd prompt-roast
python3 -m prompt_roast evaluate --type request --p1 3 --p2 3 --p3 3
```

O último comando deve mostrar `"score": 10`.

### 🪟 Windows

Abra o **PowerShell**. Se Git e Python ainda não estiverem instalados, execute:

```powershell
winget install --id Git.Git -e
winget install --id Python.Python.3.13 -e
```

Feche e abra o PowerShell novamente. Confira as versões e baixe o projeto:

```powershell
py -3 --version
git --version
git clone https://github.com/joaofgdev/prompt-roast.git
cd prompt-roast
py -3 -m prompt_roast evaluate --type request --p1 3 --p2 3 --p3 3
```

O Python deve ser 3.11 ou mais recente e o último comando deve mostrar `"score": 10`. Para testar com Claude Code no Windows, veja também o [guia de demonstração](README-WINDOWS-CLAUDE.md).

## 2. Instale no seu agente de IA

Ainda no terminal, **dentro da pasta `prompt-roast`**, escolha seu agente e execute o bloco correspondente ao seu sistema. A instalação é para seu usuário e pode ser usada em diferentes projetos. Repita para cada agente que quiser usar.

### Codex

Linux:

```bash
python3 -m prompt_roast setup-global --agent codex
python3 -m prompt_roast doctor --agent codex --scope global
```

Windows (PowerShell):

```powershell
py -3 -m prompt_roast setup-global --agent codex
py -3 -m prompt_roast doctor --agent codex --scope global
```

### Claude Code

Linux:

```bash
python3 -m prompt_roast setup-global --agent claude
python3 -m prompt_roast doctor --agent claude --scope global
```

Windows (PowerShell):

```powershell
py -3 -m prompt_roast setup-global --agent claude
py -3 -m prompt_roast doctor --agent claude --scope global
```

### Gemini CLI

Linux:

```bash
python3 -m prompt_roast setup-global --agent gemini
python3 -m prompt_roast doctor --agent gemini --scope global
```

Windows (PowerShell):

```powershell
py -3 -m prompt_roast setup-global --agent gemini
py -3 -m prompt_roast doctor --agent gemini --scope global
```

### Cursor

Linux:

```bash
python3 -m prompt_roast setup-global --agent cursor
python3 -m prompt_roast doctor --agent cursor --scope global
```

Windows (PowerShell):

```powershell
py -3 -m prompt_roast setup-global --agent cursor
py -3 -m prompt_roast doctor --agent cursor --scope global
```

No Cursor, copie também a regra exibida em **AÇÃO NECESSÁRIA** para **Settings → Rules → User Rules**. Essa etapa ativa a avaliação automática; os comandos ficam disponíveis separadamente.

### Antigravity IDE

Linux:

```bash
python3 -m prompt_roast setup-global --agent antigravity
python3 -m prompt_roast doctor --agent antigravity --scope global
```

Windows (PowerShell):

```powershell
py -3 -m prompt_roast setup-global --agent antigravity
py -3 -m prompt_roast doctor --agent antigravity --scope global
```

O diagnóstico indica se os arquivos foram preparados; ele não confirma se o agente seguirá as instruções. Se o instalador apontar conflito com um arquivo existente, preserve-o e confira o caminho informado.

## 3. Teste no chat

1. Feche a sessão anterior do agente e abra uma nova conversa, em qualquer projeto.
2. Envie um pedido com objetivo e contexto. Procure o rodapé **PromptRoast** na resposta.
3. Consulte as notas escolhendo a opção no menu do agente:

| Agente | Digite no chat e selecione |
| --- | --- |
| Codex | `$prompt-roast-score` |
| Claude Code | `/prompt-roast:score` |
| Gemini CLI | `/prompt-roast:score` |
| Cursor | `/prompt-roast-score` |
| Antigravity IDE | `/prompt-roast-score` |

Outras opções incluem `help`, `reset`, `savage-on` e `savage-off`. Digite o prefixo do seu agente para procurá-las. Esses comandos são mensagens para o agente, não comandos do terminal.

## Atualizar ou remover

Para atualizar, na pasta do projeto execute `git pull` e rode novamente o comando de instalação do agente. Para remover, substitua `codex` pelo agente desejado:

```bash
# Linux
python3 -m prompt_roast uninstall --agent codex --scope global
```

```powershell
# Windows
py -3 -m prompt_roast uninstall --agent codex --scope global
```

A remoção preserva o histórico e arquivos alterados pelo usuário. O histórico guarda notas e metadados, sem o texto completo dos prompts.

## Para desenvolver

- `prompt_roast/`: código Python e arquivos usados pelo instalador. A skill principal e sua rubrica ficam em `prompt_roast/assets/skill/`.
- `tests/`: testes automatizados. Execute `python3 -m unittest discover -s tests` (no Windows, `py -3 -m unittest discover -s tests`).
- `README-WINDOWS-CLAUDE.md`: guia de instalação e teste no Windows.

As skills e regras geradas por uma instalação local são configurações da máquina ou do projeto onde foram instaladas. Para alterar o comportamento distribuído, edite os arquivos de origem e execute os testes.

---

**Estado do projeto:** demonstração em desenvolvimento. O comportamento em cada agente e no Windows ainda precisa de testes em conversas reais; os menus e as permissões dependem da versão do aplicativo. [Licença MIT](LICENSE) · Inspirado em [ClaudeRoast](https://github.com/chadbyte/claude-roast).
