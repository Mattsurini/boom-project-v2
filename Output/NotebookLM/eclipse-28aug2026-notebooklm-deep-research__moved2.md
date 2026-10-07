---
agent: NotebookLM (Deep Research Gate)
date: '2026-08-23'
status: FINAL
notebook: "Eclipse 28 Aug 2026 Pisces - 12 Rising Signs" (id 14e34c83)
notebook_id: 14e34c83-5018-4032-b7c6-67cfc746433a
sources_imported: 44 (web, deep research, 6 errors cleaned)
conversation: 5cec8b50-07c0-444f-8ffc-d64ce1bf09d9
topic: eclipse-lunar-pisces-28aug2026
tags:
  - eclipse
  - deep-research
  - notebooklm
  - audit
---

# 📚 NotebookLM Deep Research: Partial Lunar Eclipse 28 ส.ค. 2026

**Gate:** เดิม fallback (auth expired) → หลัง login ได้วิ่ง deep research จริงบน web 44 แหล่ง.
**ผล:** พบ **correction ระดับราก 4 จุด** ที่ pipeline ต้น (Plawan/Nut/CK/Arm/Nan) คิดผิด — ต้องแก้ใน deliverable.

---

## ✅ CORRECTIONS FOUND (จาก 44 web sources + ready answers)

### C1 🔴 CRITICAL — Ayanamsa error: ผมใช้ Fagan/Bradley ติดป้าย "Lahiri"
- swisseph **default sidereal mode = Fagan/Bradley** (ayanamsa 25.113°).
- Pipeline เดิมโทรศัพท์เรียก "Lahiri" แต่นั่นคือ **Fagan/Bradley**.
- **Lahiri แท้ (SIDM_LAHIRI) = ayanamsa 24.2295°** → sidereal positions เปลี่ยน ~0.88°.
- **Sidereal Moon = ♒ 10°37' (Shatabhisha nakshatra)** — ไม่ใช่ 9°47' (Dhanishta).
- **Sun sidereal Lapíri = ♌ 10°39' (Magha nakshatra)** — ไม่ใช่ 9°47'.
- Ar/orb effect: ~49' — ย้าย nakshatra -> แปลความ nakshatra/lunar-mansion ผิด.

### C2 🔴 CRITICAL — Per-lagna house map ใช้ผิดจุดอ้างอิง
- Pipeline เดิมใช้ **tropical ♓ 4°54'** เพื่อทำ 12-rising whole-sign house map.
- Vedic whole-sign ต้องเริ่มจาก **sidereal ♒ 10°37'** (Lahiri).
- **Corrected house map** (Moon ♒ sidereal, whole-sign): 

| Rising | House | Life-area |
|--------|-------|-----------|
| Aries | 11H | gains, friendships |
| Taurus | 10H | career, fame |
| Gemini | 9H | higher learning, belief |
| Cancer | 8H | shared resources, transformation |
| Leo | 7H | partnership |
| Virgo | 6H | work, health |
| Libra | 5H | romance, children, creativity |
| Scorpio | 4H | home, family |
| Sagittarius | 3H | communication, siblings |
| Capricorn | 2H | finances |
| Aquarius | 1H | self, body |
| Pisces | 12H | seclusion, sleep, hidden |

- (ช่วง pipeline เดิมใช้ Pisces-tropical map → ทุก signs เลื่อน 1 house ผิด. ต้องแก้.)

### C3 🟡 MEDIUM — Mercury cazimi Sun (Arm ผิดที่แก้กลับ)
- Arm audit (Stage 3) ตอนแรกแก้ "Mercury cazimi → conjunct 0.47°".
- **Arm ผิด:** Mercury ได้ **cazimi จริง** — ที่ Aug 27 12:00 UTC Mer-Sun sep **12.6' (<17')** ที่ 4°14' Virgo. คืนก่อน eclipse.
- ที่ GE 04:13 (Aug 28) Mer-Sun = 17.2' — borderline, ยังจัด cazimi-adjacent.
- → Mercury cazimi = sharp clarity + "dream meets receipt" เป็น valid, แก่ Sorsby ถูก.
- ต้อง restore: Mercury cazimi Sun คืนก่อน eclipse.

### C4 🟡 MEDIUM — North Node (Rahu) eclipse ใน Shatabhisha, progressive
- เป็น **North Node lunar eclipse** — ไม่ใช่แค่ release อดีต.
- Moon eclipsed ใน **Rahu-ruled Shatabhisha** nakshatra (Sidereal ♒10°37').
- Sun ใน **Ketu-ruled Magha** (Leo sidereal) — potent axis ของ karmic realignment/clearing.
- Psychological: **progressive development** — ดึงไปสู่อนาคต, ทดสอบว่า Pisces ideals ถูก anchor ด้วย Virgo routines ได้ไหม. (ไม่ใช่แค่ "ปล่อยวางสิ่งที่ผ่านมา")

### C5 💡 ADDITIVE — Mutable T-Square (opp Jupiter... ไม่)
- จริง ๆ เป็น **Mutable T-square**: Moon ♓4°54' ↔ Sun+Mercury ♍4°54' (cazimi) + Uranus ♊5°37' เป็น apex → "bendings" sudden disruptor.
- Uranus ที่ bendings = แก้ intellectual overthinking, บังคับปล่อย grip.

---

## Q&A Evidence (saved)

1. **Fact check** — partial lunar confirmed; tropical 4°54' Pisces confirmed; sidereal **corrected** to 10°37' Aqu (Lahiri); magnitude 0.9299 ✓; GE **04:13 UTC** (04:18 = full-moon moment, แยกกับ GE).
2. **Blind-spot** — partial vs total potency (classical weaker per Ptolemy Tetrabiblos duration-month rule; modern = near-total behaves full); aspects read in tandem not priority; eclipse-set as cumulative arc **supported** (Node axis = chapters); house meanings validated.
3. **House themes + node + cazimi** — full 12-rising list (C2), North Node Rahu-Shatabhisha/Magha karmic axis (C4), Mercury cazimi significance (C3).

---

## Raw ready source (44) highlights
- 2026 Full Moons Calendar (AstroTwins)
- Solar/Lunar Eclipse Horoscopes by Zodiac (Woman's World)
- 3 Zodiac Signs Will Finally Walk Away... (The Economic Times)
- Astronomical Precision, Aspect Dynamics... Near-Total (markdown)
- + 40 more (deep web)

---

## Links
- Research brief: `Output/NotebookLM/eclipse-28aug2026-research-brief.md`
- Notebook: `14e34c83` (Eclipse 28 Aug 2026 Pisces - 12 Rising Signs)