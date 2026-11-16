# 🌐 Capítulo 11: APIs externas

> **Versão 2 do projeto** · documento revisado em 16 nov. 2026 e conferido contra o código. O que não foi testado está dito no texto.

## Objetivos

Integrar um serviço externo sem tornar o bot dependente dele, e entender o cliente de LLM do Duelo.

## Princípio: o bot funciona sem a API

Rede falha, chave expira, serviço muda. Toda integração do projeto segue quatro regras:

1. chave lida do ambiente (`.env`), nunca escrita no código;
2. HTTPS;
3. tempo máximo curto;
4. em caso de falha, o bot continua, sem aquela informação.

## Clima (opcional)

`rasa/actions/weather_api.py` consulta o OpenWeatherMap com tempo máximo de 5 segundos e devolve nulo quando falta chave, quando o tempo estoura ou quando o serviço responde com erro. A saudação, então, só não menciona o clima.

**Esta integração não foi testada nesta revisão**: o laboratório não tinha chave. O caminho “sem chave” é o que os testes e o roteiro exercitam.

## LLM do Duelo

`web_interface/llm.py` envia a frase a um LLM com uma instrução fixa: classifique em uma das intenções do bot e extraia tipo, duração e intensidade, respondendo em JSON. Foi escrito com `urllib`, sem biblioteca do provedor.

```python
# web_interface/llm.py
def configuracao():
    """Le a configuracao do ambiente. Nunca devolve a chave em si."""
    provedor = (os.getenv("LLM_PROVIDER") or "").strip().lower()
    chave = (os.getenv("LLM_API_KEY") or "").strip()
    modelo = (os.getenv("LLM_MODEL") or "").strip()
    base = (os.getenv("LLM_BASE_URL") or "").strip().rstrip("/")
    if provedor == "anthropic":
        base = base or "https://api.anthropic.com/v1"
    elif provedor == "openai":
        base = base or "https://api.openai.com/v1"
    pronto = provedor in ("openai", "anthropic") and bool(chave) and bool(modelo)
    return {"provedor": provedor, "modelo": modelo, "base_url": base, "configurado": pronto,
            "externo": pronto and not re.match(r"^https?://(localhost|127\.0\.0\.1)", base),
            "_chave": chave}
```

| `LLM_PROVIDER` | Formato do pedido |
|---|---|
| `openai` | “Chat Completions”; serve a qualquer API compatível, inclusive local, via `LLM_BASE_URL` |
| `anthropic` | API Messages |

A resposta informa `versao_prompt`. Se a instrução mudar, os duelos gravados antes continuam identificáveis.

### O que foi testado

Um servidor falso, local, recebe o pedido e devolve uma resposta no formato de cada provedor (`tests/test_llm.py`). Isso prova que o pedido é montado e a resposta é lida corretamente. **Não prova** que um provedor real aceita o pedido hoje, nem diz nada sobre a qualidade das respostas. Faça um duelo de verdade antes de depender dele.

### Privacidade

Com provedor externo, a frase digitada sai da máquina. A tela avisa. Não envie dados pessoais; para evitar a saída, aponte `LLM_BASE_URL` para um modelo local.

### Comparar com justiça

| Critério | Classificador do Rasa | LLM |
|---|---|---|
| Precisa de exemplos | Sim | Não; precisa de boa instrução |
| Tempo de resposta | Milissegundos | Depende do provedor e da rede |
| Custo por mensagem | Praticamente nenhum | Cobrado por uso, se externo |
| Mesma entrada, mesma saída | Sim | Nem sempre |
| Frase inesperada | Erra com confiança | Costuma lidar melhor |
| Dados saem da máquina | Não | Sim, se externo |

A tabela descreve características gerais; o projeto não mediu latência nem custo de nenhum provedor.

## Exercícios

1. Desligue a rede e mande `bom dia`. O bot responde? Por quê?
2. Configure um provedor e duele com `tomei um café`, `valeu, fui` e `dei uma corridinha de meia hora no parque`. Salve os duelos.
3. Leia a instrução enviada ao LLM em `llm.py`. Que frase maliciosa poderia tentar mudar o comportamento dele? (O capítulo 19 retoma o assunto.)

## Resumo

API externa é enfeite que pode cair. O bot precisa ficar de pé sem ela, e teste com servidor falso não é teste com o serviço real.

---
[← Capítulo anterior](capitulo-10-database.md) · [Índice do tutorial](../TUTORIAL_COMPLETO.md) · [Próximo capítulo →](capitulo-12-forms.md)
