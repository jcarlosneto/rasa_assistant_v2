# ▶️ Guia de execução e testes

> **Versão 2 do projeto** · documento revisado em 16 nov. 2026 e conferido contra o código. O que não foi testado está dito no texto.

## Subir tudo

```bash
python run.py start --abrir
```

| Serviço | Porta | O que faz | Log |
|---|---|---|---|
| Action Server | 5055 | Executa as ações em Python | `logs/actions.log` |
| Rasa Server | 5005 | NLU + políticas; escuta só em 127.0.0.1 | `logs/rasa.log` |
| Interface Flask | 5001 | Chat, Raio-X, mural, duelo, painel | `logs/web.log` |

No laboratório, a subida levou cerca de 50 segundos; quase todo o tempo é o Rasa carregando o modelo. `python run.py status` mostra o que respondeu e `python run.py stop` encerra os três.

Para subir um serviço só, em primeiro plano e com o log na tela: `python run.py actions`, `python run.py rasa` ou `python run.py web`, cada um em um terminal.

## Roteiro da demonstração em oito atos

| Ato | Digite | Observe no Raio-X |
|---|---|---|
| 1 · Saudação | `bom dia` | A ação lê o relógio e a agenda. Às 15h a resposta é “Boa tarde!” |
| 2 · Registro rápido | `bebi água` · `corri 30 minutos intenso` | Intenção, três entidades e a linha gravada |
| 3 · Normalização | `meditei` · `malhei 1 hora` | NLU entrega `malhei / 1`; o banco grava `musculação / 60` |
| 4 · Agenda | `agendar yoga amanhã às 7h` · `minha agenda` · `caminhei 20 minutos` | Data e hora lidas por expressão regular; baixa automática |
| 5 · Formulário | `quero registrar uma atividade` · `natação` · `um tempão` · `45` · `forte` | A validação recusa `um tempão` |
| 6 · Cancelamento | `quero registrar exercício` · `cancelar` | `action_deactivate_loop`; nada é gravado |
| 7 · Falhas | `como estou hoje?` · `tomei um café` · `bebi h2o` | Confiança alta, nenhuma entidade |
| 8 · Encerramento | `qual a capital da França?` · `tchau` | `out_of_scope` |

O roteiro está em `tests/e2e/roteiro_demo.json`. Para conferi-lo contra os serviços no ar:

```bash
python run.py roteiro
```

No laboratório: 22 conferências, nenhuma divergência.

## Correção ao vivo

```bash
python run.py corrigir-ao-vivo   # acrescenta 5 exemplos de "h2o" ao nlu.yml
python run.py stop
python run.py train              # laboratório: 69 s
python run.py start
python run.py roteiro --apos-correcao
python run.py desfazer-correcao  # devolve o nlu.yml ao estado inicial
```

Depois da correção, `bebi h2o` responde `✅ Registrei: água.`

## Testes automáticos

```bash
python run.py test
```

| Etapa | O que confere | Resultado no laboratório |
|---|---|---|
| Testes unitários (pytest) | Regras, banco, interface, cliente de LLM | 67 aprovados |
| Frases da prova não repetem o treino | `rasa/tests/nlu_inedito.yml` contra `rasa/data/nlu.yml` | sem repetição |
| `rasa data validate` | Coerência dos dados de treino | sem conflitos |
| `rasa test core` | 6 conversas de `rasa/tests/test_stories.yml` | 6 de 6 |
| `rasa test nlu` | 40 frases que o modelo nunca viu | 36 acertos (90%) |

Os testes unitários ficam em:

| Arquivo | Funções de teste | O que cobre |
|---|---|---|
| `tests/test_catalogo.py` | 9 | Regras de normalização (tipo, duração, intensidade, datas) |
| `tests/test_database.py` | 6 | Banco: usuários, semana, agenda, mural |
| `tests/test_llm.py` | 5 | Cliente de LLM contra um servidor falso local |
| `tests/test_web.py` | 9 | Rotas da interface, com o Rasa substituído |

O pytest conta 67 casos porque várias funções são parametrizadas.

### Leia os detalhes, não só o resumo

`rasa test core` devolve sucesso mesmo com conversas reprovadas. Depois de rodar, abra:

- `logs/resultados_core/failed_test_stories.yml` — deve dizer que nenhuma história falhou;
- `logs/resultados_nlu/intent_errors.json` — os erros da prova de NLU.

Os quatro erros medidos: `opa, beleza?` (lida como confirmação), `valeu, fui` (registro), `estou falando com uma pessoa?` (progresso) e `quanto está o dólar?` (progresso). Eles não foram corrigidos depois da medição: ajustar o treino olhando a prova invalidaria a prova.

### O que cada teste não prova

- Teste de conversa confere a sequência de ações. A intenção vem escrita no teste; o NLU não é avaliado ali.
- Noventa por cento em quarenta frases escritas pelo autor do teste é um indício, não uma medida de uso real.
- Tudo foi executado em uma máquina Linux. Na sua, repita.

## Replay

```bash
python run.py gravar-replay     # com os serviços no ar: grava o roteiro
python run.py replay --abrir    # sobe só a interface
```

A faixa amarela da tela informa quando, onde e com que modelo a conversa foi gravada.

## Zerar os dados

```bash
python run.py limpar-banco --sim
```

Apaga atividades, agenda e mural, sem volta. Por isso exige `--sim`.

## Próximo passo

[04-debug-troubleshooting.md](04-debug-troubleshooting.md).
