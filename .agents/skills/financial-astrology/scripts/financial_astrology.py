#!/usr/bin/env python3
"""
Financial Astrology v4 — Financial Astrology (Day Trading Focus M15/H1)
=========================================================================
Features:
- Moon position, Nakshatra, Pada, House
- Moon-Planet combinations (Chandra-Mangal, Vish Yoga, Grahan Yoga, etc.)
- Moon aspects (all aspects affecting the Moon)
- Combustion detection + Cazimi
- All major aspects between planets
- Nakshatra trading quality (favorable/unfavorable)
- Gandanta detection
- Sector-specific analysis (Gold, Bitcoin)
- Day trading signal summary
- 🆕 PLANETARY HOURS — Chaldean order, sunrise/sunset based
  Location: Japan (Asia/Tokyo, UTC+9) — default lat/lon for Hekinan

System: Sidereal (Nirayana) - Ayanamsa Lahiri
House System: Whole Sign (Vedic)
"""

import sys
import argparse
import json
import swisseph as swe
from datetime import datetime, timezone
from zoneinfo import ZoneInfo


# ============================================================
# DATA
# ============================================================

# ============================================================
# PLANETARY HOURS — Chaldean Order
# ============================================================
# Chaldean order: Saturn → Jupiter → Mars → Sun → Venus → Mercury → Moon
# (by apparent speed, slow → fast: Saturn 29y, Jupiter 12y, Mars 2y, Sun 1y, Venus 220d, Mercury 88d, Moon 27d)

CHALDEAN_ORDER = ['Saturn', 'Jupiter', 'Mars', 'Sun', 'Venus', 'Mercury', 'Moon']

# Day lord for each day of the week
# Python weekday(): Mon=0, Tue=1, Wed=2, Thu=3, Fri=4, Sat=5, Sun=6
DAY_LORDS = {
    0: 'Moon',    # Monday
    1: 'Mars',    # Tuesday
    2: 'Mercury', # Wednesday
    3: 'Jupiter', # Thursday
    4: 'Venus',   # Friday
    5: 'Saturn',  # Saturday
    6: 'Sun',     # Sunday
}

DAY_NAMES_VN = {
    0: 'Monday', 1: 'Tuesday', 2: 'Wednesday', 3: 'Thursday',
    4: 'Friday', 5: 'Saturday', 6: 'Sunday',
}

# Hora meaning for Trading
HORA_TRADING = {
    'Sun': {
        'emoji': '☀️',
        'name': 'Hour of the Sun',
        'bias': 'BULLISH — Stable uptrend',
        'assets': 'Gold (XAU), Blue-chip stocks, Government bonds',
        'strategy': 'Buy dips, hold positions, Gold strong',
        'warning': 'Avoid overconfidence, no FOMO at the top',
    },
    'Moon': {
        'emoji': '🌙',
        'name': 'Hour of the Moon',
        'bias': 'NEUTRAL → High emotion',
        'assets': 'Silver (XAG), Consumer stocks, Real estate, High liquidity',
        'strategy': 'Watch sentiment shifts, quick in-out, tight SL',
        'warning': 'Market emotion is volatile, prone to false breakouts',
    },
    'Mercury': {
        'emoji': '☿️',
        'name': 'Hour of Mercury',
        'bias': 'HIGH VOLATILITY — Whipsaws',
        'assets': 'Tech stocks, IT, Telecom, Crypto, Brokerage',
        'strategy': 'Scalping, quick trades, range trading',
        'warning': 'Many false signals, do not hold overnight, tight SL',
    },
    'Venus': {
        'emoji': '♀️',
        'name': 'Hour of Venus',
        'bias': 'BULLISH — Risk-on',
        'assets': 'Gold (XAU), Luxury stocks, Consumer, Art, Beauty',
        'strategy': 'Buy dips, trend following, Gold/XAU good',
        'warning': 'Avoid over-leverage when the market is too optimistic',
    },
    'Mars': {
        'emoji': '♂️',
        'name': 'Hour of Mars',
        'bias': 'AGGRESSIVE — High volatility',
        'assets': 'Defense, Energy, Metals, Real estate, Oil/Gas',
        'strategy': 'Momentum trading, breakout trades, aggressive entry',
        'warning': '⚠️ HIGH risk — Prone to panic selling, tight SL mandatory',
    },
    'Jupiter': {
        'emoji': '♃',
        'name': 'Hour of Jupiter',
        'bias': 'BULLISH — Expansion',
        'assets': 'Banking, Finance, Education, FMCG, Index funds',
        'strategy': 'Position trading, swing trade, buy and hold',
        'warning': 'Avoid over-optimism, always have an exit plan',
    },
    'Saturn': {
        'emoji': '♄',
        'name': 'Hour of Saturn',
        'bias': 'BEARISH → Conservative',
        'assets': 'Infrastructure, Mining, Cement, Utilities, Bonds',
        'strategy': 'Sell on rise, reduce position, cash is king, hedge',
        'warning': '⚠️ Slow market, range-bound — avoid fresh long',
    },
}

# Hora ruler per hour — meaning for Gold (XAU/USD)
HORA_GOLD = {
    'Sun': '☀️ Gold strong — Stable safe haven demand, uptrend',
    'Moon': '🌙 Gold volatile — Driven by emotion, watch silver correlation',
    'Mercury': '☿️ Gold sideways — Whipsaws, range trading',
    'Venus': '♀️ Gold GOOD — Risk-on, Gold attractive, buy dips',
    'Mars': '♂️ Gold HIGHLY volatile — Can spike up/down suddenly',
    'Jupiter': '♃ Gold rising — Expansion, banking sector support',
    'Saturn': '♄ Gold weak/slow — Correction, consolidation',
}

# Hora ruler per hour — meaning for Bitcoin (BTC/USD)
HORA_BTC = {
    'Sun': '☀️ BTC stable — Institutional interest',
    'Moon': '🌙 BTC volatile — Retail sentiment shifts',
    'Mercury': '☿️ BTC VERY ACTIVE — High trading volume, good for scalping',
    'Venus': '♀️ BTC bullish — High risk appetite, altcoin season potential',
    'Mars': '♂️ BTC AGGRESSIVE — Breakout or crash, very volatile',
    'Jupiter': '♃ BTC rising — Expansion, adoption news',
    'Saturn': '♄ BTC slow — Consolidation, accumulation phase',
}

NAKSHATRA_27 = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira",
    "Ardra", "Punarvasu", "Pushya", "Ashlesha", "Magha",
    "Purva Phalguni", "Uttara Phalguni", "Hasta", "Chitra", "Swati",
    "Vishakha", "Anuradha", "Jyeshtha", "Mula", "Purva Ashadha",
    "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha",
    "Purva Bhadrapada", "Uttara Bhadrapada", "Revati",
]

NAKSHATRA_LORDS = [
    "Ketu", "Venus", "Sun", "Moon", "Mars",
    "Rahu", "Jupiter", "Saturn", "Mercury", "Ketu",
    "Venus", "Sun", "Moon", "Mars", "Rahu",
    "Jupiter", "Saturn", "Mercury", "Ketu", "Venus",
    "Sun", "Moon", "Mars", "Rahu", "Jupiter",
    "Saturn", "Mercury",
]

NAKSHATRA_SYMBOLS = [
    "🐴", "🔥", "🔪", "🐂", "🦌",
    "🌊", "🏠", "🌸", "🐍", "👑",
    "🛏️", "🛏️", "✋", "🎨", "🌱",
    "🎯", "🌟", "🪖", "🌿", "🌊",
    "👑", "🔥", "🐘", "🐍",
    "🔥", "🐘", "🐟",
]

# Nakshatra trading quality
NAKSHATRA_TRADE = {
    "Ashwini": ("✅ Good", "Intraday, quick trades"),
    "Pushya": ("✅✅ Very good", "Investment, wealth building"),
    "Rohini": ("✅ Good", "Profit-oriented, growth"),
    "Uttara Phalguni": ("✅ Good", "Strategic planning"),
    "Hasta": ("✅ Good", "Swing trading, precision"),
    "Ardra": ("❌ Avoid", "Emotional volatility"),
    "Mula": ("❌ Avoid", "Destructive energy"),
    "Ashlesha": ("❌ Avoid", "Hidden motives, confusion"),
}

