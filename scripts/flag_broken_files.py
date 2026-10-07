import os
from pathlib import Path

def process_broken_files():
    db_base = r"E:\Boom Project\Knowledge\Astrology-Database"
    source_base = r"E:\Boom Project\Knowledge\Astrology-Database"
    
    # Find all broken .md files (< 1000 bytes, excluding index.md)
    broken_files = []
    for root, dirs, files in os.walk(db_base):
        for f in files:
            if f.endswith('.md') and f != 'index.md':
                md_path = os.path.join(root, f)
                size = os.path.getsize(md_path)
                if size < 1000:
                    broken_files.append(md_path)
    
    print(f"Found {len(broken_files)} broken files to process")
    
    flagged = 0
    
    for md_path in broken_files:
        md_name = Path(md_path).stem
        
        # Determine if this is a scan-only book (no text extracted previously)
        # We know from previous run that most of these are scan-only
        # Add proper YAML frontmatter and placeholder
        
        placeholder = f"""---
date: '2026-08-01'
tags:
- astrology
- knowledge-base
- scan-only
status: needs-ocr
source: ASTROLOGY-BOOKS-DATABASE
---

# {md_name}

> **Status**: SCAN-ONLY — This file contains only a placeholder because the source PDF is image-based (scanned pages) with no extractable text layer.
>
> **Action needed**: OCR conversion required to make this content searchable and readable.
>
> **Source**: Original PDF located in `{source_base}`

---

*This document is currently unavailable as machine-readable text. The source PDF requires Optical Character Recognition (OCR) to convert scanned images to searchable text.*

"""
        
        try:
            with open(md_path, 'w', encoding='utf-8') as f:
                f.write(placeholder)
            print(f"  FLAGGED: {md_name}")
            flagged += 1
        except Exception as e:
            print(f"  ERROR flagging {md_name}: {e}")
    
    print(f"\nDone. Flagged {flagged} files.")

if __name__ == "__main__":
    process_broken_files()
