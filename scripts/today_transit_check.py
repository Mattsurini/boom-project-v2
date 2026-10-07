"""
Today's Transit Chart for Boom Project
Birth: 1996-11-20 20:37 ICT, Chiang Rai
Cancer Rising (11° 42')
Venus in Libra 26° 55'

Generates transit positions and transiting-to-natal aspects for today.
"""
from datetime import datetime, timezone, timedelta
import sys
sys.path.insert(0, "/e/Boom Project/.venv/Lib/site-packages")
try:
    from xalen import swe
except ImportError:
    import swisseph as swe

swe.set_ephe_path(None)

# Boom's natal data
NATAL_DATE = datetime(1996, 11, 20, 20, 37, tzinfo=timezone(timedelta(hours=7)))
CITY_LAT, CITY_LON = 19.9071, 99.8328  # Chiang Rai, Thailand
HOUSE_SYSTEM = b'P'  # Placidus

# Planet mappings
PLANET_IDS = {
    "Sun": swe.SUN, "Moon": swe.MOON, "Mercury": swe.MERCURY,
    "Venus": swe.VENUS, "Mars": swe.MARS, "Jupiter": swe.JUPITER,
    "Saturn": swe.SATURN, "Uranus": swe.URANUS, "Neptune": swe.NEPTUNE,
    "Pluto": swe.PLUTO, "North Node": swe.TRUE_NODE
}

ZODIAC_SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
                "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]

ZODIAC_SYMBOLS = ["♈", "♉", "♊", "♋", "♌", "♍", "♎", "♏", "♐", "♑", "♒", "♓"]

# Boom Project aspect orbs
# Canonical rule = moiety, per stellium.engines.orbs.BOOM_FULL_ORBS:
# effective orb for a pair = (full_orb_A + full_orb_B) / 2.
BOOM_FULL_ORBS = {
    "Sun": 10.0, "Moon": 11.0, "Mercury": 7.0, "Venus": 6.0, "Mars": 7.0,
    "Jupiter": 8.0, "Saturn": 5.0, "Uranus": 5.0, "Neptune": 7.0, "Pluto": 5.0,
}

# Aspect angle only; the orb allowance is derived per pair from BOOM_FULL_ORBS.
ASPECT_ORBS = {
    "Conjunction": 0, "Semi-Sextile": 30, "Semi-Square": 45,
    "Sextile": 60, "Square": 90, "Trine": 120,
    "Quincunx": 150, "Opposition": 180
}


def effective_orb(a, b):
    """Moiety orb allowance for a planet pair."""
    return (BOOM_FULL_ORBS[a] + BOOM_FULL_ORBS[b]) / 2

SYMBOLS = {"Conjunction": "☌", "Sextile": "⚹", "Square": "□", "Trine": "△", 
           "Opposition": "☍", "Quincunx": "⊛", "Semi-Sextile": "∘", "Semi-Square": "⁂"}

ASPECT_ANGLES = {0: "Conjunction", 60: "Sextile", 90: "Square", 
                 120: "Trine", 180: "Opposition", 150: "Quincunx", 30: "Semi-Sextile", 45: "Semi-Square"}

def local_to_utc(dt):
    """Convert ICT time to UTC."""
    return dt - timedelta(hours=7)

def jd_from_datetime(dt):
    """Calculate Julian Day from datetime in UTC."""
    return swe.julday(dt.year, dt.month, dt.day, dt.hour + dt.minute/60 + dt.second/3600)

