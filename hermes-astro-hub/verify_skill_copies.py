#!/usr/bin/env python3
"""
verify_skill_copies.py — health-check the canonical horary-astrology skill.

History: this file was `sync_skill_copies.py`. It synced a copy of the
horary-astrology skill that lived at

    E:\\Boom Project\\hermes-astro-hub\\skills\\horary-astrology

That copy no longer exists — the profile skill is now the single canonical
copy, and the sync was a no-op that reported every managed file as
`[MISSING] ... skipped` while still exiting 0. A stale second copy is worse
than none, because edits made to one side silently diverge.

This version verifies instead of syncing:

  1. the canonical copy exists and is complete (no missing managed files);
  2. the hub actually provides every module the skill imports;
  3. the interpreter that can run the Hub is the one documented;
  4. each horary script executes end-to-end and reports its orb system.

Exit 0 = healthy. Exit 1 = at least one check failed.

Run:
    %LOCALAPPDATA%\\hermes\\hermes-agent\\venv\\Scripts\\python.exe verify_skill_copies.py
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

# Canonical skill location. The profile is the ONLY live copy.
PROFILE = Path(os.environ.get("LOCALAPPDATA", r"C:\Users\Turbo\AppData\Local")) \
    / "hermes" / "skills" / "horary-astrology"

HERMES_VENV = Path(os.environ.get("LOCALAPPDATA", r"C:\Users\Turbo\AppData\Local")) \
    / "hermes" / "hermes-agent" / "venv" / "Scripts" / "python.exe"

MANAGED = [
    "SKILL.md",
    "scripts/horary_chart.py",
    "scripts/horary_2nd_q.py",
    "scripts/voc_time.py",
]

# Hub modules the skill imports. If these move, this check fails loudly.
HUB_EXPORTS = [
    "all_positions", "jd_utc", "sign_index", "moon_voc_status",
    "check_aspect", "check_aspect_with_speed", "houses", "dignity",
    "ruler_of", "TRAD7", "OUTER3", "ORB_SYSTEM", "set_orb_system",
    "orb_allowance", "ALL_ORBS",
]

failures: list[str] = []


def ok(msg: str) -> None:
    print(f"  [OK]   {msg}")


def bad(msg: str) -> None:
    print(f"  [FAIL] {msg}")
    failures.append(msg)


def check_managed_files() -> None:
    print("\n1. canonical copy is complete")
    if not PROFILE.is_dir():
        bad(f"canonical skill dir missing: {PROFILE}")
        return
    ok(f"canonical skill dir: {PROFILE}")
    for rel in MANAGED:
        p = PROFILE / rel
        if p.is_file() and p.stat().st_size > 0:
            ok(f"{rel} ({p.stat().st_size} bytes)")
        else:
            bad(f"{rel} missing or empty")


def check_no_stale_duplicate() -> None:
    print("\n2. no stale second copy of the skill")
    hub_copy = Path(r"E:\Boom Project\hermes-astro-hub\skills\horary-astrology")
    if hub_copy.exists():
        bad(f"stale duplicate exists at {hub_copy} — resolve the divergence "
            f"and delete it, or the two will drift")
    else:
        ok("no duplicate under hermes-astro-hub/skills/")


def check_hub_exports() -> None:
    print("\n3. Hub exposes every symbol the skill imports")
    if not HERMES_VENV.is_file():
        bad(f"Hermes venv interpreter missing: {HERMES_VENV}")
        return
    code = ("import hermes_astro as h;"
            "missing=[n for n in %r if not hasattr(h,n)];"
            "print('MISSING:'+','.join(missing) if missing else 'ALL_OK')"
            % (HUB_EXPORTS,))
    r = subprocess.run([str(HERMES_VENV), "-c", code],
                       capture_output=True, text=True)
    out = (r.stdout or "").strip()
    if r.returncode != 0:
        bad(f"cannot import hermes_astro from {HERMES_VENV}: "
            f"{(r.stderr or '').strip().splitlines()[-1:]}")
    elif out == "ALL_OK":
        ok(f"all {len(HUB_EXPORTS)} symbols present "
           f"(engine+orb system importable)")
    else:
        bad(out)


def check_scripts_run() -> None:
    print("\n4. horary scripts execute end-to-end")
    if not HERMES_VENV.is_file():
        return
    cases = [
        ("horary_chart.py", ["2026-09-08", "21:53"]),
        ("horary_2nd_q.py", []),
        ("voc_time.py", ["2026-09-08", "21:53", "19.91", "99.83"]),
    ]
    for name, args in cases:
        script = PROFILE / "scripts" / name
        if not script.is_file():
            bad(f"{name} not found")
            continue
        r = subprocess.run([str(HERMES_VENV), str(script), *args],
                           capture_output=True, text=True,
                           encoding="utf-8", errors="replace")
        if r.returncode != 0:
            tail = (r.stderr or "").strip().splitlines()[-1:]
            bad(f"{name} exited {r.returncode}: {tail}")
            continue
        if "orbs [" not in r.stdout:
            bad(f"{name} ran but did not report its orb system")
            continue
        line = [ln for ln in r.stdout.splitlines() if "hermes_astro v" in ln]
        ok(f"{name}: {line[-1].strip() if line else 'ran'}")


def main() -> int:
    print("=" * 66)
    print("verify_skill_copies — canonical horary-astrology skill health check")
    print(f"canonical: {PROFILE}")
    print(f"python   : {HERMES_VENV}")
    print("=" * 66)

    check_managed_files()
    check_no_stale_duplicate()
    check_hub_exports()
    check_scripts_run()

    print("\n" + "=" * 66)
    if failures:
        print(f"UNHEALTHY — {len(failures)} check(s) failed:")
        for f in failures:
            print(f"  - {f}")
        return 1
    print("HEALTHY — all checks passed.")
    print("Note: the profile copy is canonical. Do not reintroduce a second "
          "copy;\n      if you need a backup, version it, don't fork it.")
    return 0


if __name__ == "__main__":
    sys.exit(main())