# 🎨 Modelos de diagrama

> **Versão 2 do projeto** · documento revisado em 16 nov. 2026 e conferido contra o código. O que não foi testado está dito no texto.

Modelos em Mermaid para novos documentos. Copie, troque os nomes e confira o resultado em um visualizador (veja [USAR-MERMAID-DIRETO.md](../diagramas/USAR-MERMAID-DIRETO.md)).

## Fluxo de componentes

```mermaid
flowchart LR
    A[Origem] -->|protocolo| B[Serviço]
    B --> C[(Banco)]
    B -.->|opcional| D[Serviço externo]
```

## Sequência de uma mensagem

```mermaid
sequenceDiagram
    participant U as Usuário
    participant S as Sistema
    U->>S: mensagem
    S-->>U: resposta
```

## Decisão

```mermaid
flowchart TD
    I[Entrada] --> Q{Condição?}
    Q -->|sim| S[Caminho A]
    Q -->|não| N[Caminho B]
```

## Modelo de dados

```mermaid
erDiagram
    TABELA_A ||--o{ TABELA_B : "relação"
    TABELA_A {
        int id
        string nome
    }
```

## Boas práticas

- Um diagrama, uma ideia. Se precisa de legenda longa, divida.
- Nomeie as setas com o que trafega (HTTP, REST, SQL).
- Linha tracejada para o que é opcional.
- Diagrama descreve o código de hoje. Mudou o código, mude o diagrama.
