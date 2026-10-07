---

name: management-talk
description: Rewrite engineer content for an engineering org audience.
metadata:
  hermes:
    tags: [writing, management, communication]
---

# Management Talk

Same audience and translation rules as a written status report, but **shaped for the channel** — JIRA comment, Slack post, async standup, email, or meeting talking-points. The audience reads code names but not code. The channel decides the length, formatting, and how much structure to leave on the page.

Use this any time engineering content needs to flow up the org, sideways into product/release, or into a non-engineering meeting — regardless of the destination.

## When to invoke

- "write something for management / exec / VP / director / PM / release manager"
- "rewrite this for [non-eng audience]"
- "make this non-technical" / "less techy" / "less jargony"
- "send a slack update / standup note / email" *about a piece of engineering work*
- "executive summary" / "exec summary" / "leadership update" / "status update"
- "talking points for [meeting]" *based on an engineering update*

If the channel is unclear after the trigger, ask one short question — *"JIRA, Slack, standup, or email?"* — and stop.

## Audience — what "engineering-org leadership" means

Engineering-savvy non-engineers: VPs, directors, PMs, release managers, execs in companies that ship technical products. They read product/framework names and cross-reference JIRA keys and PRs. They do not read code.

They want: *what's the state, what does it mean for customers, who owns it, what's next.* They do not want: how the bug works at the function level.

This is **not** for marketing, finance, customer-facing, or true ELI5 audiences — those need a different rewrite. Flag and confirm before producing one.

## Tone

**Keep.** Product names, framework names, team-owned component names, JIRA keys, PR numbers, customer/workload identifiers (`hermes-astro-hub`, `flatlib`, `sweph`, `xalen`, `Rider-Waite-Smith`, `JIRA-12345`, `PR #5751`). These are the bridge between engineering and leadership tracking.

**Strip.** Function names, file paths, struct fields, commit SHAs, code expressions, env var names, line numbers, internal data-structure jargon (`natal_chart_swe.py::calculate_voc_window()`, `scratchBuf`, `0e0a6bac`). None of this is actionable to the audience.

**Translate.** Mechanism into one or two sentences of plain-English cause-and-effect. Not *"the function reads `system='tropical'` instead of `system='sidereal'`"* but *"the astrology calculations used the wrong reference frame, causing timing windows to drift by 2 degrees."* Translate without lying — a race stays a race; a regression stays a regression.

**Don't over-strip.** Engineering-org leadership reads concept-level technical vocabulary fluently — *race condition, synchronization, uninitialized buffer, fast-path, workaround, registration, queue, driver, kernel* (in the GPU sense). The line is between *concept exists and matters here* (keep) and *here's the function/struct/file/SHA* (strip). Replacing "race" with "timing issue" patronizes the reader.

**Bias toward** active voice, concrete subjects, short paragraphs. *"We found the bug. Boom wrote the fix. PR is up for review."* beats *"The root cause has been identified and a fix has been authored and submitted for review."*

**Avoid:**

- Hedging that isn't really hedging (*"we believe," "appears to," "may have"*). State it or don't.
- Re-stating the obvious for thoroughness (*"This bug is in hermes-astro-hub, which is used for astrology calculations, which is important for clients, which..."*).
- Telling leadership how to do their job (*"you should prioritize," "this needs to land before X"*). Give them the facts; they decide.
- Engineering-process minutiae: bisect runs, debug iterations, GDB sessions. They care that you found it, not how. (Exception: when the *process* itself is the story — *"we burned three weeks before realising the bisect was misleading"* — then a single sentence as a learning, not a play-by-play.)

## Channel shapes

Same content, different shell. Pick the shape that matches where it's going.

### JIRA comment / written status report

Full structured block. Bolded section labels. Easy to scan from the ticket page.

Building blocks (use as many as fit):

- **Status / TL;DR.** One bolded line. Reader can stop here and have the right answer. *"Fixed pending merge."* / *"Root cause unknown — investigating."* / *"Blocked on vendor."* / *"Customer-visible regression in 7.2; rollback in flight."*
- **Impact.** Who's affected, how badly, what they see. Customer / workload / product terms, not test-suite terms. *"Llama-2-70B fine-tuning hangs on every eval step"* > *"the test fails."*
- **What broke.** Short paragraph. Plain-English mechanism, one level of why, no code identifiers.
- **Why now / how it slipped through.** Optional. Include when leadership will ask anyway: latent regression, CI gap, prior incomplete fix, change that landed during a freeze.
- **Owner.** Person + team + their PR/branch/JIRA artifact. One link, not five.
- **Next steps.** Concrete, near-term, ordered. *"Code review → merge → backport to 7.2."*
- **Workaround / mitigation.** If customers are hitting it now, what can they do today? One sentence.
- **Risk.** Optional. Real risks only — *"fix touches the hot path; perf regression possible until benchmarked."* Don't manufacture risk to look thorough.

Order by what matters most for *this* item.

### Slack — channel post or DM

Single message, no walls of text. Heavy bolded section labels read as "I escaped from JIRA" — don't.

- One **bolded TL;DR** as the first line.
- 2–4 short bullets underneath: impact, owner+link, next step. Drop blocks that don't apply.
- One link, embedded inline (`JIRA-12345` / `PR #5751`). Not a link wall.
- No greeting, no signoff. The channel is the context.
- If it's a **thread reply** rather than a new post, lose the TL;DR — just lead with the answer.

Length target: under ~80 words for a top-level post; under ~40 for a thread reply.

