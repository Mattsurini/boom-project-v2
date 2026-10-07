from __future__ import annotations

import csv
import hashlib
import shutil
from datetime import datetime
from pathlib import Path

ROOT = Path(r"E:\Boom Project")
KNOWLEDGE = ROOT / "Knowledge"
MAP = KNOWLEDGE / "indexes" / "KNOWLEDGE_CATEGORY_MAP.csv"
MANIFEST = KNOWLEDGE / "indexes" / "KNOWLEDGE_MOVE_MANIFEST.csv"

TEXT_EXTS = {".md", ".txt", ".html", ".htm", ".yaml", ".yml", ".json", ".xml", ".csv", ".cht", ".jhd"}
HUB_NAMES = {"readme.md", "index.md", "source-map.md", "knowledge_categories.md", "frontmatter_schema.md"}
KEEP_PREFIXES = ("indexes/", "_archive/")


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def target_for(rel: Path, category: str) -> Path | None:
    parts = rel.parts
    top = parts[0] if parts else ""
    suffix = Path(*parts[1:]) if len(parts) > 1 else Path(rel.name)
    if top == "Astrology-Database":
        sub = category.split("/", 1)[1] if category.startswith("Astrology/") else None
        if not sub or sub == "PDF-Unread":
            return None
        return KNOWLEDGE / "Astrology-Database" / sub / suffix
    if top == "Chinese-Astrology":
        sub = category.split("/", 1)[1] if category.startswith("Chinese-Astrology/") else None
        if not sub:
            return None
        return KNOWLEDGE / "Chinese-Astrology" / sub / suffix
    if top == "Psychology-Database":
        return KNOWLEDGE / "Psychology-Database" / "Applications" / suffix
    if top == "Convergence-Database":
        if category == "ML-AI/Insights":
            return KNOWLEDGE / "Convergence-Database" / "ML-AI Insights" / suffix
        if category == "Astrology/Convergence":
            return KNOWLEDGE / "Convergence-Database" / "Astrology Insights" / suffix
        return None
    if category == "System/Metadata":
        return KNOWLEDGE / "System" / "Metadata" / rel
    return None


def is_hub(rel: Path) -> bool:
    return rel.name.lower() in HUB_NAMES


def main() -> None:
    rows = {r["path"]: r for r in csv.DictReader(MAP.open(encoding="utf-8-sig"))}
    moves = []
    for path in sorted(p for p in KNOWLEDGE.rglob("*") if p.is_file()):
        rel = path.relative_to(KNOWLEDGE)
        rel_posix = rel.as_posix()
        row = rows.get(rel_posix)
        if not row or path.suffix.lower() == ".pdf":
            continue
        if rel_posix.startswith(KEEP_PREFIXES) or is_hub(rel):
            continue
        # Preserve duplicate redirect stubs at their legacy paths.
        try:
            head = path.read_text(encoding="utf-8", errors="ignore")[:500]
        except Exception:
            head = ""
        if "status: archived-duplicate" in head:
            continue
        target = target_for(rel, row["category"])
        if target is None or target.resolve() == path.resolve():
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        original_hash = digest(path)
        final_target = target
        collision = ""
        if final_target.exists():
            if digest(final_target) == original_hash:
                moves.append({"old_path": rel_posix, "new_path": final_target.relative_to(KNOWLEDGE).as_posix(), "sha256_before": original_hash, "sha256_after": original_hash, "action": "duplicate-at-target-not-moved", "category": row["category"]})
                continue
            stem, suffix = target.stem, target.suffix
            n = 1
            while final_target.exists():
                final_target = target.with_name(f"{stem}__collision-{n}{suffix}")
                n += 1
            collision = "collision-suffixed"
        shutil.move(str(path), str(final_target))
        after_hash = digest(final_target)
        assert original_hash == after_hash, (path, final_target)
        moves.append({"old_path": rel_posix, "new_path": final_target.relative_to(KNOWLEDGE).as_posix(), "sha256_before": original_hash, "sha256_after": after_hash, "action": collision or "moved", "category": row["category"]})

    # Rewrite project-relative references in readable project text after paths are final.
    replacements = [(m["old_path"], m["new_path"]) for m in moves if m["action"] in {"moved", "collision-suffixed"}]
    changed_files = 0
    replacement_count = 0
    for file in ROOT.rglob("*"):
        if not file.is_file() or file.suffix.lower() not in TEXT_EXTS:
            continue
        try:
            text = file.read_text(encoding="utf-8")
        except Exception:
            continue
        new = text
        for old, new_path in replacements:
            for old_form, new_form in ((old, new_path), (old.replace("/", "\\"), new_path.replace("/", "\\")), ("Knowledge/" + old, "Knowledge/" + new_path), ("Knowledge\\" + old.replace("/", "\\"), "Knowledge\\" + new_path.replace("/", "\\"))):
                count = new.count(old_form)
                if count:
                    new = new.replace(old_form, new_form)
                    replacement_count += count
        if new != text:
            file.write_text(new, encoding="utf-8")
            changed_files += 1

    fields = ["old_path", "new_path", "sha256_before", "sha256_after", "action", "category"]
    with MANIFEST.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(moves)
    moved = sum(m["action"] in {"moved", "collision-suffixed"} for m in moves)
    print({"moves_recorded": len(moves), "moved": moved, "reference_files_changed": changed_files, "references_rewritten": replacement_count, "manifest": str(MANIFEST), "timestamp": datetime.now().astimezone().isoformat()})


if __name__ == "__main__":
    main()
