#!/usr/bin/env python
"""
hermes.core.router — Route a request to the cheapest sufficient capability.

Token contract (§18): never preload. The router receives a short request and
returns ONE primary component plus at most `budget` secondary ones, each with
an explicit token cost. It never returns a body.

The router is deterministic and explainable: `explain()` shows why a component
was chosen, which is what makes routing auditable instead of magical.
"""
from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from typing import Any

from .registry import Registry, Descriptor
from .policy import EscalationRequest, decide as policy_decide, EscalationDecision

BOOM = os.environ.get("BOOM_ROOT", r"E:\Boom Project")

# cost tiers
FREE, LAZY, DELEGATE = 0, 1, 2


@dataclass
class Route:
    primary: Descriptor | None
    secondaries: list[Descriptor] = field(default_factory=list)
    escalation: EscalationDecision | None = None
    notes: list[str] = field(default_factory=list)

    @property
    def total_cost(self) -> int:
        return (self.primary.cost if self.primary else 0) + sum(d.cost for d in self.secondaries)

    def to_dict(self) -> dict[str, Any]:
        return {
            "primary": self.primary.to_dict() if self.primary else None,
            "secondaries": [d.to_dict() for d in self.secondaries],
            "total_cost": self.total_cost,
            "escalation": self.escalation.to_dict() if self.escalation else None,
            "notes": self.notes,
        }


