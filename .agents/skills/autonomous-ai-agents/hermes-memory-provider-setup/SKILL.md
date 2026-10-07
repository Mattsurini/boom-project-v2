---
name: hermes-memory-provider-setup
description: Use when configuring or debugging Hermes memory providers.
version: 0.1.0
author: BooM, Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [hermes, memory, providers]
    related_skills: [hermes-agent]
---
# Hermes External Memory Provider Setup

Use this workflow for external memory providers that run locally, as Hermes plugins or through a sidecar Gateway. It covers setup, secret handling, activation, and runtime verification; use the provider's own guide for version-specific details.

## When to Use

- A user wants to install, enable, or troubleshoot an external Hermes memory backend.
- The backend has a local service/sidecar, a separately configured LLM, or a non-default storage engine.
- A memory API credential or OpenAI-compatible model endpoint must be configured for the backend.

## Procedure

1. Establish the active Hermes installation before editing anything:
   - `hermes --version`
   - `hermes config path`
   - `hermes config env-path`
   - `hermes memory status`
   Resolve provider installation paths from the active `HERMES_HOME`, not a guessed `~/.hermes`.
2. Read the provider's Hermes-specific install and runtime guides. Distinguish its Hermes adapter from OpenClaw/other-host instructions; check required host, runtime, and Node versions in its package manifest.
3. Install the provider at the path and package name Hermes discovers. Preserve its required directory name and import/API contract. Install sidecar dependencies in the provider's documented working directory.
4. Select the provider with `hermes config set memory.provider <provider-name>`. Keep non-secret settings in Hermes configuration; keep API keys in the active Hermes environment file or supported secret store. Never print or reread secret values to verify them; check only whether required variable names are present.
5. If a sidecar needs a launch command, configure it in the environment inherited by Hermes. Use an absolute, correctly quoted entrypoint when Hermes may start outside the provider checkout. Persist the command using the provider's supported method.
6. Configure any LLM/embedding backend separately from the memory provider. Confirm the backend uses an API protocol the sidecar supports. For NVIDIA NIM, use the OpenAI-compatible endpoint and a currently available model ID from NVIDIA's catalog; free-tier limits and model availability can change.
7. Restart Hermes after changing provider or environment settings. An already-running agent does not reload provider selection or environment variables.
8. Verify each layer independently:
   - `hermes memory status` shows the intended provider installed, available, and active.
   - Check the sidecar's documented health endpoint.
   - Initialize the provider and make a harmless read-only recall/prefetch call; confirm it reaches the Gateway.
   - Check capture, LLM extraction, embeddings, and storage backend independently. A healthy HTTP endpoint does not prove these optional capabilities are configured.
9. Report what is active now, what requires a fresh Hermes process, the actual storage backend, and any capability that remains degraded.

## Pitfalls

- Do not infer that Docker owns a sidecar: inspect its launch configuration and health endpoint; many memory Gateways run as local Node processes.
- Do not conflate Hermes built-in memory, project registries, and external memory-provider stores; they have different owners and persistence paths.
- A provider reported as available may only mean its adapter imports. Confirm initialization and a Gateway request before claiming runtime integration.
- `vectorStore: true` or Gateway `status: ok` does not mean embeddings or LLM extraction are enabled; inspect their explicit status and run a safe capability check.
- A Codex/OAuth login in Hermes is not automatically an API credential for an external Node sidecar. Use a supported API-compatible endpoint and its own credential path.
- If a user posts an API key in chat, do not repeat or place it in command arguments or logs. Recommend revocation/rotation, then keep its replacement in the approved local secret store.

## Provider Recipe

For TencentDB Agent Memory, use [the focused setup and verification reference](references/tencentdb-agent-memory.md).