ZODIAC_SIGNS = [
    "♈ Aries", "♉ Taurus", "♊ Gemini",
    "♋ Cancer", "♌ Leo", "♍ Virgo",
    "♎ Libra", "♏ Scorpio", "♐ Sagittarius",
    "♑ Capricorn", "♒ Aquarius", "♓ Pisces",
]

ELEMENT_NAMES = ["Fire", "Earth", "Air", "Water"]
QUALITY_NAMES_VN = ["Movable", "Fixed", "Mutable"]

HOUSE_MEANINGS = {
    1: "Lagna - Self, beginnings",
    2: "Dhana - Finances, accumulation",
    3: "Sahaja - Communication, effort",
    4: "Sukha - Home, foundations",
    5: "Putra - Speculation, luck",
    6: "Shatru - Conflict, service",
    7: "Kalatra - Partners, business",
    8: "Randhara - Crises, research",
    9: "Dharma - Fortune, ethics",
    10: "Karma - Career, reputation",
    11: "Labha - Profits, income",
    12: "Vyaya - Losses, expenses",
}

BODIES = {
    'Moon': swe.MOON,
    'Sun': swe.SUN,
    'Mercury': swe.MERCURY,
    'Venus': swe.VENUS,
    'Mars': swe.MARS,
    'Jupiter': swe.JUPITER,
    'Saturn': swe.SATURN,
    'Rahu': swe.TRUE_NODE,
}

BODY_NAMES = {
    'Moon': '🌙 Moon (Chandra)',
    'Sun': '☀️ Sun (Surya)',
    'Mercury': '☿️ Mercury (Budha)',
    'Venus': '♀️ Venus (Shukra)',
    'Mars': '♂️ Mars (Mangala)',
    'Jupiter': '♃ Jupiter (Guru)',
    'Saturn': '♄ Saturn (Shani)',
    'Rahu': '🐉 Rahu (North Node)',
    'Ketu': '🔻 Ketu (South Node)',
    'Uranus': '⛧ Uranus',
    'Neptune': '♆ Neptune',
    'Pluto': '♇ Pluto',
}

# SHORT names for display
SHORT_NAMES = {
    'Moon': 'Moon', 'Sun': 'Sun', 'Mercury': 'Mercury',
    'Venus': 'Venus', 'Mars': 'Mars', 'Jupiter': 'Jupiter', 'Saturn': 'Saturn',
    'Rahu': 'Rahu', 'Ketu': 'Ketu',
    'Uranus': 'Uranus', 'Neptune': 'Neptune', 'Pluto': 'Pluto',
}

# Aspects
ASPECTS = {
    'Conjunction': {'angle': 0, 'orb': 8, 'symbol': '☌', 'type': 'major'},
    'Sextile': {'angle': 60, 'orb': 6, 'symbol': '⚹', 'type': 'major'},
    'Square': {'angle': 90, 'orb': 7, 'symbol': '□', 'type': 'major'},
    'Trine': {'angle': 120, 'orb': 8, 'symbol': '△', 'type': 'major'},
    'Opposition': {'angle': 180, 'orb': 8, 'symbol': '☍', 'type': 'major'},
    'Quincunx': {'angle': 150, 'orb': 3, 'symbol': '⚻', 'type': 'minor'},
    'Semi-Square': {'angle': 45, 'orb': 2.5, 'symbol': '∠', 'type': 'minor'},
    'Sesquiquadrate': {'angle': 135, 'orb': 2.5, 'symbol': '⚼', 'type': 'minor'},
}

# Combustion orbs — rules set by Minh (stricter than the Vedic standard)
# Source: COMBUSTION_RULES.md
COMBUST_ORBS = {
    'Mercury': 2, 'Venus': 5, 'Mars': 10, 'Jupiter': 10, 'Saturn': 10,
}
CAZIMI_ORB = 0.2833  # 17 minutes = 0.2833°

# Nakshatra span (360° / 27 nakshatras)
NAKSHATRA_SPAN = 360.0 / 27.0  # 13°20'

# ============================================================
# DASHA DATA (Vimshottari Dasha - 120-year cycle)
# ============================================================

DASHA_YEARS = {
    'Ketu': 7, 'Venus': 20, 'Sun': 6, 'Moon': 10,
    'Mars': 7, 'Rahu': 18, 'Jupiter': 16, 'Saturn': 19, 'Mercury': 17,
}

DASHA_ORDER = ['Ketu', 'Venus', 'Sun', 'Moon', 'Mars', 'Rahu', 'Jupiter', 'Saturn', 'Mercury']

DASHA_MEANINGS = {
    'Ketu': "🔻 Spirituality, deep research, detachment from the material, liberation",
    'Venus': "♀️ Finances, art, love, comfort, beauty",
    'Sun': "☀️ Fame, career, power, parents, leadership",
    'Moon': "🌙 Emotions, family, home, the public, intuition",
    'Mars': "♂️ Energy, conflict, real estate, engineering, sports",
    'Rahu': "🐉 Ambition, breakthroughs, risk, foreign countries, technology",
    'Jupiter': "♃ Luck, education, finances, expansion, wisdom",
    'Saturn': "♄ Discipline, challenges, slow but steady, karma",
    'Mercury': "☿️ Communication, business, academia, art, analysis",
}


# ============================================================
# UTILITY FUNCTIONS
# ============================================================

def angle_diff(a, b):
    diff = abs(a - b) % 360
    return min(diff, 360 - diff)

def get_nakshatra(longitude):
    span = 360.0 / 27.0
    pada_span = span / 4.0
    idx = int(longitude / span) % 27
    pos = longitude % span
    pada = int(pos / pada_span) + 1
    return idx, NAKSHATRA_27[idx], pada, NAKSHATRA_LORDS[idx], NAKSHATRA_SYMBOLS[idx]

def get_house(planet_lon, asc_lon):
    asc_sign = int(asc_lon / 30) % 12
    p_sign = int(planet_lon / 30) % 12
    return (p_sign - asc_sign + 12) % 12 + 1

def decimal_to_dms(deg):
    d = int(deg)
    m = int((deg - d) * 60)
    s = int(((deg - d) * 60 - m) * 60)
    return d, m, s

def get_sign_info(lon):
    si = int(lon / 30) % 12
    sd = lon % 30
    return si, sd, ELEMENT_NAMES[si % 4], QUALITY_NAMES_VN[si % 3]

def is_gandanta(lon):
    """Check for Gandanta (last 2° of water signs ↔ first 2° of fire signs)."""
    si = int(lon / 30) % 12
    sd = lon % 30
    # Water signs: 3 (Cancer), 7 (Scorpio), 11 (Pisces)
    # Fire signs: 0 (Aries), 4 (Leo), 8 (Sagittarius)
    water_last = si in [3, 7, 11] and sd > 28
    fire_first = si in [0, 4, 8] and sd < 2
    return water_last or fire_first


# ============================================================
# PLANETARY HOURS CALCULATION
# ============================================================

def get_sunrise_sunset(jd_start, lat, lon):
    """Calculate sunrise, sunset, next_sunrise, prev_sunset using Swiss Ephemeris.
    
    Returns: (sunrise_jd, sunset_jd, next_sunrise_jd, prev_sunset_jd)
    All JDs are in UTC.
    - sunrise_jd: sunrise of the JST date
    - sunset_jd: sunset AFTER sunrise (same JST date)
    - next_sunrise_jd: sunrise of the next day
    - prev_sunset_jd: sunset BEFORE sunrise (the night before the JST date)
    """
    geopos = (lon, lat, 0.0)
    
    # Sunrise today (JST date)
    _, tret = swe.rise_trans(jd_start, swe.SUN, swe.CALC_RISE, geopos)
    sunrise_jd = tret[0]
    
    # Sunset today (after sunrise)
    _, tret = swe.rise_trans(sunrise_jd + 0.01, swe.SUN, swe.CALC_SET, geopos)
    sunset_jd = tret[0]
    
    # Sunrise tomorrow
    _, tret = swe.rise_trans(sunset_jd + 0.01, swe.SUN, swe.CALC_RISE, geopos)
    next_sunrise_jd = tret[0]
    
    # Sunset BEFORE sunrise (search back from before sunrise)
    _, tret = swe.rise_trans(sunrise_jd - 1.0, swe.SUN, swe.CALC_SET, geopos)
    prev_sunset_jd = tret[0]
    
    return sunrise_jd, sunset_jd, next_sunrise_jd, prev_sunset_jd


