

---
name: boom-scrutinize
description: Cold outsider review of a Boom change or plan. Ask whether it should exist, trace the real code path end-to-end, verify every claim, report findings by severity with evidence.
---

# boom-scrutinize

Stand outside the change and ask whether it should exist at all, then verify it actually does what it claims end-to-end for Boom Project.

## Operating stance

- **Outsider.** Forget who wrote it and why they think it's right. Read the artifact cold.
- **End-to-end, not diff-local.** The diff is the entry point, not the scope. Follow the call graph through real code paths.
- **Actionable, concise, with rationale.** Every finding states *what to change*, *why*, and *what evidence* led you there. No filler.

## Workflow

Run these in order. Do not skip ahead.

### 1. Intent — what is this actually trying to do?

- State the goal in one sentence, in your own words. If you cannot, the artifact is underspecified — say so and stop.
- Ask: **is there a simpler, smaller, or more elegant way to achieve the same goal?** Consider:
  - Doing nothing (is the problem real / load-bearing for Boom?).
  - Using something that already exists in Boom scripts/Knowledge instead of adding new surface.
  - A smaller change that solves 90% of the goal with 10% of the risk.
  - Solving it at a different layer (config vs code, script vs pipeline, manual vs automated).
- If a better alternative exists, name it explicitly with rationale. This is the most valuable thing you can output.

### 2. Trace — walk the actual code path

- For each behavior the change claims, trace the path end-to-end through real code, not just the lines in the diff:
  - Entry point → call sites → branches taken → state mutated → exit / return / side effect.
  - Include the unchanged code on either side of the diff. Bugs hide at the seams.
- For a plan or design doc: trace the proposed flow against the existing Boom system. Where does it touch reality? What does it assume that isn't true?
- Note every place the trace surprises you (unexpected branch, dead code reached, state you didn't know existed). Surprises are signal.

**Boom trace targets:**
- `scripts/natal_chart.py` → `NatalChart` → Swiss Ephemeris calls → house system → output format
- `scripts/transit_timeline_v3.py` → exact-minute aspect timing (prefer v3 over v2)
- `scripts/tarot_engine.py` → `draw_cards()` → interpretation lookup → formatting
- `scripts/query_db.py` → index lookup → line grep → excerpts (NB: `scripts/astrology_db.py` is a **library**, no CLI — the CLI is `query_db.py`)
- astro skill scripts: `astro-natal-chart/scripts/natal_chart_swe.py`, `astro-synastry/scripts/synastry.py` — run with Boom `.venv` python 3.11 (pyswisseph 2.10.03); `hermes_astro` lives in the **Hermes** venv, not `.venv`
- Pipeline agents: Plawan → Nut/CK → Arm/Nan → Bella → PAC/Transit
- Eng/Libby: `libby/cli.py` → `build-output-index.py` → `project_index.py` → `memory_db.py`

**Check index staleness first** on anything reading a `Knowledge/indexes/` JSON.
Indexes are snapshots and drift silently, because the consumers wrap file reads in
`try/except → continue` — a fully stale index returns zero hits with no error. Cheap
check: resolve every `files[].path` against its base dir and count missing. If
non-zero, rebuild with the index's builder and re-verify. Full drill, known index
instances, and the script-tooling precedents live in `references/index-drift.md`.

### 3. Verify — does it actually do what it claims?

For each claim the change/plan makes, answer:

- **Does the code path you just traced actually produce that behavior?** Walk it explicitly. "It claims X. Path: A → B → C. At C, [observation]. Therefore [holds / doesn't hold]."
- **What inputs / states would break it?** Edge cases: birth times at midnight, polar latitudes, retrograde stations, eclipse boundaries, empty Knowledge folders, missing PDF text layers, stale indexes.
- **What does it silently change?** Performance, error semantics, observability, contract for other callers, on-disk format (frontmatter, JSON schema), index integrity.
- **How is it tested?** Do tests actually exercise the traced path, or do they pass while skipping it (mocks that hide the bug, asserts on intermediate state, happy path only)?

### 4. Report

Output one tight section per finding. Order by severity (blocker → major → nit). For each:

- **Finding** — one sentence, specific. Cite `file:line` when applicable.
- **Why it matters** — the consequence for Boom, not the principle.
- **Evidence** — the trace step or input that exposes it.
- **Suggested change** — concrete, minimal.

Close with a one-line verdict: ship / fix-then-ship / rework / reject — with the single biggest reason.

## Operating rules

- **No rubber-stamps.** "LGTM" is not an output. If you genuinely find nothing, say what you traced and what you checked.
- **Cite or it didn't happen.** Every claim references a specific path, file, or line. No vague "this might break under load."
- **Distinguish claim from verification.** "The PR says X" and "I traced X and confirmed / refuted it" are different — keep them separate.
- **One simpler-alternative pass is mandatory.** Even on small changes, spend one breath asking if the whole thing is necessary. Skip only if user explicitly says "don't question scope."
- **Don't pad with style nits when there's a structural problem.** If step 1 or 2 surfaces a real issue, lead with it; defer nits or drop them.
- **No flattery, no hedging.** "This is a great PR but..." adds nothing. State the finding.

## Boom Project Integration

### Mandatory Startup Protocol (every session)
1. Run `boom-auto-workflow-router`
2. Read `SOUL.md` and `TURBOZ.md`
3. Consult `.hermes.md` and `BOOM_PERSONAL_OPERATING_SYSTEM.md`
4. Restore relevant memory/session context
5. Load task-specific skills
6. Apply context-economy rules
7. Turboz + Ekae collaborate automatically
8. Verify files, commands, counts, external side effects

### Output routing
- Review reports → `Output/Arm/` (audit reports) or `Output/Nan/` (critique reports)
- Canonical records → `Output/Sources/` if research-related
- Leadership summaries → `boom-content-adapt` for PAC/Transit comms
