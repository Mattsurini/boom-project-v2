#!/usr/bin/env python3
"""
Transit Timeline v3 — exact minute aspect times with root-finding.
Usage: python transit_timeline_v3.py <start> <end> [options]
  start/end: YYYY-MM-DD (e.g., 2026-09-07 2026-09-07)
Options:
  --orb N         Max orb in degrees (default: 2.0)
  --tz N          Timezone offset from UTC (default: 7 for ICT)
  --inner         Include inner planet transits (Sun, Moon, Mercury, Venus, Mars)
  --output FILE   Save to markdown file
  --step H        Hourly scan step (default: 1.0 hour)
"""
import sys
try:
    import swisseph as swe_raw
except ModuleNotFoundError:
    sys.exit(
        "swisseph not found in this interpreter.\n"
        "Run with the Hermes venv python:\n"
        "  C:/Users/Turbo/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe "
        "transit_timeline_v3.py <start> <end>"
    )
import math
import argparse
from datetime import datetime, timedelta, timezone
from collections import defaultdict

# Use hermes-astro hub for all astrology calculations
from hermes_astro import (
    swe, SIGNS, SIGNS_SHORT, ASPECT_NAMES, ASPECT_SYMS,
    PLANET_ORBS, OUTER_ORBS, TRAD7, TRAD7_CODES, MAJOR_ASPECTS,
    MAX_EXACT_ORB, ICT, FLAGS,
    jd_utc, planet_position, all_positions, houses, house_of,
    closest_distance, check_aspect_with_speed,
    fmt_lon, fmt_lon_full, sign_index
)

# swe.set_ephe_path('')  # handled by hermes_astro

# ─── CONSTANTS ───
# Use hermes-astro hub constants
SIGNS = ['♈Aries','♉Taurus','♊Gemini','♋Cancer','♌Leo','♍Virgo',
         '♎Libra','♏Scorpio','♐Sagittarius','♑Capricorn','♒Aquarius','♓Pisces']
SIGNS_SHORT = ['♈','♉','♊','♋','♌','♍','♎','♏','♐','♑','♒','♓']
PLANETS = TRAD7 + ['Uranus', 'Neptune', 'Pluto']
TNS = ['Cupido', 'Hades', 'Zeus', 'Kronos', 'Apollon', 'Admetos', 'Vulcanus', 'Poseidon']
ALL_BODIES = PLANETS + TNS

# Extended body codes for TN points (not in hermes_astro)
# TN_CODES replaced by direct use of swisseph constants

# Combine TRAD7_CODES with TN_CODES
BODY_CODES = {**TRAD7_CODES, 
              'Cupido': swe_raw.CUPIDO, 'Hades': swe_raw.HADES, 'Zeus': swe_raw.ZEUS, 'Kronos': swe_raw.KRONOS,
              'Apollon': swe_raw.APOLLON, 'Admetos': swe_raw.ADMETOS, 'Vulcanus': swe_raw.VULKANUS, 'Poseidon': swe_raw.POSEIDON,
              'Uranus': swe_raw.URANUS, 'Neptune': swe_raw.NEPTUNE, 'Pluto': swe_raw.PLUTO}

ASPECTS = [
    (0, "☌", "Conjunction", "Fusion, intensification"),
    (60, "⚹", "Sextile", "Opportunity, flow"),
    (90, "□", "Square", "Tension, challenge, action"),
    (120, "△", "Trine", "Harmony, ease, talent"),
    (180, "☍", "Opposition", "Polarity, confrontation, balance"),
]

INNER = ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars']
OUTER = ['Jupiter', 'Saturn', 'Uranus', 'Neptune', 'Pluto']

