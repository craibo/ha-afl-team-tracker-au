"""Tests for the sensors."""

from __future__ import annotations

from datetime import timedelta
from unittest.mock import patch

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.afl_team_tracker.client import AflTrackerClient
from custom_components.afl_team_tracker.const import DOMAIN
from custom_components.afl_team_tracker.models import LIVE, RESULT
from custom_components.afl_team_tracker.sensor import (
    NO_GAME,
    RESULT_UNAVAILABLE,
    format_result,
    game_attributes,
    match_url,
    team_url,
)

from .common import FRE, GEEL, NOW, SYD, g

D = timedelta


@pytest.fixture(autouse=True)
def frozen_now():
    with patch("custom_components.afl_team_tracker.coordinator.dt_util.utcnow") as now:
        now.return_value = NOW
        yield


async def setup(hass, new=(), old=(), ladder=None, teams=(13,), names=None):
    by_season = {102: list(new), 85: list(old)}

    async def fetch(self, comp_season_id, team_id=None):
        return [x for x in by_season[comp_season_id] if team_id in (x.home.id, x.away.id)]

    async def fetch_ladder(self, season_id):
        return ladder or {}

    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            "competitions": [1],
            "teams": list(teams),
            "team_names": names or {"13": "Sydney Swans", "14": "Fremantle"},
            "team_competitions": {str(t): 1 for t in teams},
        },
    )
    entry.add_to_hass(hass)
    with (
        patch.object(AflTrackerClient, "fetch_matches", fetch),
        patch.object(AflTrackerClient, "fetch_ladder", fetch_ladder),
    ):
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()
    return entry


def state(hass, suffix, team="sydney_swans"):
    return hass.states.get(f"sensor.{team}_{suffix}")


def test_format_result():
    win = g(1, D(), RESULT, scores=(132, 69))
    assert format_result(win, 13) == "W 132–69"
    assert format_result(win, 10) == "L 69–132"
    assert format_result(g(1, D(), RESULT, scores=(80, 80)), 13) == "D 80–80"
    assert format_result(g(1, D(), RESULT), 13) == RESULT_UNAVAILABLE


def test_urls():
    game = g(8041, D())
    assert match_url(game) == "https://www.afl.com.au/afl/matches/8041"
    assert match_url(g(5, D(), competition_id=3)) == "https://www.afl.com.au/aflw/matches/5"
    assert team_url(game, SYD) == "https://www.afl.com.au/teams/sydney-swans"
    assert team_url(g(5, D(), competition_id=3), SYD) is None


def test_attributes_from_home_and_away_side():
    game = g(1, D(days=-2), RESULT, scores=(132, 69))
    ranks = lambda comp, team: {13: 2, 10: 7}.get(team.id)
    home = game_attributes(game, 13, ranks)
    assert home["opposition"] == "Geelong Cats"
    assert home["home_away"] == "home"
    assert home["period"] == "Result"
    assert (home["home_score"], home["away_score"]) == (132, 69)
    assert (home["home_score_detail"], home["away_score_detail"]) == ("22.0.132", "11.3.69")
    assert (home["home_rank"], home["away_rank"]) == (2, 7)
    assert (home["home_abbr"], home["away_abbr"]) == ("SYD", "GEEL")
    assert home["logos"] == {"home": "", "away": ""}
    assert home["venue"] == "SCG"
    assert home["round"] == "Round 1"
    assert "minute" not in home
    away = game_attributes(game, 10)
    assert away["opposition"] == "Sydney Swans"
    assert away["home_away"] == "away"
    assert away["home_rank"] is None


async def test_next_game_sensor(hass):
    await setup(hass, new=[g(1, D(days=2)), g(2, D(days=9))])
    nxt = state(hass, "next_game")
    assert nxt.state == (NOW + D(days=2)).isoformat()
    assert nxt.attributes["device_class"] == "timestamp"
    assert nxt.attributes["opposition"] == "Geelong Cats"
    assert nxt.attributes["period"] == "Upcoming"
    assert nxt.attributes["match_url"] == "https://www.afl.com.au/afl/matches/1"


async def test_current_game_idle_and_live(hass):
    await setup(hass, new=[g(1, D(days=2))])
    cur = state(hass, "current_game")
    assert cur.state == NO_GAME
    assert "opposition" not in cur.attributes


async def test_current_game_live(hass):
    await setup(hass, new=[g(2, D(minutes=-40), LIVE, scores=(20, 7))])
    cur = state(hass, "current_game")
    assert cur.state == "Live"
    assert cur.attributes["home_score"] == 20
    assert cur.attributes["period"] == "Live"


async def test_previous_games_and_ranks(hass):
    old = [g(i, D(days=-10 * i), RESULT, scores=(90 + i, 70)) for i in range(1, 7)]
    await setup(hass, old=old, ladder={13: 2, 10: 4})
    assert state(hass, "previous_game_1").state == "W 91–70"
    assert state(hass, "previous_game_5").state == "W 95–70"
    attrs = state(hass, "previous_game_1").attributes
    assert (attrs["home_rank"], attrs["away_rank"]) == (2, 4)
    assert state(hass, "next_game").state == "unknown"


async def test_result_from_away_side(hass):
    game = g(1, D(days=-3), RESULT, home=GEEL, away=SYD, scores=(100, 90))
    await setup(hass, old=[game])
    sensor = state(hass, "previous_game_1")
    assert sensor.state == "L 90–100"
    assert sensor.attributes["home_away"] == "away"


async def test_seven_sensors_per_team_and_device(hass):
    from homeassistant.helpers import device_registry as dr

    entry = await setup(hass, teams=(13, 14))
    names = {s.entity_id for s in hass.states.async_all("sensor")}
    assert len(names) == 14
    devices = dr.async_entries_for_config_entry(dr.async_get(hass), entry.entry_id)
    assert {d.name for d in devices} == {"Sydney Swans", "Fremantle"}


async def test_unfollowed_team_device_removed(hass):
    from homeassistant.helpers import device_registry as dr

    entry = await setup(hass, teams=(13, 14))
    hass.config_entries.async_update_entry(entry, options={"teams": [14]})

    async def fetch(self, comp_season_id, team_id=None):
        return []

    with patch.object(AflTrackerClient, "fetch_matches", fetch):
        await hass.config_entries.async_reload(entry.entry_id)
        await hass.async_block_till_done()
    devices = dr.async_entries_for_config_entry(dr.async_get(hass), entry.entry_id)
    assert {d.name for d in devices} == {"Fremantle"}
