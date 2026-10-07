---
topic: ml-ai
subtopic: hermes-training-improvement
domain: ML-AI
stage: Sandee
created_utc: 2026-08-09T15:40:00Z
---
# Sandee Technical Extraction

## Finding
Hermes improves system behavior through provider/model selection, skills, project context, persistent memory/session search, tools/MCP, delegation, routing, fallback and prompt caching. Ordinary use does **not** automatically update base-model weights. Trajectories can become data for an explicit external SFT/RL workflow, but that is not online learning.

## Mechanism boundaries

| Mechanism | Good for | Does not do |
|---|---|---|
| Skills | reusable procedures, style rules, checklists | change model weights; not a live fact database |
| Project context | stable project rules and contracts | replace evaluation or memory policy |
| Memory/session history | preferences, decisions, continuity | guarantee truth; can pollute context |
| Tools/MCP | capabilities and external state | guarantee correct tool selection or recovery |
| Routing/fallback | availability, cost/latency policies | prove quality equivalence across providers |
| Prompt caching | lower repeated-context cost/latency | improve reasoning quality by itself |
| Delegation | parallel specialists and review | eliminate orchestration errors |
| Evals/traces | measure and diagnose behavior | train weights without a separate ML workflow |

## Recommended technical loop

Instrument task, model/provider ID, skills, memory retrieval, tool calls/results/errors, retries, latency, tokens/cost, artifact/tests and approval status. Redact secrets. Classify failures before editing skills. Maintain versioned train/dev/holdout evals and safety cases.

## Sources
- Hermes docs: https://hermes-agent.nousresearch.com/docs/llms.txt
- Skills: https://hermes-agent.nousresearch.com/docs/user-guide/features/skills
- Memory: https://hermes-agent.nousresearch.com/docs/user-guide/features/memory
- Repository: https://github.com/NousResearch/hermes-agent