# ─── THEMES DATABASE ───
THEMES = {
    # Saturn
    ("Saturn", "Jupiter", "□"): "Expansion blocked by structure; patience required",
    ("Saturn", "Mercury", "△"): "Disciplined communication, mature planning",
    ("Saturn", "Moon", "☌"): "Emotional weight, responsibility, maturation",
    ("Saturn", "Saturn", "☌"): "Saturn return echo; structural reckoning in career/status",
    ("Saturn", "Sun", "□"): "Identity constraint; authority test",
    ("Saturn", "Venus", "☌"): "Relationship sobriety; commitment or restriction",
    ("Saturn", "Mars", "□"): "Action blocked; forced patience",
    ("Saturn", "Uranus", "⚹"): "Innovation meets discipline; structured breakthrough",
    ("Saturn", "Neptune", "☌"): "Dreams meet reality; disillusionment or manifestation",
    ("Saturn", "Pluto", "△"): "Deep structural support; disciplined transformation",
    # Jupiter
    ("Jupiter", "Mercury", "△"): "Big-picture thinking, learning surge",
    ("Jupiter", "Venus", "⚹"): "Relationship/financial growth window",
    ("Jupiter", "Sun", "□"): "Overreach risk; check ambition",
    ("Jupiter", "Moon", "△"): "Emotional optimism, social luck",
    ("Jupiter", "Jupiter", "☌"): "Luck peak; expansion year",
    ("Jupiter", "Mars", "△"): "Confident action; physical vitality",
    ("Jupiter", "Saturn", "△"): "Growth through discipline; wise expansion",
    # Uranus
    ("Uranus", "Pluto", "☍"): "Radical structural snap; generational climax",
    ("Uranus", "Sun", "☍"): "Identity jolt; sudden self-disruption",
    ("Uranus", "Moon", "⚹"): "Emotional breakthrough; sudden insight",
    ("Uranus", "Saturn", "⚹"): "Innovation meets discipline",
    ("Uranus", "Uranus", "△"): "Identity liberation; freedom surge",
    ("Uranus", "Mercury", "☍"): "Mental jolt; unexpected news/idea",
    ("Uranus", "Venus", "☌"): "Sudden attraction; relationship disruption",
    ("Uranus", "Mars", "△"): "Impulsive action; energy spike",
    # Neptune
    ("Neptune", "Moon", "☌"): "Emotional fog; boundary loss; sensitivity spike",
    ("Neptune", "Saturn", "☌"): "Structures dissolve; fatigue; spiritual surrender",
    ("Neptune", "Pluto", "△"): "Deep spiritual transformation undercurrent",
    ("Neptune", "Uranus", "⚹"): "Visionary breakthrough; illusion vs. innovation",
    ("Neptune", "Mercury", "△"): "Intuitive thinking; creative imagination",
    ("Neptune", "Sun", "△"): "Spiritual illumination; ego dissolution",
    ("Neptune", "Venus", "☌"): "Romantic idealism; fantasy in love",
    ("Neptune", "Mars", "☍"): "Action dissolves; fatigue or idealism clash",
    # Pluto
    ("Pluto", "Uranus", "☌"): "Generational reset personalizing; radical rebirth",
    ("Pluto", "Moon", "⚹"): "Emotional power regeneration; deep purge",
    ("Pluto", "Pluto", "⚹"): "Personal power regeneration; shadow work",
    ("Pluto", "Sun", "☌"): "Identity death/rebirth; obsession peak",
    ("Pluto", "Mercury", "⚹"): "Mental depth; investigative clarity",
    ("Pluto", "Saturn", "⚹"): "Disciplined transformation; authority purge",
    ("Pluto", "Venus", "☌"): "Intense relationship/financial transformation",
    ("Pluto", "Mars", "△"): "Empowered action; deep drive",
    ("Pluto", "Jupiter", "△"): "Transformation through expansion; power growth",
    # TN Points
    ("Hades", "Jupiter", "☍"): "Shadow material on luck/beliefs; deep reckoning",
    ("Kronos", "Jupiter", "☍"): "Authority/legacy tension with growth",
    ("Poseidon", "Jupiter", "⚹"): "Spiritual wisdom expands",
    ("Zeus", "Neptune", "□"): "Driven action vs. illusion; verify before pushing",
    ("Zeus", "Venus", "☌"): "Desire/action fuse with values; explosive attraction",
    ("Cupido", "Mars", "△"): "Social/romantic initiative",
    ("Vulcanus", "Pluto", "△"): "Power/authority dynamic regenerates",
    ("Admetos", "Uranus", "△"): "Endurance meets innovation; stubborn breakthrough",
    ("Apollon", "Jupiter", "☌"): "Success/multiplication peak; abundance",
    # Inner planets (common)
    ("Sun", "Mercury", "△"): "Mental clarity; self-expression flows",
    ("Sun", "Venus", "⚹"): "Social charm; creative expression",
    ("Sun", "Mars", "□"): "Ego-driven action; conflict potential",
    ("Sun", "Jupiter", "△"): "Confidence surge; expansive mood",
    ("Sun", "Saturn", "□"): "Reality check; responsibility weighs",
    ("Sun", "Uranus", "⚹"): "Sudden self-awareness; uniqueness shines",
    ("Sun", "Neptune", "△"): "Compassion; spiritual openness",
    ("Sun", "Pluto", "☌"): "Power encounter; transformation trigger",
    ("Moon", "Mercury", "△"): "Emotional fluency; intuitive speech",
    ("Moon", "Venus", "☌"): "Affection needs; relationship sensitivity",
    ("Moon", "Mars", "□"): "Emotional agitation; reactive energy",
    ("Moon", "Jupiter", "△"): "Emotional optimism; nurturing expansion",
    ("Moon", "Saturn", "☌"): "Emotional withdrawal; serious mood",
    ("Moon", "Uranus", "⚹"): "Sudden feelings; emotional breakthrough",
    ("Moon", "Neptune", "△"): "Dreamy sensitivity; psychic openness",
    ("Moon", "Pluto", "☌"): "Emotional intensity; power struggle",
    ("Mercury", "Mercury", "☌"): "Mental focus; communication peak",
    ("Mercury", "Venus", "⚹"): "Pleasant communication; artistic thought",
    ("Mercury", "Mars", "☌"): "Sharp mind; aggressive speech",
    ("Mercury", "Jupiter", "△"): "Expansive thinking; learning opportunity",
    ("Mercury", "Saturn", "△"): "Structured thought; serious planning",
    ("Mercury", "Uranus", "☍"): "Mental rebellion; unexpected ideas",
    ("Mercury", "Neptune", "☍"): "Confused thinking; deceptive communication",
    ("Mercury", "Pluto", "△"): "Deep investigation; transformative insight",
    ("Venus", "Venus", "☌"): "Self-love; values alignment; aesthetic peak",
    ("Venus", "Mars", "△"): "Passionate attraction; creative drive",
    ("Venus", "Jupiter", "⚹"): "Social expansion; romantic opportunity",
    ("Venus", "Saturn", "☍"): "Relationship test; commitment or ending",
    ("Venus", "Uranus", "△"): "Sudden attraction; unconventional love",
    ("Venus", "Neptune", "△"): "Romantic idealism; artistic inspiration",
    ("Venus", "Pluto", "☌"): "Obsessive love; financial power play",
    ("Mars", "Mars", "☌"): "Energy peak; action initiation; potential conflict",
    ("Mars", "Jupiter", "☍"): "Overconfidence in action; reckless expansion",
    ("Mars", "Saturn", "□"): "Frustrated action; blocked drive",
    ("Mars", "Uranus", "☍"): "Sudden aggression; explosive energy",
    ("Mars", "Neptune", "☍"): "Drained drive; confused action",
    ("Mars", "Pluto", "□"): "Power struggle; compulsive action",
}

