# TencentDB Agent Memory with Hermes

Use the provider's Hermes adapter guide at `memory_integration/tencentdb-agent-memory/MemoryCore/hermes-plugin/memory/memory_tencentdb/README.md`; do not apply its OpenClaw installation instructions to Hermes.

## Install and activate

1. Confirm the active Hermes agent checkout and `HERMES_HOME` with `hermes config path`, `hermes config env-path`, and the actual CLI installation path.
2. Check the plugin guide and `MemoryCore/package.json` for the provider key, host API, Node requirement, and Gateway command. Install/copy the Hermes provider so its final directory is exactly `plugins/memory/memory_tencentdb/` and includes its entrypoint and plugin metadata.
3. Install the Gateway's Node dependencies from its documented package directory. Use the provider's own launch instructions; the repository may include multiple host integrations and similarly named scripts.
4. Enable it with `hermes config set memory.provider memory_tencentdb`.
5. Persist `MEMORY_TENCENTDB_GATEWAY_CMD` in the environment inherited by Hermes if auto-discovery cannot find `src/gateway/server.ts`. Quote paths containing spaces and use an absolute entrypoint; Hermes may launch from a different working directory.
6. Restart Hermes so the active agent loads the provider and environment, then run `hermes memory status`.

## OpenAI-compatible LLM endpoint

The Gateway reads `TDAI_LLM_API_KEY`, `TDAI_LLM_BASE_URL`, and `TDAI_LLM_MODEL`. Store credentials in the active Hermes environment file returned by `hermes config env-path`; do not put secrets in project config, shell command history, chat, or logs.

For NVIDIA NIM, the hosted API base URL is `https://integrate.api.nvidia.com/v1`. Choose an available chat model ID from the live NVIDIA API Catalog. NIM advertises free trial endpoints, but rate limits/model availability can vary; treat free access as development/testing, not a production guarantee. Restart Hermes/Gateway after changing these variables.

## Verify capabilities separately

- `hermes memory status`: provider is installed, available, and active.
- `GET http://127.0.0.1:8420/health`: Gateway health.
- Use the provider API to initialize and perform a read-only prefetch/recall request.
- Inspect Gateway status/logs for the actual LLM and embedding configuration; do not infer extraction or vector search from health alone.
- Confirm the storage backend and data directory. The default standalone setup uses local SQLite; the product name does not imply a remote Tencent VectorDB connection.

If an API key was pasted into chat, advise rotating it before setup. Verify only the presence of its environment variable, never print its value.

## Historical conversation import and vector backfill

1. Preview the selected conversation corpus before sending it to an external LLM: retain only the intended user/assistant messages, exclude tool/system/reasoning content, redact secrets, and get explicit user approval for the external transfer. Keep approval scoped to the previewed corpus and destination.
2. Treat ingestion, L1 extraction, and L0 vector generation as separate stages. An imported L0 row is not evidence that extraction ran or a vector exists; report per-stage counts rather than one blended completion number.
3. Before starting a backfill, inspect for an existing matching process and query the target DB's aggregate counts. If the launcher returns early or reports a terminal/TTY issue, check whether the child process actually started before retrying; duplicate workers can waste API quota or create competing writes.
4. While an existing backfill runs, monitor that process, Gateway health, and aggregate counts for the specifically imported corpus. Do not launch a second worker or restart a healthy Gateway just because progress is asynchronous. Do not use global vector totals when the DB also contains unrelated records.
5. Verify completion against the imported L0 denominator: `present + missing = imported`; finish only when the process exits successfully and missing is zero (or explicitly report any unreconciled failures). Check L1 extraction counts separately; Gateway health, L0 vector completion, and embedding-task summaries do not prove L1 coverage.
6. Attribute 429/413 or other API failures only when sanitized logs tie them to the specific stage and terminal outcome. A global error count does not establish why records lack vectors or extracted memories.