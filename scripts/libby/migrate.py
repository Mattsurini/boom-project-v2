#!/usr/bin/env python3
"""
Migrate old frontmatter to new minimal format
"""

import yaml
from pathlib import Path

def migrate_file(filepath: Path):
    content = filepath.read_text(encoding="utf-8")
    
    if not content.startswith("---"):
        return
    
    parts = content.split("---", 2)
    if len(parts) < 3:
        return
    
    try:
        fm = yaml.safe_load(parts[1]) or {}
    except:
        return
    
    body = parts[2].strip()
    
    # Extract date from filename if not in frontmatter
    import re
    date_match = re.search(r'(\d{4})(\d{2})(\d{2})', filepath.name)
    if date_match:
        date = f"{date_match.group(1)}-{date_match.group(2)}-{date_match.group(3)}"
    else:
        date = fm.get("date", "")
    
    # Build minimal frontmatter
    new_fm = {
        "agent": fm.get("agent", filepath.parent.name),
        "date": date,
        "tags": fm.get("tags", []),
    }
    
    fm_yaml = yaml.dump(new_fm, allow_unicode=True, sort_keys=False)
    new_content = f"---\n{fm_yaml}---\n\n{body}"
    filepath.write_text(new_content, encoding="utf-8")
    print(f"  Migrated: {filepath.name}")

if __name__ == "__main__":
    project_root = Path("E:/Boom Project")
    output_dir = project_root / "Output"
    
    count = 0
    for folder in output_dir.iterdir():
        if not folder.is_dir():
            continue
        for md_file in folder.glob("*.md"):
            migrate_file(md_file)
            count += 1
    
    print(f"Migrated {count} files to minimal frontmatter.")