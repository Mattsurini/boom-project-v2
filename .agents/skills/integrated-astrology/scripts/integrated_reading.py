#!/usr/bin/env python3
"""
Integrated Astrology Reading — Western + Uranian
Usage: python integrated_reading.py [type] [args]
  Types:
    natal <YYYY-MM-DD> <HH:MM> <lat> <lon> [name]
    transit <natal_date> <natal_time> <lat> <lon> [transit_date]
Example:
    python integrated_reading.py natal 1996-11-20 20:37 19.91 99.83 "BooM"
    python integrated_reading.py transit 1996-11-20 20:37 19.91 99.83 2026-07-12
"""

# Engine: two-stage fallback.
#   Stage 1 — xalen.swe (XALEN ephemeris) is importable in the Hermes venv
#            (xalen 0.6.0 exposes xalen.swe), same as in C:\Users\Turbo\xalen-venv.
#   Stage 2 — these readings use Transneptunian points (Apollon, Vulcanus,
#            Poseidon, ... = SE body ids 40-47). xalen raises
#            ValueError "unsupported SE planet number" for those, so the read
#            falls back to pyswisseph, which does support them.
# Net effect: the engine actually used here is pyswisseph, because of the
# Transneptunian requirement — not because xalen is unimportable.
try:
    from xalen import swe  # Hermes venv and xalen-venv both provide xalen.swe
except ImportError:
    import swisseph as swe  # xalen not installed at all

try:
    swe.calc_ut(2451545.0, 40, 0)
except Exception:
    import swisseph as swe  # xalen lacks Transneptunian SE ids 40-47
import math, sys
from datetime import datetime, timezone, timedelta

swe.set_ephe_path('')

SIGNS = ["♈Aries","♉Taurus","♊Gemini","♋Cancer",
         "♌Leo","♍Virgo","♎Libra","♏Scorpio",
         "♐Sagittarius","♑Capricorn","♒Aquarius","♓Pisces"]

PLANETS = ["Sun","Moon","Mercury","Venus","Mars","Jupiter","Saturn","Uranus","Neptune","Pluto"]
TNS = ["Cupido","Hades","Zeus","Kronos","Apollon","Admetos","Vulcanus","Poseidon"]
ALL_BODIES = PLANETS + TNS

BODY_CODES = {
    "Sun":0,"Moon":1,"Mercury":2,"Venus":3,"Mars":4,"Jupiter":5,"Saturn":6,
    "Uranus":7,"Neptune":8,"Pluto":9,
    "Cupido":40,"Hades":41,"Zeus":42,"Kronos":43,"Apollon":44,"Admetos":45,"Vulcanus":46,"Poseidon":47,
}

