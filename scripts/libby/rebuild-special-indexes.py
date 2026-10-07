#!/usr/bin/env python3
"""
Rebuild INDEX_insights.md and INDEX_transcripts.md from existing files.
"""

import yaml
from pathlib import Path

def main():
    project_root = Path("E:/Boom Project")
    indexes_dir = project_root / "Knowledge" / "indexes"
    
    # Agent → index_type mapping from config
    special_indexes = {
        "CK": "insights",
        "Nut": "insights",
        "Plawan": "transcripts",
    }
    
    indexes = {
        "insights": [],
        "transcripts": [],
    }
    
    output_dir = project_root / "Output"
    
    for agent_folder in output_dir.iterdir():
        if not agent_folder.is_dir():
            continue
        
        agent_name = agent_folder.name
        index_type = special_indexes.get(agent_name)
        
        if not index_type:
            continue
        
        for md_file in agent_folder.glob("*.md"):
            content = md_file.read_text(encoding="utf-8")
            
            if not content.startswith("---"):
                continue
            
            parts = content.split("---", 2)
            if len(parts) < 3:
                continue
            
            try:
                fm = yaml.safe_load(parts[1]) or {}
            except:
                continue
            
            entry = {
                "file": str(md_file.relative_to(project_root)),
                "agent": agent_name,
                "date": fm.get("date", ""),
                "tags": fm.get("tags", []),
            }
            indexes[index_type].append(entry)
    
    # Write indexes
    for index_type, entries in indexes.items():
        if not entries:
            continue
        
        # Sort by date desc
        entries.sort(key=lambda x: x.get("date", ""), reverse=True)
        
        index_path = indexes_dir / f"INDEX_{index_type}.md"
        index_path.write_text(yaml.dump(entries, allow_unicode=True, sort_keys=False), encoding="utf-8")
        print(f"  [OK] INDEX_{index_type}.md ({len(entries)} entries)")

if __name__ == "__main__":
    main()