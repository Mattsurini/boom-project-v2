#!/usr/bin/env python3
"""
VOC timer — uses shared hermes_astro calculation layer.
Usage: python voc_time.py <YYYY-MM-DD> <HH:MM> <lat> <lon>
       (ICT time, default: now at Chiang Rai)
"""
import sys
from datetime import datetime, timezone, timedelta
import hermes_astro
from hermes_astro import *
from hermes_astro import __version__, set_orb_system

# VOC here uses EXACT last-aspect timing (find the moment the Moon's last
# degree-based aspect perfects), so it does not consult the orb allowance
# tables. Selecting flatlib keeps it on its documented basis and leaves
# ALL_ORBS consistent for any helper that does read it.
set_orb_system('flatlib')

swe.set_ephe_path('')

ICT_LOCAL = timezone(timedelta(hours=7))

if len(sys.argv) > 3:
    dt_local = datetime.strptime(f"{sys.argv[1]} {sys.argv[2]}", '%Y-%m-%d %H:%M')
    lat = float(sys.argv[3])
    lon_p = float(sys.argv[4]) if len(sys.argv) > 4 else 99.83
else:
    dt_local = datetime.now(ICT_LOCAL)
    lat, lon_p = 19.91, 99.83

dt_local = dt_local.replace(tzinfo=ICT_LOCAL)
jd = jd_utc(dt_local)

pos = all_positions(jd, TRAD7)
m_lon = pos['Moon']['lon']
m_sign = sign_index(m_lon)


def moon_lon_at(t):
    t_u = t.astimezone(timezone.utc)
    jd_t = swe.julday(t_u.year, t_u.month, t_u.day,
                      t_u.hour + t_u.minute/60.0 + t_u.second/3600.0)
    mm, _ = swe.calc_ut(jd_t, swe.MOON, FLAGS)
    return mm[0]


def planet_lon_at(name, t):
    t_u = t.astimezone(timezone.utc)
    jd_t = swe.julday(t_u.year, t_u.month, t_u.day,
                      t_u.hour + t_u.minute/60.0 + t_u.second/3600.0)
    pp, _ = swe.calc_ut(jd_t, TRAD7_CODES[name], FLAGS)
    return pp[0]


def sep_abs_at(name, t):
    return abs(closest_distance(moon_lon_at(t), planet_lon_at(name, t)))


def bisect_root(a, b, fn):
    fa = fn(a)
    fb = fn(b)
    for _ in range(24):
        m = a + (b - a) / 2
        fm = fn(m)
        if fa * fm <= 0:
            b, fb = m, fm
        else:
            a, fa = m, fm
    return a + (b - a) / 2


def find_sign_boundary(anchor, direction):
    """Find Moon sign boundary before/after anchor."""
    anchor_sign = sign_index(moon_lon_at(anchor))
    step = timedelta(hours=2) * direction
    a = anchor
    b = anchor + step
    for _ in range(48):
        if sign_index(moon_lon_at(b)) != anchor_sign:
            lo, hi = (b, a) if direction < 0 else (a, b)
            for _ in range(24):
                mid = lo + (hi - lo) / 2
                if sign_index(moon_lon_at(mid)) == anchor_sign:
                    if direction < 0:
                        hi = mid
                    else:
                        lo = mid
                else:
                    if direction < 0:
                        lo = mid
                    else:
                        hi = mid
            return lo + (hi - lo) / 2
        a, b = b, b + step
    raise RuntimeError('Could not find Moon sign boundary')


