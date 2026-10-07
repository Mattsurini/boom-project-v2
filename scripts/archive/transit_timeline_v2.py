#!/usr/bin/env python3
"""
Transit Timeline — comprehensive scan with exact times, durations, houses, and themes.
Usage: python transit_timeline_v2.py <start> <end> [options]
  start/end: YYYY-MM-DD (e.g., 2026-08-03 2026-12-31)
Options:
  --orb N          Max orb in degrees (default: 2.0)
  --tz N           Timezone offset from UTC (default: 7 for ICT)
  --inner          Include inner planet transits (Sun, Moon, Mercury, Venus, Mars)
  --output FILE    Save to markdown file
  --daily          Show daily summary instead of exact times
Example:
  python transit_timeline_v2.py 2026-08-03 2026-12-31 --orb 2.0 --inner --output transit_report.md
"""
import sys, math, argparse
from datetime import datetime, timedelta, timezone
from collections import defaultdict

import swisseph as swe

swe.set_ephe_path('')

# ─── CONFIG ───
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
    (0, "☌", "Conjunction", "Fusion, intensification"),
    (60, "⚹", "Sextile", "Opportunity, flow"),
    (90, "□", "Square", "Tension, challenge, action"),
    (120, "△", "Trine", "Harmony, ease, talent"),
    (180, "☍", "Opposition", "Polarity, confrontation, balance"),
]

INNER = ["Sun", "Moon", "Mercury", "Venus", "Mars"]
OUTER = ["Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"]

