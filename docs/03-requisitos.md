# 📋 Requisitos do sistema

> **Versão 2 do projeto** · documento revisado em 16 nov. 2026 e conferido contra o código. O que não foi testado está dito no texto.

Situação de cada requisito na versão 2. “Verificado” significa que há teste automático ou passo do roteiro que o confere.

## Requisitos funcionais

| ID | Requisito | Situação | Onde se verifica |
|---|---|---|---|
| RF01 | Registrar atividade numa frase, com tipo, duração e intensidade opcionais | Verificado | Roteiro, atos 2 e 3 |
| RF02 | Normalizar tipo, duração (em minutos) e intensidade antes de gravar | Verificado | `tests/test_catalogo.py` |
| RF03 | Aceitar duração apenas entre 1 e 300 minutos | Verificado | `tests/test_catalogo.py` |
| RF04 | Conduzir formulário de três campos, validando cada resposta | Verificado | Roteiro, ato 5 |
| RF05 | Cancelar o formulário sem gravar nada | Verificado | Roteiro, ato 6; `test_formulario_cancelado` |
| RF06 | Agendar atividade com data e hora; listar a agenda | Verificado | Roteiro, ato 4 |
| RF07 | Dar baixa no agendamento ao registrar a atividade no dia | Verificado | `tests/test_database.py` |
| RF08 | Informar progresso de hoje e dos últimos 7 dias | Verificado | Roteiro, ato 7 |
| RF09 | Saudar conforme a hora e lembrar a agenda do dia | Verificado | Roteiro, ato 1 |
| RF10 | Mostrar o clima na saudação quando houver chave | **Não testado** | — |
| RF11 | Separar os registros por usuário (apelido) | Verificado | `tests/test_database.py` |
| RF12 | Exibir o Raio-X de cada mensagem com dados do tracker | Verificado | `tests/test_web.py` |
| RF13 | Registrar falhas no mural, automaticamente ou por relato | Verificado | `tests/test_web.py` |
| RF14 | Comparar classificador e LLM na mesma frase | Parcial | Cliente testado com servidor falso; nenhum provedor real |
| RF15 | Reproduzir conversa gravada sem o Rasa | Verificado | Executado com Python 3.13 |
| RF16 | Exportar atividades em CSV | Conferido à mão | Resposta 200 com cabeçalho CSV; não há teste automático |
| RF17 | Responder com educação a assunto fora de escopo | Verificado | Roteiro, ato 8 |

## Requisitos não funcionais

| ID | Requisito | Situação |
|---|---|---|
| RN01 | Funcionar sem internet depois de instalado (sem CDN) | Atendido |
| RN02 | Um comando por tarefa, igual nos três sistemas (`run.py`) | Atendido em Linux; não testado em macOS e Windows |
| RN03 | Treino curto o bastante para retreinar em aula | 98 a 103 s no laboratório |
| RN04 | Rasa acessível só pela própria máquina | Atendido (`127.0.0.1`) |
| RN05 | Telemetria do Rasa desligada | Atendido (o `run.py` define `RASA_TELEMETRY_ENABLED=false`) |
| RN06 | Chaves apenas no `.env`, fora do Git | Atendido |
| RN07 | Texto do usuário inserido na página como texto, nunca como HTML | Atendido |
| RN08 | Reprodutibilidade do treino (semente fixa) | Atendido: mesmos resultados em dois treinos |
| RN09 | Acessibilidade da interface | **Não auditada** |
| RN10 | Uso simultâneo por vários usuários | **Não testado** |
| RN11 | Autenticação | **Não existe**: sistema de sala de aula |

## Limitações conhecidas

- Sem notificação ativa da agenda.
- Três falhas mantidas de propósito: `tomei um café`, `bebi h2o`, `valeu, fui`.
- Vocabulário de atividades finito, definido em `rasa/actions/catalogo.py`.
- Datas e horas da agenda são lidas por expressão regular; formas não previstas não são entendidas.

## Ideias para evoluir

Notificação da agenda; autenticação e uso em rede; prova de NLU com frases dos alunos; migração do entendimento para um LLM (a tela Duelo é o primeiro passo); auditoria de acessibilidade.
