# 📚 Tutorial completo — construindo chatbots com Rasa Open Source

> **Versão 2 do projeto** · documento revisado em 16 nov. 2026 e conferido contra o código. O que não foi testado está dito no texto.

## Sobre este tutorial

Vinte capítulos e cinco apêndices que acompanham o Assistente de Atividades, versão 2. Cada capítulo traz objetivos, explicação com trechos copiados do código, algo para experimentar no sistema e exercícios.

## Parte 1 — Fundamentos

| Capítulo | Tema |
|---|---|
| [1](tutorial/capitulo-01-introducao.md) | O que é o Rasa e em que pé está |
| [2](tutorial/capitulo-02-conceitos.md) | Intent, entity, slot, regra, história, política |
| [3](tutorial/capitulo-03-arquitetura.md) | Os três processos e o caminho de uma mensagem |
| [4](tutorial/capitulo-04-instalacao.md) | Ambiente e instalação |
| [5](tutorial/capitulo-05-estrutura.md) | Onde está cada coisa |
| [6](tutorial/capitulo-06-primeira-execucao.md) | Primeira execução e roteiro em oito atos |

## Parte 2 — Construção

| Capítulo | Tema |
|---|---|
| [7](tutorial/capitulo-07-nlu.md) | Dados de treino, pipeline e as lições das falhas |
| [8](tutorial/capitulo-08-core.md) | Regras, histórias e políticas |
| [9](tutorial/capitulo-09-actions.md) | Ações em Python; modelo entende, regra normaliza |
| [10](tutorial/capitulo-10-database.md) | Banco de dados |
| [11](tutorial/capitulo-11-apis.md) | APIs externas e o LLM do Duelo |
| [12](tutorial/capitulo-12-forms.md) | Formulários, validação e cancelamento |
| [13](tutorial/capitulo-13-testes.md) | Testes, e o que cada um prova |

## Parte 3 — Além da sala de aula (capítulos conceituais)

A versão 2 **não implementa** o que estes capítulos descrevem, e nada neles foi executado nesta revisão, salvo onde o texto indica.

| Capítulo | Tema |
|---|---|
| [14](tutorial/capitulo-14-deploy.md) | O que a produção exige, e por que não levar este projeto a ela |
| [15](tutorial/capitulo-15-performance.md) | Desempenho: o que foi medido e as alavancas usuais |
| [16](tutorial/capitulo-16-multilingue.md) | Vários idiomas |
| [17](tutorial/capitulo-17-canais.md) | Canais de comunicação |

## Parte 4 — Operação e fecho

| Capítulo | Tema |
|---|---|
| [18](tutorial/capitulo-18-analytics.md) | Métricas, mural e painel (implementado) |
| [19](tutorial/capitulo-19-seguranca.md) | Segurança e privacidade (implementado + orientação) |
| [20](tutorial/capitulo-20-projeto-final.md) | Projeto final, com rubrica |

## Apêndices

| Apêndice | Tema |
|---|---|
| [A](tutorial/apendice-a-comandos.md) | Comandos |
| [B](tutorial/apendice-b-glossario.md) | Glossário |
| [C](tutorial/apendice-c-troubleshooting.md) | Solução rápida de problemas |
| [D](tutorial/apendice-d-checklists.md) | Listas de conferência |
| [E](tutorial/apendice-e-diagramas.md) | Diagramas |

## Como usar

- **Em sequência**, se você está começando: capítulos 1 a 13, um por sessão, com o sistema no ar.
- **Por consulta**, se já conhece o Rasa: vá ao capítulo do tema e aos apêndices A e C.
- **Sem instalar**: os capítulos 1 a 3 e 7 a 9 podem ser acompanhados com a tela Replay.

## Convenções

- `texto assim` é comando, nome de arquivo ou frase a digitar no chat.
- Blocos de código com o nome do arquivo na primeira linha são **cópias** do código do projeto, extraídas no momento em que a documentação foi gerada.
- “No laboratório” indica medida feita em uma máquina Linux, em novembro de 2026. Na sua máquina os números serão outros.
- “Não testado” quer dizer exatamente isso.

## O que mudou em relação ao tutorial da versão 1

O tutorial anterior tinha cerca de 22 mil linhas e descrevia a versão 1, com Socket.IO, porta 5000, scripts por sistema operacional e capítulos extensos de deploy, canais e multilíngue que o projeto nunca implementou. Esta versão foi reescrita a partir do código atual: é bem mais curta, e cada afirmação sobre o sistema pode ser conferida nos arquivos. O que era promessa sem implementação virou capítulo conceitual, marcado como tal.

## Começar

[Capítulo 1](tutorial/capitulo-01-introducao.md).
