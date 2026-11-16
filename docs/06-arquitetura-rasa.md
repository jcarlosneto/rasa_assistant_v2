# 🏗️ Arquitetura do Rasa no projeto

> **Versão 2 do projeto** · documento revisado em 16 nov. 2026 e conferido contra o código. O que não foi testado está dito no texto.

## Visão geral

O Rasa tem duas metades. O **NLU** transforma texto em intenção e entidades. O **Core** escolhe a próxima ação com base no histórico. O código Python das ações roda em um processo separado, o **Action Server**.

## NLU: o pipeline

Componentes de `rasa/config.yml`, na ordem em que atuam (idioma: `pt`):

- `WhitespaceTokenizer`
- `RegexFeaturizer`
- `LexicalSyntacticFeaturizer`
- `CountVectorsFeaturizer`
- `CountVectorsFeaturizer` — analyzer: char_wb, min_ngram: 1, max_ngram: 4
- `DIETClassifier` — epochs: 60, constrain_similarities: True, random_seed: 42
- `EntitySynonymMapper`
- `ResponseSelector` — epochs: 20, constrain_similarities: True, random_seed: 42
- `FallbackClassifier` — threshold: 0.5, ambiguity_threshold: 0.1

| Componente | O que faz |
|---|---|
| `WhitespaceTokenizer` | Separa o texto nos espaços |
| `RegexFeaturizer` | Sinaliza padrões declarados no `nlu.yml` |
| `LexicalSyntacticFeaturizer` | Características da palavra e das vizinhas, úteis para entidades |
| `CountVectorsFeaturizer` (duas vezes) | Conta palavras e pedaços de palavra. São vetores **esparsos**, não “embeddings” pré-treinados |
| `DIETClassifier` | Classifica a intenção e extrai entidades no mesmo modelo |
| `EntitySynonymMapper` | Troca o valor de uma entidade já extraída pelo valor canônico |
| `ResponseSelector` | Presente na configuração; o projeto não define intents de recuperação |
| `FallbackClassifier` | Abaixo de 0,5 de confiança, troca a intenção por `nlu_fallback` |

O projeto tem 19 intents e 397 exemplos:

| Intent | Para que serve | Exemplos no treino |
|---|---|---|
| `greet` | Saudação neutra | 16 |
| `greet_morning` | Bom dia | 10 |
| `greet_afternoon` | Boa tarde | 7 |
| `greet_evening` | Boa noite | 7 |
| `goodbye` | Despedida | 16 |
| `stop` | Parar ou cancelar | 12 |
| `confirmar_sim` | Confirmação | 17 |
| `confirmar_nao` | Negação | 13 |
| `registrar_atividade_rapido` | Registrar numa frase só | 134 |
| `registrar_atividade_detalhado` | Pedir o formulário guiado | 31 |
| `agendar_atividade` | Agendar atividade futura | 30 |
| `ask_agenda` | Consultar a agenda | 14 |
| `ask_progresso_hoje` | Progresso de hoje | 29 |
| `ask_progresso_semana` | Progresso dos últimos 7 dias | 10 |
| `ask_motivacao` | Pedir incentivo | 11 |
| `bot_challenge` | Perguntar se é um robô | 10 |
| `ask_ajuda` | Pedir ajuda | 12 |
| `out_of_scope` | Assunto fora do escopo | 18 |
| `nlu_fallback` | Criado pelo FallbackClassifier (não tem exemplos) | — |

A intenção de registro rápido concentra um terço dos exemplos. Esse desequilíbrio ajuda a explicar por que frases estranhas tendem a cair nela.

## Core: as políticas

- `MemoizationPolicy` — max_history: 5
- `RulePolicy` — core_fallback_threshold: 0.3, core_fallback_action_name: action_default_fallback
- `UnexpecTEDIntentPolicy` — max_history: 5, epochs: 20, random_seed: 42
- `TEDPolicy` — max_history: 5, epochs: 20, constrain_similarities: True, random_seed: 42

| Política | Papel |
|---|---|
| `RulePolicy` | Aplica as regras e conduz o formulário. Tem precedência |
| `MemoizationPolicy` | Repete o que viu, exatamente igual, nas histórias |
| `TEDPolicy` | Generaliza a partir das histórias quando nada acima decide |
| `UnexpecTEDIntentPolicy` | Sinaliza intenção improvável no contexto (experimental no Rasa) |

O projeto é dirigido por regras: são 21, contra 12 histórias.

1. Responder saudação simples
2. Responder saudação matinal
3. Responder saudação tarde
4. Responder saudação noite
5. Responder despedida
6. Responder parar/cancelar fora de formulário
7. Responder sobre identidade
8. Fornecer ajuda
9. Dar mensagem motivacional
10. Responder a um "não" solto
11. Responder out of scope educadamente
12. Mostrar progresso de hoje
13. Mostrar progresso da semana
14. Agendar atividade
15. Mostrar agenda
16. Registrar atividade rápida
17. Ativar form de atividade detalhada
18. Submit form de atividade
19. Cancelar formulário ativo
20. Fallback quando não entende
21. Prevenir loop infinito de fallback