# ─── THEMES DATABASE ───
# Key: (transit_body, natal_body, aspect_symbol) -> theme
THEMES = {
    # Saturn
    ("Saturn","Jupiter","□"): "Expansion blocked by structure; patience required",
    ("Saturn","Mercury","△"): "Disciplined communication, mature planning",
    ("Saturn","Moon","☌"): "Emotional weight, responsibility, maturation",
    ("Saturn","Saturn","☌"): "Saturn return echo; structural reckoning in career/status",
    ("Saturn","Sun","□"): "Identity constraint; authority test",
    ("Saturn","Venus","☌"): "Relationship sobriety; commitment or restriction",
    ("Saturn","Mars","□"): "Action blocked; forced patience",
    ("Saturn","Uranus","⚹"): "Innovation meets discipline; structured breakthrough",
    ("Saturn","Neptune","☌"): "Dreams meet reality; disillusionment or manifestation",
    ("Saturn","Pluto","△"): "Deep structural support; disciplined transformation",
    # Jupiter
    ("Jupiter","Mercury","△"): "Big-picture thinking, learning surge",
    ("Jupiter","Venus","⚹"): "Relationship/financial growth window",
    ("Jupiter","Sun","□"): "Overreach risk; check ambition",
    ("Jupiter","Moon","△"): "Emotional optimism, social luck",
    ("Jupiter","Jupiter","☌"): "Luck peak; expansion year",
    ("Jupiter","Mars","△"): "Confident action; physical vitality",
    ("Jupiter","Saturn","△"): "Growth through discipline; wise expansion",
    # Uranus
    ("Uranus","Pluto","☍"): "Radical structural snap; generational climax",
    ("Uranus","Sun","☍"): "Identity jolt; sudden self-disruption",
    ("Uranus","Moon","⚹"): "Emotional breakthrough; sudden insight",
    ("Uranus","Saturn","⚹"): "Innovation meets discipline",
    ("Uranus","Uranus","△"): "Identity liberation; freedom surge",
    ("Uranus","Mercury","☍"): "Mental jolt; unexpected news/idea",
    ("Uranus","Venus","☌"): "Sudden attraction; relationship disruption",
    ("Uranus","Mars","△"): "Impulsive action; energy spike",
    # Neptune
    ("Neptune","Moon","☌"): "Emotional fog; boundary loss; sensitivity spike",
    ("Neptune","Saturn","☌"): "Structures dissolve; fatigue; spiritual surrender",
    ("Neptune","Pluto","△"): "Deep spiritual transformation undercurrent",
    ("Neptune","Uranus","⚹"): "Visionary breakthrough; illusion vs. innovation",
    ("Neptune","Mercury","△"): "Intuitive thinking; creative imagination",
    ("Neptune","Sun","△"): "Spiritual illumination; ego dissolution",
    ("Neptune","Venus","☌"): "Romantic idealism; fantasy in love",
    ("Neptune","Mars","☍"): "Action dissolves; fatigue or idealism clash",
    # Pluto
    ("Pluto","Uranus","☌"): "Generational reset personalizing; radical rebirth",
    ("Pluto","Moon","⚹"): "Emotional power regeneration; deep purge",
    ("Pluto","Pluto","⚹"): "Personal power regeneration; shadow work",
    ("Pluto","Sun","☌"): "Identity death/rebirth; obsession peak",
    ("Pluto","Mercury","⚹"): "Mental depth; investigative clarity",
    ("Pluto","Saturn","⚹"): "Disciplined transformation; authority purge",
    ("Pluto","Venus","☌"): "Intense relationship/financial transformation",
    ("Pluto","Mars","△"): "Empowered action; deep drive",
    ("Pluto","Jupiter","△"): "Transformation through expansion; power growth",
    # TN Points
    ("Hades","Jupiter","☍"): "Shadow material on luck/beliefs; deep reckoning",
    ("Kronos","Jupiter","☍"): "Authority/legacy tension with growth",
    ("Poseidon","Jupiter","⚹"): "Spiritual wisdom expands",
    ("Zeus","Neptune","□"): "Driven action vs. illusion; verify before pushing",
    ("Zeus","Venus","☌"): "Desire/action fuse with values; explosive attraction",
    ("Cupido","Mars","△"): "Social/romantic initiative",
    ("Vulcanus","Pluto","△"): "Power/authority dynamic regenerates",
    ("Admetos","Uranus","△"): "Endurance meets innovation; stubborn breakthrough",
    ("Apollon","Jupiter","☌"): "Success/multiplication peak; abundance",
    # Inner planets (common)
    ("Sun","Mercury","△"): "Mental clarity; self-expression flows",
    ("Sun","Venus","⚹"): "Social charm; creative expression",
    ("Sun","Mars","□"): "Ego-driven action; conflict potential",
    ("Sun","Jupiter","△"): "Confidence surge; expansive mood",
    ("Sun","Saturn","□"): "Reality check; responsibility weighs",
    ("Sun","Uranus","⚹"): "Sudden self-awareness; uniqueness shines",
    ("Sun","Neptune","△"): "Compassion; spiritual openness",
    ("Sun","Pluto","☌"): "Power encounter; transformation trigger",
    ("Moon","Mercury","△"): "Emotional fluency; intuitive speech",
    ("Moon","Venus","☌"): "Affection needs; relationship sensitivity",
    ("Moon","Mars","□"): "Emotional agitation; reactive energy",
    ("Moon","Jupiter","△"): "Emotional optimism; nurturing expansion",
    ("Moon","Saturn","☌"): "Emotional withdrawal; serious mood",
    ("Moon","Uranus","⚹"): "Sudden feelings; emotional breakthrough",
    ("Moon","Neptune","△"): "Dreamy sensitivity; psychic openness",
    ("Moon","Pluto","☌"): "Emotional intensity; power struggle",
    ("Mercury","Mercury","☌"): "Mental focus; communication peak",
    ("Mercury","Venus","⚹"): "Pleasant communication; artistic thought",
    ("Mercury","Mars","☌"): "Sharp mind; aggressive speech",
    ("Mercury","Jupiter","△"): "Expansive thinking; learning opportunity",
    ("Mercury","Saturn","△"): "Structured thought; serious planning",
    ("Mercury","Uranus","☍"): "Mental rebellion; unexpected ideas",
    ("Mercury","Neptune","☍"): "Confused thinking; deceptive communication",
    ("Mercury","Pluto","△"): "Deep investigation; transformative insight",
    ("Venus","Venus","☌"): "Self-love; values alignment; aesthetic peak",
    ("Venus","Mars","△"): "Passionate attraction; creative drive",
    ("Venus","Jupiter","⚹"): "Social expansion; romantic opportunity",
    ("Venus","Saturn","☍"): "Relationship test; commitment or ending",
    ("Venus","Uranus","△"): "Sudden attraction; unconventional love",
    ("Venus","Neptune","△"): "Romantic idealism; artistic inspiration",
    ("Venus","Pluto","☌"): "Obsessive love; financial power play",
    ("Mars","Mars","☌"): "Energy peak; action initiation; potential conflict",
    ("Mars","Jupiter","☍"): "Overconfidence in action; reckless expansion",
    ("Mars","Saturn","□"): "Frustrated action; blocked drive",
    ("Mars","Uranus","☍"): "Sudden aggression; explosive energy",
    ("Mars","Neptune","☍"): "Drained drive; confused action",
    ("Mars","Pluto","□"): "Power struggle; compulsive action",
}

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

