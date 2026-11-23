"""Tests for the bundled club logos."""

from __future__ import annotations

import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

from custom_components.afl_team_tracker.const import LOGOS, LOGOS_URL
from custom_components.afl_team_tracker.models import Team
from custom_components.afl_team_tracker.sensor import logo_url

DIR = Path(__file__).parent.parent / "custom_components" / "afl_team_tracker" / "www" / "logos"
FIXTURES = Path(__file__).parent / "fixtures"
FILES = sorted(DIR.glob("*.svg"))
SVG = "{http://www.w3.org/2000/svg}"


def test_logo_set_matches_the_files():
    assert {f.stem for f in FILES} == set(LOGOS)
    assert len(LOGOS) == 22


def test_every_men_and_women_club_abbreviation_has_a_logo():
    # Abbreviations of the 18 AFL clubs as used by the data source's API.
    clubs = (
        "ADEL BL CARL COLL ESS FRE GCFC GEEL GWS HAW MELB NMFC PORT RICH STK SYD WB WCE"
    ).split()
    assert all(c.lower() in LOGOS for c in clubs)


@pytest.mark.parametrize("path", FILES, ids=lambda p: p.stem)
def test_logo_is_a_safe_standalone_svg(path):
    text = path.read_text(encoding="utf-8")
    root = ET.fromstring(text)  # well-formed XML
    assert root.tag == f"{SVG}svg"
    assert root.get("viewBox")
    # Shown through <img>, but still never ship script, handlers or external refs.
    assert not re.search(r"<script|\son\w+\s*=|javascript:|<foreignObject|<iframe|<image", text, re.I)
    for value in re.findall(r'href="([^"]*)"', text):
        assert value.startswith("#"), value
    assert "http" not in re.sub(r'xmlns(?::\w+)?="[^"]*"', "", text)
    assert len(text) < 60_000


def test_logo_url_for_known_unknown_and_explicit_logo():
    assert logo_url(Team(13, "Sydney Swans", "SYD")) == f"{LOGOS_URL}/syd.svg"
    assert logo_url(Team(1, "Mystery", "XYZ")) == ""
    assert logo_url(Team(1, "No abbreviation", "")) == ""
    assert logo_url(Team(1, "Own", "SYD", logo="https://example.test/l.svg")) == "https://example.test/l.svg"


def test_every_fixture_team_gets_a_logo():
    for name in ("matches_2027.json", "matches_2026.json"):
        for match in json.loads((FIXTURES / name).read_text())["matches"]:
            for side in ("home", "away"):
                team = match[side].get("team")
                if team:
                    assert team["abbreviation"].lower() in LOGOS
