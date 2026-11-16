# 📖 Capítulo 1: Introdução ao Rasa Open Source

> **Versão 2 do projeto** · documento revisado em 16 nov. 2026 e conferido contra o código. O que não foi testado está dito no texto.

## Objetivos

Ao final, você saberá dizer o que é o Rasa, em que situação ele está hoje e o que vai construir neste tutorial.

## O que é

O Rasa Open Source é um framework para construir assistentes conversacionais com dados próprios, na sua máquina. Ele popularizou, em código aberto, a combinação de compreensão de linguagem (NLU) e gerenciamento de diálogo treináveis. Os mesmos conceitos — intenção, entidade, estado da conversa, política — aparecem, com outros nomes, nas plataformas da IBM, do Google e da Microsoft.

## Em que pé está

| Fato | Data |
|---|---|
| Última versão aberta: 3.6.21 | jan. 2025 |
| O repositório oficial declara modo de manutenção | conferido em nov. 2026 |
| Python aceito: 3.8, 3.9 ou 3.10, todos fora de suporte | 3.10 desde out. 2026 |

O fabricante concentrou o desenvolvimento no **CALM** (“Conversational AI with Language Models”), em que um LLM interpreta a conversa e fluxos determinísticos executam as tarefas. O CALM faz parte do Rasa Pro, que é licenciado; há uma edição gratuita para desenvolvedores, com limite de conversas.

## Então por que estudar o Rasa aberto?

Porque ele é transparente. Dá para abrir cada arquivo, ver cada decisão e errar de propósito. Quem entende intenção, entidade, slot e política aqui lê qualquer plataforma depois. O que **não** se recomenda é começar um projeto novo de produção sobre uma base em manutenção.

Uma lição que vale além do Rasa: plataformas têm prazo de validade. Os fundamentos duram mais do que os produtos.

## O que você vai construir

O Assistente de Atividades: registra e agenda atividades de bem-estar e mostra, na tela Raio-X, o que o Rasa fez com cada mensagem.

```text
Você: malhei 1 hora
Bot:  ✅ Registrei: musculação · 60 min.
```

Atrás dessa resposta há seis etapas. Os capítulos seguintes abrem cada uma.

## Mapa do tutorial

| Parte | Capítulos | Natureza |
|---|---|---|
| Fundamentos | 1 a 6 | Conferidos contra o código |
| Construção | 7 a 13 | Conferidos contra o código |
| Além da sala de aula | 14 a 17 | Conceituais: a versão 2 não implementa |
| Operação e fecho | 18 a 20 | Parte implementada, parte conceitual |

## Exercícios

1. Explique a um colega a diferença entre “código aberto” e “mantido”.
2. Liste dois riscos de usar em produção um software que só roda em versões de Python sem suporte.
3. Antes de ler o capítulo 2: o que você acha que acontece dentro do bot entre `malhei 1 hora` e a resposta?

## Resumo

O Rasa aberto é uma ótima sala de aula e uma má fundação para produto novo. Este tutorial usa a primeira qualidade.

---
[Índice do tutorial](../TUTORIAL_COMPLETO.md) · [Próximo capítulo →](capitulo-02-conceitos.md)
