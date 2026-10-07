"""Extract relevant passages from ASTROLOGY-BOOKS-DATABASE for today's transits"""
from pathlib import Path
from pypdf import PdfReader

DB = Path(r"E:\Boom Project\Knowledge\Astrology-Database")

results = []

# File 1: Planets in Signs and Houses
path1 = DB / "#Articles" / "Western Astrology - Planets in Signs and Houses.pdf"
if path1.exists():
    r = PdfReader(str(path1))
    text = "\n".join((p.extract_text() or "") for p in r.pages)
    
    queries = [
        "Moon in the Fourth House",
        "Moon square Saturn",
        "Venus sextile Pluto",
        "Saturn square Jupiter",
        "Moon trine Venus",
        "Venus in the Fifth House",
    ]
    
    results.append("=== Planets in Signs and Houses ===")
    for q in queries:
        idx = text.lower().find(q.lower())
        if idx >= 0:
            excerpt = " ".join(text[max(0, idx-80):idx+500].split())
            results.append(f"\n--- {q} ---\n{excerpt}")
        else:
            results.append(f"\n--- {q} --- NOT FOUND")

# File 2: new-techniques-of-prediction
path2 = DB / "#Articles" / "new-techniques-of-prediction.pdf"
if path2.exists():
    r = PdfReader(str(path2))
    text = "\n".join((p.extract_text() or "") for p in r.pages)
    
    queries2 = [
        "Moon square Saturn",
        "Saturn square Jupiter",
        "Venus sextile Pluto",
        "Gochara",
    ]
    
    results.append("\n=== new-techniques-of-prediction ===")
    for q in queries2:
        idx = text.lower().find(q.lower())
        if idx >= 0:
            excerpt = " ".join(text[max(0, idx-80):idx+500].split())
            results.append(f"\n--- {q} ---\n{excerpt}")
        else:
            results.append(f"\n--- {q} --- NOT FOUND")

print("\n".join(results))
