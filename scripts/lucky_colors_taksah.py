"""สีเสื้อมงคลตามตำราทักษา — scrape via crawl4ai from mu.loveiseveryday.com/lucky-colors

Usage (Boom .venv python):
  .venv/Scripts/python scripts/lucky_colors_taksah.py                  # วันนี้
  .venv/Scripts/python scripts/lucky_colors_taksah.py 06.10.2026       # วันระบุ (DD.MM.YYYY)
  .venv/Scripts/python scripts/lucky_colors_taksah.py --day พฤหัสบดี    # วันระบุชื่อ
  .venv/Scripts/python scripts/lucky_colors_taksah.py --all            # ตารางสรุป 7 วัน
  .venv/Scripts/python scripts/lucky_colors_taksah.py --birth ศุกร์     # เน้นแถววันเกิด
  .venv/Scripts/python scripts/lucky_colors_taksah.py --json           # JSON ครบ (stdout สะอาด)
  .venv/Scripts/python scripts/lucky_colors_taksah.py --no-cache       # บังคับ crawl ใหม่

Cache: Output/Sources/Lucky-Colors/lucky_colors_taksah.json (fresh < 24h)

หมายเหตุ:
  - dict ทุกตัวใช้ key ภาษาอังกฤษ เพื่อกันปัญหาอักขระไทยเพี้ยน
  - แยกตารางด้วยโครงสร้าง (จำนวนคอลัมน์/ลำดับ) ไม่พึ่งการเทียบหัวตารางภาษาไทย
  - ข้อความ log ไป stderr เพื่อให้ --json ส่ง JSON ล้วนทาง stdout
"""
import argparse
import asyncio
import json
import re
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

from bs4 import BeautifulSoup
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig

BASE = "https://mu.loveiseveryday.com/lucky-colors"
ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / "Output" / "Sources" / "Lucky-Colors" / "lucky_colors_taksah.json"
CACHE_TTL = timedelta(hours=24)

# slug -> (ชื่อไทยวัน, ดาวประจำวัน)
DAYS = {
    "sunday":    ("วันอาทิตย์",   "อาทิตย์"),
    "monday":    ("วันจันทร์",     "จันทร์"),
    "tuesday":   ("วันอังคาร",    "อังคาร"),
    "wednesday": ("วันพุธ",       "พุธ"),
    "thursday":  ("วันพฤหัสบดี", "พฤหัสบดี"),
    "friday":    ("วันศุกร์",      "ศุกร์"),
    "saturday":  ("วันเสาร์",      "เสาร์"),
}
# python weekday() Mon=0..Sun=6 -> slug
WEEKDAY_SLUG = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
# ชื่อวันเกิดที่รับ (--birth / --day)
ALIASES = {
    "อาทิตย์": "sunday", "จันทร": "monday", "จันทร์": "monday", "อังคาร": "tuesday",
    "พุธ": "wednesday", "พฤหัสบดี": "thursday", "พฤหัส": "thursday",
    "ศุกร์": "friday", "เสาร์": "saturday",
    "sunday": "sunday", "monday": "monday", "tuesday": "tuesday", "wednesday": "wednesday",
    "thursday": "thursday", "friday": "friday", "saturday": "saturday",
}


def log(msg):
    """ข้อความสถานะ -> stderr (ให้ stdout เหลือแต่ผลลัพธ์/JSON)"""
    print(msg, file=sys.stderr)


def split_colors(cell: str):
    return [c.strip() for c in re.split(r"[/·]", cell) if c.strip()]


def _cells(tr):
    return [c.get_text(" ", strip=True) for c in tr.find_all(["th", "td"])]


