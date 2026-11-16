# 🎬 Animações (GIF)

> **Versão 2 do projeto** · documento revisado em 16 nov. 2026 e conferido contra o código. O que não foi testado está dito no texto.

**Não há GIF gravado nesta entrega.** Este arquivo explica como gravar, se você quiser um segundo plano B para a aula além da tela Replay.

## O que vale gravar

| Cena | Duração sugerida | Frases |
|---|---|---|
| Raio-X acendendo etapa por etapa | 15 s | `malhei 1 hora`, em modo passo a passo |
| Formulário e cancelamento | 25 s | `quero registrar exercício`, `cancelar` |
| Falha e mural | 20 s | `tomei um café`, botão “quebrou”, tela do mural |
| Correção ao vivo | 30 s | `bebi h2o` antes e depois do retreino (corte a espera do treino e diga que cortou) |

## Como gravar

Grave a tela em vídeo com a ferramenta do sistema e converta para GIF, ou use um gravador de GIF:

- macOS: Shift+Command+5 grava a tela em vídeo;
- Windows: a Ferramenta de Captura grava vídeo nas versões recentes;
- Linux: Peek ou o gravador do ambiente gráfico.

Conversão com `ffmpeg`, se estiver instalado:

```bash
ffmpeg -i gravacao.mp4 -vf "fps=10,scale=1000:-1" demonstracao.gif
```

O comando acima é o uso comum do `ffmpeg`; não foi executado nesta revisão.

## Cuidados

Os mesmos das capturas de tela: sem chaves à vista, apelidos fictícios e, se houver corte ou aceleração, um aviso na legenda. Uma gravação não substitui o teste na máquina da aula.
