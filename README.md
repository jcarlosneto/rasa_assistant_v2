# Assistente de Atividades — Rasa Open Source na prática (versão 2)

Chatbot didático que **registra** e **agenda** atividades de bem-estar, feito com Rasa Open Source 3.6.21, Flask e SQLite.
Foi desenhado para a Aula 6 (Plataformas de ChatBots): cada conceito do slide vira algo que acontece na tela.

> **Leia antes.** O Rasa Open Source está em modo de manutenção e a última versão aberta (3.6.21) só instala em
> Python 3.8, 3.9 ou 3.10 — versões que já saíram de suporte. Este projeto serve para **aprender os fundamentos**;
> não é recomendação de arquitetura para um produto novo. Esse contraste faz parte da aula.

## O que há de novo na versão 2

| Tela | Para que serve na aula |
| --- | --- |
| **Chat + Raio-X** (`/`) | A cada mensagem, seis etapas acendem na ordem em que o Rasa as executa: mensagem → tokens → intenção → entidades → decisão (qual política escolheu cada ação) → efeito no banco. Os dados vêm do "tracker" do próprio Rasa; nada é simulado. Há um modo **passo a passo** (barra de espaço) para explicar etapa por etapa. |
| **Quebre o bot** (`/mural`) | Toda falha percebida pelo sistema, ou reportada com "🔨 quebrou", vai para um mural com ranking. O botão "Gerar candidatas para o nlu.yml" transforma as falhas em matéria-prima de treino. |
| **Duelo 1.0 × 2.0** (`/duelo`) | A mesma frase vai para o classificador do Rasa e para um LLM (opcional, com chave no `.env`). |
| **Replay** (`/replay`) | Conversa real gravada. Funciona **sem o Rasa no ar** — é o plano B da demonstração. |
| **Dashboard** (`/dashboard`) | Totais, sequência de dias, tipos, intensidade, agenda, filtro e exportação CSV, lidos do banco. |
| **Saúde** (`/saude`) | O que está no ar, latência média, taxa de falha. |

Novas capacidades do bot: **agenda** ("agendar yoga amanhã às 7h", "minha agenda", baixa automática quando a atividade
é registrada), **normalização** ("meditei" → meditação; "malhei 1 hora" → 60 min; "intenso" → intensa),
**separação por usuário** (apelido) e **cancelamento de formulário** que cancela de fato.

## Instalação (macOS, Linux, Windows)

