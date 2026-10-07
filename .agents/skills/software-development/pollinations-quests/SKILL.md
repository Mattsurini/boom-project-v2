---
name: pollinations-quests
description: "Complete Pollinations quests for Pollen via agents and PRs."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [pollinations, quests, pollen, github, api, agents, open-source]
    category: software-development
    related_skills: [github, research]
---

> **LOCAL MODIFICATION — Boom Project, 2026-10-06.** Deep reference sections were moved out of
> this body into `references/` to keep the loaded body small. This copy therefore **diverges from
> the upstream community skill**: do not blind-overwrite it on update.

# Pollinations Quests

End-to-end workflow for earning Pollen by completing quests on the Pollinations platform. Covers Setup quests (use agent/model/audio), Grow quests (create agents, get users, list apps), Contribute quests (PRs, bounties), and Community quests.

## Quest Categories & Rewards

| Category | Quest | Reward | Verification |
|---|---|---|---|
| **Setup** | Create API key | 0.25 | Auto on key creation |
| **Setup** | Use a Pollinations app | 0.25 | One successful request to any app/agent |
| **Setup** | Use an agent | 0.25 | One successful request to community agent |
| **Setup** | Use a text model | 0.25 | One successful text generation request |
| **Setup** | Use an image model | 0.25 | One successful image generation request |
| **Setup** | Use an audio model | 0.25 | One successful audio generation request |
| **Grow** | Create an agent that gets used | 2 | Agent receives ≥1 request (self-test counts) |
| **Grow** | Top up Pollen | 5 | Purchase Pollen (from 2026-06-21) |
| **Grow** | First user connects to your app | 7 | User logs in via authorize flow |
| **Grow** | App listed on Pollinations | 10 | App approved in app directory |
| **Grow** | First Paid Pollen request | 15 | External user makes paid request in your app |
| **Contribute** | Senior dev | 2 | First merged PR |
| **Contribute** | Contribute a pull request | 5 | PR merged to pollinations/pollinations |
| **Contribute** | Ship bounty #15054 | 10-15 | Build collective memory agent |
| **Contribute** | Ship bounty #15017 | 10-15 | Build model router code agent |
| **Contribute** | Ship bounty #15014 | 10-15 | Install MCP servers via Polli CLI |

## Procedure: Setup Quests (Fastest Path)

### 1. Use an Agent (0.25 pollen)

Fastest: call a community agent endpoint directly.

```bash
# List community agents
curl -s https://gen.pollinations.ai/docs/community-agents | grep -o 'agent/[^"<>]*'

# Call one (e.g., CatGPT)
curl -s "https://gen.pollinations.ai/agent/pollinations/catgpt?prompt=hello"
# Or via CLI if installed
pollinations agent pollinations/catgpt "hello"
```

**Verification:** Response contains generated text → go to https://enter.pollinations.ai/quests → Claim.

### 2. Use Text/Image/Audio Models (0.25 each)

```bash
# Text
curl -s "https://text.pollinations.ai/hello world"

# Image
curl -s "https://image.pollinations.ai/prompt/a%20cat" -o cat.jpg
```

**Audio (TTS) is PAID — do not expect the 0.25 to be free.** TTS via `/v1/audio/speech` returns `HTTP 401 Unauthorized` without a key and `402 Payment Required` when the account has 0 Paid Pollen (quest-earned Pollen does not cover TTS). The legacy `audio.pollinations.ai/<text>` endpoint is gone (HTTP 000/404). Only attempt audio if the account already has Paid Pollen; otherwise treat the "Use an audio model" quest as blocked on purchase until the user tops up.

### 3. Create API Key (0.25)

Go to https://enter.pollinations.ai → Create API Key → copy key → Claim.

## Procedure: Contribute PR Quest (5 pollen + 2 Senior dev)

### 1. Find Open Beginner-Friendly Issues

```bash
# Check POLLEN-QUEST bounties (high reward)
curl -s -H "Accept: application/vnd.github.v3+json" \
  "https://api.github.com/repos/pollinations/pollinations/issues?labels=POLLEN-QUEST&state=open&per_page=20" \
  | python -c "import sys,json; [print(f\"#{i['number']}: {i['title']}\") for i in json.load(sys.stdin)]"

# Check good-first-issue / help-wanted / documentation
for label in "good first issue" "help wanted" "documentation" "bug" "fix-me"; do
  curl -s -H "Accept: application/vnd.github.v3+json" \
    "https://api.github.com/repos/pollinations/pollinations/issues?labels=$(echo $label | sed 's/ /%20/g')&state=open&per_page=10" \
    | python -c "import sys,json; d=json.load(sys.stdin); print(f'$label: {len(d)}') if d else None"
done
```

### 2. Pick Issue & Claim It

