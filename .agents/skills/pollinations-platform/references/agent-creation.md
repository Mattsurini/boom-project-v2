# Agent Creation & Deployment

How to create and deploy agents on Pollinations for the "Create an agent that gets used" quest.

## Agent Types

### Prompt Agent (No Code)
- Pure configuration: system prompt + base model + MCP servers
- Created via Web UI at enter.pollinations.ai/my-models
- No code, no hosting required
- Best for quests and simple agents

### Code Agent (Advanced)
- Custom logic in TypeScript/JavaScript
- Deployed to Pollinations infrastructure
- Requires `apps/agent-<name>/` structure with agent.json
- See `references/pr-workflow.md` for repo structure

## Prompt Agent Creation (Web UI)

### Step-by-Step
1. Go to https://enter.pollinations.ai/my-models
2. Login if needed
3. Click **Add Agent** → **Prompt Agent**
4. Fill configuration:

```json
{
  "name": "my-test-agent",
  "title": "My Test Agent",
  "description": "Simple test agent for quest",
  "baseModel": "openai/gpt-5.4-nano",
  "systemPrompt": "You are a helpful assistant. Reply briefly in 1-2 sentences.",
  "mcpServers": ["pollinations"]
}
```

5. Click **Save** / **Deploy**
6. System generates **Agent ID** (UUID) and URL: `community/<github-username>/<agent-name>`
7. Click **Playground** / **Test** button
8. Send test message: `Hello`
9. Verify response received
10. Quest complete → Claim at enter.pollinations.ai/quests

## Required Fields
| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Unique identifier (lowercase, hyphens) |
| `title` | Yes | Display name |
| `description` | No | Shown in agent directory |
| `baseModel` | Yes | Model ID from free models list |
| `systemPrompt` | Yes | Agent personality/instructions |
| `mcpServers` | No | Array of MCP servers (e.g., `["pollinations"]`) |

## Model Selection for Quests
**Always use free models** to avoid credit errors:
- `openai/gpt-5.4-nano` (recommended)
- `deepseek/deepseek-v4-flash`
- `z-ai/glm-5.3-flash`

## MCP Servers
- `pollinations` — enables `generateImage` tool, model access
- `ffmpeg` — audio/video processing
- `exa` — web search
- `composio` — app integrations
- `computer` — persistent computer

## Testing via API (After Deployment)
```bash
# Replace with your actual agent URL
curl -s https://gen.pollinations.ai/v1/chat/completions \
  -H "Authorization: Bearer $POLLINATIONS_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"community/<YOUR_GITHUB_USERNAME>/my-test-agent","messages":[{"role":"user","content":"Hello"}]}'
```

## Verification Checklist
- [ ] Agent deployed successfully (shows Agent ID)
- [ ] Playground test returns response
- [ ] No "not enough credits" error
- [ ] Quest shows complete after 1-2 min refresh
- [ ] Claim both "Create an agent that gets used" entries (2 pollen each)

## Common Issues
| Issue | Fix |
|-------|-----|
| "Model needs paid Pollen" | Change baseModel to free model |
| Deploy fails | Check name uniqueness, try different name |
| Playground error | Wait a minute after deploy, try again |
| Quest not tracking | Ensure test request went through (check Playground response) |