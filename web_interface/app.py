# -*- coding: utf-8 -*-
"""
INTERFACE WEB (Flask) do Assistente de Atividades - versao 2.

Telas
-----
/           Chat + RAIO-X: o caminho de cada mensagem dentro do Rasa
/mural      "Quebre o bot": falhas encontradas pela turma
/duelo      Duelo 1.0 x 2.0: a mesma frase no Rasa classico e em um LLM
/replay     Conversa gravada (plano B: funciona sem o Rasa no ar)
/dashboard  Painel com dados reais do banco
/saude      Observabilidade: servicos, latencia, taxa de falha

De onde vem o Raio-X?
---------------------
Depois de cada mensagem, esta aplicacao pede ao Rasa o "tracker" da conversa
(GET /conversations/<id>/tracker). O tracker e o diario que o Rasa mantem:
o que o NLU entendeu, que politica escolheu cada acao, que slots mudaram.
Nada do que aparece na tela e simulado.

Dependencias: apenas Flask. As chamadas HTTP usam a biblioteca padrao.
"""
import csv
import io
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime

RAIZ = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.join(RAIZ, "rasa"))

from flask import Flask, Response, jsonify, render_template, request  # noqa: E402

from actions.database import AtividadesDatabase, carregar_env  # noqa: E402
import llm  # noqa: E402

carregar_env()

RASA_URL = os.getenv("RASA_SERVER_URL", "http://localhost:5005").rstrip("/")
ACTIONS_URL = os.getenv("RASA_ACTION_SERVER_URL", "http://localhost:5055").rstrip("/")
LIMIAR_CONFIANCA = 0.70          # abaixo disso a fala entra no mural como "baixa confianca"
ARQUIVO_REPLAY = os.path.join(os.path.dirname(os.path.abspath(__file__)), "replay", "roteiro_gravado.json")
ARQUIVO_DUELOS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "replay", "duelos_gravados.json")

app = Flask(__name__)
app.config["JSON_AS_ASCII"] = False
try:
    app.json.ensure_ascii = False       # Flask >= 2.3
except AttributeError:
    pass


def banco():
    return AtividadesDatabase()


# ─────────────────────────────── utilidades ───────────────────────────────
def limpar_usuario(valor):
    """Apelido vira identificador de conversa: letras, numeros, '-' e '_', ate 24 caracteres."""
    valor = re.sub(r"[^A-Za-z0-9_-]", "", str(valor or ""))[:24]
    return valor or "visitante"


def http_json(url, corpo=None, timeout=15):
    """GET (corpo=None) ou POST com JSON. Devolve o JSON decodificado."""
    dados = json.dumps(corpo).encode("utf-8") if corpo is not None else None
    requisicao = urllib.request.Request(url, data=dados, method="POST" if dados else "GET")
    if dados:
        requisicao.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(requisicao, timeout=timeout) as resposta:
        return json.loads(resposta.read().decode("utf-8"))


def servico_no_ar(url, timeout=2):
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resposta:
            return resposta.status == 200
    except Exception:
        return False


def nome_politica(bruto):
    """'policy_1_RulePolicy' -> 'RulePolicy'."""
    return re.sub(r"^policy_\d+_", "", bruto or "") or None


def montar_raiox(tracker):
    """Extrai do tracker tudo o que aconteceu DESDE a ultima fala do usuario."""
    eventos = tracker.get("events", [])
    indice = max((i for i, e in enumerate(eventos) if e.get("event") == "user"), default=None)
    if indice is None:
        return None
    usuario_ev = eventos[indice]
    parse = usuario_ev.get("parse_data", {})
    raiox = {
        "texto": usuario_ev.get("text", ""),
        "tokens": [],
        "intent": {"nome": parse.get("intent", {}).get("name"),
                   "confianca": parse.get("intent", {}).get("confidence", 0.0)},
        "ranking": [{"nome": r.get("name"), "confianca": r.get("confidence", 0.0)}
                    for r in parse.get("intent_ranking", [])[:5]],
        "entidades": [{"entidade": e.get("entity"), "valor": e.get("value"),
                       "inicio": e.get("start"), "fim": e.get("end"),
                       "extrator": e.get("extractor"),
                       "confianca": e.get("confidence_entity")}
                      for e in parse.get("entities", [])],
        "acoes": [], "slots_alterados": [], "respostas": [],
        "formulario_ativo": (tracker.get("active_loop") or {}).get("name"),
        "slots_finais": {k: v for k, v in (tracker.get("slots") or {}).items()
                         if k in ("tipo_atividade", "duracao", "intensidade", "requested_slot")},
    }
    texto = raiox["texto"]
    for par in parse.get("text_tokens") or []:
        raiox["tokens"].append(texto[par[0]:par[1]])
    for evento in eventos[indice + 1:]:
        tipo = evento.get("event")
        if tipo == "action":
            raiox["acoes"].append({"nome": evento.get("name"),
                                   "politica": nome_politica(evento.get("policy")),
                                   "confianca": evento.get("confidence")})
        elif tipo == "slot":
            raiox["slots_alterados"].append({"nome": evento.get("name"), "valor": evento.get("value")})
        elif tipo == "bot" and evento.get("text"):
            raiox["respostas"].append(evento.get("text"))
    return raiox


