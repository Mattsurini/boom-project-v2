---
name: boom-grill-me
description: Grill a loose Boom Project idea into decisions — routes to Plawan/Nut/CK/Arm/Nan/Bella/Ekae/PAC/Transit/Sources pipeline stages, respects startup protocol and token-economy indexing.
version: 0.1.0
author: BooM Project, Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [productivity, ideation, decision-making]
    related_skills: [boom-auto-workflow-router, astro-pipeline, Ekae]
---

# Boom Grill Me Skill

## When to Use
- You have a loose Boom Project idea that needs to be sharpened into actionable decisions
- You want to route ideas through the appropriate Boom Project pipeline stages (Plawan, Nut, CK, Arm, Nan, Bella, Ekae, PAC, Transit, Sources)
- You need to ensure compliance with the mandatory startup protocol (`boom-auto-workflow-router`)
- You want to follow token-economy indexing practices

## Prerequisites
- Understanding of the Boom Project mandatory startup protocol
- Familiarity with Boom Project token-economy indexing
- Knowledge of the canonical Output folders: Plawan, Nut, CK, Arm, Nan, Bella, Ekae, PAC, Transit, Sources

## How to Run
- Use this skill when you have a loose idea that needs to be grilled into decisions
- The skill will guide you through rounds of questioning until you can commit to a decision
- After grilling, route the idea to the appropriate pipeline stage

## Quick Reference
- Start every interaction with `boom-auto-workflow-router`
- Follow the grilling process in rounds
- Route output to appropriate canonical Output folder

## Procedure
1. **Start with the mandatory startup protocol**: Every interaction must begin with `boom-auto-workflow-router`
2. **Present your loose Boom Project idea** for grilling
3. **Enter grilling rounds**: Each round asks specific questions to sharpen the idea:
   - Round 1: What is the core problem or opportunity this idea addresses?
   - Round 2: How does this align with BooM's identity (SOUL.md) and mission (TURBOZ.md)?
   - Round 3: Which canonical Output folder(s) should this idea route to? (Plawan, Nut, CK, Arm, Nan, Bella, Ekae, PAC, Transit, Sources)
   - Round 4: What resources or skills are needed to execute this idea?
   - Round 5: What are the potential risks or challenges?
   - Round 6: How does this idea comply with token-economy indexing rules?
   - Round 7: What specific, actionable next steps can be committed to?
4. **Route to pipeline stage**: Based on your answers, direct the idea to the appropriate Output folder
5. **Apply token-economy indexing**: After creating markdown artifacts, run the Eng/Libby agent workflow:
   - `python scripts/libby/cli.py --once` — classify new Output markdown + add minimal frontmatter
   - `python scripts/build-output-index.py` — rebuild legacy pipeline indexes
   - `python scripts/project_index.py` — rebuild token-economy manifest/router
   - `python scripts/memory_db.py sync-manifest` — sync manifest paths/metadata/hashes into `cache/boom_project_registry.sqlite3`
   - `python scripts/memory_db.py status` — verify registry integrity/counts

## Pitfalls
- Skipping the mandatory startup protocol (`boom-auto-workflow-router`)
- Not routing ideas to canonical Output folders (creating alias folders like `idea-generator` is prohibited)
- Ignoring token-economy indexing rules (must inspect `Knowledge/indexes/PROJECT_INDEX.md` first)
- Failing to engage Ekae for preference and project-operations collaboration when dependency, conflict, or external side effect materially changes the outcome
- Not verifying files, commands, counts, and external side effects before reporting completion

## Verification
- Verify that every interaction started with `boom-auto-workflow-router`
- Confirm that the idea was routed to a canonical Output folder (not an alias folder)
- Check that token-economy indexing procedures were followed
- Validate that Ekae was consulted when appropriate for preference and project-operations alignment
- Ensure outputs were classified via Eng/Libby workflow and added to token-economy manifest