### Async standup note

The audience scans 10 of these in 30 seconds. Front-load the verb.

- 1–3 lines, max.
- Pattern: *"\<state\> \<thing\>. \<owner if not me\>. \<next\>."*
- Examples:
  - *"Fixed VOC timing drift affecting sidereal-chart clients (HERMES-42). PR #127 in review."*
  - *"Still chasing the synastry score inconsistency. Reproducer is reliable now; bisecting. No ETA yet."*
- No bullets, no bolded labels. The format **is** the sentence.

### Email — internal exec / cross-team

Subject line is half the value.

- **Subject:** the TL;DR rewritten as a noun phrase. *"VOC timing drift in sidereal charts: fix in review (HERMES-42)."*
- **Greeting:** match the recipient register (*Hi Sam,* / *Hi all,*).
- **Body:** the JIRA-comment shape, but as flowing paragraphs separated by blank lines rather than bolded section labels. Two or three paragraphs is plenty.
- **Sign off** with the next decision point that needs the recipient's attention, if any. If none, a plain *"— [Name]"* is fine.

### Meeting talking-points

You're going to *say* this, not show it.

- Bullet list, max one short clause per bullet.
- Order is the order you'll speak in.
- Include the numbers/keys you want to reference out loud, in the bullet itself, so you don't fumble.
- Skip prose. *"sidereal VOC timing was drifting by 2 degrees."* / *"Root cause: hardcoded tropical ephemeris."* / *"Boom's fix in review, PR #127."* / *"Backport to v7.2 once it lands."*

## Source material

The input is one of:

1. **A JIRA ticket key** (e.g. `HERMES-42`) → fetch via `GET /rest/api/3/issue/<KEY>?fields=summary,status,priority,assignee,comment` plus any custom fields your instance uses for technical evaluation — usually the cleanest source of current state. The most recent substantive comment is what to reframe; don't dump the full thread.
2. **Pasted technical text** → use directly.
3. **The current conversation** → if you (or the user) just produced engineering content and the user now says *"now in slack"* / *"now for the VP,"* reuse what's in context.

If the source is ambiguous, ask one question and stop.

## Output flow

1. **Confirm the channel** if it's not stated.
2. **Produce the draft** as a single chat block, formatted as the channel would render it.
3. **Ask where it goes:**
   - Default: print-only — the user copies it.
   - JIRA back-post: only if the user explicitly says so. Show the exact ADF payload, wait for explicit *"post it"* / *"go ahead"* / *"yes,"* then `POST /rest/api/3/issue/<KEY>/comment`.
   - **Never post to Slack, email, or any non-JIRA channel from this skill.** Hand the draft to the user; they post it.
4. **One iteration is normal, three is a smell.** If the user is on the third revision, ask what specific framing/audience assumption you're missing — don't keep tweaking blindly.

## Worked example — same bug, three channels

**Source (engineering JIRA comment):**

> **Mechanism:** `voc_time.py::calculate_voc_window()` called `flatlib.chart.Chart()` with `system='tropical'` hardcoded, regardless of the chart's `ephemeris` field. For sidereal charts this produced house cusps ~24° ahead of the correct sidereal positions. The VOC transition time was computed from the wrong cusp, yielding a window offset by the tropical-sidereal difference for that date.

### As a JIRA comment

> **Status: Fixed pending merge.** Bug found, fix validated, PR up for review.
>
> **Impact:** Clients using sidereal (Lahiri) charts saw muhurta timing windows drift by ~2 degrees compared to the web calculator. A gold-trading muhurta scheduled for 14:00–15:30 was actually valid for 13:45–15:15.
>
> **What broke:** The VOC calculation used the wrong ephemeris reference frame (tropical instead of sidereal), causing house cusp positions to be offset by ~24°. The timing windows derived from those cusps were therefore shifted.
>
> **Owner:** Boom. PR #127.
>
> **Next steps:** code review → merge. Clients hitting this today can switch to tropical mode as a temporary workaround.

### As a Slack post

> **VOC timing drift for sidereal-chart clients is fixed pending merge.** (HERMES-42)
>
> - Wrong ephemeris mode in VOC calculation → timing windows drifted ~2 degrees. Latent for months; sidereal was the first workload to hit it.
> - Owner: Boom, PR #127 in review.
> - Workaround until merge: switch to tropical mode.

### As a standup note

> Fixed VOC timing drift on sidereal charts (HERMES-42). Boom's PR #127 in review. Backport to v7.2 next.

What changed between channels: same diagnosis, same owner, same next step. JIRA gets every block. Slack drops "why now" — too much for the channel. Standup keeps just state + key + owner + next. None of them mention `flatlib.chart.Chart()` or `system='tropical'`.

## Rules

- **Never invent facts** to make the rewrite cleaner. If the engineering source says "root cause unknown," the rewrite says "root cause unknown" — do not promote a speculation to a finding for narrative tidiness.
- **Never strip a JIRA key, PR number, or customer/workload name** during de-jargoning. They're the cross-reference bridge — losing them breaks tracking.
- **Never invent owners.** If the source doesn't name one, ask the user — don't guess from `git blame` or recent commits.
- **Get sign-off before posting to JIRA.** Reuse the jira-check approval flow. Print-only output needs no approval.
- **Never post to Slack, email, or any non-JIRA channel from this skill.** Hand the draft to the user; they post it.
- **Stay out of advocacy.** This skill produces a status update, not a recommendation. If the user wants a recommendation memo, confirm before reframing.