def parse_tables(soup: BeautifulSoup):
    """คืน (summary, positions, birth_rows, meanings)

    แยกตารางด้วยโครงสร้าง:
      - summary   = color-table 5 คอลัมน์ (หน้าหลัก)
      - positions = color-table 3 คอลัมน์ ตัวแรกของหน้าเวัน (8 ตำแหน่งทักษา)
      - birth     = color-table 3 คอลัมน์ ตัวที่สอง (แถวแรกขึ้นต้นด้วย 'วัน')
      - meanings  = table.facts 2 คอลัมน์ (หน้าหลัก, ไม่มีแถวหัวตาราง)
    """
    summary, positions, birth_rows = [], None, None
    three_col = []
    for t in soup.find_all("table", class_="color-table"):
        rows = t.find_all("tr")
        if not rows:
            continue
        head = _cells(rows[0])
        body = [_cells(tr) for tr in rows[1:] if len(_cells(tr)) >= 2]
        if not body:
            continue
        if len(head) == 5:  # ตารางสรุป 7 วัน (หน้าหลัก)
            for r in body:
                summary.append({
                    "day": r[0],
                    "work": split_colors(r[1]),
                    "money": split_colors(r[2]),
                    "metta": split_colors(r[3]),
                    "avoid": split_colors(r[4]),
                })
        elif len(head) == 3:
            three_col.append((head, body))

    # หน้าเวัน: ตาราง 3 คอลัมน์เรียงเป็น (positions, birth)
    for head, body in three_col:
        if body[0][0].startswith("วัน"):  # แถวแรกเป็นชื่อวัน -> ตารางวันเกิด
            birth_rows = [{"birth": r[0], "highlight": r[1], "avoid": split_colors(r[2])}
                          for r in body]
        else:                             # แถวแรกเป็นหัวข้อ -> ตารางตำแหน่งทักษา
            positions = [{"topic": r[0], "colors": split_colors(r[1]), "position": r[2]}
                         for r in body]

    meanings = {}
    ft = soup.find("table", class_="facts")
    if ft:
        # ตาราง facts ไม่มีแถวหัวตาราง (แถวแรกคือ บริวาร) จึงเก็บทุกแถว
        for tr in ft.find_all("tr"):
            c = _cells(tr)
            if len(c) == 2:
                meanings[c[0]] = c[1]
    return summary, positions, birth_rows, meanings


async def crawl_all(force: bool = False):
    if not force and CACHE.exists():
        try:
            data = json.loads(CACHE.read_text(encoding="utf-8"))
            fetched = datetime.fromisoformat(data["fetched_at"])
            if datetime.now() - fetched < CACHE_TTL:
                log(f"[cache] ใช้ข้อมูลแคช {fetched:%d/%m/%Y %H:%M} ({CACHE})")
                return data
        except Exception:
            pass
    run_cfg = CrawlerRunConfig(remove_overlay_elements=True, page_timeout=45000)
    async with AsyncWebCrawler(config=BrowserConfig(headless=True, verbose=False)) as crawler:
        results = {}
        r = await crawler.arun(url=BASE, config=run_cfg)
        if not r.success:
            raise RuntimeError(f"crawl main page failed: {r.error_message}")
        summary, _, _, meanings = parse_tables(BeautifulSoup(r.html, "html.parser"))
        if len(summary) != 7:
            raise RuntimeError(f"ตารางสรุปหน้าหลักได้ {len(summary)} แถว (คาด 7)")
        results["summary"] = summary
        results["position_meanings"] = meanings
        for slug in DAYS:
            r = await crawler.arun(url=f"{BASE}/{slug}", config=run_cfg)
            if not r.success:
                raise RuntimeError(f"crawl {slug} failed: {r.error_message}")
            _, positions, birth_rows, _ = parse_tables(BeautifulSoup(r.html, "html.parser"))
            if not positions:
                raise RuntimeError(f"parse {slug}: ไม่พบตารางตำแหน่งทักษา")
            results[slug] = {"positions": positions, "birth": birth_rows or []}
            log(f"[crawl] {slug}: {len(positions)} ตำแหน่ง, {len(birth_rows or [])} แถววันเกิด")
    data = {"source": BASE, "fetched_at": datetime.now().isoformat(timespec="seconds"), **results}
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    CACHE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    log(f"[cache] บันทึก {CACHE}")
    return data


def slug_for(d: date) -> str:
    return WEEKDAY_SLUG[d.weekday()]


