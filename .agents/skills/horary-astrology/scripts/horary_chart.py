#!/usr/bin/env python3
"""
Horary chart cast — uses shared hermes_astro calculation layer.
Usage: python horary_chart.py "<question>" <YYYY-MM-DD> <HH:MM> <lat> <lon> [--placidus] [--json]
       (ICT time, defaults to now and Chiang Rai 19.91/99.83)
Options:
  --placidus     Use Placidus houses (default: Tropical Whole Sign, H1 = ASC sign)
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


def _house_of(lon, cusps, asc_sign, whole_sign):
    if whole_sign:
        return (ha.sign_index(lon) - asc_sign) % 12 + 1
    return ha.house_of(lon, cusps)


def cast(question, dt_local, lat, lon_p, whole_sign=False):
    """Compute the full horary chart as a dict (text + JSON share this)."""
    jd = ha.jd_utc(dt_local)
    pos = ha.all_positions(jd, ha.TRAD7)
    cusps, asc_lon, mc_lon = ha.houses(jd, lat, lon_p)
    asc_sign = ha.sign_index(asc_lon)

    def h_of(lon):
        return _house_of(lon, cusps, asc_sign, whole_sign)

    # ── Radicality ──
    asc_deg = asc_lon % 30
    st_name, st_meaning = ha.sign_type(asc_sign)
    m = pos['Moon']
    m_sign = ha.sign_index(m['lon'])
    m_deg = m['lon'] % 30
    m_hours_left = (30 - m_deg) / m['speed'] * 24 if m['speed'] > 0 else 999
    voc_now, blocking = ha.moon_voc_status(jd, pos)
    sat_house = h_of(pos['Saturn']['lon'])

    # ── Significators ──
    querent_name = ha.ruler_of(asc_sign)
    qr = pos[querent_name]
    qr_house = h_of(qr['lon'])
    qr_dign, qr_label = ha.dignity(querent_name, qr['lon'])

    q_house, q_kw = ha.quesited_house(question)
    if whole_sign:
        qs_cusp_sign = (asc_sign + q_house - 1) % 12
    else:
        qs_cusp_sign = ha.sign_index(cusps[q_house - 1])
    quesited_name = ha.ruler_of(qs_cusp_sign)
    qs = pos[quesited_name]
    qs_house = h_of(qs['lon'])
    qs_dign, qs_label = ha.dignity(quesited_name, qs['lon'])

    # ── Aspect between significators ──
    aspects = ha.check_aspect_with_speed(
        qr['lon'], querent_name, qr['speed'], qs['lon'], quesited_name, qs['speed'])
    timing = None
    if aspects:
        for asp in aspects:
            if asp['movement'] in ('applicative', 'exact') and asp['orb'] > 0:
                rel = abs(qr['speed'] - qs['speed'])
                if rel > 0.01:
                    timing = asp['orb'] / rel * 24
    # Fallback: translation / collection of light
    translation = None
    collection = []
    if not aspects:
        translation = ha.translation_of_light(jd, pos, querent_name, quesited_name)
        collection = ha.collection_of_light(jd, pos, querent_name, quesited_name)

    # ── Moon path (next 72h) ──
    moon_path = ha.moon_aspect_times(jd, pos, 72)
    moon_path_out = []
    for th, A, pname in moon_path:
        tdt = dt_local + timedelta(hours=th)
        m_at, _ = swe.calc_ut(jd + th / 24, swe.MOON, ha.FLAGS)
        moon_path_out.append({
            'planet': pname, 'aspect': A, 'sym': ha.ASPECT_SYMS[A],
            'hours': round(th, 1), 'when': tdt.strftime('%d %b %H:%M ICT'),
            'moon': f"{ha.SIGNS_SHORT[ha.sign_index(m_at[0])]} {m_at[0] % 30:.1f}°",
        })

    # ── Houses list ──
    houses_out = []
    for i in range(12):
        if whole_sign:
            si = (asc_sign + i) % 12
            houses_out.append({'n': i + 1, 'sign': ha.SIGNS[si], 'deg': 0.0,
                               'flag': 'ASC' if i == 0 else None})
        else:
            d = cusps[i]
            si = ha.sign_index(d)
            houses_out.append({'n': i + 1, 'sign': ha.SIGNS_SHORT[si],
                               'deg': round(d - si * 30, 1),
                               'flag': 'ASC' if i == 0 else ('MC' if i == 9 else None)})

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
        'ascendant': ha.fmt_lon_full(asc_lon),
        'asc_sign': ha.SIGNS[asc_sign],
        'asc_deg': round(asc_deg, 2),
        'asc_sign_type': st_name,
        'asc_sign_meaning': st_meaning,
        'radical': 3 <= asc_deg <= 27,
        'moon': {'pos': ha.fmt_lon(m['lon']), 'sign': ha.SIGNS_SHORT[m_sign],
                 'sign_idx': m_sign, 'deg': round(m_deg, 2),
                 'hours_in_sign': round(m_hours_left, 1)},
        'moon_voc': voc_now,
        'moon_voc_blocking': blocking,
        'saturn_house': sat_house,
        'saturn_delay': sat_house in (1, 7),
        'houses': houses_out,
        'planets': planets_out,
        'querent': {'name': querent_name, 'sym': PLANET_SYM[querent_name],
                    'pos': ha.fmt_lon(qr['lon']), 'house': qr_house,
                    'house_name': HOUSE_NAMES[qr_house],
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
        'moon_path': moon_path_out,
    }


def _print_report(c):
    print(f"🔮 HORARY CHART")
    print(f"   Question: {c['question']}")
    print(f"   {c['time']} | {c['location']}")
    print()

    print(f"🏠 HOUSES ({'Whole Sign' if c['house_system'] == 'whole-sign' else 'Placidus'})")
    for h in c['houses']:
        flag = f" ← {h['flag']}" if h['flag'] else ""
        print(f"  {h['n']}: {h['sign']} ({h['deg']:.1f}°){flag}")
    print()

    print("🪐 PLANETS")
    print(f"  {'':<14} {'Position':<14} {'Spd':>10} {'H':<3} {'Dignity':<12}")
    print(f"  {'─' * 14} {'─' * 14} {'─' * 10} {'─' * 3} {'─' * 12}")
    for p in c['planets']:
        spd_s = f"{p['speed']:+.4f}" + ("R" if p['retro'] else "")
        print(f"  {p['sym'] + p['planet']:<14} {p['pos']:<14} {spd_s:>10} "
              f"{p['house']:<3} {p['dignity']:<12}")
    print()

    print("📋 RADICALITY CHECK")
    a = c
    early = "⚠️ EARLY" if a['asc_deg'] < 3 else ""
    late = "⚠️ LATE" if a['asc_deg'] > 27 else ""
    print(f"  ASC: {a['ascendant']}  {early}{late}")
    print(f"  ASC deg: {a['asc_deg']:.1f}° {'✅ within range' if a['radical'] else '⚠️ out of range'}")
    print(f"  ASC sign type: {a['asc_sign_type']} — {a['asc_sign_meaning']}")
    print(f"  Moon: {a['moon']['sign']} {a['moon']['deg']:.2f}° | {a['moon']['hours_in_sign']:.1f}h left in sign")
    if a['moon_voc']:
        print("  Moon VOC: ✅ YES — no applying/exact aspects remain")
    else:
        b = a['moon_voc_blocking']
        print(f"  Moon VOC: ❌ NO — still has {b['movement']} {b['sym']} {b['planet']} (orb={b['orb']:.1f}°)")
    sat = "⚠️ delay/deny" if a['saturn_delay'] else "✅"
    print(f"  ♄ Saturn: House {a['saturn_house']}  {sat}")
    print()

    print("📌 SIGNIFICATORS")
    q = c['querent']
    print(f"  🧑 You (Querent): {q['sym']}{q['name']} — Ruler of House 1 ({a['asc_sign']})")
    print(f"     located @ {q['pos']} in House {q['house']} ({q['house_name']})")
    print(f"     dignity: {q['dignity']} ({q['dignity_pts']:+d}) | avastha: {q['avastha']}")
    s = c['quesited']
    print(f"  🎯 Matter (Quesited): {s['sym']}{s['name']} — Ruler of House {s['house']} ({s['house_name']})")
    print(f"     located @ {s['pos']} in House {s['sig_house']} ({s['sig_house_name']})")
    print(f"     dignity: {s['dignity']} ({s['dignity_pts']:+d}) | avastha: {s['avastha']}")
    print()

    print("🔗 ASPECT: Querent ↔ Quesited")
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
            print(f"  ☽ Moon translates light between significators → ✅ possible")
        elif c['collection_of_light']:
            print(f"  ☽ Collection of light via {', '.join(c['collection_of_light'])} → ✅ possible (third-party help)")
        else:
            print("  → Matter uncertain")
    print()

    print("☽ MOON PATH")
    next_sign = (a['moon']['sign_idx'] + 1) % 12
    print(f"  Now: {a['moon']['sign']} {a['moon']['deg']:.2f}° | → {ha.SIGNS[next_sign]} in {a['moon']['hours_in_sign']:.0f}h")
    for mp in c['moon_path']:
        print(f"  → {mp['sym']} {mp['planet']} in {mp['hours']:.1f}h ({mp['when']}, Moon {mp['moon']})")
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
        question = args[0] if args else "Test question"
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