- Read full issue: `gh issue view <N> --comments` or curl equivalent
- Comment: "I'll work on this" to prevent duplicate work
- Check for existing PRs: `gh pr list --search "#<N>" --state all`

### 3. Implement Following github/issue-to-pr Discipline

1. **Read live issue + thread** — newest comments carry decisions
2. **Sweep duplicates** — PR search + keyword variants + recent commits
3. **Validate premise** — reproduce on current main; check git history for design intent
4. **Define acceptance** — criteria → tests
5. **Implement smallest complete change** — fix the class, not one call site
5. **Sabotage test** — prove regression test fails without fix
7. **Run quality gates** — lint, typecheck, test; open PR immediately
8. **Shepherd CI** — watch checks, distinguish your failures from infra flakes
9. **Merge + comment on issue** with PR link

### 4. Verify Merge & Claim

```bash
# Verify merged state
gh pr view <PR_NUM> --json state,mergedAt
# On quests page: Claim "Contribute a pull request" (5) + "Senior dev" (2 if first)
```

## Key Endpoints & References

| Purpose | URL |
|---|---|
| Quests dashboard | https://enter.pollinations.ai/quests |
| Community agents | https://gen.pollinations.ai/docs/community-agents |
| My models (create agent) | https://enter.pollinations.ai/my-models |
| API docs | https://gen.pollinations.ai/docs |
| Connect user wallets | https://gen.pollinations.ai/docs/connect-user-wallets |
| CLI docs | https://gen.pollinations.ai/docs/cli |
| MCP servers | https://gen.pollinations.ai/docs/mcp-servers |
| GitHub repo | https://github.com/pollinations/pollinations |
| Issue search (POLLEN-QUEST) | https://github.com/pollinations/pollinations/issues?q=label%3APOLLEN-QUEST+is%3Aopen |

## Agent Endpoint Format

```
https://gen.pollinations.ai/agent/{github-username}/{model-id}
```

Examples:
- `https://gen.pollinations.ai/agent/pollinations/catgpt`
- `https://gen.pollinations.ai/agent/pollinations/sirius-elevator`
- `https://gen.pollinations.ai/agent/pollinations/npc`

**Detailed implementation patterns:** `references/agent-patterns.md`

## Pitfalls

- **Claiming before verified** — Quest only credits after actual merge/response, not PR open.
- **Duplicate PR work** — Always sweep `gh pr list --search "#<N>"` + keyword variants before starting.
- **Bounty issues may be stale** — Check issue state (open/closed) and recent comments before investing time.
- **No "good first issue" label currently** — Pollinations uses `POLLEN-QUEST`, `fix-me`, `APP-SUBMISSION` labels instead; search broadly.
- **Agent testing** — Self-test request counts for "agent gets used" quest; deploy first, then call your own endpoint.
- **Private agent needs a Models/All-perm key** — calling your own `community/<user>/<agent>` with a restricted-permission key returns `403 "not allowed for this API key"`. Mint a fresh key (Create API Key, ensure the Models permission / "All") from the dashboard, then call the agent with that key; restricted keys see only their permitted models.
- **Restricted key blocks agent DEPLOY, not just calling** — `npx @pollinations/cli agents list` against a key without the `account:keys` scope returns `403 FORBIDDEN: API key does not have 'account:keys' permission`. The hermes-default `POLLINATIONS_KEY` is such a key, so you cannot create or deploy a prompt agent from the CLI, and therefore cannot make the deployed agent itself push. Probe the gate early with `printf '%s' "$POLLINATIONS_KEY" | npx @pollinations/cli auth login --with-token` then `npx @pollinations/cli agents list`; if it 403s, stop trying to deploy and fall back to the fork→PR route (below) as the only executable path from this environment.
- **Verify which account a key belongs to** — the environment `POLLINATIONS_KEY` may be a different, creditless account than the one logged into the dashboard (quests, agents, and credits attach to the account behind the authenticated key, not the browser session). Before self-testing an agent or claiming a quest, confirm the key you are using has the Models permission and matches the account whose quests you are trying to credit.
- **API key vs Pollen** — API key is for auth; Pollen is the reward token. Top-up Pollen quest requires purchase.

## Verification Checklist

- [ ] Setup quests: each model/agent request returns valid response
- [ ] Contribute PR: merged (not just opened), visible in `gh pr view --json mergedAt`
- [ ] Bounty PR: references correct issue number (`Fixes #XXXX`), merged
- [ ] Quest page: Claim button appears after verification, pollen balance increases
- [ ] Senior dev: only triggers on FIRST merged PR ever

## Reference files — open only when its topic comes up
The body above suffices for a standard pass; opening this costs more than the old single file did.

- `pollinations_quests-reference.md` — Deep reference sections moved verbatim out of pollinations-quests/SKIL
- Moved sections: Procedure: Bounty Quests (10-15 pollen each)
