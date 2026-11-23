"""Tests for the sensor icons (icons.json)."""

from __future__ import annotations

import json
from datetime import timedelta
from pathlib import Path

from custom_components.afl_team_tracker import sensor as sensor_mod
from custom_components.afl_team_tracker.sensor import SLOTS

from .common import g
from .test_sensor import setup, state

ICONS = Path(sensor_mod.__file__).parent / "icons.json"
ICON = "mdi:football-australian"


def _sensor_icons() -> dict:
    return json.loads(ICONS.read_text(encoding="utf-8"))["entity"]["sensor"]


def test_icons_file_has_expected_shape() -> None:
    data = json.loads(ICONS.read_text(encoding="utf-8"))
    assert set(data) == {"entity"}
    for entry in _sensor_icons().values():
        assert entry == {"default": ICON}


def test_football_for_all_but_next_game() -> None:
    expected = {s.translation_key for s in SLOTS if s.key != "next"}
    assert set(_sensor_icons()) == expected
    assert "next_game" not in _sensor_icons()


async def test_next_game_keeps_timestamp_class_and_has_no_icon_override(hass) -> None:
    await setup(hass, new=[g(1, timedelta(days=1))])
    nxt = state(hass, "next_game")
    assert nxt.attributes["device_class"] == "timestamp"
    assert "icon" not in nxt.attributes
