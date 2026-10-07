#!/usr/bin/env python
"""
hermes.core.skill — Skill Manager.

Skill = methodology. Script = execution. Keeping those separate is the single
biggest anti-duplication lever in the rebuild (§15).

Rules:
  * Exactly one live skill root. Everything else is an archive, not a source.
  * Descriptions are triggers, not documentation. The description is the ONLY
    part that enters the prompt, so it is capped and enforced.
  * A skill over the size cap is split: method in SKILL.md, depth in references/.
  * A skill name present both at the top level and inside a category folder is
    a genuine duplicate and is reported.
"""
from __future__ import annotations

import os
import re
from dataclasses import dataclass, field

from .registry import Registry, Descriptor, MAX_DESCRIPTOR_CHARS
from .context import DEFAULT_MAX_SINGLE_BODY_CHARS

BOOM = os.environ.get("BOOM_ROOT", r"E:\Boom Project")
HERMES = os.environ.get("HERMES_HOME", r"C:\Users\Turbo\AppData\Local\hermes")
# The project became a git root on 2026-10-06, so `.agents/skills` is now the
# authoritative (tier0) skill root and Hermes loads it as trusted project skills.
# The profile mirror stays in sync for other sessions but is not the source.
LIVE_ROOT = os.environ.get(
    "BOOM_SKILLS_ROOT", os.path.join(BOOM, ".agents", "skills"))
MIRROR_ROOT = os.path.join(HERMES, "skills")

# A SKILL.md above this is a documentation file pretending to be a trigger.
# ADVISORY: the split-into-references/ style cap. Nothing is refused above it.
MAX_SKILL_MD_CHARS = 12_000
MAX_TRIGGER_CHARS = 200

# HARD: ContextManager.load() refuses anything above this, so a SKILL.md over
# this line can never be loaded into context by any route. Imported from
# context.py rather than re-declared, so the two numbers cannot drift apart.
HARD_BODY_CAP_CHARS = DEFAULT_MAX_SINGLE_BODY_CHARS


@dataclass
class SkillInfo:
    name: str
    path: str
    description: str
    size: int
    category: str = ""
    has_references: bool = False
    oversized: bool = False
    is_top_level: bool = True
    problems: list[str] = field(default_factory=list)

    @property
    def tokens(self) -> int:
        return self.size // 4


# Explicit routing vocabulary. Skills own these words; without them the router
# falls back to fuzzy matching and picks nonsense (measured: "who are you"
# routed to Ekae, "publish a PAC caption" routed to to-spec).
ROUTE_ALIASES: dict[str, tuple[str, ...]] = {
    "boom-router": ("route", "classify", "which skill should i use",
                    "which skill do i need", "what can you do", "help",
                    "where do i start"),
    "turboz": ("who are you", "your name", "identity", "introduce yourself",
               "what are you", "voice", "boundaries"),
    "daily-transit": ("moon", "today", "transit", "timing", "window",
                      "posting time", "when should i post", "daily",
                      "morning briefing", "pac timing"),
    "astro-natal-chart": ("natal", "birth chart", "my chart", "calculate chart",
                          "ascendant", "divisional chart"),
    "astro-synastry": ("synastry", "compatibility", "relationship chart",
                       "two charts", "partner chart", "match"),
    "horary-astrology": ("horary", "prashna", "question chart"),
    "tarot-reading": ("tarot", "card", "spread", "draw", "divin", "oracle"),
    "astro-knowledge-db": ("classical text", "parashara", "jaimini",
                           "kp astrology", "what does the text say",
                           "vedas", "source quote"),
    "research-deep": ("research", "deep dive", "investigate", "converge",
                      "literature", "compare sources"),
    "research-report": ("research report", "write up findings"),
    "boom-core-rebuild": ("boom core", "operate the core", "core router",
                          "core validator", "routing picks", "wrong skill",
                          "token bloat", "skill duplicated", "duplicate skill",
                          "agents.yaml", "agents.json", "ask jev",
                          "decision escalation", "registry", "discovery index"),
    "boom-project": ("project structure", "index", "manifest", "registry",
                     "classify files", "rebuild index", "where is",
                     "organise", "organize", "tidy the output"),
    "pac-transit-timing": ("instagram", "ig", "caption", "reel", "post",
                           "pac", "content", "social media", "posting time"),
    "boom-content-adapt": ("rewrite for instagram", "adapt content",
                           "make it punchy"),
    "chinese-almanac-scraper": ("scrape the chinese calendar",),
    "boom-chinese-almanac": ("chinese almanac", "chinese", "bazi", "ziwei",
                             "almanac", "huangli", "gan zhi", "lunar"),
    "boom-scrutinize": ("review my plan", "critique my", "critique this",
                        "outsider review", "poke holes"),
    "boom-post-mortem": ("post mortem", "write the record", "root cause doc"),
    "boom-debug-mantra": ("debug", "reproduce", "fix this bug"),
    "code-review": ("code review", "review changes", "review this diff"),
    "karpathy-guidelines": ("coding guidelines", "write code", "non-trivial code"),
    "web-search-agent": ("search the web", "google", "find online",
                         "look online", "search online"),
    "tdd": ("test first", "tdd", "unit test first"),
    "grill-me": ("grill me", "challenge my plan", "stress test my idea"),
    "xalen-ephemeris": ("ephemeris", "planet position", "xalen"),
    "financial-astrology": ("stock", "market", "financial astrology", "shares"),
    "integrated-astrology": ("western and uranian", "integrated reading"),
    "uranian-astrology-reference": ("uranian", "hamburg", "hammelburg"),
    "Ekae": ("plan my day", "milestone", "task", "reminder", "preferences"),
    "skill-creator": ("create a skill", "write a skill from scratch",
                      "author a new skill", "improve a skill",
                      "edit a skill"),
    "hermes-telegram-setup": ("telegram setup", "connect telegram"),
    "astro-pipeline": ("pipeline", "run the full pipeline", "end to end"),
    "myhora-chart": ("myhora", "fetch chart from website"),
    "lucky-colors-taksah": ("สีเสื้อมงคล", "สีมงคล", "สีกาลกิณี", "สีเสื้อ",
                            "ใส่เสื้อสีอะไร", "เสื้อสีอะไรดี", "ทักษา",
                            "lucky color", "lucky shirt", "shirt color"),
    "thai-seven-number-interpretation": ("thai 7 number", "9 base"),
}


