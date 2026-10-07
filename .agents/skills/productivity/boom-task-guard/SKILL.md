---
name: boom-task-guard
description: Keeps long Boom tasks on-track — breaks loops, handoff.
---

# boom-task-guard

Keeps a long Boom Project task on-track — breaks out of looping/circular thinking, watches the context budget, bounds internal reasoning, and triggers a clean handoff before the window fills. Use when the model is repeating steps, re-reading the same files, second-guessing in circles, stuck or spinning, or running a long multi-step task at risk of exhausting context. Also use when the user says it is "looping", "going in circles", "stuck", "repeating itself", or asks for a handoff before running out of context.

## Before each step — run this

| Check | Trigger fires when... | Do this |
|---|---|---|
| **Looping?** | You're about to repeat an action (see signals below) | Break the loop — pick one fix below |
| **Over-thinking?** | You've reasoned past ~1000 words without acting | Stop. Act on your current best decision, or ask the user one question |
| **Context tight?** | A low-context reminder appeared, **or** 2+ budget signals hold | Finish this step, then hand off |

If nothing fires, take the step.

## 1. Loops — detect and break

A step is a loop if **any** of these is true:

- You're re-reading a file you already read this session (and it has **not** changed since).
- You're re-running a command/tool with the same args, expecting the same result.
- You're returning to a hypothesis you already tried and dropped.
- You're "reconsidering from the start" with no new evidence.
- The last 2 steps gained no new information.

**Re-reading a file you just edited is NOT a loop** — that's verifying.

When a loop fires, **stop** and do exactly one:

1. State the blocker in one sentence and ask the user a specific question.
2. Write what you know vs. don't know, then take a **different** action than last time.
3. Looped 2+ times on the same sub-problem? Declare it unsolved-for-now; move on or hand off.

Never repeat a failed action hoping for a different result.

**Retry cap:** never run the same failing command a 3rd time. Can't get something working (a command, a test runner, an import) after ~3 attempts — *even varied ones* — STOP and ask the user; don't grind through more variations.

**Don't edit blind** — it's the top loop source. Read enough to know the change is correct *before* editing. After each edit, verify it (read the diff / run it / run the test) **before** the next step. One edit → one check.

**Boom-specific loop patterns:**
- Re-reading `SOUL.md`, `TURBOZ.md`, `.hermes.md` repeatedly — read once, cache mentally
- Re-running `python scripts/libby/cli.py --once` without changes — run once, verify output
- Re-querying `astro-knowledge-db` with same query — cache results
- Re-calculating same natal chart / transit timeline — save output, reference it
- Re-building indexes (`project_index.py`, `build-output-index.py`) — one per session unless files changed

## 2. Thinking — keep it bounded

Cap reasoning at **~1000 words per step**. Past that, you're deliberating instead of acting.

- Decide → act → observe. Don't re-derive a decision you already made.
- Can't decide in ~1000 words? The task is underspecified — **ask the user one sharp question**.
- Don't restate the whole problem to yourself. Reference what you concluded; don't rebuild it.

## 3. Context budget — count signals, don't estimate

**Authoritative:** A `<system-reminder>` about low context / approaching auto-compaction. → **Hand off now** (section 4). Don't start new work.

**Otherwise, count how many of these are true right now:**

- [ ] 20+ assistant turns into the task.
- [ ] Read 5+ files, or any one huge file/log/dump.
- [ ] Long tool outputs you keep scrolling back to.
- [ ] 3+ plan steps still left.

**Count the boxes that are true, then map the count to an action:**

- **Count is 0 or 1 → CONTINUE** working normally.
- **Count is 2, 3, or 4 → HAND OFF** — finish the current step, then go to section 4.

Count first, then decide — don't judge by feel. A higher count means *more* context pressure, not less. Being on the last step or "almost done" does **not** lower the count or cancel a HAND OFF.

Before any **expensive** step (large read, new subtask, long generation), ask: *"Room to finish this AND hand off after?"* If the count says HAND OFF, finish the current atomic unit, then hand off — don't start the next.

## 4. Hand off cleanly

When context is tight or the user asks:

1. **Land durable artifacts first** — save the file, commit, write the result. Nothing lost.
2. **Invoke the `handoff` skill** to compact the conversation. Don't hand-write the handoff.
3. Tell the user plainly: "Context is getting tight — handing off now; start a fresh session (`/clear`)."

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

### Works with Boom skills
- `boom-deep-research` — long research sessions
- `boom-grill-me` — extended grilling sessions
- `boom-debug-mantra` — debug sessions
- `boom-post-mortem` — post-mortem drafting
- `astro-pipeline` — full pipeline runs
- `transit-pac-pipeline` — transit→PAC generation

### Output routing
- Handoff summaries → `Output/Ekae/` (preference/ops collaboration)
- Debug ledgers → `Output/Arm/` (audit reports)
- Research outlines → `Output/Sources/`
