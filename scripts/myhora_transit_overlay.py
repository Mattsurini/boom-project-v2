#!/usr/bin/env python3
"""
myhora_transit_overlay.py — transit-to-natal overlay using myhora-chart as the engine.

Workaround for myhora's server-side transit bug: the site's --transit feature
rejects any transit whose (month,day) is lexicographically before the birth
(month,day), ignoring the year. So for a birth on 20.11, any transit before
Nov 21 of the calendar year is refused. Instead we cast the TRANSIT MOMENT as a
plain natal chart (myhora's natal-only path works for any date) and overlay it
onto the real natal chart.

Usage:
  python myhora_transit_overlay.py [TRANSIT_DATE DD.MM.YYYY] [TRANSIT_TIME HH:MM]
  python myhora_transit_overlay.py 11.09.2026 12:00
Defaults: today's date (ICT) 12:00.

Natal is fixed to BooM: 20.11.1996 20:37 ICT, Chiang Rai.
"""
import sys, time, json
sys.path.insert(0, r"E:\Boom Project\hermes-astro-hub")
from hermes_astro.myhora import get_chart

NATAL_DATE, NATAL_TIME = "20.11.1996", "20:37"
CITY = "Chiang Rai"


def fetch(date, t, tries=6):
    last = None
    for i in range(tries):
        try:
            return get_chart(date, t, CITY, tropical=True)
        except Exception as e:
            last = e
            time.sleep(3 + 3 * i)
    raise last


def house_of(cusps, lon):
    lon %= 360
    for i in range(12):
        c1, c2 = cusps[i], cusps[(i + 1) % 12]
        if c2 < c1:
            if lon >= c1 or lon < c2:
                return i + 1
        elif c1 <= lon < c2:
            return i + 1
    return 12


def angdiff(a, b):
    d = abs((a - b) % 360)
    return 360 - d if d > 180 else d


ASPECTS = {0: "☌", 60: "⚹", 90: "□", 120: "△", 180: "☍"}
MAXORB = {0: 8, 60: 6, 90: 7, 120: 8, 180: 8}
TP = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter",
      "Saturn", "Uranus", "Neptune", "Pluto"]


def main():
    td = sys.argv[1] if len(sys.argv) > 1 else None
    tt = sys.argv[2] if len(sys.argv) > 2 else "12:00"
    if td is None:
        from datetime import datetime, timezone, timedelta
        td = datetime.now(timezone(timedelta(hours=7))).strftime("%d.%m.%Y")

    print(f"Fetching natal {NATAL_DATE} {NATAL_TIME} ...", file=sys.stderr)
    natal = fetch(NATAL_DATE, NATAL_TIME)
    print(f"Fetching transit {td} {tt} ...", file=sys.stderr)
    transit = fetch(td, tt)

    nat = {p["body"]: p for p in natal["natal"]}
    cusps = [h["ecliptic_lon"] for h in natal["houses"]]
    tn = {p["body"]: p for p in transit["natal"]}

    out = {"transit_date": td, "transit_time": tt, "positions": [], "aspects": []}

    print("=== TRANSIT POSITIONS (myhora tropical) -> NATAL HOUSE ===")
    for b in TP:
        if b in tn:
            p = tn[b]
            h = house_of(cusps, p["ecliptic_lon"])
            out["positions"].append({"body": b, "sign": p["sign"],
                                     "pos": f"{p['deg']}°{p['min']:02d}'", "house": h})
            print(f"  {b:9} {p['sign']:12} {p['deg']}°{p['min']:02d}'  -> H{h}")

    print()
    print("=== TRANSIT -> NATAL ASPECTS (major, sorted by orb) ===")
    rows = []
    for tb in TP:
        if tb not in tn:
            continue
        tl = tn[tb]["ecliptic_lon"]
        for nb, np in nat.items():
            if nb in ("MC", "ASC", "MC-trop", "ASC-trop"):
                continue
            d = angdiff(tl, np["ecliptic_lon"])
            best = None
            for deg, sym in ASPECTS.items():
                orb = abs(d - deg)
                if orb <= MAXORB[deg] and (best is None or orb < best[0]):
                    best = (orb, sym, deg)
            if best:
                rows.append((best[0], tb, best[1], nb, np["sign"], best[2]))
                out["aspects"].append({"transit": tb, "aspect": best[1],
                                       "natal": nb, "natal_sign": np["sign"],
                                       "orb": round(best[0], 2), "angle": best[2]})
    rows.sort()
    for orb, tb, sym, nb, ns, deg in rows:
        print(f"  {orb:5.2f}°  {tb:9} {sym} {nb:9} ({ns}) [{deg}°]")

    print()
    print(f"saved positions={len(out['positions'])} aspects={len(out['aspects'])}", file=sys.stderr)
    with open(r"E:\Boom Project\cache\myhora_transit_overlay.json", "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
