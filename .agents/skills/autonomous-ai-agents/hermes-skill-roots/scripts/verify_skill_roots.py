#!/usr/bin/env python
"""Report how Hermes resolves skill roots: tiers, trust, conflicts, drift.

Usage:  python verify_skill_roots.py [project_root]

Prints the precedence tier of every root, the resolved status of every scanned
entry (unique / ambiguous / shadowed), which skills fall back to a lower tier,
and byte-drift between a project root and its mirror. Run it whenever a skill
"disappeared" or an edit had no effect — the cause is nearly always a tier or a
quarantine verdict, not a missing file.

find_project_root() reads the session/terminal cwd, so TERMINAL_CWD is set from
the argument here; without it the probe reports no project root and looks like a
dead root.

Exit code 1 when two roots have drifted.
"""
from __future__ import annotations

import hashlib
import os
import sys
from collections import Counter
from pathlib import Path

BOOM = Path(
    sys.argv[1]
    if len(sys.argv) > 1
    else os.environ.get("BOOM_ROOT", r"E:\Boom Project")
)

try:
    from agent import skill_utils as su
except ImportError:
    sys.path.insert(
        0,
        str(
            Path(
                os.environ.get(
                    "HERMES_HOME", r"C:\Users\Turbo\AppData\Local\hermes"
                )
            )
            / "hermes-agent"
        ),
    )
    from agent import skill_utils as su

SKIP_DIRS = {".hub", "__pycache__", ".git", ".curator_backups"}


def digest_tree(root: Path) -> dict[str, str]:
    if not root.is_dir():
        return {}
    return {
        p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in root.rglob("*")
        if p.is_file() and not SKIP_DIRS & set(p.parts)
    }


def main() -> int:
    os.environ["TERMINAL_CWD"] = str(BOOM)

    root = su.find_project_root()
    print(f"project root : {root}")
    if root is None:
        print("  not a git root -> no project tier; the profile tier is the only source")
    else:
        print(f"trusted      : {su.is_project_root_trusted(root)}")
        print(f"project dirs : {[str(d) for d in su.get_project_skills_dirs()]}")
        if not su.is_project_root_trusted(root):
            print("  UNTRUSTED -> fix with: hermes skills trust <path>")

    print("\ntiers (lowest number wins):")
    for tier, d in su.get_skill_search_roots():
        print(f"  tier{tier}  {d}")

    from tools.skills_tool import _skill_catalog

    catalog = _skill_catalog(include_hidden=True)
    loadable = [e for e in catalog if e["status"] != "shadowed"]
    print(f"\nscanned {len(catalog)}   loadable {len(loadable)}")
    print(f"  status        {dict(Counter(e['status'] for e in catalog))}")
    print(f"  loadable tier {dict(Counter(e['tier'] for e in loadable))}")

    for e in loadable:
        if e["status"] == "ambiguous":
            print(f"  AMBIGUOUS  tier{e['tier']} {e['relative_path']} -> {e['load_name']}")

    fallback = [e for e in loadable if e["tier"] != 0]
    if fallback:
        print("\nresolved below the top tier (quarantined or absent there):")
        for e in fallback:
            print(f"  tier{e['tier']}  {e['relative_path']}")

    project_dir = BOOM / ".agents" / "skills"
    a, b = digest_tree(project_dir), digest_tree(su.get_skills_dir())
    drifted = sorted(k for k in set(a) & set(b) if a[k] != b[k])
    print(f"\nproject {len(a)} files / mirror {len(b)} files")
    print(f"  drifted     : {len(drifted)} {drifted[:10]}")
    print(f"  only project: {sorted(set(a) - set(b))[:10]}")
    print(f"  only mirror : {sorted(set(b) - set(a))[:10]}")
    return 1 if drifted else 0


if __name__ == "__main__":
    raise SystemExit(main())