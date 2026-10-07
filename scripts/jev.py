#!/usr/bin/env python3
"""
jev.py — typed decisions from TypeSafe Jev (System One) via Pollinations.

Jev is a decision engine, not a writer: you post a `state` plus typed
`questions` (noul / choice / score) and get calibrated answers back.
This is the Boom-side bridge for HERMES_ORCHESTRATOR.md §5–§12 and §27.

Usage (muscle memory):
  python scripts/jev.py noul   --state "ขอไพ่ทาโรต์ 1 ใบ" --instructions "เป็นคำขอไพ่ทาโรต์หรือไม่"
  python scripts/jev.py choice --state-file state.json --instructions "เลือก workflow" \
                               --option tarot_pick_a_card="จั่วไพ่ 1 ใบ" --option tarot_general="อ่านภาพรวม"
  python scripts/jev.py score  --state "..." --instructions "เร่งด่วนแค่ไหน" \
                               --level low --level normal --level high
  python scripts/jev.py ask --file request.json      # raw state+questions (batching, §10)
  cat request.json | python scripts/jev.py ask -     # raw JSON from stdin

Flags:
  --model typesafe/jev-1.13 (alias `jev`)   --endpoint https://gen.pollinations.ai/alpha/decisions
  --timeout 60   --threshold 0.7 (noul gate → exit 1 when below)   --raw (untouched response)   --no-retry

Key resolution (the key is never printed): $POLLINATIONS_API_KEY, $POLLINATIONS_KEY,
  then E:/Boom Project/.env, then the Hermes .env.

Exit: 0 ok · 1 noul below --threshold · 2 usage/config · 3 HTTP error · 4 retries exhausted
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENDPOINT = "https://gen.pollinations.ai/alpha/decisions"
MODEL = "typesafe/jev-1.13"
ENV_FILES = [ROOT / ".env", Path.home() / "AppData/Local/hermes/.env"]
RETRYABLE = {429, 502, 503, 504}


def die(msg: str, code: int = 2) -> None:
    print(f"jev.py: {msg}", file=sys.stderr)
    raise SystemExit(code)


def resolve_key() -> str:
    for var in ("POLLINATIONS_API_KEY", "POLLINATIONS_KEY"):
        v = os.environ.get(var)
        if v:
            return v.strip()
    for path in ENV_FILES:
        try:
            for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
                line = line.strip()
                if line.startswith("#") or "=" not in line:
                    continue
                k, _, v = line.partition("=")
                if k.strip() in ("POLLINATIONS_API_KEY", "POLLINATIONS_KEY"):
                    v = v.strip().strip('"').strip("'")
                    if v:
                        return v
        except OSError:
            continue
    die("no Pollinations key found (POLLINATIONS_API_KEY / POLLINATIONS_KEY in env or .env)")


def post(endpoint: str, payload: dict, key: str, timeout: float, retry: bool) -> dict:
    body = json.dumps(payload).encode()
    attempts = 3 if retry else 1
    for attempt in range(1, attempts + 1):
        req = urllib.request.Request(
            endpoint, data=body,
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            detail = e.read().decode(errors="ignore")[:400]
            if e.code in RETRYABLE:
                if attempt < attempts:
                    time.sleep(2 ** (attempt - 1))
                    continue
                die(f"HTTP {e.code} [retryable, exhausted] {detail}", 4)
            die(f"HTTP {e.code} [non-retryable] {detail}", 3)
        except (urllib.error.URLError, TimeoutError) as e:
            if attempt < attempts:
                time.sleep(2 ** (attempt - 1))
                continue
            die(f"transport error {e}", 4)
    die("unreachable", 4)


def build_questions(a) -> dict:
    if a.cmd == "noul":
        return {a.name: {"type": "noul", "instructions": a.instructions}}
    if a.cmd == "choice":
        if not a.option:
            die("choice needs at least one --option key=description (Jev rejects an empty criteria map "
                "with HTTP 400)")
        criteria = {}
        for spec in a.option:
            if "=" not in spec:
                die(f"--option must be key=description, got {spec!r}")
            k, _, v = spec.partition("=")
            criteria[k.strip()] = v.strip()
        return {a.name: {"type": "choice", "instructions": a.instructions, "criteria": criteria}}
    if a.cmd == "score":
        if not (2 <= len(a.level) <= 10):
            die("score needs 2–10 --level flags, ordered low → high")
        return {a.name: {"type": "score", "instructions": a.instructions, "criteria": list(a.level)}}
    raise AssertionError(a.cmd)


def load_state(a) -> object:
    if a.state_file:
        return json.loads(Path(a.state_file).read_text(encoding="utf-8"))
    if a.state is None:
        die("give --state <text> or --state-file <json>")
    return a.state


def main() -> int:
    p = argparse.ArgumentParser(description="Typed Jev decisions via Pollinations (HERMES_ORCHESTRATOR.md §5–§12)")
    p.add_argument("cmd", choices=["noul", "choice", "score", "ask"])
    p.add_argument("--state", help="state as plain text")
    p.add_argument("--state-file", help="state as a JSON file (object or text)")
    p.add_argument("--instructions", default="", help="the question, in words")
    p.add_argument("--name", default="q1", help="question key in the answers map")
    p.add_argument("--option", action="append", default=[], metavar="KEY=DESC", help="choice option (repeatable)")
    p.add_argument("--level", action="append", default=[], help="score level, low → high (repeatable)")
    p.add_argument("--file", help="ask: raw request JSON file ('-' = stdin)")
    p.add_argument("--model", default=MODEL)
    p.add_argument("--endpoint", default=ENDPOINT)
    p.add_argument("--timeout", type=float, default=60.0)
    p.add_argument("--threshold", type=float, help="noul gate: exit 1 when the probability is below this")
    p.add_argument("--raw", action="store_true", help="print the untouched response")
    p.add_argument("--no-retry", action="store_true", help="single attempt, no backoff (§27)")
    a = p.parse_args()

    if a.cmd == "ask":
        if not a.file:
            die("ask needs --file <request.json> or --file -")
        raw = sys.stdin.read() if a.file == "-" else Path(a.file).read_text(encoding="utf-8")
        payload = json.loads(raw)
        payload.setdefault("model", a.model)
        if not payload.get("questions"):
            die("request JSON needs a non-empty `questions` map")
    else:
        payload = {"model": a.model, "state": load_state(a), "questions": build_questions(a)}

    resp = post(a.endpoint, payload, resolve_key(), a.timeout, not a.no_retry)
    if a.raw:
        print(json.dumps(resp, ensure_ascii=False))
    else:
        print(json.dumps({"answers": resp.get("answers"), "usage": resp.get("usage"),
                          "model": resp.get("model"), "id": resp.get("id")}, ensure_ascii=False, indent=1))

    if a.threshold is not None and a.cmd in ("noul", "ask"):
        ans = (resp.get("answers") or {}).get(a.name if a.cmd == "noul" else next(iter(resp.get("answers") or {}), ""), {})
        prob = ans.get("noul") if isinstance(ans, dict) else None
        if isinstance(prob, (int, float)) and prob < a.threshold:
            print(f"jev.py: noul {prob} < threshold {a.threshold}", file=sys.stderr)
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
