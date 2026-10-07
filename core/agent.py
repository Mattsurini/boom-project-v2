#!/usr/bin/env python
"""
hermes.core.agent — Agent Manager.

Hermes is the orchestrator. Sub-agents are specialist workers with isolated
context that return COMPACT findings (§19).

The contract that keeps tokens in check:
  * A worker never returns raw context. It returns Finding / Files / Evidence /
    Confidence, or nothing.
  * Delegation is only worth it when expected context saved > delegation
    overhead. That threshold is explicit here, not vibes.
  * Overlapping agents are merged, not duplicated. One agent, one responsibility.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field, asdict
from typing import Any

from .registry import Registry, Descriptor

BOOM = os.environ.get("BOOM_ROOT", r"E:\Boom Project")

# A worker is only worth spawning if the context it absorbs exceeds this.
DELEGATION_OVERHEAD_TOKENS = 1_500
WORTH_DELEGATING_TOKENS = 3_000

# The only shape a worker may return. Enforced by validate_finding().
FINDING_SCHEMA = {
    "finding": "1-3 sentences",
    "files": ["paths touched"],
    "symbol_or_section": "where in those files",
    "evidence": "quoted or measured proof",
    "confidence": "high | medium | low",
}

VALID_CONFIDENCE = {"high", "medium", "low"}


@dataclass
class AgentSpec:
    id: str
    role: str
    responsibilities: list[str]
    output_stage: str
    tags: list[str] = field(default_factory=list)
    merged_from: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class DelegationDecision:
    delegate: bool
    reason: str
    estimated_context_tokens: int
    overhead_tokens: int = DELEGATION_OVERHEAD_TOKENS

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def should_delegate(context_tokens: int, tasks: int = 1,
                   independent: bool = False) -> DelegationDecision:
    """Decide delegation from measured context, not from preference."""
    if context_tokens >= WORTH_DELEGATING_TOKENS:
        return DelegationDecision(True,
            f"{context_tokens} tokens absorbed > overhead "
            f"{DELEGATION_OVERHEAD_TOKENS}", context_tokens)
    if tasks >= 3 and independent:
        return DelegationDecision(True,
            f"{tasks} independent workstreams worth parallelising",
            context_tokens)
    return DelegationDecision(False,
        f"{context_tokens} tokens fits in context (< {WORTH_DELEGATING_TOKENS}) — "
        f"delegating would cost more than it saves", context_tokens)


def validate_finding(f: dict[str, Any]) -> tuple[bool, str]:
    """Reject raw-context returns. This is the isolation guarantee."""
    problems = []
    missing = [k for k in FINDING_SCHEMA if k not in f]
    if missing:
        problems.append(f"missing keys: {missing}")
    if f.get("confidence") not in VALID_CONFIDENCE:
        problems.append(f"confidence must be one of {sorted(VALID_CONFIDENCE)}")
    finding = str(f.get("finding", ""))
    if len(finding) > 800:
        problems.append(f"finding is {len(finding)} chars — return a finding, not a dump")
    ev = str(f.get("evidence", ""))
    if len(ev) > 1500:
        problems.append(f"evidence is {len(ev)} chars — quote the minimum")
    blob = json.dumps(f, default=str)
    for bad_key in ("messages", "raw", "dump", "transcript", "full_context"):
        if bad_key in f:
            problems.append(f"raw payload key '{bad_key}' — isolation violated")
    if len(blob) > 4000:
        problems.append(f"return is {len(blob)} chars (cap 4000)")
    return (not problems, "; ".join(problems) if problems else "compact and schema-valid")


def worker_prompt(goal: str, context: str, scope: str, output_format: str | None = None) -> str:
    """The only prompt template workers get. Keeps prompts identical and small."""
    fmt = output_format or (
        "Return EXACTLY: Finding (1-3 sentences), Files, Symbol/Section, "
        "Evidence, Confidence. No raw context, no file dumps.")
    return (
        f"GOAL: {goal}\n\n"
        f"CONTEXT: {context}\n\n"
        f"SCOPE: {scope}\n\n"
        f"OUTPUT: {fmt}\n"
        f"Do not return raw source. Do not speculate. If you cannot find it, say so."
    )


class AgentManager:
    def __init__(self, registry: Registry | None = None) -> None:
        self.registry = registry or Registry()
        self.config_path = os.path.join(BOOM, "config", "agents.json")

    # ------------------------------------------------------------- catalogue
    def load_agents(self) -> dict[str, AgentSpec]:
        if not os.path.exists(self.config_path):
            return {}
        raw = json.load(open(self.config_path, encoding="utf-8"))
        return {k: AgentSpec(**v) for k, v in raw.get("agents", raw).items()}

    def publish(self) -> int:
        n = 0
        for spec in self.load_agents().values():
            trig = spec.role + ("; " + ", ".join(spec.responsibilities[:2])
                                if spec.responsibilities else "")
            self.registry.register(Descriptor(
                id=f"agent:{spec.id}", kind="agent", title=spec.id,
                trigger=trig[:300], path=self.config_path,
                tags=tuple(spec.tags + ["agent"]), cost=2,
            ))
            n += 1
        return n

    # Generic vocabulary that says nothing about domain. Two agents sharing
    # only these words have NOT overlapping responsibility.
    _GENERIC = {
        "research", "analysis", "extraction", "technical", "specialist",
        "assistant", "review", "work", "support", "build", "building",
        "finding", "reporting", "data", "content", "project", "and", "of",
        "the", "from", "with", "to", "for",
    }

    def overlaps(self) -> list[tuple[str, str, str]]:
        """Find agents whose responsibilities collide — the duplicate-agent debt.

        Compares domain vocabulary, ignoring generic nouns. Without the stop
        list this reports false overlaps on words like "research" and
        "extraction" that appear in every domain.
        """
        specs = self.load_agents()
        out = []
        ids = sorted(specs)
        for i, a in enumerate(ids):
            for b in ids[i + 1:]:
                sa = {w.lower() for r in specs[a].responsibilities
                      for w in r.split()} - self._GENERIC
                sb = {w.lower() for r in specs[b].responsibilities
                      for w in r.split()} - self._GENERIC
                inter = sa & sb
                if len(inter) >= 2:
                    out.append((a, b, ", ".join(sorted(inter)[:4])))
        return out

    def plan(self, goal: str, context_tokens: int = 0, tasks: int = 1,
             independent: bool = False) -> dict[str, Any]:
        d = should_delegate(context_tokens, tasks, independent)
        cands = self.registry.find(goal, kind="agent", limit=3)
        return {
            "goal": goal,
            "delegation": d.to_dict(),
            "candidates": [c.to_dict() for c in cands],
            "contract": FINDING_SCHEMA,
        }


if __name__ == "__main__":
    import sys

    am = AgentManager()
    if len(sys.argv) > 1 and sys.argv[1] == "overlaps":
        for a, b, w in am.overlaps():
            print(f"OVERLAP {a} <-> {b}: {w}")
        print("(empty = no duplicated responsibility)")
    else:
        print(json.dumps(am.plan(" ".join(sys.argv[1:]) or "generic task",
                                 context_tokens=50_000), indent=2))