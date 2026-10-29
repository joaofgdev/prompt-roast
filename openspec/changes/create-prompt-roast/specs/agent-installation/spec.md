# Spec Delta

## Purpose

Disponibilizar uma instalação local reproduzível e reversível do PromptRoast para os cinco agentes solicitados, mantendo operações equivalentes e respeitando diferenças dos hosts.

## ADDED Requirements

### Requirement: Execução local em Python
O produto SHALL fornecer uma CLI instalável e executável como `python3 -m prompt_roast`, com ajuda em português e runtime Python 3.11+ sem dependências externas de execução. O Linux SHALL ser a plataforma validada inicialmente. A CLI SHALL explicar requisitos ausentes sem modificar o ambiente global de Python.

#### Scenario: Uso a partir do código-fonte
- **WHEN** o usuário executa `python3 -m prompt_roast --help` na raiz após a implementação
- **THEN** recebe instruções de uso sem precisar de chave de API ou instalação de pacotes de execução externos

### Requirement: Seleção de agente e escopo
A instalação SHALL aceitar um agente entre `claude`, `codex`, `cursor`, `gemini` e `antigravity`, ou `all`, e escopo `local` ou `global`. O escopo local SHALL exigir um projeto de destino explícito ou o diretório corrente. A instalação SHALL listar os destinos e passos manuais restantes.

#### Scenario: Instalação em projeto de teste
- **WHEN** o usuário instala os adaptadores de todos os agentes em um diretório de teste
- **THEN** os arquivos são criados somente naquele destino e no armazenamento do produto declarado, sem alterar outros projetos

#### Scenario: Agente ausente
- **WHEN** os arquivos de integração são instalados para um agente cujo executável não existe
- **THEN** a CLI informa que os arquivos foram preparados, mas a execução no host ainda não foi verificada

### Requirement: Operações equivalentes entre agentes
Cada integração SHALL disponibilizar `score`, `reset`, `help`, `setup-global`, `setup-local` e `savage on|off`. Claude Code e Gemini CLI SHALL oferecer aliases `/prompt-roast:<operação>`; Codex SHALL usar `$prompt-roast <operação>`; Cursor e Antigravity SHALL usar `/prompt-roast <operação>`. A ajuda SHALL mostrar a sintaxe real de cada host.

#### Scenario: Ajuda de comandos
- **WHEN** o usuário consulta a ajuda em qualquer agente suportado
- **THEN** encontra as seis operações, seus argumentos e a forma de invocação suportada naquele agente

#### Scenario: Compatibilidade do cálculo
- **WHEN** os cinco adaptadores recebem os mesmos valores estruturados de avaliação
- **THEN** todos chamam o mesmo núcleo e obtêm o mesmo resultado numérico

### Requirement: Avaliação contínua habilitada por configuração
A instalação SHALL preparar a skill e a regra de avaliação contínua no escopo escolhido. `setup-local` e `setup-global` SHALL reaplicar a configuração de forma idempotente. Se a versão do host exigir ação manual, o sistema SHALL informar estado pendente e fornecer o passo exato, sem declarar avaliação contínua ativa.

#### Scenario: Regra local configurada
- **WHEN** a instalação local termina e o host carrega suas instruções na nova conversa
- **THEN** a regra orienta a avaliar cada mensagem elegível sem o usuário invocar a skill em todos os turnos

#### Scenario: Regra global depende da interface
- **WHEN** a instalação global do Cursor prepara as skills e a versão exige cadastrar User Rules pela interface
- **THEN** o instalador fornece o texto da regra e indica a etapa manual pendente, sem editar arquivos internos do aplicativo

### Requirement: Preservação de configurações existentes
Instalação, atualização e setup SHALL alterar somente arquivos gerenciados ou blocos delimitados do PromptRoast, preservando todo conteúdo externo. Colisões com arquivos não gerenciados e links que desviem do destino SHALL produzir erro explícito. Repetir a instalação SHALL evitar duplicatas e não apagar a instalação válida antes de preparar a substituta.

#### Scenario: Arquivo de instruções existente
- **WHEN** o destino já contém `AGENTS.md`, `CLAUDE.md` ou `GEMINI.md` com regras pessoais
- **THEN** o instalador acrescenta somente um bloco delimitado e preserva as regras pessoais

#### Scenario: Arquivo com nome igual sem propriedade do produto
- **WHEN** o destino de uma skill contém um arquivo não gerenciado com o mesmo nome
- **THEN** a operação interrompe a alteração afetada e informa a colisão

#### Scenario: Reinstalação
- **WHEN** a instalação é executada duas vezes com os mesmos parâmetros
- **THEN** existe uma única regra de ativação e um único conjunto de arquivos do produto por destino

### Requirement: Desinstalação reversível
A desinstalação SHALL remover somente arquivos não modificados que pertençam ao produto e seus blocos de configuração. Histórico e arquivos modificados pelo usuário SHALL ser preservados e informados. O produto SHALL não apagar diretórios completos de agentes, projetos ou configurações do shell.

#### Scenario: Remoção com regras externas
- **WHEN** o usuário desinstala o PromptRoast de um agente com regras pessoais
- **THEN** as regras pessoais e o histórico persistem e os blocos exclusivos do produto são removidos

### Requirement: Diagnóstico verdadeiro
`doctor` SHALL verificar versão do Python, agente selecionado, arquivos e caminhos de integração, execução do núcleo e acesso ao estado. O relatório SHALL distinguir arquivos preparados, configuração pendente e teste real no host, registrando a versão quando disponível.

#### Scenario: Arquivos corretos sem teste no aplicativo
- **WHEN** os arquivos existem e o núcleo funciona, mas nenhuma conversa de teste foi executada no host
- **THEN** `doctor` relata prontidão estrutural sem afirmar teste funcional no agente

### Requirement: Documentação e testes reproduzíveis
A entrega SHALL incluir comandos de instalação, avaliação numérica, teste automatizado, diagnóstico, uso em cada agente e desinstalação, com resultados esperados e limitações conhecidas. Os testes automatizados SHALL usar diretórios temporários e não modificar configurações reais dos agentes.

#### Scenario: Primeiro teste independente do agente
- **WHEN** o usuário segue o guia de avaliação com três pilares de valor 3
- **THEN** obtém nota 10 em JSON e consegue repetir o teste sem autenticação em um agente

### Requirement: Distribuição com atribuição
A distribuição SHALL incluir licença MIT, créditos ao projeto ClaudeRoast e os avisos de licença exigidos para trechos reutilizados. A publicação em GitHub, PyPI ou marketplaces SHALL permanecer uma ação futura explicitamente solicitada, sem envio de configurações ou histórico local.

#### Scenario: Preparação local para publicação futura
- **WHEN** a implementação e a documentação são entregues nesta máquina
- **THEN** o código-fonte contém os créditos e a licença, mas não há publicação remota automática
