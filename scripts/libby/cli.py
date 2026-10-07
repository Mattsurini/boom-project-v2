#!/usr/bin/env python3
"""
Eng CLI - Classification + Formatting for LTD OS
Usage: python scripts/libby/cli.py [--watch] [--once] [--format]
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from classifier import Libby
from formatter import MarkdownFormatter

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Eng - Classifier & Formatter for LTD OS")
    parser.add_argument("--watch", action="store_true", help="Watch for new files continuously")
    parser.add_argument("--once", action="store_true", help="Run once and exit (default)")
    parser.add_argument("--format", action="store_true", help="Format all markdown files after classification")
    parser.add_argument("--project", default="E:/Boom Project", help="Project root path")
    args = parser.parse_args()

    libby = Libby(args.project)
    formatter = MarkdownFormatter(args.project)

    if args.watch:
        print("Eng watching for new files... (Ctrl+C to stop)")
        seen = set()
        while True:
            try:
                files = libby.scan_unclassified_files()
                new_files = [f for f in files if str(f) not in seen]
                if new_files:
                    for f in new_files:
                        print(f"  New: {f.relative_to(libby.project_root)}")
                        frontmatter = libby.classify_file(f)
                        body = libby.read_file(f)
                        libby.write_frontmatter(f, frontmatter, body)
                        libby.update_topic_map(f, frontmatter.get("tags", []))
                        agent = frontmatter["agent"]
                        libby.update_special_index(f, agent, frontmatter)
                    seen.update(str(f) for f in new_files)
                time.sleep(2)
            except KeyboardInterrupt:
                print("\nStopped.")
                break
    else:
        libby.process_all()
    
    if args.format:
        print("\nFormatting all markdown files...")
        formatter.format_all()

if __name__ == "__main__":
    main()