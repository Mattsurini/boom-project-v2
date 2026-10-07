#!/usr/bin/env python3
"""
Eng/Libby output organizer for Boom Project.

Consolidates messy Hermes-native alias folders into canonical agent folders
without changing file body meaning. It only moves files, canonicalizes minimal
frontmatter agent names, removes empty alias folders, and writes a compact
organization report.
"""
from __future__ import annotations

from pathlib import Path
from datetime import datetime
import json
import re
import shutil
from typing import Dict, List

import yaml

PROJECT_ROOT = Path("E:/Boom Project")
OUTPUT = PROJECT_ROOT / "Output"
REPORT = PROJECT_ROOT / "Knowledge" / "indexes" / "OUTPUT_ORGANIZATION_REPORT.md"

# Messy/alias folders -> clean canonical folders.
FOLDER_MAP: Dict[str, str] = {

    "astrology-assistant": "Nut",
    "research-specialist": "CK",
    "audit-researcher": "Arm",
    "research-critic": "Nan",
    "project-writer": "Bella",
    "transits": "Transit",
    "source-excerpts": "Sources",
}

# Canonical folders that should remain visible under Output/.
CANONICAL_FOLDERS = [
    "Plawan",
    "Nut",
    "CK",
    "Arm",
    "Nan",
    "Bella",
    "PAC",
    "Transit",
    "Sources",
]

AGENT_BY_FOLDER = {
    "Plawan": "Plawan",
    "Nut": "Nut",
    "CK": "CK",
    "Arm": "Arm",
    "Nan": "Nan",
    "Bella": "Bella",
    "PAC": "PAC",
    "Transit": "Transit",
}


def unique_destination(dest: Path) -> Path:
    """Return a non-clobbering destination path."""
    if not dest.exists():
        return dest
    stem, suffix = dest.stem, dest.suffix
    i = 2
    while True:
        candidate = dest.with_name(f"{stem}__moved{i}{suffix}")
        if not candidate.exists():
            return candidate
        i += 1


def canonicalize_frontmatter(path: Path, canonical_folder: str) -> bool:
    """Update only the frontmatter agent field when this is an agent markdown file."""
    if path.suffix.lower() != ".md":
        return False
    agent = AGENT_BY_FOLDER.get(canonical_folder)
    if not agent:
        return False
    text = path.read_text(encoding="utf-8", errors="ignore")
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n?", text, re.S)
    if not match:
        return False
    try:
        fm = yaml.safe_load(match.group(1)) or {}
    except yaml.YAMLError:
        return False
    if fm.get("agent") == agent:
        return False
    fm["agent"] = agent
    body = text[match.end():]
    new_text = "---\n" + yaml.dump(fm, allow_unicode=True, sort_keys=False) + "---\n\n" + body.lstrip("\n")
    path.write_text(new_text, encoding="utf-8")
    return True


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    for folder in CANONICAL_FOLDERS:
        (OUTPUT / folder).mkdir(parents=True, exist_ok=True)

    moved: List[dict] = []
    canonicalized: List[str] = []
    removed_dirs: List[str] = []

    for src_name, dest_name in FOLDER_MAP.items():
        src_dir = OUTPUT / src_name
        dest_dir = OUTPUT / dest_name
        if not src_dir.exists():
            continue
        dest_dir.mkdir(parents=True, exist_ok=True)
        for src in sorted(src_dir.iterdir(), key=lambda p: p.name.lower()):
            if src.is_dir():
                continue
            dest = unique_destination(dest_dir / src.name)
            shutil.move(str(src), str(dest))
            moved.append({
                "from": str(src.relative_to(PROJECT_ROOT)),
                "to": str(dest.relative_to(PROJECT_ROOT)),
            })
            if canonicalize_frontmatter(dest, dest_name):
                canonicalized.append(str(dest.relative_to(PROJECT_ROOT)))
        try:
            src_dir.rmdir()
            removed_dirs.append(str(src_dir.relative_to(PROJECT_ROOT)))
        except OSError:
            pass

    # Canonicalize already-existing canonical folders too, in case older files drifted.
    for folder in CANONICAL_FOLDERS:
        for md in (OUTPUT / folder).glob("*.md"):
            if canonicalize_frontmatter(md, folder):
                canonicalized.append(str(md.relative_to(PROJECT_ROOT)))

    dir_counts = []
    for folder in sorted([p for p in OUTPUT.iterdir() if p.is_dir()], key=lambda p: p.name.lower()):
        files = [p for p in folder.iterdir() if p.is_file()]
        dir_counts.append({
            "folder": folder.name,
            "files": len(files),
            "md": sum(1 for p in files if p.suffix.lower() == ".md"),
            "json": sum(1 for p in files if p.suffix.lower() == ".json"),
        })

    lines = [
        "# Output Organization Report",
        "",
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        "",
        "## Policy",
        "",
        "Output folders are consolidated into canonical agent folders:",
        "`Plawan`, `Nut`, `CK`, `Arm`, `Nan`, `Bella`, plus `PAC`, `Transit`, and `Sources`.",
        "Alias folders are treated as deprecated input and should not be used for new artifacts.",
        "",
        "## Result",
        "",
        f"- Files moved: {len(moved)}",
        f"- Frontmatter files canonicalized: {len(canonicalized)}",
        f"- Empty alias folders removed: {len(removed_dirs)}",
        "",
        "## Current Output folders",
        "",
    ]
    for row in dir_counts:
        lines.append(f"- `{row['folder']}` — files: {row['files']} | md: {row['md']} | json: {row['json']}")
    lines.extend(["", "## Moves", ""])
    for item in moved:
        lines.append(f"- `{item['from']}` → `{item['to']}`")
    if not moved:
        lines.append("- No moves needed.")

    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(json.dumps({
        "moved": len(moved),
        "canonicalized": len(canonicalized),
        "removed_dirs": removed_dirs,
        "folders": dir_counts,
        "report": str(REPORT),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
