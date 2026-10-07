"""GT regression: hermes_astro must reproduce the Boom reference transit charts.

The three charts below are the Boom Project ground truth, fitted to the
orb table in stellium/src/stellium/engines/orbs.py :: BOOM_FULL_ORBS and
verified against AstroGold. They are transits, so they include
Uranus / Neptune / Pluto — the bodies whose positions the Hub previously
could not fetch at all.

A regression here means a missing or extra aspect in any of the three sets,
which is the exact failure mode the flatlib orb table used to produce
(20 of 80 GT aspects wrong, all false positives).
"""
import pytest

import hermes_astro as ha
from datetime import datetime

GT = [
    ("2026-09-09 17:02", {
        ("Sun", "Mars", "Sextile"), ("Moon", "Venus", "Sextile"),
        ("Moon", "Jupiter", "Conjunction"), ("Mercury", "Neptune", "Opposition"),
        ("Mercury", "Pluto", "Trine"), ("Venus", "Pluto", "Square"),
        ("Mars", "Saturn", "Square"), ("Jupiter", "Saturn", "Trine"),
        ("Uranus", "Neptune", "Sextile"), ("Uranus", "Pluto", "Trine"),
        ("Neptune", "Pluto", "Sextile")}),
    ("2026-10-20 20:48", {
        ("Sun", "Moon", "Trine"), ("Sun", "Venus", "Conjunction"),
        ("Sun", "Jupiter", "Sextile"), ("Sun", "Pluto", "Square"),
        ("Moon", "Mercury", "Square"), ("Moon", "Mars", "Opposition"),
        ("Moon", "Jupiter", "Opposition"), ("Mercury", "Jupiter", "Square"),
        ("Venus", "Pluto", "Square"), ("Mars", "Saturn", "Trine"),
        ("Uranus", "Neptune", "Sextile"), ("Uranus", "Pluto", "Trine"),
        ("Neptune", "Pluto", "Sextile")}),
    ("2026-10-14 06:04", {
        ("Sun", "Jupiter", "Sextile"), ("Moon", "Jupiter", "Square"),
        ("Moon", "Uranus", "Opposition"), ("Moon", "Neptune", "Trine"),
        ("Moon", "Pluto", "Sextile"), ("Mercury", "Mars", "Square"),
        ("Mercury", "Jupiter", "Square"), ("Venus", "Mars", "Square"),
        ("Venus", "Pluto", "Square"), ("Mars", "Saturn", "Trine"),
        ("Mars", "Uranus", "Sextile"), ("Mars", "Neptune", "Trine"),
        ("Mars", "Pluto", "Opposition"), ("Uranus", "Neptune", "Sextile"),
        ("Uranus", "Pluto", "Trine"), ("Neptune", "Pluto", "Sextile")}),
]

# hermes_astro's own short aspect names -> the GT's canonical names.
_CANON = {"conj": "Conjunction", "sext": "Sextile", "sq": "Square",
          "square": "Square", "trine": "Trine", "opp": "Opposition"}

_BODIES = ha.TRAD7 + ha.OUTER3


def _aspect_set(label):
    dt = datetime.strptime(label, "%Y-%m-%d %H:%M").replace(tzinfo=ha.ICT)
    pos = ha.all_positions(ha.jd_utc(dt), _BODIES)
    names = list(pos)
    out = set()
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            for r in ha.check_aspect(pos[a]["lon"], a, pos[b]["lon"], b):
                if r["in_orb_active"]:
                    out.add((a, b, _CANON[r["name"]]))
    return out


def test_orb_table_matches_boom_reference():
    """The active orb table must equal the fitted Boom reference."""
    assert ha.ORB_SYSTEM == "boom", "default orb system must be 'boom'"
    for body, value in ha.BOOM_FULL_ORBS.items():
        assert ha.ALL_ORBS[body] == value, body


def test_orb_allowance_is_the_means():
    """Moiety semantics: the effective orb is the mean of both full orbs."""
    assert ha.orb_allowance("Sun", "Venus") == (10.0 + 6.0) / 2
    assert ha.orb_allowance("Jupiter", "Saturn") == (8.0 + 5.0) / 2
    assert ha.orb_allowance("Mars", "Neptune") == (7.0 + 7.0) / 2


def test_outer_planet_positions_available():
    """all_positions() must reach Uranus / Neptune / Pluto, not raise."""
    dt = datetime(2026, 10, 14, 6, 4, tzinfo=ha.ICT)
    pos = ha.all_positions(ha.jd_utc(dt), _BODIES)
    for body in ("Uranus", "Neptune", "Pluto"):
        assert body in pos, body
        assert 0.0 <= pos[body]["lon"] < 360.0, body


def test_unknown_body_raises_informative_error():
    dt = datetime(2026, 10, 14, 6, 4, tzinfo=ha.ICT)
    with pytest.raises(KeyError, match="unknown body"):
        ha.all_positions(ha.jd_utc(dt), ["NotAPlanet"])


def test_flatlib_system_still_selectable():
    """VOC / horary keep their documented flatlib basis on request."""
    try:
        ha.set_orb_system("flatlib")
        assert ha.ALL_ORBS["Saturn"] == 9
        assert ha.ALL_ORBS["Jupiter"] == 9
        assert ha.orb_allowance("Sun", "Venus") == (15 + 7) / 2
    finally:
        ha.set_orb_system("boom")
    assert ha.ALL_ORBS["Saturn"] == 5.0


def test_unknown_orb_system_rejected():
    with pytest.raises(ValueError, match="unknown orb system"):
        ha.set_orb_system("nope")


@pytest.mark.parametrize("label,expected", GT, ids=[g[0] for g in GT])
def test_gt_transit_chart_exact(label, expected):
    """The GT aspect set must be reproduced EXACTLY: no missing, no extra."""
    got = _aspect_set(label)
    expected = set(expected)
    assert not (expected - got), f"{label}: MISSING {sorted(expected - got)}"
    assert not (got - expected), f"{label}: EXTRA {sorted(got - expected)}"
    assert len(got) == len(expected), (
        f"{label}: count {len(got)} != {len(expected)}")