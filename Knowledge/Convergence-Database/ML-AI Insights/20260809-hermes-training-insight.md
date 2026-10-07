---
title: "Hermes Agent Improvement Loop"
date: "2026-08-09"
type: insight
stage: Knowledge-Distillation
topic: ml-ai
subtopic: hermes-training-improvement
tags: [ml-ai, hermes, agent-improvement, evaluation, fine-tuning]
status: final
---
# Reusable Insight

Hermes should be improved through an evaluation-led system loop first: instrument traces, build sealed holdouts, fix tools/skills/memory/context/routing, and accept only verified gains. SFT is a later option for stable tool/workflow gaps; DPO is for consistently labeled style preferences; RL/RFT is reserved for sandboxed tasks with executable rewards. Skills, memory and RAG improve external behavior and continuity; they do not update base-model weights automatically.

Source report: `Output/Bella/ML-AI/20260809-hermes-training-convergence-report.md`
