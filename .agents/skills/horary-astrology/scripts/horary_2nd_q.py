#!/usr/bin/env python3
"""
Horary Q2 — Moon-referenced chart (Prashna Tantra multiple-query system).
Rotates the chart so the Moon becomes the ASC; the Moon then represents the
querent and the ruler of the topic house (in the rotated chart) the quesited.

Usage: python horary_2nd_q.py "<question>" <YYYY-MM-DD> <HH:MM> <lat> <lon> [--placidus] [--json]
       (ICT time, defaults to now and Chiang Rai 19.91/99.83)
Options:
  --placidus     Rotate Placidus cusps so Moon = ASC (default: Tropical Whole Sign, H1 = Moon's sign)
  --json         Emit a machine-readable JSON object instead of the text report
"""
import sys
import json
from datetime import datetime, timezone, timedelta

import hermes_astro as ha
from hermes_astro import swe

swe.set_ephe_path('')

ICT_LOCAL = timezone(timedelta(hours=7))
PLANET_SYM = {'Sun': '☉', 'Moon': '☽', 'Mercury': '☿', 'Venus': '♀',
              'Mars': '♂', 'Jupiter': '♃', 'Saturn': '♄'}
HOUSE_NAMES = {1: "Self/Querent", 2: "Money", 3: "Siblings/Comm", 4: "Home/Father",
               5: "Children/Romance", 6: "Work/Health", 7: "Partner/Marriage",
               8: "Death/Sex/Inherit", 9: "Travel/Law", 10: "Career/Mother",
               11: "Friends", 12: "Hidden/Institutions"}


