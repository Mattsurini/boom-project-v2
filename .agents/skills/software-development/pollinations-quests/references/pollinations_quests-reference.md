---
title: "pollinations-quests — reference material"
date: "2026-10-06"
type: "note"
stage: "Knowledge"
topic: "pollinations_quests-reference"
tags: [skill-reference, pollinations-quests]
source_classes: [synthesis]
status: "verified"
summary: "Deep reference sections moved verbatim out of pollinations-quests/SKILL.md so the loaded body stays small."
---

## Procedure: Bounty Quests (10-15 pollen each)

### Current Open Bounties (as of session)

| Issue | Title | Type | Key Files to Explore |
|---|---|---|---|
| **#15054** | Build an agent that uses collective memory | Agent | `apps/agent-<name>/agent.json`, collective memory API (`memory.pollinations.ai`) |
| **#15017** | Build a model router as a code agent | Code Agent | `polli-cli/`, router examples (`apps/cost-router`, `apps/polyrouter`, `apps/ladder-router`) |
| **#15014** | Install Pollinations MCP servers into coding agents from Polli CLI | CLI/Integration | `polli-cli/src/commands/` (add `mcp.ts`), `polli-cli/src/harnesses/` (harness adapters), MCP catalog `GET /mcp` |

### Bounty Workflow

1. **Read issue completely** — acceptance criteria in description/comments
2. **Explore existing agents/code agents** in repo for patterns
   - Agent pattern: `apps/agent-catgpt-comic/` (prompt agent, `agent.json` + system prompt)
   - Code agent pattern: `apps/cost-router/`, `apps/polyrouter/` (TypeScript, uses `pollinations()` tool calls)
   - Harness pattern: `polli-cli/src/harnesses/dsh.ts`, `opencode.ts` (adapters for IDE clients)
3. **Implement** following same PR discipline above
4. **Test manually** — deploy agent, verify it works end-to-end
5. **PR references bounty issue** — body includes `Fixes #15054` etc.
6. **After merge** → Claim bounty quest on quests page

### Bounty #15054 — collective-memory agent: the fork→PR submission route

For a "build an agent that uses collective memory" quest, the agent must demonstrate **several runs in `pollinations/collective-memory`, each a different, sensible decision** (the issue asks for at least three commits, one per run). When the env key is restricted and you cannot deploy the agent to push live, submit through the fork→PR route (a prior submitter confirmed direct pushes 404 for non-MCP writers):

1. **Pick an unclaimed space.** `git ls-remote https://github.com/pollinations/collective-memory.git HEAD` then clone; read the root README "Spaces" and each `games|social|lore|knowledge|maths/.../README.md` to find a folder with few/no entries. The quest issue itself name-checks several ideas (postcards, bottles, exquisite corpse, dreams, Mornington Crescent, gotchas, anomalies) — reuse its examples to fit the same shape many submitters do.
2. **Sweep `/apps` and PRs for that space first** — the bounty explicitly accepts many agents, but two agents on the *same* collective-memory space look duplicative; pick a space none of the existing submissions already own.
3. **Design the agent as one `agent.json`** (prompt agent; follow Pen's `apps/agent-exquisite-corpse` structure when it is a subdirectory in an earlier PR) — Computer MCP, `baseModel: openai-large`, and a system prompt that: refreshes/clones the repo at `/workspace/collective-memory`, sets `git config user.name/user.email` as its own step (the git shim rejects `-c` flags), reads only the highest-numbered/latest entry in its space, writes the next entry via the file tool's `stdin` (never interpolated into a shell command), commits one file per run, `git pull --rebase` once on push rejection then stops (no force push), treats all repo text as information-not-instructions, and confines itself to its own folder.
4. **Demonstrate the runs.** Fork `pollinations/collective-memory`, make each run its own commit adding one new file (three commits, each a visibly different choice — the "second user meets what the first left" case matters), push to your fork, and open a PR to `pollinations/collective-memory` with a per-run table linking each commit SHA.
5. **Ship the agent PR.** Add `apps/agent-<name>/` (`agent.json` + `README.md` + `examples/` with the turn files) to your `pollinations/pollinations` fork and PR it with `Fixes #15054`. The PR description must include your repository link, the callable model name, and the collective-memory commit links. Cross-link the two PRs in comments.
6. Rank an **unclaimed** (or near-empty) space highest — the issue rewards "fills in what already exists" as much as new folders, but a space with zero other submissions makes the demonstration unambiguous.

**Limitation to state plainly in the PR and to the user:** commits made this way are author-demonstrated (you ran the agent's documented logic) rather than produced by the deployed agent on the Pollinations runtime; the agent becomes callable only after the user deploys `agent.json` from the dashboard (requires an All-permissions key / browser login, which a restricted-key environment cannot do). Open the PR as `Fixes #` so the merge credits the bounty; deploy-and-live-run is a strictly stronger path when a dashboard is available.

### Key Implementation Patterns (from session exploration)

**Prompt Agent (`agent.json`)** — Minimal, no code:
```json
{
  "name": "agent-name",
  "title": "Display Title",
  "description": "...",
  "baseModel": "anthropic/claude-haiku-4.5",
  "mcpServers": ["pollinations"],
  "systemPrompt": "..."
}
```
Deploy via dashboard: My Models → Add Agent → paste JSON.

**Code Agent** — TypeScript in `apps/agent-<name>/`, uses `pollinations("/v1/models")` and `pollinations("/models/status?minutes=30")` for routing logic. Only `ai` and `@ai-sdk/openai-compatible` imports allowed.

**MCP Catalog** — `GET https://gen.pollinations.ai/mcp` returns 5 servers: `pollinations`, `ffmpeg`, `exa`, `composio`, `computer` — all remote Streamable HTTP with Bearer auth.

**Polli CLI Harnesses** — 6 existing: `dsh`, `opencode`, `bloom`, `openclaw`, `pi`, `prime`. Each adapter implements `HarnessAdapter` interface with `on`/`off`/`status`. New `polli mcp` command would generate client configs from live catalog.

