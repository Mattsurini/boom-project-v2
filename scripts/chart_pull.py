#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
chart_pull.py — One-command chart pull using the shared hermes_astro layer.

Convention:  DD.MM.YYYY HH:MM <city>   (same as aspect_verify.py)

Usage:
    python chart_pull.py 20.11.1996 20:37 chiang-rai
    python chart_pull.py 08.09.2026 21:53 chiang-rai --aspects
    python chart_pull.py 20.11.1996 20:37 --lat 19.91 --lon 99.83 --tz 7
    python chart_pull.py 20.11.1996 20:37 chiang-rai --json

Output: engine line (pyswisseph primary / xalen fallback), Placidus cusps +
ASC/MC, Traditional 7 with speed + dignity, and (with --aspects) the VOC
aspect set. --json emits machine-readable output.

Exit code: 0 = ok, 2 = usage/input error.
"""
import sys
import io
import json
import argparse
from datetime import datetime, timedelta

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

# ── Shared calculation layer (hermes-astro-hub) ─────────────────────────────
import os
_HUB = r"E:\Boom Project\hermes-astro-hub"
if _HUB not in sys.path:
    sys.path.insert(0, _HUB)
try:
    import hermes_astro as ha
except ImportError:
    print("ERROR: hermes_astro not importable (expected at " + _HUB + ").")
    sys.exit(2)

# ─── City / timezone lookup (same convention as aspect_verify.py) ──────────
CITY_DB = {
    "chiang-rai": {"lat": 19.9022, "lon": 99.8336, "tz": "Asia/Bangkok", "name": "Chiang Rai, Thailand"},
    "bangkok": {"lat": 13.7563, "lon": 100.5018, "tz": "Asia/Bangkok", "name": "Bangkok, Thailand"},
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
    "mumbai": {"lat": 19.0760, "lon": 72.8777, "tz": "Asia/Kolkata", "name": "Mumbai, India"},
    "delhi": {"lat": 28.7041, "lon": 77.1025, "tz": "Asia/Kolkata", "name": "Delhi, India"},
    "seoul": {"lat": 37.5665, "lon": 126.9780, "tz": "Asia/Seoul", "name": "Seoul, South Korea"},
    "sydney": {"lat": -33.8688, "lon": 151.2093, "tz": "Australia/Sydney", "name": "Sydney, Australia"},
    "moscow": {"lat": 55.7558, "lon": 37.6173, "tz": "Europe/Moscow", "name": "Moscow, Russia"},
}
TZ_OFFSETS = {
    "Asia/Bangkok": 7, "Europe/London": 0, "America/New_York": -5,
    "America/Los_Angeles": -8, "Europe/Berlin": 1, "Europe/Paris": 1,
    "Asia/Tokyo": 9, "Asia/Shanghai": 8, "Asia/Dubai": 4,
    "Asia/Singapore": 8, "Europe/Istanbul": 3, "Asia/Kolkata": 5.5,
    "Asia/Seoul": 9, "Australia/Sydney": 11, "Europe/Moscow": 3,
}


def find_city(name):
    key = name.strip().lower().replace(" ", "-")
    return CITY_DB.get(key)


def main():
    ap = argparse.ArgumentParser(
        description="One-command chart pull via the shared hermes_astro layer.")
    ap.add_argument("date", help="DD.MM.YYYY")
    ap.add_argument("time", help="HH:MM (local)")
    ap.add_argument("city", nargs="?", default=None,
                    help="city name (e.g. chiang-rai) — or use --lat/--lon/--tz")
    ap.add_argument("--lat", type=float, default=None, help="override latitude")
    ap.add_argument("--lon", type=float, default=None, help="override longitude")
    ap.add_argument("--tz", type=float, default=None,
                    help="override UTC offset in hours (e.g. 7 for ICT)")
    ap.add_argument("--aspects", action="store_true",
                    help="include the VOC aspect set")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    args = ap.parse_args()

    # ── Resolve location ──
    if args.city:
        city = find_city(args.city)
        if not city:
            print(f"ERROR: city '{args.city}' not found. Known: {', '.join(sorted(CITY_DB))}")
            sys.exit(2)
        lat, lon, tz_off = city["lat"], city["lon"], TZ_OFFSETS[city["tz"]]
        loc_name = city["name"]
    else:
        if args.lat is None or args.lon is None or args.tz is None:
            print("ERROR: need <city> or all of --lat/--lon/--tz.")
            sys.exit(2)
        lat, lon, tz_off = args.lat, args.lon, args.tz
        loc_name = f"{lat}N {lon}E (custom)"

    # ── Local time → UTC → JD (same convention as aspect_verify.py) ──
    try:
        dt_local = datetime.strptime(f"{args.date} {args.time}", "%d.%m.%Y %H:%M")
    except ValueError:
        print(f"ERROR: bad date/time '{args.date} {args.time}' (want DD.MM.YYYY HH:MM).")
        sys.exit(2)
    dt_utc = dt_local - timedelta(hours=tz_off)
    jd = ha.swe.julday(dt_utc.year, dt_utc.month, dt_utc.day,
                       dt_utc.hour + dt_utc.minute / 60.0)

    # ── Compute via the shared layer ──
    eng = ha.verify_engine()
    cusps, asc, mc = ha.houses(jd, lat, lon)
    pos = ha.all_positions(jd)  # Traditional 7, {name: {lon, speed}}

    rows = []
    for name in ha.TRAD7:
        p = pos[name]
        _, dign = ha.dignity(name, p["lon"])
        rows.append({
            "planet": name,
            "lon": round(p["lon"], 4),
            "speed": round(p["speed"], 4),
            "retro": p["speed"] < 0,
            "position": ha.fmt_lon(p["lon"]),
            "dignity": dign,
        })

    result = {
        "engine": eng,
        "question_time": f"{args.date} {args.time}",
        "utc": dt_utc.strftime("%Y-%m-%d %H:%M"),
        "location": loc_name,
        "lat": lat, "lon": lon, "tz_offset": tz_off,
        "jd": round(jd, 6),
        "ascendant": round(asc, 4),
        "mc": round(mc, 4),
        "ascendant_fmt": ha.fmt_lon(asc),
        "mc_fmt": ha.fmt_lon(mc),
        "cusps": [round(c, 4) for c in cusps],
        "planets": rows,
    }

    if args.aspects:
        aspects = []
        names = ha.TRAD7
        for i, a in enumerate(names):
            for b in names[i + 1:]:
                for r in ha.check_aspect_with_speed(
                        pos[a]["lon"], a, pos[a]["speed"],
                        pos[b]["lon"], b, pos[b]["speed"]):
                    aspects.append({
                        "active": a, "passive": b,
                        "aspect": r["asp"], "sym": r.get("sym", ""),
                        "orb": round(r["orb"], 3),
                        "movement": r.get("movement"),
                        "in_orb_active": r.get("in_orb_active"),
                    })
        result["aspects"] = aspects

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    # ── Human-readable output ──
    mark = "OK" if eng["ok"] else "FAIL"
    print(f"📡 engine: {eng['engine']} [{mark}] — {eng['detail']}")
    print(f"🕰  {args.date} {args.time} local ({loc_name}) | UTC {dt_utc:%Y-%m-%d %H:%M} | JD {jd:.6f}")
    print()
    print("🏠 PLACIDUS HOUSES")
    print(f"  ASC {ha.fmt_lon_full(asc):<22} MC {ha.fmt_lon_full(mc)}")
    for i, c in enumerate(cusps, 1):
        print(f"  {i:>2}: {ha.fmt_lon(c)}")
    print()
    print("🪐 TRADITIONAL 7")
    print(f"  {'Planet':<10} {'Position':<14} {'Spd':>8}  Dignity")
    print(f"  {'─'*10} {'─'*14} {'─'*8}  {'─'*10}")
    for r in rows:
        spd = f"{r['speed']:+.4f}" + ("R" if r["retro"] else "")
        print(f"  {r['planet']:<10} {r['position']:<14} {spd:>8}  {r['dignity']}")
    if args.aspects:
        print()
        print("📐 ASPECTS (VOC, cross-sign)")
        for a in result["aspects"]:
            orb_tag = "" if a["in_orb_active"] else " (passive-only)"
            print(f"  {a['active']} {a['sym'] or a['aspect']} {a['passive']}  "
                  f"orb {a['orb']:.2f}° {a['movement']}{orb_tag}")


if __name__ == "__main__":
    main()