def calc_chart(date_time, lat, geo_lon):
    """Calculate all planetary positions and houses."""
    utc_dt = local_to_utc(date_time)
    jd = jd_from_datetime(utc_dt)
    
    planets = {}
    for name, pid in PLANET_IDS.items():
        flags = swe.FLG_SWIEPH
        arr = swe.calc_ut(jd, pid, flags)
        plon = arr[0][0]
        speed = arr[0][3]
        planets[name] = {
            "longitude": plon,
            "sign": ZODIAC_SIGNS[int(plon // 30) % 12],
            "sign_num": int(plon // 30) % 12,
            "degree": round(plon % 30, 2),
            "retrograde": speed < 0
        }
    
    # Calculate houses (geo_lon = site east longitude; keep name distinct from planet lons)
    houses_data = swe.houses(jd, lat, geo_lon, HOUSE_SYSTEM)
    cusps = list(houses_data[0])
    ascmc = list(houses_data[1])
    asc = ascmc[0] if len(ascmc) > 0 else cusps[0]
    mc = ascmc[1] if len(ascmc) > 1 else (asc + 90) % 360
    
    houses = {}
    for i in range(1, 13):
        cusp_lon = cusps[i-1] if i-1 < len(cusps) else (asc + (i-1)*30) % 360
        houses[i] = {
            "cusp": round(cusp_lon, 2),
            "sign": ZODIAC_SIGNS[int(cusp_lon // 30) % 12],
            "sign_num": int(cusp_lon // 30) % 12,
            "degree": round(cusp_lon % 30, 2)
        }
    
    return {"planets": planets, "houses": houses, "asc": asc, "mc": mc, "jd": jd}

def house_of(longitude, cusps):
    """Find which house a longitude falls into."""
    lon = longitude % 360
    for i in range(12):
        c1, c2 = cusps[i], cusps[(i + 1) % 12]
        if c2 < c1:
            if lon >= c1 or lon < c2:
                return i + 1
        elif c1 <= lon < c2:
            return i + 1
    return 12

def angle_diff(a, b):
    """Calculate the shortest angular distance."""
    d = abs((a - b) % 360)
    return 360 - d if d > 180 else d

def main():
    # Get today's date in ICT
    today = datetime.now(timezone(timedelta(hours=7)))
    trans_time = today.replace(hour=12, minute=0, second=0, microsecond=0)
    
    print("=" * 60)
    print(f"BOOM PROJECT TRANSIT CHART — {today.strftime('%d.%m.%Y')} 12:00 ICT")
    print("=" * 60)
    print()
    
    # Calculate natal chart
    print("Calculating natal chart...")
    natal = calc_chart(NATAL_DATE, CITY_LAT, CITY_LON)
    
    # Calculate transit chart  
    print("Calculating transit chart...")
    transit = calc_chart(trans_time, CITY_LAT, CITY_LON)
    
    # Transit planets to show
    trans_planet_list = ["Sun", "Moon", "Mercury", "Venus", "Mars", 
                         "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"]
    
    # Natal planets (exclude nodes)
    nat_planets = {p: d for p, d in natal["planets"].items() if p != "North Node"}
    cusps = [natal["houses"][i]["cusp"] for i in range(1, 13)]
    
    print()
    print("=== TRANSIT POSITIONS (Natal Houses) ===")
    print()
    
    for planet in trans_planet_list:
        if planet in transit["planets"]:
            p = transit["planets"][planet]
            house = house_of(p["longitude"], cusps)
            sign_num = p["sign_num"]
            sym = ZODIAC_SYMBOLS[sign_num]
            print(f"  {planet:9} {sym} {p['sign']:12} {p['degree']:.2f}°  → House {house}")
    
    print()
    print("=== TRANSIT → NATAL ASPECTS ===")
    print()
    
    # Calculate transiting-to-natal aspects
    aspects = []
    for t_name in trans_planet_list:
        if t_name not in transit["planets"]:
            continue
        t_lon = transit["planets"][t_name]["longitude"]
        
        for n_name, n_data in nat_planets.items():
            n_lon = n_data["longitude"]
            angle = angle_diff(t_lon, n_lon)
            
            # Find the best aspect (closest orb) for this pair, using the
            # moiety allowance for this specific transiting/natal pair.
            best_asp = None
            best_orb = None
            best_deg = None
            max_orb = effective_orb(t_name, n_name)

            for asp_name, asp_deg in ASPECT_ORBS.items():
                orb = abs(angle - asp_deg)
                if orb <= max_orb and (best_orb is None or orb < best_orb):
                    best_asp = asp_name
                    best_orb = orb
                    best_deg = asp_deg

            if best_asp:
                aspects.append({
                    "transit": t_name,
                    "aspect": best_asp,
                    "natal": n_name,
                    "natal_sign": n_data["sign"],
                    "orb": round(best_orb, 2),
                    "angle": best_deg,
                    "max_orb": max_orb,
                    "house": house_of(t_lon, cusps)
                })
    
    aspects.sort(key=lambda x: x["orb"])
    
    tight_cut = 2.5
    for asp in aspects:
        sym = SYMBOLS.get(asp["aspect"], "○")
        mark = "*" if asp["orb"] <= tight_cut else " "
        print(f" {mark}{asp['orb']:5.2f}°  {asp['transit']:8} {sym} {asp['natal']:8} "
              f"(natal {asp['natal_sign'][:3]}, transit H{asp['house']:2d}, max {asp['max_orb']:.1f}°) — {asp['aspect']}")
    tight = sum(1 for a in aspects if a["orb"] <= tight_cut)
    
    print()
    print("=" * 60)
    print(f"\nSummary: {len(trans_planet_list)} transiting planets, {len(aspects)} aspects to natal "
          f"({tight} within {tight_cut}°)")
    print("* = tight aspect. Orbs are moiety: (full_A + full_B)/2 per stellium.engines.orbs.BOOM_FULL_ORBS.")

if __name__ == "__main__":
    main()
