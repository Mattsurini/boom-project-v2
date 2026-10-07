#!/usr/bin/env bash
# Boom Project setup — rebuilds a NEW machine into a working Boom + Hermes box.
# GitHub backs up the CODE; this script rebuilds the RUNTIME around it.
# See the MANUAL block at the bottom for what git can never carry (API keys,
# login, the ~1GB PDF corpus, vault/cron/memories).

set -euo pipefail

# Configuration
BOOM_PROJECT_DIR="${BOOM_PROJECT_DIR:-E:/Boom Project}"
# The real Hermes home is %LOCALAPPDATA%\hermes — NOT the project dir.
# LOCALAPPDATA arrives as a Windows path (C:\Users\...\AppData\Local); bash is
# happier with forward slashes, so normalize the separators before appending.
_hermes_base="${LOCALAPPDATA:-$HOME/AppData/Local}"
HERMES_HOME="$(printf '%s' "$_hermes_base" | tr '\\' '/')/hermes"
VENV_DIR="$BOOM_PROJECT_DIR/.venv"
PY="$VENV_DIR/Scripts/python.exe"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in a Git Bash/MSYS environment (common on Windows)
if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
    IS_WINDOWS_SHELL=true
else
    IS_WINDOWS_SHELL=false
fi

# Ensure we're in the Boom Project directory
if [[ ! -d "$BOOM_PROJECT_DIR" ]]; then
    log_error "Boom Project directory not found: $BOOM_PROJECT_DIR"
    exit 1
fi

cd "$BOOM_PROJECT_DIR"
log_info "Project: $BOOM_PROJECT_DIR"
log_info "Hermes : $HERMES_HOME"
export HERMES_HOME

# ---- 1. python venv (3.11 — the pyswisseph/kerykeion wheels are 3.11-built) ----
log_info "1/7 python venv"
if [[ ! -d "$VENV_DIR" ]]; then
  py -3.11 -m venv "$VENV_DIR" || python -m venv "$VENV_DIR"
fi
"$PY" -m pip install --upgrade pip -q

# ---- 2. pinned dependencies (regenerate with: pip freeze > requirements.txt) ----
log_info "2/7 pinned dependencies"
"$PY" -m pip install -r requirements.txt -q

# ---- 3. npm packages ----
log_info "3/7 npm packages"
npm install

# ---- 4. upstream repos: git-ignored on purpose, re-cloned instead of vendored ----
log_info "4/7 upstream repos (re-clone, never vendor)"
clone_if_missing() {
  if [[ -d "$1/.git" ]]; then
    log_info "  [skip] $1"
  else
    git clone --depth 1 "$2" "$1" || log_warn "clone failed: $1"
  fi
}
clone_if_missing stellium             https://github.com/katelouie/stellium.git
clone_if_missing power-design         https://github.com/ItsssssJack/power-design
clone_if_missing frontend-slides      https://github.com/zarazhangrui/frontend-slides
clone_if_missing Deep-Research-skills https://github.com/Weizhena/Deep-Research-skills

# ---- 5. secrets ----
log_info "5/7 secrets"
if [[ ! -f .env ]]; then
  cp .env.example .env
  log_warn "created .env from .env.example — FILL IN THE VALUES"
fi
if [[ ! -f "$HERMES_HOME/.env" ]]; then
  log_warn "$HERMES_HOME/.env MISSING — copy it from the old machine."
  log_warn "Hermes reads provider keys there; without it providers return 401."
  log_warn "If you exported it, the file is at hermes-state/.env — copy it:"
  log_warn "    cp hermes-state/.env \"$HERMES_HOME/.env\""
fi

# ---- 6. skills mirror: .agents/skills (tier0) -> %HERMES_HOME%/skills (tier1) ----
log_info "6/7 skills mirror (tier0 -> tier1)"
"$PY" - <<'PYEOF'
import os, shutil
from pathlib import Path

t0 = Path(r"E:\Boom Project\.agents\skills")
t1 = Path(os.environ["LOCALAPPDATA"]) / "hermes" / "skills"