def calculate_planetary_hours(dt_utc, lat, lon):
    """Calculate the Planetary Hours (Hora) for the current day.
    
    Rules:
    - The day starts at sunrise → split into 12 daytime hours
    - Night runs from sunset → next sunrise → split into 12 nighttime hours
    - The first hour of the day belongs to that day's ruler
    - Subsequent hours follow the Chaldean order: Saturn → Jupiter → Mars → Sun → Venus → Mercury → Moon
    
    Returns: dict with current_planet, current_hora_num, is_daytime,
             sunrise_jst, sunset_jst, and the full 24-hour list
    """
    from datetime import datetime, timedelta
    from zoneinfo import ZoneInfo
    
    # Use Asia/Tokyo timezone (JST = UTC+9)
    tz = ZoneInfo('Asia/Tokyo')
    
    # Convert UTC to JST
    dt_utc_naive = dt_utc.replace(tzinfo=None)
    dt_jst = datetime(dt_utc_naive.year, dt_utc_naive.month, dt_utc_naive.day,
                      dt_utc.hour, dt_utc.minute, dt_utc.second, tzinfo=tz)
    # Actually convert properly
    dt_utc_aware = dt_utc.replace(tzinfo=timezone.utc)
    dt_jst = dt_utc_aware.astimezone(tz)
    
    # JD at local midnight (00:00 JST) — NOT 00:00 UTC!
    # This is critical: we need the JD of 00:00 in the LOCAL timezone
    local_midnight = datetime(dt_jst.year, dt_jst.month, dt_jst.day, tzinfo=tz)
    local_midnight_utc = local_midnight.astimezone(timezone.utc)
    jd_midnight = swe.julday(
        local_midnight_utc.year, local_midnight_utc.month, local_midnight_utc.day,
        local_midnight_utc.hour + local_midnight_utc.minute / 60.0 + local_midnight_utc.second / 3600.0,
        cal=swe.GREG_CAL
    )
    
    # Current JD
    now_jd = swe.julday(dt_utc.year, dt_utc.month, dt_utc.day,
                        dt_utc.hour + dt_utc.minute / 60.0 + dt_utc.second / 3600.0,
                        cal=swe.GREG_CAL)
    
    # Sunrise/Sunset for today (local date)
    sunrise_jd, sunset_jd, next_sunrise_jd, prev_sunset_jd = get_sunrise_sunset(jd_midnight, lat, lon)
    
    # Day of week — VEDIC FIX: Day starts at sunrise, not midnight
    # If before sunrise, use previous day's lord
    if now_jd < sunrise_jd:
        # Before sunrise → still yesterday's Vedic day
        effective_date = dt_jst - timedelta(days=1)
    else:
        effective_date = dt_jst
    
    # Python weekday: Mon=0, Sun=6
    # Map to DAY_LORDS: 6=Sun, 0=Mon, 1=Tue, 2=Wed, 3=Thu, 4=Fri, 5=Sat
    dow = effective_date.weekday()  # Mon=0...Sun=6
    day_lord = DAY_LORDS[dow]
    day_name = DAY_NAMES_VN[dow]
    
    # Determine which sunset to use for night hours
    if now_jd < sunrise_jd:
        night_sunset_jd = prev_sunset_jd
        night_sunrise_jd = sunrise_jd
    else:
        night_sunset_jd = sunset_jd
        night_sunrise_jd = next_sunrise_jd
    
    # Day/night lengths
    day_length_hours = (sunset_jd - sunrise_jd) * 24
    night_length_hours = (night_sunrise_jd - night_sunset_jd) * 24
    day_hour_len = day_length_hours / 12  # per daytime hour
    night_hour_len = night_length_hours / 12  # per nighttime hour
    
    # Convert JD to local timezone string
    def jd_to_local_str(jd):
        y, m, d, hour = swe.revjul(jd, swe.GREG_CAL)
        h = int(hour)
        m_rem = (hour - h) * 60
        mi = int(m_rem)
        s = int((m_rem - mi) * 60)
        dt_utc_raw = datetime(int(y), int(m), int(d), h, mi, s, tzinfo=timezone.utc)
        dt_local = dt_utc_raw.astimezone(tz)
        return f"{dt_local.hour:02d}:{dt_local.minute:02d}"
    
    # Build 24 planetary hours list
    hours_list = []
    
    # === 12 Daytime hours (sunrise → sunset) ===
    for i in range(12):
        h_start_jd = sunrise_jd + i * (day_hour_len / 24.0)
        h_end_jd = sunrise_jd + (i + 1) * (day_hour_len / 24.0)
        
        # Planet: start from day_lord, follow Chaldean order
        planet_idx = (CHALDEAN_ORDER.index(day_lord) + i) % 7
        planet = CHALDEAN_ORDER[planet_idx]
        
        hours_list.append({
            'num': i + 1,
            'period': 'day',
            'planet': planet,
            'start_jst': jd_to_local_str(h_start_jd),
            'end_jst': jd_to_local_str(h_end_jd),
            'start_jd': h_start_jd,
            'end_jd': h_end_jd,
        })
    
    # === 12 Nighttime hours (sunset → next sunrise) ===
    # Night hours CONTINUE from where day hours ended (not restart)
    night_start_idx = (CHALDEAN_ORDER.index(day_lord) + 12) % 7
    for i in range(12):
        h_start_jd = night_sunset_jd + i * (night_hour_len / 24.0)
        h_end_jd = night_sunset_jd + (i + 1) * (night_hour_len / 24.0)
        
        planet_idx = (night_start_idx + i) % 7
        planet = CHALDEAN_ORDER[planet_idx]
        
        hours_list.append({
            'num': i + 13,
            'period': 'night',
            'planet': planet,
            'start_jst': jd_to_local_str(h_start_jd),
            'end_jst': jd_to_local_str(h_end_jd),
            'start_jd': h_start_jd,
            'end_jd': h_end_jd,
        })
    
    # Find current planetary hour
    current_hora = None
    for h in hours_list:
        if h['start_jd'] <= now_jd < h['end_jd']:
            current_hora = h
            break
    
    # Fallback: if still not found, find closest hour
    if current_hora is None:
        for h in hours_list:
            if h['start_jd'] <= now_jd:
                current_hora = h
        if current_hora is None:
            current_hora = hours_list[0]
    
    result = {
        'day_name': day_name,
        'day_lord': day_lord,
        'dow': dow,
        'sunrise_jst': jd_to_local_str(sunrise_jd),
        'sunset_jst': jd_to_local_str(sunset_jd),
        'day_length_hours': round(day_length_hours, 2),
        'night_length_hours': round(night_length_hours, 2),
        'day_hour_minutes': round(day_hour_len * 60, 0),
        'night_hour_minutes': round(night_hour_len * 60, 0),
        'current_planet': current_hora['planet'] if current_hora else 'Unknown',
        'current_hora_num': current_hora['num'] if current_hora else 0,
        'current_period': current_hora['period'] if current_hora else 'unknown',
        'hours': hours_list,
    }
    
    return result


# ============================================================
# DASHA CALCULATION (Vimshottari Dasha)
# ============================================================