class Router:
    def __init__(self, registry: Registry | None = None) -> None:
        self.registry = registry or Registry()

    def route(
        self,
        request: str,
        budget: int = 2,
        context: str = "",
        **decision_signals: Any,
    ) -> Route:
        """Route a request. `budget` caps how many skills may be lazy-loaded."""
        notes: list[str] = []

        # 1. Policy gate runs first: an escalation changes the whole plan.
        escalation = None
        if decision_signals:
            escalation = policy_decide(
                EscalationRequest(decision=request, context=context, **decision_signals)
            )
            if escalation.escalate:
                notes.append(f"JEV required: {escalation.reason}")

        # 2. Cheap keyword pass to build a candidate set.
        #    Each keyword retrieves independently; a low-ranked hit on an early
        #    keyword must not be excluded, so the cap is per-keyword and the
        #    union is de-duplicated before scoring.
        keywords = self._keywords(request)
        cands: dict[str, Descriptor] = {}
        for kw in keywords:
            for d in self.registry.find(kw, limit=6):
                cands.setdefault(d.id, d)
        if not cands:
            for d in self.registry.find(request, limit=8):
                cands.setdefault(d.id, d)
        if not cands:
            cands = self._substring_candidates(request)

        # 3. Score. Deliberately boring and inspectable.
        #    Skills are methodology and should win ties against raw scripts:
        #    the skill knows when a script is the right execution.
        scored = [(self._score(request, d), d) for d in cands.values()]
        scored = [(s, d) for s, d in scored if s > 0]
        scored.sort(key=lambda x: (-(x[0] + self._kind_bonus(x[1])), x[1].id))

        if not scored:
            return Route(None, [], escalation,
                         notes + ["no registered component matched — ask, do not guess"])

        primary = scored[0][1]
        notes.append(f"primary={primary.id} (score {scored[0][0]:.1f})")

        # 4. Secondaries are capped by budget AND by cost discipline: never
        # stack two DELEGATE components for one request.
        seconds: list[Descriptor] = []
        for s, d in scored[1:]:
            if len(seconds) >= budget:
                break
            if d.cost >= DELEGATE and any(x.cost >= DELEGATE for x in seconds):
                continue
            if s < 1:
                continue
            seconds.append(d)
        if seconds:
            notes.append("secondary=" + ", ".join(d.id for d in seconds))

        return Route(primary, seconds, escalation, notes)

    def explain(self, request: str, **kw: Any) -> str:
        r = self.route(request, **kw)
        lines = [f"REQUEST: {request[:100]}", "-" * 58]
        if r.primary:
            lines.append(f"PRIMARY  [{r.primary.kind}] {r.primary.id}")
            lines.append(f"         {r.primary.trigger[:100]}")
            lines.append(f"         cost={r.primary.cost} path={r.primary.path}")
        for d in r.secondaries:
            lines.append(f"SECOND   [{d.kind}] {d.id} (cost={d.cost})")
        if r.escalation:
            e = "JEV" if r.escalation.escalate else "no-JEV"
            lines.append(f"POLICY   {e}: {r.escalation.reason}")
        lines.append(f"TOTAL COST {r.total_cost}")
        lines += [f"NOTE  {n}" for n in r.notes]
        return "\n".join(lines)

    # ------------------------------------------------------------- internals
    _STOP = {
        "the", "a", "an", "for", "to", "of", "and", "or", "in", "on", "with",
        "please", "can", "you", "do", "is", "it", "my", "me", "i", "run", "make",
    }

    def _keywords(self, request: str) -> list[str]:
        toks = re.findall(r"[A-Za-z_][A-Za-z0-9_\-]{2,}", request.lower())
        out: list[str] = []
        for t in toks:
            if t in self._STOP:
                continue
            out.append(t)
            # split compound identifiers: transit_timeline -> transit, timeline
            if "_" in t or "-" in t:
                out.extend(p for p in re.split(r"[_\-]", t) if len(p) > 2)
        # dedupe, preserve order, cap the fan-out
        seen, uniq = set(), []
        for t in out:
            if t not in seen:
                seen.add(t)
                uniq.append(t)
        return uniq[:12]

    def _substring_candidates(self, request: str) -> dict[str, Descriptor]:
        """Last-resort candidate pass for requests FTS cannot tokenise.

        FTS5 tokenises a run of Thai (or CJK) letters as ONE token, so a real
        request — "สีเสื้อมงคลวันนี้ ใส่เสื้อสีอะไรดี" — never matches the indexed
        token "สีเสื้อมงคล" and the router answers "no match" for the language
        BooM actually writes in. Substring-match the curated aliases instead:
        `_score()` already does alias substring matching, it just never got a
        candidate to score.
        """
        text = request.lower()
        hits: dict[str, Descriptor] = {}
        for d in self.registry.all():
            if any(a and len(a) >= 3 and a.lower() in text for a in d.aliases):
                hits.setdefault(d.id, d)
        return hits

    @staticmethod
    def _kind_bonus(d: Descriptor) -> float:
        """Tie-break preference: methodology before raw execution.

        A skill knows WHEN a script is the right execution and which of four
        overlapping scripts to use; a bare script name match does not. So when
        scores tie, the skill must win — otherwise "rebuild the output index"
        routes to whichever of four index scripts matched the name token first.
        """
        return {"skill": 2.5, "agent": 1.0, "script": 0.0, "project": 0.0, "mcp": 0.0}.get(d.kind, 0.0)

    def _score(self, request: str, d: Descriptor) -> float:
        # Multi-word aliases must match as phrases; keyword bags create false hits.
        text = (request + " " + " ".join(d.tags)).lower()
        name = d.id.lower()

        # 1. Explicit alias match — highest confidence signal.
        #    A phrase alias matches on substring OR on its significant words
        #    appearing in any order, so "rebuild the output index" still hits
        #    the alias "rebuild index" (filler words between them).
        s = 0.0
        alias_exact = 0
        for a in d.aliases:
            if not a:
                continue
            if a in text:
                s += 8.0
                alias_exact += 1
                continue
            words = [w for w in re.findall(r"[a-z0-9]+", a.lower()) if len(w) > 2]
            if words and all(w in text for w in words):
                s += 6.0 * (len(words) / max(len(words), 1))
                s -= 0.5  # slightly below an exact phrase hit

        # An exact multi-word alias phrase is a deliberate, specific claim on
        # this request. It must beat a generic name-token match, which is what
        # put skill-creator above boom-router for "which skill should i use"
        # (its name contains the bare word "skill").
        if alias_exact and len(max(d.aliases, key=len).split()) >= 3:
            s += 3.0

        # 2. Skill name tokens.
        for tok in name.replace("-", "_").split("_"):
            if len(tok) > 2 and tok in text:
                s += 3
        for tok in name.split("-"):
            if len(tok) > 2 and tok in text:
                s += 3
        for tag in d.tags:
            if tag.lower() in text:
                s += 1.5
        if d.title and d.title.lower() in text:
            s += 2
        # 3. Trigger words are weak — the description is documentation-flavoured.
        for w in re.findall(r"[a-z]{4,}", d.trigger.lower()):
            if w in text:
                s += 0.5
        return s


if __name__ == "__main__":
    import sys

    r = Router()
    if len(sys.argv) > 1:
        print(r.explain(" ".join(sys.argv[1:])))
    else:
        print("usage: python -m core.router <request>")