from __future__ import annotations

import csv
import hashlib
import json
import re
import subprocess
import zipfile
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from xml.etree import ElementTree

ROOT = Path(r"E:\Boom Project")
KNOWLEDGE = ROOT / "Knowledge"
INDEXES = KNOWLEDGE / "indexes"

TEXT_EXTS = {".md", ".txt", ".html", ".htm", ".cht", ".jhd", ".yaml", ".yml", ".json", ".xml", ".csv"}
PDF_EXTS = {".pdf"}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def extract_text(path: Path) -> tuple[str, str]:
    ext = path.suffix.lower()
    if ext in TEXT_EXTS:
        raw = path.read_bytes()
        for enc in ("utf-8", "utf-16", "cp874", "latin-1"):
            try:
                return raw.decode(enc, errors="ignore"), "text-extracted"
            except Exception:
                pass
    if ext == ".doc":
        try:
            result = subprocess.run(["antiword", str(path)], capture_output=True, timeout=30)
            raw = result.stdout or b""
            text = raw.decode("utf-8", errors="ignore")
            if not text.strip():
                text = raw.decode("cp874", errors="ignore")
            return text, "doc-extracted" if result.returncode == 0 else "doc-metadata-only"
        except Exception:
            return "", "doc-metadata-only"
    if ext == ".pptx":
        try:
            with zipfile.ZipFile(path) as z:
                text = []
                for name in z.namelist():
                    if name.startswith("ppt/slides/slide") and name.endswith(".xml"):
                        root = ElementTree.fromstring(z.read(name))
                        text.extend(x.text or "" for x in root.iter() if x.tag.endswith("}t"))
                return "\n".join(text), "pptx-extracted"
        except Exception:
            return "", "pptx-metadata-only"
    if ext in {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".webp"}:
        return "", "media-metadata-only"
    return "", "binary-metadata-only"


def classify(rel: Path, text: str) -> tuple[str, str, list[str]]:
    parts = rel.parts
    top = parts[0] if parts else ""
    name = rel.name.lower()
    text = text or ""
    sample = (name + " " + text[:12000]).lower()
    if top == "_archive":
        return "Archive/Duplicates", "Archived duplicate or redirect", ["archive"]
    if name == ".ds_store":
        return "System/Metadata", "Filesystem metadata file", ["system", "metadata"]
    if "Birth-detail-collections" in parts:
        return "Astrology/Chart-Collections", "Birth-detail or natal chart collection", ["astrology", "charts", "birth-data"]
    if top == "indexes":
        return "System/Indexes", "Generated project routing/index files", ["system", "index"]
    if top == "Chinese-Astrology":
        if "BaZi" in parts:
            return "Chinese-Astrology/BaZi", "BaZi folder route", ["chinese-astrology", "bazi"]
        if "ZiWei" in parts:
            return "Chinese-Astrology/ZiWei", "Zi Wei folder route", ["chinese-astrology", "ziwei"]
        if "HuangLi" in parts:
            return "Chinese-Astrology/HuangLi", "HuangLi folder route", ["chinese-astrology", "huangli"]
        if "zi wei" in sample or "ziwei" in sample or "紫微" in sample:
            return "Chinese-Astrology/ZiWei", "Zi Wei Dou Shu terms", ["chinese-astrology", "ziwei"]
        if "huang" in sample or "almanac" in sample or "黄历" in sample:
            return "Chinese-Astrology/HuangLi", "Chinese almanac terms", ["chinese-astrology", "huangli"]
        if "bazi" in sample or "ba zi" in sample:
            return "Chinese-Astrology/BaZi", "Chinese astrology / Four Pillars terms", ["chinese-astrology", "bazi"]
        return "Chinese-Astrology/General", "Chinese astrology root material", ["chinese-astrology"]
    if top == "Psychology-Database":
        return "Psychology/Applications", "Psychology database source or application note", ["psychology"]
    if top == "Convergence-Database":
        if "ml-ai" in rel.as_posix().lower() or any(x in sample for x in ["deepseek", "machine learning", "llm", "gpt-5.6"]):
            return "ML-AI/Insights", "ML/AI convergence insight", ["ml-ai", "insight"]
        return "Astrology/Convergence", "Cross-agent astrology convergence insight", ["astrology", "convergence"]
    if top == "Astrology-Database":
        folder_routes = {
            "Articles": ("Astrology/Articles", "Physical Articles category folder", ["astrology", "article"]),
            "Chart-Collections": ("Astrology/Chart-Collections", "Physical chart collection folder", ["astrology", "charts", "birth-data"]),
            "Financial": ("Astrology/Financial", "Physical financial astrology folder", ["astrology", "financial"]),
            "Jaimini": ("Astrology/Jaimini", "Physical Jaimini folder", ["astrology", "jaimini"]),
            "KP-Prashna": ("Astrology/KP-Prashna", "Physical KP/Prashna folder", ["astrology", "kp", "prashna"]),
            "Nadi": ("Astrology/Nadi", "Physical Nadi folder", ["astrology", "nadi"]),
            "Natal-Rectification": ("Astrology/Natal-Rectification", "Physical natal/rectification folder", ["astrology", "natal"]),
            "Uranian": ("Astrology/Uranian", "Physical Uranian folder", ["astrology", "uranian"]),
            "Western": ("Astrology/Western", "Physical Western astrology folder", ["astrology", "western"]),
            "Vedic-Classics": ("Astrology/Vedic-Classics", "Physical Vedic classics folder", ["astrology", "vedic"]),
        }
        for folder, route in folder_routes.items():
            if folder in parts:
                return route
        if "#Articles" in parts or "article" in name:
            return "Astrology/Articles", "Article or web-derived astrology source", ["astrology", "article"]
        rules = [
            ("Astrology/Uranian", ["uranian", "witte", "planetary picture", "hamburg"]),
            ("Astrology/Jaimini", ["jaimini", "chara dasha", "karaka"]),
            ("Astrology/Nadi", ["nadi", "naadi", "bhrigu", "sukra nadi"]),
            ("Astrology/KP-Prashna", ["krishnamurti", "kp ", "horary", "prashna", "prasna"]),
            ("Astrology/Financial", ["financial astrology", "finance", "career", "profession", "market"]),
            ("Astrology/Natal-Rectification", ["birth time", "rectification", "natal", "horoscope"]),
            ("Astrology/Western", ["western astrology", "zodiac signs", "signs and houses"]),
        ]
        for category, needles in rules:
            if any(n in sample for n in needles):
                return category, f"Matched source/name terms: {', '.join(needles[:3])}", ["astrology", category.split("/", 1)[1].lower()]
        return "Astrology/Vedic-Classics", "Astrology database source; no narrower primary signal", ["astrology", "vedic"]
    return "Review/Uncategorized", "No established Knowledge domain match", ["review"]


