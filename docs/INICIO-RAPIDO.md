# ⚡ Início rápido

> **Versão 2 do projeto** · documento revisado em 16 nov. 2026 e conferido contra o código. O que não foi testado está dito no texto.

## 1. Instalar e subir (alguns minutos, com internet)

Você precisa de um Python qualquer (3.8 ou mais novo) para rodar o lançador e da ferramenta `uv`, que baixa o Python 3.10 exigido pelo Rasa sem mexer no Python do sistema. Instruções do `uv`: <https://docs.astral.sh/uv/>.

```bash
python run.py setup            # cria o ambiente rasa-env e instala as dependências
python run.py train            # treina o modelo
python run.py start --abrir    # sobe os três serviços e abre o navegador
```

A interface abre em <http://localhost:5001>. No Windows, se `python` não existir, use `py run.py …`.

## 2. Conversar

Digite, nesta ordem, e observe o painel Raio-X à direita:

1. `bebi água`
2. `corri 30 minutos intenso`
3. `malhei 1 hora`
4. `agendar yoga amanhã às 7h`
5. `como estou hoje?`
6. `tomei um café` (falha mantida de propósito)

## 3. Conferir e encerrar

```bash
python run.py status     # o que está no ar
python run.py roteiro    # conversa de ponta a ponta, conferida automaticamente
python run.py stop
```

## Não conseguiu instalar o Rasa?

A tela Replay mostra uma conversa real gravada, com o Raio-X completo, e precisa só do Flask:

```bash
pip install flask
python run.py replay --abrir
```

## Todos os comandos

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

## Trilhas

| Tempo | Caminho |
|---|---|
| 30 minutos | Este arquivo → [03-execucao-testes.md](03-execucao-testes.md) (roteiro em 8 atos) |
| 2 horas | [02-conceitos-rasa.md](02-conceitos-rasa.md) → [06-arquitetura-rasa.md](06-arquitetura-rasa.md) → [07-customizacao.md](07-customizacao.md) |
| Curso completo | [TUTORIAL_COMPLETO.md](TUTORIAL_COMPLETO.md) |

Deu erro? Vá a [04-debug-troubleshooting.md](04-debug-troubleshooting.md).
