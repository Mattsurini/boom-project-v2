#!/usr/bin/env python3
"""
Transit Timeline — verified aspects, orbs, and core themes.
Outputs a clean markdown table.
Usage: python transit_timeline_check.py <start> <end> <orb>
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

# Concise core themes for common outer-planet + TN pairings
THEMES = {
    ("Saturn","Jupiter","□"): "Expansion blocked by structure; patience required",
    ("Jupiter","Mercury","△"): "Big-picture thinking, learning surge",
    ("Jupiter","Venus","⚹"): "Relationship/financial growth window",
    ("Jupiter","Sun","□"): "Overreach risk; check ambition",
    ("Saturn","Mercury","△"): "Disciplined communication, mature planning",
    ("Saturn","Moon","☌"): "Emotional weight, responsibility, maturation",
    ("Saturn","Saturn","☌"): "Saturn return echo; structural reckoning",
    ("Uranus","Pluto","☍"): "Radical structural snap; generational climax",
    ("Uranus","Sun","☍"): "Identity jolt; sudden self-disruption",
    ("Uranus","Moon","⚹"): "Emotional breakthrough; sudden insight",
    ("Uranus","Saturn","⚹"): "Innovation meets discipline",
    ("Uranus","Uranus","△"): "Identity liberation; freedom surge",
    ("Neptune","Moon","☌"): "Emotional fog; boundary loss; sensitivity spike",
    ("Neptune","Saturn","☌"): "Structures dissolve; fatigue; spiritual surrender",
    ("Neptune","Pluto","△"): "Deep spiritual transformation undercurrent",
    ("Neptune","Uranus","⚹"): "Visionary breakthrough; illusion vs. innovation",
    ("Neptune","Mercury","△"): "Intuitive thinking; creative imagination",
    ("Pluto","Uranus","☌"): "Generational reset personalizing; radical rebirth",
    ("Pluto","Moon","⚹"): "Emotional power regeneration; deep purge",
    ("Pluto","Pluto","⚹"): "Personal power regeneration; shadow work",
    ("Pluto","Sun","☌"): "Identity death/rebirth; obsession peak",
    ("Pluto","Mercury","⚹"): "Mental depth; investigative clarity",
    ("Pluto","Saturn","⚹"): "Disciplined transformation; authority purge",
    ("Pluto","Venus","☌"): "Intense relationship/financial transformation",
    ("Hades","Jupiter","☍"): "Shadow material on luck/beliefs; deep reckoning",
    ("Kronos","Jupiter","☍"): "Authority/legacy tension with growth",
    ("Poseidon","Jupiter","⚹"): "Spiritual wisdom expands",
    ("Zeus","Neptune","□"): "Driven action vs. illusion; verify before pushing",
    ("Zeus","Venus","☌"): "Desire/action fuse with values; explosive attraction",
    ("Cupido","Mars","△"): "Social/romantic initiative",
    ("Vulcanus","Pluto","△"): "Power/authority dynamic regenerates",
}

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

def get_theme(t_name, sym, n_name):
    return THEMES.get((t_name, n_name, sym), THEMES.get((t_name, n_name, sym[0]), ""))

def main():
    natal_date = "1996-11-20"
    natal_time = "20:37"
    lat, lon = 19.91, 99.83
    tz = 7

    start = sys.argv[1] if len(sys.argv) > 1 else "2026-08-03"
    end   = sys.argv[2] if len(sys.argv) > 2 else "2026-12-31"
    orb   = float(sys.argv[3]) if len(sys.argv) > 3 else 2.0

    ny, nm, nd = map(int, natal_date.split('-'))
    nth, ntm = map(int, natal_time.split(':'))
    dt_natal = datetime(ny, nm, nd, nth, ntm, tzinfo=timezone.utc) - timedelta(hours=tz)
    jd_natal = swe.julday(dt_natal.year, dt_natal.month, dt_natal.day, dt_natal.hour + dt_natal.minute/60.0)
    natal = get_chart(jd_natal)

    sy, sm, sd = map(int, start.split('-'))
    ey, em, ed = map(int, end.split('-'))
    dstart = datetime(sy, sm, sd, 0, 0, tzinfo=timezone.utc) - timedelta(hours=tz)
    dend   = datetime(ey, em, ed, 23, 0, tzinfo=timezone.utc) - timedelta(hours=tz)

    best = {}  # (t,n,aspect) -> (dt, orb, tlon)
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
                        if key not in best or diff < best[key][1]:
                            best[key] = (cur, diff, trans[t_name])
                        break
        cur += timedelta(hours=1)

    # Build rows
    rows = []
    for (t_name, n_name, sym), (dt_t, diff, tlon) in best.items():
        nm = next(x[2] for x in ASPECTS if x[1] == sym)
        weight = 1
        if t_name in ["Saturn","Uranus","Neptune","Pluto"]: weight = 4
        elif t_name in ["Jupiter"]: weight = 2
        elif t_name in TNS: weight = 3
        weight += max(0, int((orb - diff) * 3))
        theme = get_theme(t_name, sym, n_name)
        rows.append((dt_t, weight, t_name, sym, nm, n_name, diff, sign_str(tlon), theme))

    rows.sort(key=lambda x: x[0])

    # Filter: deduplicate same day for same t+n+aspect (already one per whole range)
    # But keep only rows with meaningful theme OR outer planets
    filtered = [r for r in rows if r[8] or r[2] in ["Saturn","Uranus","Neptune","Pluto","Jupiter"]]

    print(f"\n{'='*80}")
    print(f"  VERIFIED TRANSIT TIMELINE: {start} → {end}  |  Max orb {orb}°  |  UTC+{tz}")
    print(f"  Natal: {natal_date} {natal_time} ICT")
    print(f"{'='*80}")
    print(f"{'Date':12} {'Time':6} {'Transit':9} {'Aspect':12} {'Natal':8} {'Orb':>5} {'Core Theme'}")
    print("-"*80)
    for dt_t, _, t_name, sym, nm, n_name, diff, pos, theme in filtered:
        date_str = dt_t.strftime('%Y-%m-%d')
        time_str = fmt_time(dt_t, tz)
        print(f"{date_str:12} {time_str:6} {t_name:9} {sym+' '+nm:12} {n_name:8} {diff:>4.1f}°  {theme}")
    print(f"{'='*80}")
    swe.close()

if __name__ == "__main__":
    main()