def calculate_dasha(moon_lon, jd_utc):
    """Calculate the Vimshottari Dasha sequence from the Moon position."""
    from datetime import datetime, timedelta
    
    # Moon's Nakshatra
    nakshatra_idx = int(moon_lon / NAKSHATRA_SPAN) % 27
    nakshatra_name = NAKSHATRA_27[nakshatra_idx]
    nakshatra_lord = NAKSHATRA_LORDS[nakshatra_idx]
    
    # Position within Nakshatra
    pos_in_nakshatra = moon_lon % NAKSHATRA_SPAN
    remaining_fraction = 1.0 - (pos_in_nakshatra / NAKSHATRA_SPAN)
    
    # Build Dasha sequence
    dasha_sequence = []
    start_idx = DASHA_ORDER.index(nakshatra_lord)
    ordered_planets = DASHA_ORDER[start_idx:] + DASHA_ORDER[:start_idx]
    
    current_jd = jd_utc
    
    for i, lord in enumerate(ordered_planets):
        years = DASHA_YEARS[lord]
        
        # For first Dasha, only remaining portion
        if i == 0:
            effective_years = years * remaining_fraction
        else:
            effective_years = years
        
        # Convert JD to date
        start_date = datetime(1, 1, 1) + timedelta(days=current_jd - 1721425.5)
        end_date = start_date + timedelta(days=effective_years * 365.25)
        
        dasha_sequence.append({
            'lord': lord,
            'years': years,
            'effective_years': round(effective_years, 2),
            'start': start_date.strftime('%Y-%m-%d'),
            'end': end_date.strftime('%Y-%m-%d'),
            'jd_start': current_jd,
            'jd_end': current_jd + effective_years * 365.25,
        })
        
        current_jd += effective_years * 365.25
    
    return {
        'moon_nakshatra': nakshatra_name,
        'nakshatra_lord': nakshatra_lord,
        'remaining_fraction': round(remaining_fraction * 100, 1),
        'sequence': dasha_sequence,
    }


def get_current_dasha(dasha_data, current_jd):
    """Find the current Dasha."""
    for d in dasha_data['sequence']:
        if d['jd_start'] <= current_jd <= d['jd_end']:
            return d
    return None


def get_antardasha(dasha_data, current_jd):
    """Calculate the Antardasha (sub-period) within the current Dasha."""
    from datetime import datetime, timedelta
    
    current_dasha = get_current_dasha(dasha_data, current_jd)
    if not current_dasha:
        return []
    
    lord = current_dasha['lord']
    dasha_start_jd = current_dasha['jd_start']
    
    # Sub-lords follow same order starting from main lord
    start_idx = DASHA_ORDER.index(lord)
    sub_order = DASHA_ORDER[start_idx:] + DASHA_ORDER[:start_idx]
    
    antardashas = []
    sub_jd = dasha_start_jd
    
    for sl in sub_order:
        sub_years = DASHA_YEARS[lord] * DASHA_YEARS[sl] / 120
        sub_end_jd = sub_jd + sub_years * 365.25
        
        sub_start_date = datetime(1, 1, 1) + timedelta(days=sub_jd - 1721425.5)
        sub_end_date = datetime(1, 1, 1) + timedelta(days=sub_end_jd - 1721425.5)
        
        antardashas.append({
            'lord': sl,
            'years': round(sub_years, 2),
            'start': sub_start_date.strftime('%Y-%m-%d'),
            'end': sub_end_date.strftime('%Y-%m-%d'),
            'is_current': sub_jd <= current_jd <= sub_end_jd,
        })
        
        sub_jd = sub_end_jd
    
    return antardashas


# ============================================================
# ASPECTS
# ============================================================

def calculate_aspects(bodies_data, outer_data=None):
    aspects_list = []
    all_b = dict(bodies_data)
    if outer_data:
        all_b.update(outer_data)
    
    names = list(all_b.keys())
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            n1, n2 = names[i], names[j]
            diff = angle_diff(all_b[n1]['lon'], all_b[n2]['lon'])
            
            for aname, ainfo in ASPECTS.items():
                angle = ainfo['angle']
                orb = ainfo['orb']
                target = abs(diff - angle)
                if target <= orb:
                    tight = target <= orb * 0.5
                    aspects_list.append({
                        'p1': n1, 'p2': n2,
                        'aspect': aname, 'symbol': ainfo['symbol'],
                        'diff': diff, 'orb': round(target, 2),
                        'tight': tight, 'type': ainfo['type'],
                    })
                    break
    return aspects_list


# ============================================================
# COMBUSTION
# ============================================================

def check_combustion(bodies_data):
    results = []
    sun_lon = bodies_data['Sun']['lon']
    
    for name, limit in COMBUST_ORBS.items():
        if name not in bodies_data:
            continue
        diff = angle_diff(sun_lon, bodies_data[name]['lon'])
        
        if diff <= CAZIMI_ORB:
            results.append({'planet': name, 'diff': round(diff, 2),
                          'status': 'CAZIMI ⚡',
                          'desc': f"{SHORT_NAMES.get(name, name)} Cazimi — extremely strong, concentrated energy"})
        elif diff <= limit:
            results.append({'planet': name, 'diff': round(diff, 2),
                          'status': 'COMBUST 🔥',
                          'desc': f"{SHORT_NAMES.get(name, name)} combust — {diff:.1f}° from the Sun"})
    return results


# ============================================================
# MOON-PLANET COMBINATIONS (Vedic Yoga)
# ============================================================

def get_moon_combinations(moon_lon, bodies_data):
    """Find which planet the Moon combines with (same sign or tight aspect)."""
    combos = []
    moon_sign = int(moon_lon / 30) % 12
    
    for name in ['Sun', 'Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn', 'Rahu', 'Ketu']:
        if name not in bodies_data or name == 'Moon':
            continue
        p_lon = bodies_data[name]['lon']
        p_sign = int(p_lon / 30) % 12
        
        # Same sign = conjunction
        if moon_sign == p_sign:
            diff = angle_diff(moon_lon, p_lon)
            combos.append({
                'planet': name,
                'type': 'Conjunction (same sign)',
                'diff': round(diff, 1),
            })
    
    # Check Nakshatra lord
    _, nak_name, _, nak_lord, _ = get_nakshatra(moon_lon)
    
    return combos, nak_lord


def interpret_moon_combination(planet_name, nakshatra_lord):
    """Interpret Moon + Planet combination."""
    interpretations = {
        'Sun': ("🌙☀️ Moon-Sun (Surya Yoga)", "Stable Uptrend — Steady rise, confidence, low volatility",
                     "Buy dips, Gold strong, government bonds"),
        'Mercury': ("🌙☿️ Moon-Mercury", "High Volatility — Whipsaws, constant ups and downs",
                 "Scalping, quick in-out, tight SL"),
        'Venus': ("🌙♀️ Moon-Venus", "Risk Appetite — Risk-on, consumer/luxury strong",
                "Growth stocks, consumer sector, trend following"),
        'Mars': ("🌙♂️ Chandra-Mangal Yoga 🐂", "Bull Run — Fast rise, high volume, aggressive bullish",
                "Buy on dips, momentum trading, defense/energy"),
        'Jupiter': ("🌙♃ Moon-Jupiter", "Expansion — Steady growth, banking rally, optimism",
                "Position trading, banking/finance, swing trade"),
        'Saturn': ("🌙♄ Vish Yoga 🐻", "Slow Bleed — Range-bound to negative, struggle at resistance",
                "Sell on rise, avoid fresh long, cash"),
        'Rahu': ("🌙🐉 Grahan Yoga 🕳️", "The Trap — High volatility, fake breakout, sudden spikes",
                 "Option buying (gamma), DO NOT hold overnight, tight SL"),
        'Ketu': ("🌙🔻 Ketu Panic 💥", "Panic Button — Sudden drop with no news, 'bottom falls out'",
                 "Hedge, shorting, defensive positioning"),
    }
    
    return interpretations.get(planet_name, (f"🌙 {SHORT_NAMES.get(planet_name, planet_name)}", "", ""))


# ============================================================
# MOON ASPECTS INTERPRETATION
# ============================================================

