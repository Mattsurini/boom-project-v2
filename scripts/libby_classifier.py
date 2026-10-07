#!/usr/bin/env python3
"""
libby_classifier.py - The Libby Classifier Agent for LTD OS
Reads raw input files, analyzes content, adds YAML frontmatter,
saves to correct Output/<Agent>/ folder, updates index files.

Usage: python libby_classifier.py <input_file> [--agent <agent_name>]
"""

import os
import sys
import yaml
import re
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from collections import defaultdict

PROJECT_ROOT = Path("E:/Boom Project")
CONFIG_PATH = PROJECT_ROOT / "config" / "agents.yaml"
OUTPUT_BASE = PROJECT_ROOT / "Output"
INDEXES_DIR = PROJECT_ROOT / "Knowledge" / "indexes"

class LibbyClassifier:
    def __init__(self):
        self.config = self._load_config()
        self.agents = self.config["agents"]
        self.topic_keywords = self.config.get("topic_keywords", {})
        self.flow_stages = self.config.get("flow_stages", [])
    
    def _load_config(self) -> Dict:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    
    def detect_topics(self, content: str) -> List[str]:
        """Detect topics from content using keyword matching."""
        content_lower = content.lower()
        detected = []
        
        for topic, keywords in self.topic_keywords.items():
            for kw in keywords:
                if kw.lower() in content_lower:
                    detected.append(topic)
                    break
        
        return detected if detected else ["general"]
    
    def detect_agent(self, content: str, detected_topics: List[str], preferred_agent: Optional[str] = None) -> str:
        """Determine which agent should process this content."""
        content_lower = content.lower()
        
        # If user specified an agent, validate and use it
        if preferred_agent and preferred_agent in self.agents:
            if preferred_agent != "Eng":
                return preferred_agent
        
        # Content-based detection
        # Check for agent-specific keywords
        agent_signals = {
            "Plawan": ["blueprint", "idea", "notebooklm", "question", "brainstorm", "concept", "proposal"],
            "CK": ["research", "psychological", "extraction", "study", "analysis", "findings"],
            "Sandee": ["deepseek", "gpt-5.6", "machine learning", "machine-learning", "artificial intelligence", "artificial-intelligence", "llm", "rag", "fine-tuning", "benchmark", "dataset", "mlops"],
            "Nut": ["chart", "horoscope", "dasha", "nakshatra", "planet", "house", "technical-extraction", "astrology"],
            "Nan": ["critique", "critic", "review", "flaw", "gap", "weakness", "evaluation"],
            "Arm": ["audit", "verification", "fact-check", "validate", "source", "evidence"],
            "Bella": ["convergence", "synthesis", "report", "final", "integration", "unified"],
        }
        
        scores = defaultdict(int)
        
        for agent, signals in agent_signals.items():
            for signal in signals:
                if signal.lower() in content_lower:
                    scores[agent] += 1
        
        # Topic-based fallback
        if "astrology" in detected_topics and scores["Nut"] == 0:
            scores["Nut"] += 1
        if "ml-ai" in detected_topics and scores["Sandee"] == 0:
            scores["Sandee"] += 1
        if "psychology" in detected_topics and scores["CK"] == 0:
            scores["CK"] += 1
        if "relationships" in detected_topics and scores["Plawan"] == 0:
            scores["Plawan"] += 1
        
        if scores:
            best = max(scores, key=lambda k: scores[k])
            return best
        
        # Ultimate fallback: Plawan (idea generator)
        return "Plawan"
    
    def generate_tags(self, content: str, agent: str, topics: List[str]) -> List[str]:
        """Generate tags for the content."""
        tags = []
        
        # Add default tags for agent
        default_tags = self.agents.get(agent, {}).get("default_tags", [])
        tags.extend(default_tags)
        
        # Add detected topics
        for topic in topics:
            if topic not in tags:
                tags.append(topic)
        
        # Add date tag
        today = datetime.now().strftime("%Y-%m-%d")
        tags.append(f"date:{today}")
        
        # Deduplicate while preserving order
        seen = set()
        unique = []
        for t in tags:
            if t not in seen:
                seen.add(t)
                unique.append(t)
        
        return unique
    
    def add_frontmatter(self, content: str, agent: str, tags: List[str], title: str) -> str:
        """Add YAML frontmatter to content."""
        today = datetime.now().strftime("%Y-%m-%d")
        
        frontmatter = {
            "date": today,
            "agent": agent,
            "tags": tags,
            "title": title,
            "source": "Libby classifier",
        }
        
        fm_str = yaml.dump(frontmatter, default_flow_style=False, allow_unicode=True, sort_keys=False)
        
        return f"---\n{fm_str}---\n\n{content.strip()}\n"
    
    def save_classified(self, content: str, agent: str, title: str, topics: Optional[List[str]] = None) -> Path:
        """Save classified content to a topic-first output directory."""
        topics = topics or []
        if "ml-ai" in topics:
            output_dir = OUTPUT_BASE / "ML-AI" / agent
        elif "astrology" in topics:
            output_dir = OUTPUT_BASE / "Astrology" / agent
        else:
            configured = self.agents.get(agent, {}).get("output_dir")
            output_dir = PROJECT_ROOT / configured if configured else OUTPUT_BASE / agent
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Sanitize title for filename
        safe_title = re.sub(r'[^\w\-_.\s]', '', title).strip()
        safe_title = re.sub(r'\s+', '-', safe_title)
        
        today = datetime.now().strftime("%Y%m%d")
        filename = f"{today}-{safe_title}.md"
        
        # Avoid collisions
        counter = 1
        filepath = output_dir / filename
        while filepath.exists():
            filepath = output_dir / f"{today}-{safe_title}-{counter}.md"
            counter += 1
        
        filepath.write_text(content, encoding="utf-8")
        return filepath
    
    def update_index(self, agent: str, tags: List[str], filepath: Path):
        """Update the appropriate manual index file."""
        index_type = self.agents.get(agent, {}).get("index_type")
        if not index_type:
            return  # No index to update for this agent
        
        index_file = INDEXES_DIR / f"INDEX_{index_type}.md"
        
        today = datetime.now().strftime("%Y-%m-%d")
        rel_path = str(filepath.relative_to(PROJECT_ROOT))
        
        entry = f"""- file: {rel_path}
  agent: {agent}
  date: '{today}'
  tags:
{chr(10).join('  - ' + t for t in tags)}
"""
        
        if index_file.exists():
            with open(index_file, "a", encoding="utf-8") as f:
                f.write(entry + "\n")
        else:
            with open(index_file, "w", encoding="utf-8") as f:
                f.write(f"# INDEX_{index_type}.md\n\n{entry}\n")
        
        print(f"  [OK] Updated INDEX_{index_type}.md")
    
    def classify(self, input_path: Path, preferred_agent: Optional[str] = None) -> Path:
        """Main classification pipeline."""
        print(f"Classifying: {input_path}")
        
        content = input_path.read_text(encoding="utf-8")
        
        # Detect topics
        topics = self.detect_topics(content)
        print(f"  Topics: {', '.join(topics)}")
        
        # Detect agent
        agent = self.detect_agent(content, topics, preferred_agent)
        print(f"  Agent: {agent}")
        
        # Generate title from first heading or first line
        title = self._extract_title(content)
        print(f"  Title: {title}")
        
        # Generate tags
        tags = self.generate_tags(content, agent, topics)
        print(f"  Tags: {', '.join(tags)}")
        
        # Add frontmatter
        classified = self.add_frontmatter(content, agent, tags, title)
        
        # Save
        output_path = self.save_classified(classified, agent, title, topics)
        print(f"  Saved: {output_path}")
        
        # Update index
        self.update_index(agent, tags, output_path)
        
        return output_path
    
    def _extract_title(self, content: str) -> str:
        """Extract title from first H1 or first non-empty line."""
        for line in content.split('\n'):
            stripped = line.strip()
            if not stripped:
                continue
            if stripped.startswith('# '):
                return stripped[2:].strip()
            if stripped.startswith('#'):
                return stripped.lstrip('#').strip()
            # Return first non-empty line if no heading
            return stripped[:80]
        return "untitled"

def main():
    parser = argparse.ArgumentParser(description="Libby Classifier - Classify and tag raw input files")
    parser.add_argument("input_file", help="Path to raw input markdown file")
    parser.add_argument("--agent", "-a", help="Force specific agent (Plawan, CK, Nut, Nan, Arm, Bella)")
    
    args = parser.parse_args()
    
    input_path = Path(args.input_file)
    if not input_path.exists():
        print(f"ERROR: File not found: {input_path}")
        sys.exit(1)
    
    libby = LibbyClassifier()
    output_path = libby.classify(input_path, preferred_agent=args.agent)
    
    print(f"\nDone. Output: {output_path}")

if __name__ == "__main__":
    main()