def motivo_automatico(raiox):
    """Sinais objetivos de que o bot pode ter falhado (viram itens do mural)."""
    if raiox is None:
        return None
    nomes = [a["nome"] for a in raiox["acoes"]]
    if raiox["intent"]["nome"] == "nlu_fallback" and not raiox["formulario_ativo"] \
            and "action_submit_atividade_form" not in nomes:
        return "o bot não entendeu (fallback)"
    if any("não identifiquei a atividade" in r for r in raiox["respostas"]):
        return "entendeu a intenção, mas não a atividade"
    confianca = raiox["intent"]["confianca"] or 0
    if raiox["intent"]["nome"] != "nlu_fallback" and confianca < LIMIAR_CONFIANCA:
        return "baixa confiança (%d%%)" % round(confianca * 100)
    return None


# ───────────────────────────────── páginas ─────────────────────────────────
@app.route("/")
def pagina_chat():
    return render_template("chat.html", pagina="chat", modo="aovivo")


@app.route("/replay")
def pagina_replay():
    return render_template("chat.html", pagina="replay", modo="replay")


@app.route("/mural")
def pagina_mural():
    return render_template("mural.html", pagina="mural")


@app.route("/duelo")
def pagina_duelo():
    cfg = llm.configuracao()
    cfg.pop("_chave", None)
    return render_template("duelo.html", pagina="duelo", cfg=cfg)


@app.route("/dashboard")
def pagina_dashboard():
    return render_template("dashboard.html", pagina="dashboard")


@app.route("/saude")
def pagina_saude():
    return render_template("saude.html", pagina="saude")


# ─────────────────────────────── API: conversa ──────────────────────────────
@app.route("/api/chat", methods=["POST"])
def api_chat():
    dados = request.get_json(silent=True) or {}
    mensagem = str(dados.get("mensagem", "")).strip()[:500]
    usuario = limpar_usuario(dados.get("usuario"))
    if not mensagem:
        return jsonify({"erro": "Mensagem vazia."}), 400

    db = banco()
    antes_atividade, antes_agenda = db.maior_id("atividades"), db.maior_id("agenda")
    inicio = time.time()
    try:
        respostas = http_json(RASA_URL + "/webhooks/rest/webhook",
                              {"sender": usuario, "message": mensagem}, timeout=30)
        latencia = int((time.time() - inicio) * 1000)
        tracker = http_json(RASA_URL + "/conversations/" + urllib.parse.quote(usuario) +
                            "/tracker?include_events=ALL")
    except (urllib.error.URLError, ConnectionError, OSError) as erro:
        return jsonify({"erro": "Não consegui falar com o Rasa em %s. Ele está no ar? "
                                "(python run.py status) — ou use a tela Replay." % RASA_URL,
                        "detalhe": str(erro)}), 503

    raiox = montar_raiox(tracker) or {}
    if raiox and not raiox["tokens"]:
        try:   # alguns canais nao devolvem os tokens no tracker; pedimos ao NLU
            parse = http_json(RASA_URL + "/model/parse", {"text": mensagem})
            raiox["tokens"] = [mensagem[a:b] for a, b in parse.get("text_tokens", [])]
        except Exception:
            pass
    textos = [r.get("text", "") for r in respostas if r.get("text")]
    raiox["banco"] = {"atividades": db.obter_atividades_depois_de(antes_atividade, usuario),
                      "agenda": db.obter_agenda_depois_de(antes_agenda, usuario)}
    raiox["latencia_ms"] = latencia

    motivo = motivo_automatico(raiox)
    interacao_id = db.registrar_interacao(
        usuario, mensagem, raiox.get("intent", {}).get("nome"), raiox.get("intent", {}).get("confianca"),
        raiox.get("entidades", []), raiox.get("acoes", []), "\n".join(textos), latencia, motivo)
    return jsonify({"id": interacao_id, "usuario": usuario, "mensagem": mensagem, "respostas": textos,
                    "raiox": raiox, "motivo_auto": motivo,
                    "momento": datetime.now().strftime("%H:%M")})


