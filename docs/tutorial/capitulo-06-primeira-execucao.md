# 🚀 Capítulo 6: Primeira execução

> **Versão 2 do projeto** · documento revisado em 16 nov. 2026 e conferido contra o código. O que não foi testado está dito no texto.

## Objetivos

Subir o sistema, percorrer o roteiro e ler o Raio-X.

## Subir

```bash
python run.py start --abrir
python run.py status
```

A subida leva algum tempo (cerca de 50 segundos no laboratório), quase todo gasto pelo Rasa ao carregar o modelo.

## Escolha um apelido

A interface pede um apelido. Ele separa os seus registros dos de outras pessoas e identifica a sua conversa no Rasa. Use um apelido, não o seu nome completo: o que você digita fica gravado no banco.

## O roteiro, ato por ato

| Ato | Digite | Pergunta para você |
|---|---|---|
| 1 | `bom dia` | A saudação seguiu a palavra ou o relógio? |
| 2 | `bebi água` · `corri 30 minutos intenso` | Quantas entidades em cada frase? |
| 3 | `meditei` · `malhei 1 hora` | O que o NLU extraiu e o que foi gravado? |
| 4 | `agendar yoga amanhã às 7h` · `minha agenda` | Quem entendeu “amanhã às 7h”? |
| 5 | `quero registrar uma atividade` · `natação` · `um tempão` · `45` · `forte` | O que aconteceu com `um tempão`? |
| 6 | `quero registrar exercício` · `cancelar` | Algo foi gravado? |
| 7 | `como estou hoje?` · `tomei um café` · `bebi h2o` | Qual a confiança nas duas falhas? |
| 8 | `qual a capital da França?` · `tchau` | Que intenção apareceu? |

## Modo passo a passo

Ative o modo passo a passo e avance com a barra de espaço. Cada etapa do Raio-X acende sozinha. É o melhor jeito de explicar o processo a outra pessoa.

## Reportar uma falha

Quando o bot errar, use o botão “quebrou”. A interação vai para o mural (`/mural`), com o seu apelido. Algumas falhas vão sozinhas: fallback, atividade não identificada e confiança baixa.

## Conferir automaticamente

```bash
python run.py roteiro
```

O comando conversa com o bot seguindo o mesmo roteiro e compara cada resposta com o esperado. No laboratório: 22 conferências, nenhuma divergência.

## Encerrar

```bash
python run.py stop
```

## Exercícios

1. Encontre uma frase de registro que o bot não entenda e reporte.
2. Abra `/dashboard` com o seu apelido e depois sem filtro. O que muda?
3. Rode `python run.py roteiro` duas vezes. O resultado mudou? Por quê?

## Resumo

Você subiu três serviços, percorreu oito atos e viu duas falhas com confiança alta. Elas são o assunto do próximo capítulo.

---
[← Capítulo anterior](capitulo-05-estrutura.md) · [Índice do tutorial](../TUTORIAL_COMPLETO.md) · [Próximo capítulo →](capitulo-07-nlu.md)
