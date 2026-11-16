# 📁 Capítulo 5: Estrutura do projeto

> **Versão 2 do projeto** · documento revisado em 16 nov. 2026 e conferido contra o código. O que não foi testado está dito no texto.

## Objetivos

Saber onde está cada coisa e qual arquivo abrir para cada tipo de mudança.

## A árvore

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

## Quatro arquivos que explicam o bot

| Arquivo | Pergunta |
|---|---|
| `rasa/data/nlu.yml` | Que frases ele conhece? |
| `rasa/domain.yml` | O que ele sabe dizer, lembrar e fazer? |
| `rasa/data/rules.yml` | Como ele reage? |
| `rasa/actions/actions.py` | O que acontece quando ele age? |

Leia nessa ordem. Em meia hora você terá o desenho inteiro.

## Três arquivos que explicam a interface

| Arquivo | Papel |
|---|---|
| `web_interface/app.py` | Rotas e montagem do Raio-X |
| `web_interface/static/js/app.js` | O que acende na tela |
| `web_interface/llm.py` | O lado do LLM no Duelo |

## Onde mexer

| Quero… | Abro… |
|---|---|
| Ensinar uma frase nova | `rasa/data/nlu.yml` |
| Mudar um texto do bot | `rasa/domain.yml` (respostas) ou `actions.py` |
| Aceitar um tipo novo de atividade | `rasa/actions/catalogo.py` |
| Mudar o que vai para o banco | `rasa/actions/database.py` |
| Criar uma página | `web_interface/templates/` e `app.py` |
| Mudar o roteiro de teste | `tests/e2e/roteiro_demo.json` |

## O que não está na árvore

Pastas criadas em tempo de execução: `rasa-env/`, `logs/`, `.run/`, `database/`, e o arquivo `.env`. Nenhuma vai para o Git.

A pasta `scripts/legado-v1/` guarda os scripts da versão 1, sem revisão. Os atalhos atuais em `scripts/` só chamam o `run.py`.

## Exercícios

1. Encontre onde está escrita a frase “Ok, cancelado”.
2. Em que arquivo você acrescentaria “pilates”? Há mais de um.
3. Abra `tests/e2e/roteiro_demo.json` e conte os atos.

## Resumo

Dados em `rasa/data`, vocabulário em `domain.yml`, código em `actions/`, tela em `web_interface/`. Visão detalhada: [../05-estrutura-projeto.md](../05-estrutura-projeto.md).

---
[← Capítulo anterior](capitulo-04-instalacao.md) · [Índice do tutorial](../TUTORIAL_COMPLETO.md) · [Próximo capítulo →](capitulo-06-primeira-execucao.md)
