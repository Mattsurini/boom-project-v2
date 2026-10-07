---
agent: Nut
date: '2026-08-30'
tags:
- astrology
- technical-extraction
- chart-analysis
- psychology
- financial-astrology
- ml-ai
- methodology
- critique
- convergence
- technical
- date:2026-08-30
---

# Stage 2A Nut — Technical extraction: Thai natal-reading pipeline

**Date:** 2026-08-30  
**Role:** technical extraction after chart casting; no personal chart calculated  
**Evidence policy:** NotebookLM verification is primary. Local `Classics books/` is a cross-reference only. The listed web pages are fallback/external and secondary. Claims without a locator are marked **[UNRESOLVED]**; interpretation is explicitly marked **[SYNTHESIS]**.

## 1. Scope and provenance

This document extracts only what is supported by the supplied coverage record or by the cited local PDF pages. The NotebookLM coverage record confirms that the gate passed, that native Deep Research was completed, and that the imported notebook showed 21 sources in the verified session. It also records that the Deep Research result exposed 25 discovered sources before import, and that UI counts later varied (21/20/17/10). Therefore, **“21 sources” means the verified imported-notebook state, not a deduplicated unique-source total**. (Source: `E:/Boom Project/Output/NotebookLM/20260830-thai-natal-reading-coverage.md`, §§Verified live state, Known limitations, lines 7–13 and 23–27.)

### Source inventory

#### A. Primary working evidence: verified NotebookLM coverage

- Notebook: `การอ่านพื้นดวงด้วยโหราศาสตร์ไทย` (new Auth context); coverage status PASS. (Source: `E:/Boom Project/Output/NotebookLM/20260830-thai-natal-reading-coverage.md`, lines 3–5.)
- Native Deep Research result: `ศาสตร์แห่งการพยากรณ์พื้นดวงในโหราศาสตร์ไทย: การสังเคราะห์โครงสร้างดาว ภพ และการผูกสัมพันธ์ดวงชะตาเชิงลึก`. (Source: same file, lines 7–10.)
- Verified topic coverage: Thai/Suryiyatra chart construction (horakhun, mthayom, somphut, ascendant, Antonate, house placement); 12 houses/basic meanings; house lords, ดาวลอย, ภพผสมภพ; planetary standards เกษตร/อุจ/นิจ/ประ/มหาจักร/ราชาโชค; planetary pairs มิตร/ศัตรู/สมพล; beginner and practitioner materials. (Source: same file, §Coverage areas present, lines 15–20.)
- Titles explicitly recorded as seen live or relevant: `E-Book ถอดรหัสภพ`, `วิธีพยากรณ์แบบภพผสมภพ`, `มาตรฐานดาว - วิกิพีเดีย`, `โหราศาสตร์ไทย เรียนด้วยตนเอง อ.สิงห์โต สุริยาอารักษ์`, plus the Deep Research report above. The coverage file does **not** provide author, edition, publication date, or per-claim page/section locators for these items. Their provenance/classical status is consequently **[UNRESOLVED]**, and they are not called classical here. (Source: `.../20260830-thai-natal-reading-coverage.md`, lines 10–12; project brief supplied with task.)
- NotebookLM limitations: source labels varied by UI state; some materials were secondary web pages, social posts, or generated reports; full export and claim-level locators remain needed. (Source: same file, lines 23–27.)

#### B. Local cross-reference: classical database

The local folder contains English translations/scans of Indian/Vedic astrology works, but no Thai-specific/Suryiyatra textbook was identified in the supplied `Classics books/` inventory. These texts can support general concepts such as bhava/lords, dignity, friendship, and varga calculation; they do **not** by themselves establish a Thai-school rule, a Suriyayatra algorithm, or a Thai house-mixing formula.

Files consulted/cross-referenced:

