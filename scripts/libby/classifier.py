#!/usr/bin/env python3
"""
Libby Classifier v2 - Incremental, config-driven, minimal frontmatter
- Only processes files WITHOUT frontmatter
- Reads agent config from config/agents.yaml
- Minimal frontmatter: agent, date, tags
- Append-only indexes (no full rewrite)
"""

import yaml
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

class Libby:
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.config = self._load_config()
        self.output_dir = self.project_root / "Output"
        self.indexes_dir = self.project_root / "Knowledge" / "indexes"
        self.topic_map_path = self.indexes_dir / "TOPIC_MAP.md"
        
        # Build agent lookup from config. output_aliases lets Hermes-native
        # canonical agent folders; NotebookLM is a separate source-results lane.
        self.agents = {name: data for name, data in self.config["agents"].items()}
        self.folder_to_agent = {}
        for name, data in self.config["agents"].items():
            for output_path in [data.get("output_dir"), *data.get("output_aliases", [])]:
                if output_path:
                    self.folder_to_agent[Path(output_path).name] = name
        self.agent_folders = list(self.folder_to_agent.keys())
        self.topic_keywords = {k: v for k, v in self.config["topic_keywords"].items()}
    
    def _load_config(self) -> Dict:
        """Load agent configuration from config/agents.yaml."""
        config_path = self.project_root / "config" / "agents.yaml"
        with open(config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    
    def scan_unclassified_files(self) -> List[Path]:
        """Only scan files WITHOUT frontmatter (incremental)."""
        files = []
        for md_file in self.output_dir.rglob("*.md"):
            content = md_file.read_text(encoding="utf-8", errors="ignore")
            if not content.startswith("---"):
                files.append(md_file)
        return files
    
    def read_file(self, filepath: Path) -> str:
        """Read file content."""
        return filepath.read_text(encoding="utf-8")
    
    def write_frontmatter(self, filepath: Path, frontmatter: Dict, body: str):
        """Write minimal frontmatter + body to file."""
        fm_yaml = yaml.dump(frontmatter, allow_unicode=True, sort_keys=False)
        new_content = f"---\n{fm_yaml}---\n\n{body}"
        filepath.write_text(new_content, encoding="utf-8")
    
    def extract_tags(self, content: str, agent_name: str, filepath: Path) -> List[str]:
        """Extract tags based on agent config + content."""
        tags = []
        content_lower = content.lower()
        
        # Agent default tags from config
        agent_config = self.agents.get(agent_name, {})
        tags.extend(agent_config.get("default_tags", []))
        
        # Content-based topic tags
        for topic, keywords in self.topic_keywords.items():
            if any(kw in content_lower for kw in keywords):
                tags.append(topic)
        
        # Date tag from filename
        date_match = re.search(r'(\d{4})(\d{2})(\d{2})', filepath.name)
        if date_match:
            tags.append(f"date:{date_match.group(1)}-{date_match.group(2)}-{date_match.group(3)}")
        
        # Deduplicate while preserving order
        seen = set()
        unique_tags = []
        for t in tags:
            if t not in seen:
                seen.add(t)
                unique_tags.append(t)
        return unique_tags
    
    def classify_file(self, filepath: Path) -> Dict:
        """Classify a single file and resolve agent from Output/<Agent>/... first."""
        content = self.read_file(filepath)
        try:
            rel_parts = filepath.relative_to(self.output_dir).parts
        except ValueError:
            rel_parts = filepath.parts

        # Domain folders (Astrology/ML-AI) are nested under the agent. Resolve
        # the first configured agent component instead of using only the parent
        # folder, which would misclassify every Output/<Agent>/ML-AI file.
        agent = next((part for part in rel_parts if part in self.agents), None)
        if agent is None:
            agent = self.folder_to_agent.get(filepath.parent.name, filepath.parent.name)
        
        # Generate tags
        tags = self.extract_tags(content, agent, filepath)
        
        # Extract date from filename or use today
        date_match = re.search(r'(\d{4})(\d{2})(\d{2})', filepath.name)
        if date_match:
            date = f"{date_match.group(1)}-{date_match.group(2)}-{date_match.group(3)}"
        else:
            date = datetime.now().strftime("%Y-%m-%d")
        
        # Minimal frontmatter - 3 fields only
        return {
            "agent": agent,
            "date": date,
            "tags": tags,
        }
    
    def append_to_index(self, index_path: Path, entry: Dict):
        """Append entry to index file (no full rewrite)."""
        self.indexes_dir.mkdir(parents=True, exist_ok=True)
        
        # Load existing entries
        entries = []
        if index_path.exists():
            try:
                content = index_path.read_text(encoding="utf-8")
                entries = yaml.safe_load(content) or []
            except:
                entries = []
        
        # Remove duplicate if exists
        rel_path = entry.get("file", "")
        entries = [e for e in entries if e.get("file") != rel_path]
        entries.append(entry)
        
        # Write back (still full write for YAML list, but we process fewer files)
        index_path.write_text(yaml.dump(entries, allow_unicode=True, sort_keys=False), encoding="utf-8")
    
    def update_topic_map(self, file_path: Path, tags: List[str]):
        """Update TOPIC_MAP.md - append entries."""
        self.indexes_dir.mkdir(parents=True, exist_ok=True)
        
        # Load existing
        topic_map = {}
        if self.topic_map_path.exists():
            content = self.topic_map_path.read_text(encoding="utf-8")
            current_topic = None
            for line in content.split("\n"):
                if line.startswith("## "):
                    current_topic = line[3:].strip()
                    topic_map[current_topic] = []
                elif line.startswith("- ") and current_topic:
                    topic_map[current_topic].append(line[2:].strip())
        
        # Add new entries
        rel_path = str(file_path.relative_to(self.project_root))
        for tag in tags:
            if tag in self.topic_keywords or tag.startswith("date:"):
                if tag not in topic_map:
                    topic_map[tag] = []
                if rel_path not in topic_map[tag]:
                    topic_map[tag].append(rel_path)
        
        # Write
        lines = ["# TOPIC_MAP.md", "", "Auto-generated by Libby.", ""]
        for topic, files in sorted(topic_map.items()):
            lines.append(f"## {topic}")
            for f in sorted(files):
                lines.append(f"- {f}")
            lines.append("")
        
        self.topic_map_path.write_text("\n".join(lines), encoding="utf-8")
    
    def update_special_index(self, file_path: Path, agent_name: str, frontmatter: Dict):
        """Update insight/transcript indexes based on agent config."""
        agent_config = self.agents.get(agent_name, {})
        index_type = agent_config.get("index_type")
        
        if not index_type:
            return
        
        index_file = f"INDEX_{index_type}.md"
        index_path = self.indexes_dir / index_file
        
        entry = {
            "file": str(file_path.relative_to(self.project_root)),
            "agent": agent_name,
            "date": frontmatter.get("date", ""),
            "tags": frontmatter.get("tags", []),
        }
        
        self.append_to_index(index_path, entry)
    
    def process_all(self):
        """Process only unclassified files (incremental)."""
        files = self.scan_unclassified_files()
        
        if not files:
            print("Libby: No new files to classify.")
            return
        
        print(f"Libby: Classifying {len(files)} new files...")
        
        for filepath in files:
            print(f"  + {filepath.relative_to(self.project_root)}")
            
            # Classify
            frontmatter = self.classify_file(filepath)
            body = self.read_file(filepath)
            
            # Write minimal frontmatter
            self.write_frontmatter(filepath, frontmatter, body)
            
            # Update indexes
            agent = frontmatter["agent"]
            self.update_topic_map(filepath, frontmatter.get("tags", []))
            self.update_special_index(filepath, agent, frontmatter)
        
        print(f"Libby: Done. {len(files)} files classified.")

if __name__ == "__main__":
    libby = Libby("E:/Boom Project")
    libby.process_all()