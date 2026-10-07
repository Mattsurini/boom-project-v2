from __future__ import annotations

import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from knowledge_frontmatter import HUB_NAMES, KNOWLEDGE, metadata, yaml_frontmatter

try:
    import yaml
except ImportError as exc:
    raise SystemExit(f"PyYAML required: {exc}")

REQUIRED = {"title", "type", "stage", "topic", "status"}


def main() -> None:
    changed=[]; skipped=[]
    for path in sorted(KNOWLEDGE.rglob("*.md")):
        rel=path.relative_to(KNOWLEDGE)
        body=path.read_text(encoding="utf-8",errors="ignore")
        m=re.match(r"^---\n(.*?)\n---\n", body, re.S)
        if not m:
            continue
        try:
            old=yaml.safe_load(m.group(1)) or {}
        except Exception:
            skipped.append((rel.as_posix(),"yaml-parse")); continue
        if not isinstance(old,dict) or REQUIRED.issubset(old):
            continue
        allowed=("Convergence-Database" in rel.parts or "Psychology-Database" in rel.parts or "_archive" in rel.parts or path.name.lower() in HUB_NAMES or old.get("status")=="archived-duplicate")
        if not allowed:
            skipped.append((rel.as_posix(),"legacy-source")); continue
        base=metadata(path,body[m.end():])
        base.update(old)  # preserve canonical/source/archive fields
        if not base.get("title"): base["title"]=path.stem.replace("-"," ")
        new=yaml_frontmatter(base)+body[m.end():]
        path.write_text(new,encoding="utf-8")
        changed.append(rel.as_posix())
    print({"normalized":len(changed),"skipped":len(skipped),"changed":changed,"skipped_sample":skipped[:10]})

if __name__ == "__main__":
    main()
