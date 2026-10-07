#!/usr/bin/env bash
# export-hermes-state.sh — copy the Hermes per-machine state off this machine
# BEFORE reimaging. Everything here lives in %LOCALAPPDATA%\hermes and is NOT
# in the GitHub repo (by design: keys, tokens and machine identity).
#
# Run this on the OLD machine, then move hermes-state/ to the new one.
# On the new machine: run restore-hermes-state.sh (or just copy the files back
# into %LOCALAPPDATA%\hermes at the same paths).
#
# Usage:  bash export-hermes-state.sh
set -euo pipefail

_base="${LOCALAPPDATA:-$HOME/AppData/Local}"
HERMES_HOME="$(printf '%s' "$_base" | tr '\\' '/')/hermes"
OUT="${1:-./hermes-state}"

if [[ ! -d "$HERMES_HOME" ]]; then
  echo "no Hermes home at $HERMES_HOME" >&2
  exit 1
fi

mkdir -p "$OUT"
copied=0

copy_one() {
  local rel="$1" why="$2"
  local src="$HERMES_HOME/$rel"
  if [[ -f "$src" ]]; then
    mkdir -p "$OUT/$(dirname "$rel")"
    cp "$src" "$OUT/$rel"
    printf '  [ok]   %-34s %8s bytes  %s\n' "$rel" "$(stat -c%s "$src")" "$why"
    copied=$((copied + 1))
  else
    printf '  [--]   %-34s %8s\n' "$rel" "missing"
  fi
}

copy_dir() {
  local rel="$1" why="$2"
  local src="$HERMES_HOME/$rel"
  if [[ -d "$src" ]]; then
    mkdir -p "$OUT/$rel"
    # Plain cp -r has no exclude, and rsync may not exist on Windows Git Bash
    # (its absence silently fell through to the cp -r branch, dragging the
    # plugin's own .git/ and __pycache__/ along). Copy the tree, then prune.
    cp -r "$src/." "$OUT/$rel/"
    find "$OUT/$rel" -name '.git' -type d -prune -exec rm -rf {} + 2>/dev/null || true
    find "$OUT/$rel" -name '__pycache__' -type d -prune -exec rm -rf {} + 2>/dev/null || true
    find "$OUT/$rel" -name '*.pyc' -delete 2>/dev/null || true
    printf '  [ok]   %-34s %s\n' "$rel/" "$why"
    copied=$((copied + 1))
  else
    printf '  [--]   %-34s %s\n' "$rel/" "missing"
  fi
}

echo "Hermes home: $HERMES_HOME"
echo "Exporting to: $OUT"
echo
echo "CREDENTIALS (never commit this folder):"
copy_one ".env"                  "provider API keys"
copy_one "auth.json"             "login token (nous) + telegram bot token"
copy_one "config.yaml"           "model / provider / toolset config"
echo
echo "WORKING CONTEXT:"
copy_one "SOUL.md"               "agent identity"
copy_one "memories/MEMORY.md"    "agent notes"
copy_one "memories/USER.md"      "user profile"
copy_one "channel_directory.json" "telegram chat id"
echo
echo "SCHEDULED WORK:"
copy_one "cron/jobs.json"        "cron jobs"
echo
echo "PLUGINS (homeassistant re-installs from upstream; karpathy is local-only):"
copy_dir "plugins/karpathy-guidelines" "local plugin, no upstream remote"
copy_dir "plugins/homeassistant"       "upstream: github.com/NousResearch/hermes-homeassistant"

cat > "$OUT/RESTORE.md" <<'EOF'
# Restore onto the new machine

Order matters: install Hermes and log in FIRST, so %LOCALAPPDATA%\hermes exists
and Hermes has written its own auth.json / config.yaml — then overwrite them.

    1. install Hermes, run it once, log in
    2. close Hermes entirely (it caches state while running)
    3. copy each file back to %LOCALAPPDATA%\hermes at the SAME relative path:

         .env                    -> hermes\.env
         auth.json               -> hermes\auth.json
         config.yaml             -> hermes\config.yaml
         SOUL.md                 -> hermes\SOUL.md
         channel_directory.json  -> hermes\channel_directory.json
         memories\MEMORY.md      -> hermes\memories\MEMORY.md
         memories\USER.md        -> hermes\memories\USER.md
         cron\jobs.json          -> hermes\cron\jobs.json
         plugins\karpathy-guidelines\  -> hermes\plugins\karpathy-guidelines\

    4. run setup-boom.sh in E:\Boom Project — it creates the tier1 skills mirror
       from .agents/skills, then build the indexes
    5. boom-check  (expect core.validator 14/14)

NOT restored here, on purpose:
    skills\        — regenerated from the repo (.agents/skills is authoritative)
    sessions\, cache\, logs\, state\  — machine runtime, not worth carrying
    homeassistant  — re-install from upstream instead of copying a checkout

Rotate the NVIDIA key before or right after restoring: it was exposed in the
git history that was abandoned. See docs/NEW-MACHINE-SETUP.md.
EOF

echo
echo "=== $copied item(s) exported to $OUT ==="
du -sh "$OUT"
echo
echo "This folder contains live credentials. Do not commit it, do not email it,"
echo "do not put it in cloud sync. Move it with a USB drive or a direct file copy."
