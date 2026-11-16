# -*- coding: utf-8 -*-
"""
Roda o roteiro da demonstracao de ponta a ponta contra os servicos NO AR
(interface -> Rasa -> Action Server -> banco) e confere cada resposta.

    python run.py roteiro                  confere o roteiro
    python run.py roteiro --apos-correcao  espera que "bebi h2o" ja funcione
    python run.py gravar-replay            confere e grava web_interface/replay/roteiro_gravado.json

Usa um usuario novo a cada execucao, entao nao mexe nos registros de ninguem.
Codigo de saida: 0 se tudo conferiu, 1 se algum passo divergiu.
"""
import json
import os
import platform
import sys
import time
import urllib.request

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
args = sys.argv[1:]
url = args[args.index("--url") + 1] if "--url" in args else "http://localhost:5001"
gravar, apos_correcao = "--gravar" in args, "--apos-correcao" in args


def chamar(caminho, corpo=None):
    dados = json.dumps(corpo).encode("utf-8") if corpo is not None else None
    requisicao = urllib.request.Request(url + caminho, data=dados)
    if dados:
        requisicao.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(requisicao, timeout=60) as resposta:
        return json.loads(resposta.read().decode("utf-8"))


with open(os.path.join(RAIZ, "tests", "e2e", "roteiro_demo.json"), encoding="utf-8") as arquivo:
    roteiro = json.load(arquivo)

saude = chamar("/api/saude")
if not (saude["rasa"]["no_ar"] and saude["actions"]["no_ar"]):
    sys.exit("Rasa ou Action Server fora do ar. Rode: python run.py start")

usuario = "demo" + time.strftime("%H%M%S")
turnos, falhas = [], 0
print("Usuario do roteiro: %s | modelo: %s\n" % (usuario, saude["rasa"]["modelo"]))
for numero, passo in enumerate(roteiro["passos"], 1):
    turno = chamar("/api/chat", {"mensagem": passo["fala"], "usuario": usuario})
    texto = "\n".join(turno["respostas"])
    esperado = passo.get("apos_correcao") if (apos_correcao and passo.get("apos_correcao")) else passo.get("espera", [])
    problemas = [("faltou: " + t) for t in esperado if t not in texto]
    problemas += [("nao deveria conter: " + t) for t in passo.get("nao_espera", []) if t in texto]
    if passo.get("espera_um_de") and not any(t in texto for t in passo["espera_um_de"]):
        problemas.append("faltou um de: " + " | ".join(passo["espera_um_de"]))
    if passo.get("intent") and turno["raiox"]["intent"]["nome"] != passo["intent"]:
        problemas.append("intent %s (esperado %s)" % (turno["raiox"]["intent"]["nome"], passo["intent"]))
    for tabela in ("atividades", "agenda"):
        if ("banco_" + tabela) in passo and len(turno["raiox"]["banco"][tabela]) != passo["banco_" + tabela]:
            problemas.append("linhas novas em %s: %d (esperado %d)" % (
                tabela, len(turno["raiox"]["banco"][tabela]), passo["banco_" + tabela]))
    falhas += bool(problemas)
    print("%2d. [%s] %s" % (numero, "OK  " if not problemas else "FALHA", passo["fala"]))
    print("      intent=%s (%.2f) | acoes=%s" % (
        turno["raiox"]["intent"]["nome"], turno["raiox"]["intent"]["confianca"] or 0,
        [a["nome"] for a in turno["raiox"]["acoes"] if a["nome"] != "action_listen"]))
    print("      bot: " + texto.replace("\n", " / "))
    for p in problemas:
        print("      >>> " + p)
    turno.update({"ato": passo.get("ato"), "nota": passo.get("nota"), "falha_proposital": passo.get("falha_proposital", False)})
    turnos.append(turno)

outro = chamar("/api/chat", {"mensagem": roteiro["isolamento"]["fala"], "usuario": usuario + "b"})
texto = "\n".join(outro["respostas"])
ok_iso = all(t in texto for t in roteiro["isolamento"]["espera"])
falhas += not ok_iso
print("\nIsolamento entre usuarios: [%s] outro usuario recebeu: %s" % ("OK  " if ok_iso else "FALHA", texto.replace("\n", " / ")))
print("\nResultado: %d passo(s) divergente(s) de %d." % (falhas, len(roteiro["passos"]) + 1))

if gravar:
    if falhas:
        sys.exit("Nao gravei o replay porque o roteiro divergiu.")
    destino = os.path.join(RAIZ, "web_interface", "replay", "roteiro_gravado.json")
    with open(destino, "w", encoding="utf-8") as arquivo:
        json.dump({"gravado_em": time.strftime("%d/%m/%Y %H:%M"),
                   "ambiente": "%s %s, Python %s" % (platform.system(), platform.machine(), platform.python_version()),
                   "modelo": saude["rasa"]["modelo"], "turnos": turnos}, arquivo, ensure_ascii=False, indent=1)
    print("Replay gravado em web_interface/replay/roteiro_gravado.json (%d falas)." % len(turnos))
sys.exit(1 if falhas else 0)
