# 🚢 Capítulo 14: Deploy em produção

> **Versão 2 do projeto** · documento revisado em 16 nov. 2026 e conferido contra o código. O que não foi testado está dito no texto.

> ⚠️ **Capítulo conceitual.** O que está descrito aqui **não faz parte da versão 2** do projeto e **não foi executado** nesta revisão, salvo onde o texto diz “na v2” ou “medido”. Use como mapa de estudo e confira na documentação do Rasa antes de aplicar.

## Objetivos

Saber o que separa um sistema de sala de aula de um sistema em produção, e por que este projeto não deve ser levado a produção como está.

## A resposta curta

Não coloque este projeto em produção. Três motivos, em ordem de peso:

1. O Rasa Open Source está em modo de manutenção.
2. Ele só roda em versões de Python sem correções de segurança.
3. O projeto não tem autenticação, e isso foi uma escolha para a sala de aula.

O capítulo serve para você reconhecer os temas quando encontrar um chatbot de verdade.

## O que a versão 2 tem e o que faltaria

| Tema | Na v2 | O que um ambiente de produção pede |
|---|---|---|
| Acesso | Sem autenticação; Rasa só em 127.0.0.1 | Autenticação na interface e na API do Rasa (o Rasa aceita token ou JWT na API HTTP) |
| Transporte | HTTP local | HTTPS, em geral por um proxy reverso |
| Histórico de conversas | Memória; some ao reiniciar | “Tracker store” persistente (o Rasa documenta SQL, Redis, MongoDB e DynamoDB) |
| Várias instâncias | Uma | “Lock store” compartilhado, como Redis, para não misturar mensagens da mesma conversa |
| Banco | SQLite em arquivo | Banco com cópia de segurança e controle de acesso |
| Segredos | `.env` local | Cofre de segredos; rotação de chaves |
| Processos | `run.py` em segundo plano | Supervisor de processos ou orquestrador, com reinício automático |
| Logs | Arquivos sobrescritos a cada subida | Logs centralizados, com retenção definida |
| Atualizações | — | Dependências com suporte de segurança |

## Contêineres

Não há Dockerfile nem `docker-compose` nesta entrega: o laboratório não tinha como executá-los, e não se entrega o que não se testou. A Rasa publicava imagens oficiais do servidor e do SDK de ações; verifique se as etiquetas da versão que você usa ainda existem antes de contar com elas.

Um desenho comum tem quatro serviços: Rasa, Action Server, interface e banco, com o modelo treinado montado como volume ou embutido na imagem.

## Antes de publicar qualquer chatbot

- [ ] Quem pode acessar? Como se prova?
- [ ] Onde ficam as conversas, por quanto tempo e quem pode ler?
- [ ] O que acontece quando o processo cai?
- [ ] Como se volta à versão anterior do modelo?
- [ ] Há plano de resposta a incidente? No Brasil, incidente relevante com dados pessoais deve ser comunicado à ANPD em 3 dias úteis.
- [ ] Todas as dependências recebem correções de segurança?

## Alternativas ao Rasa aberto

Para projeto novo, avalie o produto licenciado do próprio fabricante (CALM), as plataformas comerciais ou uma arquitetura própria com LLM e fluxos determinísticos. O critério que pouca gente usa: quanto custa sair da plataforma, se ela acabar.

## Exercícios

1. Liste o que mudaria no diagrama do capítulo 3 para atender dez mil usuários.
2. Onde você guardaria a chave do LLM em produção? Por que não no `.env` do repositório?
3. Escreva um parágrafo defendendo, para um gestor, por que não publicar este projeto como está.

## Resumo

Produção é autenticação, persistência, supervisão, atualização e resposta a incidente. O projeto abre mão disso para ser simples de estudar.

---
[← Capítulo anterior](capitulo-13-testes.md) · [Índice do tutorial](../TUTORIAL_COMPLETO.md) · [Próximo capítulo →](capitulo-15-performance.md)
