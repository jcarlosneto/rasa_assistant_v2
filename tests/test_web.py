# -*- coding: utf-8 -*-
"""Interface web testada com o Rasa SUBSTITUIDO por respostas fixas.
Confere o que e responsabilidade do Flask: montar o Raio-X a partir do tracker,
sinalizar falhas para o mural, separar usuarios, exportar CSV, escapar entradas."""
import importlib
import json

import pytest

TRACKER = {
    "active_loop": {}, "slots": {"tipo_atividade": None, "duracao": None, "intensidade": None, "requested_slot": None},
    "events": [
        {"event": "action", "name": "action_session_start"},
        {"event": "action", "name": "action_listen"},
        {"event": "user", "text": "malhei 1 hora", "parse_data": {
            "intent": {"name": "registrar_atividade_rapido", "confidence": 0.99},
            "intent_ranking": [{"name": "registrar_atividade_rapido", "confidence": 0.99},
                               {"name": "agendar_atividade", "confidence": 0.005}],
            "entities": [{"entity": "tipo_atividade", "value": "malhei", "start": 0, "end": 6, "extractor": "DIETClassifier"},
                         {"entity": "duracao", "value": "1", "start": 7, "end": 8, "extractor": "DIETClassifier"}],
            "text_tokens": [[0, 6], [7, 8], [9, 13]]}},
        {"event": "slot", "name": "tipo_atividade", "value": "malhei"},
        {"event": "action", "name": "action_registrar_atividade", "policy": "policy_1_RulePolicy", "confidence": 1.0},
        {"event": "bot", "text": "✅ Registrei: musculação · 60 min."},
        {"event": "slot", "name": "tipo_atividade", "value": None},
        {"event": "action", "name": "action_listen", "policy": "policy_1_RulePolicy", "confidence": 1.0},
    ]}


@pytest.fixture
def cliente(tmp_path, monkeypatch):
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "web.db"))
    for nome in ("LLM_PROVIDER", "LLM_API_KEY", "LLM_MODEL"):
        monkeypatch.delenv(nome, raising=False)
    import app as modulo
    modulo = importlib.reload(modulo)
    estado = {"tracker": TRACKER, "respostas": [{"text": "✅ Registrei: musculação · 60 min."}], "fora": False}

    def falso_http(url, corpo=None, timeout=15):
        if estado["fora"]:
            raise OSError("conexão recusada")
        if url.endswith("/webhooks/rest/webhook"):
            modulo.banco().registrar_atividade("musculação", 60.0, None, usuario=corpo["sender"])
            return estado["respostas"]
        if "/tracker" in url:
            return estado["tracker"]
        if url.endswith("/model/parse"):
            return TRACKER["events"][2]["parse_data"]
        raise AssertionError("URL inesperada: " + url)

    monkeypatch.setattr(modulo, "http_json", falso_http)
    monkeypatch.setattr(modulo, "ARQUIVO_DUELOS", str(tmp_path / "duelos.json"))
    c = modulo.app.test_client()
    c.estado, c.modulo = estado, modulo
    return c


def test_raiox_vem_do_tracker(cliente):
    r = cliente.post("/api/chat", json={"mensagem": "malhei 1 hora", "usuario": "ana"}).get_json()
    x = r["raiox"]
    assert x["tokens"] == ["malhei", "1", "hora"]
    assert x["intent"] == {"nome": "registrar_atividade_rapido", "confianca": 0.99}
    assert [e["valor"] for e in x["entidades"]] == ["malhei", "1"]
    assert x["acoes"][0] == {"nome": "action_registrar_atividade", "politica": "RulePolicy", "confianca": 1.0}
    assert x["slots_alterados"][0] == {"nome": "tipo_atividade", "valor": "malhei"}
    assert x["banco"]["atividades"][0]["tipo"] == "musculação" and x["banco"]["atividades"][0]["usuario"] == "ana"
    assert r["motivo_auto"] is None and r["respostas"] == ["✅ Registrei: musculação · 60 min."]


