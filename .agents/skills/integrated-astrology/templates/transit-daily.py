#!/usr/bin/env python3
"""
Daily Transit Reading Template
===============================
Computes transit planet positions + Placidus houses + transit→natal aspects
for a given date and birth chart. Engine resolution: xalen.swe if importable,
otherwise pyswisseph. Both work in the Hermes venv (xalen 0.6.0 ships
xalen.swe); the dedicated xalen-venv is not required.

Usage:  python transit-daily.py "YYYY-MM-DD HH:MM" LAT LON TZ "NAME"
Example: python transit-daily.py "2026-07-27 07:38" 19.91 99.83 7 "BooM"
"""
try:
    from xalen import swe  # Hermes venv and xalen-venv both provide xalen.swe
except ImportError:
    import swisseph as swe  # pyswisseph fallback
import sys, datetime, math

# ─── CONFIG ───
# Birth data: 20 Nov 1996 20:37 ICT, Chiang Rai (19.91°N, 99.83°E)
BIRTH = {"y": 1996, "m": 11, "d": 20, "h": 20, "min": 37, "tz": 7,
         "lat": 19.91, "lon": 99.83, "name": "BooM"}

# Override from CLI args
if len(sys.argv) >= 6:
    dt_str, lat, lon, tz, name = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
    dt = datetime.datetime.strptime(dt_str, "%Y-%m-%d %H:%M")
    TRANSIT = {"y": dt.year, "m": dt.month, "d": dt.day, "h": dt.hour, "min": dt.minute,
               "tz": tz, "lat": lat, "lon": lon, "name": name}
else:
    now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7)))
    TRANSIT = {"y": now.year, "m": now.month, "d": now.day, "h": now.hour, "min": now.minute,
               "tz": 7, "lat": BIRTH["lat"], "lon": BIRTH["lon"], "name": BIRTH["name"]}

SIGNS = ["♈","♉","♊","♋","♌","♍","♎","♏","♐","♑","♒","♓"]
PLANETS = [
    (swe.SUN, "☉", "Sun"), (swe.MOON, "☽", "Moon"),
    (swe.MERCURY, "☿", "Mercury"), (swe.VENUS, "♀", "Venus"),
    (swe.MARS, "♂", "Mars"), (swe.JUPITER, "♃", "Jupiter"),
    (swe.SATURN, "♄", "Saturn"), (swe.URANUS, "♅", "Uranus"),
    (swe.NEPTUNE, "♆", "Neptune"), (swe.PLUTO, "♇", "Pluto"),
]
ASPECTS = {0: ("☌",8), 30: ("✱",3), 60: ("⚹",6), 90: ("□",5),
           120: ("△",6), 150: ("⚻",3), 180: ("☍",6)}

def jd_utc(y, m, d, h, min, tz):
    ut = h - tz
    if ut < 0: d -= 1; ut += 24
    return swe.julday(y, m, d, ut + min/60.0)

def deg_sym(d): s = int(d//30); return f"{SIGNS[s]} {d - s*30:.1f}°"

def houses_normalise(jd, lat, lon):
    c, a = swe.houses(jd, lat, lon, b'P')
    c12 = c if len(c) == 12 else c[1:13]
    return c12, a[0], a[1]

def house_num(c, lon):
    for i in range(11):
        c1, c2 = c[i], c[i+1]
        if c2 < c1 and (lon >= c1 or lon < c2): return i+1
        if c1 <= lon < c2: return i+1
    return 12

def aspect(a, b):
    d = (abs(a-b)%360); d = 360-d if d>180 else d
    for deg, (s,mx) in ASPECTS.items():
        if abs(d-deg) <= mx: return s, round(abs(d-deg), 1)
    return None, None

# ═══ CALCULATE ═══
swe.set_ephe_path(None)
nat_jd = jd_utc(**{k: BIRTH[k] for k in ["y","m","d","h","min","tz"]})
tr_jd  = jd_utc(**{k: TRANSIT[k] for k in ["y","m","d","h","min","tz"]})

nat_cusps, nat_asc, nat_mc = houses_normalise(nat_jd, BIRTH["lat"], BIRTH["lon"])
tr_cusps, tr_asc, tr_mc = houses_normalise(tr_jd, TRANSIT["lat"], TRANSIT["lon"])

nat_pos = {}
tr_pos = {}
for pid, sym, name in PLANETS:
    arr, _ = swe.calc_ut(nat_jd, pid, swe.FLG_SWIEPH | swe.FLG_SPEED)
    nat_pos[sym] = arr[0]
    arr2, _ = swe.calc_ut(tr_jd, pid, swe.FLG_SWIEPH | swe.FLG_SPEED)
    tr_pos[sym] = arr2[0]

# ═══ OUTPUT ═══
print(f"{'='*55}")
print(f"  TRANSIT {TRANSIT['name']} — {TRANSIT['y']}-{TRANSIT['m']:02d}-{TRANSIT['d']:02d} {TRANSIT['h']:02d}:{TRANSIT['min']:02d}")
print(f"{'='*55}")
print(f"  Nat ASC: {deg_sym(nat_asc)}  MC: {deg_sym(nat_mc)}")
print(f"  Tr  ASC: {deg_sym(tr_asc)}  MC: {deg_sym(tr_mc)}")
print()

# Transit table
print("─── TRANSIT ───")
for pid, sym, name in PLANETS:
    lon = tr_pos[sym]
    h = house_num(tr_cusps, lon)
    arr, _ = swe.calc_ut(tr_jd, pid, swe.FLG_SWIEPH | swe.FLG_SPEED)
    rx = " Rx" if arr[3] < 0 else ""
    print(f"  {sym} {deg_sym(lon)} — House {h}{rx}")
print()

# Aspects
print("─── TRANSIT → NATAL ASPECTS ───")
found = []
for ts, tl in tr_pos.items():
    for ns, nl in nat_pos.items():
        a, o = aspect(tl, nl)
        if a: found.append((o, ts, ns, a))
found.sort(key=lambda x: x[0])
for o, ts, ns, a in found[:20]:
    print(f"  {ts} {a} {ns}  ({o}°)")
print(f"\n{'='*55}")
_engine = "xalen" if "xalen" in getattr(swe, "__name__", "") else "pyswisseph"
print(f"  Source: Swiss Ephemeris | Placidus | {_engine}")
print(f"{'='*55}")
