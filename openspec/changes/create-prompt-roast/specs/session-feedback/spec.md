# Spec Delta

## Purpose

Manter histórico e preferências de feedback locais, permitindo acompanhar a evolução dos prompts sem misturar conversas, projetos ou agentes distintos.

## ADDED Requirements

### Requirement: Sessões explicitamente identificadas
O sistema SHALL isolar o estado pela combinação de agente, projeto e identificador de sessão. O agente SHALL usar o identificador nativo quando disponível ou criar um identificador opaco e reutilizá-lo naquela conversa. Sem identificar a sessão, a CLI SHALL exigir seleção explícita em vez de usar uma sessão global compartilhada.

#### Scenario: Duas conversas do mesmo agente
- **WHEN** duas conversas do Codex avaliam prompts no mesmo projeto
- **THEN** os registros e médias permanecem separados por sessão

#### Scenario: Agentes distintos no mesmo projeto
- **WHEN** Codex e Cursor registram uma avaliação usando o mesmo texto de identificador de sessão
- **THEN** os registros não são misturados porque o agente integra a identidade

#### Scenario: Identificador nativo indisponível
- **WHEN** um agente inicia a avaliação sem identificador nativo acessível
- **THEN** cria um novo identificador, informa sua criação quando necessário e o mantém no contexto da conversa

### Requirement: Registro mínimo e privado
Cada avaliação persistida SHALL conter versão do formato, agente, projeto identificado de forma opaca, sessão, identificador de evento, timestamp, tipo, pilares, Butler Mode, antipadrão e total. O histórico SHALL permanecer local e excluir texto bruto do prompt, código e credenciais. O plugin SHALL funcionar sem telemetria ou API própria.

#### Scenario: Inspeção de uma avaliação gravada
- **WHEN** o usuário inspeciona o histórico após enviar um prompt contendo código
- **THEN** encontra somente metadados de avaliação e nenhum trecho de código ou texto bruto da mensagem

### Requirement: Registro idempotente e íntegro
O sistema SHALL registrar um evento no máximo uma vez por sessão, retornar seu resultado em tentativas repetidas e rejeitar reutilização do mesmo identificador com valores diferentes. Escritas concorrentes ou interrompidas SHALL preservar o último histórico válido ou retornar um erro sem sobrescrevê-lo.

#### Scenario: Repetição após resposta interrompida
- **WHEN** o agente repete o registro com o mesmo identificador de evento e os mesmos pontos
- **THEN** existe somente uma avaliação e a média não muda

#### Scenario: Escritas simultâneas
- **WHEN** duas avaliações diferentes são gravadas simultaneamente na mesma sessão
- **THEN** ambas são preservadas ou uma tentativa recebe erro explícito sem perda silenciosa de registros

#### Scenario: Arquivo inválido
- **WHEN** o histórico existente contém JSON inválido ou versão desconhecida
- **THEN** o sistema preserva o arquivo, informa o problema e não o substitui por um histórico vazio

### Requirement: Estatísticas verificáveis
A operação `score` SHALL apresentar quantidade de avaliações, média com uma casa decimal, até cinco notas recentes e tendência. A tendência SHALL ser indisponível antes de três avaliações; depois comparará a última e a primeira nota das últimas cinco. Uma sessão vazia SHALL mostrar quantidade zero e média indisponível.

#### Scenario: Três avaliações com melhora
- **WHEN** a sessão contém notas 4, 7 e 9
- **THEN** `score` apresenta quantidade 3, média 6,7, as três notas e tendência de melhora

#### Scenario: Sessão vazia
- **WHEN** a operação `score` consulta uma sessão sem avaliações
- **THEN** apresenta quantidade zero, média indisponível e tendência indisponível

### Requirement: Reinício limitado à sessão
A operação `reset` SHALL remover somente avaliações e eventos da sessão selecionada, preservando outras sessões, instalação e preferência de tom daquela sessão. Sua repetição em uma sessão vazia SHALL ser segura.

#### Scenario: Reinício de uma das conversas
- **WHEN** o usuário reinicia a sessão A enquanto a sessão B possui registros
- **THEN** a sessão A fica vazia e os registros da sessão B permanecem intactos

### Requirement: Preferência de tom por sessão
A operação `savage on|off` SHALL persistir o tom somente na sessão selecionada. Uma nova sessão SHALL começar no modo normal e o comando SHALL informar o estado resultante, sem produzir uma nova avaliação.

#### Scenario: Ativação do modo savage
- **WHEN** o usuário ativa savage na sessão A
- **THEN** o tom muda em A, a sessão B continua normal e nenhuma nota é adicionada por esse comando

### Requirement: Respeito às permissões do host
A instalação SHALL informar o diretório de estado utilizado. Se o host não permitir escrita nesse diretório, o agente SHALL solicitar o acesso pelos mecanismos do host ou usar um diretório alternativo explicitamente autorizado. O sistema SHALL indicar ausência de persistência em vez de apresentar estatísticas fictícias.

#### Scenario: Diretório de estado sem acesso
- **WHEN** uma sessão tenta gravar no diretório configurado e recebe erro de permissão
- **THEN** o erro é informado e os dados existentes permanecem intactos
