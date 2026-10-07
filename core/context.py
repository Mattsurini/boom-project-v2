#!/usr/bin/env python
"""
hermes.core.context — Context Manager: budgeting and loading, never dumping.

Enforces the §18 rule mechanically: you cannot load a body without paying for
it in the budget, and the budget defaults to something small enough that
preloading everything is impossible by construction.
"""
from __future__ import annotations

import os
import time
from dataclasses import dataclass, field
from typing import Any

from .registry import Registry, Descriptor

BOOM = os.environ.get("BOOM_ROOT", r"E:\Boom Project")

# A conservative chars->tokens ratio for mixed Thai/English/markdown.
CHARS_PER_TOKEN = 4

# Default ceilings. These are the enforcement, not a suggestion.
DEFAULT_MAX_CONTEXT_CHARS = 60_000      # ~15k tokens per turn
DEFAULT_MAX_SINGLE_BODY_CHARS = 20_000   # ~5k tokens for one lazy-load


@dataclass
class Loaded:
    descriptor: Descriptor
    text: str
    chars: int

    @property
    def tokens(self) -> int:
        return self.chars // CHARS_PER_TOKEN


@dataclass
class Budget:
    max_chars: int = DEFAULT_MAX_CONTEXT_CHARS
    max_single: int = DEFAULT_MAX_SINGLE_BODY_CHARS
    used: int = 0
    entries: list[str] = field(default_factory=list)
    released: list[str] = field(default_factory=list)

    @property
    def remaining(self) -> int:
        return self.max_chars - self.used

    @property
    def tokens_used(self) -> int:
        return self.used // CHARS_PER_TOKEN

    def can_afford(self, n: int) -> bool:
        return n <= self.max_single and n <= self.remaining


class ContextManager:
    """Owns what is in the working context and what was dropped from it."""

    def __init__(self, registry: Registry | None = None,
                 budget: Budget | None = None) -> None:
        self.registry = registry or Registry()
        self.budget = budget or Budget()
        self._cache: dict[str, Loaded] = {}

    # ------------------------------------------------------------------ loads
    def load(self, component_id: str, purpose: str = "") -> Loaded | None:
        """Load a body, paying for it. This is the ONLY way content enters."""
        if component_id in self._cache:
            return self._cache[component_id]
        d = self.registry.get(component_id)
        if not d or d.deprecated:
            return None
        path = d.path
        if not os.path.isfile(path):
            return None
        text = open(path, encoding="utf-8", errors="replace").read()
        n = len(text)
        if not self.budget.can_afford(n):
            self.registry.trace(component_id, "load_denied",
                                f"{n} chars > budget (single={self.budget.max_single}, "
                                f"remaining={self.budget.remaining})")
            return None
        self.budget.used += n
        self.budget.entries.append(f"{component_id} ({n}c, {purpose or 'use'})")
        self.registry.trace(component_id, "load", f"{n} chars; purpose={purpose}")
        loaded = Loaded(d, text, n)
        self._cache[component_id] = loaded
        return loaded

    def load_many(self, component_ids: list[str], purpose: str = "") -> list[Loaded]:
        return [l for l in (self.load(i, purpose) for i in component_ids) if l]

    # --------------------------------------------------------------- release
    def release(self, component_id: str) -> bool:
        """Compress-out: drop a body and return its tokens to the budget."""
        l = self._cache.pop(component_id, None)
        if not l:
            return False
        self.budget.used -= l.chars
        self.budget.released.append(component_id)
        return True

    def release_all(self) -> int:
        freed = 0
        for cid in list(self._cache):
            freed += self._cache[cid].chars
            self.release(cid)
        self.budget.used = 0
        return freed

    # ---------------------------------------------------------------- search
    def search(self, query: str, kind: str | None = None, limit: int = 5) -> list[Descriptor]:
        """SEARCH step. Names + triggers only, always."""
        return self.registry.find(query, kind=kind, limit=limit)

    # ---------------------------------------------------------------- report
    def report(self) -> str:
        b = self.budget
        return (
            f"context: {b.tokens_used} tokens used / {b.max_chars // CHARS_PER_TOKEN} "
            f"({b.remaining} chars free) | loaded={len(b.entries)} "
            f"released={len(b.released)}"
        )

    def audit(self) -> list[dict[str, Any]]:
        """Full load history — every char that entered context, and why."""
        c = self.registry
        rows = []
        for cid, action, detail, ts in c.trace_rows("load"):
            rows.append({"ts": ts, "component": cid, "action": action, "detail": detail})
        return rows


if __name__ == "__main__":
    cm = ContextManager()
    print(cm.report())