def get_sign(lon):
    s = int(lon // 30)
    return f"{SIGNS[s]} {lon - s * 30:.1f}°"

def get_house(lon, asc_s):
    return ((int(lon//30) - asc_s) % 12) + 1

def aspect_angle(l1, l2):
    d = abs(l1 - l2)
    if d > 180: d = 360 - d
    return d

def western_aspect(a, orb=7):
    for ang, sym, nm in [(0,"☌","Conjunction"),(60,"⚹","Sextile"),(90,"□","Square"),(120,"△","Trine"),(180,"☍","Opposition")]:
        if abs(a-ang) <= orb: return sym, nm, abs(a-ang)
    return None, None, None

def dial_90(lon):
    return lon % 90

def uranian_aspect(l1, l2, orb=1.5):
    d = abs(dial_90(l1) - dial_90(l2))
    if d > 45: d = 90 - d
    if d <= orb: return "☌", "90° Dial Conjunction", d
    if abs(d-45) <= orb: return "∠", "90° Dial Semi-square", d
    return None, None, None

def midpoint(l1, l2):
    return ((l1 + l2) / 2) % 360

def get_chart(jd, flags=swe.FLG_SWIEPH):
    r = {}
    for name in ALL_BODIES:
        arr, _ = swe.calc_ut(jd, BODY_CODES[name], flags)
        r[name] = {'lon': arr[0], 'lat': arr[1], 'dist': arr[2],
                   'lon_speed': arr[3] if len(arr)>3 else 0,
                   'retro': arr[3] < 0 if len(arr)>3 else False}
    return r

# ================================================================
# MAIN
# ================================================================
if len(sys.argv) < 2:
    print(__doc__)
    sys.exit(1)

mode = sys.argv[1]

if mode == "natal":
    date_str = sys.argv[2]  # YYYY-MM-DD
    time_str = sys.argv[3]  # HH:MM
    lat = float(sys.argv[4])
    lon_p = float(sys.argv[5])
    name = sys.argv[6] if len(sys.argv) > 6 else "Native"

    parts = date_str.split('-')
    tparts = time_str.split(':')
    dt = datetime(int(parts[0]), int(parts[1]), int(parts[2]),
                  int(tparts[0]), int(tparts[1]), tzinfo=timezone.utc) - timedelta(hours=7)
    jd = swe.julday(dt.year, dt.month, dt.day, dt.hour + dt.minute/60.0)
    
    asc_arr = swe.houses(jd, lat, lon_p, b'P')
    asc_lon = asc_arr[1][0]
    mc_lon = asc_arr[1][1]
    asc_s = int(asc_lon // 30)
    
    chart = get_chart(jd)
    
    print(f"\n{'='*65}")
    print(f"  🔮 INTEGRATED NATAL CHART — {name}")
    print(f"  {date_str} {time_str} ICT @ {lat}°N, {lon_p}°E")
    print(f"  🧭 ASC: {get_sign(asc_lon)}  |  MC: {get_sign(mc_lon)}")
    print(f"{'='*65}")
    
    # Section 1: Western positions
    print(f"\n📌 1. WESTERN — Planets in Houses")
    print("-"*45)
    for p in PLANETS:
        d = chart[p]
        h = get_house(d['lon'], asc_s)
        r = "℞" if d.get('retro') else "D"
        print(f"  {p:12s} → {get_sign(d['lon']):18s} House {h:2d}  {r}")
    
    print(f"\n📌 2. URANIAN — Transneptunian in Houses")
    print("-"*45)
    for tn in TNS:
        d = chart[tn]
        h = get_house(d['lon'], asc_s)
        r = "℞" if d.get('retro') else "D"
        print(f"  {tn:12s} → {get_sign(d['lon']):18s} House {h:2d}  {r}")
    
    # Section 3: Western aspects (planet-planet)
    print(f"\n📌 3. WESTERN ASPECTS (planet-planet, orb ≤7°)")
    print("-"*45)
    for i in range(len(PLANETS)):
        for j in range(i+1, len(PLANETS)):
            a = aspect_angle(chart[PLANETS[i]]['lon'], chart[PLANETS[j]]['lon'])
            s, n, o = western_aspect(a, 7)
            if s:
                print(f"  {PLANETS[i]:10s} {s} {PLANETS[j]:10s}  orb {o:.1f}°")
    
    # Section 4: Uranian 90° dial
    print(f"\n📌 4. URANIAN 90° DIAL (≤1.5° orb)")
    print("-"*45)
    for i in range(len(ALL_BODIES)):
        for j in range(i+1, len(ALL_BODIES)):
            s, n, o = uranian_aspect(chart[ALL_BODIES[i]]['lon'], chart[ALL_BODIES[j]]['lon'], 1.5)
            if s:
                print(f"  {ALL_BODIES[i]:10s} {s} {ALL_BODIES[j]:10s}  orb {o:.1f}°")
    
    # Section 5: TN × Planet midpoints
    print(f"\n📌 5. MIDPOINTS (TN×Planet)→Target  ≤1.5°")
    print("-"*45)
    for tn in TNS:
        for p in PLANETS:
            mp = midpoint(chart[tn]['lon'], chart[p]['lon'])
            for t in ALL_BODIES:
                if t in [tn, p]: continue
                a = aspect_angle(mp, chart[t]['lon'])
                if a <= 1.5:
                    print(f"  {tn:8s}/{p:8s} ⚖ → {t:10s} orb {a:.1f}°")
                    break

elif mode == "transit":
    date_str = sys.argv[2]
    time_str = sys.argv[3]
    lat = float(sys.argv[4])
    lon_p = float(sys.argv[5])
    transit_date = sys.argv[6] if len(sys.argv) > 6 else datetime.now().strftime('%Y-%m-%d')
    
    parts = date_str.split('-')
    tparts = time_str.split(':')
    dt = datetime(int(parts[0]), int(parts[1]), int(parts[2]),
                  int(tparts[0]), int(tparts[1]), tzinfo=timezone.utc) - timedelta(hours=7)
    jd_natal = swe.julday(dt.year, dt.month, dt.day, dt.hour + dt.minute/60.0)
    
    tparts2 = transit_date.split('-')
    jd_transit = swe.julday(int(tparts2[0]), int(tparts2[1]), int(tparts2[2]), 12)
    
    asc_arr = swe.houses(jd_natal, lat, lon_p, b'P')
    asc_lon = asc_arr[1][0]
    asc_s = int(asc_lon // 30)
    
    natal = get_chart(jd_natal, swe.FLG_SWIEPH)
    trans = get_chart(jd_transit, swe.FLG_SWIEPH | swe.FLG_SPEED)
    
    BKK = datetime.now(timezone.utc) + timedelta(hours=7)
    print(f"\n{'='*65}")
    print(f"  🔮 INTEGRATED TRANSIT READING")
    print(f"  Natal: {date_str} {time_str} ICT | Transit: {transit_date}")
    print(f"{'='*65}")
    
    # Transit → Natal aspects (all bodies)
    print(f"\n📌 TRANSIT → NATAL ASPECTS")
    print(f"{'Body':<12} {'Aspect':<20} {'Natal planet':<15} {'House':<6} {'Orb':<6}")
    print("-"*60)
    
    for t_name in ALL_BODIES:
        for n_name in PLANETS:
            a = aspect_angle(trans[t_name]['lon'], natal[n_name]['lon'])
            orb_limit = 5 if t_name in PLANETS else 3
            s, nm, o = western_aspect(a, orb_limit)
            if s:
                h = get_house(natal[n_name]['lon'], asc_s)
                print(f"  {t_name:10s} {s+' '+nm:18s} {n_name:12s} House{h:1d}    {o:.1f}°")
    
    # Transit TN → Natal TN
    print(f"\n📌 TN TNASPECTS (TN transit → natal TN)")
    print("-"*45)
    for tn1 in TNS:
        for tn2 in TNS:
            if tn1 == tn2: continue
            a = aspect_angle(trans[tn1]['lon'], natal[tn2]['lon'])
            sym, nm, o = western_aspect(a, 3)
            if sym:
                print(f"  trans {tn1:8s} {sym} natal {tn2:8s} orb {o:.1f}°")
    
    # Midpoints
    print(f"\n📌 MIDPOINTS ACTIVATED BY TRANSIT")
    print("-"*45)
    for tn in TNS:
        for p in PLANETS:
            mp = midpoint(trans[tn]['lon'], trans[p]['lon'])
            for n_name in PLANETS:
                a = aspect_angle(mp, natal[n_name]['lon'])
                if a <= 1.5:
                    print(f"  trans {tn}/{p} ⚖ → natal {n_name} orb {a:.1f}°")
                    break

swe.close()
