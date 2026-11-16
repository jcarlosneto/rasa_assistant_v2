# 🎯 Capítulo 8: Construindo o Core

> **Versão 2 do projeto** · documento revisado em 16 nov. 2026 e conferido contra o código. O que não foi testado está dito no texto.

## Objetivos

Escrever regras e histórias e entender quem decide a próxima ação.

## As políticas

- `MemoizationPolicy` — max_history: 5
- `RulePolicy` — core_fallback_threshold: 0.3, core_fallback_action_name: action_default_fallback
- `UnexpecTEDIntentPolicy` — max_history: 5, epochs: 20, random_seed: 42
- `TEDPolicy` — max_history: 5, epochs: 20, constrain_similarities: True, random_seed: 42

A ordem de precedência, na prática: a RulePolicy decide quando há regra; a MemoizationPolicy repete o que viu idêntico nas histórias; a TEDPolicy generaliza no restante.

## Regras

O projeto tem 21:

1. Responder saudação simples
2. Responder saudação matinal
3. Responder saudação tarde
4. Responder saudação noite
5. Responder despedida
6. Responder parar/cancelar fora de formulário
7. Responder sobre identidade
8. Fornecer ajuda
9. Dar mensagem motivacional
10. Responder a um "não" solto
11. Responder out of scope educadamente
12. Mostrar progresso de hoje
13. Mostrar progresso da semana
14. Agendar atividade
15. Mostrar agenda
16. Registrar atividade rápida
17. Ativar form de atividade detalhada
18. Submit form de atividade
19. Cancelar formulário ativo
20. Fallback quando não entende
21. Prevenir loop infinito de fallback

Uma regra simples liga intenção a ação. Uma regra com condição só vale em certo estado:

```yaml
# rasa/data/rules.yml
  - rule: Cancelar formulário ativo
    condition:
      - active_loop: atividade_detalhada_form
    steps:
      - intent: stop
      - action: action_deactivate_loop
      - active_loop: null
      - action: action_limpar_slots_atividade
      - action: utter_stop
```

Leia de cima para baixo: **se** o formulário está ativo **e** a intenção é `stop`, desative o formulário, limpe os slots e responda.

## Histórias

Histórias do projeto: `registro_atividade_simples_agua`, `registro_atividade_simples_corrida`, `registro_atividade_simples_meditacao`, `fluxo_completo_positivo`, `registro_detalhado_completo`, `usuario_precisa_ajuda`, `out_of_scope_recovery`, `multiplos_registros`, `consulta_sem_dados`, `motivacao_leva_acao`, `agenda_e_baixa`, `interacao_complexa`.

Elas mostram sequências de vários turnos, como agendar, consultar a agenda e registrar. Não descrevem todos os caminhos possíveis; dão exemplos para o modelo generalizar.

## Quando usar cada uma

| Situação | Use |
|---|---|
| Resposta fixa a uma intenção | Regra |
| Entrada e saída de formulário | Regra |
| Conversa de vários turnos com variações | História |
| Comportamento que depende do que veio antes | História, e teste com cuidado |

Regras e histórias não podem se contradizer. `rasa data validate`, executado dentro de `python run.py test`, acusa conflitos.

## A armadilha do formulário

Com um formulário ativo, a RulePolicy **continua o formulário** e só olha as outras regras quando ele rejeita a entrada. Se o slot aceita qualquer texto, “cancelar” vira resposta e a regra acima nunca dispara. A solução está no domínio, não nas regras (capítulo 12).

Esse foi o defeito mais sério encontrado na revisão, e só apareceu ao executar a conversa. Ler os arquivos não bastava.

## Fallback

Duas redes de proteção:

- no NLU, o `FallbackClassifier` (confiança abaixo de 0,5);
- no Core, `core_fallback_threshold` em 0,3 com `action_default_fallback`.

Há ainda uma regra para evitar repetição infinita do fallback.

## Veja no Raio-X

Na etapa “Decisão”, cada ação aparece com a política que a escolheu. Digite `tchau` (regra) e depois percorra uma das histórias; compare os nomes das políticas.

## Exercícios

1. Escreva a regra para uma intenção `ask_meta` que responde com `utter_meta`.
2. Crie de propósito uma regra que contradiga outra e rode `python run.py test`. Leia a mensagem.
3. Explique por que “cancelar” fora do formulário é tratado por outra regra.

## Resumo

Regra para o que é sempre; história para o que tem variação; formulário tem precedência enquanto aceitar a entrada.

---
[← Capítulo anterior](capitulo-07-nlu.md) · [Índice do tutorial](../TUTORIAL_COMPLETO.md) · [Próximo capítulo →](capitulo-09-actions.md)