- `E:/Boom Project/Knowledge/Astrology-Database/Classics books/Kalyana Varmas Saravali.pdf`
- `E:/Boom Project/Knowledge/Astrology-Database/Classics books/Uttara-kalamrita-kalidas.pdf`
- `E:/Boom Project/Knowledge/Astrology-Database/Classics books/Mantreswara_Phaladeeplka.pdf`
- `E:/Boom Project/Knowledge/Astrology-Database/Classics books/BPHS-Santhanam-Vol-1.pdf` (contents only for relevant chapters; no Thai-specific rule extracted)
- `E:/Boom Project/Knowledge/Astrology-Database/Classics books/BPHS-Santhanam-Vol-2.pdf` (contents only for relevant chapters; no Thai-specific rule extracted)
- `E:/Boom Project/Knowledge/Astrology-Database/Classics books/Jataka-Parijata-Vol-1.pdf` (contents/terminology cross-check; no Thai-specific rule extracted)

The inventory also contains other PDFs, but they were not used as evidence for a Thai-specific claim. The local corpus is therefore a **cross-reference**, not proof that the Thai sources derive from these works.

#### C. Fallback/external web evidence

All three are secondary/external and must remain labeled that way:

1. `https://www.horawej.com/index.php?lay=show&ac=article&Id=107034&Ntype=3` — practitioner material reportedly mentioning Thai/Lahiri chart casting and natal examples; exact page-level claims were not extractable in this run, so all technical details are **[UNRESOLVED]**. (Source: `E:/Boom Project/Output/NotebookLM/20260830-thai-natal-reading-external-web.md`, lines 6–8.)
2. `https://astro.meemodel.com/ดูดวงโหราศาสตร์ไทย/` — secondary overview reportedly covering houses, ascendant, 12-house sequence, and sidereal context; extraction returned mostly page navigation and no reliable claim-level locator. Treat as **[UNRESOLVED]/fallback**, not authority. (Source: same file, lines 7–8; web extraction result.)
3. `https://www.baankhunyai.com/17244675/๓-ลัคนา` — school-specific article by/attributed to อ.อรุณ ลำเพ็ญ. The extracted page states a three-ascendant framework: ลัคนา, ตนุลัคน์, ตนุเศษ; it describes checking more than the ascendant alone and assigns distinct interpretive roles. This is external/school-specific evidence, not a universal Thai standard. (Source: same file, lines 8–14; extracted page heading and body under `# ๓ ลัคนา`.)

## 2. Chart / method observations

These are observations about the verified research coverage and the proposed extraction pipeline, not assertions that every Thai school uses one canonical method.

### 2.1 Input and chart-construction layer

The verified NotebookLM coverage says the Thai/Suryiyatra construction area includes horakhun, mthayom, somphut, ascendant, Antonate, and house placement. It does not provide formulas, tables, epoch, timezone convention, ayanamsa value, or rounding rules. (Source: `.../20260830-thai-natal-reading-coverage.md`, §Coverage areas present, lines 15–16.)

**Operational extraction:** retain, at minimum, birth date, local clock time, birth location, timezone/offset, selected calendar/ephemeris, zodiac mode, ayanamsa/epoch if applicable, and rounding/house-placement convention. This is a reproducibility requirement derived from the brief’s explicit demand to record time, calendar, zodiac, and calculation assumptions; it is not a sourced Thai doctrinal rule. (Source: `E:/Boom Project/Output/Plawan/Astrology/thai-natal-reading-blueprint.md`, lines 39–47; `.../thai-natal-reading-questions.json`, lines 80–84.)

### 2.2 Structural reading layer

The research scope explicitly centers the sequence **ลัคนา → 12 ภพ → ดาวเจ้าเรือน/ดาวลอย → ภพผสมภพ → synthesis**. This is the blueprint’s proposed reading structure, not proof that all schools use this exact order. (Source: `E:/Boom Project/Output/Plawan/Astrology/thai-natal-reading-blueprint.md`, lines 7–12.)

The NotebookLM coverage confirms that 12 houses/basic meanings, house lords, ดาวลอย, and ภพผสมภพ were present in the notebook. It does not supply claim-level definitions or a deterministic formula for combining houses. (Source: `E:/Boom Project/Output/NotebookLM/20260830-thai-natal-reading-coverage.md`, lines 17–19 and 23–27.)

Local cross-reference supports the general need to inspect houses and their lords, but not the Thai mapping:

