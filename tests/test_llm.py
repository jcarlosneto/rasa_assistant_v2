# -*- coding: utf-8 -*-
"""Cliente de LLM do duelo, testado contra um servidor FALSO local.
Isto prova o encanamento (formato do pedido, leitura da resposta, erros).
NAO prova o comportamento de nenhum modelo real."""
import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

import pytest

import llm

RESPOSTA = {"intencao": "fora_de_escopo", "tipo_atividade": None, "duracao_min": None,
            "intensidade": None, "quando": None, "resposta": "Café não é atividade, mas bom proveito!"}
RECEBIDOS = []


class Falso(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def do_POST(self):
        corpo = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        RECEBIDOS.append({"caminho": self.path, "cabecalhos": dict(self.headers), "corpo": corpo})
        if "erro" in corpo["messages"][-1]["content"]:
            self.send_response(401)
            self.end_headers()
            self.wfile.write(b'{"error": "chave invalida"}')
            return
        texto = "```json\n" + json.dumps(RESPOSTA, ensure_ascii=False) + "\n```"
        if self.path.endswith("/messages"):
            saida = {"content": [{"type": "text", "text": texto}]}
        else:
            saida = {"choices": [{"message": {"content": texto}}]}
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(saida).encode("utf-8"))


@pytest.fixture(scope="module")
def servidor():
    httpd = HTTPServer(("127.0.0.1", 0), Falso)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    yield "http://127.0.0.1:%d/v1" % httpd.server_port
    httpd.shutdown()


def configurar(monkeypatch, provedor, base):
    monkeypatch.setenv("LLM_PROVIDER", provedor)
    monkeypatch.setenv("LLM_API_KEY", "chave-de-teste")
    monkeypatch.setenv("LLM_MODEL", "modelo-de-teste")
    monkeypatch.setenv("LLM_BASE_URL", base)


def test_sem_configuracao_nao_envia_nada(monkeypatch):
    for nome in ("LLM_PROVIDER", "LLM_API_KEY", "LLM_MODEL", "LLM_BASE_URL"):
        monkeypatch.delenv(nome, raising=False)
    antes = len(RECEBIDOS)
    r = llm.interpretar("tomei um café")
    assert r["ok"] is False and r["configurado"] is False and "não configurado" in r["erro"]
    assert len(RECEBIDOS) == antes


@pytest.mark.parametrize("provedor,caminho,cabecalho", [
    ("openai", "/v1/chat/completions", "Authorization"),
    ("anthropic", "/v1/messages", "x-api-key"),
])
def test_formato_do_pedido_e_leitura_da_resposta(monkeypatch, servidor, provedor, caminho, cabecalho):
    configurar(monkeypatch, provedor, servidor)
    r = llm.interpretar("tomei um café")
    assert r["ok"] is True and r["estrutura"] == RESPOSTA and r["modelo"] == "modelo-de-teste"
    assert r["externo"] is False                       # 127.0.0.1 = nao sai da maquina
    pedido = RECEBIDOS[-1]
    assert pedido["caminho"] == caminho
    cabecalhos = {nome.lower(): valor for nome, valor in pedido["cabecalhos"].items()}   # HTTP nao diferencia maiusculas
    assert "chave-de-teste" in cabecalhos[cabecalho.lower()]
    assert pedido["corpo"]["model"] == "modelo-de-teste"
    assert pedido["corpo"]["messages"][-1] == {"role": "user", "content": "tomei um café"}


def test_erro_do_provedor_vira_mensagem_e_nao_excecao(monkeypatch, servidor):
    configurar(monkeypatch, "openai", servidor)
    r = llm.interpretar("provoque um erro")
    assert r["ok"] is False and "HTTP 401" in r["erro"]


def test_chave_nunca_aparece_na_configuracao_publica(monkeypatch, servidor):
    configurar(monkeypatch, "openai", "https://api.exemplo.com/v1")
    cfg = llm.configuracao()
    assert cfg["externo"] is True
    cfg.pop("_chave")
    assert "chave-de-teste" not in json.dumps(cfg)


def test_extrair_json_recusa_texto_sem_objeto():
    with pytest.raises(ValueError):
        llm.extrair_json("desculpe, não sei")
