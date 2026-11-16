# -*- coding: utf-8 -*-
"""Banco de dados: separacao por usuario, semana de 7 dias, sequencia, agenda, mural, migracao."""
import sqlite3
from datetime import datetime, timedelta

import pytest

from actions.database import AtividadesDatabase

AGORA = datetime(2026, 11, 19, 10, 0)


@pytest.fixture
def db(tmp_path):
    return AtividadesDatabase(str(tmp_path / "teste.db"))


def test_cada_usuario_ve_so_o_que_e_seu(db):
    db.registrar_atividade("água", usuario="ana", agora=AGORA)
    db.registrar_atividade("corrida", 30, "intensa", usuario="bia", agora=AGORA)
    assert [a["tipo"] for a in db.obter_atividades_hoje("ana", AGORA)] == ["água"]
    assert db.obter_estatisticas_hoje("bia", AGORA)["total"] == 1
    assert db.obter_estatisticas_hoje(None, AGORA)["total"] == 2      # None = turma toda


def test_semana_tem_exatamente_7_dias(db):
    for dias_atras in (0, 6, 7):                  # o de 7 dias atras fica de fora
        db.registrar_atividade("água", usuario="ana", agora=AGORA - timedelta(days=dias_atras))
    stats = db.obter_estatisticas_semana("ana", AGORA)
    assert stats["total"] == 2
    assert stats["media_dia"] == pytest.approx(2 / 7)
    serie = db.serie_7_dias("ana", AGORA)
    assert len(serie) == 7 and serie[-1] == ("2026-11-19", 1) and serie[0] == ("2026-11-13", 1)


def test_sequencia_de_dias(db):
    assert db.sequencia_dias("ana", AGORA) == 0
    for dias_atras in (0, 1, 2, 4):               # buraco no dia 3
        db.registrar_atividade("água", usuario="ana", agora=AGORA - timedelta(days=dias_atras))
    assert db.sequencia_dias("ana", AGORA) == 3


def test_agenda_e_baixa(db):
    db.agendar("ana", "yoga", "2026-11-20", "07:00", agora=AGORA)
    db.agendar("ana", "caminhada", "2026-11-19", "23:00", agora=AGORA)
    db.agendar("bia", "caminhada", "2026-11-19", None, agora=AGORA)
    itens = db.listar_agenda("ana", a_partir="2026-11-19")
    assert [(i["tipo"], i["data"]) for i in itens] == [("caminhada", "2026-11-19"), ("yoga", "2026-11-20")]
    assert db.concluir_agendamento("ana", "yoga", AGORA) is None            # yoga e amanha
    assert db.concluir_agendamento("ana", "caminhada", AGORA)["hora"] == "23:00"
    assert db.concluir_agendamento("ana", "caminhada", AGORA) is None       # nao da baixa duas vezes
    assert len(db.listar_agenda("bia", a_partir="2026-11-19")) == 1         # a de bia continua pendente


def test_mural_registra_quebra_automatica_e_reportada(db):
    a = db.registrar_interacao("ana", "tomei um café", "registrar_atividade_rapido", 0.97, [], [], "não identifiquei", 40,
                               "entendeu a intenção, mas não a atividade", agora=AGORA)
    b = db.registrar_interacao("bia", "malhei 1 hora", "registrar_atividade_rapido", 1.0, [], [], "ok", 35, None, agora=AGORA)
    db.registrar_interacao("bia", "bebi água", "registrar_atividade_rapido", 1.0, [], [], "ok", 30, None, agora=AGORA)
    assert db.reportar_quebra(b, "gravou 1 minuto")
    assert not db.reportar_quebra(9999)
    quebras = db.listar_quebras()
    assert {q["id"] for q in quebras} == {a, b}
    resumo = db.resumo_interacoes()
    assert resumo["total"] == 3 and resumo["quebras"] == 2
    assert resumo["taxa_quebra"] == pytest.approx(2 / 3) and resumo["latencia_media_ms"] == 35


def test_migra_banco_da_v1_sem_perder_linhas(tmp_path):
    caminho = str(tmp_path / "v1.db")
    conn = sqlite3.connect(caminho)
    conn.execute("""CREATE TABLE atividades (id INTEGER PRIMARY KEY AUTOINCREMENT, tipo TEXT NOT NULL,
                    duracao REAL, intensidade TEXT, data TEXT NOT NULL, hora TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)""")
    conn.execute("INSERT INTO atividades (tipo, data, hora) VALUES ('água', '2026-11-19', '08:00')")
    conn.commit()
    conn.close()
    db = AtividadesDatabase(caminho)                      # abre com o codigo da v2
    linhas = db.obter_atividades_hoje(None, AGORA)
    assert len(linhas) == 1 and linhas[0]["usuario"] == "user" and linhas[0]["tipo"] == "água"