def interpret_moon_aspect(aspect_name, other_planet):
    """Interpret Moon aspect for trading."""
    key = (aspect_name, other_planet)
    
    # Specific interpretations
    specific = {
        ('Square', 'Mars'): "PANIC SELL / FOMO BUY — Very volatile ⚠️⚠️",
        ('Opposition', 'Mars'): "Bulls vs Bears — Battlefield, prone to reversals ⚠️",
        ('Square', 'Mercury'): "False signals — Contradictory information, confusion ⚠️",
        ('Opposition', 'Mercury'): "Market divergence — Whipsaws, sideways ⚠️",
        ('Square', 'Rahu'): "BLACK SWAN potential — Extremely strong volatility ⚠️⚠️⚠️",
        ('Opposition', 'Rahu'): "Major DISRUPTION — Fake moves, sudden spikes ⚠️⚠️⚠️",
        ('Trine', 'Jupiter'): "Strongly bullish — Expansion, steady growth ✅",
        ('Conjunction', 'Jupiter'): "Optimism — Steady growth, banking rally ✅",
        ('Sextile', 'Jupiter'): "Opportunity — Growth, good entry ✅",
        ('Square', 'Saturn'): "Fear + Greed — Polarized, correction ⚠️",
        ('Opposition', 'Saturn'): "Turning point — Extreme Fear vs Greed ⚠️",
        ('Trine', 'Venus'): "Stable risk-on — Bullish trend ✅",
        ('Conjunction', 'Venus'): "High risk appetite — Bullish sentiment ✅",
        ('Square', 'Venus'): "Choppy — Constant risk on/off ⚠️",
        ('Opposition', 'Venus'): "Bull/Bear polarity — Prone to reversals ⚠️",
        ('Trine', 'Sun'): "Stable bullish momentum ✅",
        ('Conjunction', 'Sun'): "New Moon energy — Start of a new cycle",
        ('Opposition', 'Sun'): "Full Moon — Emotional peak, reversal ⚠️",
        ('Trine', 'Mars'): "Strong buying momentum — Bullish momentum ✅",
        ('Sextile', 'Mars'): "Mildly bullish — Rising momentum ✅",
        ('Sextile', 'Mercury'): "Good information — Clear setup ✅",
        ('Trine', 'Mercury'): "Accurate analysis — Smooth trading ✅",
        ('Sextile', 'Saturn'): "Balanced risk — Calculated trade",
        ('Trine', 'Saturn'): "Orderly correction — Structured ✅",
        ('Sextile', 'Rahu'): "Favorable volatility — Opportunity ✅",
        ('Trine', 'Rahu'): "Positive disruption — New trend ✅",
        ('Sextile', 'Ketu'): "Potential breakout — Opportunity ✅",
        ('Trine', 'Ketu'): "Smooth transition — Smooth ✅",
    }
    
    if key in specific:
        return specific[key]
    
    # Generic
    generic = {
        'Conjunction': f"Unified energy — {SHORT_NAMES.get(other_planet, other_planet)} strongly influences the Moon",
        'Sextile': f"Harmonious — Opportunity from {SHORT_NAMES.get(other_planet, other_planet)}",
        'Square': f"Tension — Challenge from {SHORT_NAMES.get(other_planet, other_planet)} ⚠️",
        'Trine': f"Favorable — Good flow from {SHORT_NAMES.get(other_planet, other_planet)} ✅",
        'Opposition': f"Polarity — Turning point from {SHORT_NAMES.get(other_planet, other_planet)} ⚠️",
        'Quincunx': f"Adjustment — Mild instability from {SHORT_NAMES.get(other_planet, other_planet)}",
        'Semi-Square': f"Mild tension — Watch {SHORT_NAMES.get(other_planet, other_planet)}",
        'Sesquiquadrate': f"Friction — Watch {SHORT_NAMES.get(other_planet, other_planet)}",
    }
    return generic.get(aspect_name, f"{aspect_name} {SHORT_NAMES.get(other_planet, other_planet)}")


# ============================================================
# MOON PHASE
# ============================================================

def get_moon_phase(elongation):
    if elongation < 7:
        return "New Moon", "🌑 Start of a new cycle, low volatility — Wait for breakout"
    elif elongation < 83:
        return "Waxing Crescent", "🌒 Gradually optimistic, Bullish — Buy dips"
    elif 83 <= elongation <= 97:
        return "First Quarter", "🌓 Conflict, decision point — Watch reversal"
    elif elongation < 173:
        return "Waxing Gibbous", "🌔 High optimism, Bullish — Trend following"
    elif 173 <= elongation <= 187:
        return "Full Moon", "🌕 Emotional peak, HIGH VOLATILITY — Avoid overtrading"
    elif elongation < 263:
        return "Waning Gibbous", "🌖 Declining optimism, caution — Take profit"
    elif 263 <= elongation <= 277:
        return "Last Quarter", "🌗 Reassessment, volatility — Hedge"
    elif elongation < 353:
        return "Waning Crescent", "🌘 Pessimism, Bearish — Cash, short"
    else:
        return "New Moon", "🌑 Start of a new cycle, low volatility — Wait for breakout"


# ============================================================
# CALCULATE ALL
# ============================================================

