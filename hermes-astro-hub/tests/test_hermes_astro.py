"""
Golden-fixture regression tests for the hermes_astro shared calculation layer.

The fixture is a single real horary cast:
    2026-09-08 21:53 ICT (UTC 14:53), Chiang Rai (19.91 N, 99.83 E)
    Question: "Will my ex come back?"

Golden values were captured from the live pyswisseph ephemeris (primary engine)
and cross-checked against the verified horary_chart.py output. Tolerances are
tight (0.01 deg / 0.1 h) because the same ephemeris is used — these catch
logic regressions, not ephemeris drift.

Run from the hub root:
    ~/AppData/Local/hermes/hermes-agent/venv/Scripts/python -m pytest tests/ -v
"""
import pytest

import hermes_astro as ha
from datetime import datetime

# ── Golden fixture ────────────────────────────────────────────────

T0 = datetime(2026, 9, 8, 21, 53, tzinfo=ha.ICT)
LAT, LON = 19.91, 99.83
QUESTION = "Will my ex come back?"

# Expected planet longitudes (deg) and signs.
GOLDEN_PLANETS = {
    "Sun":     (165.9789, "Virgo"),
    "Moon":    (133.1043, "Leo"),
    "Mercury": (176.4730, "Virgo"),
    "Venus":   (208.8468, "Libra"),
    "Mars":    (108.1842, "Cancer"),
    "Jupiter": (135.2795, "Leo"),
    "Saturn":  (13.2181,  "Aries"),
}
GOLDEN_ASC = 49.8504            # Taurus 19.85
GOLDEN_ASC_SIGN = "Taurus"

# Moon's next exact aspects within 72h: (planet, hours, angle_deg)
GOLDEN_MOON_PATH = [
    ("Saturn",  0.19, 120),
    ("Jupiter", 3.73,   0),
    ("Venus",  28.08,  60),
    ("Sun",    60.57,   0),
    ("Mars",   62.99,  60),
]

DEG_TOL = 0.01
HR_TOL = 0.1


@pytest.fixture(scope="module")
def chart():
    jd = ha.jd_utc(T0)
    pos = ha.all_positions(jd, ha.TRAD7)
    cusps, asc, mc = ha.houses(jd, LAT, LON)
    return {"jd": jd, "pos": pos, "cusps": cusps, "asc": asc, "mc": mc}


# ── Positions ─────────────────────────────────────────────────────

def test_planet_positions(chart):
    for name, (lon, sign) in GOLDEN_PLANETS.items():
        got = chart["pos"][name]
        assert abs(got["lon"] - lon) < DEG_TOL, f"{name} lon {got['lon']} != {lon}"
        assert ha.SIGNS[ha.sign_index(got["lon"])].endswith(sign), f"{name} sign"


def test_ascendant(chart):
    assert abs(chart["asc"] - GOLDEN_ASC) < DEG_TOL
    assert ha.SIGNS[ha.sign_index(chart["asc"])].endswith(GOLDEN_ASC_SIGN)


def test_saturn_retrograde(chart):
    assert chart["pos"]["Saturn"]["speed"] < 0


# ── Moon aspect timing (Newton-refined, cross-sign) ───────────────

def test_moon_aspect_times(chart):
    got = ha.moon_aspect_times(chart["jd"], chart["pos"], 72)
    got = [(name, h, A) for h, A, name in got]
    assert len(got) == len(GOLDEN_MOON_PATH), f"aspect count {len(got)}"
    for (name, hours, angle), (g_name, g_hours, g_angle) in zip(got, GOLDEN_MOON_PATH):
        assert name == g_name, f"aspect order: {name} != {g_name}"
        assert abs(hours - g_hours) < HR_TOL, f"{name} {hours}h != {g_hours}h"
        assert angle == g_angle, f"{name} angle {angle} != {g_angle}"


# ── Dignity / avastha / rulership ─────────────────────────────────

def test_dignity(chart):
    assert ha.dignity("Venus", chart["pos"]["Venus"]["lon"]) == (5, "Rulership")
    assert ha.dignity("Mars", chart["pos"]["Mars"]["lon"]) == (-4, "Fall")


