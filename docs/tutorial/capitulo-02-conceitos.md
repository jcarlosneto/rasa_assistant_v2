# 🧠 Capítulo 2: Conceitos fundamentais

> **Versão 2 do projeto** · documento revisado em 16 nov. 2026 e conferido contra o código. O que não foi testado está dito no texto.

## Objetivos

Nomear as peças de um chatbot baseado em NLU e reconhecê-las no Raio-X.

## As dez palavras do vocabulário

| Palavra | Pergunta que responde | Exemplo no projeto |
|---|---|---|
| Intent | O que a pessoa quer? | `ask_progresso_hoje` |
| Entity | Que dados vieram na frase? | `duracao = 30` |
| Slot | O que o bot está lembrando? | `tipo_atividade` |
| Response | Que texto pronto ele tem? | `utter_ajuda` |
| Action | Que código ele executa? | `action_agendar_atividade` |
| Form | Como ele coleta vários dados? | `atividade_detalhada_form` |
| Rule | O que ele faz sempre? | despedida → `utter_goodbye` |
| Story | Que conversas ele viu como exemplo? | `agenda_e_baixa` |
| Policy | Quem decide o próximo passo? | RulePolicy |
| Tracker | Onde fica o histórico? | lido pelo Raio-X |

## Intents do projeto

| Intent | Para que serve | Exemplos no treino |
|---|---|---|
| `greet` | Saudação neutra | 16 |
| `greet_morning` | Bom dia | 10 |
| `greet_afternoon` | Boa tarde | 7 |
| `greet_evening` | Boa noite | 7 |
| `goodbye` | Despedida | 16 |
| `stop` | Parar ou cancelar | 12 |
| `confirmar_sim` | Confirmação | 17 |
| `confirmar_nao` | Negação | 13 |
| `registrar_atividade_rapido` | Registrar numa frase só | 134 |
| `registrar_atividade_detalhado` | Pedir o formulário guiado | 31 |
| `agendar_atividade` | Agendar atividade futura | 30 |
| `ask_agenda` | Consultar a agenda | 14 |
| `ask_progresso_hoje` | Progresso de hoje | 29 |
| `ask_progresso_semana` | Progresso dos últimos 7 dias | 10 |
| `ask_motivacao` | Pedir incentivo | 11 |
| `bot_challenge` | Perguntar se é um robô | 10 |
| `ask_ajuda` | Pedir ajuda | 12 |
| `out_of_scope` | Assunto fora do escopo | 18 |
| `nlu_fallback` | Criado pelo FallbackClassifier (não tem exemplos) | — |

`nlu_fallback` não tem exemplos: o classificador de contingência a coloca no lugar da intenção quando a confiança fica abaixo de 0,5.

## Entidades e slots

O projeto tem três entidades — `tipo_atividade`, `duracao`, `intensidade` — e três slots com os mesmos nomes. A entidade é o que foi achado **nesta** frase; o slot é o que fica **lembrado** entre frases.

| Slot | Tipo | Como é preenchido |
|---|---|---|
| `tipo_atividade` | text | from_entity + from_text |
| `duracao` | any | from_entity + from_text |
| `intensidade` | text | from_entity + from_text |

`from_entity` copia a entidade para o slot. `from_text` usa a frase inteira e, no projeto, só vale dentro do formulário, quando o bot acabou de perguntar por aquele campo.

## Regras e histórias

Regra é obrigação: toda vez que a condição aparece, a ação é aquela. História é exemplo: o modelo aprende com ela e pode generalizar. O projeto prefere regras (21) e usa histórias (12) para sequências mais longas.

## Veja acontecer

Com o sistema no ar, digite `corri 30 minutos intenso` e acompanhe no Raio-X:

1. **Mensagem** — o texto cru.
2. **Tokens** — `corri`, `30`, `minutos`, `intenso`.
3. **Intenção** — a barra de `registrar_atividade_rapido` e a linha do limiar.
4. **Entidades** — três, com as confianças.
5. **Decisão** — a política que escolheu a ação.
6. **Efeito** — a linha gravada no banco.

Repare que o NLU devolve `corrida` (o sinônimo atuou) e `intenso`, e o banco grava `intensa`. A segunda troca é feita por regra em Python.

## Exercícios

1. Para `agendar yoga amanhã às 7h`, diga a intenção e a entidade antes de olhar o Raio-X. Depois confira.
2. Por que `duracao` precisa ser slot e não só entidade, no formulário?
3. Dê um exemplo de comportamento que deveria ser regra e outro que deveria ser história.

## Resumo

Entidade é da frase; slot é da conversa. Regra é obrigação; história é exemplo. O Raio-X mostra todos em ação.

---
[← Capítulo anterior](capitulo-01-introducao.md) · [Índice do tutorial](../TUTORIAL_COMPLETO.md) · [Próximo capítulo →](capitulo-03-arquitetura.md)
