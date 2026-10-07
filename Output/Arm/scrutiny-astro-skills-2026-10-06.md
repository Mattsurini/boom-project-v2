---
date: '2026-10-06'
agent: turboz
type: audit
target: astro-skills
---

# Scrutiny Report — astro-* skill set (pipeline, knowledge-db, natal-chart, synastry)

Outsider review of the four `astro-*` skills against the code they claim to
document. Read-only on claims, but **fixes were applied** (see "Fixed").

## Intent

Four skills that let an agent (a) run the Convergence research pipeline, (b)
quote classical texts, (c) calculate natal charts, (d) run synastry — each with a
documented contract an agent will follow literally.

## Verdict before fixes: the docs and the code had drifted far apart. Every one
of the four documented at least one interface or environment fact that is false on
this host, and two of them (synastry, knowledge-db) would send an agent into dead
ends or silently wrong numbers.

---

## BLOCKER 1 — `astro-knowledge-db` documented a CLI that does not exist

**Claim (old SKILL.md):** `python scripts/astrology_db.py --help`,
`--list`, `--planet Venus`, `--sign Libra --chapter 10`.

**Reality:** `scripts/astrology_db.py` is a **library only** — no `__main__`,
no `argparse`, no `sys.argv` handling (`grep -nE "__main__|argparse|add_argument"` → no match).
Running it with any flag produces *no output and no error*. The real CLI is a
different script, `scripts/query_db.py "<query>"`, which the old doc never
mentioned.

**Why it matters:** any agent following the skill literally gets an empty result
and concludes the classical-text DB is empty or the query is unsupported — exactly
the wrong conclusion.

**Fixed:** rewrote the skill around `query_db.py`, flagged `astrology_db.py` as
import-only, documented the Python-import path, and pinned the actual coverage.

## BLOCKER 2 — the astrology DB index was stale; 182 of 187 entries pointed at files that no longer existed

**Evidence:** index `Knowledge/indexes/astrology_db_index.json` (built 2026-08-01,
187 entries). Resolved each `path` against `Knowledge/Astrology-Database/`:
**182 missing, 5 present.** A live `query_db.py "Jaimini Chara Dasha"` printed
`Found 9 relevant file(s)` then `(no exact keyword matches in file — file is
relevant via index topic)` for every one and `Returned 0 excerpts` — the index
had drifted from the filesystem after files were moved into topic folders.

**Fixed:** rebuilt via `scripts/build_db_index.py` → **197 entries, 197/197 resolve
on disk, 0 missing.** Same query now returns 17 excerpts / ~9.7k chars. Four probe
queries (`Chara Dasha`, `Jaimini`, `Venus`, `BPHS Upapada`) all return real excerpts.
Backup of the stale index kept at `$TMPDIR/astrology_db_index.json.bak`.

**Residual, documented not fixed:** the index covers **197 `.md` files only**
(`build_db_index.py:119` walks `*.md`); **185 PDFs in `Knowledge/Astrology-Database/`
are not indexed** and are never content-read. Flag `[NOT IN DB]` for PDF-only
sources. This is intentional per `.hermes.md`, so it is now stated in the skill
instead of being a silent trap.

## BLOCKER 3 — `astro-synastry` scored every cross-aspect twice and dropped all same-planet pairs

**Evidence (identical charts, BooM vs himself, before fix):**
```
✅ △ Sun-Moon (trine, orb 2.7°)
✅ △ Moon-Sun (trine, orb 2.7°)     ← same aspect, counted again
✅ ☌ Sun-Sun / Moon-Moon / Venus-Venus: absent
```
Root cause in `calc_synastry_aspects`: `if p1_name == p2_name: continue` deleted
every same-planet pair — precisely the highest-weighted pairs in `KEY_PAIRS`
(Sun-Sun 3.0, Moon-Moon 3.0) — while the double loop over `(p1,p2)` and `(p2,p1)`
counted every cross-aspect **twice**.