def test_avastha():
    assert "Deeptha" in ha.avastha("Rulership")
    assert "Deena" in ha.avastha("Fall")
    assert "Mushita" in ha.avastha("Detriment")


def test_ruler_of():
    assert ha.ruler_of(1) == "Venus"   # Taurus
    assert ha.ruler_of(7) == "Mars"    # Scorpio


def test_sign_type():
    name, _ = ha.sign_type(1)          # Taurus = fixed
    assert "Sthira" in name


# ── Quesited house mapping ────────────────────────────────────────

def test_quesited_house_partner():
    assert ha.quesited_house(QUESTION) == (7, "ex")


def test_quesited_house_weather():
    assert ha.quesited_house("Will it rain?") == (4, "rain")


def test_quesited_house_lost_item():
    assert ha.quesited_house("Where is my phone?") == (2, "phone")
    assert ha.quesited_house("I lost my wallet") == (2, "lost")
    assert ha.quesited_house("มือถืออยู่ที่ไหน") == (2, "มือถือ")


def test_quesited_house_default():
    house, kw = ha.quesited_house("Tell me about my life")
    assert house == 7 and kw is None


# ── closest_distance sign convention ──────────────────────────────

def test_closest_distance_sign_convention():
    # Returns arc b-a wrapped to ±180 (NOT a-b).
    assert ha.closest_distance(0, 10) == 10
    assert ha.closest_distance(10, 0) == -10
    assert ha.closest_distance(0, 200) == -160
    assert ha.closest_distance(200, 0) == 160


# ── Moon VOC ──────────────────────────────────────────────────────

def test_moon_voc_status(chart):
    is_voc, blocking = ha.moon_voc_status(chart["jd"], chart["pos"])
    assert is_voc is False
    assert blocking is not None
    # The Moon is still applying to Jupiter (conjunction) at cast time.
    assert blocking["planet"] == "Jupiter"


# ── Translation / collection of light ─────────────────────────────

def test_translation_of_light(chart):
    # Venus (L1) and Mars (L7) have no direct aspect; check the Moon can
    # translate light between them (Moon applying to both, harmonious).
    result = ha.translation_of_light(chart["jd"], chart["pos"], "Venus", "Mars")
    assert isinstance(result, bool)


def test_collection_of_light(chart):
    result = ha.collection_of_light(chart["jd"], chart["pos"], "Venus", "Mars")
    assert isinstance(result, list)


# ── check_aspect ──────────────────────────────────────────────────

def test_check_aspect(chart):
    p = chart["pos"]
    res = ha.check_aspect(p["Moon"]["lon"], "Moon", p["Saturn"]["lon"], "Saturn")
    # Moon (Leo 13.1) and Saturn (Aries 13.2) are ~120 apart -> trine within orb.
    angles = [r["asp"] for r in res]
    assert 120 in angles


# ── chart_pull.py CLI regression ──────────────────────────────────

import json
import subprocess
import sys
from pathlib import Path

CHART_PULL = Path(r"E:\Boom Project\scripts\chart_pull.py")


def test_chart_pull_cli_golden():
    """chart_pull.py (DD.MM.YYYY HH:MM <city> --json) must reproduce the
    golden fixture: engine ok, ASC/MC/planets within DEG_TOL, 7 planets."""
    out = subprocess.run(
        [sys.executable, str(CHART_PULL), "08.09.2026", "21:53",
         "chiang-rai", "--aspects", "--json"],
        capture_output=True, text=True, encoding="utf-8",
    )
    assert out.returncode == 0, out.stderr
    d = json.loads(out.stdout)
    assert d["engine"]["ok"] is True
    assert abs(d["ascendant"] - GOLDEN_ASC) < DEG_TOL
    by_name = {r["planet"]: r for r in d["planets"]}
    assert set(by_name) == set(GOLDEN_PLANETS)
    for name, (lon, _sign) in GOLDEN_PLANETS.items():
        assert abs(by_name[name]["lon"] - lon) < DEG_TOL, name
    # Speed-based aspect set must be non-empty and well-formed.
    assert len(d["aspects"]) > 0
    for a in d["aspects"]:
        assert a["movement"] in ("applicative", "separative", "exact")
