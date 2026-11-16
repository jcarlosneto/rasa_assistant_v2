# 🐛 Guia de depuração e solução de problemas

> **Versão 2 do projeto** · documento revisado em 16 nov. 2026 e conferido contra o código. O que não foi testado está dito no texto.

## Por onde olhar primeiro

1. `python run.py status` — quem está no ar.
2. A página **Saúde** (`/saude`) — Rasa, Action Server, modelo carregado, LLM.
3. Os logs em `logs/`: `actions.log`, `rasa.log`, `web.log`.
4. O **Raio-X**: intenção errada? entidade faltando? política inesperada?

## Problemas de instalação e subida

| Sintoma | Causa provável | Solução |
|---|---|---|
| `setup` diz que não achou Python 3.8–3.10 nem `uv` | Python do sistema é 3.11 ou mais novo | Instalar o `uv` |
| Falha ao instalar o TensorFlow | Plataforma sem pacote compatível com o Rasa 3.6.21 | Guardar a mensagem; usar o Replay |
| `start` informa que um serviço “NAO respondeu” | Erro na subida | Ler `logs/<serviço>.log` |
| Rasa não sobe e o log cita o modelo | Não há modelo treinado | `python run.py train` |
| Porta em uso | Processo antigo ou outro programa | `python run.py stop`; se persistir, mudar `FLASK_PORT` |
| Chat responde “Não consegui falar com o Rasa” | Rasa fora do ar ou ainda carregando | Aguardar; `python run.py status` |

## Problemas de comportamento

| Sintoma | Como investigar | Solução |
|---|---|---|
| Intenção errada com confiança alta | Raio-X, etapa 3 | Mais exemplos da intenção certa ou de fora de escopo; retreinar |
| Intenção certa, entidade ausente | Raio-X, etapa 4 | Exemplos com a palavra **anotada** como entidade |
| Sinônimo não funciona | A entidade foi extraída? | Sinônimo só atua depois da extração (caso `h2o`) |
| Formulário não cancela | Mapeamentos `from_text` do slot | Conferir `not_intent: stop` em `rasa/domain.yml` |
| Ação não executa | `logs/actions.log` | A ação está em `actions:` no domínio? O Action Server foi reiniciado? |
| Mudei o `nlu.yml` e nada mudou | Modelo antigo | `stop`, `train`, `start` |
| Mudei `actions.py` e nada mudou | Action Server não recarrega sozinho | `stop`, `start` |
| Painel vazio | Banco sem registros | É o esperado: a v2 não mostra dado fictício |
| Aparecem registros antigos | Banco do ensaio | `python run.py limpar-banco --sim` |

O defeito mais instrutivo do projeto: com o formulário ativo, um mapeamento `from_text` aceita **qualquer** texto, inclusive “cancelar”. O formulário não rejeita a entrada e a regra de cancelamento nunca é consultada. A correção está no domínio:

```yaml
# rasa/domain.yml
  tipo_atividade:
    type: text
    influence_conversation: false
    mappings:
      # Preenche com a entidade, EXCETO na frase que abre o formulario:
      # em "quero registrar exercicio", "exercicio" nao e a resposta.
      - type: from_entity
        entity: tipo_atividade
        not_intent: registrar_atividade_detalhado
      # Dentro do formulario, quando esta e a pergunta da vez, vale o texto todo
      # (assim "pilates", que o modelo nunca viu, tambem e aceito).
      - type: from_text
        not_intent: stop          # "cancelar" nao e resposta: deixa a regra de cancelamento agir
        conditions:
          - active_loop: atividade_detalhada_form
            requested_slot: tipo_atividade
```

## Ferramentas

- **Raio-X em modo passo a passo** (barra de espaço): uma etapa por vez.
- **Tracker**: `GET http://localhost:5005/conversations/<apelido>/tracker` devolve o histórico completo da conversa.
- **Parse direto**: `POST http://localhost:5005/model/parse` com `{"text": "bebi h2o"}` mostra só o NLU.
- **Um serviço em primeiro plano**: `python run.py rasa` mostra o log na tela.
- **Roteiro**: `python run.py roteiro` aponta o primeiro passo que divergiu.

## Avisos que aparecem e não são erro

| Aviso | Explicação |
|---|---|
| `DeprecationWarning` de `pkg_resources`, `distutils`, SQLAlchemy, TensorFlow | Consequência de usar uma versão antiga do Rasa |
| `The UnexpecTED Intent Policy is currently experimental` | Aviso do próprio Rasa sobre uma política do projeto |
| `The utterance 'utter_ask_…' is not used in any story or rule` | Falso alarme: essas respostas são acionadas pelo formulário |
| `PyparsingDeprecationWarning` durante `rasa test` | Vem do matplotlib, usado nos gráficos do relatório |

## Duelo

| Sintoma | Causa |
|---|---|
| “LLM não configurado” | Faltam `LLM_PROVIDER`, `LLM_API_KEY` ou `LLM_MODEL` no `.env` |
| Erro 401 ou 404 do provedor | Chave inválida ou nome de modelo inexistente |
| Demora ou falha de rede | Aumentar `LLM_TIMEOUT`; usar duelos gravados |

## Quando pedir ajuda

Leve: sistema operacional e processador, a saída de `python run.py status`, as últimas 30 linhas do log do serviço que falhou e a frase exata digitada.

## Lista de conferência

- [ ] Os três serviços respondem.
- [ ] O modelo foi treinado depois da última mudança nos dados.
- [ ] O Action Server foi reiniciado depois da última mudança no código.
- [ ] `python run.py test` termina sem falha.
- [ ] `python run.py roteiro` termina sem divergência.
