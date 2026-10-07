#!/usr/bin/env python3
"""
Eclipse Finder for BooM — Solar & Lunar eclipses with natal aspects.
Usage: python eclipses.py [year] [orb]
  year: default current year + next 2 years
  orb:  max orb for natal aspects (default 8.0°)
"""
import sys, math
from datetime import datetime, timedelta, timezone

try:
    from xalen import swe
except ImportError:
    import swisseph as swe

try:
    swe.calc_ut(2451545.0, 40, 0)
except Exception:
    import swisseph as swe

swe.set_ephe_path('')

# ─── CONSTANTS ───
SIGNS = ["Ari","Tau","Gem","Can","Leo","Vir","Lib","Sco","Sag","Cap","Aqu","Pis"]
PLANETS = ["Sun","Moon","Mercury","Venus","Mars","Jupiter","Saturn","Uranus","Neptune","Pluto"]
TNS = ["Cupido","Hades","Zeus","Kronos","Apollon","Admetos","Vulcanus","Poseidon"]
ALL_BODIES = PLANETS + TNS

BODY_CODES = {
    "Sun":0,"Moon":1,"Mercury":2,"Venus":3,"Mars":4,"Jupiter":5,"Saturn":6,
    "Uranus":7,"Neptune":8,"Pluto":9,
    "Cupido":40,"Hades":41,"Zeus":42,"Kronos":43,"Apollon":44,"Admetos":45,"Vulcanus":46,"Poseidon":47,
}

# Eclipse type decoding
ECL_TYPE_MAP = {
    swe.ECL_TOTAL: "Total",
    swe.ECL_ANNULAR: "Annular",
    swe.ECL_PARTIAL: "Partial",
    swe.ECL_ANNULAR_TOTAL: "Annular-Total (Hybrid)",
    swe.ECL_PENUMBRAL: "Penumbral",
}

def get_eclipse_type(retflag):
    types = []
    if retflag & swe.ECL_TOTAL: types.append("Total")
    if retflag & swe.ECL_ANNULAR: types.append("Annular")
    if retflag & swe.ECL_PARTIAL: types.append("Partial")
    if retflag & swe.ECL_ANNULAR_TOTAL: types.append("Hybrid")
    if retflag & swe.ECL_PENUMBRAL: types.append("Penumbral")
    if not types: types.append("Unknown")
    return " ".join(types)

def is_central(retflag):
    if retflag & swe.ECL_CENTRAL: return "Central"
    if retflag & swe.ECL_NONCENTRAL: return "Non-central"
    return ""

# Aspect orbs for eclipses (wider)
ASPECTS = [
    (0, "☌", "Conjunction"),
    (60, "⚹", "Sextile"),
    (90, "□", "Square"),
    (120, "△", "Trine"),
    (180, "☍", "Opposition"),
]

# BooM natal data
NATAL_DATE = "1996-11-20"
NATAL_TIME = "20:37"
LAT, LON = 19.91, 99.83
TZ = 7

# ─── FUNCTIONS ───

def aspect_angle(l1, l2):
    d = abs(l1 - l2)
    if d > 180: d = 360 - d
    return d

def get_chart(jd, flags=swe.FLG_SWIEPH):
    r = {}
    for name in ALL_BODIES:
        arr, _ = swe.calc_ut(jd, BODY_CODES[name], flags)
        r[name] = arr[0]
    return r

