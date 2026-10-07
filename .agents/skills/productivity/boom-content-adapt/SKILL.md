---
name: boom-content-adapt
description: Rewrite Boom technical content for PAC/Transit audiences.
---

# boom-content-adapt

Rewrite engineer/engineer content for PAC/Transit audiences — Instagram followers, daily briefing readers, transit report consumers — and shape it for the channel: IG caption, carousel slide, story, daily briefing line, transit report summary, or email newsletter.

Use this any time Boom technical content needs to flow outward to public/semi-public channels — regardless of destination.

## When to invoke

- "write something for PAC / Instagram / social"
- "rewrite this for transit briefing / daily summary"
- "make this accessible / less jargony / for followers"
- "send a PAC caption / carousel / story / briefing / newsletter" *about a piece of astrology work*
- "executive summary" / "transit summary" / "PAC blurb" / "content card"
- "talking points for [content piece]" *based on a technical finding*

If the channel is unclear after the trigger, ask one short question — *"PAC caption, carousel, story, briefing, or newsletter?"* — and stop.

## Audience — what "PAC/Transit audience" means

Astrology-interested but not practitioners: Instagram followers, newsletter subscribers, daily briefing readers. They read planet names, sign names, house references, and major aspect keywords. They do not read chart mechanics, calculation details, or classical text citations.

They want: *what's happening, what it means for me, when it peaks, what to do.* They do not want: how the transit is calculated at the degree level.

This is **not** for academic, classical, or practitioner audiences — those need a different rewrite. Flag and confirm before producing one.

## Tone

**Keep.** Planet names, sign names, house references, major aspects, dates, orbs (in plain language), retrograde/station/direct keywords, eclipse/season markers. These are the bridge between technical astrology and public content.

**Strip.** House system names, ayanamsa specifics, calculation methodology, classical text citations (unless famous like "Parashara says"), degree-level precision beyond what's meaningful, technical pipeline references (Plawan/Nut/CK/Arm/Nan/Bella), script names, debug ledgers.

**Translate.** Mechanism into one or two sentences of plain-English cause-and-effect. Not *"Saturn at 15° Pisces applying square to natal Venus at 26° Libra within 2° orb"* but *"Saturn in Pisces is pressing on your Venus in Libra — a tension between structure and relationship that peaks mid-month."* Translate without lying — a square stays a square; a transit stays a transit.

**Don't over-strip.** PAC audience reads concept-level astrology vocabulary fluently — *square, opposition, trine, conjunction, retrograde, station, eclipse, return, progression*. The line is between *concept exists and matters here* (keep) and *here's the exact degree/calculation method* (strip). Replacing "square" with "tension aspect" patronizes the reader.

**Bias toward** active voice, concrete subjects, short paragraphs. *"Saturn squares your Venus. Relationship structures get tested. Mid-month peak."* beats *"A transit configuration involving Saturn and Venus is creating a dynamic that may require attention."*

**Avoid:**

- Hedging that isn't really hedging (*"you may feel," "this could indicate," "it's possible that"*). State it or don't.
- Re-stating the obvious for thoroughness (*"Saturn is the planet of structure, which is important for..."*).
- Telling audience how to live their life (*"you should break up," "this needs to happen before X"*). Give them the facts; they decide.
- Technical-process minutiae: which script generated it, pipeline stage, index rebuild, debug session. They care that it's accurate, not how. (Exception: when the *source* itself is the story — *"this came from a 2000-chart rectification study"* — then a single sentence as authority signal, not a play-by-play.)

## Channel shapes

Same content, different shell. Pick the shape that matches where it's going.

### PAC — Instagram Caption

Single post, scannable. Heavy bolded labels read as "I escaped from a transit report" — don't.

- One **bolded hook** as the first line.
- 3–5 short bullets underneath: what, when, what it means, one action/reflection.
- One key date/degree inline. Not a data wall.
- Hashtags at bottom (3–5 max, relevant).
- No greeting, no signoff. The platform is the context.
- Length target: under ~125 words for caption; carousel slides ~30 words each.

### PAC — Carousel Slide

- Slide 1: Hook + visual cue (planet glyphs, date)
- Slide 2–4: One concept per slide. *"What's happening", "What it means", "Your move"*
- Final slide: CTA — *"Save for the dates", "Share with a Libra rising", "Full report in bio"*

### PAC — Story

- 1–3 frames max.
- Frame 1: Visual + hook (planet + date)
- Frame 2: One-line meaning
- Frame 3: Poll/quiz/sticker for engagement
- Text minimal — visual-first.

### Transit — Daily Briefing Line

The audience scans 5–10 of these in 30 seconds. Front-load the verb.

- 1–2 lines, max.
- Pattern: *"\<planet\> \<aspect\> \<your planet\>. \<peak date\>. \<one-line meaning\>."*
- Examples:
  - *"Saturn square Venus. Relationship structures tested. Peaks Oct 15."*
  - *"Jupiter enters Gemini. Learning expansion begins. 12-month cycle."*
- No bullets, no bolded labels. The format **is** the sentence.

### Transit — Full Report Summary

Subject line is half the value.

