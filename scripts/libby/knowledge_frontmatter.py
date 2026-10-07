from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path

ROOT = Path(r"E:\Boom Project")
KNOWLEDGE = ROOT / "Knowledge"
HUB_NAMES = {"readme.md", "index.md", "source-map.md"}


def title_for(path: Path, body: str) -> str:
    for line in body.splitlines():
        m = re.match(r"^#\s+(.+?)\s*$", line)
        if m:
            return m.group(1).strip().replace('"', "'")
    return path.stem.replace("_", " ").replace("-", " ").strip().title().replace('"', "'")


def date_for(path: Path) -> str:
    m = re.search(r"(20\d{6})", path.name)
    if m:
        s=m.group(1)
        return f"{s[:4]}-{s[4:6]}-{s[6:8]}"
    return date.today().isoformat()


def metadata(path: Path, body: str) -> dict:
    rel=path.relative_to(KNOWLEDGE)
    parts=rel.parts
    title=title_for(path,body)
    if "_archive" in parts:
        topic="archive-duplicates"; tags=["boom","knowledge","archive"]; typ="note"; status="clean-with-boundaries"; summary="Archived duplicate or redirect path; use the canonical file named in the body."
    elif "Convergence-Database" in parts:
        if "ML-AI Insights" in parts:
            topic="ml-ai"; tags=["boom","knowledge","ml-ai","insight"]
        else:
            topic="astrology-convergence"; tags=["boom","knowledge","astrology","convergence"]
        typ="insight" if path.name.lower() not in HUB_NAMES else "note"; status="final" if typ=="insight" else "clean-with-boundaries"; summary="Routeable convergence knowledge note; read after the relevant source and audit artifacts."
    elif "Psychology-Database" in parts:
        topic="psychology"; tags=["boom","knowledge","psychology"]; typ="note"; status="clean-with-boundaries"; summary="Psychology/application lane hub; keep behavioral framing separate from astrology technical claims."
    elif "Chinese-Astrology" in parts:
        topic="chinese-astrology"; tags=["boom","knowledge","chinese-astrology"]; typ="source-package" if path.name.lower()=="source-map.md" else "note"; status="clean-with-boundaries"; summary="Chinese astrology route or operating hub."
    else:
        folder=next((p for p in parts if p in {"Articles","Chart-Collections","Financial","Jaimini","KP-Prashna","Nadi","Natal-Rectification","Uranian","Vedic-Classics","Western"}),"astrology")
        topic=folder.lower().replace("-","-"); tags=["boom","knowledge","astrology",topic]
        typ="source-package" if path.name.lower() in {"index.md","source-map.md"} else "note"; status="clean-with-boundaries"; summary=f"Astrology {folder} category hub; use it to route source material without mass-loading legacy files."
    return {"title":title,"date":date_for(path),"type":typ,"stage":"Knowledge","topic":topic,"tags":tags,"source_classes":["database-backed"],"status":status,"summary":summary}


def yaml_frontmatter(meta: dict) -> str:
    lines=["---"]
    lines.append(f"title: {json.dumps(meta['title'], ensure_ascii=False)}")
    lines.append(f"date: {json.dumps(meta['date'])}")
    lines.append(f"type: {meta['type']}")
    lines.append(f"stage: {meta['stage']}")
    lines.append(f"topic: {meta['topic']}")
    lines.append("tags: [" + ", ".join(meta["tags"]) + "]")
    lines.append("source_classes: [" + ", ".join(meta["source_classes"]) + "]")
    lines.append(f"status: {meta['status']}")
    lines.append(f"summary: {json.dumps(meta['summary'], ensure_ascii=False)}")
    lines.append("---\n")
    return "\n".join(lines)


def main() -> None:
    changed=[]; skipped=[]
    for path in sorted(KNOWLEDGE.rglob("*.md")):
        rel=path.relative_to(KNOWLEDGE)
        editable_name = path.name.lower() in HUB_NAMES or re.match(r"20\d{6}-", path.name) and path.stat().st_size < 50000
        if not editable_name and not any(x in rel.parts for x in ['Convergence-Database','Psychology-Database','_archive']):
            continue
        body=path.read_text(encoding="utf-8",errors="ignore")
        if body.lstrip().startswith("---"):
            skipped.append(rel.as_posix()); continue
        if "_archive" in rel.parts and path.name.lower() not in {"readme.md"} and "status: archived-duplicate" not in body[:600]:
            skipped.append(rel.as_posix()); continue
        path.write_text(yaml_frontmatter(metadata(path,body))+body,encoding="utf-8")
        changed.append(rel.as_posix())
    print({"frontmatter_added":len(changed),"already_present_or_skipped":len(skipped),"changed":changed})


if __name__ == "__main__":
    main()
