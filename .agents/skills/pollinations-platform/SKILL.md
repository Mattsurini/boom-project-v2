---
name: pollinations-platform
version: 0.1.0
description: Complete Pollinations quests, use API, create agents, PRs.
---

# Pollinations Platform Operations

## When to Use
- Completing quests on https://enter.pollinations.ai/quests
- Making API calls to gen.pollinations.ai (text, image, audio, agents)
- Creating and deploying agents via enter.pollinations.ai/my-models
- Contributing pull requests to github.com/pollinations/pollinations
- Finding and solving POLLEN-QUEST bounty issues

## Prerequisites
- Pollinations account (GitHub/Google/Wallet login at enter.pollinations.ai)
- API key from https://enter.pollinations.ai/keys (create after login)
- For PRs: fork github.com/pollinations/pollinations

## Quest Completion Procedure

### 1. Login & API Key
```bash
# 1. Login at https://enter.pollinations.ai/quests
# 2. Create API key at https://enter.pollinations.ai/keys
# 3. Export key for CLI use
export POLLINATIONS_KEY="sk_..."
```

### 2. API Quest Calls (Use Free Models)
| Quest | Model | Endpoint |
|-------|-------|----------|
| Use a text model | `openai/gpt-5.4-nano` | `/v1/chat/completions` |
| Use an image model | `gpt-image` or `black-forest-labs/flux.1-schnell` | `/v1/images/generations` |
| Use an audio model | `openai/tts-1` | `/v1/audio/speech` |
| Use an agent | `community/Lorodn4x/deepseek-v4-flash` (free) | `/v1/chat/completions` |

```bash
# Text
curl -s https://gen.pollinations.ai/v1/chat/completions \
  -H "Authorization: Bearer $POLLINATIONS_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"openai/gpt-5.4-nano","messages":[{"role":"user","content":"test"}]}'

# Image
curl -s https://gen.pollinations.ai/v1/images/generations \
  -H "Authorization: Bearer $POLLINATIONS_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"gpt-image","prompt":"test","width":512,"height":512}'

# Audio
curl -s https://gen.pollinations.ai/v1/audio/speech \
  -H "Authorization: Bearer $POLLINATIONS_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"openai/tts-1","input":"test","voice":"alloy"}' -o test.mp3

# Agent (free community agent)
curl -s https://gen.pollinations.ai/v1/chat/completions \
  -H "Authorization: Bearer $POLLINATIONS_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"community/Lorodn4x/deepseek-v4-flash","messages":[{"role":"user","content":"test"}]}'
```

### 3. Claim Quests
- After API calls, wait 1-2 minutes
- Refresh https://enter.pollinations.ai/quests
- Click **Claim** on each completed quest
- **Use a Pollinations app**: Go to https://pollinations.ai/apps → Connect any app via OAuth

### 4. Create Agent Quest ("Create an agent that gets used")
1. Go to https://enter.pollinations.ai/my-models
2. Click **Add Agent** → **Prompt Agent**
3. Configure:
   - Name: `my-test-agent`
   - Base Model: `openai/gpt-5.4-nano` (free)
   - System Prompt: `You are a helpful assistant. Reply briefly.`
   - MCP Servers: ✅ `pollinations`
4. Deploy → Test via **Playground** button (1 request = quest done)
5. Claim quest (2 pollen × 2 entries)

## PR Contribution Procedure

### Find Work
- Open POLLEN-QUEST issues (high reward): #15014, #15017, #15054
- Check https://github.com/pollinations/pollinations/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22
- Documentation fixes in `enter.pollinations.ai/`, `gen.pollinations.ai/`, `pollinations.ai/`, root `*.md`

### Submit PR
```bash
# 1. Fork at github.com/pollinations/pollinations/fork
# 2. Clone your fork
git clone https://github.com/<YOUR_USERNAME>/pollinations.git
cd pollinations
npm install

# 3. Make changes (fix typo, add test, update docs)
git checkout -b fix/descriptive-name
# edit files...
git add .
git commit -m "docs: fix typo in README.md"
git push origin fix/descriptive-name

# 4. Open PR on GitHub → wait for merge → Claim 5 pollen (+ Senior dev 2 pollen if first PR)
```

## Key Free Models (No Credits Needed)
- Text: `openai/gpt-5.4-nano`, `deepseek/deepseek-v4-flash`, `z-ai/glm-5.3-flash`
- Image: `black-forest-labs/flux.1-schnell`, `openai/gpt-image-1-mini`
- Audio: `openai/tts-1`, `openai/gpt-audio-mini`
- Agents: `community/Lorodn4x/deepseek-v4-flash`, `community/pollinations-router/polli`

## Pitfalls
- **API key not linked to current account**: Create key AFTER logging in at enter.pollinations.ai/keys; keys from other accounts won't track quests
- **Quest tracking delay**: Wait 1-2 minutes after API calls before refreshing quests page
- **Paid model errors**: "not enough credits" = model requires paid Pollen; use free models listed above
- **Agent quest requires Web UI**: No API endpoint to create agents; must use enter.pollinations.ai/my-models
- **"Use a Pollinations app" requires OAuth**: Go to pollinations.ai/apps → Connect → Authorize (not just API call)
- **Web UI calls track better than curl**: Playground/Try-it buttons on docs pages use session cookies → more reliable quest tracking
- **POLLinations repo has no open "good first issue" labels**: Check DEV-BUG, documentation, or POLLEN-QUEST issues instead

## Verification
- Quest claimed → pollen balance increases
- PR merged → appears in github.com/pollinations/pollinations/pulls
- Agent deployed → appears in My Models with Agent ID

## References
- `references/free-models.md` — curated list of free models by modality
- `references/quest-tracking.md` — how quest detection works, common failures
- `references/agent-creation.md` — agent.json schema, deployment steps, testing
- `references/pr-workflow.md` — repo structure, harness patterns, test commands