def cast(question, dt_local, lat, lon_p, whole_sign=False):
    jd = ha.jd_utc(dt_local)
    pos = ha.all_positions(jd, ha.TRAD7)
    cusps, orig_asc, mc_lon = ha.houses(jd, lat, lon_p)
    moon = pos['Moon']
    moon_lon = moon['lon']
    moon_sign = ha.sign_index(moon_lon)

    # ── Rotate so Moon = ASC ──
    if whole_sign:
        # H1 = Moon's sign; house N's sign = (moon_sign + N - 1) % 12
        def h_of(lon):
            return (ha.sign_index(lon) - moon_sign) % 12 + 1
        new_cusps = [((moon_sign + i) * 30) % 360 for i in range(12)]
        rotation = 0.0
    else:
        rotation = (moon_lon - orig_asc) % 360
        new_cusps = [(c + rotation) % 360 for c in cusps]

        def h_of(lon):
            return ha.house_of(lon, new_cusps)

    # ── Radicality (Moon-referenced) ──
    new_asc_deg = moon_lon % 30
    st_name, st_meaning = ha.sign_type(moon_sign)
    m_deg = moon_lon % 30
    m_hours_left = (30 - m_deg) / moon['speed'] * 24 if moon['speed'] > 0 else 999
    voc_now, blocking = ha.moon_voc_status(jd, pos)
    sat_house = h_of(pos['Saturn']['lon'])

    # ── Significators (rotated chart) ──
    # Querent = Moon (now the ASC)
    qr_dign, qr_label = ha.dignity('Moon', moon_lon)
    # Quesited = ruler of the topic house in the rotated chart
    q_house, q_kw = ha.quesited_house(question)
    if whole_sign:
        qs_cusp_sign = (moon_sign + q_house - 1) % 12
    else:
        qs_cusp_sign = ha.sign_index(new_cusps[q_house - 1])
    quesited_name = ha.ruler_of(qs_cusp_sign)
    qs = pos[quesited_name]
    qs_house = h_of(qs['lon'])
    qs_dign, qs_label = ha.dignity(quesited_name, qs['lon'])

    # ── Aspect between Moon (querent) and quesited ruler ──
    aspects = ha.check_aspect_with_speed(
        moon_lon, 'Moon', moon['speed'], qs['lon'], quesited_name, qs['speed'])
    timing = None
    if aspects:
        for asp in aspects:
            if asp['movement'] in ('applicative', 'exact') and asp['orb'] > 0:
                rel = abs(moon['speed'] - qs['speed'])
                if rel > 0.01:
                    timing = asp['orb'] / rel * 24
    translation = None
    collection = []
    if not aspects:
        translation = ha.translation_of_light(jd, pos, 'Moon', quesited_name)
        collection = ha.collection_of_light(jd, pos, 'Moon', quesited_name)

    # ── Houses list (rotated) ──
    houses_out = []
    for i in range(12):
        nc = new_cusps[i]
        si = ha.sign_index(nc)
        flag = 'ASC (Moon)' if i == 0 else None
        houses_out.append({'n': i + 1, 'sign': ha.SIGNS[si],
                           'deg': round(nc % 30, 2), 'flag': flag})

    # ── Planets list ──
    planets_out = []
    for pname in ha.TRAD7:
        p = pos[pname]
        planets_out.append({
            'planet': pname, 'sym': PLANET_SYM[pname], 'pos': ha.fmt_lon(p['lon']),
            'speed': p['speed'], 'retro': p['speed'] < 0,
            'house': h_of(p['lon']),
            'dignity': ha.dignity(pname, p['lon'])[1],
        })

    return {
        'question': question,
        'time': dt_local.strftime('%d %b %Y %H:%M') + ' ICT',
        'location': f"{lat}°N, {lon_p}°E",
        'house_system': 'whole-sign' if whole_sign else 'Placidus',
        'q1_asc': ha.fmt_lon_full(orig_asc),
        'q2_asc': ha.fmt_lon_full(moon_lon),
        'rotation': round(rotation, 2),
        'asc_deg': round(new_asc_deg, 2),
        'asc_sign': ha.SIGNS[moon_sign],
        'asc_sign_type': st_name,
        'asc_sign_meaning': st_meaning,
        'radical': 3 <= new_asc_deg <= 27,
        'moon': {'pos': ha.fmt_lon(moon_lon), 'sign': ha.SIGNS_SHORT[moon_sign],
                 'sign_idx': moon_sign, 'deg': round(m_deg, 2),
                 'hours_in_sign': round(m_hours_left, 1)},
        'moon_voc': voc_now,
        'moon_voc_blocking': blocking,
        'saturn_house': sat_house,
        'saturn_delay': sat_house in (1, 7),
        'houses': houses_out,
        'planets': planets_out,
        'querent': {'name': 'Moon', 'sym': PLANET_SYM['Moon'],
                    'pos': ha.fmt_lon(moon_lon), 'house': 1,
                    'house_name': 'ASC (Moon)',
                    'dignity': qr_label, 'dignity_pts': qr_dign,
                    'avastha': ha.avastha(qr_label)},
        'quesited': {'name': quesited_name, 'sym': PLANET_SYM[quesited_name],
                     'house': q_house, 'house_name': HOUSE_NAMES[q_house],
                     'keyword': q_kw, 'pos': ha.fmt_lon(qs['lon']),
                     'sig_house': qs_house, 'sig_house_name': HOUSE_NAMES[qs_house],
                     'dignity': qs_label, 'dignity_pts': qs_dign,
                     'avastha': ha.avastha(qs_label)},
        'aspect': [{'sym': a['sym'], 'angle': a['asp'], 'orb': round(a['orb'], 1),
                    'movement': a['movement']} for a in aspects],
        'aspect_timing_hours': round(timing, 1) if timing else None,
        'translation_of_light': translation,
        'collection_of_light': collection,
    }


