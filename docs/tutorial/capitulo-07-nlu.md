# 🧠 Capítulo 7: Construindo o NLU

> **Versão 2 do projeto** · documento revisado em 16 nov. 2026 e conferido contra o código. O que não foi testado está dito no texto.

## Objetivos

Escrever dados de treino, entender o pipeline e explicar por que o classificador erra com confiança alta.

## Os dados

`rasa/data/nlu.yml` tem 397 exemplos em 19 intents (um deles, `nlu_fallback`, sem exemplos). Um bloco real:

```yaml
# rasa/data/nlu.yml
  - intent: agendar_atividade
    examples: |
      - agendar [corrida](tipo_atividade) amanhã às 7h
      - agendar [yoga](tipo_atividade) para sexta às 18h
      - marcar [natação](tipo_atividade) para amanhã
      - marcar [caminhada](tipo_atividade) hoje às 19h
      - quero agendar [musculação](tipo_atividade) para segunda às 6h30
      - agenda [meditação](tipo_atividade) para hoje às 21h
```

Os colchetes marcam a entidade e os parênteses dão o nome: `[yoga](tipo_atividade)`. Sem essa anotação, o modelo não aprende a extrair.

## Expressões regulares e sinônimos

```yaml
# rasa/data/nlu.yml
  - regex: duracao
    examples: |
      - \d+\s*(min|minutos?|horas?)
      - \d+
      - (vinte|trinta|quarenta|cinquenta|sessenta)
```

A expressão regular não decide nada sozinha: vira uma característica a mais para o modelo.

```yaml
# rasa/data/nlu.yml
  - synonym: água
    examples: |
      - agua
      - h2o
      - hidratação
      - hidratar
```

| Valor canônico | Variações declaradas |
|---|---|
| corrida | 5 |
| água | 4 |
| meditação | 3 |
| caminhada | 3 |
| natação | 4 |
| yoga | 2 |
| musculação | 5 |

O sinônimo atua **depois** da extração. Ele troca o valor de uma entidade que o modelo já achou.

## O pipeline

- `WhitespaceTokenizer`
- `RegexFeaturizer`
- `LexicalSyntacticFeaturizer`
- `CountVectorsFeaturizer`
- `CountVectorsFeaturizer` — analyzer: char_wb, min_ngram: 1, max_ngram: 4
- `DIETClassifier` — epochs: 60, constrain_similarities: True, random_seed: 42
- `EntitySynonymMapper`
- `ResponseSelector` — epochs: 20, constrain_similarities: True, random_seed: 42
- `FallbackClassifier` — threshold: 0.5, ambiguity_threshold: 0.1

Os dois `CountVectorsFeaturizer` contam palavras e pedaços de palavra (de 1 a 4 letras). O segundo é o que dá ao modelo alguma tolerância a erros de digitação. São vetores esparsos de contagem; o projeto não usa “embeddings” pré-treinados.

## Lição 1: o mundo fechado

`tomei um café` é classificada como registro de atividade com confiança próxima de 100%, e nenhuma entidade é encontrada.

O classificador reparte toda a confiança entre as intenções que conhece. “Tomei” aparece em exemplos como “tomei água”. A resposta mais parecida ganha, com folga. O limiar de fallback não ajuda, porque a confiança é alta.

O que protege o usuário, nesse caso, é a ação: sem atividade reconhecida, o bot diz que não identificou e não grava nada.

## Lição 2: sinônimo não ensina palavra nova

O arquivo já tinha `h2o → água`, e `bebi h2o` falhava. O modelo nunca tinha visto `h2o` anotado como entidade; sem extração, o sinônimo não é acionado. A correção são cinco exemplos anotados:

```bash
python run.py corrigir-ao-vivo
python run.py stop && python run.py train && python run.py start
```

No laboratório o retreino levou 69 segundos, e `bebi h2o` passou a responder `✅ Registrei: água.` Depois, `python run.py desfazer-correcao`.

## Lição 3: desequilíbrio

`registrar_atividade_rapido` tem 134 exemplos, um terço do total. `greet_afternoon` tem 7. Classes grandes atraem frases ambíguas. Isso ajuda a explicar `valeu, fui` ser lida como registro.

## Como medir

Nunca meça com frases do treino. O projeto tem 40 frases inéditas em `rasa/tests/nlu_inedito.yml`, e um script que confere que nenhuma repete o treino. Resultado no laboratório: 36 acertos.

## Exercícios

1. Acrescente cinco exemplos de despedida informal (“valeu”, “fui”, “até mais”) e meça o efeito com `python run.py test`. A frase `valeu, fui` da prova **não** pode entrar no treino.
2. Escreva três frases de fora de escopo parecidas com registro (“tomei um café”, “assisti a um filme”). O que muda na confiança?
3. Por que não basta aumentar o limiar de fallback para resolver `tomei um café`?

## Resumo

Dados anotados ensinam; sinônimo e regex ajudam; confiança alta não é acerto; medir é com frase inédita.

---
[← Capítulo anterior](capitulo-06-primeira-execucao.md) · [Índice do tutorial](../TUTORIAL_COMPLETO.md) · [Próximo capítulo →](capitulo-08-core.md)
