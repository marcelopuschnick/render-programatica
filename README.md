# Renderização Programática de Vídeo

Pipeline de **composição e renderização programática** de vídeos institucionais via código — sem depender de suites de edição manuais.

---

## O que faz

1. **Importa projetos FCPXML** do DaVinci Resolve e extrai plano de edição legível (YAML)
2. **Converte planos YAML** de volta para FCPXML válido — útil para geração em escala ou templates
3. **Renderiza vídeo via FFmpeg** com cortes temporais e overlays de texto programáticos

---

## Componentes

| Arquivo | Função |
|---------|--------|
| `extract_plan.py` | Extrai timeline A-roll/B-roll/Texto de um `.fcpxml` para YAML legível |
| `yaml_to_fcpxml.py` | Converte plano YAML em `.fcpxml` pronto para importar no Resolve |
| `ffmpeg_renderer.py` | Renderiza cortes + overlays de texto via FFmpeg, sem GUI |

## Requisitos

- Python 3.11+
- FFmpeg instalado no PATH
- PyYAML (`pip install -r requirements.txt`)

## Uso

```bash
# 1. Extrair plano de um projeto Resolve
python extract_plan.py projeto.fcpxml
# Gera: projeto.yaml

# 2. Converter plano YAML para FCPXML
python yaml_to_fcpxml.py plano.yaml
# Gera: plano.fcpxml

# 3. Renderizar vídeo com cortes e overlays
python ffmpeg_renderer.py
```

## Exemplo de plano YAML

```yaml
timeline:
  - type: a_roll
    description: "Depoimento do pesquisador (midia: entrevista.mp4)"
    in: 0.0
    out: 45.5
    duration: 45.5
    start_in_source: 0.0
  - type: b_roll
    description: "Imagens do laboratorio (midia: lab.mp4)"
    in: 10.0
    out: 20.0
    duration: 10.0
    lane: 1
    over: "Depoimento do pesquisador"
  - type: text
    description: "Dr. Silva — Coordenador"
    in: 0.0
    out: 5.0
    duration: 5.0
    lane: 2
```

## Cenários de uso

- **Séries institucionais**: gerar múltiplos episódios a partir de um template YAML
- **Comunicação interna**: produzir vídeos de resultado de pesquisa rapidamente
- **Eventos**: cortes automáticos de palestras + overlays de identificação
- **Compliance LGPD**: todo o processamento local, vídeo nunca sobe pra nuvem durante edição

---

**Stack:** Python, FFmpeg, FCPXML, YAML
