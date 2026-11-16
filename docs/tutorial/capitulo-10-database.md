# 💾 Capítulo 10: Banco de dados

> **Versão 2 do projeto** · documento revisado em 16 nov. 2026 e conferido contra o código. O que não foi testado está dito no texto.

## Objetivos

Conhecer o esquema, a separação por usuário e as decisões de regra de negócio gravadas no código.

## SQLite

Um arquivo, sem servidor: `database/atividades.db`, criado na primeira execução. Para sala de aula, é o bastante. O caminho vem de `DATABASE_PATH`, no `.env`.

## Esquema

### Tabela `atividades`

| Coluna | Definição |
|---|---|
| `id` | INTEGER PRIMARY KEY AUTOINCREMENT |
| `tipo` | TEXT NOT NULL |
| `duracao` | REAL |
| `intensidade` | TEXT |
| `data` | TEXT NOT NULL |
| `hora` | TEXT NOT NULL |
| `timestamp` | DATETIME DEFAULT CURRENT_TIMESTAMP |

### Tabela `agenda`

| Coluna | Definição |
|---|---|
| `id` | INTEGER PRIMARY KEY AUTOINCREMENT |
| `usuario` | TEXT NOT NULL |
| `tipo` | TEXT NOT NULL |
| `data` | TEXT NOT NULL |
| `hora` | TEXT |
| `criado_em` | TEXT NOT NULL |
| `concluida_em` | TEXT |

### Tabela `interacoes`

| Coluna | Definição |
|---|---|
| `id` | INTEGER PRIMARY KEY AUTOINCREMENT |
| `momento` | TEXT NOT NULL |
| `usuario` | TEXT NOT NULL |
| `texto` | TEXT NOT NULL |
| `intent` | TEXT |
| `confianca` | REAL |
| `entidades` | TEXT |
| `acoes` | TEXT |
| `resposta` | TEXT |
| `latencia_ms` | INTEGER |
| `motivo_auto` | TEXT |
| `quebra_reportada` | INTEGER NOT NULL DEFAULT 0 |
| `comentario` | TEXT |

A coluna `usuario` de `atividades` entra por migração, para aceitar bancos da versão 1:

```python
# rasa/actions/database.py
            c.execute("ALTER TABLE atividades ADD COLUMN usuario TEXT NOT NULL DEFAULT 'user'")
```

Registros antigos ficam sob o usuário `user`. Há teste para isso (`test_migra_banco_da_v1_sem_perder_linhas`).

## Gravar

```python
# rasa/actions/database.py
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
```

Note o `?` nas consultas: os valores nunca são colados no texto do SQL. É a defesa básica contra injeção.

## Um usuário não vê o outro

```python
# rasa/actions/database.py
    def _filtro_usuario(usuario, prefixo=" AND "):
        return (prefixo + "usuario = ?", [usuario]) if usuario else ("", [])
```

Com apelido, o filtro entra na consulta. Sem apelido, a consulta devolve a turma toda; é o que o painel usa na visão geral.

## O que é “semana”?

```python
# rasa/actions/database.py
    def _inicio_semana(self, agora=None):
        return ((agora or datetime.now()) - timedelta(days=6)).strftime("%Y-%m-%d")
```

Sete dias de calendário, com hoje incluído. Na versão 1 a conta dava oito dias, sob o rótulo “últimos 7 dias”. Regra de negócio pequena, efeito visível nos totais.

## Agenda e baixa

Ao registrar uma atividade, o sistema procura um agendamento pendente do mesmo usuário, do mesmo tipo e do mesmo dia, e marca como concluído:

```python
# rasa/actions/database.py
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
```

## Interações e mural

Cada mensagem enviada pelo chat gera uma linha em `interacoes`: texto, intenção, confiança, entidades, ações, resposta, latência e, quando houver, o motivo automático de falha. O mural é uma consulta sobre essa tabela.

Essa tabela guarda o que as pessoas digitaram. Trate como dado pessoal: apelidos em vez de nomes e `python run.py limpar-banco --sim` ao final.

## Explorar

```bash
sqlite3 database/atividades.db "SELECT usuario, tipo, duracao, intensidade, data FROM atividades ORDER BY id DESC LIMIT 5;"
```

O comando exige o programa `sqlite3` instalado. A exportação CSV do painel (`/api/export.csv`) dá o mesmo resultado sem ele.

## Exercícios

1. Escreva a consulta que conta atividades por tipo nos últimos 7 dias.
2. O que acontece com a baixa da agenda se o usuário registrar `corrida` e tiver agendado `caminhada`?
3. Por que as conversas do Rasa não estão neste banco?

## Resumo

Três tabelas, tudo filtrado por usuário, consultas com parâmetros e regras de negócio pequenas, escritas e testadas.

---
[← Capítulo anterior](capitulo-09-actions.md) · [Índice do tutorial](../TUTORIAL_COMPLETO.md) · [Próximo capítulo →](capitulo-11-apis.md)
