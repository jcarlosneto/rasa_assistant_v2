# -*- coding: utf-8 -*-
"""
BANCO DE DADOS (SQLite) - atividades, agenda e mural de interacoes.

O que mudou em relacao a versao 1
---------------------------------
1. Toda linha passa a ter a coluna `usuario` (quem registrou). Bancos antigos
   sao migrados sem perda: as linhas existentes recebem usuario = 'user'.
2. Nova tabela `agenda` (atividades marcadas para o futuro).
3. Nova tabela `interacoes` (cada fala enviada ao bot, para o mural
   "Quebre o bot" e para a tela de observabilidade).
4. A "semana" passa a ser de 7 dias exatos (hoje e os 6 anteriores).

Sem dependencias externas: usa apenas a biblioteca padrao do Python.
"""
import json
import os
import sqlite3
from datetime import datetime, timedelta

RAIZ_PROJETO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))


def carregar_env(caminho=None):
    """Le o arquivo .env da raiz do projeto (se existir) para os.environ.
    Nao sobrescreve variaveis ja definidas no ambiente e ignora comentarios."""
    caminho = caminho or os.path.join(RAIZ_PROJETO, ".env")
    if not os.path.exists(caminho):
        return
    with open(caminho, "r", encoding="utf-8") as arquivo:
        for linha in arquivo:
            linha = linha.strip()
            if not linha or linha.startswith("#") or "=" not in linha:
                continue
            chave, valor = linha.split("=", 1)
            valor = valor.split(" #", 1)[0].strip().strip('"').strip("'")
            os.environ.setdefault(chave.strip(), valor)


carregar_env()


def caminho_do_banco():
    """DATABASE_PATH do .env (relativo a raiz do projeto) ou database/atividades.db."""
    caminho = os.getenv("DATABASE_PATH") or os.path.join("database", "atividades.db")
    if not os.path.isabs(caminho):
        caminho = os.path.join(RAIZ_PROJETO, caminho)
    return os.path.abspath(caminho)


