---
name: hermes-telegram-setup
description: "Use when setting up Telegram for a Hermes project."
version: 1.0.0
author: Hermes Agent
platforms: [windows, macos, linux]
---

# Hermes Telegram Setup

Configure the Telegram messaging platform in Hermes Agent so you can interact with the agent via Telegram bot.

## Prerequisites

- A Telegram bot token obtained from @BotFather.
- Hermes Agent installed and running.

## Procedure

0. **Diagnose before configuring anything.** "Telegram works" and "Telegram is connected to my
   project" are different states, and the second is almost always what was asked. Establish which
   one already holds so you only change what is actually broken:
   ```bash
   hermes config get platforms    # enabled flag + masked token; never read the real token
   hermes gateway status
   hermes cron list               # an active job with a platform target proves the transport
   grep -i "inbound message: platform=" <hermes-home>/logs/gateway.log | tail -5
   ```
   If inbound lines are appearing, token, polling, and pairing are all fine and the gap is almost
   always the working directory (step 2). Spending the turn on the token is wasted effort.

1. **Enable the Telegram platform**
   Set the enabled flag to true in the Hermes configuration:
   ```bash
   hermes config set platforms.telegram.enabled true
   ```

2. **Set the bot token**
   Store your Telegram bot token (from @BotFather) securely:
   ```bash
   hermes config set platforms.telegram.token <YOUR_BOT_TOKEN>
   ```
   Replace `<YOUR_BOT_TOKEN>` with the token string (e.g., `123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11`).

3. **Anchor the gateway to the project folder.**
   `terminal.cwd` is the working directory for gateway, cron, and delegation sessions (the CLI
   always uses its own launch directory). It is also the root that context-file discovery hangs
   off, so an unanchored gateway never reads the project's `AGENTS.md` / `.hermes.md` and behaves
   like a generic assistant with no project memory:
   ```bash
   hermes config set terminal.cwd "E:\\Boom Project"   # absolute path, quoted
   ```

4. **Restart the Hermes gateway**
   Apply the changes by restarting the gateway service:
   ```bash
   hermes gateway restart
   ```
   Confirm the gateway is running:
   ```bash
   hermes gateway status
   ```

5. **Verify the setup**
   - List gateways to see the default gateway running:
     ```bash
     hermes gateway list
   ```
   - Open Telegram and search for your bot by its username (set in BotFather).
   - Send `/start` or any message to the bot. The Hermes agent should respond.

## Notes

- The bot username is set when creating the bot with @BotFather, not in Hermes configuration.
- Hermes uses the `hermes-telegram` toolset for the Telegram platform (see `platform_toolsets.telegram` in config.yaml).
- No further configuration is required unless you wish to customize toolsets or behavior.
- If you encounter issues, check the gateway logs: `hermes logs` or `hermes logs --since 1h`.
- For per-surface cwd semantics, context-discovery rules, and how to prove an anchor reached the running process, see `references/gateway-cwd-and-context.md`.

## Pitfalls

- **Do not edit config.yaml manually** — always use `hermes config set` to avoid YAML syntax errors that can break the gateway.
- **Token security** — the token is stored in plain text in `config.yaml`; ensure your Hermes instance is secure.
- **Gateway restart required** — platform config AND `terminal.cwd` both need it; only the new process carries the new anchor.
- **`terminal.cwd: "."` is a placeholder, not "here".** A gateway runs as a background service with no meaningful launch directory, so the placeholder resolves to the user's home dir and every turn executes outside the project. Symptom: the bot replies fluently but knows nothing about the project, or asks where the project is.
- **Verify the live process, not the config file.** A correct config is not proof the running gateway adopted it — a stale process keeps the old anchor indefinitely. Read the running gateway's own environment and confirm `TERMINAL_CWD`.
- **Never grade a config change with the built-in defaults loader.** Internal `_cli_config_defaults()` returns hardcoded defaults (including `cwd: "."`) before user config is merged, so it reports a correctly-set field as unset and sends you chasing a phantom bug. Parse the real config file, or assert through the same resolver the gateway uses.
- **Project-local skills need a `.git` ancestor.** Project-skill discovery keys off the nearest `.git`, so in a non-repo project folder `skills.trusted_project_dirs` can never match and `.hermes/skills/` + `.agents/skills/` stay invisible no matter how the cwd is anchored. Copy them into the profile skills dir, or make the folder a repo — the user decides.
- **No allowlist means default-deny, and a boot warning.** Without `<PLATFORM>_ALLOWED_USERS` / `GATEWAY_ALLOWED_USERS` the gateway runs pairing-only and logs the warning on every start. Approved senders live in the pairing file; pairing already works, the line is just noise — offer to pin the ID rather than treating it as a fault.

## Verify

Do not report completion until all four hold:
- [ ] Live gateway process environment shows `TERMINAL_CWD` equal to the project path
- [ ] The gateway's own cwd resolver, replayed against the real config, returns the project path (and it is not a placeholder)
- [ ] Context discovery from that path finds the project's `.hermes.md` / `AGENTS.md`
- [ ] `hermes send -t telegram:<chat_id> "..."` returns `sent`

Then state plainly what you did NOT change and why (unanchored project skills, missing allowlist) so the user decides instead of discovering it later.
