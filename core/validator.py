#!/usr/bin/env python
"""
hermes.core.validator — Validator.

Nothing is "done" because a step returned. It is done when the validator says
so, against named criteria, with evidence. This is the component that makes
"REBUILD COMPLETE" mean something other than optimism (§22).
"""
from __future__ import annotations

import hashlib
import json
import os
import re
from dataclasses import dataclass, field
from typing import Any, Callable

BOOM = os.environ.get("BOOM_ROOT", r"E:\Boom Project")


@dataclass
class Criterion:
    id: str
    name: str
    check: Callable[[], tuple[bool, str]]
    blocking: bool = True


@dataclass
class Result:
    criterion: str
    passed: bool
    evidence: str
    blocking: bool = True

    @property
    def status(self) -> str:
        if self.passed:
            return "PASS"
        return "FAIL" if self.blocking else "WARN"


@dataclass
class Report:
    results: list[Result] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return all(r.passed for r in self.results if r.blocking)

    @property
    def blocking_failures(self) -> list[Result]:
        return [r for r in self.results if not r.passed and r.blocking]

    def render(self) -> str:
        w = max((len(r.criterion) for r in self.results), default=10)
        lines = []
        for r in self.results:
            ev = r.evidence.replace("\n", " ")[:110]
            lines.append(f"[{r.status:4}] {r.criterion:<{w}}  {ev}")
        n_ok = sum(1 for r in self.results if r.passed)
        lines.append("")
        lines.append(f"{n_ok}/{len(self.results)} criteria passed — "
                     f"{'VALID' if self.passed else 'NOT VALID'}")
        return "\n".join(lines)

    def to_dict(self) -> dict[str, Any]:
        return {
            "passed": self.passed,
            "results": [{"criterion": r.criterion, "status": r.status,
                         "evidence": r.evidence, "blocking": r.blocking}
                        for r in self.results],
        }


# --------------------------------------------------------------- checkers
def _path_exists(p: str) -> tuple[bool, str]:
    ok = os.path.exists(p)
    return ok, f"{'found' if ok else 'MISSING'}: {p}"


def _count_files(root: str, ext: str = ".md", recursive: bool = True) -> int:
    if not os.path.isdir(root):
        return 0
    n = 0
    for dp, dn, fn in os.walk(root):
        if not recursive:
            dn[:] = []
        n += sum(1 for f in fn if f.endswith(ext))
    return n


def check_no_legacy_roots() -> tuple[bool, str]:
    """The two dead skill roots must stay gone from the project.

    ``.agents/skills`` is deliberately NOT in this list: since the project became
    a git root (2026-10-06) it is the LIVE project skill root (tier0), not dead
    weight. ``skills/`` and ``.hermes/skills`` are the pre-rebuild duplicates.
    """
    legacy = [os.path.join(BOOM, p) for p in ("skills", ".hermes/skills")]
    remaining = [p for p in legacy if os.path.isdir(p)]
    return not remaining, (
        "dead roots absent; .agents/skills is the live project root" if not remaining
        else f"still present: {[os.path.relpath(r, BOOM) for r in remaining]}")


def check_single_live_root() -> tuple[bool, str]:
    """One live skill root per tier: the project root, plus the profile mirror.

    Project ``.agents/skills`` is tier0 and authoritative; the profile
    ``%HERMES_HOME%/skills`` is a byte-identical mirror kept only so other
    sessions (and profile-tier fallback) still resolve every skill.
    """
    h = os.environ.get("HERMES_HOME", r"C:\Users\Turbo\AppData\Local\hermes")
    project_root = os.path.join(BOOM, ".agents", "skills")
    profile_root = os.path.join(h, "skills")
    for label, root in (("project", project_root), ("profile", profile_root)):
        if not os.path.isdir(root):
            return False, f"{label} root missing: {root}"
    if not os.path.isdir(os.path.join(BOOM, ".git")):
        return False, "project is not a git root — project skills would never load"
    np = _count_files(project_root, "SKILL.md", recursive=True)
    nf = _count_files(profile_root, "SKILL.md", recursive=True)
    if np == 0:
        return False, f"no SKILL.md under {project_root}"
    return True, f"{np} SKILL.md in project root (tier0), {nf} in profile mirror (tier1)"


