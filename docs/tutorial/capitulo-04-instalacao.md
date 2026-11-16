# ⚙️ Capítulo 4: Ambiente e instalação

> **Versão 2 do projeto** · documento revisado em 16 nov. 2026 e conferido contra o código. O que não foi testado está dito no texto.

## Objetivos

Instalar o projeto e entender por que ele precisa de um Python antigo isolado.

## O problema

O Rasa 3.6.21 declara, no próprio pacote, que exige Python `>=3.8,<3.11`. Num computador com Python 3.12, `pip install rasa` falha. Trocar o Python do sistema é má ideia.

## A solução

A ferramenta `uv` baixa um Python 3.10 só para o projeto e cria o ambiente `rasa-env`. O Python do sistema fica como está e serve apenas para executar o lançador.

```bash
python run.py setup
```

O que o comando faz:

```python
# run.py
def cmd_setup(_args):
    uv = shutil.which("uv")
    if uv:
        print(">> Criando rasa-env com Python 3.10 (via uv)...")
        subprocess.check_call([uv, "venv", "--python", "3.10", VENV])
        subprocess.check_call([uv, "pip", "install", "--python", PY_VENV, "-r", os.path.join(RAIZ, "requirements.txt")])
```

Sem o `uv`, ele procura um Python 3.10, 3.9 ou 3.8 instalado. Se não achar, para e explica o que fazer.

## Passo a passo

1. Instale o `uv` (<https://docs.astral.sh/uv/>).
2. `python run.py setup` — no laboratório, o ambiente ocupou 2,6 GB.
3. `python run.py train`.
4. `python run.py start --abrir`.
5. `python run.py status`.

## O que foi testado

Apenas Linux x86_64. Em macOS e Windows, nada foi executado nesta revisão. O ponto mais sensível é o TensorFlow, que o Rasa instala com pacotes diferentes em cada plataforma. Se a instalação falhar, anote a mensagem inteira: ela é a informação útil.

## Se não der certo

A tela Replay roda só com Flask:

```bash
pip install flask
python run.py replay --abrir
```

Você acompanha a conversa gravada, com o Raio-X, e instala o Rasa depois, com calma.

## Uma reflexão

As três versões de Python aceitas já não recebem correções de segurança. Para um laboratório isolado, tudo bem. Para um sistema exposto, não. É um custo real de usar software em manutenção, e convém enxergá-lo cedo.

## Exercícios

1. Rode `python --version` e `rasa-env/bin/python --version` (no Windows, `rasa-env\Scripts\python --version`). Explique a diferença.
2. Abra `requirements.txt`. Quais dependências têm versão exata e quais têm faixa? Por quê?
3. Anote quanto tempo o `train` levou na sua máquina.

## Resumo

Python isolado pelo `uv`, um comando para instalar, e um plano B que não depende do Rasa. Guia completo: [../02-setup-instalacao.md](../02-setup-instalacao.md).

---
[← Capítulo anterior](capitulo-03-arquitetura.md) · [Índice do tutorial](../TUTORIAL_COMPLETO.md) · [Próximo capítulo →](capitulo-05-estrutura.md)
