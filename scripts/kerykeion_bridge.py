#!/usr/bin/env python3
"""
kerykeion_bridge.py — Local kerykeion wrapper for Boom Project

Replaces any need for external astrology APIs (e.g., AstrologerAPI) by using
the kerykeion library directly within the project venv.

Key design:
- All calculations are LOCAL (no external API calls)
- Location/timezone resolved explicitly (no geonames dependency)
- Returns data in the same shape as scripts/natal_chart.py for compatibility
- Supports: natal chart, synastry, transits, composite, moon phase

Usage:
  from kerykeion_bridge import calculate_natal, calculate_synastry
  chart = calculate_natal(name="Boom", year=1996, month=11, day=20, hour=20, minute=37, lat=19.9071, lon=99.8328, tz_str="Asia/Bangkok")
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass

from kerykeion import (
    AstrologicalSubject,
    SynastryAspects,
    NatalAspects,
    ReportGenerator,
    KerykeionChartSVG,
    CompositeSubjectFactory,
    MoonPhaseDetailsFactory,
    MoonPhaseOverviewModel,
    PlanetaryReturnFactory,
)

# ---------------------------------------------------------------------------
# Location resolver (local — no geonames API calls)
# ---------------------------------------------------------------------------

LOCATION_COORDS: Dict[str, Tuple[float, float, str]] = {
    "chiang rai": (19.9071, 99.8328, "Asia/Bangkok"),
    "chiang rai, thailand": (19.9071, 99.8328, "Asia/Bangkok"),
    "bangkok": (13.7563, 100.5018, "Asia/Bangkok"),
    "bangkok, thailand": (13.7563, 100.5018, "Asia/Bangkok"),
}

def resolve_location(location_str: str) -> Tuple[float, float, str]:
    """Resolve location string to (lat, lon, tz_str) locally."""
    key = location_str.lower().strip()
    if key in LOCATION_COORDS:
        return LOCATION_COORDS[key]
    raise ValueError(
        f"Unknown location '{location_str}'. Add it to LOCATION_COORDS in kerykeion_bridge.py."
    )


# ---------------------------------------------------------------------------
# Core wrapper functions
# ---------------------------------------------------------------------------

@dataclass
class ChartData:
    """Unified chart data container compatible with project pipeline."""
    name: str
    birth_date: str
    birth_time: str
    tz_str: str
    lat: float
    lon: float
    sun: Dict[str, Any]
    moon: Dict[str, Any]
    mercury: Dict[str, Any]
    venus: Dict[str, Any]
    mars: Dict[str, Any]
    jupiter: Dict[str, Any]
    saturn: Dict[str, Any]
    uranus: Dict[str, Any]
    neptune: Dict[str, Any]
    pluto: Dict[str, Any]
    north_node: Dict[str, Any]
    south_node: Dict[str, Any]
    ascendant: Dict[str, Any]
    mc: Dict[str, Any]
    houses: List[Dict[str, Any]]
    aspects: List[Dict[str, Any]]
    raw_subject: Any  # underlying kerykeion AstrologicalSubject


def _kr_point_to_dict(point) -> Dict[str, Any]:
    """Convert a kerykeion planet/house point to our standard dict."""
    return {
        "name": point.name,
        "sign": point.sign,
        "sign_num": point.sign_num,
        "position": round(point.position, 2),
        "degree": round(point.position % 30, 2),
        "house": getattr(point, "house", None),
        "retrograde": getattr(point, "retrograde", False),
        "element": getattr(point, "element", None),
        "quality": getattr(point, "quality", None),
    }


def calculate_natal(
    name: str,
    year: int,
    month: int,
    day: int,
    hour: int,
    minute: int,
    lat: float,
    lon: float,
    tz_str: str,
    city: Optional[str] = None,
    nation: Optional[str] = None,
    houses_system_identifier: str = "P",
) -> ChartData:
    """
    Calculate a natal chart using kerykeion (fully local).

    Args:
        house_system: "P"=Placidus, "K"=Koch, "W"=Whole Sign, "E"=Equal, etc.
    """
    subject = AstrologicalSubject(
        name=name,
        year=year,
        month=month,
        day=day,
        hour=hour,
        minute=minute,
        lat=lat,
        lng=lon,
        tz_str=tz_str,
        city=city,
        nation=nation,
        houses_system_identifier=houses_system_identifier,
    )

    # Extract houses
    houses = []
    for i in range(1, 13):
        h = getattr(subject, f"house_{i}", None)
        if h:
            houses.append(_kr_point_to_dict(h))

    # Extract aspects via NatalAspects
    natal_aspects = NatalAspects(subject)
    aspects = []
    for asp in natal_aspects.relevant_aspects:
        aspects.append({
            "planet1": asp.p1_name,
            "planet2": asp.p2_name,
            "aspect": asp.aspect,
            "orbit": round(asp.orbit, 2),
            "aspect_degrees": asp.aspect_degrees,
        })

    return ChartData(
        name=name,
        birth_date=f"{year:04d}-{month:02d}-{day:02d}",
        birth_time=f"{hour:02d}:{minute:02d}",
        tz_str=tz_str,
        lat=lat,
        lon=lon,
        sun=_kr_point_to_dict(subject.sun),
        moon=_kr_point_to_dict(subject.moon),
        mercury=_kr_point_to_dict(subject.mercury),
        venus=_kr_point_to_dict(subject.venus),
        mars=_kr_point_to_dict(subject.mars),
        jupiter=_kr_point_to_dict(subject.jupiter),
        saturn=_kr_point_to_dict(subject.saturn),
        uranus=_kr_point_to_dict(subject.uranus),
        neptune=_kr_point_to_dict(subject.neptune),
        pluto=_kr_point_to_dict(subject.pluto),
        north_node=_kr_point_to_dict(subject.true_north_lunar_node),
        south_node=_kr_point_to_dict(subject.true_south_lunar_node),
        ascendant=_kr_point_to_dict(subject.ascendant),
        mc=_kr_point_to_dict(subject.medium_coeli),
        houses=houses,
        aspects=aspects,
        raw_subject=subject,
    )


def calculate_synastry(
    chart1: ChartData,
    chart2: ChartData,
) -> Dict[str, Any]:
    """
    Calculate synastry aspects between two ChartData objects.
    Returns cross-aspects + relationship score metadata.
    """
    syn = SynastryAspects(chart1.raw_subject, chart2.raw_subject)
    cross_aspects = []
    for asp in syn.relevant_aspects:
        cross_aspects.append({
            "planet1": asp.p1_name,
            "planet2": asp.p2_name,
            "aspect": asp.aspect,
            "orbit": round(asp.orbit, 2),
            "aspect_degrees": asp.aspect_degrees,
        })

    return {
        "person1": chart1.name,
        "person2": chart2.name,
        "cross_aspects": cross_aspects,
        "aspect_count": len(cross_aspects),
    }


def generate_report(chart: ChartData) -> str:
    """Generate a text report using kerykeion's ReportGenerator."""
    report = ReportGenerator(chart.raw_subject)
    return report.report


