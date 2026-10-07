---
name: lucky-colors-taksah
description: "Use when BooM asks สีเสื้อมงคล / lucky shirt colors."
version: 1.0.0
author: Turboz
license: MIT
tags: [astrology, thaksa, lucky-colors, clothing, daily, crawl4ai, thai]
metadata:
  hermes:
    tags: [astrology, thaksa, lucky-colors, clothing, daily, thai]
    related_skills: [boom-chinese-almanac, thai-seven-number-horoscope, daily-transit]
---

# สีเสื้อมงคลตามตำราทักษา (Lucky Shirt Colors — Thaksa)

## When to Use

BooM asks "สีเสื้อมงคลวันนี้", "ใส่เสื้อสีอะไรดี", "สีกาลกิณี", "สีเสริมงาน/เงิน", "สีเสื้อมงคล 2570", "สีเสื้อมงคลตามทักษา", or any daily clothing-color question.

## Quick procedure

1. Normalize the date. BooM often writes `DD.MM.YYYY` — keep that convention.
2. Run the script (Boom `.venv`, cwd `E:\Boom Project`):

```
.venv/Scripts/python scripts/lucky_colors_taksah.py                 # วันนี้
.venv/Scripts/python scripts/lucky_colors_taksah.py 06.10.2026      # วันระบุ (DD.MM.YYYY)
.venv/Scripts/python scripts/lucky_colors_taksah.py --day พฤหัสบดี   # วันระบุชื่อ
.venv/Scripts/python scripts/lucky_colors_taksah.py --day ศุกร์ --birth พฤหัสบดี
.venv/Scripts/python scripts/lucky_colors_taksah.py --all           # ตาราง 7 วัน
.venv/Scripts/python scripts/lucky_colors_taksah.py --json          # JSON ครบ (stdout สะอาด)
.venv/Scripts/python scripts/lucky_colors_taksah.py --no-cache      # บังคับ crawl ใหม่
```

3. Answer fast: การงาน / เงิน-โชคลาภ / ผู้ใหญ่เมตตา / เลี่ยง first; expand only if asked.
4. Offline fallback: the table is fixed every year (traditional ทักษา) — answer from `references/taksa-7days.md` or the summary table below without crawling.

## Summary table (7 days) — static, same every year

| วัน | การงาน | เงิน/โชคลาภ | ผู้ใหญ่เมตตา | เลี่ยง (กาลกิณี) |
| --- | --- | --- | --- | --- |
| วันอาทิตย์ | ชมพู | เขียว | เทา / ดำ / น้ำตาล | ฟ้า / น้ำเงิน |
| วันจันทร์ | เขียว | ม่วง | ฟ้า / น้ำเงิน | แดง |
| วันอังคาร | ม่วง | ส้ม / แสด | แดง | เหลือง / ขาว / ครีม |
| วันพุธ | ส้ม / แสด | เทา / ดำ / น้ำตาล | เหลือง / ขาว / ครีม | ชมพู |
| วันพฤหัสบดี | ฟ้า / น้ำเงิน | แดง | เขียว | ม่วง |
| วันศุกร์ | เหลือง / ขาว / ครีม | ชมพู | ส้ม / แสด | เทา / ดำ / น้ำตาล |
| วันเสาร์ | เทา / ดำ / น้ำตาล | ฟ้า / น้ำเงิน | ชมพู | เขียว |

## Rules

- 8 ตำแหน่งในวงทักษา: บริวาร · อายุ · เดช · ศรี · มูละ · อุตสาหะ · มนตรี · กาลกิณี
- สีกาลกิณี = สีที่ควรเลี่ยงในวันสำคัญ ไม่ได้แปลว่าใส่แล้วเกิดเรื่องร้าย (ตำราใช้เสริมกำลังใจ)
- สองชั้น: (1) นับจากดาวประจำวัน → สีประจำวัน; (2) ถ้ารู้วันเกิด นับจากดาววันเกิดอีกชั้น → สีเฉพาะตัว
- คนเกิดวันพุธหลัง 18:00 นับเป็น **ราหู** ไม่ใช่พุธ — สีเด่นและกาลกิณีคนละชุดกับพุธกลางวัน
- สีประจำดาว: อาทิตย์ แดง · จันทร์ เหลือง/ขาว/ครีม · อังคาร ชมพู · พุธ เขียว · พฤหัสบดี ส้ม/แสด · ศุกร์ ฟ้า/น้ำเงิน · เสาร์ ม่วง · ราหู เทา/ดำ/น้ำตาล

## Pitfalls

- อักขระไทยในไฟล์โปรเจกต์นี้เคยเพี้ยนเป็นเครื่องหมายซ้ำ (`"สสสี"` แทน `"สี"`, `"ตำแหน่่ง"` แทน `"ตำแหน่ง"`) ทำให้เงื่อนไข `in` เป็น False และ parse ได้ค่าว่างทั้ง 7 วัน — **อย่าเทียบหัวตารางภาษาไทย**; สคริปต์แยกตารางด้วยโครงสร้าง (จำนวนคอลัมน์ + ลำดับตาราง + แถวแรกขึ้นต้นด้วย "วัน" = ตารางวันเกิด) ให้คงวิธีนี้ไว้
- dict key ทุกตัวในสคริปต์เป็นภาษาอังกฤษโดยเจตนา — อย่าเปลี่ยนกลับเป็นคีย์ไทย
- Cache: `Output/Sources/Lucky-Colors/lucky_colors_taksah.json` (TTL 24 ชม.) ใช้ `--no-cache` เมื่อต้องการข้อมูลใหม่
- log ไป stderr เพื่อให้ `--json` ส่ง JSON ล้วนทาง stdout — ถ้าแก้ ให้รักษาพฤติกรรมนี้
- ที่มา: https://mu.loveiseveryday.com/lucky-colors (สำนักหอคอยขนนก) — สำนักอื่นไม่ตรงกันเพราะปรับตามดาวจร/ดวงเมือง; ตารางนี้ตายตัวทุกปี
- ถ้า crawl ล้มเหลว ห้ามแต่งสีขึ้นเอง — ใช้ตาราง static ด้านบน/ใน references แทน

## References

- `references/taksa-7days.md` — ตารางครบ 8 ตำแหน่งของทั้ง 7 วัน + สีเฉพาะคนเกิดแต่ละวัน (สร้างจาก crawl ที่ตรวจสอบแล้ว)
- `scripts/lucky_colors_taksah.py` — ตัวสคริปต์ (crawl4ai + BeautifulSoup)