- **Subject:** the hook rewritten as a noun phrase. *"Saturn-Venus Square: Relationship Structures Tested (Peaks Oct 15)"*
- **Greeting:** match the recipient register (*Good morning,* / *Hello,* / *Hi [Name]*).
- **Body:** 2–3 paragraphs. What's happening → What it means → Dates to watch.
- **Sign off** with the next decision point or reflection prompt. *"Watch how your commitments shift this week."*

### Email Newsletter

- **Subject:** PAC caption hook + "This Week" / "This Month"
- **Body:** 3 sections — *This Week's Sky*, *Deeper Dive* (one transit), *Reflection Prompt*
- **CTA:** Link to full transit report or PAC content

## Source material

The input is one of:

1. **A Boom technical artifact** — transit report (`Output/transits/`), PAC draft (`Output/PAC/`), convergence report (`Output/Bella/`), audit (`Output/Arm/`), critique (`Output/Nan/`) → use directly.
2. **A post-mortem / debug ledger** → hand from `boom-post-mortem` or `boom-debug-mantra`.
3. **Pasted technical text** → use directly.
4. **The current conversation** → if you (or the user) just produced technical content and the user now says *"now for PAC"* / *"now for briefing,"* reuse what's in context.

If the source is ambiguous, ask one question and stop.

## Output flow

1. **Confirm the channel** if it's not stated.
2. **Produce the draft** as a single chat block, formatted as the channel would render it.
3. **Ask where it goes:**
   - Default: print-only — the user copies it.
   - Direct post: only if the user explicitly says so and provides auth. Show exact payload, wait for explicit *"post it"*, then execute.
   - **Never post to Instagram, email, or any external channel from this skill without explicit approval.** Hand the draft to the user; they post it.
4. **One iteration is normal, three is a smell.** If the user is on the third revision, ask what specific framing/audience assumption you're missing — don't keep tweaking blindly.

## Worked example — same Saturn-Venus square, three channels

**Source (technical transit report):**

> **Transit:** Saturn 15° Pisces applying square to natal Venus 26° Libra (orb 1°45', applying). Peak exact: 2024-10-15. Duration: Sep 20 – Nov 5. House: Saturn transiting 9th, Venus natal 4th. Themes: relationship structures, commitment vs. freedom, home vs. belief systems. Classical reference: Parashara BPHS Ch. 41 on Shani-Shukra yoga.

### As PAC Caption

> **Saturn in Pisces squares your Venus in Libra. Relationship structures get tested. 🪐⚖️**
>
> - What: Saturn (structure) presses Venus (relating) — commitments feel heavy
> - When: Peaks Oct 15, active Sep 20 – Nov 5
> - Meaning: Where you've been "making it work" may crack. Not a breakup transit — a *renegotiation* transit
> - Your move: Name what's unsustainable. One honest conversation > ten compromises
>
> #SaturnSquareVenus #TransitAstrology #RelationshipAstrology #PiscesSeason #LibraRising

### As Transit Briefing Line

> Saturn squares Venus (peaks Oct 15). Relationship structures tested — renegotiate what's unsustainable.

### As Newsletter Section

> **This Week's Sky:** Saturn in Pisces squares Venus in Libra, peaking October 15. This isn't about breaking up — it's about renegotiating the invisible contracts you've been honoring. Where does duty end and desire begin?
>
> **Deeper Dive:** With Saturn transiting your 9th house (beliefs, far horizons) and Venus ruling your 4th (home, foundation), the tension lives between *where you're going* and *where you come from*. The square asks: are your commitments supporting your growth, or just your safety?
>
> **Reflection Prompt:** What agreement — with a partner, a friend, yourself — needs rewriting this month?
>
> [Read full transit report →]

What changed between channels: same transit, same peak date, same core meaning. PAC gets reflection prompt + hashtags. Briefing gets one actionable line. Newsletter gets house context + CTA. None mention ayanamsa, house system, Parashara chapter, or pipeline stage.

## Rules

- **Never invent transits** to make the rewrite cleaner. If the technical source says "orb 3° separating," the rewrite says "fading" — do not promote a separating aspect to applying for narrative tidiness.
- **Never strip planet/sign/aspect/date** during de-jargoning. They're the cross-reference bridge — losing them breaks trust.
- **Never invent classical citations.** If the source doesn't name one, don't add "as the ancients said" for authority.
- **Get sign-off before posting externally.** Print-only output needs no approval.
- **Never post to Instagram, email, or any external channel from this skill.** Hand the draft to the user; they post it.
- **Stay out of prescription.** This skill produces a content piece, not a life-coaching session. If the user wants advice framing, confirm before reframing.

## Boom Project Integration

### Mandatory Startup Protocol (every session)
1. Run `boom-auto-workflow-router`
2. Read `SOUL.md` and `TURBOZ.md`
3. Consult `.hermes.md` and `BOOM_PERSONAL_OPERATING_SYSTEM.md`
4. Restore relevant memory/session context
5. Load task-specific skills
6. Apply context-economy rules
7. Turboz + Ekae collaborate automatically
8. Verify files, commands, counts, external side effects

### Output routing
- PAC content → `Output/PAC/` (ready-to-post IG content)
- Transit briefings → `Output/transits/` (transit reports)
- Newsletter → `Output/Sources/` or `Output/Ekae/`
- Technical source preserved in `Output/Arm/`, `Output/Nan/`, `Output/Bella/`