**Why it matters:** the printed "KEY SYNASTRY ASPECTS" list and the 0–100 score were
both inflated; a synastry reading would systematically over-credit cross-aspects
and silently omit the Sun-Sun/Moon-Moon/Venus-Venus signatures.

**Fixed:** each unordered pair now scored exactly once, kept in the canonical
orientation so labels and the interpretation table still resolve. Regression run:
identical charts → 29 aspects, **0 duplicated pairs**, exactly 1 `Sun-Sun`,
`Moon-Moon`, `Venus-Venus`, `Mars-Mars` conjunction each; cross-chart → 18 aspects,
0 dupes; deterministic across repeats.

## MAJOR 4 — `astro-synastry` house-overlay headers were swapped

`calc_synastry()` computes `overlaps_1 = partner1 planets in partner2 houses`, but
`format_synastry` printed `overlaps_2` under the header
`PLANETS OF {name1} IN THE HOUSES OF {name2}` and vice versa. Verified after fix:
BooM's Venus (Libra) → house 4 under the BOOM/PARTNER header; Partner's Venus →
house 5 under the PARTNER/BOOM header. Both directions now match their labels.

## MAJOR 5 — `astro-natal-chart` required things this host does not have

**Claim:** Python **3.14.x**, bundled `swisseph.cp314-win_amd64.pyd`, MSVC++ 2015–2022 redist, bundled `.pyd.dat`.

**Reality (verified):** Boom `.venv` is **Python 3.11.16**; there is **no** `.pyd`
or `.pyd.dat` in the skill's `scripts/` at all. The script works because its loader
falls back to `import swisseph`, which resolves to
`E:\Boom Project\.venv\Lib\site-packages\swisseph.cp311-win_amd64.pyd`
(pyswisseph **2.10.03**). Also documented `ChiangRai` as a valid city — it is not;
`find_city` wants hyphenated lowercase `chiang-rai` (`ChiangRai` → `City not found`).

**Also flagged (not changed — behaviour, not docs):** the engine is **tropical +
Placidus, no ayanamsa** (`calc_houses` hardcodes `b'P'`, `FLG_SWIEPH`); timezones
are a **fixed static table**, not historical, so DST-affected or pre-rule-change
births get the wrong UTC instant; and its aspect-orb table (conj 8 / sq 7 / sext 5)
does **not** match Boom's own engine (`hermes_astro.PLANET_ORBS` Sun 15 / Moon 12 /
Merc 7 / Venus 7 / Mars 8 / Jup 9 / Sat 9) or the `BOOM_FULL_ORBS` reference set.
All four now stated in the skill so no one treats these numbers as Boom's reference.

## MAJOR 6 — `astro-synastry` documented CLI, orb table and scoring formula that don't match the script

- **CLI:** doc said `synastry.py --chart1 chart1.json --chart2 chart2.json`. There
  is no argparse; it takes **6 positional args** (`date1 time1 city1 date2 time2 city2`,
  dates `DD.MM.YYYY`) plus 2 optional display names. Doc corrected with a verified run.
- **Orbs:** doc omitted that `semisquare`/`quincunx` are ±1.5° (matches) but listed
  nothing about sextile ±4 / square ±6 — corrected to the exact `SYNSTRY_ORBS` table.
- **Key-aspect list:** doc listed ASC—ASC and MC—MC as "most important".
  `calc_synastry_aspects` iterates only `chart["planets"]` (ten bodies) — `asc`/`mc`
  are separate keys and **never compared**, so neither aspect can ever appear, and
  `MC`/`IC` in the sphere lists never match. Doc now says so explicitly.
- **Scoring:** doc's "+3-5 per trine / Sun-Moon +5-8" additive list does not exist.
  Actual: `ASPECT_SCORES[type] * KEY_PAIRS weight`, normalised by the pair's own
  aspect total, `50 + raw*0.5`, clamped 10–95. Real spread measured over 60 random
  chart pairs: **44–91, median 79** — so it is a *relative* indicator, not a
  calibrated "X% compatible". Sphere mapping `5 + raw*1.5` saturates at 10 readily
  (four of five spheres printed 10/10 on the BooM/Izhevsk sample).

