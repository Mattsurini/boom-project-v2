---
agent: Nut (Astrology Technical Extractor)
date: '2026-08-23'
status: FINAL
note: "เขียนโดย orchestrator (Turboz/Ekae) จาก evidence ที่สืบค้นเสร็จแล้ว — child agent เจอ Cloudflare 524 timeout เมื่อพยายามเขียน"
tags:
  - eclipse
  - lunar-eclipse
  - pisces
  - virgo
  - 12-rising
  - technical-extraction
  - convergence
sources:
  - swisseph 2.10.03 (calculation-backed)
  - Astrology-Database Classics (database-backed)
  - Cafe Astrology / Bonnie Sorsby / AstroBella (fallback web research)
---

# 🥜 Nut Technical Extraction: Partial Lunar Eclipse ♓ 4°54' — 28 ส.ค. 2026 (12 Rising Signs)

**Agent:** Nut (Astrology Technical Extractor)
**Date:** 23 ส.ค. 2026 (updated after NotebookLM Deep Research gate)
**Eclipse:** Partial Lunar (96.2% umbral, magnitude 0.9319→0.9299) — 28 ส.ค. 2026 04:12:49 UTC (GE) / 11:13 ICT
**Output for:** Pipeline → CK (psychology), Arm (audit), Nan (critique), Bella (convergence)

> 🔴 **NotebookLM correction applied:** ข้อมูล sidereal ในรอบแรกผิดเพราะใช้ swisseph **default Fagan/Bradley ayanamsa (25.113°)** แล้วติดป้าย "Lahiri". **Lahiri แท้ (SIDM_LAHIRI) = 24.2295°** → sidereal degree ทุกตัวแก้แล้วด้านล่าง. ดู `Output/NotebookLM/eclipse-28aug2026-notebooklm-deep-research.md` C1.

---

## Evidence Convention

| Label | ความหมาย |
|-------|----------|
| **[DB]** | มีการอ้างอิงจาก database โดยตรง (Astrology-Database/Classics) |
| **[NOT IN DB]** | ไม่พบใน database — การสังเคราะห์/การตีความ |
| **[CHART]** | ข้อมูลจากการคำนวณ chart โดยตรง (swisseph) |
| **[SYNTHESIS]** | การตีความของ Nut จากหลายแหล่ง |
| **[fallback web research]** | แหล่งเว็บภายนอก (Cafe Astrology, Sorsby, AstroBella) |
| **[NotebookLM DR]** | จาก NotebookLM Deep Research (44 web sources) |

---

## 📋 Eclipse Technical Profile

| Parameter | Value | Class |
|-----------|-------|-------|
| Type | **Partial Lunar** (96.2% surface, umbral magnitude 0.9299 — deep partial, near-total "Blood Moon") | [CHART] |
| Greatest Eclipse (GE) | 28 ส.ค. 2026 **04:12:49 UTC** / 11:13 ICT | [NotebookLM DR] |
| Full-Moon moment | 28 ส.ค. 2026 04:18 UTC — ต่างจาก GE ~5 นาที | [CHART] |
| Moon (eclipse point) | Tropical ♓ 4°54' — **Sidereal Lahiri ♒ 10°37'** | [CHART] ✅ corrected |
| Sun (opposite) | Tropical ♍ 4°54' — **Sidereal Lahiri ♌ 10°39'** | [CHART] ✅ corrected |
| Nakshatra (Vedic) | Moon: **Shatabhisha** (Rahu-ruled) • Sun: **Magha** (Ketu-ruled) — potent karmic axis | [CHART]+[NotebookLM DR] |
| Key aspects | Moon opp Sun (0°), Moon opp Mercury cazimi-adjacent (~0.47° at GE), Moon sq Uranus (0.72°), Moon conj Mean Node (5.4°); **Mutable T-square** | [CHART]+[NotebookLM DR] |
| Eclipse set | **#6 ของ 7** ในชุด Virgo-Pisces (ก.ย. 2024 – ก.พ. 2027) — ปิด "almost tetrad" | [fallback web research] |
| Ayanamsa (Lahiri, SIDM_LAHIRI) | **24.2295°** (ไม่ใช่ 25.113° ซึ่งเป็น Fagan/Bradley) | [CHART] ✅ corrected |

**Full tropical positions (swisseph):** Sun ♍ 4°54', Moon ♓ 4°54', Mercury ♍ 5°22', Venus ♎ 20°02', Mars ♋ 10°57', Jupiter ♌ 12°53', Saturn ♈ 13°53' Rx, Uranus ♊ 5°37', Neptune ♈ 3°45' Rx, Pluto ♒ 3°34' Rx, Mean Node ♒ 29°30' Rx. [CHART]

