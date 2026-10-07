---
agent: Plawan
date: '2026-08-21'
tags:
- ideas
- questions
- blueprint
- execution-packet
- notebooklm
- astrology
- psychology
- financial-astrology
- ml-ai
- methodology
- critique
- convergence
- technical
---

# The Convergence Research Pipeline — Explained

This is the research pipeline used in the Boom Project for astrology + psychology convergence research. It's a 4-stage, multi-agent system that moves from a raw idea to a verified, knowledge-base-filing insight.

---

## Overview: The Big Picture

```
Raw Idea
  │
  ▼
┌─────────────────────────────────────────────────────────┐
│  STAGE 1: IDEATE (Plawan)                               │
│  Turn a thought into a structured Research Blueprint    │
└─────────────────────────────────────────────────────────┘
  │
  ▼
┌─────────────────────────────────────────────────────────┐
│  STAGE 2a: BRIDGE (Plawan)                              │
│  Convert the blueprint into a NotebookLM Execution      │
│  Packet (Context Note + Prompt Sequence + Blind-Spot)   │
└─────────────────────────────────────────────────────────┘
  │
  ▼
┌─────────────────────────────────────────────────────────┐
│  STAGE 2b: QUERY NOTEBOOKLM                             │
│  Run the prompts against NotebookLM AI, get back Q&A    │
│  results + blind-spot sweep                             │
└─────────────────────────────────────────────────────────┘
  │
  ▼
┌─────────────────────────────────────────────────────────┐
│  STAGE 2c: ANALYZE                                      │
│  Dual-track extraction → Forensic audit → Synthesis →   │
│  Extraction → Filing into Knowledge bases               │
└─────────────────────────────────────────────────────────┘
  │
  ▼
Final Convergence Report + Golden Insights filed to:
  - Knowledge/Astrology-Database/
  - Knowledge/Psychology-Database/
  - Knowledge/Convergence-Database/
```

---

## Stage 1: IDEATE — "Plawan" (Idea Generator)

**Agent:** `idea-generator` (Plawan)
**Output:** `Output/Plawan/Astrology/YYYYMMDD-slug-blueprint.md`

Takes a raw thought or topic from Boom and structures it into a **Research Blueprint** containing:

1. **Idea Card** — Core hypothesis, a-priori expectations, success markers, constraints
2. **NotebookLM Prompt Set** — 5-10 targeted questions organized into 3 phases:
   - Phase 1: Establishing Facts
   - Phase 2: Testing the Hypothesis
   - Phase 3: Adversarial/Critical Check
3. **Blind-Spot Protocol** — A specific prompt to ask NotebookLM: "What's missing from these sources that would be critical?"

The blueprint is grounded in classical texts from `Knowledge/Astrology-Database/` (BPHS, Brihat Jataka, Jaimini, etc.). Missing sources are flagged as `[NOT IN DB]`.

---

## Stage 2a: BRIDGE — "Plawan" (Session Architect)

**Agent:** `idea-generator` (acting as session-architect)
**Output:** `Output/Plawan/Astrology/YYYYMMDD-slug-execution-packet.md` + `*.json`

This stage has **two sub-steps**:

### Sub-step 1: Fetch Search (NEW)

Before building the execution packet, run a web search for supplementary sources:

1. Search for peer-reviewed papers, academic books, and reputable astrology/psychology sources related to the core hypothesis
2. Flag counter-sources that directly challenge the hypothesis — these become adversarial prompts
3. Specifically search for any `[NOT IN DB]` sources flagged in the blueprint
4. Return a structured list of findings

### Sub-step 2: Bridge

Convert the Research Blueprint (incorporating web research findings) into a **NotebookLM Execution Packet** — the exact copy-paste material for NotebookLM:

1. **Context Note** — 1-2 paragraph persona + hypothesis that gets uploaded as a separate Note in NotebookLM
2. **Prompt Sequence** — All blueprint questions organized by phase, each with an explanation of WHY it's asked and what a good answer looks like. Web sources are woven into prompts where relevant, and adversarial prompts are added for counter-sources found in the fetch search.
3. **Blind-Spot Protocol** — The exact blind-spot sweep prompt with interpretation instructions

Also saves a machine-readable `*.json` file that drives the automated NotebookLM queries.

---

## Stage 2b: QUERY NOTEBOOKLM

**Tool:** `.venv/Scripts/notebooklm.exe` + `scripts/notebooklm-run.js`
**Output:** `Output/Plawan/Astrology/YYYYMMDD-slug-notebooklm-results.md`

Runs the automated NotebookLM query script:

1. Creates the Context Note in NotebookLM
2. Asks Q1 as a new conversation, then Q2..Qn as follow-ups in the same thread
3. Runs the Blind-Spot Sweep
4. Writes all answers + citations to a results file

This is the **data collection** phase — the only stage that pulls live answers from an external AI system.

---

## Stage 2c: ANALYZE — The Multi-Agent Deep Dive

