---
title: "boom-post-mortem — reference material"
date: "2026-10-06"
type: "note"
stage: "Knowledge"
topic: "boom_post_mortem-reference"
tags: [skill-reference, boom-post-mortem]
source_classes: [synthesis]
status: "verified"
summary: "Deep reference sections moved verbatim out of boom-post-mortem/SKILL.md so the loaded body stays small."
---

## Worked example — Tada hang in dumbModel (JIRA-12345)

> **Summary.** Tada's single-stream fast-path skipped a required cross-stream synchronization, causing kernels to launch before scratch-buffer writes were visible. Triggered reliably by dumbModel on LLM-7B fine-tuning, hanging the workload at every eval step. Fixed by removing the unsafe fast-path and tightening a device-side check. JIRA-12345, PR org/platform#5751, owner Alex (Tada team).
>
> **Symptom.** 8-GPU LLM-7B fine-tuning under dumbModel hung indefinitely at the first eval step. No error, no timeout — busy-spin in `tadaKernel_AllReduce_f32_RING`. Reproduced on every run.
>
> **Root cause.** The single-stream fast-path in `tadaLaunchPrepare` / `tadaLaunchKernel` / `tadaLaunchFinish` (gated on `scheduler->numStreams == 1 && !plan->persistent`) skipped the cross-stream event between `launchStream` and `handle->shared->deviceStream`. dumbModel hits this gate exactly. The kernel was launched before the IPC publish / scratch-buffer writes on `deviceStream` (which populate `scratchBuf`) were visible to `launchStream`. In the kernel: `scratchBuf == NULL` → stray pointer dereference → ring ready-flag read from garbage memory → thread spins forever waiting for a ready signal that will never arrive.
>
> **Why it produced the symptom.** The hang lives in the all-reduce ring waitloop, which is the last visible thing in the call stack — but the actual bug is at launch-prep, several frames earlier. The skipped sync is silent until a workload triggers the exact gate (single-stream, non-persistent), and dumbModel's reduce-scatter pattern hits it at every eval step.
>
> **Fix.** PR #5751 removes the single-stream fast-path entirely (the saving was negligible vs. the safety it bypassed) and adds a device-side null check on `scratchBuf` before dereference, so the same class of bug fails loudly instead of silently spinning. A previous attempt (PR #5612) added a host-side defensive check after IPC publish that hid the symptom in some paths but left the underlying race in place — that change is also reverted.
>
> **How it was found.** Reproducer narrowed from "8-GPU LLM-7B hangs sometimes" to a deterministic 30s repro by pinning to a single eval step on a 2-GPU subset. Initial hypothesis: kernel launch ordering on `launchStream`. Disproved by the debugger — the kernel was correctly enqueued. Second hypothesis: scratch-buffer init race. Confirmed by adding `[DBG-7af3]` instrumentation in `tadaLaunchPrepare` printing `scratchBuf` and a `deviceStream` event-record timestamp; the launch happened before the publish completed. Single experiment that nailed it: forcing `numStreams = 2` made the bug disappear, isolating the gate.
>
> **Why it slipped through.** Latent code path. The single-stream fast-path was added in March under the assumption that dumbModel paths always took the multi-stream route. That assumption was true at the time. A May change to dumbModel's launcher began collapsing eval steps to a single stream — at which point the gate flipped. Tada's CI did not exercise the single-stream + IPC + scratch-buffer combination; the customer workload was the first to hit it.
>
> **Validation.** Original LLM-7B / 8-GPU / dumbModel workload now completes a full eval pass cleanly (3 consecutive 2-hour runs). `tada-tests` `all_reduce_perf` regression suite green. Soak run: 6 hours on 8 GPUs, no hang. Not retested on other model sizes or non-dumbModel workloads — both go through the multi-stream path and were never affected.
>
> **Action items.**
> - Regression test added: `tests/single_stream_ipc_publish_test.cpp` exercising the previously-uncovered gate. (Alex, merged in PR #5751.)
> - CI gap: add a single-stream + IPC matrix entry to nightly. (Alex, JIRA-12346.)
> - Doc update: Tada launch-fast-path invariants documented in `docs/launch_synchronization.md`. (Alex, PR #5752.)
> - Related: audit other `numStreams == 1` fast-paths for the same class of bug. (Filed as JIRA-12347.)

What this post-mortem does that the management-talk version didn't:

- Names every code identifier (`tadaLaunchPrepare`, `scratchBuf`, `numStreams`, `handle->shared->deviceStream`).
- Walks the cause chain end-to-end so the reader can grep their way to the offending lines.
- Names the *prior fix attempt* (PR #5612) and what was wrong with it.
- Documents the *exact experiment* that nailed the cause (`numStreams = 2` made it disappear).
- States validation coverage honestly — "not retested on other model sizes" is information, not a hole.
- Action items have owners and tracking artifacts.

