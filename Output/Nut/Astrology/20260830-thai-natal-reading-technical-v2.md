---
agent: Nut
date: '2026-08-30'
version: v2
---

# Nut Technical Extraction v2: Thai Natal-Reading Pipeline

**ขอบเขต:** extraction หลังผูกดวง ไม่คำนวณ personal chart ไม่ค้นเว็บ/secondary/classical เพิ่ม ทุกข้อระบุประเภทหลักฐาน

## NotebookLM Raw Evidence

1. **NotebookLM raw evidence:** Q&A ระบุลัคนา ตนุลัคน์/ตนุเศษ ภพ 12 ดาวเจ้าเรือน ดาวลอย ภพผสมภพ มาตรฐานดาว และดาวคู่เป็นแกนของการอ่าน (ไฟล์ `E:\Boom Project\Output\NotebookLM\20260830-thai-natal-reading-targeted-qa.md`, บรรทัด 75–143)
2. **NotebookLM raw evidence:** บทบาทที่รายงานคือ ลัคนาเป็นจุดตั้งต้น, ตนุลัคน์เกี่ยวกับตัวตน, ตนุเศษเกี่ยวกับจิตใจ, ภพ 12 เป็นโครงสร้างชีวิต, ดาวเจ้าเรือนเป็นตัวแสดงเหตุ และดาวลอยเป็นปัจจัยในภพ (targeted-qa, บรรทัด 81–115)
3. **NotebookLM raw evidence:** ภพผสมภพเชื่อมเรือนต้นทางกับผลลัพธ์; มาตรฐานดาวคือ เกษตร อุจ ประ นิจ มหาจักร ราชาโชค; ดาวคู่มีคู่ธาตุ สมพล ศัตรู มิตร (targeted-qa, บรรทัด 118–140)
4. **NotebookLM raw evidence:** blind-spot ระบุว่าขาดตารางอันโตนาฑี/ชดเชยเวลา, สูตรสมผุส, epoch/ayanamsa; ยังไม่ระบุเศษ 0 ของตนุเศษ และไม่มีตารางภพผสมภพครบ 144 คู่ (ไฟล์ `E:\Boom Project\Output\NotebookLM\20260830-thai-natal-reading-blind-spot.md`, บรรทัด 156–198)
5. **NotebookLM raw evidence:** มาตรฐานดาวขาด mapping ดาว–ราศี, คู่ 2–5 ซ้อนหลายสถานะ และยังขาด provenance, test dataset, gold standard, blind/holdout protocol (blind-spot, บรรทัด 199–234)

## Chart/Method Observations

- **Prior extraction:** เอกสารเดิมจัดลำดับ ลัคนา → ภพ 12 → ดาวเจ้าเรือน/ดาวลอย → ภพผสมภพ → synthesis และแยกหัวข้อที่ coverage รองรับออกจากสูตรที่ยังไม่พบ (ไฟล์ `E:\Boom Project\Output\Nut\Astrology\20260830-thai-natal-reading-technical.md`, บรรทัด 61–75, 112–123; ประเภท: prior extraction)
- **Prior extraction:** เสนอให้บันทึกวันเวลา สถานที่ timezone และระบบ zodiac/epoch เพื่อทำซ้ำได้ (technical เดิม, บรรทัด 65–70, 112–124; ประเภท: prior extraction)
- **Synthesis:** เก็บเฉพาะค่าที่ input มี พร้อม source/school tag; ห้ามเติมตำแหน่งดาวหรือผลบุคคลที่ไม่มีในสี่ไฟล์ (อ้าง blueprint `E:\Boom Project\Output\Plawan\Astrology\thai-natal-reading-blueprint.md`, บรรทัด 17–28, 40–53; ประเภท: synthesis)

## Source-backed Rules

- **NotebookLM raw evidence:** ภพว่างให้พิจารณาดาวเจ้าเรือนหรือดาวสัมพันธ์ แต่ยังไม่มี precedence, orb หรือ threshold ตัวเลข (targeted-qa, บรรทัด 110–115; blind-spot, บรรทัด 186–198; ประเภท: NotebookLM raw evidence)
- **NotebookLM raw evidence:** มาตรฐานดาว/ดาวคู่ต้องเก็บเป็น metadata พร้อมกฎและบริบท เพราะมี vocabulary แต่ยังไม่มี mapping, hierarchy, exception และ tie-breaker (targeted-qa, บรรทัด 126–140; blind-spot, บรรทัด 199–214; ประเภท: NotebookLM raw evidence)
- **Prior extraction:** จนกว่าจะมีสูตรและ locator ระดับข้อความ ห้ามทำ Suriyayatra/Lahiri, ตนุเศษ, ภพผสมภพ, มาตรฐานดาว หรือดาวคู่เป็น deterministic predicate; ติด `[UNRESOLVED]` (technical เดิม, บรรทัด 112–123, 126–150; ประเภท: prior extraction)

## Synthesis

**Synthesis:** bounded pipeline มี 5 ขั้น: (1) รับ chart พร้อม provenance/สมมติฐาน; (2) บันทึกลัคนา ภพ 12 ดาวสถิต ดาวเจ้าเรือน/ดาวลอย และ school tag; (3) ใช้ภพผสมภพ มาตรฐานดาว และดาวคู่เฉพาะรายการที่มีสูตร/ตาราง/ตัวอย่าง; (4) แยก observation, rule, synthesis, unresolved; (5) ส่ง claim id, locator และ rule version ไปทดสอบ (อ้าง blueprint บรรทัด 17–28, 55–71; targeted-qa บรรทัด 75–143; blind-spot บรรทัด 186–234; ประเภท: synthesis)

## Unresolved/Blind Spots

1. **NotebookLM raw evidence:** ขาดอันโตนาฑี/ชดเชยเวลา, สูตรสมผุส, epoch/ayanamsa และกติกา Suriyayatra–Lahiri (blind-spot, บรรทัด 156–185)
2. **NotebookLM raw evidence:** ขาดกรณีเศษ 0, นิยามดาวลอยที่ implement ได้, ตารางภพผสมภพครบ และ conflict resolution (blind-spot, บรรทัด 169–198)
3. **NotebookLM raw evidence:** ขาด mapping มาตรฐานดาว, นิยามดาวคู่ที่ไม่ซ้อน, provenance, test dataset, gold standard และเกณฑ์ “อ่านถูก” (blind-spot, บรรทัด 199–234)
4. **Prior extraction:** exact lordship/ดาวลอย, house-mixing formula, operational standards/pairs และ calculation assumptions ยัง unresolved (technical เดิม, บรรทัด 126–150; ประเภท: prior extraction)
5. **Synthesis:** ต้องขอ source export พร้อมข้อความต้นทาง/locator ก่อน version กฎและทดสอบแบบปกปิดผลลัพธ์; ห้ามเติมช่องว่างด้วย classical หรือ secondary (blueprint, บรรทัด 55–71; blind-spot, บรรทัด 215–234; ประเภท: synthesis)

## Sources

- `E:\Boom Project\Output\NotebookLM\20260830-thai-natal-reading-targeted-qa.md` — primary NotebookLM Q&A.
- `E:\Boom Project\Output\NotebookLM\20260830-thai-natal-reading-blind-spot.md` — primary NotebookLM blind-spot.
- `E:\Boom Project\Output\Plawan\Astrology\thai-natal-reading-blueprint.md` — blueprint/scope.
- `E:\Boom Project\Output\Nut\Astrology\20260830-thai-natal-reading-technical.md` — prior extraction only.
