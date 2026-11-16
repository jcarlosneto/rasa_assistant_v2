# 🧪 Capítulo 13: Testes automatizados

> **Versão 2 do projeto** · documento revisado em 16 nov. 2026 e conferido contra o código. O que não foi testado está dito no texto.

## Objetivos

Rodar os testes, saber o que cada um prova e desconfiar de resultado verde.

## Um comando

```bash
python run.py test
```

| Etapa | Ferramenta | Pergunta que responde |
|---|---|---|
| Testes unitários | pytest | As regras, o banco e a interface fazem o que está escrito? |
| Frases inéditas | script próprio | A prova repete frases do treino? |
| Validação dos dados | `rasa data validate` | Os dados de treino são coerentes? |
| Conversas | `rasa test core` | As políticas escolhem as ações esperadas? |
| NLU | `rasa test nlu` | O modelo entende frases que nunca viu? |

## Testes unitários

| Arquivo | Funções de teste | O que cobre |
|---|---|---|
| `tests/test_catalogo.py` | 9 | Regras de normalização (tipo, duração, intensidade, datas) |
| `tests/test_database.py` | 6 | Banco: usuários, semana, agenda, mural |
| `tests/test_llm.py` | 5 | Cliente de LLM contra um servidor falso local |
| `tests/test_web.py` | 9 | Rotas da interface, com o Rasa substituído |

São 29 funções; o pytest conta 67 casos porque várias são parametrizadas. Rodam em menos de um segundo e não precisam do Rasa no ar: a interface é testada com o Rasa substituído, e o LLM, com um servidor falso.

## Conversas de teste

```yaml
# rasa/tests/test_stories.yml
  - story: test_formulario_cancelado
    steps:
      - user: |
          quero registrar uma atividade
        intent: registrar_atividade_detalhado
      - action: atividade_detalhada_form
      - active_loop: atividade_detalhada_form
      - user: |
          cancelar
        intent: stop
      - action: action_deactivate_loop
      - active_loop: null
      - action: action_limpar_slots_atividade
      - action: utter_stop
```

Atenção ao que este teste confere: a **sequência de ações**. A intenção vem escrita no teste. Se você escrever `intent: greet_morning` ao lado da frase “oi”, o teste passa, e o NLU nunca foi consultado. A versão 1 tinha exatamente esse caso.

## Prova de NLU

Quarenta frases que não estão no treino. Resultado no laboratório: 36 acertos, com os mesmos quatro erros em dois treinos diferentes (a semente é fixa).

Regras da prova:

1. Frase da prova não entra no treino. O script `tests/checar_ineditas.py` verifica.
2. Erro encontrado na prova não se corrige olhando a prova. Escreva **outras** frases para o treino e meça de novo.
3. Noventa por cento em quarenta frases escritas por quem montou o teste é um indício. Uso real é outra coisa.

## Roteiro de ponta a ponta

```bash
python run.py start
python run.py roteiro
```

Conversa com os serviços de verdade e confere cada resposta e cada efeito no banco: 22 conferências. É o teste que mais se parece com a demonstração.

## Teste verde não é prova

- `rasa test core` devolve sucesso mesmo com conversas reprovadas. Abra `logs/resultados_core/failed_test_stories.yml`.
- Resumo esconde detalhe. Abra `logs/resultados_nlu/intent_errors.json`.
- Um teste só vale se falhar quando o código está errado.

Para conferir o último ponto, a revisão plantou sete defeitos, um por vez, numa cópia do projeto: “1 hora vale 1 minuto”, limite de duração afrouxado, “forte” deixa de ser intensa, filtro por usuário ignorado, semana de oito dias, provedor de LLM fixo e baixa na agenda errada. A suíte detectou os sete. Sete é amostra, não garantia.

## Escrever um teste novo

1. Reproduza o defeito.
2. Escreva o teste e **veja-o falhar**.
3. Corrija.
4. Veja-o passar.

Teste que nunca falhou não mostrou que sabe falhar.

## Exercícios

1. Plante um defeito em `catalogo.py` (por exemplo, aceitar duração de 500 minutos) e rode o pytest. Que teste pegou?
2. Acrescente três frases à prova de NLU e registre o resultado antes de mexer no treino.
3. Acrescente um ato ao roteiro para uma funcionalidade que você criou.

## Resumo

Cada teste responde a uma pergunta. Saiba qual é, abra os detalhes e teste os próprios testes.

---
[← Capítulo anterior](capitulo-12-forms.md) · [Índice do tutorial](../TUTORIAL_COMPLETO.md) · [Próximo capítulo →](capitulo-14-deploy.md)
