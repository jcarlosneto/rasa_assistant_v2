# 🌐 Referência de APIs

> **Versão 2 do projeto** · documento revisado em 16 nov. 2026 e conferido contra o código. O que não foi testado está dito no texto.

## Interface web (Flask, porta 5001)

| Rota | Método | O que faz |
|---|---|---|
| `/` | GET | Página do chat com o painel Raio-X |
| `/replay` | GET | Mesma página, reproduzindo a conversa gravada (não precisa do Rasa) |
| `/mural` | GET | Mural “Quebre o bot” |
| `/duelo` | GET | Duelo 1.0 × 2.0 (classificador × LLM) |
| `/dashboard` | GET | Painel de dados |
| `/saude` | GET | Situação dos serviços |
| `/api/chat` | POST | Envia uma mensagem ao Rasa e devolve respostas e Raio-X. Corpo: `{"mensagem", "usuario"}`. Sem Rasa: HTTP 503 |
| `/api/quebra` | POST | Marca uma interação como falha. Corpo: `{"id", "comentario"}` |
| `/api/mural` | GET | Resumo e lista de falhas |
| `/api/mural/nlu.yml` | GET | Rascunho de exemplos de treino a partir das falhas (texto; exige revisão humana) |
| `/api/duelo` | POST | Envia a mesma frase ao Rasa e ao LLM. Corpo: `{"mensagem"}` |
| `/api/duelo/gravados` | GET, POST | GET lista duelos salvos; POST salva um duelo em que os dois lados responderam |
| `/api/replay` | GET | Conversa gravada (JSON). Sem gravação: HTTP 404 |
| `/api/dashboard` | GET | Dados do painel. `?usuario=apelido` filtra; sem parâmetro, a turma toda |
| `/api/export.csv` | GET | Atividades em CSV (`id, usuario, tipo, duracao_min, intensidade, data, hora`) |
| `/api/atividades/hoje` | GET | Lista de atividades de hoje |
| `/api/atividades/semana` | GET | Lista dos últimos 7 dias |
| `/api/estatisticas/hoje` | GET | Totais de hoje |
| `/api/estatisticas/semana` | GET | Totais dos últimos 7 dias |
| `/api/health` | GET | Mesmo que `/api/saude` (nome antigo, mantido por compatibilidade com a versão 1) |
| `/api/saude` | GET | Situação de Flask, Rasa, Action Server, LLM e replay, mais o resumo das interações |

### `POST /api/chat`

Pedido:

```json
{"mensagem": "corri 30 minutos intenso", "usuario": "ana"}
```

Resposta (campos): `id`, `usuario`, `mensagem`, `respostas` (lista de textos), `raiox`, `motivo_auto`, `momento`.

O campo `raiox` traz `intent` (`nome`, `confianca`), `entidades` (`entidade`, `valor`, `confianca`) e `acoes`, entre outros, montados a partir do tracker do Rasa. O `usuario` é um apelido, higienizado no servidor, e serve de identificador da conversa.

Erros: mensagem vazia devolve 400; Rasa fora do ar devolve 503 com a orientação de usar o Replay.

### `GET /api/saude`

```json
{
  "status": "ok",
  "flask": "running",
  "rasa": {"no_ar": true, "url": "http://localhost:5005", "modelo": "…"},
  "actions": {"no_ar": true, "url": "http://localhost:5055"},
  "llm": {"configurado": false, "provedor": "", "modelo": "", "externo": false},
  "replay_disponivel": true,
  "interacoes": {"total": 0, "quebras": 0, "taxa_quebra": 0.0, "latencia_media_ms": 0, "ranking": []}
}
```

Os nomes dos campos são os do código; os valores acima são ilustrativos.

### `GET /api/dashboard`

Campos: `usuario`, `hoje` e `semana` (cada um com `total`, `tempo_total`, `media_dia`, `por_tipo`, `por_intensidade`, `por_dia`), `serie` (sete dias), `sequencia`, `agenda`, `recentes`.

### `POST /api/duelo`

Pedido: `{"mensagem": "tomei um café"}`. A resposta tem um bloco `rasa` e um bloco `llm`; cada um informa `ok` e, quando falha, `erro`. O bloco `llm` informa também `configurado`, `provedor`, `modelo`, `externo` e `versao_prompt`.

## Rasa Server (porta 5005, só em 127.0.0.1)

Rotas do próprio Rasa usadas pelo projeto:

| Rota | Método | Uso |
|---|---|---|
| `/webhooks/rest/webhook` | POST | Enviar mensagem: `{"sender": "ana", "message": "oi"}` |
| `/conversations/<sender>/tracker` | GET | Histórico estruturado; `?include_events=ALL` traz todos os eventos |
| `/model/parse` | POST | Só o NLU: `{"text": "bebi h2o"}` |
| `/status` | GET | Modelo carregado |

A API está habilitada sem token. Por isso o servidor escuta apenas na própria máquina.

Exemplo:

```bash
curl -s -X POST http://localhost:5005/model/parse -H "Content-Type: application/json" -d '{"text": "bebi h2o"}'
```

## Action Server (porta 5055)

| Rota | Método | Uso |
|---|---|---|
| `/health` | GET | Verificação de vida |
| `/webhook` | POST | Chamado pelo Rasa para executar uma ação |

Escuta em todas as interfaces de rede e não tem autenticação. Use em rede confiável.

## Banco de dados (SQLite)

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

A coluna `usuario` da tabela `atividades` é acrescentada por migração (`ALTER TABLE … ADD COLUMN usuario TEXT NOT NULL DEFAULT 'user'`), para que bancos da versão 1 continuem funcionando.

## Autenticação e limites

Não há autenticação nem limite de requisições. É um sistema de sala de aula. O capítulo 19 do tutorial discute o que seria preciso para ir além.
