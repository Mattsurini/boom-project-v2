# Hermes Project Setup Verification Checklist Template

Copy this template and fill in for each project setup.

```markdown
# Project Setup Verification: {{PROJECT_NAME}}

Date: {{DATE}}
Hermes Version: {{VERSION}}

## Pre-Setup
- [ ] Project directory exists
- [ ] .env file exists (or template created)
- [ ] config.yaml exists
- [ ] .venv/ directory exists
- [ ] setup script exists (setup-boom.sh or equivalent)

## Hermes Doctor
- [ ] `hermes doctor` runs without critical errors
- [ ] Config version current (v40+)
- [ ] Python environment OK
- [ ] Required packages installed
- [ ] API connectivity: provider shows ✓

## Model & Provider
- [ ] model.provider set correctly
- [ ] model.default set to available model
- [ ] API key in .env (not config.yaml)
- [ ] `hermes chat -q "test"` works

## Skills
- [ ] Project-specific skills in skills/
- [ ] Router skill installed (if mandatory)
- [ ] Declared skills from .hermes.md all present
- [ ] `hermes skills list` shows expected skills

## Indexing & Registry
- [ ] `python scripts/libby/find.py "test"` works
- [ ] `python scripts/memory_db.py status` shows counts
- [ ] PROJECT_INDEX.md date is recent
- [ ] boom_project_registry.sqlite3 has entries

## Cron Jobs
- [ ] `hermes cron list` shows expected jobs
- [ ] Morning briefing cron (if applicable)
- [ ] Pipeline cron (if applicable)

## Output Structure
- [ ] Canonical folders present (Plawan, Nut, CK, Arm, Nan, Bella, PAC)
- [ ] No non-canonical alias folders (or will consolidate)
- [ ] libby/organize-output.py runs cleanly

## NotebookLM (if applicable)
- [ ] notebooklm.exe in venv
- [ ] Auth works (login, list, use)
- [ ] Pipeline Stage 2b can execute

## Issues Found
{{ISSUES}}

## Next Actions
{{ACTIONS}}
```