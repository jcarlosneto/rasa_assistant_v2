# 🔧 Apêndice C: Solução rápida de problemas

> **Versão 2 do projeto** · documento revisado em 16 nov. 2026 e conferido contra o código. O que não foi testado está dito no texto.

Guia completo: [../04-debug-troubleshooting.md](../04-debug-troubleshooting.md).

## Em um minuto

```bash
python run.py status
```

Depois abra `/saude` e o log do serviço que não respondeu, em `logs/`.

## Tabela de bolso

| Sintoma | Primeira coisa a tentar |
|---|---|
| `setup` não acha Python compatível | Instalar o `uv` |
| Instalação falha no TensorFlow | Guardar a mensagem; `python run.py replay --abrir` |
| Rasa não sobe | `python run.py train`; ler `logs/rasa.log` |
| “Não consegui falar com o Rasa” | Esperar a subida terminar; `status` |
| Porta ocupada | `python run.py stop`; mudar `FLASK_PORT` |
| Mudança nos dados sem efeito | `stop`, `train`, `start` |
| Mudança nas ações sem efeito | `stop`, `start` |
| Intenção errada | Raio-X, etapa 3; mais exemplos; retreinar |
| Entidade ausente | Exemplos **anotados** |
| Formulário não cancela | `not_intent: stop` nos mapeamentos |
| Duelo: LLM não configurado | Três variáveis `LLM_…` no `.env` |
| Painel vazio | Banco vazio é mostrado vazio |
| Roteiro diverge | Ler o primeiro passo divergente; conferir se a correção ao vivo está aplicada |

## O roteiro falha em `bebi h2o`?

O roteiro normal espera que `bebi h2o` **falhe**. Se você aplicou `corrigir-ao-vivo` e treinou, use `python run.py roteiro --apos-correcao`, ou rode `desfazer-correcao` e treine de novo.

## Avisos que não são erro

`DeprecationWarning` de bibliotecas antigas, o aviso de política experimental (`UnexpecTED`) e os avisos `utterance … is not used in any story or rule` para as perguntas do formulário.

## Na hora da aula

Não depure diante da turma. Abra a tela Replay, diga que é gravação e siga o roteiro. Investigue depois, com o log em mãos.