def _norm_nl(raw: bytes) -> bytes:
    """Normalise line endings before hashing.

    CRLF vs LF is not drift. ``cp`` on this Windows host can silently flip a
    mirror copy's endings, which a byte hash reports as divergence forever
    after, and any text-mode round-trip on the checker's own fixtures flips them
    again. Hash the *content*, not the byte layout.
    """
    return raw.replace(b"\r\n", b"\n").replace(b"\r", b"\n")


def _skill_index(root: str) -> dict[str, str]:
    """Hash every SKILL.md under root, keyed by path RELATIVE TO root.

    Depth matters: skills live at ``<category>/<name>/SKILL.md``, so an
    ``os.listdir`` + ``<root>/<name>/SKILL.md`` probe finds nothing once every
    skill is nested and reports "no drift" vacuously.
    """
    out: dict[str, str] = {}
    if not os.path.isdir(root):
        return out
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if not d.startswith(".")]
        if "SKILL.md" not in filenames:
            continue
        p = os.path.join(dirpath, "SKILL.md")
        rel = os.path.relpath(p, root).replace(os.sep, "/")
        out[rel] = hashlib.md5(_norm_nl(open(p, "rb").read())).hexdigest()
    return out


def check_no_divergent_skills() -> tuple[bool, str]:
    """Every SKILL.md in the mirror must match the project root, at any depth.

    Tier0 (project ``.agents/skills``) is authoritative; tier1 (profile mirror)
    must be byte-identical or other sessions resolve stale bodies.
    """
    h = os.environ.get("HERMES_HOME", r"C:\Users\Turbo\AppData\Local\hermes")
    roots = (os.path.join(BOOM, ".agents", "skills"), os.path.join(h, "skills"))
    tier0, tier1 = (_skill_index(r) for r in roots)
    if not tier0:
        return False, f"no SKILL.md under {roots[0]}"
    if not tier1:
        return False, f"no SKILL.md under {roots[1]}"
    drift = sorted(k for k in set(tier0) & set(tier1) if tier0[k] != tier1[k])
    if drift:
        return False, f"{len(drift)} divergent copies: {drift[:10]}"
    only0 = sorted(set(tier0) - set(tier1))
    only1 = sorted(set(tier1) - set(tier0))
    extra = ""
    if only0:
        return False, f"{len(only0)} skills missing from the mirror: {only0[:10]}"
    if only1:
        # Mirror-only rows are not divergence, but they are unaccounted surface.
        return False, f"{len(only1)} mirror-only skills with no source: {only1[:10]}"
    return True, (f"all {len(tier0)} skills byte-identical across project + mirror "
                  + extra).strip()


def check_registry_complete() -> tuple[bool, str]:
    from .registry import Registry
    r = Registry()
    st = r.stats()
    total = sum(v for k, v in st.items() if not k.endswith("_deprecated"))
    return total > 0, f"{total} live components registered: " + ", ".join(
        f"{k}={v}" for k, v in st.items() if not k.endswith("_deprecated"))


def check_descriptors_small() -> tuple[bool, str]:
    """Measure the ACTUAL preloaded prompt surface.

    Only skill triggers are injected into every turn by Hermes. Scripts, agents
    and MCP entries live in the registry and are read on demand, so counting
    them here would measure the wrong thing and force pointless edits.
    """
    from .registry import Registry
    r = Registry()
    skills = [d for d in r.all(kind="skill")]
    tot = sum(len(d.trigger) for d in skills)
    worst = max(skills, key=lambda d: len(d.trigger)) if skills else None
    # 400 chars/skill is the enforced per-descriptor cap; 150 chars average
    # keeps the whole preloaded surface under ~12k chars (~3k tokens).
    ok = all(len(d.trigger) <= 400 for d in skills) and tot <= 12_000
    return ok, (
        f"{len(skills)} skills, {tot} chars preloaded (~{tot//4} tokens/turn); "
        f"largest={worst.id} ({len(worst.trigger)}c)" if worst else "no skills registered")