# ─── UTILITY FUNCTIONS ───

def aspect_angle(l1, l2):
    """Absolute angular distance between two longitudes (0-180°)."""
    d = abs(l1 - l2)
    if d > 180:
        d = 360 - d
    return d


def get_chart(jd, flags=FLAGS):
    r = {}
    for name in ALL_BODIES:
        code = BODY_CODES[name]
        # Fallback to swe_raw if code >= 40 for TNs
        if code >= 40:
            arr, _ = swe_raw.calc_ut(jd, code, flags)
        else:
            arr, _ = swe.calc_ut(jd, code, flags)
        r[name] = arr[0]
    return r


def transit_lon(jd, name, flags=FLAGS):
    """Longitude of a single body (fast path for root-finding inner loops)."""
    code = BODY_CODES[name]
    if code >= 40:
        arr, _ = swe_raw.calc_ut(jd, code, flags)
    else:
        arr, _ = swe.calc_ut(jd, code, flags)
    return arr[0]


def get_chart_with_speed(jd):
    r = {}
    for name in ALL_BODIES:
        code = BODY_CODES[name]
        # Fallback to swe_raw if code >= 40 for TNs
        if code >= 40:
            arr, _ = swe_raw.calc_ut(jd, code, FLAGS)
        else:
            arr, _ = swe.calc_ut(jd, code, FLAGS)
        r[name] = (arr[0], arr[3])  # (longitude, speed deg/day)
    return r


