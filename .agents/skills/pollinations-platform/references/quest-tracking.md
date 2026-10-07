# Quest Tracking & Common Failures

How Pollinations quest detection works and common reasons quests don't register.

## How Quest Tracking Works
- Quests track **API calls made with an API key linked to your logged-in account**
- System polls recent API usage (last few minutes) when you refresh the quests page
- Some quests require **Web UI interactions** (session cookies) rather than raw API calls

## Quest-Specific Tracking

| Quest | Tracking Method |
|-------|----------------|
| Create API key | Account key creation event |
| Use text/image/audio model | API call to respective endpoint with linked key |
| Use an agent | API call to `/v1/chat/completions` with agent model ID |
| Use a Pollinations app | OAuth authorize flow on pollinations.ai/apps (requires session) |
| Create agent that gets used | Agent deployment + test request via Playground |
| Contribute PR | GitHub PR merged to pollinations/pollinations |

## Common Failures & Fixes

### 1. API Key Not Linked to Current Account
**Symptom**: API calls succeed but quests don't track
**Cause**: Key created before current login, or from different account
**Fix**: Create new key at https://enter.pollinations.ai/keys AFTER logging in

### 2. Quest Tracking Delay
**Symptom**: Just made API calls, quests show incomplete
**Cause**: Backend sync takes 1-2 minutes
**Fix**: Wait 1-2 minutes, refresh quests page

### 3. Paid Model Errors
**Symptom**: `"not enough credits"` or `"This model needs paid Pollen"`
**Cause**: Model requires paid Pollen balance
**Fix**: Use free models only (see `references/free-models.md`)

### 4. Agent Quest Requires Web UI
**Symptom**: No API endpoint to create agents
**Cause**: Agent creation only via enter.pollinations.ai/my-models UI
**Fix**: Use Web UI → Add Agent → Prompt Agent → Deploy → Test via Playground

### 5. "Use a Pollinations App" Requires OAuth
**Symptom**: API calls to apps don't count
**Cause**: Quest tracks OAuth authorize flow, not API usage
**Fix**: Go to https://pollinations.ai/apps → Click Connect → Authorize wallet

### 6. Web UI Calls Track Better Than curl
**Symptom**: curl calls work but quest doesn't register
**Cause**: Playground/Try-it buttons use session cookies + account context
**Fix**: Use Web UI Playground buttons on docs pages for critical quests

### 7. No Open "Good First Issue" Labels
**Symptom**: GitHub API returns 0 issues for `good first issue` label
**Cause**: Label not currently applied to open issues
**Fix**: Check DEV-BUG, documentation, or POLLEN-QUEST issues instead

## Verification Commands
```bash
# Verify key is valid and linked
curl -s https://gen.pollinations.ai/account/key -H "Authorization: Bearer $POLLINATIONS_KEY"

# Check recent API usage (if endpoint exists)
curl -s https://gen.pollinations.ai/account/usage -H "Authorization: Bearer $POLLINATIONS_KEY"

# Test free model quickly
curl -s https://gen.pollinations.ai/v1/chat/completions \
  -H "Authorization: Bearer $POLLINATIONS_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"openai/gpt-5.4-nano","messages":[{"role":"user","content":"test"}]}'
```

## Debugging Checklist
- [ ] Logged in at enter.pollinations.ai/quests
- [ ] API key created AFTER login at enter.pollinations.ai/keys
- [ ] Using free models only
- [ ] Waited 1-2 minutes after API calls
- [ ] Refreshed quests page
- [ ] For app quest: completed OAuth on pollinations.ai/apps
- [ ] For agent quest: deployed via Web UI and tested via Playground