**Sidereal Lahiri positions (SIDM_LAHIRI, corrected):** Sun ♌ 10°39', Moon ♒ 10°37', Mercury ♌ 11°07', Venus ♍ 25°47', Mars ♊ 16°43', Jupiter ♋ 18°39', Saturn ♓ 19°39', Uranus ♉ 11°23', Neptune ♓ 9°31', Pluto ♑ 9°21', Mean Node ♒ 5°16'. **[CHART] ✅ corrected — round 1 ใช้ Fagan/Bradley ผิด**

### 🌐 GE timing note
- NotebookLM/sources: GE = 04:12:49 UTC (04:13); 04:18 = full-moon phase point.
- ต่างจาก round 1 (04:18) เพียง ~5 นาที — ไม่เปลี่ยนตีความ house/aspect อย่างมีนัย. [NotebookLM DR]

---

## 📜 Classical Extraction (Vedic)

### Eclipse = Rahu/Ketu (Node) phenomenon
- **BPHS V1 (~line 1966):** Rahu/Ketu "for they are only mathematical points. On the contrary, they eclipse or obstruct the Sun" — nodes are the mechanism of eclipse, not combust. **[DB]**
- **BPHS V1 (~line 1961):** "If a planet is eclipsed in the Sun, it proves impotent" — eclipsed planet loses power/function. **[DB]**
- **Phaladeepika v.36:** eclipsed planets are "adversely disposed." **[DB]**
- **Phaladeepika v.1541:** eclipsed house-lord → "effects of that house are totally destroyed." **[DB]** → แปลว่า per-rising interpretation = **Rahu/Ketu house effects + house-lord temporary disablement.**

### Lunar eclipse specificity
- **Saravali (infant-death chapter, ~line 537):** "If the Moon be eclipsed and be in the Ascendant along with malefics, while Mars is in 8th, the child quits the world along with its mother" — confirms **lagna-placed eclipsed Moon is the most acute** (life-level severity symbolically). **[DB]**
- **Brihat Jataka (Stanza 9, ~line 693):** "If Moon joins a malefic in lagna, eclipsed with Mars..." **[DB]**
- **Brihat Jataka (Stanza 12, ~line 2020):** "If Moon when occupying the lagna is eclipsed by Rahu, [native] suffers..." **[DB]**
- **Phaladeepika:** Moon eclipsed when ~12° from Sun (combustion-lunar rule). **[DB]**

### House system — Whole-Sign is Vedic default
- **aspects-in-vedic-astrology.md (~line 223):** "the whole sign of Sagittarius would constitute the First house" — confirms **whole-sign** as classical Vedic house basis. **[DB]**
- Placidus appears in DB **only for KP** (kp system_raghunath.md ~line 127) — **no classical rule for Placidus eclipse houses → [NOT IN DB]**.
- **Conclusion:** ใช้ **whole-sign houses** สำหรับ eclipse-effect-by-rising — เป็น classical-correct basis. [SYNTHESIS]

### Gaps confirmed NOT IN DB (after search)
- **Eclipse + Uranus:** Classics ไม่ใช้ Uranus — "No cognizance is taken of the trans-Saturnian planets" (aspects-in-vedic-astrology.md ~line 231). **[NOT IN DB]**
- **Saros/eclipse-set-as-unit:** มีแค่ eclipse-season mention (vimsottari-and-udu-dasas.md ~line 8313) — ไม่มี classical rule ว่า "ชุด eclipse" ทำงานเป็นหน่วย. **[NOT IN DB]**
- **Lunar-eclipse-by-house specific chapter:** ไม่พบบทเจาะจง. **[NOT IN DB]**

---

## 🌐 Fallback Web Research (Substantive)

### Cafe Astrology [fallback web research]
- ยืนยัน: eclipse เป็นชุด **#6 ของ 7** บน Virgo-Pisces axis (2024–2027).
- กฎ trigger: natal planets ที่ **0–10° ของ mutable signs** (Gemini/Virgo/Sagittarius/Pisces) ถูก eclipse กระตุ้นตรงที่สุด → สำหรับ eclipse นี้ = natal Sun/Moon/Mercury/Uranus ที่ ~4°54' mutable.
- Window: ผลอยู่ราว **~6 เดือน** หลัง eclipse.
- Tone: "defer judgment — we're in the dark" — ช่วง eclipse อย่าตัดสินใจยึดข้อมูลเก่า.