def sign_str(lon):
    s = int(lon // 30)
    return f"{SIGNS[s]} {lon - s * 30:.1f}°"


def fmt_time(dt, tz):
    local = dt + timedelta(hours=tz)
    return local.strftime('%H:%M')


def fmt_datetime(dt, tz):
    local = dt + timedelta(hours=tz)
    return local.strftime('%Y-%m-%d %H:%M')


def get_house(lon, cusps):
    for i in range(11):
        c1, c2 = cusps[i], cusps[i + 1]
        if c2 < c1 and (lon >= c1 or lon < c2):
            return i + 1
        if c1 <= lon < c2:
            return i + 1
    return 12


def get_theme(t_name, sym, n_name):
    return THEMES.get((t_name, n_name, sym), "")


def get_weight(t_name, diff, orb):
    w = 1
    if t_name in OUTER:
        w = 4
    elif t_name in ["Jupiter"]:
        w = 2
    elif t_name in TNS:
        w = 3
    elif t_name in INNER:
        w = 1
    w += max(0, int((orb - diff) * 3))
    return w


# ─── ROOT-FINDING FOR EXACT ASPECT TIME ───

def find_exact_aspect_time(jd_start, jd_end, t_name, n_name, target_deg, natal_pos, orb_limit=2.0):
    """
    Find exact time of minimum orb in [jd_start, jd_end] using ternary search.
    More robust than crossing detection — works for all aspect types including opposition.
    Returns (exact_jd, exact_orb) or (None, None) if minimum orb > orb_limit.
    """
    def get_orb(jd):
        a = aspect_angle(transit_lon(jd, t_name), natal_pos[n_name])
        return abs(a - target_deg)

    # Quick check: if both endpoints have orb > orb_limit and no sign of crossing, skip
    orb_start = get_orb(jd_start)
    orb_end = get_orb(jd_end)
    if orb_start > orb_limit and orb_end > orb_limit:
        # Check midpoint to see if there's a dip
        mid = (jd_start + jd_end) / 2
        orb_mid = get_orb(mid)
        if orb_mid >= min(orb_start, orb_end):
            return None, None  # no crossing in this interval

    # Ternary search for minimum orb (unimodal function in small interval)
    left, right = jd_start, jd_end
    for _ in range(40):
        m1 = left + (right - left) / 3
        m2 = right - (right - left) / 3
        f1 = get_orb(m1)
        f2 = get_orb(m2)
        if f1 < f2:
            right = m2
        else:
            left = m1

    exact_jd = (left + right) / 2
    exact_orb = get_orb(exact_jd)

    if exact_orb <= orb_limit:
        return exact_jd, exact_orb
    return None, None


def find_aspect_window(jd_center, t_name, n_name, target_deg, natal_pos, orb_threshold):
    """
    Find the time range when orb <= orb_threshold around exact aspect.
    Returns (start_jd, end_jd) in UTC.
    """
    def get_orb(jd):
        a = aspect_angle(transit_lon(jd, t_name), natal_pos[n_name])
        return abs(a - target_deg)

    # Search backward for start
    step = 1.0 / 24.0  # 1 hour in days
    left = jd_center
    for _ in range(int(orb_threshold * 10) + 50):  # generous search
        if get_orb(left) > orb_threshold:
            break
        left -= step

    # Search forward for end
    right = jd_center
    for _ in range(int(orb_threshold * 10) + 50):
        if get_orb(right) > orb_threshold:
            break
        right += step

    # Refine boundaries with binary search
    # Start boundary
    l, r = left, jd_center
    for _ in range(20):
        m = (l + r) / 2
        if get_orb(m) <= orb_threshold:
            r = m
        else:
            l = m
    start_jd = r

    # End boundary
    l, r = jd_center, right
    for _ in range(20):
        m = (l + r) / 2
        if get_orb(m) <= orb_threshold:
            l = m
        else:
            r = m
    end_jd = l

    return start_jd, end_jd


def jd_to_dt(jd):
    """Convert Julian Day to datetime (UTC)."""
    # swe.revjul gives year, month, day, hour (decimal)
    y, m, d, h = swe.revjul(jd)
    hour = int(h)
    minute = int((h - hour) * 60)
    second = int(((h - hour) * 60 - minute) * 60)
    return datetime(y, m, d, hour, minute, second, tzinfo=timezone.utc)


# ─── MAIN SCAN ───

def scan_range_exact(dstart, dend, natal, natal_cusps, tz, orb, include_inner, step_hours=1.0):
    """
    Scan for candidate aspects within orb, then refine each unique aspect once
    over the full range to the exact minute.
    Returns list of exact events with precise timing and duration.
    """
    events = {}  # key -> event dict

    cur = dstart
    step = timedelta(hours=step_hours)

    print(f"Scanning {dstart.strftime('%Y-%m-%d')} to {dend.strftime('%Y-%m-%d')} (step={step_hours}h)...", file=sys.stderr)

    jd_start = swe.julday(dstart.year, dstart.month, dstart.day, dstart.hour + dstart.minute / 60.0)
    jd_end = swe.julday(dend.year, dend.month, dend.day, dend.hour + dend.minute / 60.0)

    # Phase 1: cheap detection — which (transit, natal, aspect) are within orb anywhere in range
    # candidates[key] = [deg, sym, nm, desc, best_diff, best_jd]
    candidates = {}
    while cur <= dend:
        jd_cur = swe.julday(cur.year, cur.month, cur.day, cur.hour + cur.minute / 60.0)
        trans = get_chart(jd_cur)
        for t_name in ALL_BODIES:
            if not include_inner and t_name in INNER:
                continue
            for n_name in PLANETS:
                for deg, sym, nm, desc in ASPECTS:
                    angle = aspect_angle(trans[t_name], natal[n_name])
                    diff = abs(angle - deg)
                    if diff <= orb:
                        key = (t_name, n_name, sym)
                        if key not in candidates:
                            candidates[key] = [deg, sym, nm, desc, diff, jd_cur]
                        elif diff < candidates[key][4]:
                            candidates[key][4] = diff
                            candidates[key][5] = jd_cur
        cur = cur + step

    # Phase 2: refine each unique aspect once over the full range
    for key, (deg, sym, nm, desc, best_diff, best_jd) in candidates.items():
        t_name, n_name = key[0], key[1]
        exact_jd, exact_orb = find_exact_aspect_time(jd_start, jd_end, t_name, n_name, deg, natal, orb)
        if exact_jd is None or exact_orb > orb:
            # Root-finding didn't confirm a crossing (e.g. fast inner aspect dipping
            # in-and-out of orb mid-range). Fall back to the closest sample point.
            exact_jd, exact_orb = best_jd, best_diff
        if exact_orb > orb:
            continue

        exact_dt = jd_to_dt(exact_jd)

        # Find exact window (duration)
        start_jd, end_jd = find_aspect_window(exact_jd, t_name, n_name, deg, natal, orb)
        start_dt = jd_to_dt(start_jd)
        end_dt = jd_to_dt(end_jd)
        duration_days = (end_jd - start_jd)

        # Transit position at exact moment
        tlon = transit_lon(exact_jd, t_name)

        # House of natal planet
        house = get_house(natal[n_name], natal_cusps)

        # Weight for sorting
        weight = get_weight(t_name, exact_orb, orb)

        theme = get_theme(t_name, sym, n_name)

        event = {
            'exact_dt': exact_dt,
            'start_dt': start_dt,
            'end_dt': end_dt,
            'duration_days': duration_days,
            't_name': t_name,
            'n_name': n_name,
            'sym': sym,
            'aspect_name': nm,
            'aspect_desc': desc,
            'orb': exact_orb,
            'tlon': tlon,
            'house': house,
            'weight': weight,
            'theme': theme,
        }

        if key not in events or exact_orb < events[key]['orb']:
            events[key] = event

    return list(events.values())


def print_results(events, start, end, orb, tz, natal_date, natal_time, include_inner):
    lines = []
    lines.append(f"\n{'='*95}")
    lines.append(f"  TRANSIT TIMELINE v3 (EXACT MINUTE): {start} → {end}  |  Max orb {orb}°  |  UTC+{tz}")
    lines.append(f"  Natal: {natal_date} {natal_time} ICT | 19.91°N, 99.83°E")
    lines.append(f"  {'Inner planets included' if include_inner else 'Outer + TN planets only'}")
    lines.append(f"{'='*95}")

    # Table header
    lines.append(f"{'Exact Time':17} {'Dur':>7} {'Transit':9} {'Aspect':14} {'Natal':8} {'Orb':>5} {'H':>2} {'Core Theme'}")
    lines.append("-" * 95)

    for ev in sorted(events, key=lambda x: x['exact_dt']):
        exact_str = fmt_datetime(ev['exact_dt'], tz)
        dur_days = ev['duration_days']
        dur_str = f"{dur_days:.2f}d" if dur_days >= 1 else f"{dur_days*24:.1f}h"
        theme_display = ev['theme'] if ev['theme'] else ev['aspect_desc']
        lines.append(f"{exact_str:17} {dur_str:>7} {ev['t_name']:9} {ev['sym']+' '+ev['aspect_name']:14} {ev['n_name']:8} {ev['orb']:>4.1f}° {ev['house']:>2}  {theme_display}")

    lines.append(f"{'='*95}")

    # Summary by planet
    lines.append("\n📌 SUMMARY BY TRANSIT PLANET")
    by_planet = defaultdict(list)
    for ev in events:
        by_planet[ev['t_name']].append(ev)

    for planet in OUTER + TNS + (INNER if include_inner else []):
        if planet in by_planet:
            lines.append(f"\n  {planet}:")
            for ev in sorted(by_planet[planet], key=lambda x: x['orb'])[:5]:
                exact_str = fmt_datetime(ev['exact_dt'], tz)
                lines.append(f"    {exact_str} {ev['sym']} {ev['n_name']} (H{ev['house']}, {ev['orb']:.1f}°)")

    # Critical windows
    critical = [ev for ev in events if ev['t_name'] in OUTER and ev['orb'] < 1.0]
    if critical:
        lines.append(f"\n{'='*95}")
        lines.append("  🔴 CRITICAL WINDOWS (< 1.0° orb, outer planets)")
        lines.append(f"{'='*95}")
        for ev in sorted(critical, key=lambda x: x['orb']):
            exact_str = fmt_datetime(ev['exact_dt'], tz)
            lines.append(f"  {exact_str}  {ev['t_name']} {ev['sym']} {ev['n_name']}  {ev['orb']:.1f}° (H{ev['house']})  {ev['theme']}")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description='Transit Timeline v3 — exact minute aspects with root-finding')
    parser.add_argument('start', help='Start date YYYY-MM-DD')
    parser.add_argument('end', help='End date YYYY-MM-DD')
    parser.add_argument('--orb', type=float, default=2.0, help='Max orb in degrees (default: 2.0)')
    parser.add_argument('--tz', type=int, default=7, help='Timezone offset from UTC (default: 7)')
    parser.add_argument('--inner', action='store_true', help='Include inner planet transits')
    parser.add_argument('--output', help='Save output to markdown file')
    parser.add_argument('--step', type=float, default=1.0, help='Hourly scan step in hours (default: 1.0)')
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
                          dt_natal.hour + dt_natal.minute / 60.0)
    natal = get_chart(jd_natal)
    natal_cusps, natal_angles = swe.houses(jd_natal, lat, lon, b'P')
    natal_asc = natal_angles[0]
    natal_mc = natal_angles[1]

    # Date range
    sy, sm, sd = map(int, args.start.split('-'))
    ey, em, ed = map(int, args.end.split('-'))
    dstart = datetime(sy, sm, sd, 0, 0, tzinfo=timezone.utc) - timedelta(hours=args.tz)
    dend = datetime(ey, em, ed, 23, 0, tzinfo=timezone.utc) - timedelta(hours=args.tz)

    # Scan with exact timing
    events = scan_range_exact(dstart, dend, natal, natal_cusps, args.tz, args.orb, args.inner, args.step)

    # Output
    output = print_results(events, args.start, args.end, args.orb, args.tz,
                          natal_date, natal_time, args.inner)

    print(output)

    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(f"# Transit Timeline v3 (Exact Minute): {args.start} → {args.end}\n\n")
            f.write(f"- **Natal**: {natal_date} {natal_time} ICT\n")
            f.write(f"- **Max Orb**: {args.orb}°\n")
            f.write(f"- **Timezone**: UTC+{args.tz}\n")
            f.write(f"- **Planets**: {'All' if args.inner else 'Outer + TN'}\n")
            f.write(f"- **Scan Step**: {args.step}h\n\n")
            f.write(output)
        print(f"\n✓ Saved to {args.output}")

    swe.close()


if __name__ == "__main__":
    main()