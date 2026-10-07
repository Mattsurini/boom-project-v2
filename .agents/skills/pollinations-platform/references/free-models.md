# Free Models Reference

Curated list of free models on Pollinations (no credits/Pollen required).

## Text Models
| Model ID | Provider | Notes |
|----------|----------|-------|
| `openai/gpt-5.4-nano` | OpenAI | Fast, reliable, good for quests |
| `deepseek/deepseek-v4-flash` | DeepSeek | Strong reasoning, free |
| `z-ai/glm-5.3-flash` | Z.ai | Good general purpose |
| `openai/gpt-5-nano` | OpenAI | Alternative nano variant |
| `meta/llama-3.3-70b-instruct` | Meta | Large open model |
| `qwen/qwen3.8-2.4t-a95b` | Qwen | MoE model, strong coding |

## Image Models
| Model ID | Provider | Notes |
|----------|----------|-------|
| `black-forest-labs/flux.1-schnell` | BFL | Fast Flux variant, free |
| `openai/gpt-image-1-mini` | OpenAI | Mini version, free |
| `openai/gpt-image-2` | OpenAI | May require credits |
| `amazon/nova-canvas-v1` | Amazon | Free tier available |
| `lykon/dreamshaper-8-lcm` | Lykon | LCM fast generation |

## Audio Models
| Model ID | Provider | Notes |
|----------|----------|-------|
| `openai/tts-1` | OpenAI | Standard TTS, free |
| `openai/gpt-audio-mini` | OpenAI | Audio model, free |
| `openai/whisper-large-v3` | OpenAI | STT, free |
| `assemblyai/universal-2` | AssemblyAI | STT, free |

## Community Agents (Free)
| Model ID | Description |
|----------|-------------|
| `community/Lorodn4x/deepseek-v4-flash` | DeepSeek v4 flash wrapper |
| `community/pollinations-router/polli` | Pollinations router agent |
| `community/YoannDev90/muse-glimmer-30b:free` | Free Muse Glimmer |
| `community/MarcosFRG/glm-5.3-flash` | GLM 5.3 flash |
| `community/vendouple/muse-glimmer-30b:free` | Free Muse Glimmer |

## Usage
```bash
export POLLINATIONS_KEY="sk_..."

# Text
curl -s https://gen.pollinations.ai/v1/chat/completions \
  -H "Authorization: Bearer $POLLINATIONS_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"openai/gpt-5.4-nano","messages":[{"role":"user","content":"test"}]}'

# Image
curl -s https://gen.pollinations.ai/v1/images/generations \
  -H "Authorization: Bearer $POLLINATIONS_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"black-forest-labs/flux.1-schnell","prompt":"test","width":512,"height":512}'

# Audio
curl -s https://gen.pollinations.ai/v1/audio/speech \
  -H "Authorization: Bearer $POLLINATIONS_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"openai/tts-1","input":"test","voice":"alloy"}' -o test.mp3

# Agent
curl -s https://gen.pollinations.ai/v1/chat/completions \
  -H "Authorization: Bearer $POLLINATIONS_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"community/Lorodn4x/deepseek-v4-flash","messages":[{"role":"user","content":"test"}]}'
```

## Verification
Check model pricing via API:
```bash
curl -s https://gen.pollinations.ai/v1/models -H "Authorization: Bearer $POLLINATIONS_KEY" | jq '.data[] | select(.pricing.prompt == "0" or .pricing.prompt == 0 or .pricing.prompt == null)'
```
Models with `prompt: N/A` or `0` are free.