def draw_svg(chart: ChartData, output_path: str, theme: str = "dark") -> str:
    """Render an SVG wheel chart using kerykeion's ChartDrawer."""
    import shutil
    svg = KerykeionChartSVG(chart.raw_subject, chart_type="Natal", theme=theme)
    svg.makeSVG()
    # kerykeion writes to a default path based on the subject name
    # Copy to the requested output path
    default_path = getattr(svg, "output_path", None)
    if default_path and Path(default_path).exists():
        shutil.copy2(default_path, output_path)
    return output_path


# ---------------------------------------------------------------------------
# CLI / Test
# ---------------------------------------------------------------------------

def main():
    import json

    # Test with Boom's birth data
    print("=== Kerykeion Bridge Test ===")
    print()

    chart = calculate_natal(
        name="Boom",
        year=1996,
        month=11,
        day=20,
        hour=20,
        minute=37,
        lat=19.9071,
        lon=99.8328,
        tz_str="Asia/Bangkok",
        houses_system_identifier="P",
    )

    print(f"Natal Chart: {chart.name}")
    print(f"Birth: {chart.birth_date} {chart.birth_time} ({chart.tz_str})")
    print(f"Location: {chart.lat:.4f}N, {chart.lon:.4f}E")
    print()
    print(f"Sun:     {chart.sun['sign']} {chart.sun['degree']:.2f}°")
    print(f"Moon:    {chart.moon['sign']} {chart.moon['degree']:.2f}°")
    print(f"ASC:     {chart.ascendant['sign']} {chart.ascendant['degree']:.2f}°")
    print(f"MC:      {chart.mc['sign']} {chart.mc['degree']:.2f}°")
    print()
    print(f"Major Aspects: {len(chart.aspects)}")
    for asp in chart.aspects[:10]:
        print(f"  {asp['planet1']} {asp['aspect']} {asp['planet2']} (orb {asp['orbit']}°)")
    print()

    # JSON dump option
    if len(sys.argv) > 1 and sys.argv[1] == "--json":
        out = {
            "meta": {
                "name": chart.name,
                "birth_date": chart.birth_date,
                "birth_time": chart.birth_time,
                "tz_str": chart.tz_str,
                "lat": chart.lat,
                "lon": chart.lon,
            },
            "planets": {
                k: v for k, v in chart.__dict__.items()
                if k in {"sun", "moon", "mercury", "venus", "mars", "jupiter", "saturn", "uranus", "neptune", "pluto", "north_node", "south_node", "ascendant", "mc"}
            },
            "houses": chart.houses,
            "aspects": chart.aspects,
        }
        print(json.dumps(out, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
