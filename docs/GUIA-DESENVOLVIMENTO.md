# 🚀 Guia de desenvolvimento

> **Versão 2 do projeto** · documento revisado em 16 nov. 2026 e conferido contra o código. O que não foi testado está dito no texto.

Para quem vai alterar o projeto.

## Situação atual

| Parte | Situação |
|---|---|
| Chatbot (registro, formulário, agenda, progresso) | Funcionando; roteiro de 22 conferências passa em Linux |
| Interface (Raio-X, mural, duelo, painel, replay, saúde) | Funcionando em Linux |
| Testes | 67 casos unitários, 6 conversas, prova de NLU com 40 frases |
| macOS e Windows | Não testados |
| Duelo com provedor real | Não testado |
| Acessibilidade, uso simultâneo, autenticação | Não tratados |

## Ciclo de trabalho

1. Reproduza o problema no chat e leia o Raio-X.
2. Escreva primeiro o teste que falha: um caso em `tests/`, um passo em `tests/e2e/roteiro_demo.json` ou uma frase em `rasa/tests/nlu_inedito.yml`.
3. Altere o código ou os dados.
4. `python run.py stop && python run.py train && python run.py start`, se mexeu em dados; só `stop` e `start`, se mexeu em ações.
5. `python run.py test` e `python run.py roteiro`.
6. Abra os detalhes: `logs/resultados_core/failed_test_stories.yml` e `logs/resultados_nlu/intent_errors.json`.

## Regras da casa

- **Aprendizado de máquina para entender, regra para normalizar.** Valor que vai para o banco passa por `catalogo.py`.
- **Não treine olhando a prova.** Frase de `nlu_inedito.yml` não entra no `nlu.yml`. O script `tests/checar_ineditas.py` confere.
- **Teste verde não é prova.** Teste de conversa não avalia o NLU; resumo sem detalhe esconde resultado.
- **Sem dado fictício no painel.** Banco vazio aparece vazio.
- **Sem dependência da internet.** Nada de CDN; JavaScript e CSS próprios.
- **Texto do usuário é texto.** `textContent`, nunca `innerHTML`.
- **Chave só no `.env`.**
- **Diga o que não testou.**

## Teste dos testes

Para saber se a suíte pega defeitos, plante um de cada vez numa cópia do projeto e rode `pytest`. Na revisão, sete defeitos plantados foram detectados, entre eles “1 hora volta a valer 1 minuto” e “filtro por usuário ignorado”. Sete é uma amostra, não garantia de cobertura.

## Ferramentas

- Python 3.10 no `rasa-env` (via `uv`); qualquer Python 3.8+ para o `run.py`.
- `pytest` para os testes unitários: `rasa-env/bin/python -m pytest -q tests` (no Windows, `rasa-env\Scripts\python`).
- Um navegador. Não há etapa de compilação da interface.

## Onde está cada coisa

Veja [05-estrutura-projeto.md](05-estrutura-projeto.md). Para receitas de alteração, [07-customizacao.md](07-customizacao.md).

## Tarefas em aberto

1. Executar instalação e roteiro em macOS e em Windows e registrar o resultado.
2. Fazer um duelo com provedor real e gravá-lo.
3. Prova de NLU com frases escritas pelos alunos (o mural já as coleta).
4. Exemplos de fora de escopo para `tomei um café` e de despedida para `valeu, fui`, medindo o efeito na prova.
5. Notificação da agenda.
6. Auditoria de acessibilidade.
7. Teste automático para a exportação CSV.

## Git

O `.gitignore` deixa de fora `.env`, `rasa-env/`, `logs/`, `.run/`, o banco e os modelos. Antes de publicar, confira que nenhuma chave entrou em arquivo versionado.