This is the meat of the pipeline. It runs in 4 sub-phases with multiple agents working in parallel.

### Phase 1: GATHERING (Parallel)

Two agents work simultaneously on the NotebookLM results:

| Agent | Role | Lens | Output |
|-------|------|------|--------|
| `astrology-assistant` (Nut) | Technical Astrology Lead | Extracts exact aspects, house dignities, planetary cycles, degrees | `Output/Nut/Astrology/` |
| `research-specialist` (CK) | Psychological Research Lead | Extracts behavioral patterns, psychological themes, mental frameworks | `Output/CK/Astrology/` |

Both agents:
- Extract from NotebookLM results FIRST (primary source)
- Cross-reference against their respective `Knowledge/*-Database/` folders
- Cite exact file paths and page/sections
- Label unmapped claims as `[NOT IN DB]`
- Address the Blind-spots identified by NotebookLM

### Phase 2: AUDIT (Parallel)

Two different agents audit the raw reports:

| Agent | Role | Method | Output |
|-------|------|--------|--------|
| `audit-researcher` (Arm) | Forensic Accountant | Re-calculates, re-verifies, grades every claim [PROVEN]/[PLAUSIBLE]/[UNVERIFIED] | `Output/Arm/Astrology/` |
| `research-critic` (Nan) | Adversarial Reviewer | Challenges logic, finds gaps, stress-tests conclusions | `Output/Nan/Astrology/` |

- **Arm** focuses on **factual integrity** — are the calculations right? Are the citations real?
- **Nan** focuses on **logical integrity** — does the evidence actually support the conclusion? What's missing?

### Phase 3: SYNTHESIS

| Agent | Role | Output |
|-------|------|--------|
| `project-writer` (Bella) | Master Research Synthesizer | `Output/Bella/Astrology/` — The Convergence Report |

Takes ONLY the verified data from the audit phase and the critic's approved findings. Creates the final report that answers:
- Where does the astrological signature perfectly explain the psychological patterns?
- What's the strength of the correlation?
- How are the blind-spots resolved?

### Phase 4: EXTRACTION + FILING

| Agent | Role | Action |
|-------|------|--------|
| `insight-extractor` | Golden Thread Miner | Extracts the golden thread + top 3 insights (technical, psychological, convergence) |

The insights are:
1. Parsed as structured JSON
2. Written as dated `.md` files into the appropriate `Knowledge/*-Database/` folders
3. Appended to each database's `index.md` for future retrieval

---

## The Agent Roster (by project name)

| Project Name | Agent Type | Role | Stage |
|-------------|------------|------|-------|
| **Plawan** | `idea-generator` | Idea → Blueprint → Execution Packet | 1, 2a |
| **Nut** | `astrology-assistant` | Technical astrology extraction | 2c-Gathering |
| **CK** | `research-specialist` | Psychological extraction | 2c-Gathering |
| **Arm** | `audit-researcher` | Forensic fact-checking | 2c-Audit |
| **Nan** | `research-critic` | Adversarial logic review | 2c-Audit |
| **Bella** | `project-writer` | Convergence synthesis | 2c-Synthesis |

Plus operational agents:
| **Eng** | Pipeline orchestrator, CLI tools, indexing |
| **Ekae** | Preference and project-operations collaborator |
| **Bed** | (Not detailed in agent files) |

---

## Key Design Principles

1. **NotebookLM is the data source, not the analyst** — NotebookLM provides raw Q&A material. Every claim is then extracted, cross-referenced, audited, and stress-tested by specialized agents using the local knowledge base.

2. **Dual-track parallel processing** — Astrology and Psychology are analyzed independently by specialists, then audited by independent reviewers, before being synthesized. This prevents one lens from biasing the other.

3. **Two layers of audit** — Arm checks factual accuracy (calculations, citations). Nan checks logical consistency (reasoning, gaps). Both must pass before synthesis.

4. **Evidence grading** — Every claim is graded [PROVEN]/[PLAUSIBLE]/[UNVERIFIED]. Only [PROVEN] and [PLAUSIBLE] data reaches the final report.

5. **Closed-loop knowledge management** — Insights extracted from research are filed back into the Knowledge databases, making future research stronger.

6. **Boom approves everything** — No output is published, sent, or made consequential without Boom's approval. The pipeline produces drafts for review.

---

## Command Interface

The pipeline is controlled through opencode commands:

| Command | What it does |
|---------|-------------|
| `/ideate <topic>` | Stage 1 only — generate blueprint |
| `/bridge <blueprint>` | Stage 2a only — create execution packet |
| `/query <questions.json>` | Stage 2b only — run NotebookLM queries |
| `/analyze <results>` | Stage 2c only — full analysis |
| `/pipeline <topic>` | Full pipeline: ideate → bridge → query → analyze |

Or run the Node script directly:
```
node .claude/workflows/run-pipeline.js "<topic>" [ideate|bridge|analyze|full]
```

---

*Generated 2026-08-14 — for Boom's reference*
