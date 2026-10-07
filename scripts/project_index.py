#!/usr/bin/env python3
"""
project_index.py — token-economy indexer for Boom Project.

Builds compact machine/human indexes without loading the whole project into chat.
Outputs:
- Knowledge/indexes/project_manifest.json  (machine routing/search metadata)
- Knowledge/indexes/PROJECT_INDEX.md      (human routing map)

Policy: do not rewrite source notes by default. Missing frontmatter is reported, not mass-edited.
"""
from __future__ import annotations
from pathlib import Path
from datetime import datetime, timezone
import json, re, hashlib, os, argparse

ROOT = Path(__file__).resolve().parents[1]
INDEX_DIR = ROOT / "Knowledge" / "indexes"
MANIFEST = INDEX_DIR / "project_manifest.json"
PROJECT_INDEX = INDEX_DIR / "PROJECT_INDEX.md"

SKIP_DIRS = {'.git', '.venv', 'node_modules', '__pycache__', '.cache', 'dist', 'build'}
TEXT_SUFFIXES = {'.md', '.txt', '.json', '.yaml', '.yml', '.csv', '.ics', '.py', '.js', '.ts'}
MD_ONLY = {'.md'}

STAGE_MAP = {
    'NotebookLM': 'NotebookLM / source results', 'Plawan': 'Plawan / blueprint',
    'astrology-assistant': 'Nut / technical', 'Nut': 'Nut / technical',
    'research-specialist': 'CK / psychology', 'CK': 'CK / psychology',
    'audit-researcher': 'Arm / audit', 'Arm': 'Arm / audit',
    'research-critic': 'Nan / critique', 'Nan': 'Nan / critique',
    'project-writer': 'Bella / final', 'Bella': 'Bella / final',
    'source-excerpts': 'Source package', 'transits': 'Transit reports', 'PAC': 'PAC content',
}
TOPIC_HINTS = {
    'transit': ['transit','gochara','saturn transit','planetary transits'],
    'relationship': ['relationship','marriage','soulmate','love','synastry'],
    'financial': ['financial','market','stock','gold','trading'],
    'horary': ['horary','prashna','kp'],
    'bazi': ['bazi','four pillars','八字'],
    'uranian': ['uranian','hamburg','planetary pictures'],
    'pac': ['pac','pick-a-card','content'],
}

def skip(path: Path) -> bool:
    return any(part in SKIP_DIRS for part in path.parts)

def read_head(path: Path, n=12000) -> str:
    try:
        return path.read_text(encoding='utf-8', errors='ignore')[:n]
    except Exception:
        return ''

def parse_frontmatter(text: str):
    if text.startswith('---'):
        m = re.match(r'^---\s*\n(.*?)\n---\s*\n?', text, re.S)
        if m:
            raw = m.group(1)
            fm = {}
            key = None
            for line in raw.splitlines():
                if not line.strip() or line.lstrip().startswith('#'):
                    continue
                if re.match(r'^\w[\w-]*:', line):
                    k,v = line.split(':',1); key=k.strip(); v=v.strip()
                    if v.startswith('[') and v.endswith(']'):
                        fm[key] = [x.strip().strip('"\'') for x in v[1:-1].split(',') if x.strip()]
                    elif v:
                        fm[key] = v.strip('"\'')
                    else:
                        fm[key] = []
                elif key and line.strip().startswith('-'):
                    fm.setdefault(key, [])
                    if isinstance(fm[key], list): fm[key].append(line.strip()[1:].strip())
            return fm, text[m.end():]
    return {}, text

def first_heading(body: str, fallback: str) -> str:
    for line in body.splitlines()[:80]:
        if line.startswith('#'):
            return re.sub(r'^#+\s*','',line).strip()[:120]
    return Path(fallback).stem[:120]

def headings(body: str, limit=6):
    hs=[]
    for line in body.splitlines():
        if line.startswith('#'):
            hs.append(re.sub(r'^#+\s*','',line).strip()[:100])
            if len(hs)>=limit: break
    return hs

