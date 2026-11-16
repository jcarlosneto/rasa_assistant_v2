# 📁 Estrutura do projeto

> **Versão 2 do projeto** · documento revisado em 16 nov. 2026 e conferido contra o código. O que não foi testado está dito no texto.

## Árvore

Lista gerada a partir da pasta do projeto. Ficam de fora o que é criado em tempo de execução (`rasa-env/`, `logs/`, `.run/`, `database/`) e esta pasta `docs/`.

```text
.env.example
.gitignore
LICENSE
README.md
requirements.txt
run.py
demo/
    correcao_ao_vivo/
        nlu_patch_h2o.yml
rasa/
    config.yml
    credentials.yml
    domain.yml
    endpoints.yml
    actions/
        __init__.py
        actions.py
        catalogo.py
        database.py
        weather_api.py
    data/
        nlu.yml
        rules.yml
        stories.yml
    models/
        .gitkeep
    tests/
        nlu_inedito.yml
        test_stories.yml
scripts/
    start_actions.sh
    start_rasa.sh
    start_web.sh
    train.sh
tests/
    checar_ineditas.py
    conftest.py
    test_catalogo.py
    test_database.py
    test_llm.py
    test_web.py
    e2e/
        rodar_roteiro.py
        roteiro_demo.json
web_interface/
    app.py
    llm.py
    replay/
        roteiro_gravado.json
    static/
        css/
            app.css
        js/
            app.js
    templates/
        base.html
        chat.html
        dashboard.html
        duelo.html
        mural.html
        saude.html
```

## O que mora em cada lugar

### Raiz

| Arquivo | Papel |
|---|---|
| `run.py` | Lançador único: instala, treina, sobe, testa. Usa só a biblioteca padrão |
| `requirements.txt` | Dependências do ambiente `rasa-env` |
| `.env.example` | Modelo do arquivo de configuração local (`.env`) |
| `README.md` | Visão geral e roteiro da demonstração |

### `rasa/` — o chatbot

| Arquivo | Papel |
|---|---|
| `config.yml` | Pipeline de NLU e políticas de diálogo |
| `domain.yml` | Tudo o que o bot conhece: intents, entidades, slots, respostas, ações, formulário |
| `data/nlu.yml` | Exemplos de frases por intent, expressões regulares e sinônimos |
| `data/rules.yml` | 21 regras |
| `data/stories.yml` | 12 histórias |
| `endpoints.yml` | Endereço do Action Server |
| `credentials.yml` | Canais habilitados (a interface usa o canal REST) |
| `actions/actions.py` | As ações customizadas |
| `actions/catalogo.py` | Regras determinísticas: tipos, duração, intensidade, datas |
| `actions/database.py` | Acesso ao SQLite |
| `actions/weather_api.py` | Clima (opcional) |
| `rasa/tests/test_stories.yml` | Conversas de teste |
| `rasa/tests/nlu_inedito.yml` | 40 frases que não estão no treino |
| `models/` | Modelo treinado (criado pelo `train`) |

### `web_interface/` — a interface

| Arquivo | Papel |
|---|---|
| `app.py` | Servidor Flask: páginas e API |
| `llm.py` | Cliente de LLM do Duelo, feito com `urllib` |
| `templates/` | Uma página por tela, sobre `base.html` |
| `static/js/app.js` | Raio-X, mural, duelo, painel e saúde |
| `static/css/app.css` | Estilos; os gráficos são CSS e SVG próprios |
| `replay/roteiro_gravado.json` | Conversa gravada para a tela Replay |

### `tests/`, `demo/` e `scripts/`

| Caminho | Papel |
|---|---|
| `tests/test_*.py` | Testes unitários |
| `tests/checar_ineditas.py` | Confere que a prova de NLU não repete frases do treino |
| `tests/e2e/roteiro_demo.json` | O roteiro da demonstração, em dados |
| `tests/e2e/rodar_roteiro.py` | Executa o roteiro contra os serviços no ar |
| `demo/correcao_ao_vivo/nlu_patch_h2o.yml` | Os cinco exemplos da correção ao vivo |
| `scripts/start_*.sh`, `scripts/train.sh` | Atalhos que chamam o `run.py` |
| `scripts/legado-v1/` | Scripts da versão 1, não revisados |

### Criado em tempo de execução

| Caminho | Conteúdo |
|---|---|
| `rasa-env/` | Ambiente Python 3.10 |
| `.env` | Sua configuração local; não vai para o Git |
| `database/atividades.db` | Banco SQLite |
| `logs/` | Logs dos serviços e resultados dos testes |
| `.run/` | Identificadores dos processos em execução |

## Fluxo de dados

1. O navegador envia a mensagem a `POST /api/chat`.
2. `app.py` repassa ao Rasa pelo canal REST (`/webhooks/rest/webhook`).
3. O Rasa classifica, decide e chama o Action Server.
4. A ação normaliza com `catalogo.py` e grava com `database.py`.
5. `app.py` lê o tracker da conversa, monta o Raio-X, registra a interação e responde ao navegador.

## Onde mexer para estender

Novo tipo de atividade: `catalogo.py` e exemplos no `nlu.yml`. Nova intenção: `nlu.yml`, `domain.yml` e uma regra. Nova página: um arquivo em `templates/` e uma rota em `app.py`. Passo a passo em [07-customizacao.md](07-customizacao.md).
