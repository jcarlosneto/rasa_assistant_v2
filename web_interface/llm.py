# -*- coding: utf-8 -*-
"""
CLIENTE DE LLM para o "Duelo 1.0 x 2.0".

A mesma frase vai para o Rasa classico (classificador treinado) e para um
modelo de linguagem grande (LLM), que recebe apenas uma instrucao em texto.
Este modulo cuida do lado do LLM.

Configuracao (arquivo .env na raiz do projeto):
    LLM_PROVIDER = openai | anthropic     (openai = qualquer API compativel com
                                           Chat Completions: OpenAI, OpenRouter,
                                           Groq, Ollama local etc.)
    LLM_API_KEY  = sua chave              (para Ollama local, qualquer texto)
    LLM_MODEL    = nome exato do modelo   (confira na documentacao do provedor)
    LLM_BASE_URL = opcional               (ex.: http://localhost:11434/v1)

Privacidade: ao usar um provedor externo, a frase digitada SAI da sua maquina.
A tela do duelo avisa isso. Sem chave configurada, nada e enviado.

Usa so a biblioteca padrao (urllib), para rodar em qualquer Python 3.8+.
"""
import json
import os
import re
import time
import urllib.error
import urllib.request
from datetime import datetime

INTENCOES = ["registrar_atividade", "agendar_atividade", "consultar_progresso",
             "consultar_agenda", "saudacao", "despedida", "ajuda", "fora_de_escopo"]

PROMPT_SISTEMA = """Você é o interpretador de um assistente que registra e agenda atividades de bem-estar (água, corrida, yoga, meditação etc.).
Hoje é {hoje}. Leia a mensagem do usuário e responda SOMENTE com um objeto JSON, sem texto antes ou depois, com estas chaves:
"intencao": uma de {intencoes}
"tipo_atividade": atividade em forma de substantivo, minúsculas (ex.: "corrida"), ou null
"duracao_min": número de minutos, ou null
"intensidade": "leve", "moderada", "intensa" ou null
"quando": data e hora em texto curto se for agendamento (ex.: "2026-11-20 07:00"), ou null
"resposta": uma frase curta e simpática, em português do Brasil, que o assistente diria
Regras: não invente dados que não estão na mensagem; beber café, comer ou assuntos gerais NÃO são atividades registráveis (use "fora_de_escopo")."""
VERSAO_PROMPT = "duelo-v1"
# 0 = a mesma frase tende a receber a mesma resposta (comparacao justa com o Rasa,
# que e deterministico). Nao garante repeticao exata em todo provedor/hardware.
TEMPERATURA = 0


def configuracao():
    """Le a configuracao do ambiente. Nunca devolve a chave em si."""
    provedor = (os.getenv("LLM_PROVIDER") or "").strip().lower()
    chave = (os.getenv("LLM_API_KEY") or "").strip()
    modelo = (os.getenv("LLM_MODEL") or "").strip()
    base = (os.getenv("LLM_BASE_URL") or "").strip().rstrip("/")
    if provedor == "anthropic":
        base = base or "https://api.anthropic.com/v1"
    elif provedor == "openai":
        base = base or "https://api.openai.com/v1"
    pronto = provedor in ("openai", "anthropic") and bool(chave) and bool(modelo)
    return {"provedor": provedor, "modelo": modelo, "base_url": base, "configurado": pronto,
            "externo": pronto and not re.match(r"^https?://(localhost|127\.0\.0\.1)", base),
            "_chave": chave}


def _post_json(url, cabecalhos, corpo, timeout):
    dados = json.dumps(corpo).encode("utf-8")
    requisicao = urllib.request.Request(url, data=dados, method="POST")
    requisicao.add_header("Content-Type", "application/json")
    for nome, valor in cabecalhos.items():
        requisicao.add_header(nome, valor)
    with urllib.request.urlopen(requisicao, timeout=timeout) as resposta:
        return json.loads(resposta.read().decode("utf-8"))


def extrair_json(texto):
    """Modelos as vezes embrulham o JSON em ```json ... ``` ou texto extra."""
    texto = (texto or "").strip()
    m = re.search(r"\{.*\}", texto, flags=re.DOTALL)
    if not m:
        raise ValueError("a resposta do modelo não contém um objeto JSON")
    return json.loads(m.group(0))


def interpretar(mensagem, timeout=None):
    """
    Envia a mensagem ao LLM configurado.
    Devolve um dicionario com: ok, estrutura (o JSON interpretado), texto_bruto,
    latencia_ms, provedor, modelo, versao_prompt e, em caso de falha, erro.
    """
    cfg = configuracao()
    saida = {"ok": False, "configurado": cfg["configurado"], "provedor": cfg["provedor"],
             "modelo": cfg["modelo"], "externo": cfg["externo"], "versao_prompt": VERSAO_PROMPT}
    if not cfg["configurado"]:
        saida["erro"] = "LLM não configurado: defina LLM_PROVIDER, LLM_API_KEY e LLM_MODEL no arquivo .env."
        return saida

    timeout = timeout or float(os.getenv("LLM_TIMEOUT", "30"))
    sistema = PROMPT_SISTEMA.format(hoje=datetime.now().strftime("%Y-%m-%d (%A)"),
                                    intencoes=json.dumps(INTENCOES, ensure_ascii=False))
    inicio = time.time()
    try:
        if cfg["provedor"] == "anthropic":
            bruto = _post_json(
                cfg["base_url"] + "/messages",
                {"x-api-key": cfg["_chave"], "anthropic-version": "2023-06-01"},
                {"model": cfg["modelo"], "max_tokens": 400, "system": sistema, "temperature": TEMPERATURA,
                 "messages": [{"role": "user", "content": mensagem}]}, timeout)
            texto = "".join(b.get("text", "") for b in bruto.get("content", []) if b.get("type") == "text")
        else:
            bruto = _post_json(
                cfg["base_url"] + "/chat/completions",
                {"Authorization": "Bearer " + cfg["_chave"]},
                {"model": cfg["modelo"], "temperature": TEMPERATURA,
                 "messages": [{"role": "system", "content": sistema},
                              {"role": "user", "content": mensagem}]}, timeout)
            texto = bruto["choices"][0]["message"]["content"]
        saida["latencia_ms"] = int((time.time() - inicio) * 1000)
        saida["texto_bruto"] = texto
        saida["estrutura"] = extrair_json(texto)
        saida["ok"] = True
    except urllib.error.HTTPError as erro:
        saida["latencia_ms"] = int((time.time() - inicio) * 1000)
        detalhe = erro.read().decode("utf-8", "replace")[:300]
        saida["erro"] = "O provedor respondeu HTTP %s. %s" % (erro.code, detalhe)
    except Exception as erro:  # rede, timeout, JSON invalido...
        saida["latencia_ms"] = int((time.time() - inicio) * 1000)
        saida["erro"] = "%s: %s" % (type(erro).__name__, erro)
    return saida