def print_day(data, slug, birth=None):
    name, planet = DAYS[slug]
    d = data[slug]
    print(f"\n=== สีเสื้อมงคล {name} (ดาว{planet}) ตามตำราทักษา ===")
    print(f"ที่มา: {data['source']} (crawl {data['fetched_at'][:16]})")
    print("\n-- ครบทุกด้าน (นับทักษาจากดาวประจำวัน) --")
    for p in d["positions"]:
        print(f"  {p['topic']:<40} {' / '.join(p['colors']):<20} ({p['position']})")
    if birth:
        row = next((b for b in d["birth"] if b["birth"].startswith(birth)), None)
        if row:
            print(f"\n-- คนเกิด{row['birth']} --")
            print(f"  สีเด่น: {row['highlight']}")
            print(f"  ควรเลี่ยง: {' / '.join(row['avoid'])}")
    else:
        print("\n-- คนเกิดแต่ละวัน (สีเด่น / ควรเลี่ยง) --")
        for b in d["birth"]:
            print(f"  {b['birth']:<18} {b['highlight']:<45} เลี่ยง: {' / '.join(b['avoid'])}")


def print_all(data):
    print("\n=== ตารางสีเสื้อมงคล 7 วัน (ทักษา) ===")
    print(f"{'วัน':<12}{'การงาน':<14}{'เงิน/โชคลาภ':<18}{'เมตตา':<20}{'เลี่ยง':<16}")
    for r in data["summary"]:
        print(f"{r['day']:<12}{' / '.join(r['work']):<14}{' / '.join(r['money']):<18}"
              f"{' / '.join(r['metta']):<20}{' / '.join(r['avoid']):<16}")


def main():
    ap = argparse.ArgumentParser(description="สีเสื้อมงคลตามตำราทักษา (crawl4ai)")
    ap.add_argument("date", nargs="?", help="DD.MM.YYYY — วันที่ต้องการ (default: วันนี้)")
    ap.add_argument("--day", help="ชื่อวัน: อาทิตย์/จันทร์/อังคาร/พุธ/พฤหัสบดี/ศุกร์/เสาร์")
    ap.add_argument("--birth", help="เน้นแถววันเกิด: อาทิตย์/จันทร์/อังคาร/พุธ/พุธกลางคืน/พฤหัสบดี/ศุกร์/เสาร์")
    ap.add_argument("--all", action="store_true", help="แสดงตารางสรุป 7 วัน")
    ap.add_argument("--json", action="store_true", help="พิมพ์ JSON ทั้งหมด")
    ap.add_argument("--no-cache", action="store_true", help="บังคับ crawl ใหม่")
    args = ap.parse_args()

    data = asyncio.run(crawl_all(force=args.no_cache))

    if args.json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return

    if args.all:
        print_all(data)
        return

    if args.day:
        slug = ALIASES.get(args.day.strip()) or ALIASES.get(args.day.strip().lower())
        if not slug:
            sys.exit(f"ไม่รู้จักวัน '{args.day}'")
    elif args.date:
        try:
            d = datetime.strptime(args.date, "%d.%m.%Y").date()
        except ValueError:
            sys.exit(f"รูปแบบวันที่ไม่ถูกต้อง: '{args.date}' (ใช้ DD.MM.YYYY)")
        slug = slug_for(d)
        log(f"[date] {args.date} = {DAYS[slug][0]}")
    else:
        slug = slug_for(date.today())
        log(f"[date] วันนี้ = {DAYS[slug][0]}")

    birth = None
    if args.birth:
        b = args.birth.strip()
        if "พุธ" in b:
            birth = "วันพุธ (กลางคืน)" if "คืน" in b else "วันพุธ (กลางวัน)"
        else:
            slug_b = ALIASES.get(b) or ALIASES.get(b.lower())
            if not slug_b:
                sys.exit(f"ไม่รู้จักวันเกิด '{args.birth}'")
            birth = DAYS[slug_b][0]
    print_day(data, slug, birth)


if __name__ == "__main__":
    main()
