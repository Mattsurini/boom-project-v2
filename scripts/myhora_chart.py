#!/usr/bin/env python3
"""
myhora_chart.py — Calculate a chart via myhora.com (thin CLI wrapper).

Core logic lives in hermes-astro-hub: hermes_astro.myhora
  from hermes_astro.myhora import get_chart, build_report

Usage:
  python myhora_chart.py DD.MM.YYYY HH:MM [city] [options]
  python myhora_chart.py 20.11.1996 20:37 Chiang Rai
  python myhora_chart.py 20.11.1996 20:37 --lat 19.9081 --lon 99.8317 --utc +07:00
  python myhora_chart.py 20.11.1996 20:37 --transit 10.09.2026 14:00

Options:
  --lat/--lon/--utc   Explicit coordinates + UTC offset (overrides city)
  --transit D T       Also compute a transit/forecast date (DD.MM.YYYY HH:MM)
  --name NAME         Name label in the chart (default: empty)
  --json FILE         Save parsed data as JSON
  --html FILE         Save raw postback HTML
  --output FILE       Save report as markdown
  --house P|K|C|E|O   House system: P=Placidus(default) K=Koch C=Cox E=Equal O=Porphyry
  --tropical          Request tropical zodiac (default: sidereal Lahiri)
"""
import sys
import json
import argparse

# make hermes-astro-hub importable when run from the Boom Project
sys.path.insert(0, r"E:\Boom Project\hermes-astro-hub")

import requests
from hermes_astro.myhora import (
    CITIES, parse_date, post_chart, parse_postback, build_report,
)


def main():
    ap = argparse.ArgumentParser(description="Calculate chart via myhora.com POST")
    ap.add_argument("date", help="DD.MM.YYYY")
    ap.add_argument("time", help="HH:MM (local)")
    ap.add_argument("city", nargs="?", default=None, help="city name or omit with --lat/--lon")
    ap.add_argument("--lat", type=float)
    ap.add_argument("--lon", type=float)
    ap.add_argument("--utc", default="+07:00")
    ap.add_argument("--name", default="")
    ap.add_argument("--transit", nargs=2, metavar=("DATE", "TIME"), help="transit date DD.MM.YYYY HH:MM")
    ap.add_argument("--house", default="P", choices=["P", "K", "C", "E", "O"])
    ap.add_argument("--tropical", action="store_true")
    ap.add_argument("--json", dest="json_out")
    ap.add_argument("--html", dest="html_out")
    ap.add_argument("--output", dest="md_out")
    args = ap.parse_args()

    # resolve location
    province = amphur = None
    if args.lat is not None and args.lon is not None:
        lat, lon, utc = args.lat, args.lon, args.utc
    else:
        key = (args.city or "chiang rai").lower()
        if key not in CITIES:
            print(f"Unknown city '{args.city}'. Known: {', '.join(CITIES)}. "
                  f"Use --lat/--lon for other places.", file=sys.stderr)
            sys.exit(1)
        province, amphur, lat, lon, utc = CITIES[key]

    d, m, y_ce, y_be = parse_date(args.date)
    hh, mm = [int(x) for x in args.time.split(":")]

    session = requests.Session()
    html = post_chart(session, d, m, y_be, hh, mm, lat, lon, utc,
                      name=args.name, tropical=args.tropical,
                      house=args.house,
                      transit=args.transit,
                      province=province, amphur=amphur)
    res = parse_postback(html)

    if not res["natal"]:
        print("ERROR: no natal data parsed — page layout may have changed.", file=sys.stderr)
        if args.html_out:
            open(args.html_out, "w", encoding="utf-8").write(html)
        sys.exit(2)

    if args.html_out:
        open(args.html_out, "w", encoding="utf-8").write(html)
    if args.json_out:
        json.dump(res, open(args.json_out, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

    label = args.city or f"{lat:.4f},{lon:.4f}"
    report = build_report(res, args.date, args.time, label, lat, lon, utc)
    if args.md_out:
        open(args.md_out, "w", encoding="utf-8").write(report)
        print(f"saved: {args.md_out}")
    print(report)


if __name__ == "__main__":
    main()