- `Kalyana Varmas Saravali.pdf`, PDF p. 8, §12: horoscope effects should be predicted according to house divisions and the strength of their lords should be known before proceeding.
- Same file, PDF p. 9, §§25–33: a bhava is described as gaining strength from its lord/friendly lord/Mercury/Jupiter aspect; the page lists synonyms of the 12 bhavas and classifies kendras, panapharas, apoklimas, upachayas, and anupachayas.
- `Uttara-kalamrita-kalidas.pdf`, PDF p. 14, discussion following Sloka 2.14: examine the bhava under consideration, its lord, and its karaka; it also describes examining bhavas from Lagna and Moon Lagna. This is a Vedic cross-reference, not evidence that Thai practice must use Moon Lagna.

### 2.3 Planetary quality layer

Verified NotebookLM coverage names these planetary standards: **เกษตร, อุจ, นิจ, ประ, มหาจักร, ราชาโชค**. It also names planetary relationships **มิตร, ศัตรู, สมพล**, while expressly requiring source-level audit before canonical use. (Source: `E:/Boom Project/Output/NotebookLM/20260830-thai-natal-reading-coverage.md`, lines 19–20.)

Local cross-reference supplies general dignity material:

- `Kalyana Varmas Saravali.pdf`, PDF p. 9, §§34–36: lists moolatrikona signs and exaltation signs/degrees for the seven classical planets, with opposite signs as debilitation places.
- `Uttara-kalamrita-kalidas.pdf`, PDF p. 18, Slokas 2.30–2.31 and notes: gives exaltation/fall-point discussion and caveats about retrograde planets and association with exalted/debilitated planets.
- `Mantreswara_Phaladeeplka.pdf`, PDF pp. 4, 7–9 (table of contents): identifies chapters on lords of signs, moolatrikona, exaltation/debilitation, effects of a planet in bhava, interconnection, conjunctions, and dasa/transit conditions. These pages are chapter locators, not extracted Thai rules.

Do not map the Thai labels directly to the local Vedic dignity scheme without a Thai source locator. In particular, **ประ, มหาจักร, ราชาโชค, and สมพล are [UNRESOLVED as canonical operational rules]**: the coverage confirms their presence, but not thresholds, scoring, exceptions, or school lineage.

### 2.4 Planetary-pair and relationship layer

The notebook coverage confirms that material on friend/enemy/สมพล pairs was present, but says source-level audit is required before canonical use. (Source: `E:/Boom Project/Output/NotebookLM/20260830-thai-natal-reading-coverage.md`, line 20.)

The local texts show why this must be specified rather than assumed:

- `Uttara-kalamrita-kalidas.pdf`, PDF pp. 14–16, Sloka 2.15 and notes: distinguishes natural planetary relationship from temporary relationship based on relative house positions, then combines them into five relationship classes. This is a Vedic reference and must not be relabeled as Thai “คู่มิตร/คู่ศัตรู/คู่สมพล.”
- `Uttara-kalamrita-kalidas.pdf`, PDF p. 16: temporary friendship/enmity is stated as planets occupying the three houses before/after a planet in the birth chart; the same passage notes that some authorities treat occupation of an exaltation sign as friendship. This disagreement itself is a reason to preserve the source/school field.

### 2.5 Varga and auxiliary layer

`Kalyana Varmas Saravali.pdf`, PDF p. 8, §§12–19, describes subdivisions/vargas and gives a longitude-to-varga calculation procedure (convert longitude to arc-minutes, multiply by the relevant varga number, divide by 1800). This can be recorded as a local classical cross-reference only. No verified NotebookLM locator here establishes that this exact formula is part of the target Thai post-casting pipeline. **[UNRESOLVED for Thai use].**

### 2.6 Interpretation and output layer

The blueprint requires separating calculation-backed, source-backed, interpretive, and unresolved claims, and requires non-deterministic wording rather than overconfident predictions. (Source: `E:/Boom Project/Output/Plawan/Astrology/thai-natal-reading-blueprint.md`, lines 24–37 and 39–47.) This is a pipeline governance rule, not a traditional astrological rule.

## 3. Exact technical workflow (evidence-bounded specification)