Um detalhe que custa caro quando ignorado: **com um formulário ativo, a RulePolicy continua o formulário e só consulta as outras regras quando ele rejeita a entrada**. Por isso o cancelamento depende de o mapeamento do slot recusar a intenção `stop`:

```yaml
# rasa/data/rules.yml
  - rule: Cancelar formulário ativo
    condition:
      - active_loop: atividade_detalhada_form
    steps:
      - intent: stop
      - action: action_deactivate_loop
      - active_loop: null
      - action: action_limpar_slots_atividade
      - action: utter_stop
```

## Slots e formulário

| Slot | Tipo | Como é preenchido |
|---|---|---|
| `tipo_atividade` | text | from_entity + from_text |
| `duracao` | any | from_entity + from_text |
| `intensidade` | text | from_entity + from_text |

Nenhum dos três entra na decisão da política: `tipo_atividade` e `intensidade` têm `influence_conversation: false`, e `duracao` é do tipo `any`, que nunca influencia. Eles guardam valor; quem conduz a coleta é o formulário. O formulário `atividade_detalhada_form` pede os três, na ordem, e cada resposta passa por uma validação em Python.

## Ações

- `action_greeting_contextual`
- `action_registrar_atividade`
- `action_mostrar_progresso_hoje`
- `action_mostrar_progresso_semana`
- `action_default_fallback`
- `validate_atividade_detalhada_form`
- `action_submit_atividade_form`
- `action_limpar_slots_atividade`
- `action_agendar_atividade`
- `action_mostrar_agenda`

Respostas prontas do domínio: `utter_greet`, `utter_goodbye`, `utter_stop`, `utter_iamabot`, `utter_ajuda`, `utter_out_of_scope`, `utter_default`, `utter_ask_rephrase`, `utter_incentivo_registrar`, `utter_tudo_bem`, `utter_ask_tipo_atividade`, `utter_ask_duracao`, `utter_ask_intensidade`, `utter_motivacao`.

A regra de ouro do projeto é **aprendizado de máquina para entender, regra para normalizar**. O modelo entrega o que achou na frase; `catalogo.py` decide o que vai para o banco:

```python
# rasa/actions/catalogo.py
def duracao_valida(minutos):
    """Regra de negocio herdada da versao 1: entre 1 e 300 minutos."""
    return minutos is not None and 1 <= minutos <= 300
```

| Tipo gravado no banco | Variações aceitas |
|---|---|
| água | agua, água, hidratacao, hidratar, hidratei |
| corrida | corrida, corri, correr, running, run |
| caminhada | caminhada, caminhei, caminhar, andei, andar, walking |
| meditação | meditacao, meditei, meditar, mindfulness |
| natação | natacao, nadei, nadar, swimming, piscina |
| musculação | musculacao, malhei, malhar, academia, treino, gym |
| exercício | exercicio, exercitei, exercitar |
| yoga | yoga, ioga |
| ciclismo | ciclismo, pedalei, pedalar, bicicleta, bike |
| alongamento | alongamento, alonguei, alongar |
| leitura | leitura, li, ler, livro |
| tarefa | tarefa |

## Fluxo completo de uma mensagem

Para `malhei 1 hora`, medido em laboratório:

1. Tokens: `malhei`, `1`, `hora`.
2. Intenção: `registrar_atividade_rapido`.
3. Entidades: `tipo_atividade = malhei`, `duracao = 1`.
4. RulePolicy escolhe `action_registrar_atividade`.
5. A ação normaliza: `malhei → musculação`; `1` seguido de `hora` no texto vira `60` minutos.
6. O banco recebe `musculação, 60`. Resposta: `✅ Registrei: musculação · 60 min.`

A tela Raio-X mostra exatamente essas seis etapas, lendo `GET /conversations/<id>/tracker`.

## Avaliação

| Medida | Resultado no laboratório |
|---|---|
| Conversas de teste | 6 de 6 |
| Intenção em 40 frases inéditas | 90% |
| Entidades nas mesmas frases (F1 micro) | 0,98 |

São números de uma máquina e de frases escritas por quem montou o teste. Veja [03-execucao-testes.md](03-execucao-testes.md).

## Decisões de configuração

- **60 épocas no DIET e 20 nas políticas**, com semente fixa. O critério foi tempo de treino curto com os testes passando; não houve busca sistemática de hiperparâmetros.
- **Limiar de fallback em 0,5.** Subir o limiar faz o bot dizer “não entendi” mais vezes; baixar faz errar com mais segurança.
- **Data e hora por expressão regular**, não por entidade treinada: mais previsível com poucos exemplos.

## Próximo passo

[07-customizacao.md](07-customizacao.md).
