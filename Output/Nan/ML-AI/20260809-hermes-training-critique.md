---
topic: ml-ai
subtopic: hermes-training-improvement
domain: ML-AI
stage: Nan
created_utc: 2026-08-09T15:40:00Z
---
# Nan Adversarial Critique

## Rejected claim
“Add more prompts/memory and Hermes is trained to become smart” is misleading.

## Confounds
- benchmark leakage and prompt overfitting
- memory pollution or retrieval of the answer
- provider/model/version drift
- changed tool harness, cache or fallback path
- reward hacking and optimizing an LLM judge
- unsafe learned tool behavior
- measuring fluent prose instead of accepted task completion

## Go/no-go rule
A change is accepted only if it wins on sealed holdout tasks and unseen paraphrases, while safety violations, citation errors, tool failures, retries, latency and cost per accepted result do not regress. Fine-tune only after skills/context/tool-contract fixes plateau and the remaining gap is stable and model-internal.
