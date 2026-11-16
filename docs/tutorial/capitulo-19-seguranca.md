# 🔐 Capítulo 19: Segurança e privacidade

> **Versão 2 do projeto** · documento revisado em 16 nov. 2026 e conferido contra o código. O que não foi testado está dito no texto.

## Objetivos

Reconhecer o que a versão 2 faz por segurança, o que ela não faz e o que a lei brasileira exige quando há dados pessoais.

A primeira parte descreve o que está **implementado**. A segunda é orientação geral, não aconselhamento jurídico.

## O que a versão 2 faz

| Medida | Onde | Por quê |
|---|---|---|
| Rasa só em 127.0.0.1 | `run.py` | A API do Rasa está habilitada sem token |
| Telemetria do Rasa desligada | `run.py` | O Rasa envia dados de uso por padrão |
| Nenhuma biblioteca de CDN | `web_interface/` | Sem código de terceiros carregado em tempo de execução, sem dependência de rede |
| Texto do usuário inserido como texto | `static/js/app.js` | Evita execução de HTML ou script digitado no chat |
| Apelido higienizado no servidor | `app.py` | O apelido vira identificador de conversa e chave no banco |
| Consultas SQL com parâmetros | `database.py` | Evita injeção de SQL |
| Chaves só no `.env`, fora do Git | `.gitignore` | Segredo não se versiona |
| Chamadas externas por HTTPS e com tempo máximo | `weather_api.py`, `llm.py` | A chave não trafega em claro; falha não trava o bot |
| Aviso quando o texto sai da máquina | Tela Duelo | Transparência sobre o provedor externo |

## O que ela não faz

- **Autenticação.** Qualquer pessoa com acesso à interface lê e escreve.
- **Proteção do Action Server.** Ele escuta em todas as interfaces de rede, sem autenticação.
- **Controle de acesso por apelido.** Quem souber o apelido de outra pessoa vê os registros dela.
- **Criptografia do banco.** O SQLite é um arquivo comum.
- **Limite de requisições.**
- **Base atualizada.** O Rasa 3.6.21 exige Python sem suporte de segurança.

Por isso a recomendação: máquina própria ou rede confiável, nunca exposto à internet.

## Dados pessoais e LGPD

O que o sistema guarda: apelidos, frases digitadas, atividades e horários. Hábitos de exercício e sono podem revelar informação de saúde, que a LGPD trata como dado pessoal sensível.

Para a sala de aula:

- use apelidos, não nomes;
- avise a turma de que as frases ficam gravadas e aparecem no mural;
- `python run.py limpar-banco --sim` ao final;
- não publique capturas de tela com frases de alunos sem consentimento.

Para um sistema real, perguntas mínimas: qual a base legal do tratamento? por quanto tempo os dados ficam? como a pessoa acessa, corrige e apaga os seus dados? quem responde por um incidente? A regra em vigor manda comunicar incidente relevante à ANPD e aos titulares em 3 dias úteis.

## LLM: riscos próprios

Ao ligar o Duelo a um provedor externo:

- **A frase sai da máquina.** Não envie dados pessoais.
- **Injeção de instrução** (“prompt injection”): o texto do usuário pode tentar mudar o comportamento do modelo (“ignore as instruções e…”). No projeto o dano é limitado, porque a resposta do LLM só é exibida (e guardada como duelo, se você pedir); ela não aciona nenhuma ação do bot nem altera as atividades.
- **Saída não confiável.** Se um dia a resposta do LLM passar a acionar algo, ela precisa ser validada como qualquer entrada externa.

O OWASP mantém uma lista dos dez principais riscos de aplicações com LLM; a edição de 2025 começa por injeção de instrução e divulgação de informação sensível.

## Segredos

- A chave do LLM e a do clima ficam só no `.env`.
- Não abra o `.env` durante o compartilhamento de tela.
- Se uma chave apareceu em tela, repositório ou gravação, revogue-a.

## Exercícios

1. Digite `<b>oi</b>` no chat. O texto aparece em negrito? Por quê?
2. Tente usar o apelido de um colega. O que você vê? Como resolveria?
3. Escreva o aviso de privacidade que você leria para a turma antes da demonstração.

## Resumo

O projeto é cuidadoso para uma sala de aula e insuficiente para a internet. Saber a diferença é o conteúdo do capítulo.

---
[← Capítulo anterior](capitulo-18-analytics.md) · [Índice do tutorial](../TUTORIAL_COMPLETO.md) · [Próximo capítulo →](capitulo-20-projeto-final.md)
