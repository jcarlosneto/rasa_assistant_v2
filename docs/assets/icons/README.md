# 🎨 Ícones

> **Versão 2 do projeto** · documento revisado em 16 nov. 2026 e conferido contra o código. O que não foi testado está dito no texto.

O projeto não tem arquivos de ícone. A interface usa emojis do próprio sistema nos rótulos e nas mensagens do bot (✅, 📅, 📊, 🔥), e a página declara um ícone vazio para o navegador não pedir `favicon.ico`.

Consequência prática: a aparência dos emojis varia entre sistemas operacionais e navegadores. Isso não afeta o funcionamento.

Se quiser acrescentar ícones próprios:

1. Coloque os arquivos em `web_interface/static/`, não nesta pasta. Aqui fica só material da documentação.
2. Prefira SVG.
3. Não carregue ícones de CDN: a aula não pode depender de internet.
4. Dê um texto alternativo a cada ícone que carregue significado; emoji decorativo não deve ser a única forma de transmitir uma informação.