def test_falha_reconhecivel_vai_para_o_mural(cliente):
    cliente.estado["respostas"] = [{"text": "Entendi que você quer registrar algo, mas não identifiquei a atividade. 🤔"}]
    tracker = json.loads(json.dumps(TRACKER))
    tracker["events"][5]["text"] = cliente.estado["respostas"][0]["text"]
    cliente.estado["tracker"] = tracker
    r = cliente.post("/api/chat", json={"mensagem": "tomei um café", "usuario": "bia"}).get_json()
    assert r["motivo_auto"] == "entendeu a intenção, mas não a atividade"
    mural = cliente.get("/api/mural").get_json()
    assert mural["resumo"]["quebras"] == 1 and mural["quebras"][0]["texto"] == "tomei um café"
    yml = cliente.get("/api/mural/nlu.yml").get_data(as_text=True)
    assert "- tomei um café" in yml and "intent: registrar_atividade_rapido" in yml


def test_reportar_quebra_manual(cliente):
    r = cliente.post("/api/chat", json={"mensagem": "malhei 1 hora", "usuario": "ana"}).get_json()
    assert cliente.post("/api/quebra", json={"id": r["id"], "comentario": "deveria ser 60"}).status_code == 200
    assert cliente.post("/api/quebra", json={"id": 99999}).status_code == 404
    assert cliente.post("/api/quebra", json={"id": "x"}).status_code == 400
    quebra = cliente.get("/api/mural").get_json()["quebras"][0]
    assert quebra["quebra_reportada"] == 1 and quebra["comentario"] == "deveria ser 60"


def test_rasa_fora_do_ar_responde_503_com_orientacao(cliente):
    cliente.estado["fora"] = True
    r = cliente.post("/api/chat", json={"mensagem": "oi", "usuario": "ana"})
    assert r.status_code == 503 and "Replay" in r.get_json()["erro"]


def test_mensagem_vazia_e_recusada(cliente):
    assert cliente.post("/api/chat", json={"mensagem": "   ", "usuario": "ana"}).status_code == 400


def test_apelido_e_higienizado(cliente):
    r = cliente.post("/api/chat", json={"mensagem": "malhei 1 hora", "usuario": "<script>alert(1)</script>"}).get_json()
    assert r["usuario"] == "scriptalert1script"


def test_dashboard_separa_usuario_e_turma(cliente):
    cliente.post("/api/chat", json={"mensagem": "malhei 1 hora", "usuario": "ana"})
    cliente.post("/api/chat", json={"mensagem": "malhei 1 hora", "usuario": "bia"})
    assert cliente.get("/api/dashboard?usuario=ana").get_json()["hoje"]["total"] == 1
    turma = cliente.get("/api/dashboard").get_json()
    assert turma["hoje"]["total"] == 2 and len(turma["serie"]) == 7 and turma["sequencia"] == 1
    csv = cliente.get("/api/export.csv?usuario=ana").get_data(as_text=True)
    assert csv.count("\n") == 2 and "ana,musculação,60.0" in csv


def test_duelo_sem_llm_configurado_nao_falha(cliente):
    r = cliente.post("/api/duelo", json={"mensagem": "tomei um café"}).get_json()
    assert r["rasa"]["ok"] is True and r["rasa"]["intent"] == "registrar_atividade_rapido"
    assert r["llm"]["ok"] is False and r["llm"]["configurado"] is False
    assert cliente.post("/api/duelo/gravados", json=r).status_code == 400     # so grava duelo completo


def test_paginas_abrem_e_replay_ausente_e_404(cliente, monkeypatch, tmp_path):
    for rota in ("/", "/mural", "/duelo", "/dashboard", "/replay", "/saude"):
        assert cliente.get(rota).status_code == 200, rota
    monkeypatch.setattr(cliente.modulo, "ARQUIVO_REPLAY", str(tmp_path / "nao_existe.json"))
    assert cliente.get("/api/replay").status_code == 404
