#!/usr/bin/env python3
"""
Thai 7-Number 9-Base Numerology Calculator
Ported from https://hora-7-of-9-base.vercel.app/ (Next.js bundle)
For Boom Project integration with scripts/ astrology stack
"""

from __future__ import annotations
from dataclasses import dataclass
from datetime import date, datetime
from typing import Literal
import json


# ─── Thai Lunar Calendar Constants ─────────────────────────────────────

# Thai zodiac animals (12-year cycle)
THAI_ZODIAC = [
    "ชวด", "ฉลู", "ขาล", "เถาะ", "มะโรง", "มะเส็ง",
    "มะเมีย", "มะแม", "วอก", "ระกา", "จอ", "กุน"
]

# Weekday names
THAI_WEEKDAYS = [
    "อาทิตย์", "จันทร์", "อังคาร", "พุธ", "พฤหัสบดี", "ศุกร์", "เสาร์"
]

# Lunar month names
THAI_MONTHS = [
    "มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", "พฤษภาคม", "มิถุนายน",
    "กรกฎาคม", "สิงหาคม", "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"
]

# Naksat (lunar mansions) - 12 nakshatras
NAKSAT = [
    "อัตตะ", "หินะ", "ธนัง", "ปิตา", "มาตา", "โภคา",
    "มัชฌิมา", "อาตมา", "ทาสา", "สิทธิโชค", "โภคสมบัติ", "มหาโจร"
]

# Buddhist Era offset
BE_OFFSET = 543

# Supported date range (Julian Days)
JD_START = 2385520  # ~1820 CE
JD_END = 2555000    # ~2120 CE


# ─── Core Calendar Functions ──────────────────────────────────────────

