#!/usr/bin/env python3
"""Batch convert PDFs in Books by Authors folder to Markdown files."""

import fitz  # PyMuPDF
import os
import re
from pathlib import Path

BOOKS_DIR = Path(r"E:\Boom Project\Knowledge\Astrology-Database\Books by Authors")

def pdf_to_markdown(pdf_path: Path) -> str:
    doc = fitz.open(str(pdf_path))
    lines = []
    for page in doc:
        text = page.get_text()
        if text.strip():
            lines.append(text.strip())
    doc.close()
    full_text = "\n\n".join(lines)
    # Basic cleanup: collapse multiple blank lines
    full_text = re.sub(r'\n{3,}', '\n\n', full_text)
    # Add a title from filename
    title = pdf_path.stem.replace("_", " ").replace("-", " ")
    md = f"# {title}\n\n{full_text}\n"
    return md

def main():
    pdf_files = sorted(BOOKS_DIR.rglob("*.pdf"))
    if not pdf_files:
        print("No PDF files found in Books by Authors.")
        return
    for pdf in pdf_files:
        md_path = pdf.with_suffix(".md")
        # Skip if .md already exists and is newer
        if md_path.exists() and md_path.stat().st_mtime > pdf.stat().st_mtime:
            print(f"SKIP (up-to-date): {md_path.name}")
            continue
        try:
            md_content = pdf_to_markdown(pdf)
            md_path.write_text(md_content, encoding="utf-8")
            print(f"OK: {md_path.name}")
        except Exception as e:
            print(f"ERR: {pdf.name} -> {e}")
    print(f"\nDone. Processed {len(pdf_files)} PDF(s).")

if __name__ == "__main__":
    main()
