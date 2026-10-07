---
topic: ml-ai
subtopic: hermes-training-improvement
domain: ML-AI
stage: Bella
status: final
created_utc: 2026-08-09T15:40:00Z
---
# Convergence Report: วิธีทำให้ Hermes เก่งขึ้น

## Verdict
**เริ่มด้วย evaluation-led system improvement ไม่ใช่ fine-tuning**

Hermes ไม่ได้เรียนรู้เปลี่ยนน้ำหนัก model อัตโนมัติจากการใช้งานปกติ แต่ทำให้เก่งขึ้นตาม workload ได้ผ่าน skills, project context, memory/session retrieval, tools, routing, delegation, model/provider policy และ feedback loop ที่ตรวจสอบได้ ส่วน SFT/DPO/RL/RFT เป็นขั้น ML แยกต่างหากและมักผูกกับ base model/provider

## Recommended improvement pipeline

```text
1. Instrument runs and tool traces
2. Build 50–100 representative tasks + sealed safety holdout
3. Freeze baseline: model/provider, skills, memory, tools, cache, fallback
4. Classify failures: knowledge/retrieval, procedure, tool schema, reasoning, style, safety
5. Fix system layer first: tool contracts, approval, skills, memory policy, retrieval, routing
6. Re-run dev + holdout; canary only verified changes
7. If a stable model-internal gap remains, try trace SFT
8. If stable Thai/style preference gap remains, collect chosen/rejected pairs and test DPO
9. Use RL/RFT only for sandboxed sequential tasks with executable rewards
10. Version, monitor, rollback, and feed new failures into the eval set
```

## What belongs where

- **Skills:** procedures, style rules, checklists, tool protocols
- **Memory:** stable preferences/decisions with provenance, scope, TTL and deletion
- **RAG/project context:** changing facts and source-backed knowledge
- **Trace SFT:** repeated tool/workflow behavior failures after system fixes
- **DPO:** consistent style/preference gaps with reliable pair labels
- **RL/RFT:** code or other tasks with trustworthy executable verifiers
- **Policy outside the model:** secrets, approvals, destructive actions and external sends

## BooM-specific evaluation

Include Thai naturalness, PAC Format A/B, source-grounded research, Windows file edits with verification, tool-loop recovery, memory scope/recall, coding tests, Telegram constraints and safety injection cases. Score accepted-result rate, severity-weighted failure, tool correctness, citation support, style/format adherence, retries, latency, tokens/cost and human acceptance.

## Final recommendation
For BooM's Hermes, the highest-leverage first project is an **eval + trace + skill/memory/tool-contract loop**. Do not fine-tune until that loop proves a stable failure that cannot be solved by external context or system controls. Keep provider-specific fine-tuned models optional; keep the control plane, safety gates and knowledge in Hermes.

## Pipeline artifacts
- Plawan: `Output/Plawan/ML-AI/20260809-hermes-training-blueprint.md`
- Sandee: `Output/Sandee/ML-AI/20260809-hermes-training-technical.md`
- Arm: `Output/Arm/ML-AI/20260809-hermes-training-audit.md`
- Nan: `Output/Nan/ML-AI/20260809-hermes-training-critique.md`
- Bella: this report
- Knowledge: `Knowledge/Convergence-Database/ML-AI Insights/20260809-hermes-training-insight.md`

## Sources
- Hermes docs: https://hermes-agent.nousresearch.com/docs/llms.txt
- Hermes skills: https://hermes-agent.nousresearch.com/docs/user-guide/features/skills
- Hermes memory: https://hermes-agent.nousresearch.com/docs/user-guide/features/memory
- OpenAI optimization/evals/SFT guidance: https://developers.openai.com/api/docs/guides/model-optimization.md
- InstructGPT: https://arxiv.org/abs/2203.02155
- DPO: https://arxiv.org/abs/2305.18290
- Toolformer: https://arxiv.org/abs/2302.04761
- ReAct: https://arxiv.org/abs/2210.03629
- RAG: https://arxiv.org/abs/2005.11401
- DeepSeekMath/GRPO: https://arxiv.org/abs/2402.03300
- SWE-bench: https://arxiv.org/abs/2310.06770