def fmt_time(dt, tz):
    local = dt + timedelta(hours=tz)
    return local.strftime('%H:%M')

def get_house(lon, cusps):
    for i in range(11):
        c1, c2 = cusps[i], cusps[i+1]
        if c2 < c1 and (lon >= c1 or lon < c2): return i+1
        if c1 <= lon < c2: return i+1
    return 12

def get_theme(t_name, sym, n_name):
    return THEMES.get((t_name, n_name, sym), "")

def get_weight(t_name, diff, orb):
    w = 1
    if t_name in OUTER: w = 4
    elif t_name in ["Jupiter"]: w = 2
    elif t_name in TNS: w = 3
    elif t_name in INNER: w = 1
    w += max(0, int((orb - diff) * 3))
    return w

def scan_range(dstart, dend, natal, natal_cusps, tz, orb, include_inner):
    """Scan every hour, return list of events with exact minimum times."""
    best = {}  # (t_name, n_name, aspect_sym) -> (dt, orb, tlon, duration_hours)
    active = defaultdict(list)  # Track duration
    
    cur = dstart
    while cur <= dend:
        jd_t = swe.julday(cur.year, cur.month, cur.day, cur.hour + cur.minute/60.0)
        trans = get_chart(jd_t, swe.FLG_SWIEPH | swe.FLG_SPEED)
        
        for t_name in ALL_BODIES:
            if not include_inner and t_name in INNER:
                continue
            for n_name in PLANETS:
                a = aspect_angle(trans[t_name], natal[n_name])
                for deg, sym, nm, desc in ASPECTS:
                    diff = abs(a - deg)
                    if diff <= orb:
                        key = (t_name, n_name, sym)
                        if key not in best or diff < best[key][1]:
                            best[key] = (cur, diff, trans[t_name], 1)
                        else:
                            # Extend duration if still active
                            best[key] = (best[key][0], best[key][1], best[key][2], best[key][3] + 1)
                        break
        cur += timedelta(hours=1)
    
    return best

def build_rows(best, natal_positions, natal_cusps, tz, orb):
    rows = []
    for (t_name, n_name, sym), (dt_t, diff, tlon, duration) in best.items():
        nm = next(x[2] for x in ASPECTS if x[1] == sym)
        desc = next(x[3] for x in ASPECTS if x[1] == sym)
        weight = get_weight(t_name, diff, orb)
        theme = get_theme(t_name, sym, n_name)
        house = get_house(natal_positions[n_name], natal_cusps)
        duration_days = duration / 24.0
        rows.append((dt_t, weight, t_name, sym, nm, n_name, diff, sign_str(tlon), 
                    house, duration_days, theme, desc))
    rows.sort(key=lambda x: x[0])
    return rows

