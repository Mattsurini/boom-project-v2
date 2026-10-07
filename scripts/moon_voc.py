#!/usr/bin/env python3
"""
Moon VOC (Void of Course) Calculator — exact minute precision
Uses flatlib VOC logic: last Ptolemaic aspect (Traditional 7) → next sign ingress
Root-finding for exact aspect times, binary search for exact ingress.
"""
import sys
import math
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass

# Use hermes-astro hub for all astrology calculations
from hermes_astro import (
    swe, TRAD7, TRAD7_CODES, MAJOR_ASPECTS, ASPECT_SYMS,
    ALL_ORBS, MAX_EXACT_ORB, FLAGS, ICT,
    jd_utc, planet_position, closest_distance
)


# ── Data classes ────────────────────────────────────────────────

@dataclass
class VOCAspect:
    """The exact aspect that starts VOC"""
    planet: str
    aspect_name: str
    symbol: str
    exact_time_ict: datetime
    orb: float
    movement: str  # 'applicative' or 'exact'


@dataclass
class VOCWindow:
    """Complete VOC window with exact boundaries"""
    voc_start: datetime      # exact time of last aspect (ICT)
    voc_end: datetime        # exact time of sign ingress (ICT)
    start_aspect: VOCAspect
    duration: timedelta
    is_current: bool         # True if now is within this window


# ── Core functions ──────────────────────────────────────────────

def get_trad7_positions(jd):
    """Get all Traditional 7 positions at JD"""
    return {name: planet_position(jd, code) for name, code in TRAD7_CODES.items()}


def check_all_aspects(moon_lon, moon_spd, trad7_positions):
    """Check Moon aspects to all Traditional 7 planets, return list of (planet, asp_deg, orb, movement)"""
    results = []
    for planet in TRAD7:
        if planet == 'Moon':
            continue
        p_lon, p_spd = trad7_positions[planet]
        sep = closest_distance(moon_lon, p_lon)
        abs_sep = abs(sep)

        for asp in MAJOR_ASPECTS:
            orb = abs(abs_sep - asp)
            active_orb = ALL_ORBS.get('Moon', 12)
            passive_orb = ALL_ORBS.get(planet, 7)

            # flatlib: both must be in orb for aspect to count
            if active_orb < orb and passive_orb < orb:
                continue

            in_orb_active = orb <= active_orb

            # Determine movement using actual speeds
            if sep >= 0:
                orb_dir = sep - asp
            else:
                orb_dir = sep + asp

            if abs(orb_dir) < MAX_EXACT_ORB:
                movement = 'exact'
            else:
                # Moon is always active/faster for inner aspects
                if (orb_dir > 0 and moon_spd > 0) or (orb_dir < 0 and moon_spd < 0):
                    movement = 'applicative'
                else:
                    movement = 'separative'

            if in_orb_active and movement in ('applicative', 'exact'):
                results.append({
                    'planet': planet,
                    'aspect': asp,
                    'orb': orb,
                    'movement': movement
                })
    return results


def find_exact_aspect_time(jd_start, jd_end, target_planet, target_asp_deg, moon_pos_start, trad7_pos_start):
    """
    Find exact time of minimum orb using ternary search.
    Returns (exact_jd, exact_orb) or (None, None)
    """
    def get_orb(jd):
        moon_lon, moon_spd = planet_position(jd, swe.MOON)
        p_lon, _ = planet_position(jd, TRAD7_CODES[target_planet])
        sep = closest_distance(moon_lon, p_lon)
        abs_sep = abs(sep)
        return abs(abs_sep - target_asp_deg)

    # Quick check
    orb_start = get_orb(jd_start)
    orb_end = get_orb(jd_end)
    if orb_start > 1.0 and orb_end > 1.0:
        mid = (jd_start + jd_end) / 2
        if get_orb(mid) >= min(orb_start, orb_end):
            return None, None

    # Ternary search
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

    if exact_orb <= 0.05:  # Very tight for exact aspect
        return exact_jd, exact_orb
    return None, None


