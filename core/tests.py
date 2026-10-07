#!/usr/bin/env python
"""
Routing regression tests — the rebuild's acceptance suite.

These encode MEASURED behaviour, not aspirations. Run after any change to
core/skill.py ROUTE_ALIASES or core/router.py scoring.

    python -m core.tests                 # summary
    python -m core.tests --verbose       # per-case

A new ambiguity discovered in use belongs here as a case, so routing quality
is a tracked number instead of a gut feeling.
"""
from __future__ import annotations

import sys

# (request, expected primary)
CASES: list[tuple[str, str]] = [
    ("who are you", "turboz"),
    ("what is the moon doing today", "daily-transit"),
    ("publish a PAC caption for instagram", "pac-transit-timing"),
    ("interpret my natal chart", "astro-natal-chart"),
    ("draw me a tarot spread", "tarot-reading"),
    ("run the transit timeline script", "daily-transit"),
    ("rebuild the output index", "boom-project"),
    ("plan my day", "Ekae"),
    ("what does the classical text say about dashaa", "astro-knowledge-db"),
    ("when should I post the transit reading", "daily-transit"),
    ("run a horary chart for my question", "horary-astrology"),
    ("research the connection between ML and astrology", "research-deep"),
    ("search the web for jupiter ephemeris", "web-search-agent"),
    ("run a full research pipeline", "astro-pipeline"),
    ("write a post mortem for the outage", "boom-post-mortem"),
    ("fix this bug", "boom-debug-mantra"),
    ("synastry with my partner", "astro-synastry"),
    ("calculate a divisional chart", "astro-natal-chart"),
    # formerly ambiguous — resolved by merging astro-agent-* into astro-pipeline,
    # chinese-almanac-scraper into boom-chinese-almanac, and tightening aliases
    ("critique my plan", "boom-scrutinize"),
    ("fetch the Chinese almanac for today", "boom-chinese-almanac"),
    ("which skill should I use for this", "boom-router"),
    ("organise the output files", "boom-project"),
    # core-operations cases
    ("operate the boom core router", "boom-core-rebuild"),
    ("why is routing picking the wrong skill", "boom-core-rebuild"),
    ("a skill is duplicated", "boom-core-rebuild"),
    ("what is the moon doing today", "daily-transit"),
    # Thai requests — FTS5 tokenises a whole Thai run as ONE token, so these
    # only ever route through Router._substring_candidates(). BooM writes in
    # Thai, so this is the common case, not an edge case.
    ("สีเสื้อมงคลวันนี้ ใส่เสื้อสีอะไรดี", "lucky-colors-taksah"),
    ("สีกาลกิณีของคนเกิดวันพุธ", "lucky-colors-taksah"),
]

# Requests where two components genuinely compete and the merge has not been
# decided yet. Documented rather than hidden.
KNOWN_AMBIGUOUS: list[tuple[str, str, str]] = []


def run(verbose: bool = False) -> tuple[int, int]:
    from .router import Router

    r = Router()
    passed = 0
    for q, want in CASES:
        rt = r.route(q)
        got = rt.primary.id if rt.primary else None
        ok = got == want
        passed += ok
        if verbose or not ok:
            print(f"{'OK  ' if ok else 'FAIL'} {q[:46]:48} -> {got}")
    print()
    print("KNOWN AMBIGUOUS (merge to resolve):")
    for q, want, rival in KNOWN_AMBIGUOUS:
        got = r.route(q).primary.id if r.route(q).primary else None
        hit = want if got == want else (rival if got == rival else got)
        mark = "resolved" if got == want else "OPEN   "
        print(f"  {mark} {q[:44]:46} -> {got}")
    return passed, len(CASES)


def main() -> int:
    passed, total = run(verbose="--verbose" in sys.argv)
    print()
    print(f"routing accuracy: {passed}/{total} "
          f"({passed/total*100:.0f}%) on unambiguous cases")
    return 0 if passed == total else 1


if __name__ == "__main__":
    raise SystemExit(main())