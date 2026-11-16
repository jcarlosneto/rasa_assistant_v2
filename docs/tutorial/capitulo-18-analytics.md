# 📊 Capítulo 18: Analytics e métricas

> **Versão 2 do projeto** · documento revisado em 16 nov. 2026 e conferido contra o código. O que não foi testado está dito no texto.

## Objetivos

Usar o que o projeto já registra para entender como o bot está se saindo, e conhecer os limites dessas medidas.

Este capítulo descreve, em sua maior parte, o que a versão 2 **implementa**. O que é conceitual está indicado.

## O que o sistema registra

Cada mensagem enviada pelo chat vira uma linha na tabela `interacoes`: texto, intenção, confiança, entidades, ações, resposta, latência, motivo automático de falha e, se houver, o relato manual.

## Onde ver

| Tela | O que mostra |
|---|---|
| Saúde (`/saude`) | Total de interações, falhas, taxa de falha, latência média |
| Quebre o bot (`/mural`) | As falhas, com ranking por apelido |
| Dashboard (`/dashboard`) | Atividades: totais, por tipo, por intensidade, sequência de dias, agenda |
| `/api/export.csv` | Atividades em CSV, para análise fora do sistema |

O painel só mostra o que está no banco. Banco vazio aparece vazio: não há dado de exemplo.

## Falhas automáticas

Três sinais mandam uma interação para o mural sem ninguém pedir:

```python
# web_interface/app.py
def motivo_automatico(raiox):
    """Sinais objetivos de que o bot pode ter falhado (viram itens do mural)."""
    if raiox is None:
        return None
    nomes = [a["nome"] for a in raiox["acoes"]]
    if raiox["intent"]["nome"] == "nlu_fallback" and not raiox["formulario_ativo"] \
            and "action_submit_atividade_form" not in nomes:
        return "o bot não entendeu (fallback)"
    if any("não identifiquei a atividade" in r for r in raiox["respostas"]):
        return "entendeu a intenção, mas não a atividade"
    confianca = raiox["intent"]["confianca"] or 0
    if raiox["intent"]["nome"] != "nlu_fallback" and confianca < LIMIAR_CONFIANCA:
        return "baixa confiança (%d%%)" % round(confianca * 100)
```

São sinais objetivos, e incompletos. `valeu, fui` é classificada como registro com confiança alta e, se uma atividade for reconhecida por engano, nenhum sinal dispara. Para esses casos existe o botão “quebrou”.

## Do mural para o treino

A rota `/api/mural/nlu.yml` monta um rascunho de exemplos a partir das falhas. O rascunho usa a intenção que o modelo previu, que pode estar errada. **Revise antes de colar no `nlu.yml`**: corrigir a intenção e anotar as entidades é trabalho humano.

É o ciclo de manutenção de um chatbot: coletar falhas, rotular, acrescentar ao treino, medir de novo.

## Que perguntas fazer aos dados

| Pergunta | Medida | Cuidado |
|---|---|---|
| O bot entende? | Taxa de fallback; acertos na prova de NLU | Fallback baixo não significa acerto: há erro com confiança alta |
| O usuário consegue o que quer? | Conversas que terminam em registro | Exige definir “conversa” e “sucesso” |
| Onde ele trava? | Formulários cancelados; perguntas repetidas | Cancelar pode ser escolha legítima |
| O bot é rápido? | Latência por interação | Depende da máquina e das integrações |
| O que as pessoas pedem e o bot não faz? | Frases em `out_of_scope` e no mural | Fonte das próximas funcionalidades |

## Limites

- **Relato manual tem viés.** Quem reporta é quem se incomodou; quem desistiu em silêncio não aparece.
- **Turma não é público real.** Em aula, as pessoas tentam quebrar o bot.
- **Latência média esconde extremos.** Uma integração lenta some na média.
- **Privacidade.** A tabela guarda o que as pessoas digitaram. Use apelidos e limpe o banco ao final.

## Em produção (conceitual, não implementado)

Sistemas maiores enviam os eventos da conversa para uma fila ou um banco analítico (o Rasa chama isso de “event broker”) e constroem painéis sobre eles. Aqui, o SQLite e três telas bastam.

## Exercícios

1. Depois de uma sessão, calcule a taxa de falha por intenção com uma consulta SQL na tabela `interacoes`.
2. Baixe o rascunho de `/api/mural/nlu.yml`. Quantas candidatas têm a intenção errada?
3. Proponha um sinal automático que pegaria `valeu, fui`. Que falso alarme ele causaria?

## Resumo

O projeto registra cada interação e mostra falhas e latência. Os sinais automáticos ajudam, não substituem a leitura humana, e os dados pedem cuidado.

---
[← Capítulo anterior](capitulo-17-canais.md) · [Índice do tutorial](../TUTORIAL_COMPLETO.md) · [Próximo capítulo →](capitulo-19-seguranca.md)
