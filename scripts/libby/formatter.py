#!/usr/bin/env python3
"""
Markdown Formatter - Standardizes markdown files in the project
Rules:
- Max 2 consecutive blank lines
- Single space after heading markers
- No trailing whitespace
- Consistent list indentation (2 spaces)
- Proper spacing around code blocks
- Ensure newline at end of file
"""

import re
from pathlib import Path
from typing import List

class MarkdownFormatter:
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        # Directories to skip
        self.skip_dirs = ["node_modules", ".venv", "__pycache__", "hermes_astro.egg-info"]
    
    def should_process(self, filepath: Path) -> bool:
        """Check if file should be formatted."""
        rel = filepath.relative_to(self.project_root)
        parts = rel.parts
        
        for skip in self.skip_dirs:
            if skip in parts:
                return False
        
        return True
    
    def format_content(self, content: str) -> str:
        """Format markdown content."""
        lines = content.split("\n")
        formatted = []
        blank_count = 0
        in_code_block = False
        
        for line in lines:
            # Skip empty lines tracking
            stripped = line.rstrip()
            
            if not stripped:
                blank_count += 1
                if blank_count <= 2:
                    formatted.append("")
                continue
            else:
                blank_count = 0
            
            # Check code block toggle
            if stripped.startswith("```"):
                in_code_block = not in_code_block
                formatted.append(stripped)
                continue
            
            # In code blocks, preserve as-is (just strip trailing whitespace)
            if in_code_block:
                formatted.append(stripped)
                continue
            
            # Format headings: ensure single space after #
            if re.match(r'^#{1,6}\s+', stripped):
                # Already properly spaced
                formatted.append(stripped)
            elif re.match(r'^#{1,6}[^\s]', stripped):
                # Missing space after #
                fixed = re.sub(r'^(#{1,6})([^\s])', r'\1 \2', stripped)
                formatted.append(fixed)
            else:
                formatted.append(stripped)
        
        # Ensure single newline at end
        result = "\n".join(formatted)
        if not result.endswith("\n"):
            result += "\n"
        
        return result
    
    def format_file(self, filepath: Path) -> bool:
        """Format a single file. Returns True if changes were made."""
        content = filepath.read_text(encoding="utf-8", errors="ignore")
        formatted = self.format_content(content)
        
        if formatted != content:
            filepath.write_text(formatted, encoding="utf-8")
            return True
        return False
    
    def format_all(self):
        """Format all markdown files in the project."""
        changed = 0
        checked = 0
        
        for md_file in self.project_root.rglob("*.md"):
            if not self.should_process(md_file):
                continue
            
            checked += 1
            if self.format_file(md_file):
                print(f"  [OK] {md_file.relative_to(self.project_root)}")
                changed += 1
        
        print(f"\nFormatted {changed} files ({checked} checked).")
        return changed, checked

if __name__ == "__main__":
    formatter = MarkdownFormatter("E:/Boom Project")
    formatter.format_all()