## MAJOR 7 — `astro-pipeline` pointed at seven skills that were deleted on 2026-10-06

The 2026-10-06 consolidation merged `astro-agent-{plawan,nut,ck,arm,nan,bella,bed}`
into `astro-pipeline` itself (text archived in `.rebuild/legacy_skill_texts.txt`),
but the skill still said "load the matching `astro-agent-*` skill" at every stage and
listed all seven in `related_skills`. `ls skills/astro-agent-*` → **no such
directory**. An agent following the text would fail every stage. Stage headings now
name the agent roles, with an explicit "do not `skill_view` them" warning.

## MAJOR 8 — `notebooklm-run.js` crashed on the packet format actually in the repo

**Evidence:** `Output/Plawan/Astrology/20260809-retrograde-pipeline-v2-questions.json`
uses `"questions": ["What do classical sources say about Vakri?", ...]` (plain
strings) plus a `topic` key, not the `{id, phase, prompt}` objects the script
expected. Run → `TypeError [ERR_INVALID_ARG_TYPE]` inside `writeTempPrompt(q.prompt)`
because `q.prompt` was `undefined`. The 2026-08-01 packet has the same shape.

**Fixed:** `normalizeQ` accepts strings, `{prompt}` objects, and rejects anything
else with a named error; `title` falls back to `topic`; empty question list fails
loudly instead of silently doing nothing. Verified: strings packet and object packet
both parse and reach the CLI (then stop at `AUTH_REQUIRED`, see below); malformed
entry → `Error: question #1 in bad.json is neither a string nor {prompt: ...}`.

**Also fixed in the doc, and still a live risk:** the skill claimed results land in
`Output/Plawan/Astrology/`; the script writes `Output/NotebookLM/` (`notebooklm-run.js:8`).
Documented the real path and warned that the run is deduped by `slug` — without an
explicit `slug` two different topics that slugify the same silently skip the query.

---

## Verified working, unchanged

- `natal_chart_swe.py` — correct text + `--json` output for `20.11.1996 20:37 chiang-rai`;
  ASC Cancer 11°42′, Sun Scorpio 28°31′, Venus Libra 26°55′ (matches BooM's known chart).
- `draw_wheel.py` — renders 5760×2880 PNG from `--json` (warns only about the
  absent `frame_small.png.dat`, which is a cosmetic QR overlay).
- `query_db.py` / `astrology_db.py` — now working against a correct index.
- `synastry.py` — end-to-end after the three fixes above.
- NotebookLM stage is **blocked, not broken**: `notebooklm.exe metadata` →
  `Not logged in` / `AUTH_REQUIRED`. Needs `notebooklm login` + `notebooklm use <id>`.
  Stages 1, 2a and 2c still run; only 2b needs it. Now stated in the skill.
- `config/agents.json` (Plawan/Nut/CK/Nan/Arm/Bella/Sandee/Eng/Ekae/Bed) is the live
  agent registry the skill defers to — consistent with the consolidated stage table.

## Not fixed (needs BooM's call)

- **`astro-synastry` scoring model itself** — normalisation-by-own-aspect-count and
  the saturating sphere mapping produce 79-median, mostly-10/10 output. The math is
  now documented honestly, but if you want the number to mean something it needs a
  redesign (e.g. weight *rare* harmonious aspects above dense ones, calibrate against
  a baseline). That is a judgement call about what synastry is for, not a bug.
- **PDF sources still unindexed** (185 files) — intentional per `.hermes.md`; if you
  ever want text extraction from them, that is a new decision.
- **`hermes-astro-hub/skills/` mirror drift** — the same class of problem as M1 in the
  2026-10-05 audit (`Output/Arm/scrutiny-hermes-astro-hub-2026-10-05.md`): the hub
  mirrors profile skills with no per-file direction guard. Out of scope here, still open.