@app.route("/api/quebra", methods=["POST"])
def api_quebra():
    dados = request.get_json(silent=True) or {}
    try:
        interacao_id = int(dados.get("id"))
    except (TypeError, ValueError):
        return jsonify({"erro": "id inválido"}), 400
    ok = banco().reportar_quebra(interacao_id, str(dados.get("comentario", "")))
    return (jsonify({"ok": True}), 200) if ok else (jsonify({"erro": "interação não encontrada"}), 404)


@app.route("/api/mural")
def api_mural():
    db = banco()
    return jsonify({"resumo": db.resumo_interacoes(), "quebras": db.listar_quebras()})


@app.route("/api/mural/nlu.yml")
def api_mural_nlu():
    """Transforma as falhas do mural em candidatas a exemplos de treino."""
    por_intent = {}
    for q in banco().listar_quebras():
        por_intent.setdefault(q["intent"] or "nlu_fallback", [])
        if q["texto"] not in por_intent[q["intent"] or "nlu_fallback"]:
            por_intent[q["intent"] or "nlu_fallback"].append(q["texto"])
    linhas = ["# Candidatas a exemplos de treino geradas a partir do mural \"Quebre o bot\".",
              "# REVISE antes de colar em rasa/data/nlu.yml:",
              "#   1) o intent abaixo e o que o modelo PREVIU; troque pelo correto;",
              "#   2) marque as entidades: bebi [h2o](tipo_atividade);",
              "#   3) retreine (python run.py train) e teste de novo.",
              'version: "3.1"', "nlu:"]
    for intent, frases in sorted(por_intent.items()):
        linhas += ["  - intent: %s   # previsto pelo modelo - confirme" % intent, "    examples: |"]
        linhas += ["      - " + frase.replace("\n", " ") for frase in frases]
    if not por_intent:
        linhas.append("  # (o mural ainda esta vazio)")
    return Response("\n".join(linhas) + "\n", mimetype="text/plain; charset=utf-8")


# ──────────────────────────────── API: duelo ────────────────────────────────
@app.route("/api/duelo", methods=["POST"])
def api_duelo():
    dados = request.get_json(silent=True) or {}
    mensagem = str(dados.get("mensagem", "")).strip()[:500]
    if not mensagem:
        return jsonify({"erro": "Mensagem vazia."}), 400
    resultado = {"mensagem": mensagem, "momento": datetime.now().isoformat(timespec="seconds")}

    inicio = time.time()
    try:   # /model/parse so interpreta: nao grava nada nem altera a conversa
        parse = http_json(RASA_URL + "/model/parse", {"text": mensagem})
        resultado["rasa"] = {
            "ok": True, "latencia_ms": int((time.time() - inicio) * 1000),
            "intent": parse.get("intent", {}).get("name"),
            "confianca": parse.get("intent", {}).get("confidence", 0.0),
            "ranking": [{"nome": r["name"], "confianca": r["confidence"]}
                        for r in parse.get("intent_ranking", [])[:3]],
            "entidades": [{"entidade": e["entity"], "valor": e["value"]} for e in parse.get("entities", [])]}
    except Exception as erro:
        resultado["rasa"] = {"ok": False, "erro": "Rasa fora do ar (%s)." % type(erro).__name__}

    resultado["llm"] = llm.interpretar(mensagem)
    return jsonify(resultado)


@app.route("/api/duelo/gravados", methods=["GET", "POST"])
def api_duelos_gravados():
    """GET lista duelos salvos; POST salva um duelo REAL para uso offline."""
    gravados = []
    if os.path.exists(ARQUIVO_DUELOS):
        with open(ARQUIVO_DUELOS, encoding="utf-8") as arquivo:
            gravados = json.load(arquivo)
    if request.method == "POST":
        duelo = request.get_json(silent=True) or {}
        if not (duelo.get("llm", {}).get("ok") and duelo.get("rasa", {}).get("ok")):
            return jsonify({"erro": "Só gravo duelos em que os dois lados responderam."}), 400
        gravados = [g for g in gravados if g.get("mensagem") != duelo.get("mensagem")] + [duelo]
        with open(ARQUIVO_DUELOS, "w", encoding="utf-8") as arquivo:
            json.dump(gravados, arquivo, ensure_ascii=False, indent=1)
    return jsonify(gravados)


