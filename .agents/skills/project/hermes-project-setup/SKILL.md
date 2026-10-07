---
name: hermes-project-setup
description: "Use when setting up a Hermes project workspace."
category: project
---

# Hermes Project Setup & Troubleshooting

This skill captures the standard setup sequence and common failure patterns when initializing a Hermes project workspace (like the Boom Project).

## Standard Setup Sequence

```bash
# 1. Verify project directory
cd /path/to/project

# 2. Run project setup script (if exists)
./setup-boom.sh

# 3. Run Hermes doctor
hermes doctor

# 4. Fix config version if needed
hermes doctor --fix

# 5. Set provider and model
hermes config set model.provider <provider>
hermes config set model.default <model-id>

# 6. Add API keys to .env (never config.yaml)
echo 'NVIDIA_API_KEY=your-key' >> .env
# or use hermes setup (interactive)

# 7. Verify model works
hermes chat -q "test"
```

## Common Failure Patterns & Fixes

### 1. Python Venv Path Mismatch

**Symptom**: `No Python at '"C:\\Users\\...\\python.exe"'` when running venv python

**Cause**: `.venv/pyvenv.cfg` points to original Python home, not the venv itself

**Fix**:
```bash
# Read current config
cat .venv/pyvenv.cfg

# Update to point to local venv
# home = /path/to/project/.venv
# executable = /path/to/project/.venv/Scripts/python.exe
# command = /path/to/project/.venv/Scripts/python.exe -m venv /path/to/project/.venv
```

**Prevention**: Recreate venv in place: `python -m venv .venv` from project root

### 2. Model Not Found (HTTP 404)

**Symptom**: `NotFoundError [HTTP 404]` from provider endpoint

**Cause**: Configured model ID doesn't exist on that provider's API

**Debug**:
```bash
# List available models for provider
curl -H "Authorization: Bearer $API_KEY" https://api.provider.com/v1/models
```

**Fix**: Update config to an available model:
```bash
hermes config set model.default <available-model-id>
```

### 3. API Key Not Recognized

**Symptom**: `No API key found for provider 'X'` despite key in `.env`

**Causes & Fixes**:
- Key format: `PROVIDER_API_KEY=value` (uppercase, underscores)
- Provider expects different env var name — check provider reference
- Key in config.yaml instead of .env — move to .env
- Config provider mismatch — verify `model.provider` matches key

### 4. Missing Declared Skills

**Symptom**: Project docs reference skills that don't exist in `skills/`

**Fix**:
```bash
# List declared skills in .hermes.md
# Install each from .claude/skills/ or create via skill_manage
cp -r .claude/skills/skill-name skills/
```

### 5. Router Skill Not Loading

**Symptom**: Mandatory startup protocol references `boom-auto-workflow-router` but skill not found

**Cause**: Skill exists in `.claude/skills/` (OpenCode format) but not in Hermes `skills/`

**Fix**: Copy or recreate in Hermes skills directory:
```bash
cp -r .claude/skills/boom-auto-workflow-router skills/
# OR
skill_manage create from the SKILL.md content
```

### 6. Config Version Outdated

**Symptom**: `Config version outdated (v0 → v40)`

**Fix**: `hermes doctor --fix` migrates automatically

### 7. Cron Jobs Not Running

**Symptom**: Declared cron skills (morning-transit-briefing, transit-pac-pipeline) not executing

**Cause**: No cron jobs created in `cron/` directory

**Fix**:
```bash
hermes cron create --name morning-transit --schedule "0 7 * * *" --command "python scripts/transit_timeline_v2.py"
# or use cronjob_manage tool
```

### 8. Stale Project Manifest

**Symptom**: `PROJECT_INDEX.md` date is old; new Output files not indexed

**Fix**: Run full Eng/Libby pipeline:
```bash
python scripts/libby/cli.py --once
python scripts/build-output-index.py
python scripts/project_index.py
python scripts/memory_db.py sync-manifest
python scripts/memory_db.py status
```

### 9. Non-Canonical Output Folders

**Symptom**: Output folders like `Astrology/`, `Marketing/`, `Client-Readings/` exist alongside canonical ones

**Fix**: `python scripts/libby/organize-output.py`

### 10. NotebookLM CLI Auth Hangs

**Symptom**: `notebooklm.exe login` or `hermes portal login` hangs on curses/TTY

**Workaround**: Run in cmd.exe or use winpty:
```bash
winpty hermes portal login
# or run notebooklm.exe directly in Windows Terminal
```

## Verification Checklist

After setup, verify:
- [ ] `hermes doctor` shows no critical errors
- [ ] `hermes chat -q "test"` returns a response
- [ ] `python scripts/libby/find.py "test query"` works
- [ ] `python scripts/memory_db.py status` shows registry counts
- [ ] Cron jobs listed in `hermes cron list` or `cronjob_manage action=list`
- [ ] Skills listed in `hermes skills list` include project-specific ones

## References

- [Hermes docs: setup](https://hermes-agent.nousresearch.com/docs/user-guide/setup)
- [Hermes docs: providers](https://hermes-agent.nousresearch.com/docs/user-guide/providers)
- [Hermes docs: skills](https://hermes-agent.nousresearch.com/docs/user-guide/skills)
- [Hermes docs: cron](https://hermes-agent.nousresearch.com/docs/user-guide/cron)

## Integration with Boom Project

For the Boom Project specifically:
- Router skill: `.claude/skills/boom-auto-workflow-router/SKILL.md` → copy to `skills/`
- Declared Hermes skills: `astro-agent-*`, `astro-pipeline`, `morning-transit-briefing`, `transit-pac-pipeline`
- Model: Use `nvidia/nemotron-3-super-120b-a12b` (available on NVIDIA NIM)
- Venv: Fixed `.venv/pyvenv.cfg` to point to `E:\Boom Project\.venv`
- Eng pipeline: Run weekly or after major Output changes