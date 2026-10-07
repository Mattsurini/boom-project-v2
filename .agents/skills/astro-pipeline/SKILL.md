---
name: astro-pipeline
description: Run the full Convergence Research Pipeline end-to-end (ideate → bridge → query NotebookLM → analyze) for BooM Project.
version: 0.2.0
author: BooM Project, Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [astro, pipeline, orchestrator]
    related_skills: ["astro-knowledge-db", "Ekae"]
---

# Astro Pipeline — Convergence Research Pipeline

Run the full research pipeline: ideate → bridge → query NotebookLM → analyze.

## Trigger
When Boom says:
- "run pipeline on <topic>"
- "do the full research pipeline for <topic>"
- "ideate / bridge / query / analyze <topic>" (a single stage)

## Prerequisites Check
1. **NotebookLM access** — run `.venv\Scripts\notebooklm.exe metadata`. If it prints
   `Not logged in` / `AUTH_REQUIRED`, STOP and tell BooM to run
   `.venv\Scripts\notebooklm.exe login` then `.venv\Scripts\notebooklm.exe use <notebook-id>`.
   **Status 2026-10-06: NOT logged in — the NotebookLM stage is currently blocked.**
   Stages 1, 2a and 2c (ideate / bridge / analyze) can still run; only 2b needs it.
2. **Output directory** — ensure `Output/Plawan/Astrology/` exists.
3. **Knowledge databases** — use the `astro-knowledge-db` skill. Flag `[NOT IN DB]`
   for anything PDF-only (the index covers 197 `.md` files; the 185 PDFs in
   `Knowledge/Astrology-Database/` are not indexed).

## Execution
Each stage = load the matching agent role. The seven `astro-agent-*` skills were
merged into this document on 2026-10-06 (originals archived in
`.rebuild/legacy_skill_texts.txt`); **do not try to `skill_view` them — they no
longer exist.** `config/agents.json` remains the registry of who does what.

### Stage 1 — IDEATE (Plawan)
Produce the Research Blueprint:
- **Idea Card**: hypothesis, expectations, success markers, constraints
- **NotebookLM Prompt Set**: 5-10 questions in 3 phases (Establishing Facts, Testing Hypothesis, Adversarial/Critical Check)
- **Blind-Spot Instructions**: a "Blind-spot Sweep" prompt

Ground the blueprint in classical texts from `Knowledge/Astrology-Database/` (BPHS, Brihat Jataka, Jaimini, Saravali, Phaladeepika, KN Rao, etc.). Flag missing sources as `[NOT IN DB]`.

**Save to:** `Output/Plawan/Astrology/YYYYMMDD-slug-blueprint.md`

### Stage 2a — BRIDGE (Plawan)
1. **Fetch Search** — web search for supplementary sources (peer-reviewed papers, academic books, reputable astrology/psychology). Flag counter-sources (they become adversarial prompts). Specifically search any `[NOT IN DB]` sources flagged in the blueprint.
2. **Bridge** — convert the blueprint (incorporating web findings) into a NotebookLM Execution Packet:
   - **Context Note**: 1-2 paragraph persona + hypothesis
   - **Prompt Sequence**: organized by phase, web sources woven in, adversarial prompts for counter-sources
   - **Blind-Spot Protocol**: exact blind-spot sweep prompt with interpretation instructions

**Save to:** `Output/Plawan/Astrology/YYYYMMDD-slug-execution-packet.md` AND `Output/Plawan/Astrology/YYYYMMDD-slug-questions.json`

`questions.json` schema (both forms accepted — verified 2026-10-06):
```json
{
  "title": "Retrograde/Vakri",
  "slug": "retrograde-vakri",
  "contextNote": "1-2 paragraphs…",
  "questions": [
    { "id": "Q1", "phase": "Establishing Facts", "prompt": "…" },
    { "id": "Q2", "phase": "Testing Hypothesis", "prompt": "…" }
  ],
  "blindSpot": "…"
}
```
Plain-string questions (`"questions": ["…", "…"]`) also work. **Always set `slug`** —
without it the title drives the dedupe key, and two different topics that
slugify the same (or both fall back to `research`) silently skip the run.

