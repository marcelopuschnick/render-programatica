# Renderização Programática de Vídeo Institucional

Motor de renderização por composição programática para séries institucionais, eventos e branded content. Substitui templates manuais do After Effects por código versionável, com integração de assets dinâmicos (texto, imagem, áudio).

## Como funciona

1. **Entrada**: JSON de composição (sequência de cenas, durações, fontes)
2. **Compositor**: Python + Remotion-like pipeline (FFmpeg + ImageMagick)
3. **Saída**: MP4 pronto para entrega final, com overlays, lower-thirds e branding

## Uso rápido

```bash
python compositor.py assets/composicao_reuniao.json --output evento_final.mp4
```

## Exemplo de composição

```json
{
  "titulo": "Assembleia Geral 2024",
  "duracao": 120,
  "cenas": [
    {"tipo": "intro", "asset": "logo_animado.mp4", "duracao": 5},
    {"tipo": "lower-third", "texto": "Dr. Silva — Diretor de Pesquisa", "duracao": 8},
    {"tipo": "broll", "asset": "lab_cenas.mp4", "duracao": 45}
  ]
}
```

## Por que programático

- Reutilização de composições entre episódios de série institucional
- Versionamento via Git — histórico completo de alterações
- Geração em lote (batch) para séries de 20+ episódios
- Renderização em servidor sem interface gráfica (headless)

## Stack

- Python 3.10+
- FFmpeg (renderização)
- Pillow (overlays gráficos)
- JSON Schema (validação de composições)
