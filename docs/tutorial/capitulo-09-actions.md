# ⚙️ Capítulo 9: Custom actions

> **Versão 2 do projeto** · documento revisado em 16 nov. 2026 e conferido contra o código. O que não foi testado está dito no texto.

## Objetivos

Ler e escrever ações em Python e aplicar o princípio “modelo entende, regra normaliza”.

## Anatomia

Uma ação é uma classe com dois métodos: `name()`, que devolve o nome usado no domínio, e `run()`, que recebe o `dispatcher` (para falar), o `tracker` (para ler a conversa) e o domínio, e devolve uma lista de eventos.

```python
# rasa/actions/actions.py
class ActionGreetingContextual(Action):
    """Por que e custom action? Porque a resposta depende de dados que mudam:
    o relogio, a agenda do usuario e (se houver chave) a API de clima."""

    def name(self) -> Text:
        return "action_greeting_contextual"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        agora = datetime.now()

        # 1. Periodo do dia: vem do relogio, nao do que a pessoa digitou.
        mensagem = catalogo.saudacao_do_periodo(agora.hour) + "! 👋"

        # 2. Clima (opcional): so aparece se OPENWEATHER_API_KEY estiver no .env.
        clima_api = WeatherAPI()
        clima = clima_api.obter_clima(os.getenv("DEFAULT_CITY", "São Paulo")) if clima_api.api_key else None
        if clima:
            mensagem += "\n" + clima_api.formatar_clima_mensagem(clima) + "."

        # 3. Agenda de hoje deste usuario.
        hoje = agora.strftime("%Y-%m-%d")
        pendentes = AtividadesDatabase().listar_agenda(tracker.sender_id, a_partir=hoje, ate=hoje)
        if pendentes:
            itens = ", ".join(
                p["tipo"] + (" às " + p["hora"] if p["hora"] else "") for p in pendentes)
            mensagem += "\n🔔 Na sua agenda de hoje: " + itens + "."

        mensagem += "\nComo posso ajudar com suas atividades?"
        dispatcher.utter_message(text=mensagem)
        return []
```

A saudação segue o relógio da máquina. Por isso `bom dia` às 15h recebe “Boa tarde!”.

## As ações do projeto

- `action_greeting_contextual`
- `action_registrar_atividade`
- `action_mostrar_progresso_hoje`
- `action_mostrar_progresso_semana`
- `action_default_fallback`
- `validate_atividade_detalhada_form`
- `action_submit_atividade_form`
- `action_limpar_slots_atividade`
- `action_agendar_atividade`
- `action_mostrar_agenda`

## Modelo entende, regra normaliza

O NLU entrega o que achou na frase. Antes de gravar, a ação passa os valores por `rasa/actions/catalogo.py`:

| Tipo gravado no banco | Variações aceitas |
|---|---|
| água | agua, água, hidratacao, hidratar, hidratei |
| corrida | corrida, corri, correr, running, run |
| caminhada | caminhada, caminhei, caminhar, andei, andar, walking |
| meditação | meditacao, meditei, meditar, mindfulness |
| natação | natacao, nadei, nadar, swimming, piscina |
| musculação | musculacao, malhei, malhar, academia, treino, gym |
| exercício | exercicio, exercitei, exercitar |
| yoga | yoga, ioga |
| ciclismo | ciclismo, pedalei, pedalar, bicicleta, bike |
| alongamento | alongamento, alonguei, alongar |
| leitura | leitura, li, ler, livro |
| tarefa | tarefa |

```python
# rasa/actions/catalogo.py
def saudacao_do_periodo(hora):
    """0-11 -> 'Bom dia', 12-17 -> 'Boa tarde', 18-23 -> 'Boa noite'."""
    if hora < 12:
        return "Bom dia"
    if hora < 18:
        return "Boa tarde"
    return "Boa noite"
```

Para `malhei 1 hora`, o NLU entrega `malhei` e `1`. O catálogo devolve `musculação` e, lendo “hora” no texto, 60 minutos. Na versão 1, essa frase gravava 1 minuto.

Regras são previsíveis e testáveis: cada linha do catálogo tem teste em `tests/test_catalogo.py`.

```python
# tests/test_catalogo.py
def test_normalizar_tipo(entrada, esperado):
    assert catalogo.normalizar_tipo(entrada) == esperado


def test_normalizar_tipo_vazio():
    assert catalogo.normalizar_tipo(None) is None
    assert catalogo.normalizar_tipo("  ") is None
```

## Uma ação que usa texto e regra

A agenda não treina entidades de data. A intenção e o tipo vêm do NLU; “amanhã às 7h” é lido por expressão regular:

```python
# rasa/actions/actions.py
class ActionAgendarAtividade(Action):
    """'agendar corrida amanha as 7h'.
    Divisao de trabalho: o NLU descobre a intencao e o tipo; data e hora sao
    lidas por expressao regular em catalogo.extrair_quando()."""

    def name(self) -> Text:
        return "action_agendar_atividade"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        texto = tracker.latest_message.get("text", "")
        tipo = catalogo.normalizar_tipo(_entidade(tracker, "tipo_atividade")) \
            or catalogo.resgatar_tipo_do_texto(texto)
        if not tipo:
            dispatcher.utter_message(text=(
                "Qual atividade você quer agendar? 📅\n"
                "Diga tudo de uma vez, por exemplo: 'agendar corrida amanhã às 7h'."))
            return LIMPAR_SLOTS

        quando = catalogo.extrair_quando(texto)
        AtividadesDatabase().agendar(tracker.sender_id, tipo, quando["data"], quando["hora"])

        mensagem = "📅 Agendei: %s para %s%s." % (
            tipo, catalogo.descrever_data(quando["data"]),
            " às " + quando["hora"] if quando["hora"] else "")
        if not quando["entendeu_data"]:
            mensagem += "\nℹ️ Você não disse o dia; assumi hoje."
        mensagem += "\nQuando fizer, é só me contar que eu dou baixa."
        dispatcher.utter_message(text=mensagem)
        return LIMPAR_SLOTS
```

## Eventos

O que a ação devolve muda a conversa. `SlotSet("tipo_atividade", None)` apaga um slot; lista vazia não muda nada. A ação de limpeza usada no cancelamento só devolve eventos:

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

## Cuidados

- Toda ação nova precisa estar em `actions:` no domínio.
- Mudou o código? Reinicie o Action Server (`python run.py stop` e `start`).
- Erro dentro da ação aparece em `logs/actions.log`, não na tela.
- Não sobrescreva ações internas do Rasa, como `action_deactivate_loop`. A versão 1 fazia isso; a versão 2 usa a ação padrão.

## Exercícios

1. Acrescente “pilates” ao catálogo, com teste.
2. Faça a saudação mencionar quantas atividades o usuário registrou ontem.
3. O que acontece se `run()` levantar uma exceção? Provoque e observe o log.

## Resumo

A ação é onde o bot faz algo de verdade. Deixe o entendimento com o modelo e a exatidão com as regras.

---
[← Capítulo anterior](capitulo-08-core.md) · [Índice do tutorial](../TUTORIAL_COMPLETO.md) · [Próximo capítulo →](capitulo-10-database.md)
