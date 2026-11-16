# 🔧 Customização e extensão

> **Versão 2 do projeto** · documento revisado em 16 nov. 2026 e conferido contra o código. O que não foi testado está dito no texto.

Depois de qualquer mudança em `rasa/data/` ou `rasa/domain.yml`: `python run.py stop`, `python run.py train`, `python run.py start`. Depois de mudar código Python das ações, basta `stop` e `start`.

## Acrescentar um tipo de atividade

Exemplo: “pilates”.

1. Em `rasa/actions/catalogo.py`, acrescente uma linha ao dicionário `TIPOS`: `"pilates": ["pilates"],`.
2. Em `rasa/data/nlu.yml`, acrescente exemplos **anotados** ao intent `registrar_atividade_rapido`: `- fiz [pilates](tipo_atividade)`, `- [pilates](tipo_atividade) por 40 minutos`. Cinco bastam para começar.
3. Acrescente um caso em `tests/test_catalogo.py`.
4. Treine e teste.

Sem o passo 2, o modelo pode não marcar “pilates” como entidade. É a lição do `h2o`.

## Acrescentar uma intenção

Exemplo: “quanto falta para a minha meta?”.

1. `nlu.yml`: um bloco `- intent: ask_meta` com pelo menos dez exemplos variados.
2. `domain.yml`: o nome em `intents:` e, se a resposta for fixa, um `utter_meta` em `responses:`.
3. `rules.yml`: uma regra ligando a intenção à resposta ou à ação.
4. `rasa/tests/nlu_inedito.yml`: duas ou três frases **diferentes** das do treino.
5. `python run.py test`.

Modelo de bloco, copiado do projeto:

```yaml
# rasa/data/nlu.yml
  - intent: agendar_atividade
    examples: |
      - agendar [corrida](tipo_atividade) amanhã às 7h
      - agendar [yoga](tipo_atividade) para sexta às 18h
      - marcar [natação](tipo_atividade) para amanhã
      - marcar [caminhada](tipo_atividade) hoje às 19h
      - quero agendar [musculação](tipo_atividade) para segunda às 6h30
      - agenda [meditação](tipo_atividade) para hoje às 21h
```

## Acrescentar uma entidade

1. Declare em `entities:` no domínio.
2. Anote nos exemplos: `[valor](nome_da_entidade)`.
3. Se o valor precisa ser lembrado, crie o slot com mapeamento `from_entity`.
4. Normalize o valor em Python antes de gravar. Não confie no texto bruto.

## Acrescentar uma ação

1. Crie a classe em `rasa/actions/actions.py`, com `name()` e `run()`.
2. Liste o nome em `actions:` no domínio.
3. Ligue por regra ou história.
4. Reinicie o Action Server.

Exemplo real, a ação que limpa os slots depois do cancelamento:

```python
# rasa/actions/actions.py
class ActionLimparSlotsAtividade(Action):
    """Usada no cancelamento do formulario. Quem DESATIVA o formulario e a
    acao padrao do Rasa `action_deactivate_loop`; esta so esvazia a memoria,
    para a proxima conversa nao comecar com respostas antigas."""

    def name(self) -> Text:
        return "action_limpar_slots_atividade"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        return LIMPAR_SLOTS
```

## Acrescentar um campo ao formulário

1. Novo slot no domínio, com `from_entity` e `from_text`, este condicionado ao formulário e com `not_intent: stop`.
2. Nome do slot em `required_slots` do formulário.
3. Resposta `utter_ask_<slot>`.
4. Método `validate_<slot>` em `ValidateAtividadeDetalhadaForm`.
5. Passos novos em `tests/e2e/roteiro_demo.json`.

## Acrescentar uma página à interface

1. Um arquivo em `web_interface/templates/` que estenda `base.html`.
2. Uma rota em `web_interface/app.py`.
3. Um item no menu de `base.html`.
4. Um caso em `tests/test_web.py`.

Insira texto do usuário com `textContent`, nunca com `innerHTML`. A interface inteira segue essa regra.

## Integrar outra API

Use `rasa/actions/weather_api.py` como modelo: chave lida do ambiente, HTTPS, tempo máximo de 5 segundos e resposta nula quando falha. A ação que chama a API precisa funcionar sem ela.

## Mudar o provedor de LLM do Duelo

Não exige código: `LLM_PROVIDER`, `LLM_MODEL` e, para API compatível, `LLM_BASE_URL` no `.env`. Veja [08-configuracoes.md](08-configuracoes.md).

## Lista de conferência

- [ ] Exemplos novos estão anotados.
- [ ] O domínio declara tudo o que os dados usam (`python run.py test` confere).
- [ ] Há pelo menos uma frase nova na prova de NLU, diferente do treino.
- [ ] O roteiro continua passando.
- [ ] Nenhuma chave foi parar em arquivo versionado.