### Bonnie Sorsby [fallback web research]
- Mercury **cazimi Sun** ที่ 5° Virgo (คืนก่อนหน้า) — Mercury อยู่ในใจกลางของ Sun = การสื่อสารถูก "หลอม/ชี้เจน" แบบพิเศษก่อน eclipse.
- Uranus เป็น **apex ของ T-square** — แรงปลดปล่อยฉับพลัน, sudden clarity.
- ยืนยัน: per-rising house themes ตรงกับ whole-sign map ของเรา.

### AstroBella [fallback web research]
- Fomalhaut (~4°14' Pisces) conjunct eclipse point — "star of success/fame" สัมผัสจุด eclipse.
- Uranus square = sudden clarity / "เปลี่ยนไฟล์ขณะที่มันยังเปิดอยู่"
- eclipse นี้ = "final chapter of the axis" — ปิดจบธีม Virgo-Pisces ที่สะสมมากว่า 2 ปีครึ่ง.

---

## ♈–♓ Per-Rising-Sign Technical Section (Whole-Sign)

### Trigger-point rule (corrected for sidereal ♒10°37')
Natal planets ที่ **นาที ~10°37' ของ sidereal Aquarius** (หรือตามแหล่ง web: 0–10° ของ mutable signs/Tropical 4°54') จะถูก eclipse กระตุ้นตรงจุด. ตรวจ natal Moon/Sun/Mercury/Uranus เป็นหลัก. [fallback web research + [CHART]]

