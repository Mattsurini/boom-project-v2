# Boom Project Specific Setup Notes

## Router Skill
- Location: `.claude/skills/boom-auto-workflow-router/SKILL.md`
- Must be copied to `skills/boom-auto-workflow-router/` for Hermes to load it
- Mandatory per `TURBOZ.md` and `.hermes.md`

## Declared Hermes Skills (Missing)
From `.hermes.md:97-103`:
- `astro-agent-{plawan,nut,ck,arm,nan,bella}` — pipeline agents
- `astro-pipeline` — full pipeline orchestrator
- `morning-transit-briefing` — daily transit summary (cron: 07:00 ICT)
- `transit-pac-pipeline` — generate PAC content from transits

These need to be created or installed.

## Model Configuration
- Current config: `nvidia/nemotron-3-ultra-550b-a55b` (NOT on NVIDIA NIM)
- Available on NVIDIA NIM: `nvidia/nemotron-3-super-120b-a12b`, `nvidia/nemotron-3-ultra-550b-a55b` (check via API)
- Working model found: `nvidia/nemotron-3-super-120b-a12b`
- Fix: `hermes config set model.default nvidia/nemotron-3-super-120b-a12b`

## Python Venv Fix Applied
- `.venv/pyvenv.cfg` updated:
  - `home = E:\Boom Project\.venv`
  - `executable = E:\Boom Project\.venv\Scripts\python.exe`
  - `command = E:\Boom Project\.venv\Scripts\python.exe -m venv E:\Boom Project\.venv`
- Version updated to 3.11.16

## Eng/Libby Pipeline (Run After Output Changes)
```bash
python scripts/libby/cli.py --once
python scripts/build-output-index.py
python scripts/project_index.py
python scripts/memory_db.py sync-manifest
python scripts/memory_db.py status
```

## Non-Canonical Output Folders to Consolidate
- `Output/Astrology/`
- `Output/Marketing/`
- `Output/Client-Readings/`
- Run: `python scripts/libby/organize-output.py`

## Cron Jobs to Create
- `morning-transit-briefing`: 07:00 ICT daily
- `transit-pac-pipeline`: on transit changes

## NotebookLM Integration (Added 2026-09-06)

### Installation
```bash
.venv\Scripts\pip install "notebooklm-py[browser]"
.venv\Scripts\playwright install chromium
```

### Authentication
```bash
# Interactive login (saves cookies to ~/.notebooklm/profiles/default/storage_state.json)
.venv\Scripts\notebooklm.exe login

# Verify auth
.venv\Scripts\notebooklm.exe auth check --test --json
```

### Skill Installation (for Claude Code / agent integration)
```bash
.venv\Scripts\notebooklm.exe skill install
```

Installs to:
- `~/.claude/skills/notebooklm/SKILL.md`
- `~/.agents/skills/notebooklm/SKILL.md`

### Existing Notebooks (as of setup)
| Notebook ID | Title |
|-------------|-------|
| `ce891443-b9fe-404a-8a92-...` | Principles of Uranian Astrology and the 90-Degree Dial |
| `7b2d3148-1888-40c3-b9ec-...` | Celestial Keys: Thai Astrology Foundations and Wealth Prediction |
| `5a5d4f74-cf09-4046-b021-...` | (unnamed) |

### Custom Runner Script
`scripts/notebooklm-run.js` — Node.js wrapper for batch research:
- Takes JSON spec with questions
- Runs sequentially against a notebook
- Saves results to `Output/NotebookLM/` with timestamped filenames
- Tracks runs in `notebooklm-run-log.json` to avoid duplicates

Usage:
```bash
node scripts/notebooklm-run.js path/to/questions.json [--notebook <id>]
```

### Output Directory
All generated NotebookLM research results go to:
```
Output/NotebookLM/
```

### Python API
```python
import asyncio
from notebooklm import NotebookLMClient

async def main():
    async with NotebookLMClient.from_storage() as client:
        nb = await client.notebooks.create("Research")
        await client.sources.add_url(nb.id, "https://example.com", wait=True)
        result = await client.chat.ask(nb.id, "Summarize this")
        print(result.answer)

asyncio.run(main())
```

### Use Cases for This Project
1. **Astrology Research** — Load classical texts, generate summaries, create study guides
2. **Content Generation** — Generate podcasts, slide decks, infographics from research
3. **Knowledge Distillation** — Run deep research, condense into skills for zero-token reuse
4. **Cross-Session Memory** — Maintain a "Master Brain" notebook with session notes
5. **Grounded Coding Agent** — Expose project docs/RFCs via MCP for citation-grounded answers

### NotebookLM Auth Issue (Resolved)
- `notebooklm.exe login` / `hermes portal login` hangs on curses/TTY in Git Bash
- Workaround: Run in cmd.exe or Windows Terminal
- Needed for pipeline Stage 2b (NotebookLM query)
- **Status**: Auth completed successfully for turboztarot@gmail.com (3 notebooks found)

## Verification Commands
```bash
# Full health check
hermes doctor

# Test model
hermes chat -q "test"

# Check indexes
python scripts/libby/find.py "test"

# Check registry
python scripts/memory_db.py status

# List skills
hermes skills list

# List cron
hermes cron list
```