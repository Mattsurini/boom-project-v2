---
date: '2026-08-01'
tags:
- project
source: hermes-astro-hub/skills/integrated-astrology/references/local-vs-localchart.md
---

# Local Events vs Local Chart

## Meaning split

In this user’s workflow, "Local" can mean two different things:

1. **Local events**
   - Source: Astro-Seek `.ics` files in `~/AppData/Local/hermes/scripts/transit_data/`
   - Output: event list for the day in ICT
   - Use: show `SUMMARY` and time only; do not read `DESCRIPTION` as if it were user-specific truth
   - Typical request wording: "get all of today's Events", "get today's Local"

2. **Local chart**
   - Source: Swiss Ephemeris transit chart cast for the current location
   - Output: current transit planets + the houses they fall in for that location
   - Use: analyze house emphasis, angles, and exact transit tone at that place/time
   - Typical request wording: "what is the Transit like now, which house is each planet in", "current Local chart"

## Guardrail

Never mix these two outputs in the same answer without labeling them explicitly.

- Event list answer → label as **Local events**
- Transit chart answer → label as **Local chart**

If the user only says "Local" and the surrounding request doesn't make the meaning obvious, ask one short clarification question.