def exact_moon_aspects_between(start_t, end_t):
    """Exact Moon major aspects to Traditional 7 within one Moon sign.

    Detects both sign-crossing roots AND near-touch aspects (local minima of
    |sep - asp| that never cross the aspect angle, e.g. a slowly moving partner
    where the Moon approaches and recedes without perfecting). For near-touch
    aspects a single global minimum per planet+aspect is emitted, so the Moon's
    last aspect is reported at its true closest approach.
    """
    roots = []
    step = timedelta(minutes=15)
    for planet in TRAD7:
        if planet == 'Moon':
            continue
        for asp in MAJOR_ASPECTS:
            t0 = start_t
            f0 = sep_abs_at(planet, t0) - asp
            # 1) Sign-crossing roots (aspect perfects).
            while t0 < end_t:
                t1 = min(t0 + step, end_t)
                f1 = sep_abs_at(planet, t1) - asp
                if f0 == 0 or f0 * f1 <= 0:
                    root = bisect_root(t0, t1, lambda t, p=planet, a=asp: sep_abs_at(p, t) - a)
                    if start_t <= root < end_t:
                        roots.append((root, planet, asp, sep_abs_at(planet, root) - asp))
                t0, f0 = t1, f1
            # 2) Near-touch aspect: global minimum of |sep - asp| that never
            #    crosses. Ternary-search over the whole sign interval.
            lo, hi = start_t, end_t
            fl, fh = sep_abs_at(planet, lo) - asp, sep_abs_at(planet, hi) - asp
            for _ in range(40):
                m1 = lo + (hi - lo) / 3
                m2 = hi - (hi - lo) / 3
                if abs(sep_abs_at(planet, m1) - asp) < abs(sep_abs_at(planet, m2) - asp):
                    hi = m2
                else:
                    lo = m1
            root = lo + (hi - lo) / 2
            froot = sep_abs_at(planet, root) - asp
            if start_t <= root < end_t and abs(froot) < 0.5:
                roots.append((root, planet, asp, froot))
    # De-duplicate: keep only the closest-approach root per planet+aspect.
    roots.sort(key=lambda x: (x[1], x[2], -abs(x[3])))
    best_per_key = {}
    for r in roots:
        key = (r[1], r[2])
        if key not in best_per_key or abs(r[3]) < abs(best_per_key[key][3]):
            best_per_key[key] = r
    deduped = sorted(best_per_key.values(), key=lambda x: x[0])
    return deduped


sign_start = find_sign_boundary(dt_local, -1)
sign_end = find_sign_boundary(dt_local, 1)
exact_aspects = exact_moon_aspects_between(sign_start + timedelta(seconds=1), sign_end)
last_aspect = exact_aspects[-1] if exact_aspects else None

print(f"☽ Moon @ {fmt_lon_full(m_lon)}")
print()

if last_aspect and dt_local <= last_aspect[0]:
    current_voc = False
    orb_now = abs(sep_abs_at(last_aspect[1], dt_local) - last_aspect[2])
    print("Current: Moon VOC? ❌ NO")
    print(f"  Last applying/exact before ingress: {ASPECT_SYMS[last_aspect[2]]} {last_aspect[1]} (orb={orb_now:.2f}°)")
elif last_aspect:
    current_voc = True
    print("Current: Moon VOC? ✅ YES")
else:
    current_voc = True
    print("Current: Moon VOC? ✅ YES")
    print("  No Traditional 7 major aspect before next sign ingress")
print()

print("=== Scanning for VOC start ===")
if last_aspect:
    voc_start = last_aspect[0]
    print(f"  🟢 Last aspect: {voc_start.strftime('%d %b %H:%M')} ICT "
          f"({ASPECT_SYMS[last_aspect[2]]} {last_aspect[1]} @ {fmt_lon(moon_lon_at(voc_start))})")
    print(f"  🟢 VOC START: {voc_start.strftime('%d %b %H:%M')} ICT (@ {fmt_lon(moon_lon_at(voc_start))})")
else:
    print(f"  🟢 VOC START: {sign_start.strftime('%d %b %H:%M')} ICT (entire sign, no aspects found)")
print(f"  🟢 VOC END:   {sign_end.strftime('%d %b %H:%M')} ICT (→ {SIGNS[sign_index(moon_lon_at(sign_end + timedelta(seconds=1)))]} @ {fmt_lon(moon_lon_at(sign_end))})")

print()
print(f"— hermes_astro v{__version__} (exact last-aspect VOC + "
      f"{EPHEMERIS_ENGINE}, orbs [{hermes_astro.ORB_SYSTEM}]) —")
swe.close()

