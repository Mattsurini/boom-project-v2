#!/usr/bin/env python3
"""
Transit Timeline — scan date range for exact transit→natal aspects.
Usage: python transit_timeline.py <start> <end> <orb> [transit_time]
  start/end: YYYY-MM-DD
  orb: max orb in degrees (default 2.0)
  transit_time: HH:MM for each day (default 12:00)
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

def main():
    # Boom natal
    natal_date = "1996-11-20"
    natal_time = "20:37"
    lat, lon = 19.91, 99.83
    tz = 7

    start = sys.argv[1] if len(sys.argv) > 1 else "2026-08-03"
    end   = sys.argv[2] if len(sys.argv) > 2 else "2026-12-31"
    orb   = float(sys.argv[3]) if len(sys.argv) > 3 else 2.0
    ttime = sys.argv[4] if len(sys.argv) > 4 else "12:00"

    # natal JD
    ny, nm, nd = map(int, natal_date.split('-'))
    nth, ntm = map(int, natal_time.split(':'))
    dt_natal = datetime(ny, nm, nd, nth, ntm, tzinfo=timezone.utc) - timedelta(hours=tz)
    jd_natal = swe.julday(dt_natal.year, dt_natal.month, dt_natal.day, dt_natal.hour + dt_natal.minute/60.0)
    natal = get_chart(jd_natal)

    sy, sm, sd = map(int, start.split('-'))
    ey, em, ed = map(int, end.split('-'))
    dstart = datetime(sy, sm, sd)
    dend   = datetime(ey, em, ed)

    events = []
    cur = dstart
    while cur <= dend:
        t_h, t_m = map(int, ttime.split(':'))
        dt_t = datetime(cur.year, cur.month, cur.day, t_h, t_m, tzinfo=timezone.utc) - timedelta(hours=tz)
        jd_t = swe.julday(dt_t.year, dt_t.month, dt_t.day, dt_t.hour + dt_t.minute/60.0)
        trans = get_chart(jd_t, swe.FLG_SWIEPH | swe.FLG_SPEED)

        for t_name in ALL_BODIES:
            for n_name in PLANETS:
                a = aspect_angle(trans[t_name], natal[n_name])
                for deg, sym, nm in ASPECTS:
                    if abs(a - deg) <= orb:
                        # prioritize outer-planet transits and tighter orbs
                        weight = 1
                        if t_name in ["Saturn","Uranus","Neptune","Pluto"]:
                            weight = 3
                        elif t_name in ["Jupiter"]:
                            weight = 2
                        weight += max(0, int((orb - abs(a-deg)) * 2))  # tighter = higher
                        events.append((cur.strftime('%Y-%m-%d'), weight, t_name, sym, nm, n_name, abs(a-deg), sign_str(trans[t_name])))
                        break
        cur += timedelta(days=1)

    # deduplicate: same t_name+n_name+aspect within 3 days -> keep tightest
    events.sort(key=lambda x: (x[2], x[5], x[3], x[0]))
    filtered = []
    last_key = None
    for e in events:
        key = (e[2], e[5], e[3])
        if last_key == key:
            # same aspect pair; keep if tighter or keep existing? Keep tightest overall
            if filtered and abs(e[6] - 0) < abs(filtered[-1][6] - 0):
                filtered[-1] = e
        else:
            filtered.append(e)
            last_key = key

    filtered.sort(key=lambda x: x[0])

    print(f"\n{'='*70}")
    print(f"  TRANSIT TIMELINE: {start} → {end}  |  Max orb {orb}°  |  {ttime} UTC+7 daily")
    print(f"  Natal: {natal_date} {natal_time} ICT | {lat}°N, {lon}°E")
    print(f"{'='*70}")
    print(f"{'Date':12} {'Transit':10} {'Aspect':14} {'Natal':10} {'Orb':>6} {'Transit Pos':16}")
    print("-"*70)
    for date, _, t_name, sym, nm, n_name, o, pos in filtered:
        print(f"{date:12} {t_name:10} {sym+' '+nm:14} {n_name:10} {o:>5.1f}° {pos:16}")
    print(f"{'='*70}")

    # summary of major outer planet windows
    print("\n📌 OUTER PLANET WINDOWS (Saturn / Uranus / Neptune / Pluto)")
    outer = [e for e in filtered if e[2] in ["Saturn","Uranus","Neptune","Pluto","Cupido","Hades","Zeus","Kronos","Apollon","Admetos","Vulcanus","Poseidon"]]
    for e in outer[:30]:
        date, _, t_name, sym, nm, n_name, o, pos = e
        print(f"  {date}  {t_name:8} {sym} {n_name:8}  ({o:.1f}°)  {pos}")

    swe.close()

if __name__ == "__main__":
    main()