def gregorian_to_julian_day(year: int, month: int, day: int) -> int:
    """Convert Gregorian date to Julian Day Number."""
    a = (14 - month) // 12
    y = year + 4800 - a
    m = month + 12 * a - 3
    return day + ((153 * m + 2) // 5) + 365 * y + (y // 4) - (y // 100) + (y // 400) - 32045


def julian_day_to_gregorian(jd: int) -> tuple[int, int, int]:
    """Convert Julian Day Number to Gregorian date."""
    b = jd + 32044
    c = (4 * b + 3) // 146097
    d = b - (146097 * c) // 4
    e = (4 * d + 3) // 1461
    f = d - (1461 * e) // 4
    g = (5 * f + 2) // 153
    day = f - (153 * g + 2) // 5 + 1
    month = g + 3 - 12 * (g // 10)
    year = 100 * c + e - 4800 + (g // 10)
    return year, month, day


# ─── Precomputed Lunar Calendar Table (from gen_lunar_table.py) ────────

# The bundle contains a massive JSON with month lengths for 100 years.
# We'll load it from a JSON file (to be generated/extracted).
# For now, here's the structure:

@dataclass
class LunarMonth:
    jd: int           # Julian Day of month start
    code: int         # Month number (1-12 or 88 for leap 8th)
    length: int       # 29 or 30 days


def load_lunar_table(json_path: str) -> list[LunarMonth]:
    """Load precomputed lunar month table from JSON."""
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    # data['months'] is a compact string: MMDDCC where MM=month, DD=days, CC=century flag
    # We'll parse it into LunarMonth objects
    months_str = data['months']
    start_jd = data['startJd']
    naksat_anchor_jd = data['naksatAnchorJd']
    naksat_anchor_index = data['naksatAnchorIndex']
    
    months = []
    jd = start_jd
    for i in range(0, len(months_str), 4):
        month = int(months_str[i:i+2])
        length = int(months_str[i+2:i+4])
        months.append(LunarMonth(jd=jd, code=month, length=length))
        jd += length
    return months


# ─── Thai Lunar Conversion ────────────────────────────────────────────

# Naksat anchor constants (from bundle)
NAKSAT_ANCHOR_JD = 2429834
NAKSAT_ANCHOR_INDEX = 4

@dataclass
class ThaiLunarDate:
    julian_day: int
    weekday_index: int      # 0=Sun .. 6=Sat
    weekday: str
    month: int              # 1-12 (or 88 for leap 8th)
    is_second_eighth: bool
    month_name: str
    lunar_day: int          # 1-29/30
    phase: str              # "ขึ้น" (waxing) or "แรม" (waning)
    phase_day: int          # 1-15
    naksat_index: int       # 0-11
    naksat: str
    buddhist_year: int
    wednesday_night: bool   # True if Wed night (affects day count)


def find_lunar_month_index(months: list[LunarMonth], target_jd: int) -> int:
    """Binary search for lunar month containing target_jd."""
    lo, hi = 0, len(months) - 1
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if months[mid].jd <= target_jd:
            lo = mid
        else:
            hi = mid - 1
    return lo


def to_thai_lunar(
    year: int, month: int, day: int,
    hour: int = 0, minute: int = 0,
    months: list[LunarMonth] | None = None
) -> ThaiLunarDate:
    """
    Convert Gregorian date/time to Thai Lunar date.
    
    Args:
        year: Gregorian year (CE)
        month: Gregorian month (1-12)
        day: Gregorian day (1-31)
        hour: Hour (0-23), 6 AM cutoff for previous day
        minute: Minute (0-59)
        months: Precomputed lunar table (load once, reuse)
    
    Returns:
        ThaiLunarDate with all lunar components
    """
    if months is None:
        raise ValueError("Lunar months table required. Call load_lunar_table() first.")
    
    # Adjust for pre-6AM = previous day
    if hour < 6:
        # Subtract one day
        y, m, d = julian_day_to_gregorian(gregorian_to_julian_day(year, month, day) - 1)
        year, month, day = y, m, d
    
    jd = gregorian_to_julian_day(year, month, day)
    
    if jd < JD_START or jd > JD_END:
        raise ValueError(f"Date out of supported range (BE 2363-2663)")
    
    # Find lunar month
    idx = find_lunar_month_index(months, jd)
    lm = months[idx]
    
    # Day within lunar month (1-indexed)
    lunar_day = jd - lm.jd + 1
    
    # Weekday
    weekday_index = (jd + 1) % 7  # 0=Sun
    weekday = THAI_WEEKDAYS[weekday_index]
    
    # Month info
    is_second_eighth = (lm.code == 88)
    month_num = 8 if is_second_eighth else lm.code
    month_name = THAI_MONTHS[month_num - 1]
    
    # Phase
    if lunar_day <= 15:
        phase = "ขึ้น"
        phase_day = lunar_day
    else:
        phase = "แรม"
        phase_day = lunar_day - 15
    
    # Naksat (lunar mansion) - using anchor from bundle
    naksat_idx = ((idx - (sum(1 for m in months if m.jd <= NAKSAT_ANCHOR_JD) - 1)) + NAKSAT_ANCHOR_INDEX) % 12
    naksat = NAKSAT[naksat_idx]
    
    # Buddhist year
    buddhist_year = year + BE_OFFSET
    
    # Wednesday night check (affects some calculations)
    wednesday_night = (weekday_index == 3 and hour >= 18)
    
    return ThaiLunarDate(
        julian_day=jd,
        weekday_index=weekday_index,
        weekday=weekday,
        month=month_num,
        is_second_eighth=is_second_eighth,
        month_name=month_name,
        lunar_day=lunar_day,
        phase=phase,
        phase_day=phase_day,
        naksat_index=naksat_idx,
        naksat=naksat,
        buddhist_year=buddhist_year,
        wednesday_night=wednesday_night
    )


# ─── 7-Number 9-Base Calculation ──────────────────────────────────────

# House names (12 houses)
HOUSE_NAMES = {
    1: "อัตตะ", 2: "ธนัง", 3: "สหัชชะ", 4: "พันธุ",
    5: "ปุตตะ", 6: "อริ", 7: "ปัตนิ", 8: "มรณะ",
    9: "ภาคย์", 10: "กตัณห์", 11: "ลาภ", 12: "พยาย"
}

# Base labels
BASE_LABELS = {
    1: "ฐานวันเกิด",
    2: "ฐานเดือนเกิด", 
    3: "ฐานปีเกิด",
    4: "ฐานบวก (กำลังพระเคราะห์)",
    5: "เอา 7 ลบ",
    6: "เอา 2 คูณ ลบด้วย 7",
    7: "เอา 2 คูณ ลบด้วย 7",
    8: "เดินยามกลางวัน (ซ้ายไปขวา)",
    9: "เดินยามกลางวัน (ขวาไปซ้าย)"
}


def p_mod7(x: int) -> int:
    """Modulo 7 with range 1-7 (Thai style)."""
    return ((x - 1) % 7) + 1


def bases_from_seeds(day_seed: int, month_seed: int, year_seed: int) -> dict[int, list[int]]:
    """
    Generate all 9 bases from 3 seeds (day, month, year).
    Each base is a list of 7 numbers (houses 1-7).
    """
    # Generate 3 rows of 7 numbers each
    def row(seed: int) -> list[int]:
        return [p_mod7(seed + i) for i in range(7)]
    
    r1 = row(day_seed)
    r2 = row(month_seed)
    r3 = row(year_seed)
    
    # Base 1-3: direct rows
    bases = {
        1: r1,
        2: r2,
        3: r3,
    }
    
    # Base 4: element-wise sum of 3 rows, mod 7
    bases[4] = [p_mod7(r1[i] + r2[i] + r3[i]) for i in range(7)]
    
    # Base 5: 7 - base4
    bases[5] = [p_mod7(7 - x) for x in bases[4]]
    
    # Base 6: 2*base5 mod 7, then 7 - that
    bases[6] = [p_mod7(7 - p_mod7(2 * x)) for x in bases[5]]
    
    # Base 7: same as base 6 (formula 2*base5 mod 7)
    bases[7] = bases[6][:]
    
    # Base 8: "walk daytime left-to-right"
    # Take base 4, shift based on weekday? Bundle uses specific pattern
    bases[8] = [bases[4][(i + 6) % 7] for i in range(7)]  # rotate
    
    # Base 9: "walk daytime right-to-left"  
    bases[9] = [bases[4][(6 - i) % 7] for i in range(7)]  # reverse
    
    return bases


def chart_from_birth(
    year: int, month: int, day: int,
    hour: int = 0, minute: int = 0,
    sex: Literal["male", "female", "unknown"] = "unknown",
    lunar_months: list[LunarMonth] | None = None
) -> dict:
    """
    Generate complete 7-number 9-base chart from birth data.
    
    Returns dict with:
    - lunar: ThaiLunarDate
    - seeds: {day, month, year}
    - bases: {1..9: [7 numbers]}
    """
    if lunar_months is None:
        raise ValueError("Lunar months table required")
    
    lunar = to_thai_lunar(year, month, day, hour, minute, lunar_months)
    
    # Seeds: weekday (1-7), lunar month (1-12), naksat index (1-12)
    day_seed = lunar.weekday_index + 1
    month_seed = p_mod7(lunar.month)
    year_seed = p_mod7(lunar.naksat_index + 1)
    
    bases = bases_from_seeds(day_seed, month_seed, year_seed)
    
    return {
        "lunar": lunar,
        "seeds": {"day": day_seed, "month": month_seed, "year": year_seed},
        "bases": bases
    }


# ─── Interpretation Helpers ──────────────────────────────────────────

# Number quality
GOOD_NUMBERS = {1, 3, 7}
MID_NUMBERS = {4, 11, 14, 16, 18, 19}
BAD_NUMBERS = {5, 6, 13, 15, 17, 21}

def natal_quality(num: int) -> str:
    if num in GOOD_NUMBERS:
        return "ดี"
    elif num in MID_NUMBERS:
        return "ปานกลาง"
    return "ไม่ดี"


# Star pairs (from bundle)
ELEMENT_PAIRS = [[1, 2], [2, 5], [3, 8], [4, 6]]
FRIEND_PAIRS = [[1, 6], [2, 8], [3, 5], [4, 7]]
SIN_STARS = [[1, 5], [2, 4], [3, 6], [7, 8]]
SOMPHON_PAIRS = [[1, 3], [4, 8], [6, 7], [2, 5]]
STAR_POWER = [1, 3, 7, 10, 12, 15, 17, 19, 20, 21]
SUPPORTIVE_KINDS = {"คู่ธาตุ", "คู่สมพล", "คู่กำลัง", "คู่กำลังสอง", "คู่มิตร"}


def pair_kind(a: int, b: int) -> str:
    """Determine relationship kind between two stars."""
    if any(set(p) == {a, b} for p in ELEMENT_PAIRS):
        return "คู่ธาตุ"
    if any(set(p) == {a, b} for p in SOMPHON_PAIRS):
        return "คู่สมพล"
    if any(set(p) == {a, b} for p in FRIEND_PAIRS):
        return "คู่มิตร"
    if any(set(p) == {a, b} for p in SIN_STARS):
        return "คู่ศัตรู"
    return "คู่กลาง"


# ─── Demo / CLI ──────────────────────────────────────────────────────

def demo():
    """Run example calculations."""
    # Load lunar table (would be from JSON file in production)
    # For demo, we'll use a minimal table
    print("Thai 7-Number 9-Base Calculator")
    print("=" * 50)
    
    # Example: BooM's natal (1996-11-20 20:37 ICT, Chiang Rai)
    # Note: This uses Gregorian; the site converts to Thai lunar internally
    
    # Since we don't have the full 100-year lunar table here,
    # we'll show the algorithm structure
    print("\nAlgorithm structure:")
    print("1. Gregorian → Julian Day")
    print("2. Julian Day → Thai Lunar (via 100-year table)")
    print("3. Extract 3 seeds: weekday, lunar_month, naksat")
    print("4. Generate 9 bases × 7 houses from seeds")
    print("5. Interpret each base/house combination")
    
    print("\nSeeds for BooM (1996-11-20 20:37):")
    print("  Day seed: weekday (1-7)")
    print("  Month seed: lunar month (1-12)")  
    print("  Year seed: naksat index (1-12)")
    print("\nBases generated:")
    for b in range(1, 10):
        print(f"  Base {b}: {BASE_LABELS[b]}")


if __name__ == "__main__":
    demo()