def infer_stage(rel: str) -> str:
    parts = Path(rel).parts
    for part in parts:
        if part in STAGE_MAP: return STAGE_MAP[part]
    if parts and parts[0] == 'Knowledge': return 'Knowledge DB'
    if parts and parts[0] == 'context': return 'Context/admin'
    return parts[0] if parts else 'root'

def infer_topics(rel: str, title: str, tags):
    blob = ' '.join([rel, title, ' '.join(tags if isinstance(tags,list) else [])]).lower()
    out=[]
    for topic, keys in TOPIC_HINTS.items():
        if any(k in blob for k in keys): out.append(topic)
    return sorted(set(out)) or ['general']

def short_hash(path: Path):
    try:
        h=hashlib.sha1()
        with path.open('rb') as f: h.update(f.read(65536))
        return h.hexdigest()[:10]
    except Exception:
        return ''

def wiki_path(path: str) -> str:
    """Escape path characters that Obsidian treats as link syntax."""
    return path.replace('#', '%23')

def main():
    parser = argparse.ArgumentParser(description="Boom Project token-economy indexer")
    parser.add_argument("--compact", action="store_true", help="Generate compact PROJECT_INDEX.md (no full note list)")
    parser.add_argument("--json-only", action="store_true", help="Only write manifest JSON, skip PROJECT_INDEX.md")
    parser.add_argument("--limit-recent", type=int, default=25, help="Number of recent artifacts to list")
    args = parser.parse_args()

    build(compact=args.compact, json_only=args.json_only, limit_recent=args.limit_recent)


