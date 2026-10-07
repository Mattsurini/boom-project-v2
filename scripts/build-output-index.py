#!/usr/bin/env python3
"""
build-output-index.py - The Deterministic Index Builder for LTD OS
Scans all output folders, reads frontmatter created by Libby,
rebuilds INDEX_output.md from scratch, connects research flows,
creates coverage reports.
Run when /done is triggered.
"""

import os
import yaml
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from collections import defaultdict

class IndexBuilder:
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.output_dir = self.project_root / "Output"
        self.knowledge_dir = self.project_root / "Knowledge"
        self.indexes_dir = self.knowledge_dir / "indexes"
        
        # Load config
        self.config = self._load_config()
        self.agents = self.config["agents"]
        self.folder_to_agent = {}
        for name, data in self.agents.items():
            if name == "Eng":
                continue
            for output_path in [data.get("output_dir"), *data.get("output_aliases", [])]:
                if output_path:
                    self.folder_to_agent[Path(output_path).name] = name
        self.agent_folders = [name for name in self.agents.keys() if name != "Eng"]
        self.flow_stages = self.config.get("flow_stages", self.agent_folders)
    
    def _load_config(self) -> Dict:
        """Load agent configuration from config/agents.yaml."""
        config_path = self.project_root / "config" / "agents.yaml"
        with open(config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    
    def scan_directory(self, dir_path: Path) -> List[Dict]:
        """Scan a directory for markdown files with frontmatter."""
        entries = []
        
        for md_file in dir_path.rglob("*.md"):
            content = md_file.read_text(encoding="utf-8")
            frontmatter, body = self.parse_frontmatter(content)
            
            if not frontmatter:
                continue
            
            entry = {
                "file": str(md_file.relative_to(self.project_root)).replace(chr(92), "/"),
                "agent": frontmatter.get("agent", md_file.parent.name),
                "date": str(frontmatter.get("date", "")),
                "tags": frontmatter.get("tags", []),
                "topic": frontmatter.get("topic") or self.extract_main_topic(frontmatter.get("tags", [])),
            }
            entries.append(entry)
        
        return entries
    
    def scan_all_outputs(self) -> List[Dict]:
        """Scan every markdown artifact under Output, including topic-first folders."""
        entries = []
        for md_file in self.output_dir.rglob("*.md"):
            rel_file = str(md_file.relative_to(self.project_root)).replace(chr(92), "/")
            content = md_file.read_text(encoding="utf-8")
            frontmatter, body = self.parse_frontmatter(content)
            if not frontmatter:
                continue
            parent_agent = md_file.parent.name
            entries.append({
                "file": rel_file,
                "agent": frontmatter.get("agent", parent_agent),
                "date": str(frontmatter.get("date", "")),
                "tags": frontmatter.get("tags", []),
                "topic": frontmatter.get("topic") or self.extract_main_topic(frontmatter.get("tags", [])),
            })
        return entries
    
    def scan_all_knowledge(self) -> List[Dict]:
        """Scan Knowledge/ directory for all markdown files."""
        return self.scan_directory(self.knowledge_dir)
    
    def parse_frontmatter(self, content: str) -> tuple[Dict, str]:
        """Parse YAML frontmatter."""
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                try:
                    parsed = yaml.safe_load(parts[1]) or {}
                    # Guard: a literal divider like "--- Page 1 ---" parses to a
                    # scalar (str), which is not frontmatter. Only treat dicts
                    # as frontmatter; anything else fall through to default.
                    return (parsed if isinstance(parsed, dict) else {}), parts[2].strip()
                except yaml.YAMLError:
                    pass
        return {}, content
    
    def extract_main_topic(self, tags: List[str]) -> str:
        """Extract main research topic from tags."""
        # Collect all default tags from config
        default_tags = set()
        for agent_name, agent_config in self.agents.items():
            default_tags.update(agent_config.get("default_tags", []))
        # Also add topic keywords as defaults
        default_tags.update(self.config.get("topic_keywords", {}).keys())
        
        topic_tags = [t for t in tags if not t.startswith("date:") and t not in default_tags]
        return topic_tags[0] if topic_tags else "general"
    
    def group_by_topic(self, entries: List[Dict]) -> Dict[str, List[Dict]]:
        """Group entries by research topic."""
        grouped = defaultdict(list)
        for entry in entries:
            grouped[entry["topic"]].append(entry)
        return grouped
    
    def build_flow_chains(self, grouped: Dict[str, List[Dict]]) -> Dict[str, List[Dict]]:
        """Build research flow chains: idea -> Q&A -> research -> reviews -> script"""
        flows = {}
        
        for topic, entries in grouped.items():
            # Sort by flow stage order
            stage_order = {stage: i for i, stage in enumerate(self.flow_stages)}
            entries.sort(key=lambda e: stage_order.get(e["agent"], 999))
            
            # Build chain
            chain = []
            for entry in entries:
                chain.append({
                    "stage": entry["agent"],
                    "file": entry["file"],
                    "title": Path(entry["file"]).stem,
                    "date": entry["date"],
                    "tags": entry["tags"],
                })
            
            if chain:
                flows[topic] = chain
        
        return flows
    
    def generate_index_output(self, entries: List[Dict]) -> str:
        """Generate INDEX_output.md content."""
        lines = [
            "# INDEX_output.md",
            "",
            f"Auto-generated by build-output-index.py on {datetime.now().isoformat()}",
            f"Total files: {len(entries)}",
            "",
            "---",
            ""
        ]
        
        # Group by agent
        by_agent = defaultdict(list)
        for entry in entries:
            by_agent[entry["agent"]].append(entry)
        
        for agent in self.agent_folders:
            if agent not in by_agent:
                continue
            lines.append(f"## {agent}")
            lines.append("")
            for entry in sorted(by_agent[agent], key=lambda x: x["date"], reverse=True):
                tags_str = ", ".join(entry["tags"]) if entry["tags"] else "—"
                file_stem = Path(entry['file']).stem
                lines.append(f"- [[{entry['file']}|{file_stem}]]")
                lines.append(f"  - Date: {entry['date']} | Tags: {tags_str}")
            lines.append("")
        
        return "\n".join(lines)
    
    def generate_flow_index(self, flows: Dict[str, List[Dict]]) -> str:
        """Generate research flow index showing idea → Q&A → research → reviews → script"""
        lines = [
            "# RESEARCH_FLOWS.md",
            "",
            f"Auto-generated on {datetime.now().isoformat()}",
            "",
            "Research pipelines showing the full chain from idea to final output.",
            "",
            "---",
            ""
        ]
        
        for topic, chain in sorted(flows.items()):
            lines.append(f"## {topic}")
            lines.append("")
            
            for i, step in enumerate(chain):
                arrow = " → " if i < len(chain) - 1 else ""
                lines.append(f"{i+1}. **{step['stage']}**: [[{step['file']}|{step['title']}]] ({step['date']}){arrow}")
            
            lines.append("")
            lines.append("---")
            lines.append("")
        
        return "\n".join(lines)
    
    def generate_coverage_report(self, entries: List[Dict], flows: Dict[str, List[Dict]]) -> str:
        """Generate coverage report showing what's missing in each flow."""
        lines = [
            "# COVERAGE_REPORT.md",
            "",
            f"Auto-generated on {datetime.now().isoformat()}",
            "",
            "Analysis of research pipeline completeness per topic.",
            "",
            "---",
            ""
        ]
        
        expected_stages = set(self.flow_stages)
        
        for topic, chain in sorted(flows.items()):
            present_stages = {step["stage"] for step in chain}
            missing_stages = expected_stages - present_stages
            
            lines.append(f"## {topic}")
            lines.append("")
            lines.append(f"**Completed stages ({len(present_stages)}/{len(expected_stages)}):**")
            for stage in self.flow_stages:
                if stage in present_stages:
                    step = next(s for s in chain if s["stage"] == stage)
                    lines.append(f"  - ✅ {stage}: {step['title']}")
                else:
                    lines.append(f"  - ❌ {stage}: MISSING")
            
            if missing_stages:
                lines.append("")
                lines.append("**Gaps to fill:**")
                for stage in sorted(missing_stages):
                    lines.append(f"  - Run {stage} for this topic")
            
            lines.append("")
            lines.append("---")
            lines.append("")
        
        # Topics with no flow at all
        all_topics = set()
        for entry in entries:
            all_topics.add(entry["topic"])
        
        topics_with_flows = set(flows.keys())
        orphan_topics = all_topics - topics_with_flows
        
        if orphan_topics:
            lines.append("## Orphan Files (no complete flow)")
            lines.append("")
            for topic in sorted(orphan_topics):
                topic_entries = [e for e in entries if e["topic"] == topic]
                lines.append(f"### {topic}")
                for entry in topic_entries:
                    lines.append(f"  - {entry['agent']}: {Path(entry['file']).stem} ({entry['date']})")
                lines.append("")
        
        return "\n".join(lines)
    
    def generate_master_index(self, entries: List[Dict]) -> str:
        """Generate MASTER_INDEX.md - flat chronological list of ALL files."""
        lines = [
            "# MASTER_INDEX.md",
            "",
            f"Auto-generated on {datetime.now().isoformat()}",
            f"Total files: {len(entries)}",
            "",
            "Flat chronological list of every file in the system.",
            "",
            "---",
            ""
        ]
        
        # Sort by date desc
        sorted_entries = sorted(entries, key=lambda x: x.get("date", ""), reverse=True)
        
        for entry in sorted_entries:
            tags_str = ", ".join(entry["tags"]) if entry["tags"] else "—"
            lines.append(f"- **{Path(entry['file']).stem}** | `{entry['agent']}` | {entry['date']} | Tags: {tags_str}")
        
        return "\n".join(lines)
    
    def generate_topic_index(self, entries: List[Dict]) -> str:
        """Generate TOPIC_INDEX.md - cross-reference by topic."""
        lines = [
            "# TOPIC_INDEX.md",
            "",
            f"Auto-generated on {datetime.now().isoformat()}",
            "",
            "Cross-reference of all files by research topic.",
            "",
            "---",
            ""
        ]
        
        grouped = self.group_by_topic(entries)
        
        for topic, topic_entries in sorted(grouped.items()):
            lines.append(f"## {topic} ({len(topic_entries)} files)")
            lines.append("")
            
            by_agent = defaultdict(list)
            for entry in topic_entries:
                by_agent[entry["agent"]].append(entry)
            
            for agent in self.agent_folders:
                if agent in by_agent:
                    lines.append(f"### {agent}")
                    for entry in sorted(by_agent[agent], key=lambda x: x["date"], reverse=True):
                        lines.append(f"- {Path(entry['file']).stem} (`{entry['file']}`) — {entry['date']}")
                    lines.append("")
        
        return "\n".join(lines)
    
    def build_all(self):
        """Run the full index building pipeline."""
        print("Scanning output folders...")
        output_entries = self.scan_all_outputs()
        print(f"Found {len(output_entries)} output files")
        
        print("Scanning knowledge base...")
        knowledge_entries = self.scan_all_knowledge()
        print(f"Found {len(knowledge_entries)} knowledge files")
        
        all_entries = output_entries + knowledge_entries
        
        if not output_entries:
            print("No output files with frontmatter found. Run Libby first.")
            return
        
        print("Grouping by topic...")
        grouped = self.group_by_topic(output_entries)
        
        print("Building research flows...")
        flows = self.build_flow_chains(grouped)
        
        print("Generating indexes...")
        self.indexes_dir.mkdir(parents=True, exist_ok=True)
        
        # INDEX_output.md - only output files
        index_output = self.generate_index_output(output_entries)
        (self.indexes_dir / "INDEX_output.md").write_text(index_output, encoding="utf-8")
        print("  [OK] INDEX_output.md")
        
        # RESEARCH_FLOWS.md - only output files
        flow_index = self.generate_flow_index(flows)
        (self.indexes_dir / "RESEARCH_FLOWS.md").write_text(flow_index, encoding="utf-8")
        print("  [OK] RESEARCH_FLOWS.md")
        
        # COVERAGE_REPORT.md - only output files
        coverage = self.generate_coverage_report(output_entries, flows)
        (self.indexes_dir / "COVERAGE_REPORT.md").write_text(coverage, encoding="utf-8")
        print("  [OK] COVERAGE_REPORT.md")
        
        # TOPIC_INDEX.md - only output files
        topic_index = self.generate_topic_index(output_entries)
        (self.indexes_dir / "TOPIC_INDEX.md").write_text(topic_index, encoding="utf-8")
        print("  [OK] TOPIC_INDEX.md")
        
        # MASTER_INDEX.md - output + knowledge files
        master_index = self.generate_master_index(all_entries)
        (self.indexes_dir / "MASTER_INDEX.md").write_text(master_index, encoding="utf-8")
        print("  [OK] MASTER_INDEX.md")
        
        print(f"\nAll indexes rebuilt successfully.")
        print(f"  Output files: {len(output_entries)}")
        print(f"  Knowledge files: {len(knowledge_entries)}")
        print(f"  Total tracked: {len(all_entries)}")
        print(f"Output directory: {self.indexes_dir}")

if __name__ == "__main__":
    builder = IndexBuilder("E:/Boom Project")
    builder.build_all()