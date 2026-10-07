#!/usr/bin/env python
"""
hermes.core.script — Script Registry (execution layer).

Skill = methodology (what to do, why). Script = execution (how, precisely).
The rebuild's rule is that a skill must never reimplement a script's job.

Discovery is registry-driven, so `AGENTS.md`-style hand-maintained inventories
are unnecessary and cannot go stale.
"""
from __future__ import annotations

import ast
import os
import re
import subprocess
import sys
from dataclasses import dataclass, field
from typing import Any

from .registry import Registry, Descriptor

BOOM = os.environ.get("BOOM_ROOT", r"E:\Boom Project")
SCRIPT_DIRS = ("scripts", "tools", "core")
PYTHON = sys.executable


@dataclass
class ScriptInfo:
    name: str
    path: str
    description: str
    args: list[str] = field(default_factory=list)
    cli: bool = False
    size: int = 0
    problems: list[str] = field(default_factory=list)

    @property
    def entry(self) -> str:
        return f'"{PYTHON}" "{self.path}"'


def _module_summary(path: str) -> tuple[str, list[str], bool]:
    """Read structure via AST, not by importing. Importing runs code."""
    try:
        tree = ast.parse(open(path, encoding="utf-8", errors="replace").read())
    except SyntaxError:
        return "", [], False
    doc = (ast.get_docstring(tree) or "").strip().splitlines()
    desc = doc[0].strip() if doc else ""
    if not desc:
        for node in tree.body:
            if isinstance(node, ast.Assign):
                for t in node.targets:
                    if isinstance(t, ast.Name) and t.id in ("__doc__", "DESCRIPTION", "SUMMARY"):
                        try:
                            desc = ast.literal_eval(node.value)
                        except Exception:
                            pass
    args: list[str] = []
    has_cli = False
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and getattr(node.func, "attr", "") == "add_argument":
            if node.args:
                a = node.args[0]
                if isinstance(a, ast.Constant):
                    args.append(str(a.value))
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name) and t.id == "__name__" and getattr(node.value, "value", None) == "__main__":
                    has_cli = True
    return desc, args, has_cli


class ScriptRegistry:
    def __init__(self, registry: Registry | None = None) -> None:
        self.registry = registry or Registry()

    def scan(self) -> list[ScriptInfo]:
        out: list[ScriptInfo] = []
        for d in SCRIPT_DIRS:
            root = os.path.join(BOOM, d)
            if not os.path.isdir(root):
                continue
            for dp, dn, fn in os.walk(root):
                dn[:] = [x for x in dn
                         if x not in {"__pycache__", "node_modules", ".venv", "venv",
                                      "archive", "research", "libby", "backup"}]
                if os.path.abspath(dp) == os.path.abspath(root):
                    dn[:] = [x for x in dn if not x.endswith(".py")]
                for f in sorted(fn):
                    if not f.endswith((".py", ".js")):
                        continue
                    p = os.path.join(dp, f)
                    if f.startswith("_"):
                        continue
                    name = os.path.splitext(f)[0]
                    desc, args, cli = _module_summary(p) if f.endswith(".py") else ("", [], False)
                    info = ScriptInfo(name=name, path=p, description=desc, args=args,
                                      cli=cli, size=os.path.getsize(p))
                    if not desc:
                        info.problems.append("no module docstring — undiscoverable")
                    out.append(info)
        return out

    def publish_all(self) -> tuple[int, list[str]]:
        ok, bad = 0, []
        for s in self.scan():
            trig = s.description or f"{s.name} script"
            if len(trig) > 300:
                trig = trig[:297] + "..."
            d = Descriptor(id=f"script:{s.name}", kind="script", title=s.name.replace("_", " ").title(),
                           trigger=trig, path=s.path, tags=("script", "execution"),
                           cost=0)
            self.registry.register(d)
            ok += 1
        return ok, bad

    def run(self, name: str, *args: str, timeout: int = 300) -> dict[str, Any]:
        """Execute a registered script. Cost 0 — execution is not context."""
        d = self.registry.get(name) or self.registry.get(f"script:{name}")
        if not d:
            cands = [x for x in self.registry.all(kind="script")
                     if x.id.split(":", 1)[-1] == name]
            if not cands:
                return {"ok": False, "error": f"script not registered: {name}"}
            d = cands[0]
        cmd = [PYTHON, d.path, *args]
        self.registry.trace(d.id, "execute", " ".join(args)[:200])
        try:
            p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout,
                               cwd=BOOM)
            return {"ok": p.returncode == 0, "returncode": p.returncode,
                    "stdout": p.stdout[-8000:], "stderr": p.stderr[-4000:],
                    "command": " ".join(cmd)}
        except subprocess.TimeoutExpired:
            return {"ok": False, "error": f"timeout after {timeout}s", "command": " ".join(cmd)}

    def report(self) -> str:
        s = self.scan()
        nodoc = [x for x in s if x.problems]
        return (
            "SCRIPT REGISTRY\n" + "=" * 52 +
            f"\nscanned     : {len(s)} scripts in {', '.join(SCRIPT_DIRS)}/"
            f"\ncli         : {sum(1 for x in s if x.cli)}"
            f"\nno docstring: {len(nodoc)}"
            + ("\n\nUNDISCOVERABLE:" if nodoc else "\n\nall scripts have module docstrings")
            + "".join(f"\n  {x.name:32} {x.problems[0]}" for x in nodoc[:20])
        )


if __name__ == "__main__":
    import sys

    sr = ScriptRegistry()
    if len(sys.argv) > 1 and sys.argv[1] == "run":
        print(sr.run(*sys.argv[2:]))
    else:
        print(sr.report())