def sign_str(lon):
    s = int(lon // 30)
    return f"{SIGNS[s]} {lon - s*30:.1f}°"

def jd_to_datetime(jd, tz=7):
    """Convert Julian Day to local datetime (ICT)."""
    year, month, day, hour, minute, second = swe.jdet_to_utc(jd, swe.GREG_CAL)
    dt = datetime(year, month, day, hour, minute, int(second), tzinfo=timezone.utc)
    local = dt + timedelta(hours=tz)
    return local

def find_solar_eclipses(year):
    """Find all solar eclipses in a year."""
    eclipses = []
    jd_start = swe.julday(year, 1, 1, 0)
    jd_end = swe.julday(year + 1, 1, 1, 0)
    
    jd = jd_start
    while jd < jd_end:
        try:
            result = swe.sol_eclipse_when_glob(jd, swe.FLG_SWIEPH, 0, False)
            retflag = result[0]
            tret = result[1]
            eclipse_jd = tret[0]
            
            if eclipse_jd >= jd_end:
                break
            
            # Get eclipse position (where maximum)
            try:
                where = swe.sol_eclipse_where(eclipse_jd, swe.FLG_SWIEPH)
                max_lon, max_lat = where[1][0], where[1][1]
            except:
                max_lon, max_lat = None, None
            
            # Check visibility from Chiang Rai
            try:
                how = swe.sol_eclipse_how(eclipse_jd, [LON, LAT, 0], swe.FLG_SWIEPH)
                coverage = how[1][0]  # fraction of diameter covered
                is_visible = coverage > 0 and how[1][5] > 0  # above horizon
            except:
                coverage = 0
                is_visible = False
            
            # Eclipse longitude = Sun/Moon conjunction longitude
            arr, _ = swe.calc_ut(eclipse_jd, swe.SUN, swe.FLG_SWIEPH)
            eclipse_lon = arr[0]
            
            eclipses.append({
                'jd': eclipse_jd,
                'type': 'Solar',
                'subtype': get_eclipse_type(retflag),
                'central': is_central(retflag),
                'lon': eclipse_lon,
                'max_lat': max_lat,
                'max_lon': max_lon,
                'coverage': coverage,
                'visible': is_visible,
            })
            
            jd = eclipse_jd + 1
        except Exception as e:
            break
    
    return eclipses

def find_lunar_eclipses(year):
    """Find all lunar eclipses in a year."""
    eclipses = []
    jd_start = swe.julday(year, 1, 1, 0)
    jd_end = swe.julday(year + 1, 1, 1, 0)
    
    jd = jd_start
    while jd < jd_end:
        try:
            result = swe.lun_eclipse_when(jd, swe.FLG_SWIEPH, 0, False)
            retflag = result[0]
            tret = result[1]
            eclipse_jd = tret[0]
            
            if eclipse_jd >= jd_end:
                break
            
            # Get Moon position at eclipse
            arr, _ = swe.calc_ut(eclipse_jd, swe.MOON, swe.FLG_SWIEPH)
            moon_lon = arr[0]
            
            # Lunar eclipses visible from night side
            # Check if Moon above horizon at Chiang Rai
            try:
                how = swe.lun_eclipse_how(eclipse_jd, [LON, LAT, 0], swe.FLG_SWIEPH)
                coverage = how[1][0]  # umbral magnitude
                is_visible = how[1][5] > 0  # Moon above horizon
            except:
                coverage = tret[8] if len(tret) > 8 else 0  # fallback
                is_visible = True  # Generally visible from night side
            
            eclipses.append({
                'jd': eclipse_jd,
                'type': 'Lunar',
                'subtype': get_eclipse_type(retflag),
                'central': "",
                'lon': moon_lon,
                'max_lat': None,
                'max_lon': None,
                'coverage': coverage,
                'visible': is_visible,
            })
            
            jd = eclipse_jd + 1
        except Exception as e:
            break
    
    return eclipses

def check_natal_aspects(eclipse_lon, orb):
    """Check which natal planets the eclipse aspects."""
    aspects_found = []
    natal = get_chart(jd_natal)
    
    for n_name in PLANETS:
        a = aspect_angle(eclipse_lon, natal[n_name])
        for deg, sym, nm in ASPECTS:
            if abs(a - deg) <= orb:
                house = get_house(natal[n_name])
                aspects_found.append({
                    'planet': n_name,
                    'aspect': sym,
                    'name': nm,
                    'orb': abs(a - deg),
                    'natal_pos': sign_str(natal[n_name]),
                    'house': house,
                })
                break
    
    return aspects_found

def get_house(natal_lon):
    """Get natal house for a planet."""
    asc_arr = swe.houses(jd_natal, LAT, LON, b'P')
    cusps = asc_arr[0] if len(asc_arr[0]) == 12 else asc_arr[0][1:13]
    for i in range(11):
        c1, c2 = cusps[i], cusps[i+1]
        if c2 < c1 and (natal_lon >= c1 or natal_lon < c2): return i+1
        if c1 <= natal_lon < c2: return i+1
    return 12

def get_natal_sign_for_lon(lon):
    s = int(lon // 30)
    return SIGNS[s]

def get_eclipse_themes(ecl_type, subtype, aspects, eclipse_lon):
    """Generate astrological themes."""
    themes = []
    s = int((eclipse_lon % 360) // 30)
    sign = SIGNS[s]
    
    # Sign-based general meaning
    sign_meanings = {
        0: "new beginnings, identity, self-assertion",
        1: "values, finances, self-worth, security",
        2: "communication, learning, siblings, local travel",
        3: "home, family, emotions, roots, endings",
        4: "creativity, romance, children, self-expression",
        5: "work, health, daily routines, service",
        6: "relationships, partnerships, contracts, balance",
        7: "transformation, shared resources, intimacy, crisis",
        8: "expansion, philosophy, travel, higher learning",
        9: "career, public standing, authority, achievement",
        10: "community, friends, future vision, innovation",
        11: "spirituality, dissolution, transcendence, hidden matters",
    }
    
    if ecl_type == 'Solar':
        themes.append(f"Solar eclipse in {sign}: External turning point around {sign_meanings.get(s, 'transformation')}. New 6-18 month cycle begins.")
    else:
        themes.append(f"Lunar eclipse in {sign}: Emotional culmination, release, or closure around {sign_meanings.get(s, 'transformation')}. Full moon intensified.")
    
    # Aspect-based themes
    for asp in aspects:
        p = asp['planet']
        h = asp['house']
        sym = asp['aspect']
        orb = asp['orb']
        
        if orb < 2:
            intensity = "MAJOR"
        elif orb < 5:
            intensity = "Strong"
        else:
            intensity = "Moderate"
        
        themes.append(f"  → {intensity} {sym} natal {p} (H{h}): Activates {p.lower()} energy in your {h}{'th' if h not in [1,2,3] else {1:'st',2:'nd',3:'rd'}[h]} house domain")
    
    return themes

# ─── MAIN ───
if __name__ == "__main__":
    year = int(sys.argv[1]) if len(sys.argv) > 1 else datetime.now().year
    orb = float(sys.argv[2]) if len(sys.argv) > 2 else 8.0
    
    # Calculate natal JD
    ny, nm, nd = map(int, NATAL_DATE.split('-'))
    nth, ntm = map(int, NATAL_TIME.split(':'))
    dt_natal = datetime(ny, nm, nd, nth, ntm, tzinfo=timezone.utc) - timedelta(hours=TZ)
    jd_natal = swe.julday(dt_natal.year, dt_natal.month, dt_natal.day, dt_natal.hour + dt_natal.minute/60.0)
    
    print(f"\n{'='*75}")
    print(f"  ECLIPSES FOR BOOM — {year}")
    print(f"  Natal: {NATAL_DATE} {NATAL_TIME} ICT | {LAT}°N, {LON}°E")
    print(f"  Aspect orb: {orb}°")
    print(f"{'='*75}")
    
    # Find eclipses
    solar = find_solar_eclipses(year)
    lunar = find_lunar_eclipses(year)
    all_eclipses = sorted(solar + lunar, key=lambda x: x['jd'])
    
    if not all_eclipses:
        print("No eclipses found for this year.")
        swe.close()
        sys.exit(0)
    
    for ecl in all_eclipses:
        dt = jd_to_datetime(ecl['jd'], TZ)
        eclipse_lon = ecl['lon'] % 360
        
        print(f"\n{'─'*75}")
        print(f"  {ecl['type'].upper()} ECLIPSE — {dt.strftime('%Y-%m-%d %H:%M')} ICT")
        print(f"  Type: {ecl['subtype']}")
        if ecl['central']:
            print(f"  Path: {ecl['central']}")
        print(f"  Position: {sign_str(eclipse_lon)}")
        
        if ecl['type'] == 'Solar':
            if ecl['max_lat'] is not None:
                print(f"  Max visibility: {ecl['max_lat']:.1f}°N, {ecl['max_lon']:.1f}°E")
            if ecl['visible']:
                print(f"  Chiang Rai visibility: YES (coverage {ecl['coverage']:.1%})")
            else:
                print(f"  Chiang Rai visibility: NO")
        else:
            if ecl['coverage'] > 0:
                print(f"  Umbral magnitude: {ecl['coverage']:.2f}")
            if ecl['visible']:
                print(f"  Chiang Rai visibility: Moon above horizon")
            else:
                print(f"  Chiang Rai visibility: Moon below horizon")
        
        # Natal aspects
        aspects = check_natal_aspects(eclipse_lon, orb)
        if aspects:
            print(f"\n  NATAL ASPECTS (within {orb}°):")
            for asp in sorted(aspects, key=lambda x: x['orb']):
                exact = "★ EXACT" if asp['orb'] < 2 else ""
                print(f"    {asp['aspect']} {asp['planet']:8} (H{asp['house']})  {asp['natal_pos']:12}  orb {asp['orb']:4.1f}° {exact}")
        else:
            print(f"\n  No major natal aspects within {orb}°")
        
        # Themes
        themes = get_eclipse_themes(ecl['type'], ecl['subtype'], aspects, eclipse_lon)
        print(f"\n  THEMES:")
        for t in themes:
            print(f"    • {t}")
    
    print(f"\n{'='*75}")
    print(f"  Total eclipses in {year}: {len(all_eclipses)} ({len(solar)} solar, {len(lunar)} lunar)")
    print(f"{'='*75}")
    
    swe.close()
