# ✅ Apêndice D: Listas de conferência

> **Versão 2 do projeto** · documento revisado em 16 nov. 2026 e conferido contra o código. O que não foi testado está dito no texto.

## Antes da aula (até a véspera)

- [ ] `python run.py setup`, `train`, `start`, `test`, `roteiro` na máquina da aula.
- [ ] Tempo de treino anotado.
- [ ] Replay regravado nessa máquina: `python run.py gravar-replay`.
- [ ] Se for usar o Duelo: `.env` preenchido, um duelo feito e salvo.
- [ ] Aviso de privacidade preparado para a turma.

## Trinta minutos antes

- [ ] `python run.py limpar-banco --sim`.
- [ ] `python run.py start`; página Saúde conferida.
- [ ] Replay aberto em outra aba.
- [ ] Zoom do navegador ajustado; Raio-X legível no compartilhamento de tela.
- [ ] `.env` e terminais com chaves fora da tela.

## Depois da aula

- [ ] `python run.py desfazer-correcao`.
- [ ] `python run.py stop`.
- [ ] Banco limpo ou guardado em local adequado.
- [ ] Falhas interessantes do mural anotadas para a próxima versão.

## Nova intenção

- [ ] Dez ou mais exemplos variados.
- [ ] Declarada no domínio.
- [ ] Regra ou história que a use.
- [ ] Frases novas na prova de NLU, diferentes do treino.
- [ ] `python run.py test` sem falha.

## Nova ação

- [ ] Classe com `name()` e `run()`.
- [ ] Nome em `actions:` no domínio.
- [ ] Valores normalizados antes de gravar.
- [ ] Funciona quando a integração externa falha.
- [ ] Teste unitário para a regra nova.
- [ ] Action Server reiniciado.

## Novo campo de formulário

- [ ] Slot com `from_entity` e `from_text` condicionado.
- [ ] `not_intent: stop`.
- [ ] `utter_ask_<slot>`.
- [ ] `validate_<slot>`.
- [ ] Cancelamento testado.

## Antes de publicar código

- [ ] Nenhuma chave em arquivo versionado.
- [ ] `.env`, banco, logs e modelos fora do Git.
- [ ] Testes e roteiro passando.
- [ ] O que não foi testado está escrito.

## Privacidade

- [ ] Apelidos, não nomes.
- [ ] Turma avisada de que as frases ficam gravadas.
- [ ] Sem dados pessoais enviados a LLM externo.
- [ ] Capturas de tela sem frases de alunos, salvo com consentimento.
