---
date: '2026-08-01'
tags:
- project
source: hermes-astro-hub/skills/integrated-astrology/references/solar-arc-career-timing.md
---

# Solar Arc Career Timing — BooM Workflow

Use when BooM asks: “when is there a chance of getting/changing jobs”, “will I get a job this year”, or career timing via Solar Arc.

## Source-backed Solar Arc basics

Primary source checked in-session: Astrodienst Astrowiki `Solar Arc`.

Verified points:

- Solar Arc Direction is a predictive method based on the Sun's diurnal movement.
- All planets and axes are moved by the same amount as the Sun moves in one day, symbolizing one year of life.
- It can use true solar arc or mean solar arc / Naibod key.
- Interpretation uses directed planet/axis aspects to natal factors.
- Use tight orb, generally under 1°.
- Bibliography on Astrodienst page: Noel Tyl, *Solar Arcs: Astrology's Most Successful Predictive System* (2001).

Local formula source checked: `xalen-ephemeris/crates/xalen-western/src/progressions.rs`

```text
Solar Arc = progressed Sun − natal Sun
Directed position = natal position + Solar Arc
```

## Career houses and database anchors

Database excerpts used in this session:

- `Western Astrology - Planets in Signs and Houses.pdf`
  - 10th house = career, not the 6th.
  - 6th house = how one works / job routine / co-workers / service.
  - 11th house = groups; also money directly earned from career because it is 2nd from the 10th.
  - Mercury in 10th = communication or transportation central to career.
  - Jupiter in 10th = luck/support in career; powerful people may help.
  - Saturn in 10th = business, hard work, discipline, organizational ability, responsibility.

## Career timing workflow

1. Calculate natal chart with verified birth data and timezone conversion.
2. Calculate Solar Arc for target date/range:
   - progressed JD = birth JD + elapsed tropical years
   - arc = progressed Sun − natal Sun
   - directed point = natal point + arc
3. Scan directed factors against natal career factors.
4. Use hard aspects first: `0°, 45°, 90°, 135°, 180°`.
5. Require orb under `1°`; strongest windows are under `0°30′`.
6. Use Solar Arc as the **year/window** signal, not the sole promise.
7. Confirm timing with transits and/or progressed Moon:
   - Transit Jupiter/Mercury/Sun/Venus/Mars/Saturn to MC, 2nd/6th/10th/11th cusps, rulers, or SA point.
   - Progressed Moon to MC, 6th, 10th ruler, Jupiter, Saturn, or 11th cusp for month-level movement.
8. Output ranked windows, not vague statements.

## Career factors to prioritize

| Factor | Meaning |
|---|---|
| MC / 10th cusp | career direction, status, visibility |
| 6th cusp | job routine, daily work, employment function |
| 2nd cusp | income, salary, earning capacity |
| 11th cusp | gains from career, groups, network |
| Sun | visibility, self-direction |
| Mercury | applications, interviews, messages, documents |
| Mars | action, competition, start, urgency; also 10th ruler if MC Aries |
| Jupiter | opportunity, growth, support |
| Saturn | contract, company, structure, responsibility |
| Venus | support, social value, audience/gains when ruling 11th |
| Kronos | official approval, authority, status |
| Apollon | commerce, knowledge, network, expansion |
| Vulkanus | breakthrough, force, high-pressure opportunity |

## Example from BooM session — verified calculations

Birth data used: `20 Nov 1996, 20:37 ICT, Chiang Rai`.

Natal anchors calculated:

| Natal factor | Position | Meaning |
|---|---:|---|
| ASC | 11.72° Cancer | self/body/direction |
| MC / 10th cusp | 04.28° Aries | career; ruler Mars |
| 2nd cusp | 06.24° Leo | income; ruler Sun |
| 6th cusp | 11.13° Sagittarius | job routine; ruler Jupiter |
| 11th cusp | 08.04° Taurus | gains/network; ruler Venus |
| Mars | 11.33° Virgo | 10th ruler |
| Jupiter | 16.25° Capricorn | 6th ruler |
| Venus | 26.92° Libra | 11th ruler |

Solar Arc at 27 Jul 2026:

```text
Natal Sun = 28.519° Scorpio
Progressed Sun = 28.636° Sagittarius
Solar Arc = 30.117° ≈ 30°07′
```

Key windows calculated:

| Window | Trigger | Reading |
|---|---|---|
| 28 Jul–22 Aug 2026 | `SA Vulkanus = natal MC/Cusp10`, `SA Apollon = natal MC/Cusp10`; transit Jupiter to 2nd/6th/Mercury | strongest near-term job/income opening |
| 31 Oct–15 Nov 2026 | `SA Mars □ natal ASC`; progressed Moon to 11th cusp; transit Uranus sextile MC | career direction shift, online/freelance/network opportunity |
| 7–25 Feb 2027 | `SA Kronos □ natal Venus`; transit Saturn trine 6th/Mercury | formal/company/contract-style work, heavier responsibility |
| 16 Sep–12 Oct 2027 | transit Jupiter to natal Mars/ASC/Jupiter | growth from action/competition/project; secondary window if 2026 does not settle |
| May–Aug 2028 | `SA MC □ natal 2nd cusp`, `SA Sun/Mars` contacts | larger career-income turning point, heavier than 2026 |

## Required BooM answer format

- Start with a concise verdict/ranked windows.
- Include `Source / Calculation` line.
- Separate `Solar Arc = big window` from `Transit/Progressed Moon = trigger`.
- Explain every date/aspect in plain English; do not dump numbers without meaning.
- If database was not checked, label the answer as non-database draft.
