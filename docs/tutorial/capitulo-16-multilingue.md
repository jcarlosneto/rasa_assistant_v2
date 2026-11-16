# 🌍 Capítulo 16: Multilíngue e internacionalização

> **Versão 2 do projeto** · documento revisado em 16 nov. 2026 e conferido contra o código. O que não foi testado está dito no texto.

> ⚠️ **Capítulo conceitual.** O que está descrito aqui **não faz parte da versão 2** do projeto e **não foi executado** nesta revisão, salvo onde o texto diz “na v2” ou “medido”. Use como mapa de estudo e confira na documentação do Rasa antes de aplicar.

## Objetivos

Entender o que amarra um assistente Rasa a um idioma e os caminhos para atender mais de um.

## Como está a v2

O projeto é só em português: `language: pt` no `config.yml`, exemplos e respostas em português. O pipeline não usa modelo de linguagem pré-treinado; aprende do zero com os exemplos, contando palavras e pedaços de palavra.

Dois cuidados com o português já estão no código:

- comparação sem acento nas regras do catálogo, para que `agua` e `água` deem no mesmo tipo;
- o segundo `CountVectorsFeaturizer`, de pedaços de palavra, que dá tolerância a variações como `natacao` e `natação`.

## O que depende do idioma

| Peça | Depende? | Observação |
|---|---|---|
| `WhitespaceTokenizer` | Pouco | Funciona em línguas que separam palavras por espaço |
| Featurizadores de contagem | Não | Aprendem com os seus dados |
| Exemplos do `nlu.yml` | Totalmente | Um conjunto por idioma |
| Respostas do domínio | Totalmente | Um texto por idioma |
| Regras do catálogo (tipos, “hora”, “amanhã”) | Totalmente | São listas de palavras em português |
| Regras, histórias, políticas | Não | Trabalham com nomes de intenção |

## Caminhos para vários idiomas

1. **Um assistente por idioma.** Mesmos nomes de intenção, dados e respostas próprios, um modelo treinado para cada língua. É o caminho mais simples de entender e de testar.
2. **Detecção de idioma na entrada**, encaminhando a mensagem ao assistente certo.
3. **Modelo multilíngue pré-treinado** como featurizador, para aproveitar exemplos entre línguas. Exige mais memória e tempo, e a qualidade precisa ser medida idioma a idioma.
4. **LLM para o entendimento**, que costuma lidar com vários idiomas sem treino específico, ao custo discutido no capítulo 11.

Nenhum deles foi implementado ou testado neste projeto.

## Respostas

Para um bot bilíngue, os textos fixos precisam existir nas duas línguas. Opções: domínios separados por idioma, respostas condicionadas a um slot de idioma, ou gerar as respostas fora do Rasa. As mensagens montadas nas ações (como `✅ Registrei: …`) também precisam de tradução; hoje estão escritas diretamente no código.

## Além da tradução

- Datas e horas: `amanhã às 7h` tem outra forma em cada língua, e o formato 12/24 horas varia.
- Unidades e números: vírgula ou ponto decimal.
- Nomes de atividades e costumes locais.
- Variação regional dentro da mesma língua. Uma prova de NLU escrita por uma pessoa só reflete o jeito dela de falar.

## Exercícios

1. Liste os arquivos que você teria de duplicar para uma versão em espanhol.
2. Teste cinco frases sem acento e cinco com erros de digitação. Quantas o bot entende?
3. A frase `fiz running` funciona? Procure a explicação no catálogo.

## Resumo

O que amarra o bot ao português são os dados, as respostas e as regras do catálogo. Trocar de idioma é refazer esses três, e medir de novo.

---
[← Capítulo anterior](capitulo-15-performance.md) · [Índice do tutorial](../TUTORIAL_COMPLETO.md) · [Próximo capítulo →](capitulo-17-canais.md)
