"""
hermes_astro.myhora — Chart calculation via myhora.com (POST, no browser).
==========================================================================
myhora.com/astrology/classical.aspx is an ASP.NET WebForms page: the server
computes the chart on postback (no client-side chart JS). This module GETs
the page, grabs __VIEWSTATE + form fields, POSTs the birth data, and parses
the result HTML (natal / houses / aspects tabs).

Usage (programmatic):
    from hermes_astro.myhora import get_chart, build_report
    chart = get_chart("20.11.2015", "18:18", city="Chiang Rai", tropical=True)
    print(build_report(chart, "20.11.2015", "18:18", "Chiang Rai"))

chart = {
    "meta":    {lat, lon, utc, zodiac, ayanamsa, house_system},
    "natal":   [{body, body_th, sign, sign_th, deg, min, sec, ecliptic_lon, house}],
    "houses":  [{house, name_th, sign, sign_th, deg, min, sec, ecliptic_lon}],
    "aspects": [{body1, aspect, angle, body2, orb}],   # deduped, reciprocal merged
}

CLI wrapper: E:\\Boom Project\\scripts\\myhora_chart.py
"""
import re
import time

import requests
from bs4 import BeautifulSoup

URL = "https://myhora.com/astrology/classical.aspx"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")

# City map: name -> (province_id, amphur_id, lat, lon, utc)
# province_id / amphur_id from myhora's dd_province / dd_amphur (verified via
# the site's own WebForms postback). lat/lon/utc from myhora's own defaults.
CITIES = {
    "chiang rai":   (13, 192, 19.9081, 99.8317, "+07:00"),
    "chiang saen":  (13, 193, 20.2533, 100.0933, "+07:00"),
    "chiang mai":   (14, 210, 18.7883, 98.9853, "+07:00"),
    "bangkok":      (1, 15, 13.7563, 100.5018, "+07:00"),
    "phuket":       (42, 537, 7.8804, 98.3923, "+07:00"),
}

# Thai body name -> English (myhora's own labels; prefix match, longest first)
BODY_TH_EN = {
    "เมอริเดียน": "MC", "ลัคนา": "ASC",
    "อาทิตย": "Sun", "จันทร": "Moon", "พุธ": "Mercury", "ศุกร": "Venus",
    "อังคาร": "Mars", "พฤหัสบดี": "Jupiter", "เสาร์": "Saturn",
    "ยูเรนัส": "Uranus", "เนปจูน": "Neptune", "พลูโต": "Pluto",
    "ราหู": "TrueNode", "เกตุ": "SouthNode", "องคลาภ": "MeanNode",
    "อีริส": "Iris", "ไครอน": "Chiron", "จูโน": "Juno", "เวสต้า": "Vesta",
    "พาลลาส": "Pallas", "เซเรส": "Ceres", "แบล็คมูน": "Lilith",
    "องคลาภ": "MeanNode", "เวอรเทค": "Vertex", "เวอร์เทค": "Vertex",
    "เมษ": "AriesPoint", "พฤษภ": "TaurusPoint", "มิถุน": "GeminiPoint",
    "กรกฎ": "CancerPoint", "สิงห": "LeoPoint", "กันย": "VirgoPoint",
    "ตุล": "LibraPoint", "พิจิก": "ScorpioPoint", "ธนู": "SagittariusPoint",
    "มกร": "CapricornPoint", "กุมภ": "AquariusPoint", "มีน": "PiscesPoint",
}
# longest Thai keys first so prefix matching is unambiguous
_BODY_KEYS = sorted(BODY_TH_EN, key=len, reverse=True)

SIGN_EN = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
           "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
SIGN_TH = {
    "Aries": "เมษ", "Taurus": "พฤษภ", "Gemini": "มิถุน", "Cancer": "กรกฎ",
    "Leo": "สิงห", "Virgo": "กัญ", "Libra": "ตุล", "Scorpio": "พิจิก",
    "Sagittarius": "ธนู", "Capricorn": "มกร", "Aquarius": "กุมภ", "Pisces": "มีน",
}