def calculate_all(dt_utc, lat, lon, is_natal=False):
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    
    jd_ut = swe.julday(dt_utc.year, dt_utc.month, dt_utc.day,
                       dt_utc.hour + dt_utc.minute / 60.0 + dt_utc.second / 3600.0,
                       cal=swe.GREG_CAL)
    
    ayanamsa = swe.get_ayanamsa_ut(jd_ut)
    
    # Ascendant (sidereal)
    tropical_cusps, asmc = swe.houses(jd_ut, lat, lon, b'P')
    asc_sidereal = (tropical_cusps[0] - ayanamsa) % 360
    mc_sidereal = (tropical_cusps[10] - ayanamsa) % 360
    
    asc_si = int(asc_sidereal / 30) % 12
    asc_sd = asc_sidereal % 30
    asc_d, asc_m, asc_s = decimal_to_dms(asc_sd)
    mc_si = int(mc_sidereal / 30) % 12
    mc_sd = mc_sidereal % 30
    mc_d, mc_m, mc_s = decimal_to_dms(mc_sd)
    
    # Navagraha
    bodies = {}
    for name, bid in BODIES.items():
        r, _ = swe.calc_ut(jd_ut, bid, swe.FLG_SIDEREAL)
        p_lon, p_lat, dist, spd = r[0], r[1], r[2], r[3]
        si, sd, elem, qual = get_sign_info(p_lon)
        d, m, s = decimal_to_dms(sd)
        ni, nn, pa, nl, ns = get_nakshatra(p_lon)
        h = get_house(p_lon, asc_sidereal)
        
        bodies[name] = {
            'lon': p_lon, 'lat': p_lat, 'dist': dist, 'spd': spd,
            'si': si, 'sd': sd, 'd': d, 'm': m, 's': s,
            'sign': ZODIAC_SIGNS[si], 'elem': elem, 'qual': qual,
            'ni': ni, 'nak': nn, 'ns': ns, 'pada': pa, 'nl': nl, 'house': h,
        }
    
    # Ketu
    rahu_lon = bodies['Rahu']['lon']
    ketu_lon = (rahu_lon + 180) % 360
    si, sd, elem, qual = get_sign_info(ketu_lon)
    d, m, s = decimal_to_dms(sd)
    ni, nn, pa, nl, ns = get_nakshatra(ketu_lon)
    h = get_house(ketu_lon, asc_sidereal)
    bodies['Ketu'] = {
        'lon': ketu_lon, 'lat': 0, 'dist': 0, 'spd': 0,
        'si': si, 'sd': sd, 'd': d, 'm': m, 's': s,
        'sign': ZODIAC_SIGNS[si], 'elem': elem, 'qual': qual,
        'ni': ni, 'nak': nn, 'ns': ns, 'pada': pa, 'nl': nl, 'house': h,
    }
    
    # Outer planets
    outer_names = {'Uranus': swe.URANUS, 'Neptune': swe.NEPTUNE, 'Pluto': swe.PLUTO}
    outer = {}
    for name, bid in outer_names.items():
        r, _ = swe.calc_ut(jd_ut, bid, swe.FLG_SIDEREAL)
        p_lon, p_lat, dist, spd = r[0], r[1], r[2], r[3]
        si, sd, elem, qual = get_sign_info(p_lon)
        d, m, s = decimal_to_dms(sd)
        ni, nn, pa, nl, ns = get_nakshatra(p_lon)
        h = get_house(p_lon, asc_sidereal)
        
        outer[name] = {
            'lon': p_lon, 'lat': p_lat, 'dist': dist, 'spd': spd,
            'si': si, 'sd': sd, 'd': d, 'm': m, 's': s,
            'sign': ZODIAC_SIGNS[si], 'elem': elem, 'qual': qual,
            'ni': ni, 'nak': nn, 'ns': ns, 'pada': pa, 'nl': nl, 'house': h,
        }
    
    # Moon phase
    elongation = (bodies['Moon']['lon'] - bodies['Sun']['lon']) % 360
    phase_name, phase_desc = get_moon_phase(elongation)
    
    # Aspects
    aspects = calculate_aspects(bodies, outer)
    
    # Combustion
    combustions = check_combustion(bodies)
    
    # Moon combinations
    moon_combos, nakshatra_lord = get_moon_combinations(bodies['Moon']['lon'], bodies)
    
    # Gandanta
    moon_gandanta = is_gandanta(bodies['Moon']['lon'])
    
    # Dasha (Vimshottari) - only for natal charts
    dasha = None
    current_dasha = None
    antardashas = []
    
    if is_natal:
        dasha = calculate_dasha(bodies['Moon']['lon'], jd_ut)
        # Use current date to find active Dasha, not birth date
        from datetime import datetime
        current_jd = swe.julday(datetime.now(timezone.utc).year, datetime.now(timezone.utc).month, 
                                datetime.now(timezone.utc).day, 
                                datetime.now(timezone.utc).hour + datetime.now(timezone.utc).minute / 60.0,
                                cal=swe.GREG_CAL)
        current_dasha = get_current_dasha(dasha, current_jd)
        antardashas = get_antardasha(dasha, current_jd)
    
    # Planetary Hours — using accurate hora_service.py
    try:
        from hora_service import get_current_hora
        tz = ZoneInfo('Asia/Tokyo')
        from datetime import datetime
        now_tz = datetime.now(tz)
        hora_data = get_current_hora(lat=lat, lon=lon, tz_name='Asia/Tokyo')
        planetary_hours = {
            'day_name': hora_data['day_of_week'],
            'day_lord': hora_data['first_hora_lord'],
            'sunrise_jst': hora_data['sunrise'],
            'sunset_jst': hora_data['sunset'],
            'day_length_hours': hora_data['day_length_hours'],
            'night_length_hours': hora_data['night_length_hours'],
            'day_hour_minutes': hora_data['day_length_hours'] * 60 / 12,
            'night_hour_minutes': hora_data['night_length_hours'] * 60 / 12,
            'current_planet': hora_data['current_hora']['lord'],
            'current_hora_num': hora_data['current_hora']['hour_num'],
            'current_period': 'day' if hora_data['is_daytime'] else 'night',
            'current_trading': hora_data['current_hora']['trading'],
            'current_strategy': hora_data['current_hora']['strategy'],
            'current_element': hora_data['current_hora']['element'],
            'hours': [{
                'num': h['hour_num'],
                'period': h['period'],
                'planet': h['lord'],
                'start_jst': h['start'],
                'end_jst': h['end'],
                'trading': h.get('trading', ''),
                'strategy': h.get('strategy', ''),
            } for h in hora_data['full_sequence']],
        }
    except ImportError:
        # Fallback to old method if hora_service.py not available
        planetary_hours = calculate_planetary_hours(dt_utc, lat, lon)
    
    return {
        'ayanamsa': ayanamsa, 'jd': jd_ut,
        'asc_si': asc_si, 'asc_sd': asc_sd, 'asc_d': asc_d, 'asc_m': asc_m, 'asc_s': asc_s,
        'mc_si': mc_si, 'mc_sd': mc_sd, 'mc_d': mc_d, 'mc_m': mc_m, 'mc_s': mc_s,
        'bodies': bodies, 'outer': outer,
        'phase_name': phase_name, 'phase_desc': phase_desc, 'elongation': elongation,
        'aspects': aspects, 'combustions': combustions,
        'moon_combos': moon_combos, 'nakshatra_lord': nakshatra_lord,
        'moon_gandanta': moon_gandanta,
        'dasha': dasha, 'current_dasha': current_dasha, 'antardashas': antardashas,
        'planetary_hours': planetary_hours,
    }


# ============================================================
# FORMAT OUTPUT
# ============================================================

