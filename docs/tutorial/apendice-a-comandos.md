# 📖 Apêndice A: Referência rápida de comandos

> **Versão 2 do projeto** · documento revisado em 16 nov. 2026 e conferido contra o código. O que não foi testado está dito no texto.

## Lançador

```text
python run.py setup             cria o ambiente rasa-env (Python 3.10) e instala tudo
python run.py train             treina o modelo (rasa/models/chatbot-assistant-v2.tar.gz)
python run.py start [--abrir]   sobe os 3 servicos em segundo plano
python run.py status            mostra o que esta no ar
python run.py stop              derruba os 3 servicos
python run.py test              roda todas as verificacoes automaticas
python run.py roteiro           conversa de ponta a ponta contra os servicos no ar
python run.py gravar-replay     grava o roteiro para a tela Replay
python run.py replay [--abrir]  sobe SO a interface (sem Rasa) para o Replay
python run.py corrigir-ao-vivo  aplica a correcao "h2o" no nlu.yml (depois: train)
python run.py desfazer-correcao desfaz a correcao acima
python run.py limpar-banco --sim  apaga atividades, agenda e mural
python run.py actions | rasa | web   sobe UM servico em primeiro plano
```

No Windows, se `python` não existir, use `py run.py …`.

## Sequências comuns

| Situação | Comandos |
|---|---|
| Primeira vez | `setup` → `train` → `start --abrir` |
| Mudei dados de treino ou o domínio | `stop` → `train` → `start` |
| Mudei código das ações ou da interface | `stop` → `start` |
| Antes da aula | `limpar-banco --sim` → `start` → `roteiro` |
| Correção ao vivo | `corrigir-ao-vivo` → `stop` → `train` → `start` |
| Depois da aula | `desfazer-correcao` → `stop` |
| Rasa não instala | `replay --abrir` |

## Comandos do Rasa, dentro do ambiente

O `run.py` cobre o uso normal. Para explorar, chame o Rasa pelo Python do ambiente, a partir da pasta `rasa/`:

```bash
cd rasa
../rasa-env/bin/python -m rasa data validate --domain domain.yml --data data
../rasa-env/bin/python -m rasa shell nlu --model models/chatbot-assistant-v2.tar.gz
../rasa-env/bin/python -m rasa test nlu --model models/chatbot-assistant-v2.tar.gz --nlu tests/nlu_inedito.yml
```

No Windows, o interpretador fica em `..\rasa-env\Scripts\python`. `rasa shell nlu` abre um terminal interativo que mostra só a saída do NLU.

## Consultas HTTP

```bash
# só o NLU
curl -s -X POST http://localhost:5005/model/parse -H "Content-Type: application/json" -d '{"text": "bebi h2o"}'

# conversa pelo canal REST
curl -s -X POST http://localhost:5005/webhooks/rest/webhook -H "Content-Type: application/json" -d '{"sender": "teste", "message": "bebi água"}'

# histórico da conversa
curl -s "http://localhost:5005/conversations/teste/tracker?include_events=ALL"

# situação dos serviços
curl -s http://localhost:5001/api/saude
```

## Testes unitários diretos

```bash
rasa-env/bin/python -m pytest -q tests
rasa-env/bin/python -m pytest -q tests/test_catalogo.py -k duracao
```

## Onde ficam os resultados

| Arquivo | Conteúdo |
|---|---|
| `logs/actions.log`, `logs/rasa.log`, `logs/web.log` | Log de cada serviço |
| `logs/resultados_core/failed_test_stories.yml` | Conversas reprovadas |
| `logs/resultados_nlu/intent_errors.json` | Erros da prova de NLU |