### House map — 🔴 CORRECTED (sidereal Aquarius, whole-sign) — per NotebookLM C2
> Vedic whole-sign ต้องวัดจาก **sidereal Moon ♒ 10°37'** (Lahiri) ไม่ใช่ tropical Pisces. round 1 ใช้ ♓ 4°54' ผิด → ทุก sign เลื่อน 1 house.
> *Reference (tropical Pisces ♓4°54') เพื่อเทียบบรรทัด: Aries=12H, Taurus=11H, Gemini=10H, Cancer=9H, Leo=8H, Virgo=7H, Libra=6H, Scorpio=5H, Sag=4H, Cap=3H, Aqu=2H, Pis=1H.*

| Rising | Eclipse Moon (sidereal ♒) | Life-area (Vedic) | Sun ♌10°39' house |
|--------|----------------------|-------------------|-------------------|
| **Aries** | 11H | gains, friendships, hopes, networks | 5H |
| **Taurus** | 10H | career, status, profession, fame | 4H |
| **Gemini** | 9H | higher learning, belief, dharma, far lands | 3H |
| **Cancer** | 8H | shared resources, transformation, crisis, occult | 2H |
| **Leo** | 7H | partnership, marriage, contracts, other | 1H |
| **Virgo** | 6H | work, health, daily routine, service, enemies | 12H |
| **Libra** | 5H | romance, children, creativity, speculation | 11H |
| **Scorpio** | 4H | home, family, roots, immovable property, mother | 10H |
| **Sagittarius** | 3H | communication, siblings, short trips, courage | 9H |
| **Capricorn** | 2H | finances, family assets, wealth, speech | 8H |
| **Aquarius** | 1H | **self, body, health, identity, new beginnings (lagna)** | 7H |
| **Pisces** | 12H | seclusion, sleep, hidden, moksha, isolation, expenses | 6H |

### Codebook (aspect dynamic per house)
- **Moon opp Sun+Mercury (opp cluster, Mercury cazimi-adjacent):** communication/contracts/คำพูดตึงถึงจุดแตก — สิ่งที่พิมพ์/พูด/เซ็น โดนทบทวน; Sharper มากเพราะ Mercury cazimi (dream vs receipt). [CHART + [NotebookLM DR]]
- **Moon sq Uranus (0.72°):** สะสมมานาน explode แบบไม่คาดคิด → sudden release, "bendings" ของ T-square. [CHART + [NotebookLM DR]]
- **Moon conj Mean Node (5.4°) + Rahu-Shatabhisha / Ketu-Magha nakshatra axis:** karmic realignment, **North Node = progressive development ดึงไปสู่อนาคต** (ไม่ใช่แค่ปล่อยอดีต). [CHART + [NotebookLM DR]]
- **Eclipsed house-lord + house:** ความหมายของเรือนนั้น "โดนปิด/ชะงัก" ชั่วคราว → reset แล้วค่อยกลับมา. [DB — Phaladeepika v.1541]

### ♈ Aries Rising — Eclipse 11H
- Eclipse Moon 11H (sidereal ♒): gains, friendships, hopes, networks, groups
- Sun 5H, Mean Node 10H (approx)
- Theme: กลุ่ม/เพื่อน/คอนเนคชัน/เป้าหมายระยะยาว reset — ตัดทอนเครือข่าย, ทบทวนเพื่อนที่ "แท้จริง"
- Dynamics: Mercury opp → ข้อความ/สัญญาในกลุ่มถูกชำแหละ; Uranus sq → เพื่อน/กลุ่มที่พันมานานหลุดแบบกระทันหัน
- Trigger: natal planets 0–10° mutable

### ♉ Taurus Rising — Eclipse 10H
- Eclipse Moon 10H: อาชีพ, ชื่อเสียง, สถานะ, เจ้านาย, เป้าหมายชีวิต
- Sun 4H, Node 9H
- Theme: การงาน/สถานะ reset — บทบาทหน้าที่ถูกทบทวน, ชื่อเสียง/ภาพพจน์โดนปิดชั่วคราวก่อนคืน
- Dynamics: Mercury opp → คำพูด/เอกสารในงานถูกตรวจสอบพิเศษ; Uranus sq → โครงสร้างงานเปลี่ยนกะทันหัน, ถูกไล่/ย้าย/เปลี่ยนบทบาท

### ♊ Gemini Rising — Eclipse 9H
- Eclipse Moon 9H: การศึกษาสูง, ต่างประเทศ, ศาสนา/ปรัชญา, คดีความ, ความเชื่อ
- Sun 3H, Node 8H
- Theme: ความเชื่อ/การศึกษา/เรื่องไกลตัว reset — ทบทวน world-view, เรียน/เดินทาง/คดีชะงักชั่วคราว
- Dynamics: Mercury opp → เอกสาร/ประกาศ/วิทยานิพนธ์ถูกแก้; Uranus sq → มุมมองความเชื่อเปลี่ยนกระทันหัน

### ♋ Cancer Rising — Eclipse 8H
- Eclipse Moon 8H: การเงินร่วม, หนี้สิน, มรดก, ทรัพยากรของคนอื่น, วิกฤต, ปลดหนี้/เปลี่ยนผ่าน, occult
- Sun 2H, Node 7H
- Theme: การเงินร่วม/หนี้/การลงทุนที่ใช้เงินคนอื่น reset — วิกฤตที่ต้องผ่าน, shared-resource ถูกทบทวน
- Dynamics: Mercury opp → สัญญาทางการเงิน/ประกัน/ภาษีถูกชำแหละ; Uranus sq → หนี้/การลงทุนผันผวนกะทันหัน ต้องสำรอง
- Note: 8H member-leo ที่เปลี่ยนผ่านเชิงลึก (transformative) — หนักปานกลาง

### ♌ Leo Rising — Eclipse 7H
- Eclipse Moon 7H: คู่ชีวิต, หุ้นส่วน, สัญญา, ศัตรูเปิดเผย, ความสัมพันธ์ 1-ต่อ-1
- Sun 1H, Node 6H
- Theme: ความสัมพันธ์/สัญญา/การเป็นคู่ reset — การแต่งงาน/หุ้นส่วน/สัญญากฎหมายถูกทบทวน
- Dynamics: Mercury opp → ข้อตกลง/คำพูดระหว่างคู่ถูกตรวจ; Uranus sq → ความสัมพันธ์ที่ "พ้นกำหนด" แตกกะทันหัน

### ♍ Virgo Rising — Eclipse 6H
- Eclipse Moon 6H: สุขภาพ, งานประจำ, พนักงาน/คนรับใช้, กิจวัตร, โรคภัย
- Sun 12H, Node 5H
- Theme: งานประจำ/สุขภาพ/กิจวัตร reset — เปลี่ยนงาน, ตรวจสุขภาพ, ปรับระบบทำงาน
- Dynamics: Mercury opp → งานเอกสาร/รายงาน/คิวโดนโหลด; Uranus sq → งาน/สุขภาพกระทึ; ต้องแยกร่างกายกับงาน

### ♎ Libra Rising — Eclipse 5H
- Eclipse Moon 5H: ความรักโรแมนติก, ลูก, ความคิดสร้างสรรค์, การเก็งกำไร, ความสนุก
- Sun 11H, Node 4H
- Theme: ความรัก/ลูก/สร้างสรรค์ reset — เรื่องหัวใจ/โปรเจกต์สร้างสรรค์/การลงทุนเสี่ยงถูกทบทวน
- Dynamics: Mercury opp → บทสนทนา/สัญญารักถูกชำแหละ; Uranus sq → ความรู้สึก/ไฟสร้างสรรค์เปลี่ยนกะทันหัน

### ♏ Scorpio Rising — Eclipse 4H
- Eclipse Moon 4H: บ้าน, ครอบครัว, รากเหง้า, อสังหาริมทรัพย์, ความมั่นคงในใจ, แม่
- Sun 10H, Node 3H
- Theme: บ้าน/ครอบครัว/ราก reset — ย้ายบ้าน, เรื่องพ่อแม่/คนในบ้าน, ความมั่นคงทางใจ
- Dynamics: Mercury opp → การติดต่อ/เอกสารบ้านถูกตรวจ; Uranus sq → สภาพบ้าน/ครอบครัวเปลี่ยนกระทันหัน

### ♐ Sagittarius Rising — Eclipse 3H
- Eclipse Moon 3H: การสื่อสาร, พี่น้อง, เพื่อนบ้าน, ระยะสั้น, การเดินทางใกล้, ทักษะ, ความกล้า
- Sun 9H, Node 2H
- Theme: การสื่อสาร/พี่น้อง/ยานพาหนะ reset — เปลี่ยนวิธีพูดคุย, เรื่องติดต่อ, เรียนสั้น/เดินทางใกล้
- Dynamics: Mercury opp → คำพูด/ข้อความถูกเข้าใจผิดพิเศษ; Uranus sq → ข่าว/ติดต่อ/การเดินทางเปลี่ยนกระทันหัน

### ♑ Capricorn Rising — Eclipse 2H
- Eclipse Moon 2H: การเงินส่วนตัว, รายได้, ค่านิยม, ความมั่นคง, ทรัพย์สินของตัวเอง
- Sun 8H, Node 1H
- Theme: รายได้/ค่านิยม/ทรัพย์ส่วนตัว reset — รายได้เปลี่ยนทาง, ทบทวนสิ่งที่ให้ค่ากับตัวเอง
- Dynamics: Mercury opp → ตัวเลข/สัญญาการเงินถูกชำแหละ; Uranus sq → รายได้/ค่าใช้จ่ายผันผวนกะทันหัน ตั้งสำรอง

### ♒ Aquarius Rising — Eclipse 1H (Lagna) — 🔴 acute (ถูกแก้จาก 2H wrong)
- Eclipse Moon 1H (Lagna): ตัวตน, ร่างกาย, อัตลักษณ์, การปรากฏตัว, ทิศทางชีวิต — **acute ที่สุด** (lagna eclipsed)
- Sun 7H, Node 12H
- Theme: ตัวตน/ร่างกาย/ภาพพจน์ reset — identity shift, รูปลักษณ์/บทบาทเปลี่ยน, reset ทิศทาง; North Node = progressive development สู่ตัวตนใหม่ (ไม่ใช่แค่ปล่อย)
- Dynamics: Mercury opp → ตนเอง vs คู่ขัดแย้งทางคำพูด; Uranus sq → ภาพพจน์/ตัวตนเปลี่ยนกระทันหัน; node conj ใน Shatabhisha = ชัดเจนว่าต้องเติบโตไปทางไหน

### ♓ Pisces Rising — Eclipse 12H
- Eclipse Moon 12H: seclusion, sleep, hidden, moksha, isolation, expenses, foreign lands
- Sun 6H, Node 11H
- Theme: เรื่องลับ/ปลีกวิเวก/ค่าใช้จ่าย/มรรคปล่อยวาง reset — ลางาน, จัดการความกลัว/หนี้ที่ซ่อน, spiritual release
- Dynamics: Mercury opp → เก็บคำพูดในใจไว้ไม่ได้, ระบายออก; Uranus sq → เรื่องซ่อนที่ "เหนื่อยแบก" หลุดออกแบบกระทันหัน

---

## 📊 Evidence Class Summary

| Section | [CHART] | [DB] | [NOT IN DB] | [fallback web research] | [SYNTHESIS] |
|---------|--------|------|-------------|--------------------------|-------------|
| Eclipse profile | ✅ | — | — | set #6 | — |
| Classical eclipse rule | — | ✅ BPHS, Phal., Saravali, BJ | — | — | — |
| Whole-sign house | — | ✅ | Placidus eclipse rule | — | whole-sign chosen |
| Uranus/saros gaps | — | — | ✅ | — | — |
| Per-rising themes | ✅ positions | house-lord rule | — | trigger rule | house meanings |
| Web research | — | — | — | ✅ | — |

**Nota bene:** Per-rising house *themes* (12H=จิตใต้สำนึก etc.) เป็น classical house meanings ที่รู้กันทั่วไป [SYNTHESIS] — individual trigger ต้อง validate natal planets ที่ 0–10° mutable แยกแต่ละคนต่อไปใน Bella.