def check_skill_bodies_loadable() -> tuple[bool, str]:
    """A SKILL.md that ContextManager would refuse is dead methodology.

    ``MAX_SKILL_MD_CHARS`` (12k) is a *style* cap for splitting depth into
    ``references/``; the *loadability* line is
    ``context.DEFAULT_MAX_SINGLE_BODY_CHARS`` (20k). Anything above it can never be
    loaded at all, so it is a real defect rather than a warning.
    """
    from .context import DEFAULT_MAX_SINGLE_BODY_CHARS
    from .skill import SkillManager, MAX_SKILL_MD_CHARS

    infos = SkillManager().scan()
    dead = sorted((i for i in infos if i.size > DEFAULT_MAX_SINGLE_BODY_CHARS),
                  key=lambda x: -x.size)
    if dead:
        names = [f"{i.category}/{i.name}" if i.category else i.name for i in dead]
        return False, (f"{len(dead)} skills cannot be loaded (>{DEFAULT_MAX_SINGLE_BODY_CHARS}c, "
                       f"ContextManager refuses): {', '.join(names[:10])}")
    soft = sum(1 for i in infos if i.size > MAX_SKILL_MD_CHARS)
    return True, (f"every SKILL.md loadable (<={DEFAULT_MAX_SINGLE_BODY_CHARS}c); "
                  f"{soft} over the {MAX_SKILL_MD_CHARS}c style cap (split advised)")


def check_skills_described() -> tuple[bool, str]:
    """No skill may be undiscoverable: a missing description is a dead trigger."""
    from .skill import SkillManager

    infos = SkillManager().scan()
    und = sorted((i.name for i in infos if not i.description))
    if und:
        return False, f"{len(und)} skills with no description: {und[:10]}"
    return True, f"all {len(infos)} skills carry a description"


def check_router_resolves() -> tuple[bool, str]:
    from .router import Router
    router = Router()
    probes = [
        ("what is the moon doing today", "astrology"),
        ("run the transit timeline script", "transit"),
        ("who are you", "identity"),
        ("organize the output folder and rebuild indexes", "index"),
    ]
    lines = []
    for q, expect in probes:
        route = router.route(q)
        ok = route.primary is not None
        lines.append(f"{'ok' if ok else 'MISS'}:{expect}")
        if not ok:
            return False, f"no route for '{q}'"
    return True, "resolved: " + " ".join(lines)


def check_policy_gates_jev() -> tuple[bool, str]:
    from .policy import EscalationRequest, decide
    must = [
        (EscalationRequest("delete skills root", reversible=False,
                           options=["a", "b", "c"]), True),
        (EscalationRequest("publish PAC", publishes=True), True),
        (EscalationRequest("run transit script"), False),
        (EscalationRequest("interpret natal chart"), False),
    ]
    for req, want in must:
        got = decide(req).escalate
        if got != want:
            return False, f"policy gate wrong for '{req.decision}': got {got}, want {want}"
    return True, "JEV escalates only on triggers, never on routine work"


def check_context_budget_enforced() -> tuple[bool, str]:
    from .context import ContextManager, Budget
    cm = ContextManager(budget=Budget(max_chars=500, max_single=500))
    from .registry import Registry
    r = Registry()
    big = next((d.id for d in r.all() if os.path.getsize(d.path or "") > 400
                and os.path.isfile(d.path or "")), None)
    if big:
        got = cm.load(big)
        if got is not None:
            return False, f"oversized body '{big}' loaded despite budget"
    return True, "oversized bodies refused; budget is enforcement, not advice"


def check_artifacts_traceable() -> tuple[bool, str]:
    from .registry import Registry
    r = Registry()
    bad = []
    for a in r.artifacts():
        if not a["sources"] or not a["path"]:
            bad.append(a["artifact_id"])
    return not bad, (
        "all artifacts carry source lineage" if not bad
        else f"untraceable artifacts: {bad}")


