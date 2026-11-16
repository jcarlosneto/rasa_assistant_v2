# -*- coding: utf-8 -*-
"""
CUSTOM ACTIONS - o codigo Python que o Rasa chama quando precisa "fazer algo".

Fluxo de uma mensagem
---------------------
1. O usuario escreve; o NLU descobre a intencao (intent) e as entidades.
2. O Core escolhe a proxima acao (uma regra, ou a rede TED).
3. Se a acao for uma destas classes, o Rasa chama o Action Server (porta 5055).
4. A action le o contexto no `tracker`, executa a regra de negocio,
   responde pelo `dispatcher` e devolve eventos (por exemplo, limpar slots).

Cada classe abaixo tem: name() -> o nome declarado no domain.yml
                        run()  -> a logica.

As regras de normalizacao ficam em catalogo.py e o SQL em database.py,
para poderem ser testadas sem subir o Rasa.
"""
import os
from datetime import datetime
from typing import Any, Dict, List, Text

from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import FormValidationAction
from rasa_sdk.types import DomainDict

from . import catalogo
from .database import AtividadesDatabase
from .weather_api import WeatherAPI

LIMPAR_SLOTS = [SlotSet("tipo_atividade", None), SlotSet("duracao", None), SlotSet("intensidade", None)]


def _plural(n, singular, plural):
    return singular if n == 1 else plural


def _descrever(tipo, duracao=None, intensidade=None):
    """'corrida', 30, 'intensa' -> 'corrida · 30 min · intensa'."""
    partes = [tipo]
    if duracao:
        partes.append("%d min" % int(duracao))
    if intensidade:
        partes.append(intensidade)
    return " · ".join(partes)


def _entidade(tracker, nome):
    """Primeiro valor da entidade `nome` na ULTIMA mensagem (ou None)."""
    for entidade in tracker.latest_message.get("entities", []):
        if entidade.get("entity") == nome:
            return entidade.get("value")
    return None


# ═══════════════════════════════════════════════════════════════
# ACTION 1 - SAUDACAO CONTEXTUAL (hora do dia + agenda + clima opcional)
# ═══════════════════════════════════════════════════════════════
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


# ═══════════════════════════════════════════════════════════════
# ACTION 2 - REGISTRO RAPIDO ("bebi agua", "corri 30 minutos intenso")
# ═══════════════════════════════════════════════════════════════
class ActionRegistrarAtividade(Action):
    def name(self) -> Text:
        return "action_registrar_atividade"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        texto = tracker.latest_message.get("text", "")
        usuario = tracker.sender_id

        # 1. O que o NLU extraiu (valor "bruto", como a pessoa escreveu).
        tipo_bruto = _entidade(tracker, "tipo_atividade")

        # 2. Normalizacao por regra (catalogo.py): "meditei" -> "meditação".
        tipo = catalogo.normalizar_tipo(tipo_bruto) or catalogo.resgatar_tipo_do_texto(texto)
        duracao = catalogo.extrair_duracao_min(texto, _entidade(tracker, "duracao"))
        intensidade = catalogo.normalizar_intensidade(_entidade(tracker, "intensidade"))

        if not tipo:
            # A intencao foi reconhecida, mas nao sabemos QUAL atividade.
            dispatcher.utter_message(text=(
                "Entendi que você quer registrar algo, mas não identifiquei a atividade. 🤔\n"
                "Tente: 'bebi água', 'corri 20 minutos' ou 'meditei'."))
            return LIMPAR_SLOTS

        if duracao is not None and not catalogo.duracao_valida(duracao):
            dispatcher.utter_message(text=(
                "⚠️ Entendi %d minutos de %s, mas só registro durações entre 1 e 300 minutos. "
                "Pode conferir?" % (int(duracao), tipo)))
            return LIMPAR_SLOTS

        # 3. Grava e consulta o total do dia DESTE usuario.
        db = AtividadesDatabase()
        db.registrar_atividade(tipo=tipo, duracao=duracao, intensidade=intensidade, usuario=usuario)
        total = db.obter_estatisticas_hoje(usuario)["total"]

        mensagem = "✅ Registrei: %s.\n🔥 Total hoje: %d %s." % (
            _descrever(tipo, duracao, intensidade), total, _plural(total, "atividade", "atividades"))

        # 4. Se isto estava na agenda de hoje, marca como cumprido.
        cumprido = db.concluir_agendamento(usuario, tipo)
        if cumprido:
            mensagem += "\n📅 Isso cumpre o que você tinha agendado%s." % (
                " para as " + cumprido["hora"] if cumprido["hora"] else " para hoje")

        if total == 5:
            mensagem += "\n🌟 Cinco atividades hoje!"
        dispatcher.utter_message(text=mensagem)
        return LIMPAR_SLOTS


