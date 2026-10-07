---
name: docker-mcp
user-invocable: true
allowed-tools: terminal, web_extract
description: Workflow for using and verifying Docker MCP Toolkit.
---

# Docker MCP Toolkit Skill

## Setup and Verification Workflow
1. **Verify Connection**: Use `docker mcp profile list` to confirm your profile exists.
2. **Dry Run**: Before starting a gateway for real, run `docker mcp gateway run --profile <profile_id> --dry-run` to ensure all servers, tools, and OCI images are correctly configured and accessible.
3. **Pitfall: Flag Conflicts**: Do not use `--profile` with individual `--servers`, `--enable-all-servers`, or manual registry/catalog flags. The profile acts as a complete configuration unit.
4. **Pitfall: Gateway Initialization**: Allow ~8-10 seconds for the Docker MCP Gateway to fully initialize dynamic tools and OAuth providers before assuming commands will succeed.

## Adding remote (non-OCI) HTTP MCP servers
`docker mcp profile server add` accepts `https://` ONLY as an MCP-Registry reference (registry.modelcontextprotocol.io), NOT an arbitrary remote endpoint — a bare `https://host/mcp/x` URL is rejected ("invalid registry URL"). Remote servers that are published in the registry can be added by registry name, but the name's slash must be URL-encoded:
- `docker mcp profile server add <profile> --server "https://registry.modelcontextprotocol.io/v0/servers/<ns>%2F<name>"`
- Plain-name form (`.../servers/<ns>/<name>`) 404s; the CLI drops the last path segment. URL-encoded-slash form resolves.
- Find names via `curl 'https://registry.modelcontextprotocol.io/v0/servers?search=<term>&limit=50'` (returns reverse-domain names like `io.github.pollinations/pollinations`).
- After add, each server declares a secret in `profile show` as `<server-name>.<var>` (e.g. `io-github-pollinations-pollinations.api_key`, env `API_KEY`). Set each with `printf '%s' "$KEY" | docker mcp secret set <name>` (stdin so the secret never hits the process list). The gateway injects it into the header (e.g. `Authorization: Bearer ***`).
- A "Dynamic OAuth discovery failed" / "OAuth notification monitor" warning during add/dry-run is harmless for Bearer-auth servers (no OAuth metadata at the host root).
- Verify with `docker mcp gateway run --profile <id> --dry-run` (lists tool counts per server from the live endpoint), then prove auth by calling a free tool (e.g. `listModels`) directly with `curl` + `Authorization: Bearer ***

## Connecting an AI client to a profile
1. **List clients**: `docker mcp client ls --global` — the `--global` flag is REQUIRED; without it the CLI fails with "could not find root project root". Supported clients: claude-code, claude-desktop, cline, codex, continue, crush, cursor, gemini, goose, gordon, kiro, lmstudio, opencode, sema4, vscode, zed.
2. **Connect**: `docker mcp client connect <client> -p <profile_id> --global`. This writes the client's MCP config (VS Code: `%APPDATA%\Code\User\mcp.json`) with a stdio entry that runs `docker mcp gateway run --profile <profile_id>`.
3. **No separate activation step**: the profile is baked into the client's gateway launch command, so the client's gateway loads the profile's servers automatically on start. Do NOT try to "activate" the profile via `mcp-activate-profile` — see pitfall below.
4. **Restart the client** after connecting; it only picks up the new MCP config on restart.
5. **Verify** with `docker mcp gateway run --profile <profile_id> --dry-run` (lists per-server tool counts from the live images).

**Pitfall: `docker mcp tools ls/call` is NOT the client's gateway.** These commands spawn their own ephemeral gateway using the *default* profile (log shows "Default profile not found, using empty configuration"), so they cannot activate a profile for a connected client or reflect its state. Verify what a client will actually load via `--dry-run` of the same `--profile` the client config uses.

## Usage
- **Invoke Tools**: Use `docker mcp gateway run --profile <profile_id>` to start the gateway in stdio mode for AI clients.
- **Troubleshooting**: If a specific server (e.g., Playwright) fails, run `docker mcp gateway run --profile <profile_id> --dry-run` to see if the OCI image is pulled correctly or if there are path/config conflicts.