1. **Freeze provenance and assumptions.** Record source identifier/title, school, author/edition when available, chart calculator, time standard/timezone, calendar, zodiac/ayanamsa/epoch, location, and rounding. If any field is unavailable, emit `[UNRESOLVED]`; do not silently default. The need for this audit trail is explicit in the blueprint and questions. (Source: `.../thai-natal-reading-blueprint.md`, lines 39–47; `.../thai-natal-reading-questions.json`, lines 80–84.)
2. **Cast or import the post-casting chart.** Preserve raw planetary longitudes, ascendant, house placement, and all derived Thai/Suryiyatra components actually used (horakhun, mthayom, somphut, Antonate). The coverage confirms these components as covered topics but does not provide their algorithms. (Source: `.../20260830-thai-natal-reading-coverage.md`, lines 15–16.)
3. **Validate chart identity.** Check that the ascendant and house placement are reproducible under the recorded assumptions; flag any Suriyayatra/Lahiri or school mismatch before interpretation. Exact tolerance and correction procedure are **[UNRESOLVED]**.
4. **Build the structural table.** For each of 12 houses, store house number, subject label, sign/placement under the selected school, occupying planets, house lord, and any karaka/auxiliary indicator. The presence of 12 houses, house lords, and ดาวลอย is NotebookLM-supported; the field definitions and Thai labels need source-level locators. (Source: `.../20260830-thai-natal-reading-coverage.md`, lines 17–18.)
5. **Compute/record ดาวเจ้าเรือน and ดาวลอย.** Do not infer the mapping from a Vedic table unless the chosen Thai source explicitly defines it. Record the source and school for each mapping. Exact Thai lordship and ดาวลอย rules are **[UNRESOLVED]** in the supplied evidence.
6. **Apply ภพผสมภพ only when its formula is specified.** Record the input houses, operation/order, resulting topic, and source locator. The notebook confirms the technique is covered, but no formula or page/section locator is supplied. Therefore no universal house-mixing equation is asserted here. (Source: `.../20260830-thai-natal-reading-coverage.md`, lines 18 and 26.)
7. **Attach planetary quality metadata.** Record each applicable standard (เกษตร/อุจ/นิจ/ประ/มหาจักร/ราชาโชค), relationship (มิตร/ศัตรู/สมพล), and the rule/exception that triggered it. Coverage supports the vocabulary only; operational thresholds are **[UNRESOLVED]**. (Source: same file, lines 19–20.)
8. **Cross-check with non-Thai classics without relabeling.** Use the cited Saravali/Uttara-kalamrita/Phaladeepika pages for comparison of general bhava, lord, dignity, friendship, or varga concepts. Mark every transfer as “Vedic cross-reference,” never “Thai classical.”
9. **Resolve conflicts by school/source priority.** Prefer a directly located Thai/Suryiyatra primary or practitioner source for a Thai rule; otherwise preserve competing versions side-by-side. Exact priority order among Thai schools is **[UNRESOLVED]**.
10. **Synthesize with evidence labels.** Produce separate chart observations, source-backed rules, synthesis, and unresolved claims. Phrase outputs as tendencies/conditional readings unless a tested rule justifies stronger language. (Source: `.../thai-natal-reading-blueprint.md`, lines 24–47.)
11. **Handoff for testing/audit.** Export claim IDs, inputs, rule version, source locator, output wording, and unresolved flags so CK can test operational definitions/blind holdouts and Arm can audit schema, timezone, reproducibility, and traceability. (Source: `.../thai-natal-reading-questions.json`, lines 41–58 and 80–96.)

## 4. Ambiguities and unresolved technical decisions

### Suriyayatra versus Lahiri

- **Verified:** NotebookLM labels the construction coverage Thai/Suryiyatra and explicitly includes Suriyayatra-related material. (Source: `.../20260830-thai-natal-reading-coverage.md`, lines 15–16.)
- **External fallback:** Horawej is recorded as mentioning Thai/Lahiri chart casting, but it is secondary and its exact technical passage was not retrieved. (Source: `.../20260830-thai-natal-reading-external-web.md`, lines 6–8.)
- **Not established:** whether the target pipeline uses Suriyayatra, Lahiri, a Thai ayanamsa variant, tropical/sidereal conversion, a fixed epoch, or a particular correction; how horakhun/mthayom/somphut/Antonate are calculated; and how disagreements change house placement. **[UNRESOLVED]**
- **Required resolution:** export the exact NotebookLM source passage(s), formula/table, edition, and calculator assumptions; run a same-input comparison with explicit longitude deltas and house changes.