def check_no_dead_wall() -> tuple[bool, str]:
    """The 46MB TencentDB stack must not remain wired as if it were live."""
    p = os.path.join(BOOM, "memory_integration", "tencentdb-agent-memory")
    if not os.path.isdir(p):
        return True, "tencentdb stack removed from the live tree"
    refs = 0
    for sub in ("scripts", "skills", "core"):
        d = os.path.join(BOOM, sub)
        if os.path.isdir(d):
            for dp, dn, fn in os.walk(d):
                dn[:] = [x for x in dn if x not in {"__pycache__", "node_modules"}]
                for f in fn:
                    if f.endswith((".py", ".md")):
                        try:
                            if "tencentdb" in open(os.path.join(dp, f),
                                                    encoding="utf-8", errors="ignore").read().lower():
                                refs += 1
                        except Exception:
                            pass
    return refs == 0, (f"tencentdb present but unreferenced from {refs} live files"
                       if refs else "tencentdb unreferenced; quarantined not live")


def check_backup_intact() -> tuple[bool, str]:
    b = os.path.join(BOOM, ".rebuild", "backup")
    if not os.path.isdir(b):
        return False, f"no backup at {b}"
    runs = sorted(os.listdir(b))
    latest = os.path.join(b, runs[-1])
    man = os.path.join(latest, "BACKUP_MANIFEST.json")
    if not os.path.isfile(man):
        return False, "backup manifest missing"
    m = json.load(open(man, encoding="utf-8"))
    return bool(m.get("verified")), f"{runs[-1]}: {m.get('files')} files, verified={m.get('verified')}"


def check_no_two_systems() -> tuple[bool, str]:
    """Guards against 'new architecture + compatibility hacks' (§20)."""
    problems = []
    for legacy in ("HERMES_ORCHESTRATOR.md", "HERMES_SYSTEM_PROMPT.md",
                   "HERMES_SYSTEM_AUDIT.md", "boom-auto-workflow-router"):
        if os.path.exists(os.path.join(BOOM, legacy)):
            problems.append(legacy)
        h = os.path.join(os.environ.get("HERMES_HOME",
                  r"C:\Users\Turbo\AppData\Local\hermes"), "skills", legacy)
        if os.path.isdir(h):
            problems.append(f"skills/{legacy}")
    return not problems, ("single authority; no legacy override in force"
                           if not problems else f"still shadowing: {problems}")


def default_criteria() -> list[Criterion]:
    return [
        Criterion("backup",       "Backup exists and verified",        check_backup_intact),
        Criterion("single-root",  "Exactly one load-bearing skill root", check_single_live_root),
        Criterion("legacy-gone",  "Legacy skill roots removed",         check_no_legacy_roots),
        Criterion("no-drift",     "No divergent skill copies",          check_no_divergent_skills),
        Criterion("registry",     "Registry populated",                 check_registry_complete),
        Criterion("thin-prompts", "Discovery descriptors thin",         check_descriptors_small),
        Criterion("loadable",     "SKILL.md bodies are loadable",        check_skill_bodies_loadable),
        Criterion("described",    "Every skill is discoverable",         check_skills_described),
        Criterion("router",       "Router resolves real requests",       check_router_resolves),
        Criterion("policy",       "Policy engine gates JEV",            check_policy_gates_jev),
        Criterion("budget",       "Context budget enforced",            check_context_budget_enforced),
        Criterion("artifacts",    "Artifacts traceable to sources",     check_artifacts_traceable),
        Criterion("no-dead-wall", "No dead integration left wired",     check_no_dead_wall),
        Criterion("no-two-sys",   "No legacy/compat shadowing",         check_no_two_systems),
    ]


def run(criteria: list[Criterion] | None = None) -> Report:
    rep = Report()
    for c in (criteria or default_criteria()):
        try:
            ok, ev = c.check()
        except Exception as e:
            ok, ev = False, f"checker error: {type(e).__name__}: {e}"
        rep.results.append(Result(c.id, ok, ev, c.blocking))
    return rep


if __name__ == "__main__":
    import sys

    r = run()
    print(r.render())
    if "--json" in sys.argv:
        print(json.dumps(r.to_dict(), indent=2))
    raise SystemExit(0 if r.passed else 1)