# 📊 Diagramas do projeto

> **Versão 2 do projeto** · documento revisado em 16 nov. 2026 e conferido contra o código. O que não foi testado está dito no texto.

Cinco diagramas em Mermaid, reescritos para a versão 2.

| Arquivo | O que mostra |
|---|---|
| `arquitetura-geral.mmd` | Os três serviços, o banco e as integrações opcionais |
| `pipeline-nlu.mmd` | Os componentes do NLU, na ordem de `rasa/config.yml` |
| `fluxo-conversacao.mmd` | Como o Core decide, com o caso do formulário e do cancelamento |
| `modelo-dados.mmd` | As três tabelas do SQLite |
| `estrutura-diretorios.mmd` | As pastas principais |

As três tabelas não têm chave estrangeira entre si: ligam-se pelo apelido do usuário e, na baixa da agenda, por usuário, tipo e data.

Como visualizar: [USAR-MERMAID-DIRETO.md](USAR-MERMAID-DIRETO.md).

O que mudou em relação à versão 1: saiu o Socket.IO; entraram as tabelas `agenda` e `interacoes`, a coluna `usuario`, o Replay e o LLM opcional.
