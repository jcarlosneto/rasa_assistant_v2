#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
run.py - um unico comando para instalar, treinar, subir e testar o assistente.
Funciona em macOS, Linux e Windows; usa so a biblioteca padrao do Python.

    python run.py setup             cria o ambiente rasa-env (Python 3.10) e instala tudo
    python run.py train             treina o modelo (rasa/models/chatbot-assistant-v2.tar.gz)
    python run.py start [--abrir]   sobe os 3 servicos em segundo plano
    python run.py status            mostra o que esta no ar
    python run.py stop              derruba os 3 servicos
    python run.py test              roda todas as verificacoes automaticas
    python run.py roteiro           conversa de ponta a ponta contra os servicos no ar
    python run.py gravar-replay     grava o roteiro para a tela Replay
    python run.py replay [--abrir]  sobe SO a interface (sem Rasa) para o Replay
    python run.py corrigir-ao-vivo  aplica a correcao "h2o" no nlu.yml (depois: train)
    python run.py desfazer-correcao desfaz a correcao acima
    python run.py limpar-banco --sim  apaga atividades, agenda e mural
    python run.py actions | rasa | web   sobe UM servico em primeiro plano

Por que Python 3.10? O Rasa Open Source 3.6.21 (ultima versao aberta) so instala
em Python 3.8, 3.9 ou 3.10. O `setup` usa a ferramenta `uv`, que baixa o
Python 3.10 sozinha, sem mexer no Python do seu sistema.
"""
import json
import os
import shutil
import signal
import subprocess
import sys
import time
import urllib.request
import webbrowser

RAIZ = os.path.dirname(os.path.abspath(__file__))
VENV = os.path.join(RAIZ, "rasa-env")
WINDOWS = os.name == "nt"
PY_VENV = os.path.join(VENV, "Scripts", "python.exe") if WINDOWS else os.path.join(VENV, "bin", "python")
PASTA_RASA = os.path.join(RAIZ, "rasa")
MODELO = os.path.join("models", "chatbot-assistant-v2.tar.gz")
PASTA_RUN = os.path.join(RAIZ, ".run")
PASTA_LOGS = os.path.join(RAIZ, "logs")
ARQ_PIDS = os.path.join(PASTA_RUN, "pids.json")
NLU = os.path.join(PASTA_RASA, "data", "nlu.yml")
PATCH = os.path.join(RAIZ, "demo", "correcao_ao_vivo", "nlu_patch_h2o.yml")


def ambiente():
    env = dict(os.environ)
    env["RASA_TELEMETRY_ENABLED"] = "false"      # o Rasa envia telemetria anonima por padrao; aqui fica desligada
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONUTF8"] = "1"                      # acentos e emojis no terminal do Windows
    # O servidor de actions (rasa_sdk) nao aceita -i; le o endereco de SANIC_HOST e, sem ela,
    # escuta em 0.0.0.0 (toda a rede). Aqui fica so nesta maquina, como o Rasa (-i 127.0.0.1).
    env.setdefault("SANIC_HOST", "127.0.0.1")
    return env


def porta_web():
    porta = os.getenv("FLASK_PORT")
    caminho = os.path.join(RAIZ, ".env")
    if not porta and os.path.exists(caminho):
        for linha in open(caminho, encoding="utf-8"):
            if linha.strip().startswith("FLASK_PORT="):
                porta = linha.split("=", 1)[1].split("#")[0].strip()
    return int(porta or 5001)


def exigir_venv():
    if not os.path.exists(PY_VENV):
        sys.exit("Ambiente rasa-env nao encontrado. Rode primeiro:  python run.py setup")


def no_ar(url, timeout=2):
    try:
        with urllib.request.urlopen(url, timeout=timeout) as r:
            return r.status == 200
    except Exception:
        return False


def comando(nome):
    """Linha de comando e pasta de trabalho de cada servico."""
    if nome == "actions":
        return [PY_VENV, "-m", "rasa", "run", "actions", "--actions", "actions", "--port", "5055"], PASTA_RASA
    if nome == "rasa":
        if not os.path.exists(os.path.join(PASTA_RASA, MODELO)):
            sys.exit("Modelo nao encontrado em rasa/%s. Rode:  python run.py train" % MODELO.replace(os.sep, "/"))
        # -i 127.0.0.1: a API do Rasa fica acessivel so nesta maquina (ela nao tem autenticacao).
        return [PY_VENV, "-m", "rasa", "run", "--model", MODELO, "--enable-api", "--port", "5005",
                "-i", "127.0.0.1", "--endpoints", "endpoints.yml", "--credentials", "credentials.yml"], PASTA_RASA
    if nome == "web":
        interpretador = PY_VENV if os.path.exists(PY_VENV) else sys.executable
        return [interpretador, "app.py"], os.path.join(RAIZ, "web_interface")
    raise ValueError(nome)


URLS = {"actions": "http://localhost:5055/health", "rasa": "http://localhost:5005/status"}


def url_saude(nome):
    return URLS.get(nome) or "http://localhost:%d/api/health" % porta_web()


# ───────────────────────────── instalacao ─────────────────────────────
def cmd_setup(_args):
    uv = shutil.which("uv")
    if uv:
        print(">> Criando rasa-env com Python 3.10 (via uv)...")
        subprocess.check_call([uv, "venv", "--python", "3.10", VENV])
        subprocess.check_call([uv, "pip", "install", "--python", PY_VENV, "-r", os.path.join(RAIZ, "requirements.txt")])
    else:
        candidatos = [["py", "-3.10"]] if WINDOWS else []
        candidatos += [["python3.10"], ["python3.9"], ["python3.8"]]
        base = next((c for c in candidatos if shutil.which(c[0])), None)
        if sys.version_info[:2] in ((3, 8), (3, 9), (3, 10)):
            base = [sys.executable]
        if not base:
            sys.exit(
                "Nao encontrei Python 3.8-3.10 nem a ferramenta uv.\n"
                "Caminho mais simples: instale o uv (https://docs.astral.sh/uv/) e rode de novo.\n"
                "Seu Python atual e %d.%d, que o Rasa 3.6.21 nao aceita." % sys.version_info[:2])
        print(">> Criando rasa-env com", " ".join(base))
        subprocess.check_call(base + ["-m", "venv", VENV])
        subprocess.check_call([PY_VENV, "-m", "pip", "install", "--upgrade", "pip"])
        subprocess.check_call([PY_VENV, "-m", "pip", "install", "-r", os.path.join(RAIZ, "requirements.txt")])
    if not os.path.exists(os.path.join(RAIZ, ".env")):
        shutil.copy(os.path.join(RAIZ, ".env.example"), os.path.join(RAIZ, ".env"))
        print(">> Criei o arquivo .env a partir do .env.example")
    print("\nPronto. Proximo passo:  python run.py train")


def cmd_train(_args):
    exigir_venv()
    inicio = time.time()
    codigo = subprocess.call(
        [PY_VENV, "-m", "rasa", "train", "--domain", "domain.yml", "--config", "config.yml", "--data", "data",
         "--out", "models", "--fixed-model-name", "chatbot-assistant-v2"], cwd=PASTA_RASA, env=ambiente())
    print("\nTreino %s em %d s." % ("concluido" if codigo == 0 else "FALHOU", time.time() - inicio))
    sys.exit(codigo)


# ───────────────────────────── servicos ─────────────────────────────
def ler_pids():
    if os.path.exists(ARQ_PIDS):
        with open(ARQ_PIDS) as arquivo:
            return json.load(arquivo)
    return {}


def subir(nome):
    linha, pasta = comando(nome)
    os.makedirs(PASTA_LOGS, exist_ok=True)
    log = open(os.path.join(PASTA_LOGS, nome + ".log"), "w", encoding="utf-8")
    extra = {"creationflags": subprocess.CREATE_NEW_PROCESS_GROUP} if WINDOWS else {"start_new_session": True}
    return subprocess.Popen(linha, cwd=pasta, env=ambiente(), stdout=log, stderr=subprocess.STDOUT, **extra).pid


def esperar(nome, segundos):
    limite = time.time() + segundos
    while time.time() < limite:
        if no_ar(url_saude(nome)):
            return True
        time.sleep(1.5)
    return False


def cmd_start(args, servicos=("actions", "rasa", "web")):
    if "rasa" in servicos:
        exigir_venv()
    if any(no_ar(url_saude(s)) for s in servicos):
        sys.exit("Ja existe servico no ar. Rode `python run.py stop` antes (ou `status` para ver).")
    os.makedirs(PASTA_RUN, exist_ok=True)
    pids = {}
    for nome in servicos:
        pids[nome] = subir(nome)
        print(">> %-7s iniciando (pid %s) - log em logs/%s.log" % (nome, pids[nome], nome))
    with open(ARQ_PIDS, "w") as arquivo:
        json.dump(pids, arquivo)
    print(">> Aguardando os servicos responderem (o Rasa leva de 20 s a alguns minutos)...")
    tudo_ok = True
    for nome in servicos:
        ok = esperar(nome, 300 if nome == "rasa" else 60)
        tudo_ok = tudo_ok and ok
        print("   %-7s %s" % (nome, "no ar" if ok else "NAO respondeu - veja logs/%s.log" % nome))
    endereco = "http://localhost:%d/%s" % (porta_web(), "replay" if servicos == ("web",) else "")
    print("\nInterface: " + endereco)
    if "--abrir" in args and tudo_ok:
        webbrowser.open(endereco)
    sys.exit(0 if tudo_ok else 1)


def cmd_stop(_args):
    for nome, pid in ler_pids().items():
        try:
            if WINDOWS:
                subprocess.call(["taskkill", "/T", "/F", "/PID", str(pid)],
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            else:
                os.killpg(os.getpgid(pid), signal.SIGTERM)
            print(">> %-7s parado (pid %s)" % (nome, pid))
        except (ProcessLookupError, PermissionError, OSError):
            print(">> %-7s ja nao estava rodando" % nome)
    if os.path.exists(ARQ_PIDS):
        os.remove(ARQ_PIDS)


def cmd_status(_args):
    for nome in ("actions", "rasa", "web"):
        print("%-7s %s  (%s)" % (nome, "NO AR" if no_ar(url_saude(nome)) else "fora ", url_saude(nome)))


def cmd_frente(nome):
    linha, pasta = comando(nome)
    if nome != "web":
        exigir_venv()
    sys.exit(subprocess.call(linha, cwd=pasta, env=ambiente()))


# ───────────────────────────── verificacoes ─────────────────────────────
def cmd_test(_args):
    exigir_venv()
    etapas = [
        ("Testes unitarios (pytest)", [PY_VENV, "-m", "pytest", "-q", "tests"], RAIZ),
        ("Frases da prova nao repetem o treino", [PY_VENV, os.path.join("tests", "checar_ineditas.py")], RAIZ),
        ("Validacao dos dados do Rasa", [PY_VENV, "-m", "rasa", "data", "validate", "--domain", "domain.yml",
                                         "--data", "data", "--config", "config.yml"], PASTA_RASA),
    ]
    if os.path.exists(os.path.join(PASTA_RASA, MODELO)):
        etapas += [
            ("Testes de conversa (rasa test core)", [PY_VENV, "-m", "rasa", "test", "core", "--model", MODELO,
                                                     "--stories", os.path.join("tests", "test_stories.yml"),
                                                     "--out", os.path.join("..", "logs", "resultados_core")], PASTA_RASA),
            ("Prova do NLU com frases ineditas (rasa test nlu)", [PY_VENV, "-m", "rasa", "test", "nlu", "--model", MODELO,
                                                                  "--nlu", os.path.join("tests", "nlu_inedito.yml"),
                                                                  "--out", os.path.join("..", "logs", "resultados_nlu")], PASTA_RASA),
        ]
    else:
        print("AVISO: sem modelo treinado - os testes do Rasa que dependem de modelo foram PULADOS.")
    os.makedirs(PASTA_LOGS, exist_ok=True)
    falhas = 0
    for titulo, linha, pasta in etapas:
        print("\n=== %s ===" % titulo)
        codigo = subprocess.call(linha, cwd=pasta, env=ambiente())
        print("--> %s" % ("OK" if codigo == 0 else "FALHOU (codigo %d)" % codigo))
        falhas += codigo != 0
    relatorio = os.path.join(PASTA_LOGS, "resultados_nlu", "intent_report.json")
    if os.path.exists(relatorio):
        with open(relatorio) as arquivo:
            print("\nAcuracia de intencao nas frases ineditas: %.1f%%  (detalhes em logs/resultados_nlu/)"
                  % (json.load(arquivo)["accuracy"] * 100))
    print("\nResumo: %d etapa(s) com falha de %d." % (falhas, len(etapas)))
    print("Lembrete: `rasa test core` retorna 0 mesmo com conversas reprovadas; confira logs/resultados_core/.")
    sys.exit(1 if falhas else 0)


def cmd_roteiro(args, gravar=False):
    interpretador = PY_VENV if os.path.exists(PY_VENV) else sys.executable
    linha = [interpretador, os.path.join("tests", "e2e", "rodar_roteiro.py"), "--url", "http://localhost:%d" % porta_web()]
    if gravar:
        linha.append("--gravar")
    sys.exit(subprocess.call(linha + [a for a in args if a.startswith("--")], cwd=RAIZ, env=ambiente()))


# ───────────────────────────── correcao ao vivo ─────────────────────────────
ANCORA = "  - intent: registrar_atividade_rapido\n    examples: |\n"


def _bloco_da_correcao():
    """Linhas de exemplo do arquivo de correcao, ja com a indentacao do nlu.yml.
    (Nao ha comentario marcador: dentro de um bloco `examples: |` do YAML,
    uma linha de comentario encerraria o bloco e quebraria o arquivo.)"""
    exemplos = [l.strip() for l in open(PATCH, encoding="utf-8").read().splitlines() if l.strip().startswith("- ")]
    return "".join("      " + l + "\n" for l in exemplos), len(exemplos)


def cmd_corrigir(_args):
    texto = open(NLU, encoding="utf-8").read()
    bloco, quantos = _bloco_da_correcao()
    if ANCORA + bloco in texto:
        sys.exit("A correcao ja esta aplicada.")
    if ANCORA not in texto:
        sys.exit("Nao encontrei o intent registrar_atividade_rapido no nlu.yml.")
    open(NLU, "w", encoding="utf-8").write(texto.replace(ANCORA, ANCORA + bloco, 1))
    print("Inseri %d exemplos em rasa/data/nlu.yml. Agora:  python run.py stop && python run.py train && python run.py start"
          % quantos)


def cmd_desfazer(_args):
    texto = open(NLU, encoding="utf-8").read()
    bloco, _ = _bloco_da_correcao()
    if ANCORA + bloco not in texto:
        sys.exit("Nao ha correcao aplicada.")
    open(NLU, "w", encoding="utf-8").write(texto.replace(ANCORA + bloco, ANCORA, 1))
    print("Correcao removida. Retreine para voltar ao comportamento original.")


def cmd_limpar(args):
    if "--sim" not in args:
        sys.exit("Isto APAGA atividades, agenda e mural. Confirme com:  python run.py limpar-banco --sim")
    sys.path.insert(0, PASTA_RASA)
    from actions.database import AtividadesDatabase
    AtividadesDatabase().limpar_tudo()
    print("Banco limpo.")


COMANDOS = {
    "setup": cmd_setup, "train": cmd_train, "start": cmd_start, "stop": cmd_stop, "status": cmd_status,
    "test": cmd_test, "roteiro": cmd_roteiro, "gravar-replay": lambda a: cmd_roteiro(a, gravar=True),
    "replay": lambda a: cmd_start(a, servicos=("web",)),
    "corrigir-ao-vivo": cmd_corrigir, "desfazer-correcao": cmd_desfazer, "limpar-banco": cmd_limpar,
    "actions": lambda a: cmd_frente("actions"), "rasa": lambda a: cmd_frente("rasa"), "web": lambda a: cmd_frente("web"),
}

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in COMANDOS:
        print(__doc__)
        sys.exit(0 if len(sys.argv) < 2 else 2)
    COMANDOS[sys.argv[1]](sys.argv[2:])
