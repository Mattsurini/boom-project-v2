"""
hermes.core — the rebuild's clean core.

Nine components, one responsibility each. Import the one you need; the package
imports nothing heavy, so importing this stays cheap.

    registry   discovery          single index of everything that exists
    router     orchestration      request -> cheapest sufficient component
    policy     decision support   when Ask JEV earns its cost
    context    token control      budgeted load / release, never preload
    project    context boundary   scope resolution and write containment
    memory     memory manager     Notes = truth, index = retrieval
    skill      skill manager      methodology catalogue, lazy-load only
    script     script registry    execution layer, registry-discovered
    agent      agent manager      specialist workers, isolated context
    validator  validation         named criteria, evidence, no optimism
"""
from __future__ import annotations

__all__ = [
    "registry", "router", "policy", "context", "project",
    "memory", "skill", "script", "agent", "validator",
]

__version__ = "1.0.0-rebuild"