---
topic: astrology
subtopic: simple-transit-method
stage: Nut
created_utc: 2026-08-09T16:05:00Z
---
# Nut Technical Extraction: Simple Transit Method

## Easy layer
- ใช้ natal chart ที่คำนวณด้วยวันเวลา/สถานที่ถูกต้อง และใช้ zodiac/house system เดียวกัน
- overlay transits กับ natal Sun, Moon, ASC, MC, chart ruler และ ruler ของเรื่องที่ถาม
- priority: Saturn/Jupiter/Uranus/Neptune/Pluto, eclipses/nodes → Mars → Sun/Mercury/Venus/Moon
- major aspects ก่อน: conjunction, opposition, square → trine, sextile
- fast planet ปกติเป็น trigger ของธีมที่ slow planet ตั้งไว้

## Timing layer
แยก applying, exact, separating; ตรวจ retrograde ที่ทำให้ aspect กลับมาหลาย pass ใช้ ephemeris scan ไม่ใช้ linear speed โดยเฉพาะ Mercury/Mars และต้องแปลง UTC เป็น ICT

## Advanced verification
สแกน transit-to-natal ทั้งหมดแล้ว sort ตาม orb; ตรวจ houses/angles, station/retrograde, eclipse proximity และ VOC เฉพาะเมื่อคำถามเป็น horary/electional/event timing ไม่เอา VOC มาใช้เป็นกฎ transit ทั่วไป

## Common errors
natal time ผิด, house system ไม่ตรง, ใช้ transit sign อย่างเดียว, cherry-pick Moon, ใช้ orb กว้างแบบ natal, และให้ความหมายก่อนตรวจ calculation

## Sources
- Astrodienst Astrowiki — Transit: https://www.astro.com/astrowiki/en/Transit
- Swiss Ephemeris: https://www.astro.com/swisseph/swephinfo_e.htm
- Project calculation/source protocol: `integrated-astrology` skill