def norm(p: Path) -> bytes:
    # CRLF vs LF is not drift (core/validator.py:_norm_nl). Compare content, not
    # byte layout, or this rewrites files on every run and never converges.
    return p.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")


if not t1.is_dir():
    shutil.copytree(t0, t1)
    print(f"  created tier1 mirror -> {t1}")
else:
    added = refreshed = 0
    for p in t0.rglob("SKILL.md"):
        dst = t1 / p.relative_to(t0)
        if not dst.exists():
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(p, dst); added += 1
        elif norm(p) != norm(dst):
            shutil.copy2(p, dst); refreshed += 1
    print(f"  +{added} added, ~{refreshed} refreshed from tier0")
print("  tier0 (.agents/skills) stays authoritative")
PYEOF

# ---- 7. indexes + registry ----
log_info "7/7 indexes + registry"
for step in "scripts/libby/cli.py --once" "scripts/build-output-index.py" \
            "scripts/project_index.py" "scripts/memory_db.py sync-manifest"; do
  if "$PY" $step >/dev/null 2>&1; then log_info "  ok: $step"; else log_warn "  skipped: $step"; fi
done

# Create convenient aliases
log_info "Setting up convenient aliases..."
cat >> ~/.bashrc << 'EOF'

# ---- Boom Project aliases ----
export BOOM="E:/Boom Project"
boom-update='cd "$BOOM" && python scripts/libby/cli.py --once && python scripts/build-output-index.py && python scripts/project_index.py && python scripts/memory_db.py sync-manifest && python scripts/memory_db.py status'
boom-verify='cd "$BOOM" && python scripts/memory_db.py status'
boom-classify='cd "$BOOM" && python scripts/libby/cli.py --once'
boom-check='cd "$BOOM" && python -m core.validator && python -m core.tests'
boom-transits='cd "$BOOM" && python scripts/transit_timeline_v3.py'
boom-natal='cd "$BOOM" && python scripts/natal_chart.py'
boom-tarot='cd "$BOOM" && python scripts/tarot_engine.py'
boom-eclipses='cd "$BOOM" && python scripts/eclipses.py'
EOF

# For Zsh users
if [[ -f ~/.zshrc ]]; then
    cat >> ~/.zshrc << 'EOF'

# Boom Project aliases
export BOOM="E:/Boom Project"
boom-update='cd "$BOOM" && python scripts/libby/cli.py --once && python scripts/build-output-index.py && python scripts/project_index.py && python scripts/memory_db.py sync-manifest && python scripts/memory_db.py status'
boom-verify='cd "$BOOM" && python scripts/memory_db.py status'
boom-classify='cd "$BOOM" && python scripts/libby/cli.py --once'
boom-check='cd "$BOOM" && python -m core.validator && python -m core.tests'
boom-transits='cd "$BOOM" && python scripts/transit_timeline_v3.py'
boom-natal='cd "$BOOM" && python scripts/natal_chart.py'
boom-tarot='cd "$BOOM" && python scripts/tarot_engine.py'
boom-eclipses='cd "$BOOM" && python scripts/eclipses.py'
EOF
fi

log_info ""
log_info "Boom Project setup complete!"
log_info ""
log_info "MANUAL steps git cannot carry to a new machine:"
log_info "  [ ] API keys : copy %LOCALAPPDATA%\\\\hermes\\\\.env from the old machine"
log_info "                (.gitignore blocks .env* — never commit the filled file)"
log_info "  [ ] Login    : run Hermes once and log in (auth.json is per-machine)"
log_info "  [ ] PDFs     : copy the ~1GB corpus from the old machine —"
log_info "                Knowledge/Astrology-Database/ (217 PDFs) and Tarot Knowledge/"
log_info "                (git-ignored on purpose; GitHub backs up code, not the library)"
log_info "  [ ] Memories : copy memories/MEMORY.md + memories/USER.md"
log_info "  [ ] Cron     : copy cron/jobs.json"
log_info "  [ ] Vault    : browser logins are encrypted + machine-bound, re-save them"
log_info ""
log_info "Verify the rebuild:  source ~/.bashrc && boom-check   (expect 14/14)"