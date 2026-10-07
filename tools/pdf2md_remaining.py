#!/usr/bin/env python3
"""Batch convert PDFs in Classics books, Good books, Nadi jyotish to Markdown."""

import fitz  # PyMuPDF
import os
import re
import sys
from pathlib import Path

FOLDERS = [
    Path(r"E:\Boom Project\Knowledge\Astrology-Database\Classics books"),
    Path(r"E:\Boom Project\Knowledge\Astrology-Database\Good books"),
    Path(r"E:\Boom Project\Knowledge\Astrology-Database\Nadi jyotish"),
]

def pdf_to_markdown(pdf_path: Path) -> str:
    doc = fitz.open(str(pdf_path))
    lines = []
    for page in doc:
        text = page.get_text()
        if text.strip():
            lines.append(text.strip())
    doc.close()
    full_text = "\n\n".join(lines)
    full_text = re.sub(r'\n{3,}', '\n\n', full_text)
    title = pdf_path.stem.replace("_", " ").replace("-", " ")
    md = f"# {title}\n\n{full_text}\n"
    return md

def main():
    for folder in FOLDERS:
        if not folder.exists():
            print(f"Folder not found: {folder}")
            continue
        pdf_files = sorted(folder.glob("*.pdf"))
        if not pdf_files:
            print(f"No PDFs in: {folder.name}")
            continue
        for pdf in pdf_files:
            md_path = pdf.with_suffix(".md")
            if md_path.exists() and md_path.stat().st_mtime > pdf.stat().st_mtime:
                print(f"SKIP: {md_path.name}")
                continue
            try:
                md_content = pdf_to_markdown(pdf)
                md_path.write_text(md_content, encoding="utf-8")
                print(f"OK: {folder.name}/{md_path.name}")
            except Exception as e:
                print(f"ERR: {folder.name}/{pdf.name} -> {e}")

if __name__ == "__main__":
    main()