class AtividadesDatabase:
    """Encapsula todas as consultas. `usuario=None` significa "todos" (visao da turma)."""

    def __init__(self, db_path=None):
        self.db_path = os.path.abspath(db_path) if db_path else caminho_do_banco()
        pasta = os.path.dirname(self.db_path)
        if pasta and not os.path.exists(pasta):
            os.makedirs(pasta)
        self._criar_tabelas()

    # ------------------------------------------------------------------ base
    def _conectar(self):
        conn = sqlite3.connect(self.db_path, timeout=10)
        conn.row_factory = sqlite3.Row
        return conn

    def _criar_tabelas(self):
        conn = self._conectar()
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS atividades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tipo TEXT NOT NULL,
                duracao REAL,
                intensidade TEXT,
                data TEXT NOT NULL,
                hora TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )""")
        # Migracao: bancos da versao 1 nao tinham a coluna `usuario`.
        colunas = [linha["name"] for linha in c.execute("PRAGMA table_info(atividades)")]
        if "usuario" not in colunas:
            c.execute("ALTER TABLE atividades ADD COLUMN usuario TEXT NOT NULL DEFAULT 'user'")
        c.execute("""
            CREATE TABLE IF NOT EXISTS agenda (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario TEXT NOT NULL,
                tipo TEXT NOT NULL,
                data TEXT NOT NULL,
                hora TEXT,
                criado_em TEXT NOT NULL,
                concluida_em TEXT
            )""")
        c.execute("""
            CREATE TABLE IF NOT EXISTS interacoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                momento TEXT NOT NULL,
                usuario TEXT NOT NULL,
                texto TEXT NOT NULL,
                intent TEXT,
                confianca REAL,
                entidades TEXT,
                acoes TEXT,
                resposta TEXT,
                latencia_ms INTEGER,
                motivo_auto TEXT,
                quebra_reportada INTEGER NOT NULL DEFAULT 0,
                comentario TEXT
            )""")
        c.execute("CREATE INDEX IF NOT EXISTS idx_data ON atividades(data)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_tipo ON atividades(tipo)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_usuario ON atividades(usuario)")
        conn.commit()
        conn.close()

    @staticmethod
    def _filtro_usuario(usuario, prefixo=" AND "):
        return (prefixo + "usuario = ?", [usuario]) if usuario else ("", [])

    # ------------------------------------------------------------ atividades
    def registrar_atividade(self, tipo, duracao=None, intensidade=None, usuario="user", agora=None):
        agora = agora or datetime.now()
        conn = self._conectar()
        c = conn.cursor()
        c.execute(
            "INSERT INTO atividades (tipo, duracao, intensidade, data, hora, usuario) VALUES (?, ?, ?, ?, ?, ?)",
            (tipo, duracao, intensidade, agora.strftime("%Y-%m-%d"), agora.strftime("%H:%M"), usuario),
        )
        novo_id = c.lastrowid
        conn.commit()
        conn.close()
        return novo_id

    def _listar(self, sql, parametros):
        conn = self._conectar()
        linhas = [dict(l) for l in conn.execute(sql, parametros)]
        conn.close()
        return linhas

    def obter_atividades_hoje(self, usuario=None, agora=None):
        hoje = (agora or datetime.now()).strftime("%Y-%m-%d")
        filtro, extra = self._filtro_usuario(usuario)
        return self._listar(
            "SELECT id, tipo, duracao, intensidade, data, hora, usuario FROM atividades "
            "WHERE data = ?" + filtro + " ORDER BY hora, id", [hoje] + extra)

    def _inicio_semana(self, agora=None):
        return ((agora or datetime.now()) - timedelta(days=6)).strftime("%Y-%m-%d")

    def obter_atividades_semana(self, usuario=None, agora=None):
        filtro, extra = self._filtro_usuario(usuario)
        return self._listar(
            "SELECT id, tipo, duracao, intensidade, data, hora, usuario FROM atividades "
            "WHERE data >= ?" + filtro + " ORDER BY data DESC, hora DESC, id DESC",
            [self._inicio_semana(agora)] + extra)

    def obter_atividades_depois_de(self, ultimo_id, usuario=None):
        """Linhas gravadas depois de `ultimo_id` (usado pelo Raio-X para mostrar o INSERT)."""
        filtro, extra = self._filtro_usuario(usuario)
        return self._listar(
            "SELECT id, tipo, duracao, intensidade, data, hora, usuario FROM atividades "
            "WHERE id > ?" + filtro + " ORDER BY id", [ultimo_id] + extra)

    def maior_id(self, tabela):
        assert tabela in ("atividades", "agenda", "interacoes")
        conn = self._conectar()
        valor = conn.execute("SELECT COALESCE(MAX(id), 0) FROM " + tabela).fetchone()[0]
        conn.close()
        return valor

    def _estatisticas(self, data_inicial, usuario, dias):
        filtro, extra = self._filtro_usuario(usuario)
        params = [data_inicial] + extra
        conn = self._conectar()
        total = conn.execute("SELECT COUNT(*) FROM atividades WHERE data >= ?" + filtro, params).fetchone()[0]
        por_tipo = {l[0]: l[1] for l in conn.execute(
            "SELECT tipo, COUNT(*) FROM atividades WHERE data >= ?" + filtro +
            " GROUP BY tipo ORDER BY COUNT(*) DESC, tipo", params)}
        por_intensidade = {l[0]: l[1] for l in conn.execute(
            "SELECT intensidade, COUNT(*) FROM atividades WHERE data >= ? AND intensidade IS NOT NULL" +
            filtro + " GROUP BY intensidade", params)}
        por_dia = {l[0]: l[1] for l in conn.execute(
            "SELECT data, COUNT(*) FROM atividades WHERE data >= ?" + filtro +
            " GROUP BY data ORDER BY data", params)}
        tempo = conn.execute(
            "SELECT COALESCE(SUM(duracao), 0) FROM atividades WHERE data >= ? AND duracao IS NOT NULL" + filtro,
            params).fetchone()[0]
        conn.close()
        return {"total": total, "por_tipo": por_tipo, "por_intensidade": por_intensidade,
                "por_dia": por_dia, "tempo_total": float(tempo or 0),
                "media_dia": (total / float(dias)) if dias else 0.0}

    def obter_estatisticas_hoje(self, usuario=None, agora=None):
        hoje = (agora or datetime.now()).strftime("%Y-%m-%d")
        return self._estatisticas(hoje, usuario, 1)

    def obter_estatisticas_semana(self, usuario=None, agora=None):
        return self._estatisticas(self._inicio_semana(agora), usuario, 7)

    def serie_7_dias(self, usuario=None, agora=None):
        """Lista de 7 pares (data ISO, total), do mais antigo ate hoje. Dias sem registro valem 0."""
        agora = agora or datetime.now()
        por_dia = self.obter_estatisticas_semana(usuario, agora)["por_dia"]
        dias = [(agora - timedelta(days=d)).strftime("%Y-%m-%d") for d in range(6, -1, -1)]
        return [(dia, por_dia.get(dia, 0)) for dia in dias]

    def sequencia_dias(self, usuario=None, agora=None):
        """Dias consecutivos com pelo menos uma atividade, contando de hoje para tras."""
        agora = agora or datetime.now()
        filtro, extra = self._filtro_usuario(usuario, prefixo=" WHERE ")
        conn = self._conectar()
        dias = {l[0] for l in conn.execute("SELECT DISTINCT data FROM atividades" + filtro, extra)}
        conn.close()
        sequencia, dia = 0, agora
        while dia.strftime("%Y-%m-%d") in dias:
            sequencia += 1
            dia -= timedelta(days=1)
        return sequencia

    # ----------------------------------------------------------------- agenda
    def agendar(self, usuario, tipo, data, hora=None, agora=None):
        agora = agora or datetime.now()
        conn = self._conectar()
        c = conn.cursor()
        c.execute("INSERT INTO agenda (usuario, tipo, data, hora, criado_em) VALUES (?, ?, ?, ?, ?)",
                  (usuario, tipo, data, hora, agora.isoformat(timespec="seconds")))
        novo_id = c.lastrowid
        conn.commit()
        conn.close()
        return novo_id

    def listar_agenda(self, usuario=None, a_partir=None, somente_pendentes=True, ate=None):
        a_partir = a_partir or datetime.now().strftime("%Y-%m-%d")
        filtro, extra = self._filtro_usuario(usuario)
        sql = "SELECT id, usuario, tipo, data, hora, criado_em, concluida_em FROM agenda WHERE data >= ?" + filtro
        params = [a_partir] + extra
        if ate:
            sql += " AND data <= ?"
            params.append(ate)
        if somente_pendentes:
            sql += " AND concluida_em IS NULL"
        return self._listar(sql + " ORDER BY data, COALESCE(hora, '99:99'), id", params)

    def obter_agenda_depois_de(self, ultimo_id, usuario=None):
        filtro, extra = self._filtro_usuario(usuario)
        return self._listar("SELECT id, usuario, tipo, data, hora, concluida_em FROM agenda WHERE id > ?" +
                            filtro + " ORDER BY id", [ultimo_id] + extra)

    def concluir_agendamento(self, usuario, tipo, agora=None):
        """Se houver agendamento pendente de hoje para este tipo, marca como concluido.
        Devolve o agendamento concluido (dict) ou None."""
        agora = agora or datetime.now()
        hoje = agora.strftime("%Y-%m-%d")
        conn = self._conectar()
        linha = conn.execute(
            "SELECT id, tipo, data, hora FROM agenda WHERE usuario = ? AND tipo = ? AND data = ? "
            "AND concluida_em IS NULL ORDER BY COALESCE(hora, '99:99'), id LIMIT 1",
            (usuario, tipo, hoje)).fetchone()
        if linha is None:
            conn.close()
            return None
        conn.execute("UPDATE agenda SET concluida_em = ? WHERE id = ?",
                     (agora.isoformat(timespec="seconds"), linha["id"]))
        conn.commit()
        conn.close()
        return dict(linha)

    # ------------------------------------------------------- mural/interacoes
    def registrar_interacao(self, usuario, texto, intent, confianca, entidades, acoes,
                            resposta, latencia_ms, motivo_auto=None, agora=None):
        agora = agora or datetime.now()
        conn = self._conectar()
        c = conn.cursor()
        c.execute(
            "INSERT INTO interacoes (momento, usuario, texto, intent, confianca, entidades, acoes, "
            "resposta, latencia_ms, motivo_auto) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (agora.isoformat(timespec="seconds"), usuario, texto, intent, confianca,
             json.dumps(entidades, ensure_ascii=False), json.dumps(acoes, ensure_ascii=False),
             resposta, latencia_ms, motivo_auto))
        novo_id = c.lastrowid
        conn.commit()
        conn.close()
        return novo_id

    def reportar_quebra(self, interacao_id, comentario=None):
        conn = self._conectar()
        cur = conn.execute("UPDATE interacoes SET quebra_reportada = 1, comentario = ? WHERE id = ?",
                           ((comentario or "").strip()[:300] or None, interacao_id))
        conn.commit()
        conn.close()
        return cur.rowcount == 1

    def listar_quebras(self, limite=200):
        """Interacoes sinalizadas automaticamente ou reportadas por alguem, da mais recente para a mais antiga."""
        linhas = self._listar(
            "SELECT * FROM interacoes WHERE motivo_auto IS NOT NULL OR quebra_reportada = 1 "
            "ORDER BY id DESC LIMIT ?", [limite])
        for l in linhas:
            l["entidades"] = json.loads(l["entidades"] or "[]")
            l["acoes"] = json.loads(l["acoes"] or "[]")
        return linhas

    def resumo_interacoes(self):
        """Numeros para a tela de observabilidade: volume, latencia, taxa de quebra, ranking."""
        conn = self._conectar()
        total, latencia = conn.execute(
            "SELECT COUNT(*), COALESCE(AVG(latencia_ms), 0) FROM interacoes").fetchone()
        quebras = conn.execute(
            "SELECT COUNT(*) FROM interacoes WHERE motivo_auto IS NOT NULL OR quebra_reportada = 1").fetchone()[0]
        ranking = [dict(l) for l in conn.execute(
            "SELECT usuario, COUNT(*) AS quebras FROM interacoes "
            "WHERE motivo_auto IS NOT NULL OR quebra_reportada = 1 "
            "GROUP BY usuario ORDER BY quebras DESC, usuario LIMIT 10")]
        conn.close()
        return {"total": total, "latencia_media_ms": int(latencia or 0), "quebras": quebras,
                "taxa_quebra": (quebras / float(total)) if total else 0.0, "ranking": ranking}

    def limpar_tudo(self):
        """Apaga atividades, agenda e interacoes. Usado so pelo comando explicito de limpeza."""
        conn = self._conectar()
        for tabela in ("atividades", "agenda", "interacoes"):
            conn.execute("DELETE FROM " + tabela)
        conn.commit()
        conn.close()