def format_output(data, dt, tz, lat, lon):
    b = data['bodies']
    o = data['outer']
    a = data['aspects']
    c = data['combustions']
    mc = data['moon_combos']
    nl = data['nakshatra_lord']
    moon = b['Moon']
    
    lines = []
    def W(s=""): lines.append(s)
    
    W("=" * 75)
    W("📊 FINANCIAL ASTROLOGY — DAY TRADING FOCUS (M15/H1)")
    W("   (SIDEREAL - AYANAMSA LAHIRI | WHOLE SIGN HOUSES)")
    W("=" * 75)
    W(f"⏰ {dt.strftime('%Y-%m-%d %H:%M:%S')} {tz} | 📍 {lat}°N, {lon}°E")
    W(f"🌐 Ayanamsa: {data['ayanamsa']:.4f}° | JD: {data['jd']:.6f}")
    W("=" * 75)
    W()
    
    # Chart info
    W(f"⬆️ Lagna: {ZODIAC_SIGNS[data['asc_si']]} {data['asc_d']}°{data['asc_m']}'{data['asc_s']}\"")
    W(f"☀️ MC:    {ZODIAC_SIGNS[data['mc_si']]} {data['mc_d']}°{data['mc_m']}'{data['mc_s']}\"")
    W()
    
    # =============================================
    # 0. PLANETARY HOURS
    # =============================================
    ph = data.get('planetary_hours', {})
    if ph:
        current_planet = ph['current_planet']
        hora_info = HORA_TRADING.get(current_planet, {})
        
        W("=" * 75)
        W("⏰ HORA (PLANETARY HOURS) — Chaldean Order")
        W("=" * 75)
        W(f"📅 {ph['day_name']} — Day lord: {current_planet}")
        W(f"🌅 Sunrise: {ph['sunrise_jst']} JST | 🌇 Sunset: {ph['sunset_jst']} JST")
        W(f"☀️ Daytime: {ph['day_length_hours']}h ({ph['day_hour_minutes']:.0f}min/hour) | 🌙 Nighttime: {ph['night_length_hours']}h ({ph['night_hour_minutes']:.0f}min/hour)")
        W()
        
        emoji = hora_info.get('emoji', '❓')
        name = hora_info.get('name', f'Hour of {current_planet}')
        bias = hora_info.get('bias', '')
        assets = hora_info.get('assets', '')
        strategy = hora_info.get('strategy', '')
        warning = hora_info.get('warning', '')
        
        period_emoji = '☀️ DAYTIME' if ph['current_period'] == 'day' else '🌙 NIGHTTIME'
        
        W(f"{emoji} CURRENT HOUR: {name} (Hora {ph['current_hora_num']}/24) — {period_emoji}")
        W(f"   📊 Bias: {bias}")
        W(f"   💰 Favorable assets: {assets}")
        W(f"   🎯 Strategy: {strategy}")
        if warning:
            W(f"   ⚠️ Warning: {warning}")
        W()
        
        # Gold (XAU/USD) specific
        gold_meaning = HORA_GOLD.get(current_planet, '')
        W(f"🥇 GOLD (XAU/USD): {gold_meaning}")
        
        # Bitcoin specific
        btc_meaning = HORA_BTC.get(current_planet, '')
        W(f"₿ BITCOIN (BTC/USD): {btc_meaning}")
        W()
        
        # Show today's full 24-hour schedule
        W("--- TODAY'S 24-HOUR HORA SCHEDULE ---")
        W(f"{'Hora':<6} {'Period':<5} {'JST Time':<12} {'Planet':<10} {'Trading':<30}")
        W("-" * 70)
        
        for h in ph['hours']:
            period_icon = '☀️' if h['period'] == 'day' else '🌙'
            h_planet = h['planet']
            h_info = HORA_TRADING.get(h_planet, {})
            h_bias = h_info.get('bias', '')[:28]
            
            marker = ' ◀' if h['num'] == ph['current_hora_num'] else ''
            W(f"  {h['num']:2d}  {period_icon:<4} {h['start_jst']}-{h['end_jst']:<7} {h_planet:<10} {h_bias}{marker}")
        W()
        W("=" * 75)
        W()
    
    # =============================================
    # 1. MOON ANALYSIS
    # =============================================
    W("=" * 75)
    W("🌙 MOON ANALYSIS — SHORT-TERM SENTIMENT (M15/H1)")
    W("=" * 75)
    
    W(f"🌙 Phase: {data['phase_name']}")
    W(f"   {data['phase_desc']}")
    W(f"   Elongation: {data['elongation']:.1f}°")
    W()
    
    W(f"🌙 Moon in {moon['sign']} {moon['d']}°{moon['m']}'{moon['s']}\"")
    W(f"   Element: {moon['elem']} | Quality: {moon['qual']}")
    
    # Element mood
    if moon['elem'] == "Fire":
        W("   🔥 MOOD: RISK-ON → Confident, bullish, risk-seeking")
        W("   → Bias: BUY dips, momentum plays")
    elif moon['elem'] == "Earth":
        W("   🌍 MOOD: PRACTICAL → Safe haven, value play")
        W("   → Bias: Gold strong, crypto stable")
    elif moon['elem'] == "Air":
        W("   💨 MOOD: RATIONAL → Analytical, indecisive, sideways")
        W("   → Bias: Range trading, false breakouts")
    elif moon['elem'] == "Water":
        W("   💧 MOOD: EMOTIONAL → Sensitive, prone to strong moves")
        W("   → Bias: Watch sudden moves, tight SL")
    
    W()
    W(f"   {moon['ns']} Nakshatra: {moon['nak']} (#{moon['ni']+1}/27) | Pada: {moon['pada']}/4")
    W(f"   Lord: {moon['nl']}")
    
    # Nakshatra trade quality
    if moon['nak'] in NAKSHATRA_TRADE:
        quality, desc = NAKSHATRA_TRADE[moon['nak']]
        W(f"   {quality} for trading — {desc}")
    
    # Gandanta
    if data['moon_gandanta']:
        W("   ⚠️🌊 MOON AT GANDANTA POINT — Extreme volatility, unexpected reversal!")
        W("   ⚠️ Recommendation: Avoid trading or use VERY TIGHT SL")
    
    W()
    
    # Moon speed (the Moon always moves direct, never retrograde)
    if moon['spd'] > 13:
        W(f"   🚀 Moon fast ({moon['spd']:.1f}°/day) → HIGH volatility, many M15/H1 opportunities")
    elif moon['spd'] > 0:
        W(f"   🐢 Moon normal ({moon['spd']:.1f}°/day) → Average volatility")
    else:
        W(f"   ⚠️ Moon stationary → Trend paused, watch for breakout")
    
    # =============================================
    # 2. MOON-PLANET COMBINATIONS
    # =============================================
    W()
    W("-" * 50)
    W("🔗 MOON COMBINATIONS (Moon combined with planets)")
    W("-" * 50)
    
    if mc:
        for combo in mc:
            title, trend, strategy = interpret_moon_combination(combo['planet'], nl)
            W(f"   {title} (separation {combo['diff']}°)")
            W(f"   → {trend}")
            W(f"   → Strategy: {strategy}")
    else:
        W(f"   Moon is not conjunct with any planet in the same sign")
    
    # Nakshatra lord influence
    W(f"   🌙 Moon Nakshatra Lord: {nl} → {nl} will strongly influence today's trend")
    
    # =============================================
    # 3. MOON ASPECTS
    # =============================================
    W()
    W("-" * 50)
    W("🔗 MOON ASPECTS — Aspects affecting the Moon")
    W("   ⚡ Most important for M15/H1 ⚡")
    W("-" * 50)
    
    moon_asps = [x for x in a if x['p1'] == 'Moon' or x['p2'] == 'Moon']
    
    if not moon_asps:
        W("   ⚪ Moon has no major aspects → Quiet market, low volatility")
    else:
        for asp in sorted(moon_asps, key=lambda x: x['orb']):
            other = asp['p2'] if asp['p1'] == 'Moon' else asp['p1']
            tight = "🔴 TIGHT" if asp['tight'] else ""
            interp = interpret_moon_aspect(asp['aspect'], other)
            W(f"   🌙 {asp['symbol']} {asp['aspect']} {SHORT_NAMES.get(other, other)} (orb: {asp['orb']}°) {tight}")
            W(f"      → {interp}")
    
    # =============================================
    # 4. COMBUSTION
    # =============================================
    W()
    W("=" * 75)
    W("🔥 COMBUSTION — Planet burnt by the Sun")
    W("=" * 75)
    
    if c:
        for comb in c:
            W(f"   {comb['desc']}")
            if comb['planet'] == 'Mercury':
                W("   → Market information may be distorted, many false signals")
            elif comb['planet'] == 'Venus':
                W("   → Risk appetite affected, distorted valuation")
            elif comb['planet'] == 'Mars':
                W("   → Reduced aggression, but sudden rises")
    else:
        W("   ✅ No planet is combust → Stable sentiment")
    
    # =============================================
    # 5. MERCURY STATUS
    # =============================================
    W()
    W("=" * 75)
    W("☿️ MERCURY — INFORMATION & SIGNALS")
    W("=" * 75)
    
    merc = b['Mercury']
    if merc['spd'] < 0:
        W("   ☿️ MERCURY RETROGRADE")
        W("   ⚠️ False breakout/breakdown — do not enter at the breakout")
        W("   ⚠️ Technical glitch, execution error")
        W("   ⚠️ Misinformation, shocking news")
        W("   → Recommendation: Wait for confirmation, reduce position size, tight SL")
    else:
        W("   ☿️ Mercury direct → Clear information, reliable setups")
    
    merc_combust = any(x['planet'] == 'Mercury' for x in c)
    if merc_combust:
        W("   🔥 MERCURY COMBUST → High false signals, trade fewer orders")
    
    # =============================================
    # 6. ALL MAJOR ASPECTS
    # =============================================
    W()
    W("=" * 75)
    W("🔗 ALL MAJOR ASPECTS")
    W("=" * 75)
    
    sorted_asps = sorted(a, key=lambda x: x['orb'])
    for asp in sorted_asps:
        tight = "🔴" if asp['tight'] else " "
        W(f"  {tight} {SHORT_NAMES.get(asp['p1'], asp['p1'])} {asp['symbol']} {asp['aspect']} {SHORT_NAMES.get(asp['p2'], asp['p2'])} (orb: {asp['orb']}°)")
    
    # =============================================
    # 7. DAY TRADING SIGNAL
    # =============================================
    W()
    W("=" * 75)
    W("📊 DAY TRADING SIGNAL (M15/H1)")
    W("=" * 75)
    
    signals = []
    
    # Moon phase bias
    if "Waxing" in data['phase_name']:
        signals.append("📈 Moon Phase: BULLISH BIAS")
    elif "Waning" in data['phase_name']:
        signals.append("📉 Moon Phase: BEARISH BIAS")
    elif data['phase_name'] == "Full Moon":
        signals.append("🌕 Full Moon: HIGH VOLATILITY — Watch for reversal")
    elif data['phase_name'] == "New Moon":
        signals.append("🌑 New Moon: LOW VOLATILITY — Wait for breakout")
    
    # Moon aspects sentiment
    if moon_asps:
        neg = ['Square', 'Opposition', 'Quincunx']
        pos = ['Trine', 'Sextile', 'Conjunction']
        neg_c = sum(1 for x in moon_asps if x['aspect'] in neg)
        pos_c = sum(1 for x in moon_asps if x['aspect'] in pos)
        
        if neg_c >= 2:
            signals.append(f"⚠️ Moon has {neg_c} negative aspects → HIGH VOLATILITY, be cautious")
        elif pos_c >= 2:
            signals.append(f"✅ Moon has {pos_c} positive aspects → Favorable trend")
        elif neg_c >= 1:
            signals.append("⚡ Moon has a tense aspect → Watch for volatility spikes")
    
    # Mercury
    if merc['spd'] < 0:
        signals.append("☿️ Mercury Rx → Be cautious, do not trade the news, wait for confirmation")
    if merc_combust:
        signals.append("🔥 Mercury combust → High false signals")
    
    # Gandanta
    if data['moon_gandanta']:
        signals.append("🌊 Moon at Gandanta → EXTREME VOLATILITY, avoid trading or use tight SL")
    
    # Moon combos
    for combo in mc:
        title, trend, _ = interpret_moon_combination(combo['planet'], nl)
        signals.append(f"🔗 {title} → {trend}")
    
    for s in signals:
        W(f"  {s}")
    
    # =============================================
    # 8. NAVAGRAHA SUMMARY
    # =============================================
    W()
    W("=" * 75)
    W("📋 NAVAGRAHA SUMMARY")
    W("=" * 75)
    
    order = ['Moon', 'Sun', 'Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn', 'Rahu', 'Ketu']
    for name in order:
        if name not in b:
            continue
        d = b[name]
        pos = f"{d['d']}°{d['m']}'{d['s']}\""
        rx = " Rx" if d['spd'] < 0 else ""
        cb = " 🔥COMBUST" if any(x['planet'] == name and x['status'] == 'COMBUST 🔥' for x in c) else ""
        cz = " ⚡CAZIMI" if any(x['planet'] == name and x['status'] == 'CAZIMI ⚡' for x in c) else ""
        W(f"  {BODY_NAMES[name]}: {d['sign']} {pos} | House {d['house']} | {d['ns']} {d['nak']} P{d['pada']}{rx}{cb}{cz}")
    
    # =============================================
    # 9. OUTER PLANETS
    # =============================================
    W()
    W("=" * 75)
    W("🪐 OUTER PLANETS")
    W("=" * 75)
    
    for name in ['Uranus', 'Neptune', 'Pluto']:
        if name not in o:
            continue
        d = o[name]
        pos = f"{d['d']}°{d['m']}'{d['s']}\""
        rx = " Rx" if d['spd'] < 0 else ""
        W(f"  {BODY_NAMES[name]}: {d['sign']} {pos} | House {d['house']} | {d['nak']} P{d['pada']}{rx}")
    
    # =============================================
    # 10. DASHA (VIMSHOTTARI)
    # =============================================
    W()
    W("=" * 75)
    W("📊 DASHA — MAJOR & MINOR PERIODS (Vimshottari 120 years)")
    W("=" * 75)
    
    dasha = data.get('dasha', {})
    current_dasha = data.get('current_dasha')
    antardashas = data.get('antardashas', [])
    
    if dasha:
        W(f"🌙 Moon Nakshatra: {dasha['moon_nakshatra']}")
        W(f"👑 Nakshatra Lord: {dasha['nakshatra_lord']}")
        W(f"📐 Remaining in Nakshatra: {dasha['remaining_fraction']}%")
        W()
        
        if current_dasha:
            W(f"🔴 CURRENT MAJOR PERIOD: {current_dasha['lord']}")
            W(f"   {DASHA_MEANINGS.get(current_dasha['lord'], '')}")
            W(f"   From {current_dasha['start']} to {current_dasha['end']}")
            W()
        
        W("--- MAJOR PERIODS (120 years) ---")
        W(f"{'Period':<12} {'Years':<8} {'From':<12} {'To':<12} {'Current':<10}")
        W("-" * 60)
        
        for d in dasha['sequence']:
            marker = "🔴 CURRENT" if (current_dasha and d['lord'] == current_dasha['lord']) else ""
            W(f"{d['lord']:<12} {d['effective_years']:<8.2f} {d['start']:<12} {d['end']:<12} {marker}")
        
        W()
        
        if antardashas:
            W("--- MINOR PERIODS (Antardasha) ---")
            W(f"{'Sub-period':<12} {'From':<12} {'To':<12} {'Meaning':<30}")
            W("-" * 70)
            
            for ad in antardashas:
                marker = "🔴" if ad['is_current'] else " "
                meaning = DASHA_MEANINGS.get(ad['lord'], '')[:30]
                W(f"{ad['lord']:<12} {ad['start']:<12} {ad['end']:<12} {marker} {meaning}")
    else:
        W("ℹ️ Dasha is only calculated for the Natal Chart (add --natal to compute Dasha)")
    
    # =============================================
    # 11. ASSET-SPECIFIC
    # =============================================
    W()
    W("=" * 75)
    W("📊 ASSET-SPECIFIC ANALYSIS")
    W("=" * 75)
    
    # Gold
    W()
    W("🥇 GOLD (XAU/USD)")
    W("-" * 40)
    sun = b['Sun']
    venus = b['Venus']
    W(f"  ☀️ Sun in {sun['sign']} | ♀️ Venus in {venus['sign']}")
    
    if moon['elem'] in ["Earth", "Water"]:
        W("  🌙 Moon in Earth/Water sign → HIGH safe haven demand, supports Gold")
    elif moon['elem'] == "Fire":
        W("  🔥 Moon in Fire sign → Risk-on, Gold may lose appeal")
    elif moon['elem'] == "Air":
        W("  💨 Moon in Air sign → Indecisive, Gold sideways")
    
    # Bitcoin
    W()
    W("₿ BITCOIN (BTC/USD)")
    W("-" * 40)
    rahu = b['Rahu']
    uranus = o.get('Uranus', {})
    W(f"  🐉 Rahu in {rahu['sign']} | ⛧ Uranus in {uranus.get('sign', '?')}")
    
    if merc['spd'] < 0 or merc_combust:
        W("  ☿️ Mercury Rx/combust → Crypto highly volatile, false signals")
    else:
        W("  ☿️ Mercury direct → Clearer Crypto signals")
    
    if uranus.get('si') == 10:  # Aquarius
        W("  ♇ Pluto in Aquarius → New era for Crypto, AI, Decentralization")
    
    # =============================================
    # DISCLAIMER
    # =============================================
    W()
    W("=" * 75)
    W("⚠️ NOTE:")
    W("  • Financial astrology is a SUPPLEMENTARY tool, NOT a replacement for technical analysis")
    W("  • Correlation ≠ causation — planets do not 'cause' market moves")
    W("  • Always use stop loss, do not risk more than 1-2% per trade")
    W("  • Investing involves risk; you are responsible for your own decisions")
    W("=" * 75)
    
    return "\n".join(lines)