Pré-requisito único: a ferramenta [`uv`](https://docs.astral.sh/uv/), que baixa o Python 3.10 sozinha, sem mexer no
Python do sistema. (Sem `uv`, o `setup` procura um Python 3.8–3.10 já instalado.)

```bash
python run.py setup      # cria o ambiente rasa-env e instala as dependências
python run.py train      # treina o modelo
python run.py start --abrir
```

No Windows use `py run.py ...`. Para parar: `python run.py stop`. Estado: `python run.py status`.

**Sem conseguir instalar o Rasa?** A tela Replay precisa só do Flask e roda em qualquer Python 3.8+ (inclusive 3.12):

```bash
pip install flask
python run.py replay --abrir
```

### O que foi e o que não foi testado

| Ambiente | Situação |
| --- | --- |
| Linux x86_64, Python 3.10.20 | **Testado**: instalação, treino, testes e roteiro completo (evidências em `docs/`). |
| macOS Intel (ex.: MacBook Air 2013) | **Não testado** nesta entrega. A versão 1 já rodava nessa máquina com as mesmas versões de Rasa. |
| macOS Apple Silicon (M1 ou mais novo) | **Não testado.** O pacote do Rasa declara, para essa plataforma, a dependência `tensorflow-macos 2.12.0`. |
| Windows | **Não testado.** O `run.py` foi escrito para Windows, mas ninguém o executou lá. |
| Módulos sem Rasa (`catalogo`, `database`, interface, cliente LLM) | Testados também em Python 3.13. |

Se a instalação falhar na sua máquina, use o Replay na aula e traga a mensagem de erro.

## Roteiro da demonstração

`tests/e2e/roteiro_demo.json` é o roteiro falado em aula, em oito atos. Com os serviços no ar:

```bash
python run.py roteiro          # conversa de ponta a ponta e confere cada resposta
python run.py gravar-replay    # idem, e regrava a tela Replay na SUA máquina
```

### Falhas mantidas de propósito

| Frase | O que acontece | O que ensina |
| --- | --- | --- |
| `tomei um café` | Intenção "registrar" com confiança alta; nenhuma atividade identificada | Classificador de mundo fechado: sempre escolhe um dos intents que conhece |
| `bebi h2o` | Idem | Sinônimo não ensina palavra nova: o modelo precisa ver a palavra marcada como entidade |
| `valeu, fui` | Classificado como registro, não como despedida | Medir em frase inédita (`rasa/tests/nlu_inedito.yml`): 36 de 40 acertos no laboratório |

### Correção ao vivo ("do mural para o treino")

```bash
python run.py corrigir-ao-vivo     # insere 5 exemplos de "h2o" no nlu.yml
python run.py stop && python run.py train && python run.py start
python run.py roteiro --apos-correcao
python run.py desfazer-correcao    # volta ao estado original (retreine depois)
```

No laboratório o retreino levou 69 s (2 vCPU). **Na sua máquina o tempo será outro: ensaie antes.**

## Verificações automáticas

```bash
python run.py test
```

Roda: testes unitários (pytest), conferência de que as frases da prova não repetem o treino, validação dos dados,
testes de conversa (`rasa test core`) e a prova do NLU com frases inéditas (`rasa test nlu`).
Atenção: `rasa test core` confere a ação escolhida **dado o intent rotulado**; quem confere o NLU é a prova de frases inéditas.

## Duelo 1.0 × 2.0 (opcional)

Preencha no `.env`: `LLM_PROVIDER` (`openai` para qualquer API compatível com Chat Completions, ou `anthropic`),
`LLM_API_KEY` e `LLM_MODEL` (nome exato, copiado da documentação do provedor no dia). Reinicie a interface.

- Com provedor externo, **a frase digitada sai da sua máquina**; a tela avisa. Para manter tudo local, aponte
  `LLM_BASE_URL` para um servidor compatível na própria máquina (por exemplo, Ollama).
- O botão "Salvar este duelo" grava o resultado real para uso offline, sempre rotulado como gravação.
- O cliente foi testado contra um servidor falso (formato do pedido e leitura da resposta). **Nenhum provedor real
  foi chamado nesta entrega**: faça um duelo de ensaio antes da aula.

## Privacidade e uso em sala

- Por padrão tudo escuta só em `127.0.0.1` (a própria máquina). A API do Rasa não tem autenticação.
- Para a turma acessar pela rede local, defina `FLASK_HOST=0.0.0.0` no `.env`. Faça isso só em rede confiável:
  a interface **não tem login**.
- Use **apelidos**, não nomes completos. Atividade física e bem-estar podem revelar dado de saúde (LGPD).
  Ao fim da aula: `python run.py limpar-banco --sim`.
- O Rasa envia telemetria anônima por padrão; o `run.py` a desliga (`RASA_TELEMETRY_ENABLED=false`).

## Estrutura

```
run.py                     comando único (setup, train, start, test, roteiro...)
rasa/
  domain.yml               intents, entidades, slots, respostas, formulário
  config.yml               pipeline do NLU e políticas do Core
  data/                    nlu.yml (exemplos), rules.yml (regras), stories.yml (conversas)
  actions/actions.py       ações em Python       actions/catalogo.py  normalização por regra
  actions/database.py      SQLite                actions/weather_api.py  clima (opcional)
  tests/                   test_stories.yml (Core) e nlu_inedito.yml (prova do NLU)
web_interface/             app.py (Flask), llm.py (duelo), templates/, static/, replay/
tests/                     pytest (catálogo, banco, interface, cliente LLM) e e2e/ (roteiro)
demo/correcao_ao_vivo/     exemplos usados na correção ao vivo
docs/legado-v1/            documentação da versão 1 (não revisada)
scripts/                   atalhos .sh da versão 1 que chamam o run.py
```

## Exercícios sugeridos

1. Faça o bot entender "valeu, fui" como despedida. Meça antes e depois com `python run.py test`.
2. Acrescente a intensidade "puxado" a um exemplo do `nlu.yml` e veja o Raio-X.
3. Crie o intent `cancelar_agendamento` (regra + action + teste).
4. Encontre três falhas novas, gere as candidatas pelo mural e corrija uma.
5. Compare no Duelo: em quais frases o LLM acerta e o classificador erra? E o contrário?

## Licença

MIT (ver `LICENSE`). Rasa Open Source é distribuído sob Apache 2.0.
