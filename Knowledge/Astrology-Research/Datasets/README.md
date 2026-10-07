---
title: "Astro-Databank Scientist vs Athlete dataset"
date: "2026-08-26"
type: "source-package"
stage: "Source"
topic: "astrology-ml-blindtest"
tags: [boom, astrology, ml, dataset]
source_classes: [external-web-material]
status: "clean-with-boundaries"
summary: "59 birth records (29 scientists: Physics/Math, 30 athletes: Boxing/Tennis) scraped from Astro-Databank for occupation blind-test experiment."
---

# Astro-Databank: Scientist vs Athlete

- Source: astro.com/astro-databank (Rodden collection), scraped 2026-08-26 via browser
- Categories: `Vocation : Science : Physics` + `Mathematics/Statistics`; `Vocation : Sports : Boxing` + `Tennis`
- 59 records JSONL fields: name, born (date+time ICT-naive local), place (lat/lon string), rating (Rodden), label
- Ratings: AA=40, A=4, B=1, C=6, X=7 — filter AA for high-quality analysis
- License: ADB grants copy/reuse of birth data records for research (see their Copyright notice)

Known limitation: first-N alphabetical sampling — not random; fine for pilot blind test, not population inference.
