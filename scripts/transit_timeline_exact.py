#!/usr/bin/env python3
"""
Transit Timeline with exact times — scans every hour for tightest orbs.
Usage: python transit_timeline_exact.py <start> <end> <orb> [tz]
  start/end: YYYY-MM-DD
  orb: max orb in degrees (default 2.0)
  tz: timezone offset from UTC (default 7 for ICT)
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

SIGNS = ["Ari","Tau","Gem","Can","Leo","Vir","Lib","Sco","Sag","Cap","Aqu","Pis"]
PLANETS = ["Sun","Moon","Mercury","Venus","Mars","Jupiter","Saturn","Uranus","Neptune","Pluto"]
TNS = ["Cupido","Hades","Zeus","Kronos","Apollon","Admetos","Vulcanus","Poseidon"]
ALL_BODIES = PLANETS + TNS

BODY_CODES = {
    "Sun":0,"Moon":1,"Mercury":2,"Venus":3,"Mars":4,"Jupiter":5,"Saturn":6,
    "Uranus":7,"Neptune":8,"Pluto":9,
    "Cupido":40,"Hades":41,"Zeus":42,"Kronos":43,"Apollon":44,"Admetos":45,"Vulcanus":46,"Poseidon":47,
}

ASPECTS = [
    (0,"☌","Conjunction"),
    (60,"⚹","Sextile"),
    (90,"□","Square"),
    (120,"△","Trine"),
    (180,"☍","Opposition"),
]

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

def fmt_time(dt, tz):
    local = dt + timedelta(hours=tz)
    return local.strftime('%H:%M')

def main():
    # Boom natal
    natal_date = "1996-11-20"
    natal_time = "20:37"
    lat, lon = 19.91, 99.83
    tz = int(sys.argv[4]) if len(sys.argv) > 4 else 7

    start = sys.argv[1] if len(sys.argv) > 1 else "2026-08-03"
    end   = sys.argv[2] if len(sys.argv) > 2 else "2026-12-31"
    orb   = float(sys.argv[3]) if len(sys.argv) > 3 else 2.0

    # natal JD
    ny, nm, nd = map(int, natal_date.split('-'))
    nth, ntm = map(int, natal_time.split(':'))
    dt_natal = datetime(ny, nm, nd, nth, ntm, tzinfo=timezone.utc) - timedelta(hours=tz)
    jd_natal = swe.julday(dt_natal.year, dt_natal.month, dt_natal.day, dt_natal.hour + dt_natal.minute/60.0)
    natal = get_chart(jd_natal)

    sy, sm, sd = map(int, start.split('-'))
    ey, em, ed = map(int, end.split('-'))
    dstart = datetime(sy, sm, sd, 0, 0, tzinfo=timezone.utc) - timedelta(hours=tz)
    dend   = datetime(ey, em, ed, 23, 0, tzinfo=timezone.utc) - timedelta(hours=tz)

    # For each (transit_body, natal_body, aspect_type) track minimum orb and datetime
    events = {}  # key -> (datetime, orb, transit_lon)

    cur = dstart
    while cur <= dend:
        jd_t = swe.julday(cur.year, cur.month, cur.day, cur.hour + cur.minute/60.0)
        trans = get_chart(jd_t, swe.FLG_SWIEPH | swe.FLG_SPEED)

        for t_name in ALL_BODIES:
            for n_name in PLANETS:
                a = aspect_angle(trans[t_name], natal[n_name])
                for deg, sym, nm in ASPECTS:
                    diff = abs(a - deg)
                    if diff <= orb:
                        key = (t_name, n_name, sym)
                        if key not in events or diff < events[key][1]:
                            events[key] = (cur, diff, trans[t_name])
                        break
        cur += timedelta(hours=1)

    # Sort by datetime
    results = []
    for key, (dt_t, diff, tlon) in events.items():
        t_name, n_name, sym = key
        # find aspect name
        nm = next(x[2] for x in ASPECTS if x[1] == sym)
        # weight for filtering: outer planets + tight orbs
        weight = 1
        if t_name in ["Saturn","Uranus","Neptune","Pluto"]:
            weight = 4
        elif t_name in ["Jupiter"]:
            weight = 2
        elif t_name in TNS:
            weight = 3
        weight += max(0, int((orb - diff) * 3))
        results.append((dt_t, weight, t_name, sym, nm, n_name, diff, sign_str(tlon)))

    results.sort(key=lambda x: x[0])

    print(f"\n{'='*75}")
    print(f"  TRANSIT TIMELINE (hourly scan): {start} → {end}  |  Max orb {orb}°  |  UTC+{tz}")
    print(f"  Natal: {natal_date} {natal_time} ICT | {lat}°N, {lon}°E")
    print(f"{'='*75}")
    print(f"{'Date':12} {'Time':6} {'Transit':9} {'Aspect':12} {'Natal':8} {'Orb':>5} {'Pos':14}")
    print("-"*75)

    # Deduplicate: if same t_name+n_name+aspect within 1 day, keep only tightest
    filtered = []
    last_key = None
    last_date = None
    for r in results:
        date_str = r[0].strftime('%Y-%m-%d')
        key = (r[2], r[5], r[3])
        if last_key == key and last_date == date_str:
            continue  # same day, same aspect pair; we already have the tightest from that day
        filtered.append(r)
        last_key = key
        last_date = date_str

    for dt_t, _, t_name, sym, nm, n_name, diff, pos in filtered:
        date_str = dt_t.strftime('%Y-%m-%d')
        time_str = fmt_time(dt_t, tz)
        print(f"{date_str:12} {time_str:6} {t_name:9} {sym+' '+nm:12} {n_name:8} {diff:>4.1f}° {pos:14}")

    print(f"{'='*75}")

    # Outer planet summary
    print("\n📌 OUTER + TN PLANET EXACT TIMES")
    outer = [e for e in filtered if e[2] in ["Saturn","Uranus","Neptune","Pluto","Jupiter"] + TNS]
    for dt_t, _, t_name, sym, nm, n_name, diff, pos in outer[:40]:
        date_str = dt_t.strftime('%Y-%m-%d')
        time_str = fmt_time(dt_t, tz)
        print(f"  {date_str} {time_str}  {t_name:8} {sym} {n_name:8}  ({diff:.1f}°)  {pos}")

    swe.close()

if __name__ == "__main__":
    main()