def main() -> None:
    INDEXES.mkdir(parents=True, exist_ok=True)
    rows = []
    for path in sorted(p for p in KNOWLEDGE.rglob("*") if p.is_file()):
        rel = path.relative_to(KNOWLEDGE)
        ext = path.suffix.lower()
        digest = sha256(path)
        if ext in PDF_EXTS:
            rows.append({"path": rel.as_posix(), "extension": ext, "size": path.stat().st_size, "sha256": digest, "read_status": "SKIPPED_PDF", "category": "Astrology/PDF-Unread", "reason": "Explicitly excluded by user"})
            continue
        text, read_status = extract_text(path)
        category, reason, tags = classify(rel, text)
        rows.append({"path": rel.as_posix(), "extension": ext or "[none]", "size": path.stat().st_size, "sha256": digest, "read_status": read_status, "category": category, "reason": reason, "tags": ";".join(tags), "title_signal": re.sub(r"\s+", " ", text[:180]).strip()})
    csv_path = INDEXES / "KNOWLEDGE_CATEGORY_MAP.csv"
    fields = ["path", "extension", "size", "sha256", "read_status", "category", "reason", "tags", "title_signal"]
    with csv_path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    json_path = INDEXES / "KNOWLEDGE_CATEGORY_MAP.json"
    json_path.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    counts = Counter(r["category"] for r in rows if r["read_status"] != "SKIPPED_PDF")
    statuses = Counter(r["read_status"] for r in rows if r["read_status"] != "SKIPPED_PDF")
    md = ["# Knowledge Category Map", "", f"Generated: {datetime.now().astimezone().isoformat()}", "", "Scope: every file under `Knowledge/`; PDF files are inventoried by path/size/hash only and their contents were not read.", "", "## Counts (non-PDF)"]
    for category, count in sorted(counts.items()):
        md.append(f"- `{category}`: {count}")
    md += ["", "## Read status (non-PDF)"]
    for status, count in sorted(statuses.items()):
        md.append(f"- `{status}`: {count}")
    md += ["", "## Routing rule", "- This map is the authoritative primary-category route for the physically organized Knowledge tree.", "- Non-PDF source files are physically placed under their category folders; legacy hubs/indexes remain as navigation anchors.", "- Use the CSV/JSON for exact per-file routing, hash verification, and future moves.", "- `Astrology/PDF-Unread` is intentionally excluded from content classification and PDF files remain in place.", ""]
    (INDEXES / "KNOWLEDGE_CATEGORY_MAP.md").write_text("\n".join(md), encoding="utf-8")
    print(json.dumps({"total": len(rows), "nonpdf": sum(r["read_status"] != "SKIPPED_PDF" for r in rows), "pdf_skipped": sum(r["read_status"] == "SKIPPED_PDF" for r in rows), "categories": dict(sorted(counts.items())), "read_status": dict(sorted(statuses.items())), "csv": str(csv_path), "json": str(json_path), "markdown": str(INDEXES / 'KNOWLEDGE_CATEGORY_MAP.md')}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
