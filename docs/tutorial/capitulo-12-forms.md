# 📝 Capítulo 12: Formulários

> **Versão 2 do projeto** · documento revisado em 16 nov. 2026 e conferido contra o código. O que não foi testado está dito no texto.

## Objetivos

Montar um formulário, validar respostas e garantir que o usuário consiga sair dele.

## O formulário do projeto

```yaml
# rasa/domain.yml
forms:
  atividade_detalhada_form:
    required_slots:
      - tipo_atividade
      - duracao
      - intensidade
```

O Rasa pergunta, na ordem, por cada slot ainda vazio, usando a resposta `utter_ask_<slot>`.

## Entrada e saída por regras

```yaml
# rasa/data/rules.yml
  - rule: Ativar form de atividade detalhada
    steps:
      - intent: registrar_atividade_detalhado
      - action: atividade_detalhada_form
      - active_loop: atividade_detalhada_form
```

```yaml
# rasa/data/rules.yml
  - rule: Submit form de atividade
    condition:
      - active_loop: atividade_detalhada_form
    steps:
      - action: atividade_detalhada_form
      - active_loop: null
      - slot_was_set:
          - requested_slot: null
      - action: action_submit_atividade_form
```

## Mapeamentos: o detalhe que decide tudo

```yaml
# rasa/domain.yml
  tipo_atividade:
    type: text
    influence_conversation: false
    mappings:
      # Preenche com a entidade, EXCETO na frase que abre o formulario:
      # em "quero registrar exercicio", "exercicio" nao e a resposta.
      - type: from_entity
        entity: tipo_atividade
        not_intent: registrar_atividade_detalhado
      # Dentro do formulario, quando esta e a pergunta da vez, vale o texto todo
      # (assim "pilates", que o modelo nunca viu, tambem e aceito).
      - type: from_text
        not_intent: stop          # "cancelar" nao e resposta: deixa a regra de cancelamento agir
        conditions:
          - active_loop: atividade_detalhada_form
            requested_slot: tipo_atividade
```

- `from_entity` preenche o slot quando o NLU extrai a entidade.
- `from_text` usa a frase inteira, mas **só** quando o formulário está ativo e pedindo este slot (`conditions`).
- `not_intent: stop` impede que “cancelar” seja aceito como resposta.

Sem a última linha, o formulário aceita “cancelar” como tipo de atividade e pergunta “por quantos minutos?”. O usuário fica preso. Com ela, o formulário rejeita a entrada, a RulePolicy consulta as demais regras e a de cancelamento dispara.

## Validação

Cada resposta passa por um método `validate_<slot>`:

```python
# rasa/actions/actions.py
class ValidateAtividadeDetalhadaForm(FormValidationAction):
    """O Rasa chama validate_<slot>() sempre que o formulario preenche um slot.
    Devolver {slot: None} faz o bot perguntar de novo."""

    def name(self) -> Text:
        return "validate_atividade_detalhada_form"

    def validate_tipo_atividade(self, slot_value: Any, dispatcher: CollectingDispatcher,
                                tracker: Tracker, domain: DomainDict) -> Dict[Text, Any]:
        tipo = catalogo.normalizar_tipo(slot_value)
        if not tipo or len(tipo) > 40:
            dispatcher.utter_message(text="⚠️ Não entendi a atividade. Exemplos: corrida, yoga, natação.")
            return {"tipo_atividade": None}
        return {"tipo_atividade": tipo}

    def validate_duracao(self, slot_value: Any, dispatcher: CollectingDispatcher,
                         tracker: Tracker, domain: DomainDict) -> Dict[Text, Any]:
        texto = tracker.latest_message.get("text", "")
        duracao = catalogo.extrair_duracao_min(texto, slot_value)
        if duracao is None:
            dispatcher.utter_message(text="⚠️ Não entendi a duração. Digite, por exemplo: 30, 45 minutos ou 1 hora.")
            return {"duracao": None}
        if not catalogo.duracao_valida(duracao):
            dispatcher.utter_message(text="⚠️ Informe uma duração entre 1 e 300 minutos.")
            return {"duracao": None}
        return {"duracao": duracao}

    def validate_intensidade(self, slot_value: Any, dispatcher: CollectingDispatcher,
                             tracker: Tracker, domain: DomainDict) -> Dict[Text, Any]:
        intensidade = catalogo.normalizar_intensidade(slot_value)
        if intensidade is None:
            dispatcher.utter_message(text="⚠️ Escolha uma destas: leve, moderada ou intensa.")
            return {"intensidade": None}
        return {"intensidade": intensidade}
```

Devolver o slot com valor aceita a resposta. Devolver `None` recusa, e o Rasa pergunta de novo. No roteiro, `um tempão` é recusado e `45` é aceito.

## Cancelamento

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

A conversa de teste correspondente:

```yaml
# rasa/tests/test_stories.yml
  - story: test_formulario_cancelado
    steps:
      - user: |
          quero registrar uma atividade
        intent: registrar_atividade_detalhado
      - action: atividade_detalhada_form
      - active_loop: atividade_detalhada_form
      - user: |
          cancelar
        intent: stop
      - action: action_deactivate_loop
      - active_loop: null
      - action: action_limpar_slots_atividade
      - action: utter_stop
```

## Veja no Raio-X

Durante o formulário, a etapa “Decisão” mostra a RulePolicy mantendo o laço. Ao digitar `cancelar`, aparecem `action_deactivate_loop` e a limpeza dos slots, e nenhuma linha é gravada.

## Boas práticas

- Peça poucos campos. Cada pergunta a mais é uma chance de desistência.
- Aceite o registro numa frase só, quando o usuário já deu tudo.
- Mensagem de recusa deve dizer o que é aceito (“um número de minutos, entre 1 e 300”).
- Teste a saída do formulário antes de testar o caminho feliz.

## Exercícios

1. Remova `not_intent: stop` de um slot, treine e tente cancelar. Observe o Raio-X. Desfaça.
2. Acrescente o campo “local” (casa, academia, rua) ao formulário, com validação.
3. O que acontece se o usuário responder `corri 20 minutos` quando o bot pergunta o tipo? Experimente.

## Resumo

Formulário é coleta guiada com precedência sobre as outras regras. Quem define se há saída são os mapeamentos dos slots.

---
[← Capítulo anterior](capitulo-11-apis.md) · [Índice do tutorial](../TUTORIAL_COMPLETO.md) · [Próximo capítulo →](capitulo-13-testes.md)
