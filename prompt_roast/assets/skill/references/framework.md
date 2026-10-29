# Rubrica PromptRoast

Cada pilar vale de 0 a 3: 0 ausente, 1 implícito ou vago, 2 parcialmente especificado, 3 específico e suficiente. Considere informações já dadas na conversa apenas quando forem claras e aplicáveis; não presuma detalhes ausentes. Atribua 3 somente quando houver evidência suficiente para aquele pilar. Não aumente notas para agradar e não desconte pela escrita informal ou por erros de digitação se o pedido for compreensível.

- **Pedidos:** origem (problema e situação), destino (resultado desejado) e limites (restrições ou critérios de sucesso).
- **Perguntas:** hipótese (ideia ou alternativas), escopo (onde investigar) e contexto (propósito e circunstâncias).
- **Butler:** tarefa pontual simples que o usuário poderia executar diretamente; base 0 em vez de 1. Não confunda com refatorações ou investigações.
- **Antipadrões:** `hail_mary` (erro despejado e pedido genérico, limite 2); `just_do_it` (abandono do objetivo e decisões, limite 1); `why_no_context` (pergunta sem contexto, limite 1); `copy_paste_loop` (erros repetidos sem examinar resultados, limite 1). Uma continuação de trabalho já definido não é antipadrão apenas por ser curta. Sem antipadrão use `none`.

Exemplos: um pedido com falha de login, comportamento desejado e restrição clara pode receber 3/3/3; perguntar sobre índice numa consulta lenta com objetivo de desempenho fornece hipótese, escopo e contexto; responder “pode continuar” depois de estabelecer os requisitos deve aproveitar o contexto anterior. A classificação e o comentário são estimativas do modelo, não uma medida objetiva de inteligência.
