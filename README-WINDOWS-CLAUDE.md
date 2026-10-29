# PromptRoast — demonstração no Windows com Claude Code

Esta é uma versão de demonstração do PromptRoast para experimentar feedback sobre seus pedidos no **Claude Code**. A avaliação é uma sugestão feita pelo modelo, não uma medida objetiva. Esta versão ainda precisa ser testada em um Windows real.

## 1. O que você precisa

- Windows com **Python 3.13 ou mais recente** e o inicializador `py`. Ao instalar o Python, escolha a opção de adicionar o Python ao PATH.
- Claude Code instalado e autenticado no seu computador. O Claude Code pode funcionar no PowerShell; o Git for Windows é opcional para usar o Git Bash. Consulte a [instalação oficial do Claude Code](https://code.claude.com/docs/en/setup).
- A pasta do projeto extraída do ZIP do GitHub (botão **Code → Download ZIP**) ou clonada com Git.

Esta demonstração usa o Claude Code local. Não foi criada para a página de conversas do Claude no navegador.

## 2. Abra o PowerShell na pasta da demonstração

1. Extraia o arquivo ZIP.
2. Abra a pasta extraída do projeto: ela deve conter este README e a pasta `prompt_roast`.
3. Na barra de endereço do Explorador de Arquivos, digite `powershell` e pressione Enter. O PowerShell será aberto nessa pasta.
4. Confira os programas:

```powershell
py -3 --version
claude --version
```

Confirme que o Python é 3.13 ou superior. Se `py` não for reconhecido, instale o Python e abra o PowerShell novamente; se sua instalação usar `python` em vez de `py -3`, substitua `py -3` por `python` nos exemplos.

## 3. Faça um teste do cálculo

Ainda no PowerShell, execute:

```powershell
py -3 -m prompt_roast evaluate --type request --p1 3 --p2 3 --p3 3
```

O resultado deve conter `"score": 10`. Esse comando verifica o cálculo sem instalar a integração no Claude.

## 4. Instale para o seu usuário do Claude Code

```powershell
py -3 -m prompt_roast setup-global --agent claude
py -3 -m prompt_roast doctor --agent claude --scope global
```

O instalador prepara os comandos do Claude, a skill e o programa Python. Ele acrescenta uma seção delimitada ao seu arquivo de instruções `~/.claude/CLAUDE.md`, preservando as demais regras. Se encontrar arquivos com o mesmo nome que não foram criados pelo PromptRoast, informará a colisão em vez de sobrescrevê-los.

O diagnóstico informa se os arquivos foram preparados. Isso não confirma o comportamento em uma conversa real. O histórico fica no perfil do usuário, normalmente em `.local/state/prompt-roast`, e contém notas e metadados, sem o texto completo dos prompts. As permissões efetivas da pasta dependem da configuração do Windows.

## 5. Teste no Claude Code

Feche qualquer sessão anterior do Claude Code e inicie uma nova:

```powershell
claude
```

No chat do Claude, envie uma pergunta ou um pedido, por exemplo:

> Explique o que é uma função em Python e mostre um exemplo curto.

Após a resposta, procure o rodapé com **PromptRoast**, a nota e um comentário. Envie outra mensagem com mais contexto para observar a nova avaliação. Uma saudação simples como `Olá` não deve receber nota.

Digite estes comandos **no chat do Claude**, não no PowerShell:

```text
/prompt-roast:score
/prompt-roast:help
/prompt-roast:savage-on
/prompt-roast:savage-off
/prompt-roast:reset
```

`score` mostra as notas da sessão; `savage` muda o tom do comentário; `reset` limpa somente as notas da sessão atual. A resposta e a nota dependem de o Claude seguir as instruções e de ter permissão para executar o programa Python e gravar o histórico.

Se o comando não aparecer, inicie outra sessão e confirme que o diagnóstico mostra a integração preparada. Se o Claude pedir autorização para ler a skill ou executar o programa, revise os caminhos apresentados antes de autorizar. Em caso de erro, envie ao criador a mensagem de erro e as versões do Python e do Claude Code; remova eventuais dados pessoais ou credenciais antes de compartilhar.

## 6. Como remover a demonstração

No PowerShell, novamente dentro da pasta do projeto:

```powershell
py -3 -m prompt_roast uninstall --agent claude --scope global
```

O comando remove apenas os arquivos gerenciados e a seção de instruções do PromptRoast. O histórico e eventuais arquivos modificados pelo usuário permanecem preservados; o resultado informa o que foi removido ou preservado.
