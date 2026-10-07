# Scan, Classify, Manifest

## Harness name lists
Files: `claude.md`, `codex.md`, `gemini.md`, `opencode.json`, `opencode.md`, `windsurf.md`, `.clinerules`, `cursorrules`, `web-researcher.toml`
Dirs: `.claude`, `.codex`, `.opencode`, `.gemini`, `.windsurf`, `.cursor`, `.cline`, `.aider`, `.claude-plugin`, `agents-codex`
Candidates (classify by hand): `agents/` (harness agent defs vs content), `agents.md`
Skip: `.git`, `node_modules`, `dist`, `build`, `__pycache__`, `.venv`, `.quarantine`, `sessions`

## Tree scan
```python
from pathlib import Path
import sys
root = Path(sys.argv[1] if len(sys.argv) > 1 else '.')
HARNESS_FILES = {'claude.md','codex.md','gemini.md','opencode.json','opencode.md',
                 'windsurf.md','.clinerules','cursorrules','web-researcher.toml'}
HARNESS_DIRS = {'.claude','.codex','.opencode','.gemini','.windsurf','.cursor',
                '.cline','.aider','.claude-plugin','agents-codex','agents'}
SKIP = {'.git','node_modules','dist','build','__pycache__','.venv','.quarantine','sessions'}
hits = []
for x in sorted(root.rglob('*')):
    if x.is_dir():
        continue
    parts = [p.lower() for p in x.relative_to(root).parts]
    if any(p in SKIP for p in parts):
        continue
    if x.name.lower() in HARNESS_FILES or any(p in HARNESS_DIRS for p in parts):
        hits.append(f"{x.relative_to(root)} ({x.stat().st_size}b)")
print(f"TOTAL: {len(hits)}")
print('\n'.join(hits))
```
Run it writing output to a scratch file (large scans truncate inline stdout), then read the file back.

## Reference scan
Needles: `.claude/`, `.opencode/`, `.codex/`, `opencode.json`, `~/.claude`, `~/.codex`, `~/.config/opencode`, `agents-codex`
Scan: root *.md docs, scripts/, config files, Knowledge/indexes, the profile skills dir.
For each hit decide: patch (project doc) / rebuild (generated index) / leave (generic documentation).

## Classification
- **Harness-only → quarantine:** settings, plugin manifests, harness-DSL workflow scripts, other harnesses' agent defs, other-harness skill variants.
- **Reusable → migrate first:** agent role definitions, pipeline specs, command templates, search strategies.
- **Same-name content → keep:** design templates, docs, files that merely share a name.

## Manifest format (BATCH-N-MANIFEST.json)
```json
{
  "batch": 3,
  "date": "ISO-8601",
  "scope": "what this batch covered",
  "quarantine_root": ".quarantine/<task>-<date>",
  "recovery": "how files come back (git, physical location)",
  "migrated_before_quarantine": ["source -> destination"],
  "kept": ["path (reason)"],
  "moved": [{"path": "rel/path", "reason": "why"}]
}
```

## Merge-safe move
```python
def move(src: Path, dest: Path):
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        for c in src.iterdir():
            move(c, dest / c.name)
        src.rmdir()
    else:
        shutil.move(str(src), str(dest))
```