# ──────────────────────────────── API: replay ───────────────────────────────
@app.route("/api/replay")
def api_replay():
    if not os.path.exists(ARQUIVO_REPLAY):
        return jsonify({"erro": "Ainda não há conversa gravada. Rode: python run.py gravar-replay"}), 404
    with open(ARQUIVO_REPLAY, encoding="utf-8") as arquivo:
        return jsonify(json.load(arquivo))


# ─────────────────────────────── API: dashboard ─────────────────────────────
@app.route("/api/dashboard")
def api_dashboard():
    usuario = request.args.get("usuario")
    usuario = limpar_usuario(usuario) if usuario else None      # None = turma toda
    db = banco()
    return jsonify({
        "usuario": usuario,
        "hoje": db.obter_estatisticas_hoje(usuario),
        "semana": db.obter_estatisticas_semana(usuario),
        "serie": db.serie_7_dias(usuario),
        "sequencia": db.sequencia_dias(usuario),
        "agenda": db.listar_agenda(usuario),
        "recentes": db.obter_atividades_semana(usuario)[:200],
    })


@app.route("/api/export.csv")
def api_export():
    usuario = request.args.get("usuario")
    usuario = limpar_usuario(usuario) if usuario else None
    saida = io.StringIO()
    escritor = csv.writer(saida)
    escritor.writerow(["id", "usuario", "tipo", "duracao_min", "intensidade", "data", "hora"])
    for a in banco().obter_atividades_semana(usuario):
        escritor.writerow([a["id"], a["usuario"], a["tipo"], a["duracao"] or "", a["intensidade"] or "",
                           a["data"], a["hora"]])
    return Response("﻿" + saida.getvalue(), mimetype="text/csv; charset=utf-8",
                    headers={"Content-Disposition": "attachment; filename=atividades_7_dias.csv"})


# Rotas herdadas da v1 (mantidas para nao quebrar quem ja usa)
@app.route("/api/atividades/hoje")
def api_atividades_hoje():
    return jsonify(banco().obter_atividades_hoje())


@app.route("/api/atividades/semana")
def api_atividades_semana():
    return jsonify(banco().obter_atividades_semana())


@app.route("/api/estatisticas/hoje")
def api_estatisticas_hoje():
    return jsonify(banco().obter_estatisticas_hoje())


@app.route("/api/estatisticas/semana")
def api_estatisticas_semana():
    return jsonify(banco().obter_estatisticas_semana())


# ───────────────────────────── API: observabilidade ─────────────────────────
@app.route("/api/health")
@app.route("/api/saude")
def api_saude():
    modelo = None
    rasa_ok = False
    try:
        estado = http_json(RASA_URL + "/status", timeout=2)
        rasa_ok, modelo = True, estado.get("model_file")
    except Exception:
        pass
    cfg = llm.configuracao()
    return jsonify({
        "status": "ok", "flask": "running", "momento": datetime.now().isoformat(timespec="seconds"),
        "rasa": {"no_ar": rasa_ok, "url": RASA_URL, "modelo": modelo},
        "actions": {"no_ar": servico_no_ar(ACTIONS_URL + "/health"), "url": ACTIONS_URL},
        "llm": {"configurado": cfg["configurado"], "provedor": cfg["provedor"], "modelo": cfg["modelo"],
                "externo": cfg["externo"]},
        "replay_disponivel": os.path.exists(ARQUIVO_REPLAY),
        "interacoes": banco().resumo_interacoes(),
    })


if __name__ == "__main__":
    porta = int(os.getenv("FLASK_PORT", "5001"))
    # 127.0.0.1 = so esta maquina. Para a turma acessar pela rede local, defina
    # FLASK_HOST=0.0.0.0 no .env (e leia o aviso de privacidade no README).
    host = os.getenv("FLASK_HOST", "127.0.0.1")
    print("=" * 62)
    print(" ASSISTENTE DE ATIVIDADES v2 - interface web")
    print(" Chat + Raio-X : http://localhost:%d" % porta)
    print(" Mural         : http://localhost:%d/mural" % porta)
    print(" Duelo         : http://localhost:%d/duelo" % porta)
    print(" Replay        : http://localhost:%d/replay" % porta)
    print(" Dashboard     : http://localhost:%d/dashboard" % porta)
    print("=" * 62)
    app.run(host=host, port=porta, debug=False, use_reloader=False, threaded=True)
