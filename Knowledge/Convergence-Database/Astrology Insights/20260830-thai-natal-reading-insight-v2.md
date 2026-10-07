---
title: "Thai Natal Reading Pipeline — NotebookLM-Backed v2 Insight"
date: 2026-08-30
domain: Astrology
status: conditional
confidence: LOW
evidence_mode: notebooklm-raw-backed
---

# Verdict

**[SYNTHESIS]** Corrective v2 ใช้ raw NotebookLM targeted Q&A และ raw blind-spot sweep เป็น primary inputs จริง ไม่ใช่เพียง coverage metadata แบบ v1. ผลที่ได้คือ pipeline ที่มี candidate sequence และ dependency gates ชัดเจน แต่ยังไม่ใช่ canonical Thai algorithm และยังไม่มี predictive validity

**[SOURCED]** NotebookLM raw targeted Q&A เสนอ candidate sequence: ลัคนา → ตนุลัคน์/ตนุเศษ → ภพ 12/ดาวเจ้าเรือน → ดาวลอย → ภพผสมภพ → มาตรฐานดาว → ดาวคู่ (`Output/NotebookLM/20260830-thai-natal-reading-targeted-qa.md`).

**[SOURCED]** NotebookLM raw blind-spot sweep ระบุ gaps สำคัญ: สูตรคำนวณ, อันโตนาที/time correction, สุริยยาตร์/Lahiri assumptions, mapping ภพผสมภพ, conflict priority, มาตรฐานดาว/ดาวคู่, provenance, benchmark และ gold standard (`Output/NotebookLM/20260830-thai-natal-reading-blind-spot.md`).

# Pipeline Design

1. Freeze input, timezone, coordinate, calendar, zodiac, ascendant method, Rahu/Ketu convention, rounding, and school.
2. Preserve raw chart and derived fields before interpretation.
3. Separate chart observation from source rule and interpreter judgment.
4. Attach source ID, school, locator, conditions, exceptions, and rule version.
5. Use house lords, ดาวลอย, ภพผสมภพ, standards, and pairs only when their rule representation is source-located.
6. Convert claims into conditional, observable hypotheses with disconfirming conditions.
7. Audit provenance and calculation reproducibility before client delivery.
8. Evaluate using preregistered blind/holdout cases, baselines, misses, false positives, false negatives, and harm outcomes.

# Evidence Classes

- **[SOURCED — NotebookLM raw]** What the notebook answered or listed as a blind spot; not automatically a classical rule.
- **[SOURCED — local cross-reference]** Vedic/Indian texts may illuminate general concepts, but do not prove Thai meanings or Suriyayatra formulas.
- **[SOURCED — external fallback]** Secondary web sources and school-specific methods remain fallback evidence.
- **[SYNTHESIS]** Proposed pipeline structure, rule schema, QA gates, and evaluation design.
- **UNRESOLVED** Formula, school precedence, exact Thai mapping, or predictive performance without claim-level source and test evidence.

# Hard Boundaries

- Do not call the NotebookLM report or discovered sources “classical” without author/edition/text verification.
- Do not treat UI counts (21/20/17/10/40) as deduplicated independent-source counts.
- Do not transfer Vedic dignity/friendship rules into Thai rules automatically.
- Do not extrapolate a partial 144-pair house-mixing list into a complete lookup table.
- Do not treat blind-spot output as proof that a rule is absent; verify against source export.
- Do not claim causal or deterministic personal outcomes.
- Do not treat client satisfaction or emotional resonance as predictive validity.

# Current Blockers

1. Complete NotebookLM source export and deduplication.
2. Thai claim-level quotations and locators.
3. Frozen school/calculation specification and executable test vectors.
4. Formal rules for house mixing, ดาวลอย, standards, and planetary pairs.
5. Benchmark dataset, gold standard, outcome ontology, power/sample-size plan, null model, and holdout analysis.
6. Adversarial cases and system-sensitivity comparison.

# Audit State

- Arm v2: **⚠️ DISCREPANCIES** — raw outputs incorporated, but provenance/formula/validation gaps remain.
- Nan v2: **⚠️ NEEDS REVISION** — protocol is plausible, not evidence of rule validity or predictive accuracy.
- Bella v2: **LOW (conditional)** — convergence is strongest at governance and evidence-boundary level.

# Practical Use

For client/PAC work, use only after the selected Thai school, calculation assumptions, and source rule are explicitly tagged. Present foundation reading as conditional tendencies and keep timing methods separate from natal structure.

# Links

- `E:/Boom Project/Output/NotebookLM/20260830-thai-natal-reading-targeted-qa.md`
- `E:/Boom Project/Output/NotebookLM/20260830-thai-natal-reading-blind-spot.md`
- `E:/Boom Project/Output/Nut/Astrology/20260830-thai-natal-reading-technical-v2.md`
- `E:/Boom Project/Output/CK/Astrology/20260830-thai-natal-reading-methodology-v2.md`
- `E:/Boom Project/Output/Arm/Astrology/20260830-thai-natal-reading-audit-v2.md`
- `E:/Boom Project/Output/Nan/Astrology/20260830-thai-natal-reading-critique-v2.md`
- `E:/Boom Project/Output/Bella/Astrology/20260830-thai-natal-reading-convergence-report-v2.md`
- Previous v1 insight: `E:/Boom Project/Knowledge/Convergence-Database/Astrology Insights/20260830-thai-natal-reading-insight.md`