class SkillManager:
    def __init__(self, registry: Registry | None = None) -> None:
        self.registry = registry or Registry()

    # --------------------------------------------------------------- scanning
    def scan(self, root: str | None = None) -> list[SkillInfo]:
        """Inspect the live root. Returns metadata, never file contents.

        Walks RECURSIVELY. Hermes organises skills as <category>/<name>/SKILL.md
        (e.g. research/arxiv/SKILL.md) alongside <name>/SKILL.md. A name present
        at both levels is a genuine duplicate and is flagged as such.
        """
        root = root or LIVE_ROOT
        out: list[SkillInfo] = []
        if not os.path.isdir(root):
            return out
        root_abs = os.path.abspath(root)
        seen_top: set[str] = set()
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames
                           if not d.startswith(".") and d != "references"]
            if "SKILL.md" not in filenames:
                continue
            sm = os.path.join(dirpath, "SKILL.md")
            rel = os.path.relpath(dirpath, root)
            name = rel.split(os.sep)[-1]
            if os.sep not in rel:
                seen_top.add(name)
            text = open(sm, encoding="utf-8", errors="replace").read()
            info = SkillInfo(
                name=name, path=sm, description=self._description(text, dirpath),
                size=len(text),
                category=rel.split(os.sep)[0] if os.sep in rel else "",
                has_references=os.path.isdir(os.path.join(dirpath, "references")),
                oversized=len(text) > MAX_SKILL_MD_CHARS,
                is_top_level=os.sep not in rel,
            )
            if info.oversized:
                info.problems.append(
                    f"SKILL.md is {len(text)} chars "
                    f"(cap {MAX_SKILL_MD_CHARS}) — split depth into references/")
            if len(info.description) > MAX_TRIGGER_CHARS:
                info.problems.append(
                    f"description is {len(info.description)} chars "
                    f"(cap {MAX_TRIGGER_CHARS}) — trim to trigger only")
            if not info.description:
                info.problems.append("no description in frontmatter — undiscoverable")
            out.append(info)
        # Flag shadows: a skill nested inside a category folder whose name also
        # exists at the top level is a genuine duplicate.
        for i in out:
            if not i.is_top_level and i.name in seen_top:
                i.problems.append(f"DUPLICATE: shadows top-level '{i.name}'")
        return out

    @staticmethod
    def _description(text: str, skill_dir: str) -> str:
        m = re.search(r"^---\s*\n(.*?)\n---", text, re.S)
        block = m.group(1) if m else text[:800]
        d = re.search(r"^description:\s*(.+)$", block, re.M)
        if d:
            return d.group(1).strip().strip("'\"")
        for f in ("DESCRIPTION.md", "README.md"):
            p = os.path.join(skill_dir, f)
            if os.path.isfile(p):
                return open(p, encoding="utf-8", errors="replace").read()[:300].strip()
        return ""

    # ------------------------------------------------------------- publishing
    def publish(self, info: SkillInfo) -> Descriptor:
        """Publish a skill to the single live root and register its trigger."""
        trigger = info.description or info.name
        if len(trigger) > MAX_DESCRIPTOR_CHARS:
            raise ValueError(
                f"{info.name}: trigger {len(trigger)} chars exceeds "
                f"{MAX_DESCRIPTOR_CHARS}. Shorten the frontmatter description.")
        d = Descriptor(
            id=info.name, kind="skill", title=info.name.replace("-", " ").title(),
            trigger=trigger, path=info.path,
            tags=tuple(t for t in (info.category, "skill") if t),
            cost=1, aliases=ROUTE_ALIASES.get(info.name, ()),
        )
        self.registry.register(d)
        return d

    def publish_all(self) -> tuple[int, list[str]]:
        """One live root, registered. Returns (published, rejected)."""
        ok, bad = 0, []
        for info in self.scan():
            if any(p.startswith("DUPLICATE") for p in info.problems):
                bad.append(f"{info.name}: duplicate of a top-level skill — skipped")
                continue
            try:
                self.publish(info)
                ok += 1
            except ValueError as e:
                bad.append(str(e))
        return ok, bad

    # ---------------------------------------------------------------- hygiene
    def oversized(self) -> list[SkillInfo]:
        return [i for i in self.scan() if i.oversized]

    def undescribed(self) -> list[SkillInfo]:
        return [i for i in self.scan() if not i.description]

    def duplicates(self) -> list[SkillInfo]:
        return [i for i in self.scan()
                if any(p.startswith("DUPLICATE") for p in i.problems)]

    def prompt_cost(self) -> dict[str, int]:
        """What the preloaded skill surface actually costs."""
        infos = self.scan()
        desc_chars = sum(len(i.description) for i in infos)
        return {
            "skills": len(infos),
            "description_chars": desc_chars,
            "description_tokens": desc_chars // 4,
            "body_chars": sum(i.size for i in infos),
            "body_tokens": sum(i.size for i in infos) // 4,
            "oversized": sum(1 for i in infos if i.oversized),
        }

    def report(self) -> str:
        c = self.prompt_cost()
        lines = [
            "SKILL MANAGER",
            "=" * 52,
            f"live root            : {LIVE_ROOT}",
            f"skills               : {c['skills']}",
            f"PRELOADED per turn   : ~{c['description_tokens']} tokens "
            f"({c['description_chars']} chars of descriptions)",
            f"bodies (lazy)        : ~{c['body_tokens']} tokens total, loaded on demand",
            f"over style cap       : {c['oversized']} (advisory, {MAX_SKILL_MD_CHARS}c)",
        ]
        dups = self.duplicates()
        if dups:
            lines.append(f"\nDUPLICATES ({len(dups)}) — nested copy shadows top-level:")
            for i in dups[:20]:
                lines.append(f"  {i.category}/{i.name}")
        ov = self.oversized()
        hard = sorted((i for i in ov if i.size > HARD_BODY_CAP_CHARS),
                      key=lambda x: -x.size)
        if hard:
            lines.append(f"\nUNLOADABLE ({len(hard)}) — over ContextManager's "
                         f"{HARD_BODY_CAP_CHARS}c ceiling, these never load at all:")
            for i in hard:
                lines.append(f"  {i.size:7d} chars  {i.category}/{i.name}")
        soft = [i for i in ov if i.size <= HARD_BODY_CAP_CHARS]
        if soft:
            lines.append(f"\nOVER THE STYLE CAP ({len(soft)}) — loadable, but a split "
                         f"into references/ is advised at {MAX_SKILL_MD_CHARS}c:")
            for i in sorted(soft, key=lambda x: -x.size):
                lines.append(f"  {i.size:7d} chars  {i.category}/{i.name}")
        und = self.undescribed()
        if und:
            lines.append("\nMISSING DESCRIPTION:")
            for i in und:
                lines.append(f"  {i.category}/{i.name}")
        return "\n".join(lines)


if __name__ == "__main__":
    print(SkillManager().report())