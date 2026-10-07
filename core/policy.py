#!/usr/bin/env python
"""
hermes.core.policy — Policy Engine + Decision Support (Ask JEV) gating.

The rebuild's rule (§12): Ask JEV is a Decision Support Layer, never an
unconditional tool. This module is the only place allowed to decide whether a
decision is escalated, and it decides from a declared policy — not from vibes.

Everything here is data + pure functions. No LLM calls. That is what makes the
escalation auditable after the fact.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Any

BOOM = os.environ.get("BOOM_ROOT", r"E:\Boom Project")
POLICY_PATH = os.path.join(BOOM, "config", "policy.json")


# --------------------------------------------------------------------- policy
@dataclass
class Policy:
    name: str
    description: str
    escalate_when: list[str]
    never_escalate: list[str] = field(default_factory=list)
    confidence_floor: float = 0.0


# Defaults are conservative: JEV only earns its cost on genuinely
# high-stakes, low-confidence, multi-option decisions.
DEFAULT_POLICIES: dict[str, Policy] = {
    "architecture-migration": Policy(
        name="architecture-migration",
        description="Restructuring or deleting components; hard to reverse.",
        escalate_when=[
            "options >= 3",
            "irreversible = true",
            "touches_user_data = true",
            "confidence < 0.7",
        ],
        never_escalate=["reversible = true", "scope = single_file"],
        confidence_floor=0.0,
    ),
    "external-side-effect": Policy(
        name="external-side-effect",
        description="Anything visible outside this machine.",
        escalate_when=["publish = true", "send = true", "cost > 0"],
        never_escalate=[],
        confidence_floor=0.0,
    ),
    "content-publication": Policy(
        name="content-publication",
        description="PAC / IG content going public.",
        escalate_when=["publish = true", "client_facing = true"],
        never_escalate=["draft_only = true"],
    ),
    "astrology-interpretation": Policy(
        name="astrology-interpretation",
        description="Chart reads. Interpretation is Turboz's job, not a committee's.",
        escalate_when=[],
        never_escalate=[],
        confidence_floor=-1.0,
    ),
    "routine-navigation": Policy(
        name="routine-navigation",
        description="Finding, reading, running a registered component.",
        escalate_when=[],
        never_escalate=[],
        confidence_floor=-1.0,
    ),
}

# Hard ceiling: JEV may never be invoked for these regardless of policy.
JEV_DENYLIST = {
    "astrology-interpretation", "routine-navigation", "transit-calculation",
    "file-read", "index-query",
}


@dataclass
class EscalationRequest:
    decision: str
    options: list[str] = field(default_factory=list)
    reversible: bool = True
    touches_user_data: bool = False
    publishes: bool = False
    sends: bool = False
    cost: float = 0.0
    client_facing: bool = False
    draft_only: bool = False
    scope: str = ""
    confidence: float = 1.0
    context: str = ""

    def signals(self) -> dict[str, Any]:
        return {
            "options": len(self.options),
            "irreversible": not self.reversible,
            "touches_user_data": self.touches_user_data,
            "publish": self.publishes,
            "send": self.sends,
            "cost": self.cost,
            "client_facing": self.client_facing,
            "draft_only": self.draft_only,
            "scope": self.scope,
            "confidence": self.confidence,
        }


def load_policies() -> dict[str, Policy]:
    if os.path.exists(POLICY_PATH):
        try:
            raw = json.load(open(POLICY_PATH, encoding="utf-8"))
            return {
                k: Policy(**v) for k, v in raw.get("policies", raw).items()
                if isinstance(v, dict)
            } or DEFAULT_POLICIES
        except Exception:
            return DEFAULT_POLICIES
    return DEFAULT_POLICIES


def _evaluate_condition(cond: str, sig: dict[str, Any]) -> bool:
    if ">=" in cond:
        k, v = cond.split(">=", 1)
        return float(sig.get(k.strip(), 0)) >= float(v.strip())
    if "<" in cond:
        k, v = cond.split("<", 1)
        return float(sig.get(k.strip(), 1)) < float(v.strip())
    if "=" in cond:
        k, v = cond.split("=", 1)
        k, v = k.strip(), v.strip()
        return str(sig.get(k, "")).lower() == v.lower()
    return False


@dataclass
class EscalationDecision:
    escalate: bool
    policy: str
    reason: str
    matched: list[str] = field(default_factory=list)
    blocked_by: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "escalate": self.escalate, "policy": self.policy, "reason": self.reason,
            "matched": self.matched, "blocked_by": self.blocked_by,
        }


def decide(req: EscalationRequest, policy_name: str | None = None) -> EscalationDecision:
    """Pure gate. Default: do NOT escalate. Escalation must be earned."""
    policies = load_policies()
    name = policy_name or _infer_policy(req)
    p = policies.get(name)

    if name in JEV_DENYLIST:
        return EscalationDecision(False, name, "denylisted decision class", blocked_by="jev_denylist")

    if p is None:
        return EscalationDecision(False, name or "unknown", "no policy for this decision class")

    sig = req.signals()
    matched = [c for c in p.escalate_when if _evaluate_condition(c, sig)]

    # An explicit exemption wins over a match.
    for c in p.never_escalate:
        if _evaluate_condition(c, sig):
            return EscalationDecision(False, name, f"exempt: {c}", matched, blocked_by=c)

    if req.confidence > p.confidence_floor and not matched:
        return EscalationDecision(False, name, "confidence sufficient and no trigger fired")

    if matched:
        return EscalationDecision(True, name, f"triggers: {', '.join(matched)}", matched)

    return EscalationDecision(False, name, "no trigger fired")


ASTROLOGY_HINTS = ("chart", "natal", "transit", "synastry", "horary", "dashaa",
                   "tarot", "ashtakavarga", "prashna", "auspicious", "muhurta")
DATA_HINTS = ("delete", "remove", "migrate", "rename", "restructure", "drop",
              "rewrite", "teardown", "rebuild")


def _infer_policy(req: EscalationRequest) -> str:
    """Route a request to the policy that actually governs it.

    Precedence matters: a denylisted class must never win over a real trigger,
    so cheap reversible navigation is checked LAST, not first.
    """
    text = (req.decision + " " + req.context).lower()

    if any(h in text for h in ASTROLOGY_HINTS):
        return "astrology-interpretation"

    if req.publishes or req.client_facing or req.draft_only:
        return "content-publication"
    if req.sends or req.cost > 0:
        return "external-side-effect"

    # Low confidence alone is a trigger, so it must route to a non-denylisted
    # policy — otherwise the `confidence < 0.7` rule is dead code.
    if (req.touches_user_data or not req.reversible or len(req.options) >= 3
            or req.confidence < 0.7 or any(h in text for h in DATA_HINTS)):
        return "architecture-migration"

    return "routine-navigation"


def explain() -> str:
    """Human-readable policy dump for auditing. Used by `core/policy.py explain`."""
    pol = load_policies()
    lines = ["JEV DECISION SUPPORT POLICY", "=" * 60]
    for name, p in sorted(pol.items()):
        flag = "DENYLISTED" if name in JEV_DENYLIST else "active"
        lines.append(f"\n[{name}] ({flag})")
        lines.append(f"  purpose : {p.description}")
        if p.escalate_when:
            lines.append(f"  escalate: {', '.join(p.escalate_when)}")
        if p.never_escalate:
            lines.append(f"  exempt  : {', '.join(p.never_escalate)}")
    lines.append(f"\ndenylist: {', '.join(sorted(JEV_DENYLIST))}")
    lines.append("default: NEVER escalate. Triggers must fire.")
    return "\n".join(lines)


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "explain":
        print(explain())
    elif len(sys.argv) > 1 and sys.argv[1] == "test":
        cases = [
            EscalationRequest("run transit script"),                        # routine
            EscalationRequest("interpret natal chart"),                     # astrology
            EscalationRequest("delete skills root", reversible=False,
                              options=["a", "b", "c"]),                      # migrate
            EscalationRequest("post PAC caption", publishes=True,
                              draft_only=True),                             # exempt
            EscalationRequest("publish PAC", publishes=True),              # escalate
            EscalationRequest("pick routing option", options=["x", "y"],
                              confidence=0.4),                              # low conf
        ]
        for c in cases:
            d = decide(c)
            print(f"{'JEV' if d.escalate else 'no '}  {c.decision:34} "
                  f"[{d.policy:24}] {d.reason}")
    else:
        print("usage: policy.py explain | test")