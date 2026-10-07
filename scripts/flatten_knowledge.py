from __future__ import annotations

import csv
import hashlib
import shutil
from pathlib import Path

ROOT = Path(r"E:\Boom Project")
KNOWLEDGE = ROOT / "Knowledge"
MANIFEST = KNOWLEDGE / "indexes" / "KNOWLEDGE_MOVE_MANIFEST.csv"
PAIRS = [
    (KNOWLEDGE / "Astrology-Database" / "Articles" / "#Articles", KNOWLEDGE / "Astrology-Database" / "Articles"),
    (KNOWLEDGE / "Convergence-Database" / "Astrology Insights" / "Astrology Insights", KNOWLEDGE / "Convergence-Database" / "Astrology Insights"),
    (KNOWLEDGE / "Convergence-Database" / "ML-AI Insights" / "ML-AI Insights", KNOWLEDGE / "Convergence-Database" / "ML-AI Insights"),
]


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for c in iter(lambda: f.read(1024 * 1024), b""):
            h.update(c)
    return h.hexdigest()


def main() -> None:
    moves=[]
    for old_root, new_root in PAIRS:
        if not old_root.exists():
            continue
        for src in sorted(p for p in old_root.rglob("*") if p.is_file()):
            rel=src.relative_to(old_root)
            dst=new_root/rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            before=sha(src)
            if dst.exists():
                if sha(dst)==before:
                    src.unlink()
                    action="flatten-dedup"
                    after=before
                else:
                    stem,suffix=dst.stem,dst.suffix; n=1
                    while dst.exists():
                        dst=dst.with_name(f"{stem}__collision-{n}{suffix}"); n+=1
                    shutil.move(str(src),str(dst)); action="flatten-collision"; after=sha(dst)
            else:
                shutil.move(str(src),str(dst)); action="flattened"; after=sha(dst)
            moves.append({"old_path":src.relative_to(KNOWLEDGE).as_posix(),"new_path":dst.relative_to(KNOWLEDGE).as_posix(),"sha256_before":before,"sha256_after":after,"action":action,"category":"structure-cleanup"})
    if moves:
        rows=list(csv.DictReader(MANIFEST.open(encoding="utf-8-sig")))
        fields=list(rows[0].keys())
        for r in moves:
            r={k:r.get(k,"") for k in fields}
            rows.append(r)
        with MANIFEST.open("w",newline="",encoding="utf-8-sig") as f:
            w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(rows)
    print({"flattened":len(moves),"manifest":str(MANIFEST)})


if __name__ == "__main__":
    main()
