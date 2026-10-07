#!/usr/bin/env python
"""
Generate config/agents.yaml from config/agents.json.

Why this exists: `scripts/libby/classifier.py` reads `config/agents.yaml`, and
the rebuild deleted that hand-maintained file (its `output_aliases` pointed at
stage-alias folders the project rules forbid). Rather than hand-maintain the
same data twice, the YAML is GENERATED from the JSON registry — so the agent
registry has exactly one source of truth and cannot drift.

Run after any edit to config/agents.json:
    python scripts/export_agents_yaml.py
"""
from __future__ import annotations

import json
import os
import sys

BOOM = os.environ.get("BOOM_ROOT", r"E:\Boom Project")
SRC = os.path.join(BOOM, "config", "agents.json")
DST = os.path.join(BOOM, "config", "agents.yaml")


def to_yaml(data: dict) -> str:
    """Minimal YAML emitter — avoids a PyYAML dependency in the core path."""
    out = ["# GENERATED FILE — do not edit by hand.",
           "# Source of truth: config/agents.json  (regenerate: python scripts/export_agents_yaml.py)",
           "#",
           "# v2 rebuild note: `output_aliases` were removed. The old file mapped agents",
           "# onto stage-alias folders (Output/research-specialist, Output/idea-generator, ...)",
           "# which the project rules explicitly forbid. Each agent now has exactly one",
           "# canonical output stage.",
           "",
           "agents:"]
    for name, a in data["agents"].items():
        out.append(f"  {name}:")
        out.append(f"    name: {a['name']}")
        out.append(f"    role: {_q(a['role'])}")
        out.append(f"    output_dir: {a['output_stage']}")
        out.append(f"    output_aliases: []")
        out.append(f"    default_tags: [{', '.join(a.get('tags', []))}]")
        if a.get("responsibilities"):
            out.append("    responsibilities:")
            for r in a["responsibilities"]:
                out.append(f"      - {_q(r)}")
        if a.get("merged_from"):
            out.append(f"    merged_from: [{', '.join(a['merged_from'])}]")
    # libby/classifier.py also reads these top-level sections. They are inputs
    # to classification, not derived data, so they are emitted verbatim from
    # agents.json (recovered from the verified backup — never inferred).
    if "flow_stages" in data:
        out.append("")
        out.append("flow_stages: [" + ", ".join(data["flow_stages"]) + "]")
    if "topic_keywords" in data:
        out.append("")
        out.append("topic_keywords:")
        for topic, words in data["topic_keywords"].items():
            out.append(f"  {topic}: [{', '.join(words)}]")
    return "\n".join(out) + "\n"


def _q(s: str) -> str:
    s = str(s)
    return '"' + s.replace('"', '\\"') + '"' if any(c in s for c in ':#') or s.strip() != s else s


def main() -> int:
    if not os.path.exists(SRC):
        print(f"missing {SRC}", file=sys.stderr)
        return 1
    data = json.load(open(SRC, encoding="utf-8"))
    y = to_yaml(data)
    with open(DST, "w", encoding="utf-8") as f:
        f.write(y)
    n = len(data["agents"])
    print(f"wrote {DST} ({n} agents, {len(y)} chars)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())