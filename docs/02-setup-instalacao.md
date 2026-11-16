# 🚀 Guia de instalação

> **Versão 2 do projeto** · documento revisado em 16 nov. 2026 e conferido contra o código. O que não foi testado está dito no texto.

## O que foi testado

| Ambiente | Situação |
|---|---|
| Linux x86_64, Python 3.10.20 | **Testado**: instalação, treino, testes e roteiro completo |
| macOS (Intel e Apple Silicon) | **Não testado**. O Rasa usa pacotes diferentes do TensorFlow em cada plataforma |
| Windows | **Não testado**. O `run.py` foi escrito para funcionar lá, mas não foi executado |

Se algo falhar fora do Linux, a tela Replay funciona só com Flask (veja o fim deste guia).

## Pré-requisitos

- Um Python 3.8 ou mais novo, só para executar o `run.py`.
- A ferramenta `uv` (<https://docs.astral.sh/uv/>). Ela baixa o Python 3.10 que o Rasa exige, sem alterar o Python do sistema.
- Internet na instalação e uns 4 GB livres em disco (o ambiente `rasa-env` ocupou 2,6 GB no laboratório).

**Por que Python 3.10?** O Rasa Open Source 3.6.21 só instala em Python 3.8, 3.9 ou 3.10. Com Python 3.11 ou mais novo, `pip install rasa` falha. As três versões aceitas já estão fora de suporte: aceitável para estudo, não para produção.

## Instalação recomendada

```bash
python run.py setup
```

O comando cria o ambiente `rasa-env` com Python 3.10, instala o que está em `requirements.txt` e cria o arquivo `.env` a partir do `.env.example`.

Sem o `uv`, o `setup` procura um Python 3.10, 3.9 ou 3.8 já instalado e usa `venv` + `pip`. Se não achar nenhum, para e explica.

## Instalação manual (para entender o que o setup faz)

```bash
uv venv --python 3.10 rasa-env
uv pip install --python rasa-env -r requirements.txt
cp .env.example .env          # no Windows: copy .env.example .env
```

Dependências principais: `rasa==3.6.21`, `rasa-sdk==3.6.2`, `Flask`, `requests`, `pytest`.

## Treinar

```bash
python run.py train
```

Gera `rasa/models/chatbot-assistant-v2.tar.gz`. No laboratório (2 CPUs virtuais) levou entre 98 e 103 segundos. Na sua máquina, meça: o tempo depende do processador.

Um modelo treinado em Linux acompanha a entrega em arquivo separado. Ele serve para um primeiro contato em Linux; em outros sistemas, treine.

## Verificar

```bash
python run.py start
python run.py status
python run.py test
```

`status` deve mostrar os três serviços no ar. `test` deve terminar com “0 etapa(s) com falha”.

## Configurações opcionais

- **Clima na saudação**: preencha `OPENWEATHER_API_KEY` no `.env`. Sem chave, a saudação funciona e só não mostra o clima. Essa integração não foi testada nesta revisão.
- **Duelo com LLM**: preencha `LLM_PROVIDER`, `LLM_API_KEY` e `LLM_MODEL`. Detalhes em [08-configuracoes.md](08-configuracoes.md).

A chave fica só no `.env`, que não vai para o Git.

## Problemas comuns

| Sintoma | Causa provável | O que fazer |
|---|---|---|
| “Nao encontrei Python 3.8-3.10 nem a ferramenta uv” | Python do sistema é 3.11+ e não há `uv` | Instalar o `uv` e repetir |
| Erro ao instalar `tensorflow` | Plataforma sem pacote compatível | Anotar a mensagem completa; usar o Replay enquanto isso |
| `python` não é reconhecido (Windows) | Lançador se chama `py` | `py run.py setup` |
| Porta em uso | Outro programa em 5001, 5005 ou 5055 | `python run.py stop`; mudar `FLASK_PORT` no `.env` |

Mais casos em [04-debug-troubleshooting.md](04-debug-troubleshooting.md).

## Plano B: só o Replay

```bash
pip install flask
python run.py replay --abrir
```

Roda em qualquer Python 3.8 ou mais novo (testado também no 3.13), sem o Rasa.

## Próximo passo

[03-execucao-testes.md](03-execucao-testes.md).