def print_results(rows, start, end, orb, tz, natal_date, natal_time, include_inner):
    lines = []
    lines.append(f"\n{'='*85}")
    lines.append(f"  TRANSIT TIMELINE: {start} → {end}  |  Max orb {orb}°  |  UTC+{tz}")
    lines.append(f"  Natal: {natal_date} {natal_time} ICT | 19.91°N, 99.83°E")
    lines.append(f"  {'Inner planets included' if include_inner else 'Outer + TN planets only'}")
    lines.append(f"{'='*85}")
    
    # Table header
    lines.append(f"{'Date':12} {'Time':6} {'Transit':9} {'Aspect':14} {'Natal':8} {'Orb':>5} {'H':>2} {'Duration':>8} {'Core Theme'}")
    lines.append("-" * 85)
    
    for dt_t, _, t_name, sym, nm, n_name, diff, pos, house, dur, theme, desc in rows:
        date_str = dt_t.strftime('%Y-%m-%d')
        time_str = fmt_time(dt_t, tz)
        dur_str = f"{dur:.1f}d" if dur >= 1 else f"{int(dur*24)}h"
        theme_display = theme if theme else desc
        lines.append(f"{date_str:12} {time_str:6} {t_name:9} {sym+' '+nm:14} {n_name:8} {diff:>4.1f}° {house:>2} {dur_str:>8}  {theme_display}")
    
    lines.append(f"{'='*85}")
    
    # Summary by planet
    lines.append("\n📌 SUMMARY BY TRANSIT PLANET")
    by_planet = defaultdict(list)
    for r in rows:
        by_planet[r[2]].append(r)
    
    for planet in OUTER + TNS + (INNER if include_inner else []):
        if planet in by_planet:
            lines.append(f"\n  {planet}:")
            for r in by_planet[planet][:5]:
                dt_t, _, _, sym, _, n_name, diff, _, house, _, theme, _ = r
                lines.append(f"    {dt_t.strftime('%Y-%m-%d')} {sym} {n_name} (H{house}, {diff:.1f}°)")
    
    # Critical windows
    critical = [r for r in rows if r[2] in OUTER and r[6] < 1.0]
    if critical:
        lines.append(f"\n{'='*85}")
        lines.append("  🔴 CRITICAL WINDOWS (< 1.0° orb, outer planets)")
        lines.append(f"{'='*85}")
        for r in critical:
            dt_t, _, t_name, sym, nm, n_name, diff, pos, house, dur, theme, _ = r
            lines.append(f"  {dt_t.strftime('%Y-%m-%d')} {fmt_time(dt_t, tz)}  {t_name} {sym} {n_name}  {diff:.1f}° (H{house})  {theme}")
    
    return "\n".join(lines)

def main():
    parser = argparse.ArgumentParser(description='Transit Timeline with exact times and themes')
    parser.add_argument('start', help='Start date YYYY-MM-DD')
    parser.add_argument('end', help='End date YYYY-MM-DD')
    parser.add_argument('--orb', type=float, default=2.0, help='Max orb in degrees (default: 2.0)')
    parser.add_argument('--tz', type=int, default=7, help='Timezone offset from UTC (default: 7)')
    parser.add_argument('--inner', action='store_true', help='Include inner planet transits')
    parser.add_argument('--output', help='Save output to markdown file')
    args = parser.parse_args()
    
    # Boom natal data
    natal_date = "1996-11-20"
    natal_time = "20:37"
    lat, lon = 19.91, 99.83
    
    # Calculate natal chart
    ny, nm, nd = map(int, natal_date.split('-'))
    nth, ntm = map(int, natal_time.split(':'))
    dt_natal = datetime(ny, nm, nd, nth, ntm, tzinfo=timezone.utc) - timedelta(hours=args.tz)
    jd_natal = swe.julday(dt_natal.year, dt_natal.month, dt_natal.day, 
                          dt_natal.hour + dt_natal.minute/60.0)
    natal = get_chart(jd_natal)
    natal_cusps, natal_angles = swe.houses(jd_natal, lat, lon, b'P')
    natal_asc = natal_angles[0]
    natal_mc = natal_angles[1]
    
    # Date range
    sy, sm, sd = map(int, args.start.split('-'))
    ey, em, ed = map(int, args.end.split('-'))
    dstart = datetime(sy, sm, sd, 0, 0, tzinfo=timezone.utc) - timedelta(hours=args.tz)
    dend = datetime(ey, em, ed, 23, 0, tzinfo=timezone.utc) - timedelta(hours=args.tz)
    
    # Scan
    best = scan_range(dstart, dend, natal, natal_cusps, args.tz, args.orb, args.inner)
    rows = build_rows(best, natal, natal_cusps, args.tz, args.orb)
    
    # Output
    output = print_results(rows, args.start, args.end, args.orb, args.tz, 
                          natal_date, natal_time, args.inner)
    
    print(output)
    
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(f"# Transit Timeline: {args.start} → {args.end}\n\n")
            f.write(f"- **Natal**: {natal_date} {natal_time} ICT\n")
            f.write(f"- **Max Orb**: {args.orb}°\n")
            f.write(f"- **Timezone**: UTC+{args.tz}\n")
            f.write(f"- **Planets**: {'All' if args.inner else 'Outer + TN'}\n\n")
            f.write(output)
        print(f"\n✓ Saved to {args.output}")
    
    swe.close()

if __name__ == "__main__":
    main()
