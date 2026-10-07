---
name: boom-deep-research
description: Two-phase deep research for Boom, routes to pipeline stages.
---

# boom-deep-research

## What it does

`boom-deep-research` runs structured deep research in two phases — **outline** then **deep investigation** — with human-in-the-loop control at every stage. It's designed for Boom Project's astrology, psychology, convergence, and content research workflows.

Unlike generic deep research, this skill:
- Routes output to canonical Boom Output folders (Plawan, Nut, CK, Arm, Nan, Bella, Ekae, PAC, Transit, Sources)
- Integrates with Eng/Libby token-economy indexing
- Respects mandatory startup protocol and context-economy rules
- Leverages Boom's astrology scripts and Knowledge database

## When to reach for it

Invoke by typing `/boom-deep-research <topic>` in a fresh conversation.

Use for:
- **Astrology literature surveys** — classical texts, modern interpretations, cross-system comparisons
- **Transit/financial astrology backtesting** — historical correlation studies
- **Psychological archetype mapping** — CK/Nut extraction across chart collections
- **Convergence hypothesis testing** — Bella synthesis across astrology + psychology + ML
- **Content strategy research** — PAC/Transit topic gaps, audience analysis
- **Tooling/script evaluation** — which calculations, APIs, databases to adopt

## Phase 1: Outline Generation (`/boom-deep-research`)

### Step 1: Initial Framework from Model Knowledge + Boom Context
Based on topic + BooM natal (1996-11-20 20:37 ICT, Chiang Rai, Cancer Rising 11.7°, Venus ♎ 26.9°), generate:
- **Research objects/items list** — what to investigate (e.g., classical texts, planetary combinations, house systems, timing techniques)
- **Field framework** — dimensions to research each item (e.g., source, tradition, reliability, applicability, citations)

Output for your confirmation via AskUserQuestion:
- Add/remove items?
- Does field framework meet requirements?
- Target Output folder? (Plawan/Nut/CK/Arm/Nan/Bella/Ekae/PAC/Transit/Sources)

### Step 2: Web Search + Knowledge Base Supplement
Ask for time range (e.g., last 6 months, since 2020, classical only, unlimited).

Launch web-search-agent with Boom-enhanced prompt:
```python
prompt = f"""## Task
Research topic: {topic}
Current date: {YYYY-MM-DD}
BooM natal: 1996-11-20 20:37 ICT, Chiang Rai (19.91°N, 99.83°E)
Cancer Rising 11.7°, Venus ♎ 26.9°

Based on the following initial framework, supplement latest items and recommended research fields.

## Existing Framework
{step1_output}

## Goals
1. Verify if existing items miss important objects in this domain
2. Supplement items based on missing objects
3. Search for {topic} related items within {time_range} and supplement
4. Supplement new fields relevant to Boom Project

## Boom-Specific Search Priorities
- Classical Vedic texts (Parashara, Jaimini, Nadi, Bhrigu)
- Western/Uranian/Hamburg School sources
- KP/Prashna/horary techniques
- Financial/market astrology correlations
- Psychological/archetype mappings
- Cross-system convergence evidence

## Output Requirements
Return structured results directly (do not write files):

### Supplementary Items
- item_name: Brief explanation (why it should be added, Boom relevance)
...

### Recommended Supplementary Fields
- field_name: Field description (why this dimension is needed for Boom)
...

### Sources
- [Source1](url1) — classical text, paper, article, database entry
- [Source2](url2)
"""
```

### Step 3: Existing Fields / Knowledge Index Check
Ask if you have existing field definitions or want to pull from `Knowledge/indexes/` (PROJECT_INDEX.md, project_manifest.json, FRONTMATTER_SCHEMA.md).

### Step 4: Generate Outline Files
Merge Step 1 + Step 2 + existing fields, generate two files in `Output/Sources/{topic_slug}/`:

**outline.yaml** (items + config):
```yaml
topic: "{topic}"
boom_natal: "1996-11-20 20:37 ICT, Chiang Rai (19.91°N, 99.83°E)"
target_output_folder: "Plawan"  # or Nut, CK, Arm, Nan, Bella, Ekae, PAC, Transit, Sources
items:
  - name: "Parashara Hora Shastra"
    category: "Vedic Classic"
    description: "Foundational Vedic astrology text"
    priority: high
    boom_relevance: "Core reference for natal/rectification work"
  - name: "Saturn-Jupiter Conjunction 2020"
    category: "Transit Event"
    description: "Great Conjunction at 0° Aquarius"
    priority: high
    boom_relevance: "Transit timing for PAC content"
execution:
  batch_size: 3          # parallel agents per batch (confirm)
  items_per_agent: 2     # items per agent (confirm)
  output_dir: "./results"
  use_boom_scripts: true # natal_chart.py, transit_timeline_v2.py, etc.
```

