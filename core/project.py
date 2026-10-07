#!/usr/bin/env python
"""
hermes.core.project — Project as Context Boundary.

A project is not a folder. It is a scope: everything inside it is addressable
by ID from everywhere else, so content is referenced, never copied (§16).
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Any

from .registry import Registry

BOOM = os.environ.get("BOOM_ROOT", r"E:\Boom Project")

# Canonical Output folders. Stage alias folders are forbidden by project rule.
CANONICAL_STAGES = (
    "Plawan", "Nut", "CK", "Arm", "Nan", "Bella", "Sandee", "Ekae",
    "PAC", "Transit", "Sources",
)


@dataclass
class Project:
    id: str
    title: str
    root: str
    description: str
    mounts: dict[str, str] = field(default_factory=dict)
    rules: list[str] = field(default_factory=list)

    def path(self, *parts: str) -> str:
        return os.path.join(self.root, *parts)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id, "title": self.title, "root": self.root,
            "description": self.description, "mounts": self.mounts,
            "rules": self.rules,
        }


class ProjectManager:
    """Resolves a request's project scope and rejects out-of-boundary writes."""

    def __init__(self, registry: Registry | None = None) -> None:
        self.registry = registry or Registry()
        self.config_path = os.path.join(BOOM, "config", "projects.json")
        self._projects: dict[str, Project] = {}
        self._load()

    def _load(self) -> None:
        data = {}
        if os.path.exists(self.config_path):
            try:
                data = json.load(open(self.config_path, encoding="utf-8"))
            except Exception:
                data = {}
        if not data:
            data = {"boom": {
                "title": "Boom Project",
                "root": BOOM,
                "description": "BooM's astrology + research + content workspace.",
                "mounts": {
                    "knowledge": "Knowledge", "output": "Output",
                    "scripts": "scripts", "skills": "skills", "wiki": "Knowledge/indexes",
                    "core": "core", "registry": "cache/registry.sqlite3",
                    "backups": ".rebuild/backup",
                },
                "rules": [
                    "Never duplicate content across folders — reference by ID.",
                    "Stage alias folders are forbidden; use CANONICAL_STAGES.",
                    "PDFs are content-read on demand, never bulk-loaded.",
                ],
            }}
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            json.dump(data, open(self.config_path, "w", encoding="utf-8"), indent=2)
        for pid, v in data.items():
            self._projects[pid] = Project(id=pid, **v)

    def get(self, project_id: str) -> Project | None:
        return self._projects.get(project_id)

    def resolve(self, path: str, project_id: str = "boom") -> str:
        """Turn a relative path into an absolute path inside the boundary."""
        p = self._projects.get(project_id)
        if not p:
            raise KeyError(f"unknown project: {project_id}")
        return os.path.normpath(os.path.join(p.root, path))

    def contains(self, path: str, project_id: str = "boom") -> bool:
        p = self._projects.get(project_id)
        if not p:
            return False
        root = os.path.normpath(p.root).lower()
        target = os.path.normpath(os.path.abspath(path)).lower()
        return target == root or target.startswith(root + os.sep)

    def mount(self, name: str, project_id: str = "boom") -> str:
        p = self._projects.get(project_id)
        if not p:
            raise KeyError(project_id)
        m = p.mounts.get(name)
        if not m:
            raise KeyError(f"unknown mount '{name}' in project {project_id}")
        return p.path(m)

    def validate_stage(self, stage: str) -> bool:
        return stage in CANONICAL_STAGES

    def summary(self) -> str:
        lines = []
        for p in self._projects.values():
            lines.append(f"{p.id}: {p.title}")
            lines.append(f"  root   : {p.root}")
            for k, v in p.mounts.items():
                lines.append(f"  mount  : {k:10} -> {v}")
            for r in p.rules:
                lines.append(f"  rule   : {r}")
        return "\n".join(lines)


if __name__ == "__main__":
    pm = ProjectManager()
    print(pm.summary())
    print("\nstages:", ", ".join(CANONICAL_STAGES))
    p = pm.get("boom")
    print("\nin-boundary check:")
    for path in [os.path.join(BOOM, "scripts", "x.py"), r"C:\Windows\System32\cmd.exe"]:
        print(f"  {pm.contains(path)!s:5} {path}")