### Schools and three ascendants

- The external Baan Khun Yai page presents ลัคนา, ตนุลัคน์, and ตนุเศษ as a three-ascendant approach and says reading only one point is incomplete. This is a school-specific external technique, not a canonical Thai-wide rule. (Source: external URL above; `.../external-web.md`, lines 8–14.)
- Whether the target pipeline should include all three, and how they interact with the primary ascendant/house-lord workflow, is **[UNRESOLVED]**. Do not add it as a mandatory stage without a source-level decision.

### House mixing and “ดาวลอย”

The notebook confirms coverage but supplies no formula, precedence rule, or worked example locator. The exact composition operation, whether house lords or occupants have priority, and how contradictions are resolved are **[UNRESOLVED]**. This is the highest-priority source-export request because it directly affects pipeline outputs.

### Planetary standards and pairs

The vocabulary is confirmed, but the evidence does not fix scoring, dignity hierarchy, orb/association rules, tie-breaking, or exceptions. The local Vedic texts demonstrate multiple relationship/dignity conventions; they cannot settle Thai usage. **[UNRESOLVED]**.

### Deterministic outcomes

No supplied source locator supports deterministic personal outcomes. The blueprint explicitly excludes personal-chart predictions at this stage and requires testing/uncertainty controls. (Source: `.../thai-natal-reading-blueprint.md`, lines 32–37 and 64–72.) Any claim that a placement guarantees a health, financial, relationship, or event outcome is outside this extraction and **[UNRESOLVED]**.

## 5. Claim-to-source matrix

| ID | Claim / rule | Evidence class | Locator | Status |
|---|---|---|---|---|
| C1 | Verified notebook gate passed; imported notebook showed 21 sources, while discovered/UI counts varied | NotebookLM coverage | `.../20260830-thai-natal-reading-coverage.md`, lines 7–13, 23–27 | **PROVEN as session state; not unique-count proof** |
| C2 | Covered construction vocabulary includes horakhun, mthayom, somphut, ascendant, Antonate, house placement | NotebookLM coverage | same, lines 15–16 | **PROVEN as coverage; formulas unresolved** |
| C3 | Covered structural topics include 12 houses, house lords, ดาวลอย, ภพผสมภพ | NotebookLM coverage | same, lines 17–18 | **PROVEN as coverage; definitions/formula unresolved** |
| C4 | Covered standards include เกษตร/อุจ/นิจ/ประ/มหาจักร/ราชาโชค | NotebookLM coverage | same, line 19 | **PROVEN as vocabulary coverage; operational rules unresolved** |
| C5 | Covered pairs include มิตร/ศัตรู/สมพล, pending source audit | NotebookLM coverage | same, line 20 | **PROVEN as coverage; canonical use unresolved** |
| C6 | Read structure proposed as ascendant → 12 houses → lords/ดาวลอย → house mixing → synthesis | Project blueprint | `.../thai-natal-reading-blueprint.md`, lines 7–12 | **PROVEN as project design; not universal doctrine** |
| C7 | Saravali requires house divisions and strength of lords for horoscope prediction | Local Vedic cross-reference | `.../Kalyana Varmas Saravali.pdf`, PDF p. 8, §12 | **PROVEN for cited text; Thai transfer unresolved** |
| C8 | Saravali lists 12-bhava synonyms and house groupings | Local Vedic cross-reference | same, PDF p. 9, §§25–33 | **PROVEN for cited text; Thai transfer unresolved** |
| C9 | Uttara-kalamrita advises examining bhava, lord, and karaka; also mentions Lagna/Moon Lagna | Local Vedic cross-reference | `.../Uttara-kalamrita-kalidas.pdf`, PDF p. 14 | **PROVEN for cited text; Thai mandate unresolved** |
| C10 | Uttara-kalamrita distinguishes natural and temporary planetary relationships | Local Vedic cross-reference | same, PDF pp. 14–16, Sloka 2.15/notes | **PROVEN for cited text; Thai pair mapping unresolved** |
| C11 | External Baan Khun Yai presents three ascendants | External/secondary | URL in §1C; extracted page heading/body | **PROVEN as page claim; school-specific, not universal** |
| C12 | Suriyayatra/Lahiri formula, ayanamsa, epoch, timezone, and conflict behavior | Mixed/insufficient | NotebookLM coverage lines 15–16; external-web lines 6–8 | **UNRESOLVED** |
| C13 | Exact Thai house-mixing formula and ดาวลอย definition | Insufficient | NotebookLM confirms topic only, lines 17–18, 23–27 | **UNRESOLVED** |
| C14 | Exact operational rules for ประ/มหาจักร/ราชาโชค/สมพล | Insufficient | NotebookLM vocabulary only, lines 19–20 | **UNRESOLVED** |
| C15 | Personal deterministic outcome from any placement | Not supported | Blueprint scope boundaries, lines 32–37 | **UNRESOLVED / excluded** |

