# 📱 Capítulo 17: Canais de comunicação

> **Versão 2 do projeto** · documento revisado em 16 nov. 2026 e conferido contra o código. O que não foi testado está dito no texto.

> ⚠️ **Capítulo conceitual.** O que está descrito aqui **não faz parte da versão 2** do projeto e **não foi executado** nesta revisão, salvo onde o texto diz “na v2” ou “medido”. Use como mapa de estudo e confira na documentação do Rasa antes de aplicar.

## Objetivos

Entender o que é um canal no Rasa, qual o projeto usa e o que muda ao ligar o bot a um aplicativo de mensagens.

## Como está a v2

A interface web fala com o Rasa pelo canal **REST**: envia `{"sender", "message"}` a `/webhooks/rest/webhook` e recebe a lista de respostas. É o canal mais simples: uma pergunta, uma resposta.

O arquivo `rasa/credentials.yml` habilita `rest`. Há também um bloco `socketio`, herdado da versão 1, que a interface atual não usa.

## O que é um canal

Um conector que traduz o formato de uma plataforma para o formato interno do Rasa, e de volta. O Rasa 3.6 documenta conectores para Slack, Telegram, Facebook Messenger, Twilio, Microsoft Bot Framework, Google Chat, Cisco Webex Teams, Mattermost e Rocket.Chat, além de REST, callback, Socket.IO e conectores escritos por você.

WhatsApp costuma entrar por um intermediário (como o Twilio) ou por um conector próprio.

**Nada disso foi configurado ou testado neste projeto.** E os conectores acompanham o Rasa em manutenção: as plataformas mudam as suas APIs, e um conector parado pode deixar de funcionar.

## O que muda fora da web local

| Tema | Por quê |
|---|---|
| Endereço público com HTTPS | A plataforma precisa alcançar o seu servidor |
| Verificação de origem | Só a plataforma pode chamar o seu webhook |
| Identidade do usuário | O `sender` passa a ser um identificador real, como um número de telefone: dado pessoal |
| Formato das respostas | Botões, imagens e limites de tamanho variam por canal |
| Regras da plataforma | Janela de atendimento, modelos de mensagem, políticas de uso |
| Raio-X | Não existe no aplicativo de mensagens; seria uma ferramenta à parte, para a equipe |

## Respostas por canal

O domínio do Rasa permite variar uma resposta conforme o canal. Um texto com emojis e várias linhas, bom na web, pode precisar ser mais curto em outro lugar. As mensagens montadas nas ações do projeto são únicas para todos os canais.

## Voz

Em um canal de voz, o texto vem de um reconhecedor de fala e volta por um sintetizador. Erros de reconhecimento chegam ao NLU como frases estranhas. E voz é dado pessoal; biometria de voz é dado pessoal sensível, segundo a LGPD.

## Um exercício de projeto

Antes de ligar um bot a um canal real, responda: quem é o controlador dos dados? Onde ficam as conversas? Por quanto tempo? Como a pessoa pede a exclusão? Essas perguntas vêm antes do conector.

## Exercícios

1. Envie uma mensagem ao Rasa sem a interface: `curl -s -X POST http://localhost:5005/webhooks/rest/webhook -H "Content-Type: application/json" -d '{"sender": "teste", "message": "bebi água"}'`.
2. Que respostas do bot ficariam ruins numa tela pequena?
3. O que o apelido da interface e um número de telefone têm de diferente, do ponto de vista da LGPD?

## Resumo

A v2 usa o canal REST e nada mais. Outros canais existem no Rasa 3.6, trazem exigências de segurança e de privacidade, e não foram testados aqui.

---
[← Capítulo anterior](capitulo-16-multilingue.md) · [Índice do tutorial](../TUTORIAL_COMPLETO.md) · [Próximo capítulo →](capitulo-18-analytics.md)