def sign_of(lon):
    """Ecliptic longitude -> (sign_en, sign_th, deg_in_sign)."""
    lon = lon % 360
    i = int(lon // 30)
    return SIGN_EN[i], SIGN_TH[SIGN_EN[i]], lon - i * 30


def body_en(thai):
    """Thai body label -> English name (keeps '-trop' for tropical axis rows)."""
    trop = "ทถ." in thai
    base = thai.replace("\xa0", " ").replace(" ทถ.", "").strip()
    for th in _BODY_KEYS:
        if base.startswith(th):
            return BODY_TH_EN[th] + ("-trop" if trop else "")
    return base + ("-trop" if trop else "")


def parse_date(s):
    """DD.MM.YYYY -> (d, m, y_ce, y_be)"""
    d, m, y = s.split(".")
    y = int(y)
    return int(d), int(m), y, y + 543


def _request(session, method, url, **kw):
    """GET/POST with retry (myhora is flaky: intermittent SSL timeouts)."""
    last = None
    for i in range(4):
        try:
            r = getattr(session, method)(url, **kw)
            r.raise_for_status()
            return r
        except Exception as e:
            last = e
            time.sleep(2 + 2 * i)
    raise last


def fetch_form(session):
    r = _request(session, "get", URL, headers={"User-Agent": UA}, timeout=30)
    soup = BeautifulSoup(r.text, "html.parser")
    form = soup.find("form")
    data = {}
    for tag in form.find_all("input"):
        n = tag.get("name")
        if not n:
            continue
        t = tag.get("type")
        if t == "radio":
            # only the checked radio is submitted by a browser
            if tag.get("checked"):
                data[n] = tag.get("value") or n
        elif t == "checkbox":
            data[n] = "on" if tag.get("checked") else ""
        else:
            data[n] = tag.get("value") or ""
    return data


def post_chart(session, d, m, y_be, hh, mm, lat, lon, utc,
               name="", tropical=False, house="P",
               transit=None, province=None, amphur=None):
    """POST the birth data and return the raw result HTML."""
    data = fetch_form(session)
    data.update({
        "txt_name": name,
        "dd_day": str(d), "dd_month": str(m), "dd_year": str(y_be),
        "dd_hh": str(hh), "dd_mm": str(mm),
        "dd_natal_date_option": "",
        "txt_lat": f"{lat:.6f}", "txt_lon": f"{lon:.6f}", "txt_utc": utc,
        "txt_lat_th": f"{lat:.6f}", "txt_lon_th": f"{lon:.6f}", "txt_utc_th": utc,
        "dd_house": house,
    })
    if province is not None:
        data["dd_province"] = str(province)
    if amphur is not None:
        data["dd_amphur"] = str(amphur)
    # zodiac radio (empirically verified): rb_sys1 = tropical, rb_sys2 = sidereal
    data["sys"] = "rb_sys1" if tropical else "rb_sys2"
    if transit:
        td, tm, ty_be, _ = parse_date(transit[0])
        data.update({
            "dd_day2": str(td), "dd_month2": str(tm), "dd_year2": str(ty_be),
            "dd_hh2": str(transit[1][0]), "dd_mm2": str(transit[1][1]),
            "dd_transit_date_option": "",
            "txt_lat2": f"{lat:.6f}", "txt_lon2": f"{lon:.6f}", "txt_utc2": utc,
            "txt_lat_th2": f"{lat:.6f}", "txt_lon_th2": f"{lon:.6f}", "txt_utc_th2": utc,
        })
    data = {k: v for k, v in data.items() if v != ""}
    r = _request(session, "post", URL, data=data,
                 headers={"User-Agent": UA, "Referer": URL}, timeout=60)
    return r.text


def _parse_pos(text):
    """'17°d54'07'' -> (deg, min, sec)"""
    m = re.match(r"(\d+)°\s*(?:[a-zA-Z0-9])\s*(\d+)'(\d+)'", text)
    if not m:
        return None
    return int(m.group(1)), int(m.group(2)), int(m.group(3))


def parse_postback(html):
    """Parse myhora's result HTML -> {meta, natal, houses, aspects}."""
    soup = BeautifulSoup(html, "html.parser")
    out = {"meta": {}, "natal": [], "houses": [], "aspects": []}

    # meta from header
    hdr = soup.find(id="p_result")
    if hdr:
        hdr_txt = hdr.get_text(" ", strip=True)
        m = re.search(r"ละติจูด (\d+)°N(\d+)'(\d+)'' ลองจิจูด (\d+)°E(\d+)'(\d+)''", hdr_txt)
        if m:
            out["meta"]["lat"] = int(m.group(1)) + int(m.group(2)) / 60 + int(m.group(3)) / 3600
            out["meta"]["lon"] = int(m.group(4)) + int(m.group(5)) / 60 + int(m.group(6)) / 3600
        m = re.search(r"\(UTC([+-]\d+):(\d+)\)", hdr_txt)
        if m:
            out["meta"]["utc"] = f"{m.group(1)}:{m.group(2)}"
        m = re.search(r"(Sidereal|Tropical)\s*(?:\(([^)]*)\))?", hdr_txt)
        if m:
            out["meta"]["zodiac"] = m.group(1)
            if m.group(2):
                out["meta"]["ayanamsa"] = m.group(2)
        m = re.search(r"เรือนชะตา (\S+)", hdr_txt)
        if m:
            out["meta"]["house_system"] = m.group(1)

    # natal tab
    tab = soup.find(id="ttbh0_tab")
    if tab:
        for row in tab.select("div.pz0"):
            cells = row.select("div.pz2, div.pz3, div.pz4, div.pz5")
            if len(cells) < 4:
                continue
            body_th = cells[0].get_text(strip=True)
            pos = _parse_pos(cells[1].get_text(" ", strip=True))
            lon_txt = cells[2].get_text(strip=True).rstrip("°")
            house = cells[3].get_text(strip=True)
            if not lon_txt:
                continue
            lon = float(lon_txt)
            sign, sign_th, _ = sign_of(lon)
            out["natal"].append({
                "body": body_en(body_th),
                "body_th": body_th,
                "sign": sign, "sign_th": sign_th,
                "deg": pos[0] if pos else None,
                "min": pos[1] if pos else None,
                "sec": pos[2] if pos else None,
                "ecliptic_lon": lon,
                "house": int(house) if house.isdigit() else None,
            })

    # houses tab
    tab = soup.find(id="ttbh1_tab")
    if tab:
        for row in tab.select("div.hz0"):
            cells = row.select("div.hz1, div.hz2, div.hz4")
            if len(cells) < 3:
                continue
            m = re.match(r"(\d+)\s+(\S+)", cells[0].get_text(strip=True))
            if not m:
                continue
            h = int(m.group(1))
            pos = _parse_pos(cells[1].get_text(" ", strip=True))
            lon_txt = cells[2].get_text(strip=True).rstrip("°")
            if not lon_txt:
                continue
            lon = float(lon_txt)
            sign, sign_th, _ = sign_of(lon)
            out["houses"].append({
                "house": h, "name_th": m.group(2),
                "sign": sign, "sign_th": sign_th,
                "deg": pos[0] if pos else None,
                "min": pos[1] if pos else None,
                "sec": pos[2] if pos else None,
                "ecliptic_lon": lon,
            })

    # aspects tab
    tab = soup.find(id="ttbh2_tab")
    if tab:
        for row in tab.select("div.az0"):
            title = row.get("title", "")
            m = re.match(r"(\S+)\s+(\S+) \((\d+)°\)\s+(.+?)\s+Orb:\s+(-?[\d.]+)°", title)
            if not m:
                continue
            b1, aspect, angle, b2, orb = m.groups()
            out["aspects"].append({
                "body1": body_en(b1),
                "aspect": aspect,
                "angle": int(angle),
                "body2": body_en(b2),
                "orb": float(orb),
            })

    # dedupe reciprocal pairs (myhora lists A->B and B->A)
    seen = set()
    deduped = []
    for a in out["aspects"]:
        key = (frozenset((a["body1"], a["body2"])), a["aspect"], a["angle"])
        if key in seen:
            continue
        seen.add(key)
        deduped.append(a)
    out["aspects"] = deduped
    return out


def get_chart(date, time_hhmm, city=None, lat=None, lon=None, utc="+07:00",
              name="", tropical=False, house="P", transit=None):
    """High-level: fetch + parse a chart in one call.

    date: "DD.MM.YYYY"; time_hhmm: "HH:MM" (local).
    city: name from CITIES (default "chiang rai"), or pass lat/lon/utc.
    Returns the parsed chart dict (see module docstring).
    """
    if lat is not None and lon is not None:
        province = amphur = None
    else:
        key = (city or "chiang rai").lower()
        if key not in CITIES:
            raise ValueError(f"Unknown city {city!r}. Known: {', '.join(CITIES)}")
        province, amphur, lat, lon, utc = CITIES[key]

    d, m, y_ce, y_be = parse_date(date)
    hh, mm = [int(x) for x in time_hhmm.split(":")]

    session = requests.Session()
    html = post_chart(session, d, m, y_be, hh, mm, lat, lon, utc,
                      name=name, tropical=tropical, house=house,
                      transit=transit, province=province, amphur=amphur)
    res = parse_postback(html)
    if not res["natal"]:
        raise RuntimeError("No natal data parsed — myhora page layout may have changed.")
    return res


def fmt_pos(p):
    return f"{p['sign']} {p['deg']}°{p['min']:02d}'{p['sec']:02d}''"


def build_report(res, date, time_hhmm, label, lat, lon, utc):
    """Markdown report: 4 tables (Natal, House cusps, Major, Minor aspects)."""
    L = []
    meta = res["meta"]
    zodiac = meta.get('zodiac', '?')
    L.append(f"# myhora.com chart — {date} {time_hhmm} {label}")
    L.append("")
    L.append(f"UTC {utc} | {meta.get('house_system','?')} | {zodiac} {meta.get('ayanamsa','')}")
    L.append(f"Lat {meta.get('lat','?')}°N Lon {meta.get('lon','?')}°E")
    L.append("")
    L.append(f"## Natal ({zodiac.lower()})")
    L.append("")
    L.append("| Body | Sign | Position | Ecliptic | House |")
    L.append("|---|---|---|---|---|")
    for p in res["natal"]:
        L.append(f"| {p['body']} | {p['sign_th']} {p['sign']} | {fmt_pos(p)} | {p['ecliptic_lon']:.2f}° | {p['house']} |")
    L.append("")
    L.append("## House cusps")
    L.append("")
    L.append("| # | Sign | Position | Ecliptic |")
    L.append("|---|---|---|---|")
    for h in res["houses"]:
        L.append(f"| {h['house']} | {h['sign_th']} {h['sign']} | {fmt_pos(h)} | {h['ecliptic_lon']:.2f}° |")
    L.append("")

    MAJOR = {0, 60, 90, 120, 180}
    major = sorted((a for a in res["aspects"] if a["angle"] in MAJOR), key=lambda a: abs(a["orb"]))
    minor = sorted((a for a in res["aspects"] if a["angle"] not in MAJOR), key=lambda a: abs(a["orb"]))
    for title, rows in (("## Major aspects", major), ("## Minor aspects", minor)):
        L.append(f"{title} ({len(rows)})")
        L.append("")
        L.append("| Body1 | Aspect | Body2 | Orb |")
        L.append("|---|---|---|---|")
        for a in rows:
            L.append(f"| {a['body1']} | {a['aspect']} ({a['angle']}°) | {a['body2']} | {a['orb']:+.2f} |")
        L.append("")
    return "\n".join(L)
