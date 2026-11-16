# 🗺️ Apêndice E: Diagramas

> **Versão 2 do projeto** · documento revisado em 16 nov. 2026 e conferido contra o código. O que não foi testado está dito no texto.

Os cinco diagramas do projeto, desenhados em Mermaid. Os arquivos-fonte estão em [../assets/diagramas/](../assets/diagramas/README.md). Em visualizadores sem suporte a Mermaid, aparece o texto do diagrama.

## Arquitetura geral

```mermaid
flowchart LR
    U["Navegador"] -->|"HTTP"| W["Interface Flask<br/>porta 5001"]
    W -->|"REST /webhooks/rest/webhook"| R["Rasa Server<br/>porta 5005 (127.0.0.1)"]
    W -->|"GET /conversations/id/tracker"| R
    R -->|"HTTP /webhook"| A["Action Server<br/>porta 5055"]
    A -->|"SQL"| B[("SQLite<br/>atividades, agenda, interacoes")]
    W -->|"SQL"| B
    A -.->|"opcional"| C["API de clima"]
    W -.->|"opcional"| L["LLM do Duelo"]
    W -->|"arquivo"| G["Replay gravado (JSON)"]
```

## Pipeline de NLU

```mermaid
flowchart TD
    T["Texto: malhei 1 hora"] --> K["WhitespaceTokenizer"]
    K --> F1["RegexFeaturizer"]
    F1 --> F2["LexicalSyntacticFeaturizer"]
    F2 --> F3["CountVectorsFeaturizer (palavras)"]
    F3 --> F4["CountVectorsFeaturizer (pedaços de palavra)"]
    F4 --> D["DIETClassifier<br/>intenção + entidades"]
    D --> S["EntitySynonymMapper"]
    S --> RS["ResponseSelector"]
    RS --> FB{"confiança < 0,5?"}
    FB -->|"sim"| NF["nlu_fallback"]
    FB -->|"não"| OK["intenção e entidades seguem para o Core"]
```

## Fluxo de decisão da conversa

```mermaid
flowchart TD
    M["Mensagem do usuário"] --> N["NLU: intenção e entidades"]
    N --> Q{"Formulário ativo?"}
    Q -->|"sim"| V{"O slot aceita a entrada?"}
    V -->|"sim"| P["Valida e pede o próximo campo"]
    V -->|"não: intenção stop"| X["Regra de cancelamento<br/>desativa o formulário e limpa os slots"]
    Q -->|"não"| R{"Alguma regra se aplica?"}
    R -->|"sim"| A["Ação da regra"]
    R -->|"não"| T["Memoization ou TED escolhem"]
    P --> F{"Faltam campos?"}
    F -->|"sim"| P
    F -->|"não"| S["Grava a atividade"]
    A --> O["Resposta ao usuário"]
    T --> O
    S --> O
    X --> O
```

O ramo da esquerda é o que explica o cancelamento: o formulário só larga a conversa quando o slot recusa a entrada.

## Modelo de dados

```mermaid
erDiagram
    ATIVIDADES {
        int id PK
        string usuario
        string tipo
        float duracao
        string intensidade
        string data
        string hora
        datetime timestamp
    }
    AGENDA {
        int id PK
        string usuario
        string tipo
        string data
        string hora
        string criado_em
        string concluida_em
    }
    INTERACOES {
        int id PK
        string momento
        string usuario
        string texto
        string intent
        float confianca
        string entidades
        string acoes
        string resposta
        int latencia_ms
        string motivo_auto
        int quebra_reportada
        string comentario
    }
```

## Estrutura de pastas

```mermaid
flowchart TD
    P["rasa_assistant_v2/"] --> RUN["run.py"]
    P --> RASA["rasa/"]
    P --> WEB["web_interface/"]
    P --> TST["tests/"]
    P --> DEMO["demo/"]
    P --> DOCS["docs/"]
    RASA --> CFG["config.yml · domain.yml"]
    RASA --> DATA["data/ (nlu, rules, stories)"]
    RASA --> ACT["actions/ (actions, catalogo, database, weather_api)"]
    RASA --> RT["tests/ (test_stories, nlu_inedito)"]
    WEB --> APP["app.py · llm.py"]
    WEB --> TPL["templates/"]
    WEB --> STA["static/ (js, css)"]
    WEB --> RPL["replay/"]
    TST --> UNI["test_*.py"]
    TST --> E2E["e2e/ (roteiro)"]
```

## Telas

As capturas reais do sistema estão em [../assets/screenshots/](../assets/screenshots/INSTRUCOES-SCREENSHOTS.md).
