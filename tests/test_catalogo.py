# -*- coding: utf-8 -*-
"""Regras deterministicas (catalogo.py). Rodam sem o Rasa: python -m pytest tests"""
from datetime import datetime

import pytest

from actions import catalogo


@pytest.mark.parametrize("entrada,esperado", [
    ("meditei", "meditação"), ("Meditação", "meditação"), ("caminhei", "caminhada"),
    ("malhei", "musculação"), ("nadei", "natação"), ("corri", "corrida"),
    ("água", "água"), ("agua", "água"), ("pedalei", "ciclismo"), ("ioga", "yoga"),
    ("pilates", "pilates"),          # desconhecido: mantem o que a pessoa disse
])
def test_normalizar_tipo(entrada, esperado):
    assert catalogo.normalizar_tipo(entrada) == esperado


def test_normalizar_tipo_vazio():
    assert catalogo.normalizar_tipo(None) is None
    assert catalogo.normalizar_tipo("  ") is None


def test_resgate_so_cobre_a_lista_herdada_da_v1():
    assert catalogo.resgatar_tipo_do_texto("corri 30 minutos") == "corrida"
    assert catalogo.resgatar_tipo_do_texto("fui na academia") == "musculação"
    # Falhas mantidas de proposito para a aula:
    assert catalogo.resgatar_tipo_do_texto("bebi h2o") is None
    assert catalogo.resgatar_tipo_do_texto("tomei um café") is None


@pytest.mark.parametrize("texto,entidade,esperado", [
    ("malhei 1 hora", "1", 60.0),            # v1 gravava 1 minuto
    ("nadei meia hora", None, 30.0),         # v1 gravava sem duracao
    ("corri 1h30", None, 90.0),
    ("pedalei 2 horas e meia", "2", 150.0),
    ("corri 30 minutos intenso", "30", 30.0),
    ("corri 30 min", "30", 30.0),
    ("caminhei uma hora", None, 60.0),
    ("45", "45", 45.0),
    ("45", None, 45.0),
    ("bebi água", None, None),
    ("forte", "forte", None),
])
def test_extrair_duracao(texto, entidade, esperado):
    assert catalogo.extrair_duracao_min(texto, entidade) == esperado


def test_duracao_valida_segue_a_regra_de_1_a_300():
    assert catalogo.duracao_valida(1) and catalogo.duracao_valida(300)
    assert not catalogo.duracao_valida(0) and not catalogo.duracao_valida(301)
    assert not catalogo.duracao_valida(None)


@pytest.mark.parametrize("entrada,esperado", [
    ("intenso", "intensa"), ("intensa", "intensa"), ("forte", "intensa"), ("pesado", "intensa"),
    ("moderado", "moderada"), ("leve", "leve"), ("relaxante", "leve"), ("bem leve", "leve"),
    ("muito", None), (None, None),
])
def test_normalizar_intensidade(entrada, esperado):
    assert catalogo.normalizar_intensidade(entrada) == esperado


AGORA = datetime(2026, 11, 19, 10, 0)   # quinta-feira, dia da aula


@pytest.mark.parametrize("texto,data,hora,entendeu", [
    ("agendar yoga amanhã às 7h", "2026-11-20", "07:00", True),
    ("marcar corrida hoje às 19h30", "2026-11-19", "19:30", True),
    ("agendar natação para sexta 18:30", "2026-11-20", "18:30", True),
    ("vou correr na quinta às 6h", "2026-11-26", "06:00", True),     # quinta dita numa quinta = a proxima
    ("agendar yoga depois de amanhã", "2026-11-21", None, True),
    ("marcar caminhada às 8 da noite", "2026-11-19", "20:00", False),
    ("agendar corrida", "2026-11-19", None, False),
    ("marcar exercício para dia 25 às 18h", "2026-11-25", "18:00", True),
    ("agende yoga para amanhã às 7 da manhã", "2026-11-20", "07:00", True),
])
def test_extrair_quando(texto, data, hora, entendeu):
    q = catalogo.extrair_quando(texto, AGORA)
    assert (q["data"], q["hora"], q["entendeu_data"]) == (data, hora, entendeu)


def test_descrever_data():
    assert catalogo.descrever_data("2026-11-19", AGORA) == "hoje"
    assert catalogo.descrever_data("2026-11-20", AGORA) == "amanhã"
    assert catalogo.descrever_data("2026-11-25", AGORA) == "qua 25/11"


def test_saudacao_do_periodo():
    assert [catalogo.saudacao_do_periodo(h) for h in (0, 11, 12, 17, 18, 23)] == \
        ["Bom dia", "Bom dia", "Boa tarde", "Boa tarde", "Boa noite", "Boa noite"]
