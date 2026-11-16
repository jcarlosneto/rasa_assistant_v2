# -*- coding: utf-8 -*-
"""Confere que nenhuma frase de rasa/tests/nlu_inedito.yml aparece em rasa/data/nlu.yml.
Uso: python tests/checar_ineditas.py   (codigo de saida 1 se houver repeticao)"""
import os
import re
import sys

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def frases(caminho):
    encontradas = set()
    with open(caminho, encoding="utf-8") as arquivo:
        for linha in arquivo:
            m = re.match(r"\s+- (.+)$", linha)
            if m and not m.group(1).startswith("intent:"):
                texto = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", m.group(1))
                encontradas.add(texto.strip().lower())
    return encontradas


treino = frases(os.path.join(RAIZ, "rasa", "data", "nlu.yml"))
prova = frases(os.path.join(RAIZ, "rasa", "tests", "nlu_inedito.yml"))
repetidas = sorted(treino & prova)
print("frases de treino: %d | frases da prova: %d | repetidas: %d" % (len(treino), len(prova), len(repetidas)))
for frase in repetidas:
    print("  REPETIDA:", frase)
sys.exit(1 if repetidas else 0)