# ============================================================
# MAIN
# ============================================================

def main():
    parser = argparse.ArgumentParser(description='Financial Astrology — Day Trading Focus (M15/H1)')
    parser.add_argument('--tz', type=str, default='Asia/Tokyo')
    parser.add_argument('--date', type=str, default=None)
    parser.add_argument('--lat', type=float, default=34.9333)
    parser.add_argument('--lon', type=float, default=136.9667)
    parser.add_argument('--asset', type=str, default='all')
    parser.add_argument('--json', action='store_true')
    parser.add_argument('--natal', action='store_true', help='Calculate Dasha for natal chart')
    
    args = parser.parse_args()
    
    tz = ZoneInfo(args.tz)
    
    if args.date:
        dt_naive = datetime.strptime(args.date, '%Y-%m-%d %H:%M:%S')
        dt_display = dt_naive.replace(tzinfo=tz)
        dt_utc = dt_display.astimezone(timezone.utc)
    else:
        dt_display = datetime.now(tz)
        dt_utc = dt_display.astimezone(timezone.utc)
    
    data = calculate_all(dt_utc, args.lat, args.lon, is_natal=args.natal)
    
    if args.json:
        print(json.dumps(data, default=str, ensure_ascii=False))
    else:
        print(format_output(data, dt_display, args.tz, args.lat, args.lon))

if __name__ == '__main__':
    main()