### Stage 2b — QUERY NOTEBOOKLM
Run the automated NotebookLM query script:
```
node scripts/notebooklm-run.js Output/Plawan/Astrology/YYYYMMDD-slug-questions.json
```
This creates the Context Note, asks Q1 as a new conversation (Q2..Qn as follow-ups), runs the Blind-Spot Sweep, and writes **`Output/NotebookLM/YYYYMMDD-slug-notebooklm-results.md`**
(not `Output/Plawan/Astrology/` — the script writes to `Output/NotebookLM/`, and
re-running an already-logged `slug` exits without querying).

### Stage 2c — ANALYZE
1. **GATHERING (parallel)**:
   - Nut (technical extraction) → `Output/Nut/Astrology/`
   - CK (psychological extraction) → `Output/CK/Astrology/`
2. **AUDIT (parallel)**:
   - Arm (forensic verification, grade each claim [PROVEN]/[PLAUSIBLE]/[UNVERIFIED]) → `Output/Arm/Astrology/`
   - Nan (adversarial review) → `Output/Nan/Astrology/`
3. **SYNTHESIS**:
   - Bella (Convergence Report using ONLY verified data) → `Output/Bella/Astrology/`
4. **EXTRACTION + FILING**:
   - Bed (golden thread + top 3 insights: technical / psychological / convergence)
   - File dated `.md` entries into `Knowledge/Astrology-Database/`, `Knowledge/Psychology-Database/`, `Knowledge/Convergence-Database/`; update each `index.md`.

## Output Summary
When the pipeline completes, present:
1. **Golden Thread** — the core insight in one sentence
2. **Top Insights** — technical, psychological, convergence (one line each)
3. **Critic's Verdict** — verified / needs revision / rejected
4. **Files Written** — full list of every file created across all stages
5. **Next Steps** — what needs Boom's review, what was filed, what needs manual attention

## Important Rules
- **Respect the critic's verdict** — if the report is [REJECTED], do not finalize. Explain why and what needs fixing.
- **NotebookLM is required** — do not substitute self-research for the NotebookLM query.
- **Boom approves everything** — nothing is published, sent, or filed without approval. The pipeline produces drafts.
- **If a stage fails**, stop and report the blocker. Do not skip stages or guess.
- **Source priority** — NotebookLM results are primary. Knowledge databases are cross-reference. Web search is fallback. Always cite.

## Quick Reference: File Flow
```
Output/Plawan/  ← blueprint + execution packet + questions.json
Output/NotebookLM/  ← NotebookLM Q&A results
Output/Nut/     ← technical astrology extraction
Output/CK/      ← psychological extraction
Output/Arm/     ← forensic audit report
Output/Nan/     ← critical review report
Output/Bella/   ← final Convergence Report
Knowledge/*-Database/  ← filed golden insights
```

## Pipeline stages (consolidated 2026-10-06)

Seven separate `astro-agent-*` skills (plawan, ck, nan, arm, nut, bella, bed) were
merged into this single methodology. Their text is archived at
`.rebuild/legacy_skill_texts.txt`. The agent REGISTRY (`config/agents.json`) is
still the source of truth for who does what — this skill is how to run them.

| Stage | Agent | Output stage | Responsibility |
|---|---|---|---|
| 1 | Plawan | `Output/Plawan` | ideate — idea cards, blueprints |
| 2 | Nut  | `Output/Nut`  | astrology chart calculation and extraction |
| 2 | CK   | `Output/CK`   | psychological insight extraction |
| 3 | Arm  | `Output/Arm`  | source verification and claim auditing |
| 3 | Nan  | `Output/Nan`  | critique and counter-argument |
| 4 | Bella| `Output/Bella`| narrative synthesis and client-facing prose |
| 5 | Eng  | `Output/Sources` | classify, index, registry sync |
| 5 | Bed  | `Output/Sources` | durable insight capture |

Run only the stages the task needs. Never run all seven by default — that is the
agent-overuse debt this consolidation removes. Ask JEV is not a stage; it is
decision support and is gated by `core/policy.py`.