def find_sign_ingress(jd_start, jd_end, start_sign):
    """Binary search for exact sign ingress time"""
    def get_sign(jd):
        moon_lon, _ = planet_position(jd, swe.MOON)
        return int(moon_lon // 30) % 12

    # Check if sign change happens in this range
    if get_sign(jd_start) != start_sign:
        return jd_start
    if get_sign(jd_end) == start_sign:
        return None  # no change in range

    # Binary search
    left, right = jd_start, jd_end
    for _ in range(30):
        mid = (left + right) / 2
        if get_sign(mid) != start_sign:
            right = mid
        else:
            left = mid
    return right


def jd_to_ict(jd):
    """Convert JD to ICT datetime"""
    y, m, d, h = swe.revjul(jd)
    hour = int(h)
    minute = int((h - hour) * 60)
    second = int(((h - hour) * 60 - minute) * 60)
    dt_utc = datetime(y, m, d, hour, minute, second, tzinfo=timezone.utc)
    return dt_utc.astimezone(ICT)


# ── Main VOC window finder ─────────────────────────────────────

def find_voc_window(start_dt: datetime = None, lat=19.91, lon=99.83) -> VOCWindow:
    """
    Find the current/next VOC window with exact minute precision.
    Returns VOCWindow with exact start (last aspect) and end (sign ingress).
    """
    if start_dt is None:
        start_dt = datetime.now(ICT)

    # Ensure timezone-aware
    if start_dt.tzinfo is None:
        start_dt = start_dt.replace(tzinfo=ICT)

    start_jd = jd_utc(start_dt)

    # Get initial Moon state
    moon_lon, moon_spd = planet_position(start_jd, swe.MOON)
    start_sign = int(moon_lon // 30) % 12
    trad7_pos = get_trad7_positions(start_jd)

    # Check current VOC status
    aspects_now = check_all_aspects(moon_lon, moon_spd, trad7_pos)
    current_voc = len(aspects_now) == 0

    # Scan forward to find sign change (max ~2.5 days for Moon)
    max_scan_days = 3
    scan_end_jd = start_jd + max_scan_days

    # Find sign ingress
    ingress_jd = find_sign_ingress(start_jd, scan_end_jd, start_sign)
    if ingress_jd is None:
        raise RuntimeError("Sign ingress not found within scan range")

    # Now find the LAST aspect before ingress
    # We need to scan from start_jd to ingress_jd and find the final exact aspect
    last_aspect = None
    last_aspect_jd = None

    # Use hourly steps to bracket aspects, then refine
    step_hours = 1.0
    cur_jd = start_jd
    step_jd = step_hours / 24.0

    # We need to find ALL aspects in the window, then pick the last one
    candidate_aspects = []

    while cur_jd < ingress_jd:
        next_jd = min(cur_jd + step_jd, ingress_jd)

        # Check aspects at both endpoints
        for jd in (cur_jd, next_jd):
            moon_lon_jd, moon_spd_jd = planet_position(jd, swe.MOON)
            trad7_pos_jd = get_trad7_positions(jd)
            aspects = check_all_aspects(moon_lon_jd, moon_spd_jd, trad7_pos_jd)

            for asp in aspects:
                planet = asp['planet']
                asp_deg = asp['aspect']
                orb = asp['orb']

                if orb < 0.5:  # Close enough to warrant exact refinement
                    exact_jd, exact_orb = find_exact_aspect_time(
                        cur_jd, next_jd, planet, asp_deg,
                        None, None
                    )
                    if exact_jd and exact_jd < ingress_jd:
                        candidate_aspects.append({
                            'jd': exact_jd,
                            'planet': planet,
                            'asp_deg': asp_deg,
                            'orb': exact_orb,
                            'movement': asp['movement']
                        })

        cur_jd = next_jd

    # Pick the LATEST aspect before ingress
    if candidate_aspects:
        candidate_aspects.sort(key=lambda x: x['jd'], reverse=True)
        last = candidate_aspects[0]
        last_aspect_jd = last['jd']
        last_aspect = last

    # If no aspect found in forward scan, scan backward from start
    if last_aspect is None:
        # Scan backward ~1 day
        back_start = start_jd - 1.0
        cur_jd = back_start
        while cur_jd < start_jd:
            next_jd = min(cur_jd + step_jd, start_jd)
            moon_lon_jd, moon_spd_jd = planet_position(cur_jd, swe.MOON)
            trad7_pos_jd = get_trad7_positions(cur_jd)
            aspects = check_all_aspects(moon_lon_jd, moon_spd_jd, trad7_pos_jd)

            for asp in aspects:
                if asp['orb'] < 0.5:
                    exact_jd, exact_orb = find_exact_aspect_time(
                        cur_jd, next_jd, asp['planet'], asp['aspect'], None, None
                    )
                    if exact_jd:
                        candidate_aspects.append({
                            'jd': exact_jd,
                            'planet': asp['planet'],
                            'asp_deg': asp['aspect'],
                            'orb': exact_orb,
                            'movement': asp['movement']
                        })
            cur_jd = next_jd

        if candidate_aspects:
            candidate_aspects.sort(key=lambda x: x['jd'], reverse=True)
            last = candidate_aspects[0]
            last_aspect_jd = last['jd']
            last_aspect = last

    if last_aspect is None:
        raise RuntimeError("No qualifying aspect found for VOC start")

    # Build result
    voc_start = jd_to_ict(last_aspect_jd)
    voc_end = jd_to_ict(ingress_jd)
    duration = voc_end - voc_start

    is_current = current_voc and start_dt >= voc_start and start_dt < voc_end

    start_aspect = VOCAspect(
        planet=last_aspect['planet'],
        aspect_name={0: 'Conjunction', 60: 'Sextile', 90: 'Square', 120: 'Trine', 180: 'Opposition'}[last_aspect['asp_deg']],
        symbol=ASPECT_SYMS[last_aspect['asp_deg']],
        exact_time_ict=voc_start,
        orb=last_aspect['orb'],
        movement=last_aspect['movement']
    )

    return VOCWindow(
        voc_start=voc_start,
        voc_end=voc_end,
        start_aspect=start_aspect,
        duration=duration,
        is_current=is_current
    )


def format_voc_window(voc: VOCWindow) -> str:
    """Format VOC window for display"""
    lines = []
    lines.append("=" * 60)
    lines.append("MOON VOC WINDOW (Traditional 7 planets)")
    lines.append("=" * 60)
    lines.append(f"VOC Begins: {voc.voc_start.strftime('%Y-%m-%d %H:%M:%S')} ICT")
    lines.append(f"  Last aspect: Moon {voc.start_aspect.symbol} {voc.start_aspect.planet} "
                 f"({voc.start_aspect.aspect_name})")
    lines.append(f"  Orb: {voc.start_aspect.orb:.4f}° ({voc.start_aspect.movement})")
    lines.append(f"VOC Ends:   {voc.voc_end.strftime('%Y-%m-%d %H:%M:%S')} ICT")
    lines.append(f"  Sign ingress")
    lines.append(f"Duration:   {voc.duration}")
    lines.append(f"Status:     {'ACTIVE NOW' if voc.is_current else 'Not active'}")
    lines.append("=" * 60)
    return "\n".join(lines)


# ── CLI ─────────────────────────────────────────────────────────

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Moon VOC Calculator — exact minute precision')
    parser.add_argument('--date', help='Start date YYYY-MM-DD (default: today)')
    parser.add_argument('--time', help='Start time HH:MM (default: now)')
    parser.add_argument('--lat', type=float, default=19.91, help='Latitude')
    parser.add_argument('--lon', type=float, default=99.83, help='Longitude')
    args = parser.parse_args()

    if args.date:
        if args.time:
            dt = datetime.strptime(f"{args.date} {args.time}", "%Y-%m-%d %H:%M")
        else:
            dt = datetime.strptime(args.date, "%Y-%m-%d")
        dt = dt.replace(tzinfo=ICT)
    else:
        dt = datetime.now(ICT)

    voc = find_voc_window(dt, args.lat, args.lon)
    print(format_voc_window(voc))


if __name__ == "__main__":
    main()