# 📚 Apêndice B: Glossário

> **Versão 2 do projeto** · documento revisado em 16 nov. 2026 e conferido contra o código. O que não foi testado está dito no texto.

Termos em inglês aparecem como são usados no Rasa, com a tradução ao lado.

| Termo | Significado |
|---|---|
| **Action** (ação) | O que o bot faz: enviar um texto pronto ou executar código |
| **Action Server** | Processo que executa as ações escritas em Python |
| **CALM** | “Conversational AI with Language Models”: abordagem licenciada do fabricante, com LLM para entender e fluxos para executar |
| **Canal** | Conector entre o Rasa e um meio de conversa (REST, aplicativos de mensagens) |
| **Confiança** | Número entre 0 e 1 que o classificador atribui à intenção escolhida. Não é probabilidade de acerto |
| **Core** | A parte do Rasa que decide a próxima ação |
| **Custom action** | Ação escrita por você, em Python |
| **DIET** | Modelo do Rasa que classifica a intenção e extrai entidades juntos |
| **Domain** (domínio) | Arquivo que declara tudo o que o bot conhece |
| **Entity** (entidade) | Dado extraído da frase, como duração ou tipo |
| **Época** (“epoch”) | Uma passada completa pelos dados no treino |
| **Fallback** | Resposta de contingência quando o bot não tem segurança |
| **Featurizador** | Componente que transforma texto em números |
| **Form** (formulário) | Mecanismo que pergunta por slots até preencher todos |
| **Intent** (intenção) | O que o usuário quer com a frase |
| **LLM** | Modelo de linguagem de grande porte |
| **Lock store** | Trava que impede duas instâncias de processar a mesma conversa ao mesmo tempo |
| **Mapeamento de slot** | Regra que diz como um slot é preenchido (`from_entity`, `from_text`) |
| **Modo de manutenção** | Situação de um software que não recebe mais recursos novos |
| **Mundo fechado** | Limitação do classificador: só escolhe entre as intenções que conhece |
| **NLU** | “Natural Language Understanding”, compreensão de linguagem natural |
| **Pipeline** | Sequência de componentes do NLU |
| **Policy** (política) | Componente que escolhe a próxima ação |
| **Raio-X** | Tela do projeto que mostra as seis etapas do processamento de uma mensagem |
| **Replay** | Tela que reproduz uma conversa gravada, sem o Rasa |
| **Response** (resposta) | Texto pronto declarado no domínio (`utter_…`) |
| **Rule** (regra) | Comportamento fixo: dada a condição, sempre a mesma ação |
| **Semente** (“random seed”) | Número que fixa os sorteios do treino, para repetir resultados |
| **Sender** | Identificador da conversa. No projeto, o apelido |
| **Slot** | Memória da conversa |
| **Story** (história) | Exemplo de conversa usado para treinar as políticas |
| **Sinônimo** | Mapeamento que troca o valor de uma entidade já extraída |
| **TED** | Política do Rasa que generaliza a partir das histórias |
| **Token** | Pedaço do texto, em geral uma palavra |
| **Tracker** | Histórico estruturado de uma conversa |
| **Tracker store** | Onde o Rasa guarda os trackers (no projeto, em memória) |
| **`uv`** | Ferramenta que instala versões do Python e cria ambientes isolados |
| **Vetor esparso** | Lista de números em que quase tudo é zero; resultado da contagem de palavras |
