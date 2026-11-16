# ⚡ Capítulo 15: Desempenho

> **Versão 2 do projeto** · documento revisado em 16 nov. 2026 e conferido contra o código. O que não foi testado está dito no texto.

> ⚠️ **Capítulo conceitual.** O que está descrito aqui **não faz parte da versão 2** do projeto e **não foi executado** nesta revisão, salvo onde o texto diz “na v2” ou “medido”. Use como mapa de estudo e confira na documentação do Rasa antes de aplicar.

## Objetivos

Saber o que medir, conhecer os números medidos no laboratório e as alavancas usuais de ajuste.

## O que foi medido

Em uma máquina Linux com 2 CPUs virtuais, sem placa gráfica:

| Operação | Tempo |
|---|---|
| Treino completo | 98 a 103 s (duas medições) |
| Retreino após a correção `h2o` (só o NLU muda) | 69 s |
| Subida dos três serviços | cerca de 50 s |
| Testes unitários | menos de 1 s |

Esses números valem para aquela máquina. Não os tome como esperados na sua: meça. Latência por mensagem não foi medida de forma controlada; a interface registra a latência de cada interação e mostra a média na página Saúde.

## Onde o tempo vai

- **Na subida**: carregar o TensorFlow e o modelo.
- **No treino**: o DIET e a TEDPolicy. O Rasa guarda em cache as etapas que não mudaram, e por isso o retreino depois de mexer só no NLU é mais curto.
- **Na conversa**: o NLU e as políticas são rápidos em modelo pequeno; ações que consultam serviços externos dominam o tempo. O clima tem limite de 5 segundos; o LLM, o valor de `LLM_TIMEOUT`.

## Alavancas de treino

| Alavanca | Efeito | Risco |
|---|---|---|
| Menos `epochs` | Treino mais curto | Modelo pior; meça com a prova de NLU |
| Menos histórias, mais regras | Core treina menos | Menos generalização |
| Pipeline menor | Treino e resposta mais rápidos | Perda de qualidade nas entidades |
| Semente fixa | Não acelera; torna comparável | — |

O projeto usa 60 épocas no DIET e 20 nas políticas, escolhidas por tempo de treino com os testes passando. **Não houve busca sistemática**; pode haver configuração melhor.

## Alavancas de atendimento (não aplicadas na v2)

- Vários processos do servidor Rasa (variável `SANIC_WORKERS`), o que exige “lock store” compartilhado.
- Vários processos do Action Server (`ACTION_SERVER_SANIC_WORKERS`).
- Banco próprio para concorrência, no lugar do SQLite.
- Respostas em cache para consultas repetidas.

Nenhuma delas foi testada aqui. O projeto nunca foi exercitado com vários usuários ao mesmo tempo.

## Medir antes de mexer

1. Defina a pergunta: tempo de treino? de resposta? com quantos usuários?
2. Meça três vezes, na mesma máquina.
3. Mude **uma** coisa.
4. Meça de novo e confira a qualidade (`python run.py test`).

Otimizar sem medir é trocar um problema conhecido por um desconhecido.

## LLM: outra escala de custo

Um classificador local responde em milissegundos e não cobra por mensagem. Um LLM externo acrescenta rede, fila do provedor e preço por uso. Em produção, isso leva a decisões como usar o LLM só quando o classificador está inseguro. O projeto não mediu nenhum provedor.

## Exercícios

1. Meça o treino com 30, 60 e 100 épocas no DIET. Registre tempo e acertos na prova de NLU.
2. Abra a página Saúde depois de vinte mensagens. Qual a latência média?
3. Por que não faz sentido comparar o tempo do laboratório com o do seu computador?

## Resumo

Há quatro números medidos e várias alavancas não testadas. Meça na sua máquina antes de concluir qualquer coisa.

---
[← Capítulo anterior](capitulo-14-deploy.md) · [Índice do tutorial](../TUTORIAL_COMPLETO.md) · [Próximo capítulo →](capitulo-16-multilingue.md)
