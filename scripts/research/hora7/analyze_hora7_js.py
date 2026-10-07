import os, re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DIR = BASE_DIR / "assets"
out = []
keywords = ["ฐาน","7ตัว","9ฐาน","ดวง","ลูนาร์","lunar","thai","ปฏิทิน","100ปี","วันจันทร์","ปีนักษัตร","อัตตะ","หินะ","ธนัง","ปิตา","มาตา","โภคา","มัชฌิมา","ตนุ","กดุมพะ","สหัชชะ","พันธุ","ปุตตะ","อริ","ปัตนิ","มรณะ","ศุภะ","กัมมะ","ลาภะ","พยายะ","ทาสา","ทาสี"]
pattern = re.compile("|".join([re.escape(k) for k in keywords]), re.I)

for f in DIR.glob("*.js"):
    if f.name=="js_list.json": continue
    txt = f.read_text(errors="ignore")
    hits = []
    for m in pattern.finditer(txt):
        start = max(0, m.start()-120)
        end = min(len(txt), m.end()+120)
        snippet = txt[start:end].replace("\n"," ")
        hits.append(snippet)
    # also search for thai month names
    thai_months = ["มกราคม","กุมภาพันธ์","มีนาคม","เมษายน","พฤษภาคม","มิถุนายน","กรกฎาคม","สิงหาคม","กันยายน","ตุลาคม","พฤศจิกายน","ธันวาคม"]
    for mname in thai_months:
        if mname in txt:
            hits.append(f"[MONTH]{mname}")
    out.append({"file": f.name, "size": f.stat().st_size, "hits": hits[:50]})

(BASE_DIR / "artifacts").mkdir(parents=True, exist_ok=True)
(BASE_DIR / "artifacts" / "hora7_js_analysis.json").write_text(__import__("json").dumps(out, ensure_ascii=False, indent=2))
print("analyzed", len(out))
