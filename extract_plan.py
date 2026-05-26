#!/usr/bin/env python3
"""
extract_plan.py
Extrai um plano de edicao legivel (YAML) a partir de um FCPXML.
"""
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


def time_to_seconds(t: str) -> float:
    """Converte '0s', '5s', '150/24s' ou '1/24s' para segundos float."""
    if not t:
        return 0.0
    t = t.replace("s", "").strip()
    if "/" in t:
        num, den = t.split("/")
        return float(num) / float(den)
    return float(t)


def extract_plan(fcpxml_path: Path) -> dict:
    tree = ET.parse(fcpxml_path)
    root = tree.getroot()

    # Mapear recursos (assets)
    assets = {}
    resources = root.find("resources")
    if resources is not None:
        for asset in resources.findall("asset"):
            aid = asset.get("id")
            name = asset.get("name", "unknown")
            src = asset.get("src", "")
            assets[aid] = {"name": name, "src": src}

    plan = {"timeline": []}
    library = root.find("library")
    if library is None:
        return plan

    event = library.find("event")
    if event is None:
        return plan

    project = event.find("project")
    if project is None:
        return plan

    sequence = project.find("sequence")
    if sequence is None:
        return plan

    spine = sequence.find("spine")
    if spine is None:
        return plan

    for child in spine:
        tag = child.tag
        if tag not in ("clip", "title", "audition", "ref-clip"):
            continue

        name = child.get("name", "sem_nome")
        offset = time_to_seconds(child.get("offset", "0s"))
        duration = time_to_seconds(child.get("duration", "0s"))
        ref = child.get("ref", "")
        lane = child.get("lane", "0")
        start = time_to_seconds(child.get("start", "0s"))

        asset_info = assets.get(ref, {})
        asset_name = asset_info.get("name", ref)

        if tag == "title":
            text_elem = child.find("text")
            text_content = ""
            if text_elem is not None:
                ts = text_elem.find("text-style")
                if ts is not None and ts.text:
                    text_content = ts.text
            item = {
                "type": "text",
                "description": text_content or name,
                "in": offset,
                "out": offset + duration,
                "duration": duration,
                "lane": int(lane) if lane else 0,
            }
        elif lane and int(lane) > 0:
            item = {
                "type": "b_roll",
                "description": f"{name} (midia: {asset_name})",
                "in": offset,
                "out": offset + duration,
                "duration": duration,
                "lane": int(lane),
                "over": None,
            }
        else:
            item = {
                "type": "a_roll",
                "description": f"{name} (midia: {asset_name})",
                "in": offset,
                "out": offset + duration,
                "duration": duration,
                "start_in_source": start,
            }

        plan["timeline"].append(item)

    # Segunda passada: atribuir 'over' nos b_roll baseado em sobreposicao temporal com a_roll
    a_rolls = [x for x in plan["timeline"] if x["type"] == "a_roll"]
    for item in plan["timeline"]:
        if item["type"] == "b_roll":
            for ar in a_rolls:
                if item["in"] >= ar["in"] and item["in"] < ar["out"]:
                    item["over"] = ar["description"]
                    break

    return plan


def plan_to_yaml(plan: dict) -> str:
    lines = ["timeline:"]
    for i, item in enumerate(plan["timeline"], 1):
        lines.append(f"  - type: {item['type']}")
        lines.append(f"    description: \"{item['description']}\"")
        lines.append(f"    in: {item['in']}")
        lines.append(f"    out: {item['out']}")
        lines.append(f"    duration: {item['duration']}")
        if item.get("lane"):
            lines.append(f"    lane: {item['lane']}")
        if item.get("over"):
            lines.append(f"    over: \"{item['over']}\"")
        if item.get("start_in_source") is not None:
            lines.append(f"    start_in_source: {item['start_in_source']}")
        lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python extract_plan.py <arquivo.fcpxml>")
        sys.exit(1)

    path = Path(sys.argv[1])
    if not path.exists():
        print(f"Arquivo nao encontrado: {path}")
        sys.exit(1)

    plan = extract_plan(path)
    yaml_text = plan_to_yaml(plan)
    print(yaml_text)

    out_path = path.with_suffix(".yaml")
    out_path.write_text(yaml_text, encoding="utf-8")
    print(f"\nPlano salvo em: {out_path}")
