# Pollinations Agent Patterns

Reference for implementing agents and code agents for POLLEN-QUEST bounties.

## Prompt Agent (agent.json only — no code)

Minimal deployment: paste JSON in dashboard → My Models → Add Agent.

```json
{
  "name": "unique-agent-id",
  "title": "Display Title",
  "description": "One-line description for directory",
  "baseModel": "anthropic/claude-haiku-4.5",
  "mcpServers": ["pollinations"],
  "systemPrompt": "Full system prompt with tool-calling instructions"
}
```

**Required fields:**
- `name`: unique identifier (kebab-case)
- `title`: human-readable
- `description`: shown in agent directory
- `baseModel`: any model from `GET /v1/models` that supports tool calling
- `mcpServers`: `["pollinations"]` enables `generateImage` tool
- `systemPrompt`: must instruct agent to call tools in correct order

**Example: CatGPT Comic** (`apps/agent-catgpt-comic/agent.json`)
- Uses `generateImage` tool with reference image for style consistency
- System prompt enforces: spoken line first, then exactly one `generateImage` call
- Image model: `google/gemini-3.1-flash-lite-image` (accepts reference image)
- Reference image URL passed in every call

**Deploy & Test:**
```bash
# After deploying via dashboard, call via API
curl -H "Authorization: Bearer $KEY" \
  -H "Content-Type: application/json" \
  -d '{"model": "community/<username>/<agent-name>", "messages": [{"role": "user", "content": "test"}]}' \
  https://gen.pollinations.ai/v1/chat/completions
```

## Code Agent (TypeScript + polling logic)

Lives in `apps/agent-<name>/` with:
- `agent.json` (references the code entry point)
- `index.ts` or `main.ts` — exports agent logic
- Uses `pollinations("/v1/models")` and `pollinations("/models/status?minutes=30")` for routing
- Only imports allowed: `ai` and `@ai-sdk/openai-compatible`

**Router Pattern** (from `apps/cost-router/`, `apps/polyrouter/`):
```typescript
// Fetch models + health
const models = await pollinations("/v1/models");
const status = await pollinations("/models/status?minutes=30");

// Score/rank models by criteria (cost, health, latency, capability)
const chosen = rank(models, status, prompt);

// Call chosen model
const response = await pollinations("/v1/chat/completions", {
  model: chosen.id,
  messages: [...],
});

// Return response with routing trace header
```

**Verification:** Show 3 requests routed differently with reason for each.

## Collective Memory Agent (Bounty #15054)

Uses collective memory API at `https://memory.pollinations.ai` (or via MCP).

**Patterns from issue:**
- **Postcards**: user tells about day → agent leaves postcard, reads one from stranger
- **Tavern rumours**: keeper tells real gossip, user's rumour retold distorted
- **Dream swap**: tell dream → hear similar one → two get linked
- **Ask collective**: leave question → another agent may answer later
- **Nomic politician**: vote/propose in shared Nomic game
- **Day in life**: each run = one turn: read diary, do one thing, write entry
- **Explorer**: visit unseen space, contribute, report back
- **Duels**: challenge another agent to riddles/poems

**Implementation:** Create `apps/agent-<name>/agent.json` with system prompt that:
1. Reads from collective memory on start
2. Takes user input
3. Writes to collective memory
4. Returns response with discovered memory content

## MCP Server Integration (Bounty #15014)

**Live Catalog:** `GET https://gen.pollinations.ai/mcp`
```json
[
  {"id": "pollinations", "url": "https://gen.pollinations.ai/mcp/pollinations"},
  {"id": "ffmpeg", "url": "https://gen.pollinations.ai/mcp/ffmpeg"},
  {"id": "exa", "url": "https://gen.pollinations.ai/mcp/exa"},
  {"id": "composio", "url": "https://gen.pollinations.ai/mcp/composio"},
  {"id": "computer", "url": "https://gen.pollinations.ai/mcp/computer"}
]
```
All are remote Streamable HTTP, Bearer auth with dedicated key per client.

**Harness Adapter Pattern** (`polli-cli/src/harnesses/*.ts`):
```typescript
interface HarnessAdapter {
  id: string;
  label: string;
  description: string;
  restartHint: string;
  on(ctx, options): Promise<HarnessResult>;
  off(ctx): Promise<HarnessResult>;
  status(ctx): Promise<HarnessResult>;
}
```

**New `polli mcp` command would:**
1. Fetch live catalog
2. For each selected server, create dedicated key via `/account/keys`
3. Generate client-specific config (Claude Desktop, OpenCode, VS Code, etc.)
4. Write config to client's config location
5. Support `--client <name>` flag for target
6. Support `polli mcp remove <server> --client <name>` for cleanup

## Verification Checklist for All Bounties

- [ ] Agent/code agent works end-to-end when deployed
- [ ] Self-test request succeeds (counts for "agent gets used" quest)
- [ ] PR includes `Fixes #<bounty-number>` in body
- [ ] PR passes CI (lint, typecheck, tests)
- [ ] After merge: Claim quest on https://enter.pollinations.ai/quests
- [ ] Pollen balance increases