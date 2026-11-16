# ⚙️ Configurações

> **Versão 2 do projeto** · documento revisado em 16 nov. 2026 e conferido contra o código. O que não foi testado está dito no texto.

## Onde fica cada configuração

| Arquivo | O que configura |
|---|---|
| `.env` | Portas, endereços, banco, chaves opcionais |
| `rasa/config.yml` | Pipeline de NLU e políticas |
| `rasa/domain.yml` | Sessão, slots, respostas |
| `rasa/endpoints.yml` | Endereço do Action Server |
| `rasa/credentials.yml` | Canais do Rasa |
| `requirements.txt` | Versões das dependências |

## O arquivo `.env`

Criado pelo `python run.py setup` a partir do `.env.example`. Não vai para o Git.

| Variável | Valor no `.env.example` | Para que serve |
|---|---|---|
| `FLASK_PORT` | `5001` | Porta da interface web |
| `FLASK_HOST` | `127.0.0.1` | `127.0.0.1` = só esta máquina |
| `RASA_SERVER_URL` | `http://localhost:5005` | Onde a interface encontra o Rasa |
| `RASA_ACTION_SERVER_URL` | `http://localhost:5055` | Onde fica o Action Server |
| `DATABASE_PATH` | `database/atividades.db` | Arquivo SQLite |
| `OPENWEATHER_API_KEY` | (vazio) | Chave do clima (opcional; não testada nesta revisão) |
| `DEFAULT_CITY` | `São Paulo` | Cidade do clima |
| `LLM_PROVIDER` | (vazio) | `openai` (qualquer API compatível) ou `anthropic` |
| `LLM_API_KEY` | (vazio) | Chave do provedor de LLM (só no `.env`) |
| `LLM_MODEL` | (vazio) | Nome exato do modelo, copiado da documentação do provedor |
| `LLM_BASE_URL` | (vazio) | Endereço de API compatível (ex.: modelo local) |
| `LLM_TIMEOUT` | `30` | Tempo máximo da chamada ao LLM, em segundos |

### Interface acessível pela rede local

`FLASK_HOST=0.0.0.0` abre a interface para outros computadores da mesma rede. Antes de fazer isso, considere: não há autenticação, qualquer pessoa na rede lê e escreve, e os apelidos e as frases ficam gravados no banco. O Rasa continua acessível só pela própria máquina.

### LLM do Duelo

```ini
LLM_PROVIDER=openai
LLM_API_KEY=cole-a-sua-chave-aqui
LLM_MODEL=nome-exato-do-modelo
```

- `openai` serve a qualquer API compatível com “Chat Completions”; para outro endereço, inclusive um modelo local, use `LLM_BASE_URL`.
- `anthropic` usa a API Messages.
- Não há modelo padrão, de propósito: nomes de modelo mudam com frequência. Copie o nome da documentação do provedor no dia.
- Sem os três valores, o lado do LLM fica desligado e nada sai da máquina.
- Com provedor externo, a frase digitada é enviada para fora. A tela avisa.

O cliente foi testado contra um servidor falso local. Nenhum provedor real foi chamado nesta revisão.

## `rasa/config.yml`

Pipeline:

- `WhitespaceTokenizer`
- `RegexFeaturizer`
- `LexicalSyntacticFeaturizer`
- `CountVectorsFeaturizer`
- `CountVectorsFeaturizer` — analyzer: char_wb, min_ngram: 1, max_ngram: 4
- `DIETClassifier` — epochs: 60, constrain_similarities: True, random_seed: 42
- `EntitySynonymMapper`
- `ResponseSelector` — epochs: 20, constrain_similarities: True, random_seed: 42
- `FallbackClassifier` — threshold: 0.5, ambiguity_threshold: 0.1

Políticas:

- `MemoizationPolicy` — max_history: 5
- `RulePolicy` — core_fallback_threshold: 0.3, core_fallback_action_name: action_default_fallback
- `UnexpecTEDIntentPolicy` — max_history: 5, epochs: 20, random_seed: 42
- `TEDPolicy` — max_history: 5, epochs: 20, constrain_similarities: True, random_seed: 42

| Parâmetro | Efeito de aumentar |
|---|---|
| `epochs` (DIET) | Treino mais longo; pode melhorar ou decorar o treino |
| `threshold` (FallbackClassifier) | Mais respostas “não entendi” |
| `ambiguity_threshold` | Fallback também quando as duas melhores intenções ficam próximas |
| `max_history` | A política olha mais turnos para trás |
| `core_fallback_threshold` | Mais fallback na escolha da ação |
| `random_seed` | Não é para aumentar: fixa o sorteio e torna o treino repetível |

## Sessão

```yaml
session_config:
  session_expiration_time: 60
  carry_over_slots_to_new_session: false
```

Depois de 60 minutos sem mensagens, a conversa recomeça. Os slots não passam para a sessão nova, para que um formulário abandonado não contamine a conversa seguinte.

## `rasa/endpoints.yml` e `rasa/credentials.yml`

O `endpoints.yml` aponta o Action Server em `http://localhost:5055/webhook`. Não há “tracker store” configurado: o Rasa guarda as conversas em memória e as esquece ao reiniciar. As atividades ficam no SQLite, que persiste.

O `credentials.yml` habilita o canal `rest`, usado pela interface. Há também um bloco `socketio`, herdado da versão 1; a interface da versão 2 não o utiliza.

## Banco de dados

`DATABASE_PATH` aponta o arquivo SQLite, criado na primeira execução. Para começar do zero: `python run.py limpar-banco --sim`. Um banco da versão 1 é migrado na abertura (a coluna `usuario` é acrescentada e os registros antigos ficam sob o usuário `user`); faça uma cópia do arquivo antes.

## Logs

O `run.py start` grava um arquivo por serviço em `logs/` e o sobrescreve a cada subida. Os resultados dos testes ficam em `logs/resultados_core/` e `logs/resultados_nlu/`.

## Variáveis que o `run.py` define sozinho

`RASA_TELEMETRY_ENABLED=false`, para que o Rasa não envie dados de uso.

## Cenários

| Quero… | Faça |
|---|---|
| Outra porta para a interface | `FLASK_PORT` no `.env` |
| Treino mais rápido para um teste | Reduzir `epochs` e medir o efeito com `python run.py test` |
| Bot mais cauteloso | Subir `threshold` do `FallbackClassifier` |
| Duelo sem enviar dados para fora | `LLM_BASE_URL` apontando um modelo local |
