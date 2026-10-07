#!/usr/bin/env python3
"""
natal_chart.py — Birth data → Swiss Ephemeris → Interpretation lookup
Pipeline: parse birth → compute chart → query DB → structured report

Usage:
  python natal_chart.py --name "Boom" --date "1996-11-20" --time "20:37" --tz "ICT" --location "Chiang Rai, Thailand"
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, r"E:\Boom Project\scripts")

import argparse
import json
import math
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from pathlib import Path

import swisseph as swe
from astrology_db import search_summary, search

# Set ephemeris path and fallback to Moshier if files missing
EPHE_PATH = r"E:\Boom Project\.ephe"
swe.set_ephe_path(EPHE_PATH)

# Use Moshier built-in ephemeris (no external files needed)
EPHE_FLAGS = swe.FLG_MOSEPH

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
PLANETS = {
    "Sun": swe.SUN,
    "Moon": swe.MOON,
    "Mercury": swe.MERCURY,
    "Venus": swe.VENUS,
    "Mars": swe.MARS,
    "Jupiter": swe.JUPITER,
    "Saturn": swe.SATURN,
    "Uranus": swe.URANUS,
    "Neptune": swe.NEPTUNE,
    "Pluto": swe.PLUTO,
    "North Node": swe.TRUE_NODE,
    "South Node": swe.TRUE_NODE,  # computed as opposite
}

ZODIAC_SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer",
    "Leo", "Virgo", "Libra", "Scorpio",
    "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

ZODIAC_SYMBOLS = [
    "♈", "♉", "♊", "♋", "♌", "♍",
    "♎", "♏", "♐", "♑", "♒", "♓"
]

HOUSE_SYSTEMS = {
    "Placidus": b'P',
    "Koch": b'K',
    "Equal": b'E',
    "Whole Sign": b'W',
    "Campanus": b'C',
    "Regiomontanus": b'R',
    "Porphyry": b'O',
    "Topocentric": b'T',
    "Vedic (Equal from Asc)": b'A',
}

ASPECT_ORBS = {
    "Conjunction": (0, 8),
    "Semi-Sextile": (30, 2),
    "Semi-Square": (45, 2),
    "Sextile": (60, 6),
    "Square": (90, 8),
    "Trine": (120, 8),
    "Quincunx": (150, 3),
    "Opposition": (180, 8),
}

# ---------------------------------------------------------------------------
# Core Calculation
# ---------------------------------------------------------------------------

class NatalChart:
    def __init__(self, name: str, year: int, month: int, day: int,
                 hour: int, minute: int, tz_offset: float,
                 lat: float, lon: float, house_system: str = "Placidus"):
        self.name = name
        self.year = year
        self.month = month
        self.day = day
        self.hour = hour
        self.minute = minute
        self.tz_offset = tz_offset  # hours from UTC (e.g., ICT = +7)
        self.lat = lat
        self.lon = lon
        self.house_system = house_system
        
        # Compute Julian Day in UT
        self.jd = self._compute_jd()
        
        # Calculate
        self.planets = self._compute_planets()
        self.houses, self.ascendant, self.mc = self._compute_houses()
        self.aspects = self._compute_aspects()
    
    def _compute_jd(self) -> float:
        """Convert local time to UT and compute Julian Day."""
        # Local time as decimal hours
        local_decimal = self.hour + self.minute / 60.0
        # Convert to UT
        ut_decimal = local_decimal - self.tz_offset
        
        # Handle day wrap
        day = self.day
        month = self.month
        year = self.year
        if ut_decimal < 0:
            ut_decimal += 24
            # previous day
            from datetime import timedelta
            dt = datetime(year, month, day) - timedelta(days=1)
            year, month, day = dt.year, dt.month, dt.day
        elif ut_decimal >= 24:
            ut_decimal -= 24
            from datetime import timedelta
            dt = datetime(year, month, day) + timedelta(days=1)
            year, month, day = dt.year, dt.month, dt.day
        
        jd = swe.julday(year, month, day, ut_decimal)
        return jd
    
    def _compute_planets(self) -> Dict[str, Dict]:
        """Calculate all planetary positions."""
        result = {}
        
        for name, planet_id in PLANETS.items():
            if name == "South Node":
                # South node = opposite of North node
                nn = result.get("North Node", {})
                lon = (nn.get("longitude", 0) + 180) % 360
                result[name] = {
                    "longitude": lon,
                    "sign": self._lon_to_sign(lon),
                    "sign_num": int(lon // 30),
                    "degree": lon % 30,
                    "retrograde": nn.get("retrograde", False),
                }
                continue
            
            # swe.calc_ut returns (longitude, latitude, distance, speed_long, speed_lat, speed_dist)
            flags = EPHE_FLAGS
            if planet_id == swe.TRUE_NODE:
                flags |= swe.FLG_EQUATORIAL
            calc = swe.calc_ut(self.jd, planet_id, flags)
            lon = calc[0][0]
            speed = calc[0][3]
            
            result[name] = {
                "longitude": lon,
                "sign": self._lon_to_sign(lon),
                "sign_num": int(lon // 30),
                "degree": round(lon % 30, 2),
                "retrograde": speed < 0,
            }
        
        return result
    
    def _compute_houses(self) -> Tuple[Dict[int, Dict], float, float]:
        """Calculate house cusps."""
        hs_letter = HOUSE_SYSTEMS.get(self.house_system, b'P')
        
        # swe.houses returns (cusps, ascmc)
        houses_data = swe.houses(self.jd, self.lat, self.lon, hs_letter)
        
        cusps = houses_data[0]  # list of 13 cusps (1-12 + ascendant sometimes)
        # Actually houses_ex returns: (cusps, ascmc) where ascmc = [asc, mc, armc, eqasc, ...]
        # Let's handle both old and new API
        
        if isinstance(houses_data, tuple) and len(houses_data) >= 2:
            cusps_list = list(houses_data[0])
            ascmc = list(houses_data[1])
        else:
            # Fallback for older API
            cusps_list = list(houses_data)
            ascmc = [cusps_list[0], cusps_list[9]] if len(cusps_list) >= 10 else [0, 0]
        
        ascendant = ascmc[0] if len(ascmc) > 0 else cusps_list[0]
        mc = ascmc[1] if len(ascmc) > 1 else (ascendant + 90) % 360
        
        houses = {}
        for i in range(1, 13):
            idx = i - 1  # cusps[0] = House 1, cusps[11] = House 12
            cusp_lon = cusps_list[idx] if idx < len(cusps_list) else ((ascendant + (i-1)*30) % 360)
            houses[i] = {
                "cusp": round(cusp_lon, 2),
                "sign": self._lon_to_sign(cusp_lon),
                "sign_num": int(cusp_lon // 30),
                "degree": round(cusp_lon % 30, 2),
            }
        
        return houses, round(ascendant, 2), round(mc, 2)
    
    def _lon_to_sign(self, longitude: float) -> str:
        sign_num = int(longitude // 30) % 12
        return ZODIAC_SIGNS[sign_num]
    
    def _compute_aspects(self) -> List[Dict]:
        """Calculate major aspects between planets."""
        aspects = []
        planet_names = list(self.planets.keys())
        
        for i in range(len(planet_names)):
            for j in range(i + 1, len(planet_names)):
                p1 = planet_names[i]
                p2 = planet_names[j]
                
                lon1 = self.planets[p1]["longitude"]
                lon2 = self.planets[p2]["longitude"]
                
                diff = abs(lon1 - lon2)
                if diff > 180:
                    diff = 360 - diff
                
                for aspect_name, (angle, orb) in ASPECT_ORBS.items():
                    if abs(diff - angle) <= orb:
                        aspects.append({
                            "planet1": p1,
                            "planet2": p2,
                            "aspect": aspect_name,
                            "angle": round(diff, 2),
                            "orb": round(abs(diff - angle), 2),
                        })
        
        # Sort by orb (tightest first)
        aspects.sort(key=lambda x: x["orb"])
        return aspects
    
    def get_planets_in_houses(self) -> Dict[int, List[str]]:
        """Map planets to houses."""
        mapping = {i: [] for i in range(1, 13)}
        
        for planet_name, data in self.planets.items():
            lon = data["longitude"]
            house = self._find_house(lon)
            mapping[house].append(planet_name)
        
        return mapping
    
    def _find_house(self, longitude: float) -> int:
        """Find which house a longitude falls into."""
        for i in range(1, 13):
            cusp_i = self.houses[i]["cusp"]
            next_i = self.houses[i + 1]["cusp"] if i < 12 else self.houses[1]["cusp"] + 360
            
            # Handle wrap-around
            if next_i < cusp_i:
                next_i += 360
            
            check_lon = longitude
            if check_lon < cusp_i:
                check_lon += 360
            
            if cusp_i <= check_lon < next_i:
                return i
        
        return 1  # Fallback
    
    def query_interpretations(self, max_excerpts: int = 5, max_chars: int = 8000) -> Dict:
        """Query astrology DB for relevant interpretations."""
        queries = []
        
        # Key placements to look up
        asc_sign = self._lon_to_sign(self.ascendant)
        queries.append(f"ascendant {asc_sign}")
        
        sun_sign = self.planets["Sun"]["sign"]
        queries.append(f"sun in {sun_sign}")
        
        moon_sign = self.planets["Moon"]["sign"]
        queries.append(f"moon in {moon_sign}")
        
        # House placements
        house_mapping = self.get_planets_in_houses()
        for house_num, planets in house_mapping.items():
            if planets:
                for p in planets[:2]:  # Limit to 2 per house
                    queries.append(f"{p.lower()} in {house_num}th house")
        
        # Aspects
        for asp in self.aspects[:5]:
            queries.append(f"{asp['planet1'].lower()} {asp['aspect'].lower()} {asp['planet2'].lower()}")
        
        results = {}
        total_chars = 0
        
        for q in queries:
            excerpts = search(q, max_results=2, max_total_chars=max_chars - total_chars)
            if excerpts:
                results[q] = excerpts
                total_chars += sum(len(e["context"]) for e in excerpts)
            
            if total_chars >= max_chars:
                break
        
        return results
    
    def to_dict(self) -> Dict:
        """Serialize chart to dict."""
        return {
            "meta": {
                "name": self.name,
                "birth_date": f"{self.year:04d}-{self.month:02d}-{self.day:02d}",
                "birth_time": f"{self.hour:02d}:{self.minute:02d}",
                "tz_offset": self.tz_offset,
                "location": {"lat": self.lat, "lon": self.lon},
                "house_system": self.house_system,
                "julian_day": self.jd,
            },
            "planets": self.planets,
            "houses": self.houses,
            "angles": {
                "ascendant": self.ascendant,
                "mc": self.mc,
            },
            "aspects": self.aspects,
            "house_mapping": self.get_planets_in_houses(),
        }
    
    def to_markdown(self, interpretations: Optional[Dict] = None) -> str:
        """Format chart as markdown report."""
        m = self.to_dict()
        
        lines = [
            f"# Natal Chart: {self.name}",
            "",
            f"**Birth:** {m['meta']['birth_date']} {m['meta']['birth_time']} (UTC{'+' if self.tz_offset >= 0 else ''}{self.tz_offset})  ",
            f"**Location:** {self.lat:.4f}N, {self.lon:.4f}E  ",
            f"**House System:** {self.house_system}  ",
            f"**Julian Day:** {self.jd:.6f}",
            "",
            "---",
            "",
            "## Planetary Positions",
            "",
            "| Planet | Sign | Degree | Retro |",
            "|--------|------|--------|-------|",
        ]
        
        for planet_name, data in self.planets.items():
            retro = "℞" if data["retrograde"] else ""
            sym = ZODIAC_SYMBOLS[data["sign_num"]]
            lines.append(f"| {planet_name} | {sym} {data['sign']} | {data['degree']:.2f}° | {retro} |")
        
        lines.extend([
            "",
            "## Houses",
            "",
            "| House | Cusp | Sign |",
            "|-------|------|------|",
        ])
        
        for i in range(1, 13):
            h = self.houses[i]
            sym = ZODIAC_SYMBOLS[h["sign_num"]]
            lines.append(f"| {i} | {h['degree']:.2f}° | {sym} {h['sign']} |")
        
        lines.extend([
            "",
            "## Angles",
            "",
            f"- **Ascendant:** {self.ascendant:.2f}° ({self._lon_to_sign(self.ascendant)})",
            f"- **MC (Midheaven):** {self.mc:.2f}° ({self._lon_to_sign(self.mc)})",
            "",
            "## House Placements",
            "",
        ])
        
        mapping = self.get_planets_in_houses()
        for i in range(1, 13):
            planets = mapping.get(i, [])
            if planets:
                lines.append(f"**House {i}:** {', '.join(planets)}")
        
        lines.extend([
            "",
            "## Major Aspects",
            "",
            "| Planet 1 | Aspect | Planet 2 | Orb |",
            "|----------|--------|----------|-----|",
        ])
        
        for asp in self.aspects[:15]:
            lines.append(f"| {asp['planet1']} | {asp['aspect']} | {asp['planet2']} | {asp['orb']}° |")
        
        if interpretations:
            lines.extend([
                "",
                "---",
                "",
                "## Database Interpretations",
                "",
            ])
            
            for query, excerpts in interpretations.items():
                lines.append(f"### Query: {query}")
                lines.append("")
                for ex in excerpts[:3]:
                    preview = ex["context"][:400].replace("\n", " ")
                    lines.append(f"- *{ex['file']}:{ex['line']}* — {preview}...")
                    lines.append("")
        
        return "\n".join(lines)

# ---------------------------------------------------------------------------
# Geocoding helpers
# ---------------------------------------------------------------------------

LOCATION_COORDS = {
    "chiang rai": (19.9071, 99.8328),
    "chiang rai, thailand": (19.9071, 99.8328),
    "bangkok": (13.7563, 100.5018),
    "bangkok, thailand": (13.7563, 100.5018),
}

def resolve_location(location_str: str) -> Tuple[float, float]:
    """Simple location resolver. Extend with geocoding API if needed."""
    key = location_str.lower().strip()
    if key in LOCATION_COORDS:
        return LOCATION_COORDS[key]
    
    # Default fallback
    print(f"WARNING: Unknown location '{location_str}'. Using Chiang Rai as default.")
    return (19.9071, 99.8328)

# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Natal Chart Calculator + DB Interpretation")
    parser.add_argument("--name", "-n", default="Querent", help="Person's name")
    parser.add_argument("--date", "-d", required=True, help="Birth date YYYY-MM-DD")
    parser.add_argument("--time", "-t", required=True, help="Birth time HH:MM (24h)")
    parser.add_argument("--tz", default="ICT", help="Timezone offset or name (e.g., ICT=+7, EST=-5)")
    parser.add_argument("--location", "-l", required=True, help="Birth location (city, country)")
    parser.add_argument("--house-system", "-hs", default="Placidus", choices=list(HOUSE_SYSTEMS.keys()))
    parser.add_argument("--json", action="store_true", help="Output raw JSON")
    parser.add_argument("--no-interpretation", action="store_true", help="Skip DB lookup")
    
    args = parser.parse_args()
    
    # Parse date
    year, month, day = map(int, args.date.split("-"))
    hour, minute = map(int, args.time.split(":"))
    
    # Parse timezone
    tz_offsets = {
        "ICT": 7, "BST": 6, "IST": 5.5, "CET": 1, "CEST": 2,
        "GMT": 0, "UTC": 0, "EST": -5, "EDT": -4, "CST": -6,
        "CDT": -5, "MST": -7, "MDT": -6, "PST": -8, "PDT": -7,
        "JST": 9, "AEST": 10, "AEDT": 11,
    }
    
    if args.tz in tz_offsets:
        tz = tz_offsets[args.tz]
    else:
        try:
            tz = float(args.tz)
        except ValueError:
            print(f"WARNING: Unknown timezone '{args.tz}'. Using +7 (ICT).")
            tz = 7
    
    # Resolve location
    lat, lon = resolve_location(args.location)
    
    # Build chart
    chart = NatalChart(
        name=args.name,
        year=year, month=month, day=day,
        hour=hour, minute=minute,
        tz_offset=tz,
        lat=lat, lon=lon,
        house_system=args.house_system
    )
    
    # Query interpretations
    interpretations = None
    if not args.no_interpretation:
        print("Querying astrology database for interpretations...")
        interpretations = chart.query_interpretations()
        print(f"Retrieved {len(interpretations)} interpretation queries.\n")
    
    # Output
    if args.json:
        data = chart.to_dict()
        data["interpretations"] = interpretations
        print(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        print(chart.to_markdown(interpretations))

if __name__ == "__main__":
    main()
