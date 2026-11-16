# 📚 Documentação — Assistente de Atividades (Rasa Open Source, versão 2)

> **Versão 2 do projeto** · documento revisado em 16 nov. 2026 e conferido contra o código. O que não foi testado está dito no texto.

Esta pasta explica o projeto da Aula 6: um chatbot que registra e agenda atividades de bem-estar e deixa ver, na tela, o que o Rasa faz com cada mensagem.

## Por onde começar

| Você quer… | Leia |
|---|---|
| Rodar em poucos minutos | [INICIO-RAPIDO.md](INICIO-RAPIDO.md) |
| Entender o que é o projeto | [01-introducao.md](01-introducao.md) |
| Aprender os conceitos do Rasa | [02-conceitos-rasa.md](02-conceitos-rasa.md) |
| Instalar com calma | [02-setup-instalacao.md](02-setup-instalacao.md) |
| Executar e testar | [03-execucao-testes.md](03-execucao-testes.md) |
| Resolver um problema | [04-debug-troubleshooting.md](04-debug-troubleshooting.md) |
| Estudar em sequência, do zero | [TUTORIAL_COMPLETO.md](TUTORIAL_COMPLETO.md) (20 capítulos) |

## Todos os documentos

| Documento | Conteúdo |
|---|---|
| [01-introducao.md](01-introducao.md) | O que é, para quem, o que se aprende |
| [02-conceitos-rasa.md](02-conceitos-rasa.md) | Intent, entity, slot, form, policy, action |
| [02-setup-instalacao.md](02-setup-instalacao.md) | Instalação em Linux, macOS e Windows |
| [03-execucao-testes.md](03-execucao-testes.md) | Subir os serviços, roteiro da demonstração, testes |
| [03-requisitos.md](03-requisitos.md) | Requisitos funcionais e não funcionais, com a situação de cada um |
| [04-debug-troubleshooting.md](04-debug-troubleshooting.md) | Sintomas, causas e soluções |
| [05-estrutura-projeto.md](05-estrutura-projeto.md) | Árvore de arquivos comentada |
| [06-arquitetura-rasa.md](06-arquitetura-rasa.md) | Pipeline de NLU, políticas, ações, fluxo de uma mensagem |
| [07-customizacao.md](07-customizacao.md) | Como acrescentar intent, entidade, atividade, página |
| [08-configuracoes.md](08-configuracoes.md) | `.env`, `config.yml`, `endpoints.yml`, `credentials.yml` |
| [09-api-reference.md](09-api-reference.md) | Rotas da interface, API do Rasa, banco de dados |
| [GUIA-DESENVOLVIMENTO.md](GUIA-DESENVOLVIMENTO.md) | Ciclo de trabalho para quem vai alterar o projeto |
| [assets/](assets/README.md) | Telas reais e diagramas |
| [tutorial/](TUTORIAL_COMPLETO.md) | Tutorial em 20 capítulos e 5 apêndices |

## Três avisos que valem para tudo

1. **O Rasa Open Source está em modo de manutenção.** A última versão aberta é a 3.6.21 (jan. 2025) e só instala em Python 3.8, 3.9 ou 3.10, versões que já não recebem correções de segurança. O projeto serve para aprender, não para produção.
2. **Testado só em Linux.** Instalação, treino, testes e roteiro foram executados em Linux x86_64 com Python 3.10. macOS e Windows não foram testados.
3. **É um sistema de sala de aula.** Não há autenticação. Não exponha os serviços à internet.

## Sobre esta revisão

Estes documentos substituem os da versão 1. Foram reescritos a partir do código da versão 2: tabelas de intents, rotas, banco e variáveis são geradas dos próprios arquivos do projeto, e os trechos de código são cópias. Os capítulos 14 a 17 do tutorial tratam de assuntos que a versão 2 não implementa e estão marcados como conceituais.
