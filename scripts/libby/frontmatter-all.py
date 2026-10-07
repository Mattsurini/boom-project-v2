#!/usr/bin/env python3
"""
Add minimal YAML frontmatter to ALL project markdown files.
Skips: node_modules, .venv, third-party packages.
Only adds frontmatter if file doesn't already have it.
"""

import yaml
import re
from pathlib import Path
from datetime import datetime

# Skip these directories
SKIP_DIRS = [
    "node_modules",
    ".venv",
    "Scripts",
    "__pycache__",
    "hermes_astro.egg-info",
    "templates",
]

# Project-specific tag mappings
DIR_TAGS = {
    "Knowledge/Astrology-Database": ["astrology", "knowledge-base"],
    "Knowledge/Psychology-Database": ["psychology", "knowledge-base"],
    "Knowledge/Convergence-Database": ["convergence", "knowledge-base"],
    "Knowledge/indexes": ["index", "metadata"],
    "Inbox": ["inbox", "raw"],
    "scripts": ["script", "tool"],
    "config": ["config", "system"],
    "Output": ["output", "agent-work"],
}

def should_skip(path: Path, project_root: Path) -> bool:
    """Check if file should be skipped."""
    rel = path.relative_to(project_root)
    parts = rel.parts
    
    for skip in SKIP_DIRS:
        if skip in parts:
            return True
    
    return False

def get_dir_tags(path: Path, project_root: Path) -> list:
    """Infer tags from directory path."""
    rel = str(path.relative_to(project_root)).replace("\\", "/")
    
    for prefix, tags in sorted(DIR_TAGS.items(), key=lambda x: -len(x[0])):
        if rel.startswith(prefix):
            return list(tags)
    
    return ["project"]

def add_frontmatter(filepath: Path, project_root: Path):
    """Add minimal frontmatter to a single file."""
    content = filepath.read_text(encoding="utf-8", errors="ignore")
    
    # Skip if already has frontmatter
    if content.startswith("---"):
        return False
    
    # Extract date from filename
    date_match = re.search(r'(\d{4})[-]?(\d{2})[-]?(\d{2})', filepath.name)
    if date_match:
        date = f"{date_match.group(1)}-{date_match.group(2)}-{date_match.group(3)}"
    else:
        date = datetime.fromtimestamp(filepath.stat().st_mtime).strftime("%Y-%m-%d")
    
    # Get tags from directory
    tags = get_dir_tags(filepath.parent, project_root)
    
    # Build minimal frontmatter
    fm = {
        "date": date,
        "tags": tags,
        "source": str(filepath.relative_to(project_root)).replace("\\", "/"),
    }
    
    fm_yaml = yaml.dump(fm, allow_unicode=True, sort_keys=False)
    new_content = f"---\n{fm_yaml}---\n\n{content}"
    filepath.write_text(new_content, encoding="utf-8")
    return True

def main():
    project_root = Path("E:/Boom Project")
    count = 0
    skipped = 0
    
    for md_file in project_root.rglob("*.md"):
        if should_skip(md_file, project_root):
            skipped += 1
            continue
        
        if add_frontmatter(md_file, project_root):
            print(f"  + {md_file.relative_to(project_root)}")
            count += 1
    
    print(f"\nDone: {count} files frontmatter added, {skipped} skipped.")

if __name__ == "__main__":
    main()