# Spec Delta

## Purpose

Fornecer avaliação contextual de prompts e cálculo consistente de notas, ajudando o usuário a comunicar problemas, objetivos e critérios ao seu agente de IA.

## ADDED Requirements

### Requirement: Classificação contextual compartilhada
O agente SHALL classificar prompts avaliáveis como `request` ou `question` e atribuir três notas inteiras de 0 a 3 segundo uma rubrica compartilhada. Pedidos usam origem, destino e limites; perguntas usam hipótese, escopo e contexto. O contexto já informado na conversa SHALL contar na avaliação.

#### Scenario: Pedido com problema e resultado definidos
- **WHEN** o usuário descreve a falha no login, o resultado esperado e as restrições
- **THEN** o agente apresenta notas para origem, destino e limites usando a mesma rubrica em qualquer integração

#### Scenario: Pergunta exploratória
- **WHEN** o usuário pergunta se a ausência de índice explica uma consulta lenta e informa seu objetivo
- **THEN** o agente avalia hipótese, escopo e contexto sem exigir a estrutura de um pedido de implementação

#### Scenario: Continuação curta com contexto suficiente
- **WHEN** o usuário responde brevemente a uma pergunta anterior do agente
- **THEN** a avaliação considera o contexto anterior em vez de aplicar um limite de nota somente pelo tamanho da mensagem

### Requirement: Cálculo determinístico e Butler Mode
O sistema SHALL calcular `base + p1 + p2 + p3`, sendo base 1 normalmente e 0 em Butler Mode. Butler Mode SHALL ser usado para tarefas pontuais simples, conforme a rubrica, e limitar a nota máxima a 9. Os mesmos valores e sinalizadores SHALL produzir a mesma nota em todos os agentes.

#### Scenario: Pontuação máxima normal
- **WHEN** os três pilares recebem 3 e Butler Mode está desativado
- **THEN** a nota calculada é 10

#### Scenario: Pontuação máxima Butler
- **WHEN** os três pilares recebem 3 e Butler Mode está ativado
- **THEN** a nota é 9 e a apresentação indica Butler Mode

### Requirement: Limites de antipadrões
O sistema SHALL aplicar após a soma um limite de 2 para `hail_mary` e de 1 para `just_do_it`, `why_no_context` e `copy_paste_loop`. A identificação contextual SHALL ser feita pelo agente, sem correspondência cega de palavras-chave.

#### Scenario: Erro sem investigação nem objetivo
- **WHEN** o agente identifica `hail_mary` e a soma seria 5
- **THEN** a nota final é 2 e o feedback indica qual contexto ajudaria

#### Scenario: Delegação informada
- **WHEN** o usuário diz para prosseguir depois de estabelecer o objetivo e os critérios
- **THEN** essa continuação não recebe automaticamente o antipadrão `just_do_it`

### Requirement: Validação das entradas
A CLI SHALL rejeitar pilares não inteiros ou fora de 0 a 3, tipos e antipadrões desconhecidos e combinações inválidas, com mensagem útil e saída não zero. Uma avaliação inválida SHALL deixar o histórico intacto.

#### Scenario: Pilar fora do intervalo
- **WHEN** uma avaliação recebe `p1=-1` ou `p1=4`
- **THEN** a CLI informa o intervalo permitido e não grava nota

#### Scenario: Antipadrão desconhecido
- **WHEN** uma avaliação recebe um nome de antipadrão não suportado
- **THEN** a CLI lista ou explica os valores aceitos sem assumir silenciosamente que não há antipadrão

### Requirement: Feedback após a resposta principal
Com a avaliação habilitada, o agente SHALL responder ao pedido e incluir um único rodapé com `PromptRoast`, nota de 0 a 10, título/emoji, média disponível e feedback curto no idioma do usuário. A nota SHALL servir como orientação, sem impedir a tarefa ou julgar inteligência. Saudações, comandos administrativos e mensagens automáticas de ferramentas SHALL ser ignorados.

#### Scenario: Nota baixa
- **WHEN** um pedido avaliável recebe nota 2
- **THEN** o agente continua atendendo ao pedido e termina com uma sugestão concreta para melhorar o contexto

#### Scenario: Saudação
- **WHEN** o usuário envia somente uma saudação
- **THEN** o agente responde sem nota e sem novo registro de avaliação

#### Scenario: Comando de estatísticas
- **WHEN** o usuário executa a operação `score`
- **THEN** o agente mostra as estatísticas sem pontuar o próprio comando

### Requirement: Estilos normal e savage
O feedback normal SHALL elogiar brevemente notas 8 a 10, combinar reconhecimento e uma sugestão para 5 a 7, e orientar melhorias para 0 a 4. `savage on|off` SHALL alterar somente o tom, usando o estilo de instrutor militar solicitado, sem modificar critérios, cálculo ou limites.

#### Scenario: Mesmo pedido em dois estilos
- **WHEN** a mesma avaliação numérica é apresentada nos estilos normal e savage
- **THEN** nota, pilares e limites são iguais e apenas o texto do feedback muda

### Requirement: Falha transparente de execução
Se o agente não puder executar o núcleo ou acessar o histórico, ele SHALL informar a limitação sem inventar gravação, estatísticas ou sucesso de instalação. Uma avaliação textual SHALL ser identificada como sem registro quando oferecida, mantendo a resposta principal disponível.

#### Scenario: Execução de Python bloqueada pelo host
- **WHEN** o host não autoriza a chamada de Python para registrar uma avaliação
- **THEN** o agente informa que a nota não foi registrada e não apresenta uma média fictícia
