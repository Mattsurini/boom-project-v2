#!/usr/bin/env python3
"""
Eng/Libby project finder for Boom Project.

Use this before raw broad searches. It queries the token-economy manifest first,
then falls back to file names/headings/frontmatter-like metadata already captured
by Eng. It prints compact evidence only.
"""
from __future__ import annotations

from pathlib import Path
import argparse
import json
import re
from typing import Any, Dict, List

PROJECT_ROOT = Path("E:/Boom Project")
MANIFEST = PROJECT_ROOT / "Knowledge" / "indexes" / "project_manifest.json"
PROJECT_INDEX = PROJECT_ROOT / "Knowledge" / "indexes" / "PROJECT_INDEX.md"


def norm(s: Any) -> str:
    if isinstance(s, list):
        return " ".join(map(str, s)).lower()
    return str(s or "").lower()


def score_entry(entry: Dict[str, Any], terms: List[str]) -> int:
    # Support both old (long) and new (short) field names for backwards compat
    path = entry.get("p") or entry.get("path", "")
    title = entry.get("t") or entry.get("title", "")
    stage = entry.get("s") or entry.get("stage") or entry.get("agent", "")
    topic = entry.get("tp") or entry.get("topics") or entry.get("topic", "")
    tags = entry.get("tg") or entry.get("tags", [])
    headings = entry.get("h") or entry.get("headings", [])
    
    hay = " ".join([
        norm(path),
        norm(title),
        norm(stage),
        norm(topic),
        norm(tags),
        norm(headings),
    ])
    score = 0
    for term in terms:
        if term in hay:
            score += 10
        # weaker token overlap for Thai/English mixed filenames
        for piece in re.split(r"[\s_\-:/\\.]+", term):
            if len(piece) >= 3 and piece in hay:
                score += 2
    path_norm = norm(path)
    if all(t in path_norm for t in terms if len(t) >= 2):
        score += 5
    return score


def main() -> None:
    parser = argparse.ArgumentParser(description="Eng/Libby manifest-first project finder")
    parser.add_argument("query", nargs="+", help="Search terms")
    parser.add_argument("--limit", type=int, default=12)
    parser.add_argument("--brief", action="store_true", help="Print only score, path, and title for low-token routing")
    parser.add_argument("--route", action="store_true", help="Low-token routing preset: brief output, top 5 matches")
    parser.add_argument("--json", action="store_true", help="Print JSON instead of markdown")
    args = parser.parse_args()

    if args.route:
        args.brief = True
        if args.limit == 12:
            args.limit = 5

    if not MANIFEST.exists():
        raise SystemExit(f"Manifest missing: {MANIFEST}. Run python scripts/project_index.py first.")

    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    terms = [q.lower() for q in args.query]
    rows = []
    for entry in data.get("entries", []):
        score = score_entry(entry, terms)
        if score:
            rows.append((score, entry))
    rows.sort(key=lambda x: (-x[0], norm(x[1].get("p") or x[1].get("path", ""))))
    rows = rows[: args.limit]

    result = {
        "query": " ".join(args.query),
        "manifest": str(MANIFEST),
        "project_index": str(PROJECT_INDEX),
        "matches": [
            {
                "score": score,
                "path": entry.get("p") or entry.get("path"),
                "title": entry.get("t") or entry.get("title"),
                "agent": entry.get("s") or entry.get("stage") or entry.get("agent"),
                "topic": entry.get("tp") or entry.get("topics") or entry.get("topic"),
                "tags": (entry.get("tg") or entry.get("tags", []))[:8],
                "headings": (entry.get("h") or entry.get("headings", []))[:5],
                "size": entry.get("sz") or entry.get("size"),
                "has_frontmatter": entry.get("fm") or entry.get("frontmatter"),
            }
            for score, entry in rows
        ],
    }

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    if args.brief:
        print(f"# Eng Find Brief: {' '.join(args.query)}")
        print(f"Matches: {len(rows)}")
        for i, (score, entry) in enumerate(rows, 1):
            print(f"{i}. {score} | {entry.get('p') or entry.get('path')} | {entry.get('t') or entry.get('title') or '—'}")
        return

    print(f"# Eng Find: {' '.join(args.query)}")
    print(f"Manifest: {MANIFEST}")
    print(f"Matches: {len(rows)}")
    print("")
    for i, (score, entry) in enumerate(rows, 1):
        print(f"{i}. score={score} `{entry.get('p') or entry.get('path')}`")
        print(f"   title: {entry.get('t') or entry.get('title') or '—'}")
        agent = entry.get("s") or entry.get("stage") or entry.get("agent") or "—"
        print(f"   agent/stage: {agent} | topic: {entry.get('tp') or entry.get('topics') or entry.get('topic') or '—'} | frontmatter: {entry.get('fm') or entry.get('frontmatter')}")
        headings = entry.get("h") or entry.get("headings") or []
        if headings:
            print(f"   headings: {'; '.join(map(str, headings[:3]))}")
        print("")


if __name__ == "__main__":
    main()