**fields.yaml** (field definitions):
```yaml
field_categories:
  - category: "Source Metadata"
    fields:
      - name: "source_title"
        description: "Full title of source text/article"
        detail_level: "moderate"
      - name: "tradition"
        description: "Vedic/Western/Uranian/KP/Nadi/Chinese"
        detail_level: "brief"
      - name: "reliability"
        description: "Source credibility assessment"
        detail_level: "detailed"
      - name: "citations"
        description: "Key passages, verses, page numbers"
        detail_level: "detailed"
  - category: "Boom Applicability"
    fields:
      - name: "natal_relevance"
        description: "How this applies to BooM's Cancer Rising/Venus Libra chart"
        detail_level: "detailed"
      - name: "pac_potential"
        description: "Can this generate PAC/Transit content?"
        detail_level: "moderate"
      - name: "convergence_score"
        description: "Cross-domain synthesis potential (astrology+psychology+ML)"
        detail_level: "moderate"
      - name: "script_integration"
        description: "Which Boom scripts can operationalize this (natal_chart, transit_timeline, tarot_engine, astrology_db)"
        detail_level: "brief"
uncertain_fields: []  # auto-filled in deep phase
```

### Step 5: Save and Confirm
- Create `Output/Sources/{topic_slug}/`
- Save `outline.yaml` and `fields.yaml`
- Show to you for confirmation before Phase 2

## Phase 2: Deep Investigation (`/boom-deep-research-deep`)

### Step 1: Auto-locate Outline
Find `Output/Sources/{topic_slug}/outline.yaml`, read items + config.

### Step 2: Resume Check
Check completed JSON files in `outline.execution.output_dir` (default `Output/Sources/{topic_slug}/results/`). Skip completed items.

### Step 3: Batch Execution
- Batch by `batch_size` (ask approval before each batch)
- Each agent handles `items_per_agent` items
- Launch research agents in parallel (background, task output disabled)

**Agent Prompt Template** (strict reproduction, variables only):
```python
prompt = f"""## Task
Research {item_related_info}, output structured JSON to {output_path}

## Field Definitions
Read {fields_path} to get all field definitions

## Boom Context
- BooM natal: 1996-11-20 20:37 ICT, Chiang Rai (19.91°N, 99.83°E)
- Cancer Rising 11.7°, Venus ♎ 26.9°
- Target output folder: {target_output_folder}
- Available Boom scripts: natal_chart.py, transit_timeline_v2.py, tarot_engine.py, astrology_db.py, eclipses.py

## Output Requirements
1. Output JSON according to fields defined in fields.yaml
2. Mark uncertain field values with [uncertain]
3. Add uncertain array at end of JSON, listing all uncertain field names
4. All field values in English
5. For classical texts: cite book/chapter/verse or page
6. For transit/financial: include date ranges, orbs, house systems used
7. For psychological: map to archetype, cognitive pattern, or CK framework

## Output Path
{output_path}

## Validation
After JSON output, run validation:
python scripts/validate_boom_research.py -f {fields_path} -j {output_path}
Task complete only after validation passes.
"""
```

### Step 4: Consolidation + Eng/Libby Indexing
After all items complete:
1. Consolidate results into `Output/Sources/{topic_slug}/consolidated.json`
2. Generate human-readable report in target Output folder (e.g., `Output/Plawan/{topic_slug}.md`)
3. Run Eng/Libby workflow:
   ```bash
   python scripts/libby/cli.py --once
   python scripts/build-output-index.py
   python scripts/project_index.py
   python scripts/memory_db.py sync-manifest
   python scripts/memory_db.py status
   ```

## Complementary Commands

| Command | Purpose |
|---------|---------|
| `/boom-deep-research-add-items` | Supplement items to existing outline |
| `/boom-deep-research-add-fields` | Supplement fields to existing fields.yaml |
| `/boom-deep-research-deep` | Start deep research phase |
| `/boom-deep-research-report` | Generate final report from completed research |

## Boom Project Integration Points

### Mandatory Startup Protocol (every session)
1. Run `boom-auto-workflow-router`
2. Read `SOUL.md` and `TURBOZ.md`
3. Consult `.hermes.md` and `BOOM_PERSONAL_OPERATING_SYSTEM.md`
4. Restore relevant memory/session context
5. Load task-specific skills (astro-knowledge-db, astro-pipeline, etc.)
6. Apply context-economy rules
7. Turboz + Ekae collaborate automatically
8. Verify files, commands, counts, external side effects

### Token-Economy Indexing (after artifacts produced)
- `python scripts/libby/cli.py --once` — classify + frontmatter
- `python scripts/build-output-index.py` — legacy indexes
- `python scripts/project_index.py` — manifest/router
- `python scripts/memory_db.py sync-manifest` — registry sync
- `python scripts/memory_db.py status` — verify

### Database Ownership
- `cache/boom_project_registry.sqlite3` — Eng-owned Project registry
- `cache/hermes_memory.sqlite3` — Hermes runtime memory (do NOT edit from Eng)
- Neither stores raw PDF/file bodies; files remain source of truth

### Canonical Output Folders (use these, not aliases)
- `Output/Plawan/` — idea cards + blueprints
- `Output/Nut/` — technical extraction
- `Output/CK/` — psychological extraction
- `Output/Arm/` — audit reports
- `Output/Nan/` — critique reports
- `Output/Bella/` — convergence reports
- `Output/Ekae/` — preference/ops collaboration
- `Output/PAC/` — ready-to-post IG content
- `Output/transits/` — transit reports
- `Output/Sources/` — raw research captures
- `Knowledge/...` — indexed knowledge base

## Quick-start

```
/boom-deep-research "Saturn transit 10th house career timing for Cancer Rising"

Context:
- Target folder: Transit → PAC
- Time range: last 2 years + classical references
- Scripts needed: transit_timeline_v2.py, natal_chart.py
```