## 6. Blind-spot resolution and handoff

1. **Missing source-level provenance:** The 21-source state lacks a complete exported inventory with author, edition, date, document type, and locators. Resolve by exporting the notebook source list and tagging each item as primary Thai, practitioner, secondary web, generated report, or unknown. Until then, do not use “classical.”
2. **Missing formulas:** Export exact passages for Suriyayatra construction, house mixing, ดาวลอย, standards, and pairs. A title or coverage label is not enough to instantiate a rule.
3. **System-conversion sensitivity:** Run the same input through every candidate zodiac/time convention and store longitude/ascendant/house deltas. No personal chart is required for this methodological test.
4. **School ambiguity:** Treat the three-ascendant page and any Lahiri reference as optional school-specific variants until NotebookLM or a primary source establishes inclusion and precedence.
5. **Classical mismatch:** Local books are Vedic/Indian cross-references. They help identify concepts and competing conventions, but no Thai-specific claim may cite them as if they were Thai classics.
6. **Testing handoff:** CK should operationalize each rule as a versioned predicate and evaluate blind/holdout cases, agreement, and calibration; Arm should verify input/output schema, units, timezone, reproducibility, conflict handling, and claim traceability; Nan should test alternative explanations, selection effects, hindsight/Barnum effects, and sensitivity to school/calculation changes. (Source: `.../thai-natal-reading-blueprint.md`, lines 44–47 and `.../thai-natal-reading-questions.json`, lines 41–58 and 80–96.)

## 7. Synthesis

**[SYNTHESIS]** The defensible Stage 2A design is an evidence-first, versioned pipeline: freeze calculation assumptions; preserve the raw chart and derived Thai/Suryiyatra fields; inspect ascendant, 12 houses, occupants, lords, and ดาวลอย; apply house-mixing, planetary standards, and pair rules only when each has an explicit source locator and school tag; then synthesize conditional language with unresolved claims visible. The verified NotebookLM record supports the topic architecture and vocabulary, but it does not yet support a single canonical Thai algorithm. Local classics support general comparative concepts, not Thai provenance. External pages can expose school variants—especially three ascendants and Thai/Lahiri references—but remain fallback evidence. No personal chart or deterministic prediction is produced.

## Sources

- `E:/Boom Project/Output/NotebookLM/20260830-thai-natal-reading-coverage.md`
- `E:/Boom Project/Output/NotebookLM/20260830-thai-natal-reading-external-web.md`
- `E:/Boom Project/Output/Plawan/Astrology/thai-natal-reading-blueprint.md`
- `E:/Boom Project/Output/Plawan/Astrology/thai-natal-reading-questions.json`
- `E:/Boom Project/Knowledge/Astrology-Database/Classics books/Kalyana Varmas Saravali.pdf`
- `E:/Boom Project/Knowledge/Astrology-Database/Classics books/Uttara-kalamrita-kalidas.pdf`
- `E:/Boom Project/Knowledge/Astrology-Database/Classics books/Mantreswara_Phaladeeplka.pdf`
- `E:/Boom Project/Knowledge/Astrology-Database/Classics books/BPHS-Santhanam-Vol-1.pdf`
- `E:/Boom Project/Knowledge/Astrology-Database/Classics books/BPHS-Santhanam-Vol-2.pdf`
- `E:/Boom Project/Knowledge/Astrology-Database/Classics books/Jataka-Parijata-Vol-1.pdf`
- External fallback URLs listed in §1C (retrieved/recorded in `20260830-thai-natal-reading-external-web.md`).