# ═══════════════════════════════════════════════════════════════
# ACTIONS 3 e 4 - PROGRESSO (hoje / ultimos 7 dias)
# ═══════════════════════════════════════════════════════════════
class ActionMostrarProgressoHoje(Action):
    def name(self) -> Text:
        return "action_mostrar_progresso_hoje"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        db = AtividadesDatabase()
        atividades = db.obter_atividades_hoje(tracker.sender_id)
        if not atividades:
            dispatcher.utter_message(text=(
                "Você ainda não registrou nenhuma atividade hoje. 📭\n"
                "Que tal começar agora? Diga: 'bebi água', 'corri' ou 'meditei'."))
            return []

        total = len(atividades)
        linhas = ["📊 Seu progresso hoje (%d %s):" % (total, _plural(total, "atividade", "atividades"))]
        for i, a in enumerate(atividades, 1):
            linhas.append("%d. %s - %s" % (
                i, _descrever(a["tipo"].capitalize(), a["duracao"], a["intensidade"]), a["hora"]))
        tempo = db.obter_estatisticas_hoje(tracker.sender_id)["tempo_total"]
        if tempo > 0:
            linhas.append("⏱️ Tempo total: %d minutos" % int(tempo))
        linhas.append("🔥 Continue assim!")
        dispatcher.utter_message(text="\n".join(linhas))
        return []


class ActionMostrarProgressoSemana(Action):
    def name(self) -> Text:
        return "action_mostrar_progresso_semana"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        db = AtividadesDatabase()
        stats = db.obter_estatisticas_semana(tracker.sender_id)
        if stats["total"] == 0:
            dispatcher.utter_message(text=(
                "Você não registrou atividades nos últimos 7 dias. 😢\n"
                "Que tal começar uma nova sequência hoje? 💪"))
            return []

        linhas = ["📊 Seu progresso nos últimos 7 dias:",
                  "📈 Total: %d %s" % (stats["total"], _plural(stats["total"], "atividade", "atividades")),
                  "📊 Média: %.1f por dia" % stats["media_dia"],
                  "🔥 Sequência: %d %s" % (
                      db.sequencia_dias(tracker.sender_id),
                      _plural(db.sequencia_dias(tracker.sender_id), "dia seguido", "dias seguidos"))]
        top = list(stats["por_tipo"].items())[:3]
        if top:
            linhas.append("🏆 Mais frequentes: " + ", ".join("%s (%dx)" % (t, n) for t, n in top))
        if stats["tempo_total"] > 0:
            linhas.append("⏱️ Tempo total: %dh %dmin" % (
                int(stats["tempo_total"] // 60), int(stats["tempo_total"] % 60)))
        dispatcher.utter_message(text="\n".join(linhas))
        return []


# ═══════════════════════════════════════════════════════════════
# ACTION 5 - FALLBACK (o bot admite que nao entendeu)
# ═══════════════════════════════════════════════════════════════
class ActionDefaultFallback(Action):
    def name(self) -> Text:
        return "action_default_fallback"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(text=(
            "Hmm, não entendi bem... 🤔\n"
            "Posso te ajudar com:\n"
            "• Registrar: 'bebi água', 'corri 30 minutos'\n"
            "• Agendar: 'agendar yoga amanhã às 7h'\n"
            "• Consultar: 'como estou hoje?', 'minha agenda'"))
        return []


# ═══════════════════════════════════════════════════════════════
# FORMULARIO - validacao de cada resposta
# ═══════════════════════════════════════════════════════════════
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


class ActionSubmitAtividadeForm(Action):
    """Roda quando o formulario termina: grava e limpa os slots."""

    def name(self) -> Text:
        return "action_submit_atividade_form"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        tipo = tracker.get_slot("tipo_atividade")
        duracao = tracker.get_slot("duracao")
        intensidade = tracker.get_slot("intensidade")
        usuario = tracker.sender_id

        db = AtividadesDatabase()
        db.registrar_atividade(tipo=tipo, duracao=duracao, intensidade=intensidade, usuario=usuario)
        total = db.obter_estatisticas_hoje(usuario)["total"]
        mensagem = "✅ Registrei: %s.\n🔥 Total hoje: %d %s." % (
            _descrever(tipo, duracao, intensidade), total, _plural(total, "atividade", "atividades"))
        cumprido = db.concluir_agendamento(usuario, tipo)
        if cumprido:
            mensagem += "\n📅 Isso cumpre o que você tinha agendado%s." % (
                " para as " + cumprido["hora"] if cumprido["hora"] else " para hoje")
        dispatcher.utter_message(text=mensagem)
        return LIMPAR_SLOTS


class ActionLimparSlotsAtividade(Action):
    """Usada no cancelamento do formulario. Quem DESATIVA o formulario e a
    acao padrao do Rasa `action_deactivate_loop`; esta so esvazia a memoria,
    para a proxima conversa nao comecar com respostas antigas."""

    def name(self) -> Text:
        return "action_limpar_slots_atividade"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        return LIMPAR_SLOTS


# ═══════════════════════════════════════════════════════════════
# AGENDA - marcar e consultar atividades futuras
# ═══════════════════════════════════════════════════════════════
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


class ActionMostrarAgenda(Action):
    def name(self) -> Text:
        return "action_mostrar_agenda"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        itens = AtividadesDatabase().listar_agenda(tracker.sender_id)
        if not itens:
            dispatcher.utter_message(text=(
                "Sua agenda está vazia. 📭\n"
                "Para marcar algo: 'agendar yoga amanhã às 7h'."))
            return []
        linhas = ["📅 Sua agenda (%d %s):" % (len(itens), _plural(len(itens), "item", "itens"))]
        for i, item in enumerate(itens, 1):
            linhas.append("%d. %s - %s%s" % (
                i, item["tipo"].capitalize(), catalogo.descrever_data(item["data"]),
                " às " + item["hora"] if item["hora"] else ""))
        dispatcher.utter_message(text="\n".join(linhas))
        return []
