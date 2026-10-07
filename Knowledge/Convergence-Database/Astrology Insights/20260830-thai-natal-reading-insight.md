---
title: "Thai Natal Reading Pipeline — Evidence-First Insight"
date: 2026-08-30
domain: Astrology
status: conditional
confidence: LOW
---

# Core Insight / Verdict

**[SYNTHESIS]** สำหรับการอ่านพื้นดวงด้วยโหราศาสตร์ไทย ควรใช้ pipeline แบบ evidence-first ที่แยก 4 ชั้น: calculation-backed chart observation → source-backed Thai rule → interpreter synthesis → unresolved claim. ลำดับที่เหมาะสำหรับโครงการคือ ลัคนา → 12 ภพ → ดาวเจ้าเรือน/ดาวลอย → ภพผสมภพ → มาตรฐานดาว/ดาวคู่ → synthesis แต่ลำดับนี้เป็น **proposed project design** ไม่ใช่หลักสากลของทุกสำนัก

**[SOURCED]** NotebookLM Coverage Gate ผ่านและ native Deep Research ถูกใช้งานจริง; รายงานครอบคลุมสุริยยาตร์, ลัคนา, ภพ 12, ดาวเจ้าเรือน/ดาวลอย, ภพผสมภพ, มาตรฐานดาว และดาวคู่ (`Output/NotebookLM/20260830-thai-natal-reading-coverage.md`). จำนวน sources ที่เห็นเป็น UI/session observations ไม่ใช่จำนวน unique sources ที่ deduplicate

# Evidence Boundaries

- **[SOURCED]** NotebookLM sources confirm topic coverage, not canonical formulas or predictive validity.
- **[SOURCED]** Local classics (Saravali, Uttara-kalamrita, Phaladeepika, BPHS, Jataka-Parijata) are Vedic/Indian cross-references; they must not be relabeled as Thai doctrine (`Output/Nut/Astrology/20260830-thai-natal-reading-technical.md`).
- **[SOURCED]** Arm audit = ⚠️ DISCREPANCIES; Nan critique = ⚠️ NEEDS REVISION. No Thai canonical algorithm, gold standard, blind evaluation, or demonstrated predictive validity was established (`Output/Arm/Astrology/20260830-thai-natal-reading-audit.md`, `Output/Nan/Astrology/20260830-thai-natal-reading-critique.md`).

# Practical / PAC Usage

1. Freeze birth input, timezone, calendar, zodiac, ascendant method, Rahu/Ketu convention, rounding, and school tag.
2. Preserve raw chart values before interpretation.
3. Write each claim as: observation → cited rule → interpretation → disconfirming condition → observable outcome.
4. For client-facing readings, use conditional and agency-preserving language; do not turn a natal placement into a guaranteed event.
5. Keep natal foundation separate from timing methods such as transits, Thaksa/Triwai, or other age systems.
6. Before using a rule in PAC or client content, attach a source locator and label whether it is Thai-school-specific, Vedic cross-reference, fallback web, or synthesis.

# Do / Don't

## Do

- **[SOURCED]** Keep source provenance, rule versions, locators, unresolved flags, and all misses (`Output/CK/Astrology/20260830-thai-natal-reading-methodology.md`).
- Use blind/holdout evaluation, preregistration, baselines, counterexamples, and separate measures for reliability, predictive accuracy, reflective usefulness, and harm.
- Preserve conflicting school versions as separate models until comparison is justified.

## Don't

- Do not call a source “classical” without author/edition/text-level verification.
- Do not transfer Vedic dignity/friendship rules into Thai labels automatically.
- Do not treat “21/40 sources” UI counts as independent evidence counts.
- Do not claim causal or deterministic personal outcomes.
- Do not select only successful cases or revise wording after seeing outcomes.
- Do not use client satisfaction or emotional resonance as a substitute for predictive validity.

# Open Blockers / Next Research

- Export and deduplicate the complete NotebookLM source inventory.
- Obtain Thai claim-level locators for Suriyayatra, house lords, ดาวลอย, ภพผสมภพ, standards, and pairs.
- Freeze school scope and calculation conventions; run sensitivity comparisons.
- Define outcome ontology, dataset, sample size, null/baseline, scoring, and holdout protocol.
- Build adversarial cases: rule-present/outcome-absent, outcome-present/rule-absent, conflicts, boundary birth times, and alternative systems.

# Links

- Final convergence: `E:/Boom Project/Output/Bella/Astrology/20260830-thai-natal-reading-convergence-report.md`
- Audit: `E:/Boom Project/Output/Arm/Astrology/20260830-thai-natal-reading-audit.md`
- Critique: `E:/Boom Project/Output/Nan/Astrology/20260830-thai-natal-reading-critique.md`
- Technical: `E:/Boom Project/Output/Nut/Astrology/20260830-thai-natal-reading-technical.md`
- Methodology: `E:/Boom Project/Output/CK/Astrology/20260830-thai-natal-reading-methodology.md`
- NotebookLM coverage: `E:/Boom Project/Output/NotebookLM/20260830-thai-natal-reading-coverage.md`
- External web: `E:/Boom Project/Output/NotebookLM/20260830-thai-natal-reading-external-web.md`
