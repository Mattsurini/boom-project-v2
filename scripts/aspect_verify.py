#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
aspect_verify.py — Verify a reference aspect list against freshly computed
positions, and confirm the set is complete (two-way).

Reference lists come from Astro-Seek (major-aspect default). This tool
reproduces Astro-Seek's orb rule exactly, so a correct reference list yields a
clean two-way PASS (0 missing, 0 extra).

Usage:
    python aspect_verify.py <DD.MM.YYYY> <HH:MM> <city> <reference.txt>
                            [--tol 0.01] [--tns] [--minor]

Example:
    python aspect_verify.py 19.11.2015 18:18 chiang-rai ref_2015.txt

Reference file format (one aspect per line, the exact shape you paste):
    Sun Square Moon (Orb: 2°35', Separating)
    Sun Conjunction Mercury (Orb: 1°04', Separating)
    ...

Hard pass criteria (both must hold for PASS / exit 0):
  1. Collection match (two-way): every aspect in the reference file is found
     in the computed set, AND every computed aspect is in the reference file.
  2. Orb match: for each reference aspect, |computed_orb - reference_orb|
     <= --tol (default 0.02° — Astro-Seek sources round to 1' and use a
     slightly different ephemeris, so deltas run ~0.010-0.016°).

Applying/separating is computed and DISPLAYED as info only — it never affects
the pass/fail verdict.

Exit code: 0 = PASS, 1 = FAIL, 2 = usage/input error.
"""
import sys
import io
import os
import re
import math
import argparse
from datetime import datetime, timedelta

# ─── Load ephemeris: xalen (preferred) → swisseph fallback ────────────────
swe = None
try:
    from xalen import swe
except Exception:
    try:
        import swisseph as swe
    except Exception:
        print("ERROR: no ephemeris library found (tried xalen, swisseph).")
        sys.exit(2)

# Fix Windows console encoding for unicode aspect glyphs
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")


# ─── Bodies ────────────────────────────────────────────────────────────────
PLANETS = ["Sun", "Moon", "Mercury", "Venus", "Mars",
           "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"]
TNS = ["Cupido", "Hades", "Zeus", "Kronos", "Apollon", "Admetos",
       "Vulcanus", "Poseidon"]
BODY_CODES = {
    "Sun": 0, "Moon": 1, "Mercury": 2, "Venus": 3, "Mars": 4,
    "Jupiter": 5, "Saturn": 6, "Uranus": 7, "Neptune": 8, "Pluto": 9,
    "Cupido": 40, "Hades": 41, "Zeus": 42, "Kronos": 43,
    "Apollon": 44, "Admetos": 45, "Vulcanus": 46, "Poseidon": 47,
}
LUMINARIES = {"Sun", "Moon"}

# ─── Aspect targets ────────────────────────────────────────────────────────
ASPECT_TARGETS = {
    "conjunction": 0, "sextile": 60, "square": 90, "trine": 120,
    "opposition": 180,
    # minor
    "semisextile": 30, "semi-sextile": 30, "semisquare": 45, "semi-square": 45,
    "biquintile": 72, "bi-quintile": 72, "trisquare": 135, "tri-square": 135,
    "sesquiquadrate": 135, "biqintile": 144, "bi-quintile": 144,
    "quincunx": 150, "inconjunct": 150,
}
MAJOR_TARGETS = {0, 60, 90, 120, 180}
MINOR_TARGETS = {30, 45, 72, 135, 144, 150}
ASPECT_SYMS = {0: "☌", 60: "✶", 90: "□", 120: "△", 180: "☍",
               30: "⚺", 45: "∠", 72: "⚹", 135: "⚹", 144: "⚹", 150: "⚹"}


def seek_orb(name_a, name_b, target, include_minor):
    """Astro-Seek default orb rule (verified against the 2015-11-19 reference).

    Major 0/90/120/180: 7°, +3° if a luminary (Sun/Moon) is involved -> 10°.
    Sextile 60:         4°, +1.5° if a luminary is involved -> 5.5°.
    Minor 30/45/72/135/144/150: 2.5° fixed (only when include_minor).
    Returns None if the aspect is not part of the scan.
    """
    lum = (name_a in LUMINARIES) or (name_b in LUMINARIES)
    if target == 60:
        return 5.5 if lum else 4.0
    if target in (0, 90, 120, 180):
        return 10.0 if lum else 7.0
    if include_minor and target in MINOR_TARGETS:
        return 2.5
    return None


# ─── City / coordinate / timezone lookup (same as natal_chart_swe.py) ──────
CITY_DB = {
    "izhevsk": {"lat": 56.8519, "lon": 53.2114, "tz": "Europe/Samara", "name": "Izhevsk, Russia"},
    "moscow": {"lat": 55.7558, "lon": 37.6173, "tz": "Europe/Moscow", "name": "Moscow, Russia"},
    "saint-petersburg": {"lat": 59.9343, "lon": 30.3351, "tz": "Europe/Moscow", "name": "Saint Petersburg, Russia"},
    "petersburg": {"lat": 59.9343, "lon": 30.3351, "tz": "Europe/Moscow", "name": "Saint Petersburg, Russia"},
    "spb": {"lat": 59.9343, "lon": 30.3351, "tz": "Europe/Moscow", "name": "Saint Petersburg, Russia"},
    "yekaterinburg": {"lat": 56.8389, "lon": 60.6057, "tz": "Asia/Yekaterinburg", "name": "Yekaterinburg, Russia"},
    "novosibirsk": {"lat": 55.0084, "lon": 82.9357, "tz": "Asia/Novosibirsk", "name": "Novosibirsk, Russia"},
    "kazan": {"lat": 55.7887, "lon": 49.1221, "tz": "Europe/Moscow", "name": "Kazan, Russia"},
    "nizhny-novgorod": {"lat": 56.2965, "lon": 43.9361, "tz": "Europe/Moscow", "name": "Nizhny Novgorod, Russia"},
    "samara": {"lat": 53.2001, "lon": 50.1500, "tz": "Europe/Samara", "name": "Samara, Russia"},
    "rostov-na-donu": {"lat": 47.2357, "lon": 39.7015, "tz": "Europe/Moscow", "name": "Rostov-on-Don, Russia"},
    "voronezh": {"lat": 51.6720, "lon": 39.1843, "tz": "Europe/Moscow", "name": "Voronezh, Russia"},
    "krasnodar": {"lat": 45.0355, "lon": 38.9753, "tz": "Europe/Moscow", "name": "Krasnodar, Russia"},
    "ufa": {"lat": 54.7388, "lon": 55.9721, "tz": "Asia/Yekaterinburg", "name": "Ufa, Russia"},
    "volgograd": {"lat": 48.7080, "lon": 44.5133, "tz": "Europe/Moscow", "name": "Volgograd, Russia"},
    "perm": {"lat": 58.0105, "lon": 56.2502, "tz": "Asia/Yekaterinburg", "name": "Perm, Russia"},
    "tyumen": {"lat": 57.1522, "lon": 65.5272, "tz": "Asia/Yekaterinburg", "name": "Tyumen, Russia"},
    "omsk": {"lat": 54.9885, "lon": 73.3242, "tz": "Asia/Omsk", "name": "Omsk, Russia"},
    "barnaul": {"lat": 53.3548, "lon": 83.7698, "tz": "Asia/Barnaul", "name": "Barnaul, Russia"},
    "irkutsk": {"lat": 52.2978, "lon": 104.2964, "tz": "Asia/Irkutsk", "name": "Irkutsk, Russia"},
    "khabarovsk": {"lat": 48.4827, "lon": 135.0839, "tz": "Asia/Vladivostok", "name": "Khabarovsk, Russia"},
    "vladivostok": {"lat": 43.1332, "lon": 131.9113, "tz": "Asia/Vladivostok", "name": "Vladivostok, Russia"},
    "yaroslavl": {"lat": 57.6261, "lon": 39.8845, "tz": "Europe/Moscow", "name": "Yaroslavl, Russia"},
    "tolyatti": {"lat": 53.5303, "lon": 49.3461, "tz": "Europe/Samara", "name": "Tolyatti, Russia"},
    "chelyabinsk": {"lat": 55.1644, "lon": 61.4368, "tz": "Asia/Yekaterinburg", "name": "Chelyabinsk, Russia"},
    "saratov": {"lat": 51.5336, "lon": 46.0343, "tz": "Europe/Samara", "name": "Saratov, Russia"},
    "minsk": {"lat": 53.9045, "lon": 27.5615, "tz": "Europe/Minsk", "name": "Minsk, Belarus"},
    "kiev": {"lat": 50.4501, "lon": 30.5234, "tz": "Europe/Kiev", "name": "Kyiv, Ukraine"},
    "almaty": {"lat": 43.2220, "lon": 76.8512, "tz": "Asia/Almaty", "name": "Almaty, Kazakhstan"},
    "tashkent": {"lat": 41.2995, "lon": 69.2401, "tz": "Asia/Tashkent", "name": "Tashkent, Uzbekistan"},
    "mozhga": {"lat": 56.4527, "lon": 52.2117, "tz": "Europe/Samara", "name": "Mozhga, Russia"},
    "london": {"lat": 51.5074, "lon": -0.1278, "tz": "Europe/London", "name": "London, UK"},
    "new-york": {"lat": 40.7128, "lon": -74.0060, "tz": "America/New_York", "name": "New York, USA"},
    "los-angeles": {"lat": 34.0522, "lon": -118.2437, "tz": "America/Los_Angeles", "name": "Los Angeles, USA"},
    "berlin": {"lat": 52.5200, "lon": 13.4050, "tz": "Europe/Berlin", "name": "Berlin, Germany"},
    "paris": {"lat": 48.8566, "lon": 2.3522, "tz": "Europe/Paris", "name": "Paris, France"},
    "tokyo": {"lat": 35.6762, "lon": 139.6503, "tz": "Asia/Tokyo", "name": "Tokyo, Japan"},
    "beijing": {"lat": 39.9042, "lon": 116.4074, "tz": "Asia/Shanghai", "name": "Beijing, China"},
    "dubai": {"lat": 25.2048, "lon": 55.2708, "tz": "Asia/Dubai", "name": "Dubai, UAE"},
    "singapore": {"lat": 1.3521, "lon": 103.8198, "tz": "Asia/Singapore", "name": "Singapore"},
    "istanbul": {"lat": 41.0082, "lon": 28.9784, "tz": "Europe/Istanbul", "name": "Istanbul, Turkey"},
    "tel-aviv": {"lat": 32.0853, "lon": 34.7818, "tz": "Asia/Jerusalem", "name": "Tel Aviv, Israel"},
    "mumbai": {"lat": 19.0760, "lon": 72.8777, "tz": "Asia/Kolkata", "name": "Mumbai, India"},
    "delhi": {"lat": 28.7041, "lon": 77.1025, "tz": "Asia/Kolkata", "name": "Delhi, India"},
    "seoul": {"lat": 37.5665, "lon": 126.9780, "tz": "Asia/Seoul", "name": "Seoul, South Korea"},
    "sydney": {"lat": -33.8688, "lon": 151.2093, "tz": "Australia/Sydney", "name": "Sydney, Australia"},
    "toronto": {"lat": 43.6532, "lon": -79.3832, "tz": "America/Toronto", "name": "Toronto, Canada"},
    "chicago": {"lat": 41.8781, "lon": -87.6298, "tz": "America/Chicago", "name": "Chicago, USA"},
    "madrid": {"lat": 40.4168, "lon": -3.7038, "tz": "Europe/Madrid", "name": "Madrid, Spain"},
    "rome": {"lat": 41.9028, "lon": 12.4964, "tz": "Europe/Rome", "name": "Rome, Italy"},
    "amsterdam": {"lat": 52.3676, "lon": 4.9041, "tz": "Europe/Amsterdam", "name": "Amsterdam, Netherlands"},
    "stockholm": {"lat": 59.3293, "lon": 18.0686, "tz": "Europe/Stockholm", "name": "Stockholm, Sweden"},
    "oslo": {"lat": 59.9139, "lon": 10.7522, "tz": "Europe/Oslo", "name": "Oslo, Norway"},
    "copenhagen": {"lat": 55.6761, "lon": 12.5683, "tz": "Europe/Copenhagen", "name": "Copenhagen, Denmark"},
    "helsinki": {"lat": 60.1699, "lon": 24.9384, "tz": "Europe/Helsinki", "name": "Helsinki, Finland"},
    "warsaw": {"lat": 52.2297, "lon": 21.0122, "tz": "Europe/Warsaw", "name": "Warsaw, Poland"},
    "prague": {"lat": 50.0755, "lon": 14.3788, "tz": "Europe/Prague", "name": "Prague, Czech Republic"},
    "bucharest": {"lat": 44.4268, "lon": 26.1025, "tz": "Europe/Bucharest", "name": "Bucharest, Romania"},
    "budapest": {"lat": 47.4979, "lon": 19.0402, "tz": "Europe/Budapest", "name": "Budapest, Hungary"},
    "athens": {"lat": 37.9838, "lon": 23.7275, "tz": "Europe/Athens", "name": "Athens, Greece"},
    "lisbon": {"lat": 38.7223, "lon": -9.1393, "tz": "Europe/Lisbon", "name": "Lisbon, Portugal"},
    "brussels": {"lat": 50.8466, "lon": 4.3522, "tz": "Europe/Brussels", "name": "Brussels, Belgium"},
    "zurich": {"lat": 47.3769, "lon": 8.5417, "tz": "Europe/Zurich", "name": "Zurich, Switzerland"},
    "vienna": {"lat": 48.2082, "lon": 16.3738, "tz": "Europe/Vienna", "name": "Vienna, Austria"},
    "chisinau": {"lat": 47.0105, "lon": 28.8638, "tz": "Europe/Chisinau", "name": "Chisinau, Moldova"},
    "riga": {"lat": 56.9496, "lon": 24.1052, "tz": "Europe/Riga", "name": "Riga, Latvia"},
    "vilnius": {"lat": 54.6870, "lon": 25.2796, "tz": "Europe/Vilnius", "name": "Vilnius, Lithuania"},
    "tallinn": {"lat": 59.4370, "lon": 24.7536, "tz": "Europe/Tallinn", "name": "Tallinn, Estonia"},
    "bangkok": {"lat": 13.7563, "lon": 100.5018, "tz": "Asia/Bangkok", "name": "Bangkok, Thailand"},
    "chiang-rai": {"lat": 19.9022, "lon": 99.8336, "tz": "Asia/Bangkok", "name": "Chiang Rai, Thailand"},
}
TZ_OFFSETS = {
    "Europe/Moscow": 3, "Europe/Samara": 4, "Asia/Yekaterinburg": 5,
    "Asia/Novosibirsk": 7, "Asia/Omsk": 6, "Asia/Barnaul": 7,
    "Asia/Irkutsk": 8, "Asia/Vladivostok": 10, "Europe/Minsk": 3,
    "Europe/Kiev": 2, "Asia/Almaty": 6, "Asia/Tashkent": 5,
    "Asia/Baku": 4, "Asia/Tbilisi": 4, "Asia/Yerevan": 4,
    "Europe/London": 0, "America/New_York": -5, "America/Los_Angeles": -8,
    "Europe/Berlin": 1, "Europe/Paris": 1, "Asia/Tokyo": 9,
    "Asia/Shanghai": 8, "Asia/Dubai": 4, "Asia/Singapore": 8,
    "Europe/Istanbul": 3, "Asia/Jerusalem": 2, "Asia/Kolkata": 5.5,
    "Asia/Seoul": 9, "Australia/Sydney": 11, "America/Toronto": -5,
    "America/Chicago": -6, "Europe/Madrid": 1, "Europe/Rome": 1,
    "Europe/Amsterdam": 1, "Europe/Stockholm": 1, "Europe/Oslo": 1,
    "Europe/Copenhagen": 1, "Europe/Helsinki": 2, "Europe/Warsaw": 1,
    "Europe/Prague": 1, "Europe/Bucharest": 2, "Europe/Budapest": 1,
    "Europe/Athens": 2, "Europe/Lisbon": 0, "Europe/Brussels": 1,
    "Europe/Zurich": 1, "Europe/Vienna": 1, "Europe/Chisinau": 2,
    "Europe/Riga": 2, "Europe/Vilnius": 2, "Europe/Tallinn": 2,
    "Asia/Bangkok": 7,
}


def find_city(city_name):
    key = city_name.strip().lower().replace(" ", "-")
    if key in CITY_DB:
        return CITY_DB[key]
    for k, v in CITY_DB.items():
        if key in k or k in key:
            return v
    return None


# ─── Position + aspect math ────────────────────────────────────────────────
def get_positions(jd, bodies):
    pos = {}
    for name in bodies:
        arr, _ = swe.calc_ut(jd, BODY_CODES[name], swe.FLG_SWIEPH | swe.FLG_SPEED)
        pos[name] = {"lon": arr[0], "speed": arr[3]}
    return pos


def folded_angle(l1, l2):
    d = abs(l1 - l2) % 360
    return d if d <= 180 else 360 - d


def orb_for(l1, l2, target):
    return abs(folded_angle(l1, l2) - target)


def applying_separating(pos, name_a, name_b, target, dt_hours=1.0):
    """Numerically: is the orb shrinking (applying) or growing (separating)?"""
    def orb_at(dt):
        la = (pos[name_a]["lon"] + pos[name_a]["speed"] * dt / 24.0) % 360
        lb = (pos[name_b]["lon"] + pos[name_b]["speed"] * dt / 24.0) % 360
        return orb_for(la, lb, target)
    now = orb_at(0.0)
    later = orb_at(dt_hours)
    return "Applying" if later < now else "Separating"


def scan_aspects(pos, include_minor):
    """Return {frozenset({a,b}): {aspect_name: orb}} for all in-orb aspects."""
    found = {}
    names = list(pos)
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, b = names[i], names[j]
            for aname, target in ASPECT_TARGETS.items():
                if target in MAJOR_TARGETS or include_minor:
                    allowance = seek_orb(a, b, target, include_minor)
                    if allowance is None:
                        continue
                    orb = orb_for(pos[a]["lon"], pos[b]["lon"], target)
                    if orb <= allowance:
                        found.setdefault(frozenset((a, b)), {})[aname] = orb
    return found


# ─── Reference file parsing ────────────────────────────────────────────────
REF_RE = re.compile(
    r"^\s*(\w+)\s+([A-Za-z\-]+)\s+(\w+)\s*\(Orb:\s*(\d+)°(\d+)[\u0027\u2019]\s*,\s*([A-Za-z]+)\)"
)


def parse_reference(path):
    refs = []
    with open(path, "r", encoding="utf-8") as f:
        for lineno, line in enumerate(f, 1):
            line = line.rstrip("\n")
            if not line.strip() or line.strip().startswith("#"):
                continue
            m = REF_RE.match(line)
            if not m:
                print(f"WARNING: line {lineno} not parsed, skipped: {line!r}")
                continue
            p1, aspect, p2, deg, minute, appsep = m.groups()
            refs.append({
                "p1": p1, "aspect": aspect.strip().lower(), "p2": p2,
                "orb": int(deg) + int(minute) / 60.0,
                "appsep": appsep.strip().capitalize(),
                "line": lineno,
            })
    return refs


def dms(deg):
    d = int(deg)
    m = (deg - d) * 60
    return f"{d}°{int(round(m)):02d}'"


def main():
    ap = argparse.ArgumentParser(
        description="Verify a reference aspect list against computed positions.")
    ap.add_argument("date", help="DD.MM.YYYY")
    ap.add_argument("time", help="HH:MM")
    ap.add_argument("city", help="city name (e.g. chiang-rai)")
    ap.add_argument("reference", help="path to reference aspect list")
    ap.add_argument("--tol", type=float, default=0.02,
                    help="orb match tolerance in degrees (default 0.02; "
                         "Astro-Seek sources round to 1' and sit at "
                         "~0.010-0.016° over 0.01)")
    ap.add_argument("--tns", action="store_true",
                    help="include the 8 Uranian TNS in the scan")
    ap.add_argument("--minor", action="store_true",
                    help="include minor aspects (30/45/72/135/144/150) in the scan")
    args = ap.parse_args()

    # ── Resolve city + JD ──
    city = find_city(args.city)
    if not city:
        print(f"ERROR: city '{args.city}' not found in the database.")
        sys.exit(2)
    tz_off = TZ_OFFSETS.get(city["tz"], 0)
    try:
        dt_local = datetime.strptime(f"{args.date} {args.time}", "%d.%m.%Y %H:%M")
    except ValueError:
        print(f"ERROR: bad date/time '{args.date} {args.time}' (want DD.MM.YYYY HH:MM).")
        sys.exit(2)
    dt_utc = dt_local - timedelta(hours=tz_off)
    jd = swe.julday(dt_utc.year, dt_utc.month, dt_utc.day,
                    dt_utc.hour + dt_utc.minute / 60.0)

    # ── Parse reference ──
    if not os.path.exists(args.reference):
        print(f"ERROR: reference file not found: {args.reference}")
        sys.exit(2)
    refs = parse_reference(args.reference)
    if not refs:
        print("ERROR: no parseable aspects in the reference file.")
        sys.exit(2)

    # Auto-enable minor scanning if the reference contains any minor aspect.
    include_minor = args.minor
    ref_has_minor = any(
        r["aspect"] in ASPECT_TARGETS
        and ASPECT_TARGETS[r["aspect"]] in MINOR_TARGETS
        for r in refs)
    if ref_has_minor and not args.minor:
        include_minor = True
        print("NOTE: reference contains minor aspects -> minor scan auto-enabled.")

    bodies = PLANETS + (TNS if args.tns else [])

    # ── Compute positions + scan ──
    pos = get_positions(jd, bodies)
    computed = scan_aspects(pos, include_minor)
    computed_keys = set()
    for pair, aspects in computed.items():
        for aname in aspects:
            computed_keys.add((pair, aname))

    # ── Match each reference aspect ──
    rows = []
    ref_keys = set()
    missing = []
    orb_over = []
    for r in refs:
        pair = frozenset((r["p1"], r["p2"]))
        aname = r["aspect"]
        ref_keys.add((pair, aname))
        if (pair, aname) not in computed_keys:
            # reference lists an aspect the scan rule does not produce
            missing.append(r)
            rows.append({**r, "computed_orb": None, "delta": None,
                         "mine_appsep": None, "status": "MISSING"})
            continue
        comp_orb = computed[pair][aname]
        delta = abs(comp_orb - r["orb"])
        a, b = sorted((r["p1"], r["p2"]))
        # find the canonical names for applying/separating (order-independent)
        mine_appsep = applying_separating(pos, r["p1"], r["p2"],
                                          ASPECT_TARGETS[aname])
        status = "OK" if delta <= args.tol else "OVER"
        if delta > args.tol:
            orb_over.append(r)
        rows.append({**r, "computed_orb": comp_orb, "delta": delta,
                     "mine_appsep": mine_appsep, "status": status})

    # ── Extras: computed but not in reference (two-way) ──
    extras = []
    for (pair, aname) in sorted(computed_keys - ref_keys,
                                key=lambda x: (tuple(sorted(x[0])), x[1])):
        a, b = sorted(pair)
        extras.append((a, b, aname, computed[frozenset((a, b))][aname]))

    # ── Report ──
    print("=" * 78)
    print(f"  ASPECT VERIFICATION  |  {args.date} {args.time}  {city['name']}")
    print(f"  {city['lat']}N {city['lon']}E  {city['tz']} (UTC+{tz_off})  JD {jd:.6f}")
    print(f"  Bodies: {len(bodies)}  Minor scan: {'on' if include_minor else 'off'}  "
          f"tol: {args.tol}°")
    print("=" * 78)
    print(f"{'Reference aspect':30s} {'ref orb':>9s} {'computed':>9s} "
          f"{'Δ':>8s} {'ref':>10s} {'mine':>10s}  verdict")
    print("-" * 78)
    for r in sorted(rows, key=lambda x: (x["status"] != "OK", x["delta"] or 0)):
        pair_s = f"{r['p1']} {r['aspect'].title()} {r['p2']}"
        if r["status"] == "MISSING":
            print(f"{pair_s:30s} {dms(r['orb']):>9s} {'--':>9s} {'--':>8s} "
                  f"{r['appsep']:>10s} {'--':>10s}  MISSING")
        else:
            print(f"{pair_s:30s} {dms(r['orb']):>9s} {dms(r['computed_orb']):>9s} "
                  f"{r['delta']:7.4f}° {r['appsep']:>10s} {r['mine_appsep']:>10s}  "
                  f"{r['status']}")
    print("-" * 78)

    if extras:
        print(f"EXTRA aspects (computed, not in reference) — {len(extras)}:")
        for a, b, aname, orb in extras:
            print(f"   {a} {aname.title()} {b}  {dms(orb)}")
        print()

    # ── Verdict ──
    collection_ok = not missing and not extras
    orbs_ok = not orb_over
    passed = collection_ok and orbs_ok
    print("=" * 78)
    print(f"  Collection match (two-way): "
          f"{'PASS' if collection_ok else 'FAIL'}  "
          f"(missing={len(missing)}  extra={len(extras)})")
    print(f"  Orb match (Δ <= {args.tol}°): "
          f"{'PASS' if orbs_ok else 'FAIL'}  (over={len(orb_over)})")
    print(f"  RESULT: {'PASS' if passed else 'FAIL'}")
    if not orbs_ok and orb_over:
        print(f"  hint: {len(orb_over)} orb(s) over tolerance — likely reference "
              f"rounded to 1′; try --tol 0.02")
    print("=" * 78)
    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