def build(compact=False, json_only=False, limit_recent=25):
    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    entries=[]; md_count=0; fm_count=0; text_count=0
    by_dir={}; missing_frontmatter=[]
    for p in ROOT.rglob('*'):
        if not p.is_file() or skip(p): continue
        rel = str(p.relative_to(ROOT)).replace('\\','/')
        suffix=p.suffix.lower()
        if suffix in TEXT_SUFFIXES: text_count += 1
        if suffix not in MD_ONLY: continue
        md_count += 1
        text = read_head(p)
        fm, body = parse_frontmatter(text)
        if fm: fm_count += 1
        elif len(missing_frontmatter) < 80: missing_frontmatter.append(rel)
        title = str(fm.get('title') or first_heading(body, rel))
        tags = fm.get('tags', [])
        if isinstance(tags, str): tags=[tags]
        top = rel.split('/')[0]
        by_dir.setdefault(top, {'md':0,'frontmatter':0})
        by_dir[top]['md'] += 1
        if fm: by_dir[top]['frontmatter'] += 1
        stat=p.stat()
        entry={
            'p': rel,
            't': title,
            's': str(fm.get('stage') or fm.get('agent') or infer_stage(rel)),
            'd': str(fm.get('date') or ''),
            'tg': tags[:20],
            'tp': [str(fm.get('topic'))] if fm.get('topic') else infer_topics(rel,title,tags),
            'fm': bool(fm),
            'sz': stat.st_size,
            'mt': int(stat.st_mtime),
            'h': headings(body),
            'hsh': short_hash(p),
        }
        entries.append(entry)
    entries.sort(key=lambda e: (e['mt'], e['p']), reverse=True)
    topics={}
    stages={}
    for e in entries:
        for t in e['tp']: topics.setdefault(t, []).append(e)
        stages.setdefault(e['s'], []).append(e)
    manifest={
        'generated_at': datetime.now(timezone.utc).isoformat(),
        'root': str(ROOT),
        'policy': 'Use this manifest/PROJECT_INDEX before reading raw project files. External web remains required for research answers.',
        'counts': {'markdown': md_count, 'with_frontmatter': fm_count, 'frontmatter_pct': round(fm_count/md_count*100,2) if md_count else 0, 'text_like_files': text_count},
        'by_top_dir': by_dir,
        'missing_frontmatter_sample': missing_frontmatter,
        'entries': entries,
    }
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
    lines=[]
    lines.append('# PROJECT_INDEX — Boom Project Token-Economy Router')
    lines.append('')
    lines.append(f'Generated: `{manifest["generated_at"]}`')
    lines.append(f'Root: `{ROOT}`')
    lines.append('')
    lines.append('## Verdict')
    lines.append(f'- Markdown files: **{md_count}**')
    lines.append(f'- With frontmatter: **{fm_count} / {md_count} ({manifest["counts"]["frontmatter_pct"]}%)**')
    lines.append('- Existing indexing exists, but coverage is partial; use this manifest as the first routing layer before reading raw files.')
    lines.append('')
    lines.append('## How to use this index')
    lines.append('1. Search/read `project_manifest.json` or this `PROJECT_INDEX.md` first.')
    lines.append('2. Use topic/stage/path to choose 1-3 files, then read only line windows.')
    lines.append('3. For research answers, combine local files with external web fetch as source material.')
    lines.append('4. Do not load whole `Knowledge/` or `Output/` into chat.')
    lines.append('')
    lines.append('## Top directories')
    lines.append('| Directory | Markdown | Frontmatter | Coverage |')
    lines.append('|---|---:|---:|---:|')
    for d,c in sorted(by_dir.items(), key=lambda kv: kv[1]['md'], reverse=True):
        pct=round(c['frontmatter']/c['md']*100,1) if c['md'] else 0
        lines.append(f'| `{d}` | {c["md"]} | {c["frontmatter"]} | {pct}% |')
    lines.append('')
    lines.append('## Recent artifacts (last 25)')
    for e in entries[:25]:
        tagstr=', '.join(e['tg'][:6])
        lines.append(f'- [[{wiki_path(e["p"])}|{e["t"]}]] — stage: {e["s"]} | topics: {", ".join(e["tp"])} | fm: {"yes" if e["fm"] else "no"}')
    lines.append('')
    lines.append('## Topic routes')
    for t, arr in sorted(topics.items(), key=lambda kv: len(kv[1]), reverse=True):
        lines.append(f'### {t} ({len(arr)})')
        for e in arr[:12]:
            lines.append(f'- [[{wiki_path(e["p"])}|{e["t"]}]]')
        lines.append('')
    lines.append('## Frontmatter gap sample (first 20)')
    for rel in missing_frontmatter[:20]: lines.append(f'- `{rel}`')
    if not json_only:
        if compact:
            PROJECT_INDEX.write_text(
                f'# PROJECT_INDEX — Boom Project Token-Economy Router\n\n'
                f'Generated: `{manifest["generated_at"]}`\n'
                f'Root: `{ROOT}`\n\n'
                f'## Verdict\n'
                f'- Markdown files: **{md_count}**\n'
                f'- With frontmatter: **{fm_count} / {md_count} ({manifest["counts"]["frontmatter_pct"]}%)**\n\n'
                f'## Top directories\n'
                + '\n'.join(f'| `{d}` | {c["md"]} | {c["frontmatter"]} | {round(c["frontmatter"]/c["md"]*100,1) if c["md"] else 0}% |' 
                           for d,c in sorted(by_dir.items(), key=lambda kv: kv[1]['md'], reverse=True))
                + f'\n\n## Topic routes (top {limit_recent})\n'
                + '\n'.join(f'### {t} ({len(arr)})\n' + '\n'.join(f'- [[{wiki_path(e["p"])}|{e["t"]}]]' for e in arr[:8]) 
                           for t, arr in sorted(topics.items(), key=lambda kv: len(kv[1]), reverse=True)[:10])
                + '\n', encoding='utf-8')
        else:
            PROJECT_INDEX.write_text('\n'.join(lines)+'\n', encoding='utf-8')
    print(json.dumps({'manifest': str(MANIFEST), 'project_index': str(PROJECT_INDEX) if not json_only else None, 'counts': manifest['counts'], 'top_dirs': by_dir}, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()