def _print_report(c):
    print("🔮 HORARY Q2 — Moon-Referenced Chart")
    print(f"   Question: {c['question']}")
    print(f"   {c['time']} | {c['location']}")
    print(f"   Q1 ASC orig: {c['q1_asc']}")
    print(f"   Q2 ASC now:  {c['q2_asc']} ← Moon position")
    print(f"   Rotation: {c['rotation']:.2f}°")
    print()

    print(f"🏠 HOUSES (Moon-referenced, {'Whole Sign' if c['house_system'] == 'whole-sign' else 'Placidus'})")
    for h in c['houses']:
        flag = f" ← {h['flag']}" if h['flag'] else ""
        print(f"  H{h['n']}: {h['sign']} {h['deg']:.2f}°{flag}")
    print()

    print("🪐 PLANETS IN Q2 CHART")
    print(f"  {'':<14} {'Position':<14} {'Spd':>10} {'H':<3} {'Dignity':<12}")
    print(f"  {'─' * 14} {'─' * 14} {'─' * 10} {'─' * 3} {'─' * 12}")
    for p in c['planets']:
        spd_s = f"{p['speed']:+.4f}" + ("R" if p['retro'] else "")
        print(f"  {p['sym'] + p['planet']:<14} {p['pos']:<14} {spd_s:>10} "
              f"{p['house']:<3} {p['dignity']:<12}")
    print()

    print("📋 RADICALITY (Q2 Moon chart)")
    print(f"  ASC (Moon): {c['asc_sign']} {c['asc_deg']:.2f}°")
    print(f"  {'✅ ASC within 3-27° — radical' if c['radical'] else '⚠️ ASC ' + ('<3° early' if c['asc_deg'] < 3 else '>27° late') + ' — not ideal'}")
    print(f"  ASC sign type: {c['asc_sign_type']} — {c['asc_sign_meaning']}")
    if c['moon_voc']:
        print("  Moon VOC: ✅ YES — no applying/exact aspects remain")
    else:
        b = c['moon_voc_blocking']
        print(f"  Moon VOC: ❌ NO — still has {b['movement']} {b['sym']} {b['planet']} (orb={b['orb']:.1f}°)")
    print(f"  Moon in {c['asc_sign']} for ~{c['moon']['hours_in_sign']:.0f}h more")
    sat = "⚠️ delay/deny" if c['saturn_delay'] else "✅"
    print(f"  ♄ Saturn: House {c['saturn_house']}  {sat}")
    print()

    print(f"🔍 KEY: {c['quesited']['house_name']} (House {c['quesited']['house']})")
    q = c['querent']
    s = c['quesited']
    print(f"  🧑 You (Querent): {q['sym']}{q['name']} — the Moon, now ASC")
    print(f"     located @ {q['pos']} in House {q['house']} ({q['house_name']})")
    print(f"     dignity: {q['dignity']} ({q['dignity_pts']:+d}) | avastha: {q['avastha']}")
    print(f"  🎯 Matter (Quesited): {s['sym']}{s['name']} — Ruler of House {s['house']} ({s['house_name']})")
    print(f"     located @ {s['pos']} in House {s['sig_house']} ({s['sig_house_name']})")
    print(f"     dignity: {s['dignity']} ({s['dignity_pts']:+d}) | avastha: {s['avastha']}")
    print()

    print("🔗 ASPECT: Moon (Querent) ↔ Quesited Ruler")
    if c['aspect']:
        for asp in c['aspect']:
            verdict = "✅ YES" if asp['angle'] in (0, 60, 120) else "❌ NO/DELAY"
            print(f"  {q['sym']}{q['name']} {asp['sym']} {s['sym']}{s['name']} "
                  f"(orb {asp['orb']:.1f}°, {asp['movement']})")
            print(f"  → {verdict}")
        if c['aspect_timing_hours']:
            print(f"  → timing: ~{c['aspect_timing_hours']:.0f}h to perfect")
    else:
        print("  No major aspect between significators")
        if c['translation_of_light']:
            print("  ☽ Moon translates light between significators → ✅ possible")
        elif c['collection_of_light']:
            print(f"  ☽ Collection of light via {', '.join(c['collection_of_light'])} → ✅ possible (third-party help)")
        else:
            print("  → Matter uncertain")
    print()

    print("💡 Hint: Interpret the relevant house from THIS rotated chart,")
    print("   not from the original Q1 chart. The question maps to the house")
    print("   matching the topic (weather=4th, partner=7th, work=6th, etc.).")
    print()
    print(f"— hermes_astro v{ha.__version__} "
          f"(moiety orbs [{ha.ORB_SYSTEM}] + {ha.EPHEMERIS_ENGINE}) —")


def main():
    raw_args = sys.argv[1:]
    WHOLE_SIGN = '--placidus' not in raw_args  # default: Tropical Whole Sign
    AS_JSON = '--json' in raw_args
    args = [a for a in raw_args if a not in ('--placidus', '--json')]

    if len(args) >= 4:
        question = args[0]
        dt_local = datetime.strptime(f"{args[1]} {args[2]}", '%Y-%m-%d %H:%M')
        lat = float(args[3])
        lon_p = float(args[4]) if len(args) > 4 else 99.83
    else:
        question = args[0] if args else "Q2 follow-up"
        dt_local = datetime.now(ICT_LOCAL)
        lat, lon_p = 19.91, 99.83

    dt_local = dt_local.replace(tzinfo=ICT_LOCAL)
    c = cast(question, dt_local, lat, lon_p, whole_sign=WHOLE_SIGN)
    if AS_JSON:
        print(json.dumps(c, ensure_ascii=False, indent=2))
    else:
        _print_report(c)
    swe.close()


if __name__ == '__main__':
    main()
