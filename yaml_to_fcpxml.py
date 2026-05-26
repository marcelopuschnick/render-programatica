#!/usr/bin/env python3
"""
yaml_to_fcpxml.py
Converte um plano de edicao (YAML) em FCPXML valido para importar no DaVinci Resolve.
"""
import sys
import uuid
from pathlib import Path

try:
    import yaml
except ImportError:
    print("Erro: instale PyYAML: pip install pyyaml")
    sys.exit(1)


def make_uuid() -> str:
    return str(uuid.uuid4()).upper()


def seconds_to_fcpxml_time(t: float) -> str:
    return f"{t}s"


def build_fcpxml(data: dict) -> str:
    assets = data.get("assets", [])
    timeline_items = data.get("timeline", [])

    for i, asset in enumerate(assets):
        if "id" not in asset:
            asset["id"] = f"r{i + 2}"

    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<fcpxml version="1.9">',
        '  <resources>',
        '    <format id="r1" name="FFVideoFormat1080p24" frameDuration="1/24s" width="1920" height="1080"/>',
    ]

    for asset in assets:
        aid = asset["id"]
        name = asset.get("name", "midia")
        src = asset.get("src", f"file:///videos/{name}.mp4")
        duration = asset.get("duration", "20s")
        has_video = asset.get("hasVideo", 1)
        has_audio = asset.get("hasAudio", 1)
        uid = make_uuid()
        lines.append(
            f'    <asset id="{aid}" name="{name}" uid="{uid}" src="{src}" start="0s" duration="{duration}" hasVideo="{has_video}" hasAudio="{has_audio}"/>'
        )

    lines.append("  </resources>")
    lines.append("  <library>")
    lines.append('    <event name="Evento">')
    lines.append('      <project name="Edicao">')
    lines.append('        <sequence format="r1">')
    lines.append("          <spine>")

    for item in timeline_items:
        item_type = item.get("type", "a_roll")
        desc = item.get("description", "sem_nome")
        t_in = item.get("in", 0.0)
        t_out = item.get("out", 5.0)
        duration = t_out - t_in
        ref = item.get("ref", "r2")
        lane = item.get("lane", 0)
        offset = seconds_to_fcpxml_time(t_in)
        dur = seconds_to_fcpxml_time(duration)
        start = seconds_to_fcpxml_time(item.get("start_in_source", 0.0))

        if item_type == "text":
            lines.append(f'            <title name="{desc}" lane="{lane}" offset="{offset}" ref="r1" duration="{dur}">')
            lines.append("              <text>")
            lines.append(f'                <text-style ref="ts1">{desc}</text-style>')
            lines.append("              </text>")
            lines.append('              <text-style-def id="ts1">')
            lines.append('                <text-style font="Helvetica" fontSize="64" alignment="center"/>')
            lines.append("              </text-style-def>")
            lines.append("            </title>")
        else:
            lane_attr = f' lane="{lane}"' if lane else ""
            lines.append(
                f'            <clip name="{desc}"{lane_attr} offset="{offset}" ref="{ref}" start="{start}" duration="{dur}"/>'
            )

    lines.append("          </spine>")
    lines.append("        </sequence>")
    lines.append("      </project>")
    lines.append("    </event>")
    lines.append("  </library>")
    lines.append("</fcpxml>")

    return "\n".join(lines)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python yaml_to_fcpxml.py <arquivo.yaml>")
        sys.exit(1)

    path = Path(sys.argv[1])
    if not path.exists():
        print(f"Arquivo nao encontrado: {path}")
        sys.exit(1)

    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    xml_content = build_fcpxml(data)
    out_path = path.with_suffix(".fcpxml")
    out_path.write_text(xml_content, encoding="utf-8")
    print(f"FCPXML gerado: {out_path}")
