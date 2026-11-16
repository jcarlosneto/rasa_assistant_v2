# 🎓 Capítulo 20: Projeto final

> **Versão 2 do projeto** · documento revisado em 16 nov. 2026 e conferido contra o código. O que não foi testado está dito no texto.

## Objetivos

Aplicar o tutorial inteiro em uma extensão do assistente, com evidência de que funciona.

Este capítulo é uma **proposta de trabalho**. Não há solução pronta no projeto.

## A proposta

Escolha **uma** extensão e leve-a do pedido ao teste:

| Opção | O que envolve | Dificuldade |
|---|---|---|
| A. Metas semanais | Nova intenção, nova tabela, resposta de progresso em relação à meta | Média |
| B. Novo campo no formulário (“local”) | Slot, mapeamento, validação, cancelamento | Média |
| C. Remarcar e cancelar agendamentos | Novas intenções, regras de data, baixa na agenda | Alta |
| D. Tratar as três falhas conhecidas | Dados de treino para `tomei um café`, `bebi h2o` e `valeu, fui`, com medida antes e depois | Baixa no código, alta no método |
| E. Entendimento por LLM com execução determinística | O LLM classifica; as ações e regras continuam as mesmas | Alta |

## O que entregar

1. **Enquadramento** (meia página): o problema, o que fica de fora, como você saberá que deu certo.
2. **Código e dados** alterados.
3. **Testes**: ao menos um unitário, um passo novo no roteiro e três frases novas na prova de NLU.
4. **Medida antes e depois**: saída de `python run.py test` e do roteiro, nas duas situações.
5. **Relato honesto** (uma página): o que funciona, o que não foi testado, o que você faria com mais tempo.

## Roteiro de trabalho

1. Reproduza a situação atual e guarde a saída dos testes.
2. Escreva primeiro o teste que falha.
3. Faça a menor mudança que o faça passar.
4. Treine, suba, rode `test` e `roteiro`.
5. Abra os detalhes dos resultados, não só o resumo.
6. Peça a um colega para tentar quebrar. Registre no mural.
7. Escreva o relato.

## Rubrica

| Critério | Peso | O que se observa |
|---|---|---|
| Funciona | 25% | A funcionalidade faz o que o enquadramento prometeu |
| Evidência | 25% | Testes que falhavam antes e passam depois; medida antes e depois |
| Método | 20% | Prova de NLU não contaminada pelo treino; uma mudança por vez |
| Clareza do código e dos dados | 15% | Outra pessoa entende e consegue alterar |
| Honestidade do relato | 15% | Limites e itens não testados declarados |

Um trabalho que funciona pela metade e diz isso com clareza vale mais do que um que parece completo e esconde o que falhou.

## Armadilhas conhecidas

- Colar na base de treino as frases da prova, e comemorar 100%.
- Esquecer `not_intent: stop` em slot novo do formulário.
- Mudar `actions.py` e não reiniciar o Action Server.
- Confiar no resumo de `rasa test core`.
- Na opção E: deixar a resposta do LLM acionar uma gravação sem validar.

## Para ir além

- Compare o seu resultado com o de um colega que escolheu a mesma opção: as frases de teste dele derrubam o seu modelo?
- Monte o mesmo fluxo no playground gratuito do fabricante e compare o esforço.
- Leia o capítulo 14 e escreva o que faltaria para a sua extensão ir a produção.

## Resumo

O projeto final é pequeno de propósito. O que se avalia é o caminho: enquadrar, testar antes, medir, relatar com franqueza.

---
[← Capítulo anterior](capitulo-19-seguranca.md) · [Índice do tutorial](../TUTORIAL_COMPLETO.md)
