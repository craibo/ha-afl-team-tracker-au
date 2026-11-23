"""Tests for the config flow and options flow."""

from __future__ import annotations

from datetime import timedelta
from unittest.mock import AsyncMock, patch

import pytest
import voluptuous as vol
from homeassistant.config_entries import ConfigEntryState
from homeassistant.data_entry_flow import FlowResultType
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.afl_team_tracker.client import AflTrackerClient, AflTrackerError
from custom_components.afl_team_tracker.const import DOMAIN
from custom_components.afl_team_tracker.models import CompSeason

from .common import FRE, GEEL, NOW, SYD, g

D = timedelta
PREMIERSHIP = "Toyota AFL Premiership"


@pytest.fixture(autouse=True)
def frozen_now():
    with patch("custom_components.afl_team_tracker.coordinator.dt_util.utcnow") as now:
        now.return_value = NOW
        yield


# season id -> games. 102 = 2027 premiership, 85 = 2026 premiership, 96 = AFLW.
BY_SEASON = {
    102: [g(1, D(days=2), home=SYD, away=GEEL), g(2, D(days=9), home=FRE, away=SYD)],
    85: [g(8, D(days=-200), home=SYD, away=FRE)],
    96: [g(3, D(days=-90), home=GEEL, away=FRE, competition_id=3)],
}


async def fetch_ok(self, comp_season_id, team_id=None):
    games = BY_SEASON[comp_season_id]
    if team_id is not None:
        games = [x for x in games if team_id in (x.home.id, x.away.id)]
    return games


async def fetch_fail(self, comp_season_id, team_id=None):
    raise AflTrackerError("boom")


async def fetch_empty(self, comp_season_id, team_id=None):
    return []


async def start(hass, comps):
    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": "user"})
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "user"
    return await hass.config_entries.flow.async_configure(
        result["flow_id"], {"competitions": comps}
    )


def team_options(result):
    schema = result["data_schema"].schema
    key = next(k for k in schema if k == "teams")
    return {o["value"]: o["label"] for o in schema[key].validators[0].config["options"]}


async def test_full_flow(hass):
    with (
        patch.object(AflTrackerClient, "fetch_matches", fetch_ok),
        patch("custom_components.afl_team_tracker.async_setup_entry", return_value=True),
    ):
        result = await start(hass, ["1"])
        assert result["step_id"] == "teams"
        assert team_options(result) == {
            "14": f"Fremantle ({PREMIERSHIP})",
            "10": f"Geelong Cats ({PREMIERSHIP})",
            "13": f"Sydney Swans ({PREMIERSHIP})",
        }
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], {"teams": ["13"]}
        )
        assert result["type"] is FlowResultType.CREATE_ENTRY
        assert result["title"] == "AFL Team Tracker"
        assert result["data"] == {
            "competitions": [1],
            "teams": [13],
            "team_names": {"13": "Sydney Swans"},
            "team_competitions": {"13": 1},
        }


async def test_teams_sorted_by_name_and_multiple_competitions(hass):
    with patch.object(AflTrackerClient, "fetch_matches", fetch_ok):
        result = await start(hass, ["1", "3"])
    opts = team_options(result)
    assert list(opts) == ["14", "10", "13"]  # sorted by name
    # A team in two competitions is offered once, under the first selected one.
    assert opts["10"] == f"Geelong Cats ({PREMIERSHIP})"
    assert len(opts) == 3


async def test_falls_back_to_previous_season_when_new_one_has_no_fixtures(hass):
    async def fetch(self, comp_season_id, team_id=None):
        return [] if comp_season_id == 102 else BY_SEASON[comp_season_id]

    with patch.object(AflTrackerClient, "fetch_matches", fetch):
        result = await start(hass, ["1"])
    assert set(team_options(result)) == {"13", "14"}


async def test_empty_competitions_rejected(hass):
    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": "user"})
    with pytest.raises(vol.Invalid):
        await hass.config_entries.flow.async_configure(result["flow_id"], {"competitions": []})


async def test_empty_teams_rejected(hass):
    with patch.object(AflTrackerClient, "fetch_matches", fetch_ok):
        result = await start(hass, ["1"])
        with pytest.raises(vol.Invalid):
            await hass.config_entries.flow.async_configure(result["flow_id"], {"teams": []})


async def test_cannot_connect(hass):
    with patch.object(AflTrackerClient, "fetch_matches", fetch_fail):
        result = await start(hass, ["1"])
    assert result["step_id"] == "user"
    assert result["errors"] == {"base": "cannot_connect"}


async def test_season_list_failure_is_cannot_connect(hass, stub_network):
    with patch.object(
        AflTrackerClient, "fetch_comp_seasons", AsyncMock(side_effect=AflTrackerError("x"))
    ):
        result = await start(hass, ["1"])
    assert result["errors"] == {"base": "cannot_connect"}


async def test_no_teams(hass):
    with patch.object(AflTrackerClient, "fetch_matches", fetch_empty):
        result = await start(hass, ["1"])
    assert result["step_id"] == "user"
    assert result["errors"] == {"base": "no_teams"}


async def test_single_instance(hass):
    MockConfigEntry(domain=DOMAIN, unique_id=DOMAIN, data={"competitions": [1], "teams": [13]}).add_to_hass(hass)
    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": "user"})
    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "already_configured"


def make_entry(hass, teams=(13,)):
    entry = MockConfigEntry(
        domain=DOMAIN,
        unique_id=DOMAIN,
        data={
            "competitions": [1],
            "teams": list(teams),
            "team_names": {"13": "Sydney Swans", "14": "Fremantle"},
            "team_competitions": {"13": 1, "14": 1},
        },
    )
    entry.add_to_hass(hass)
    return entry


async def test_options_flow_updates_and_reloads(hass):
    entry = make_entry(hass)
    with patch.object(AflTrackerClient, "fetch_matches", fetch_ok):
        await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()
        first = entry.runtime_data
        result = await hass.config_entries.options.async_init(entry.entry_id)
        assert result["type"] is FlowResultType.FORM
        assert result["step_id"] == "init"
        result = await hass.config_entries.options.async_configure(
            result["flow_id"], {"teams": ["14"]}
        )
        assert result["type"] is FlowResultType.CREATE_ENTRY
        await hass.async_block_till_done()
        assert entry.options == {
            "teams": [14],
            "team_names": {"14": "Fremantle"},
            "team_competitions": {"14": 1},
        }
        assert entry.state is ConfigEntryState.LOADED
        assert entry.runtime_data is not first
        assert list(entry.runtime_data.data) == [14]


async def test_options_flow_cannot_connect(hass):
    entry = make_entry(hass)
    with patch.object(AflTrackerClient, "fetch_matches", fetch_fail):
        result = await hass.config_entries.options.async_init(entry.entry_id)
    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "cannot_connect"}


async def test_options_flow_submit_does_not_refetch(hass):
    entry = make_entry(hass)
    with patch.object(AflTrackerClient, "fetch_matches", fetch_ok):
        result = await hass.config_entries.options.async_init(entry.entry_id)
    assert result["errors"] == {}
    with patch.object(AflTrackerClient, "fetch_matches", fetch_fail):
        result = await hass.config_entries.options.async_configure(
            result["flow_id"], {"teams": ["13", "14"]}
        )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["data"] == {
        "teams": [13, 14],
        "team_names": {"13": "Sydney Swans", "14": "Fremantle"},
        "team_competitions": {"13": 1, "14": 1},
    }


async def test_options_flow_down_can_still_unfollow(hass):
    entry = make_entry(hass, teams=(13, 14))
    with patch.object(AflTrackerClient, "fetch_matches", fetch_fail):
        result = await hass.config_entries.options.async_init(entry.entry_id)
        assert result["errors"] == {"base": "cannot_connect"}
        assert team_options(result) == {"13": "Sydney Swans", "14": "Fremantle"}
        result = await hass.config_entries.options.async_configure(
            result["flow_id"], {"teams": ["14"]}
        )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["data"]["teams"] == [14]
    assert result["data"]["team_competitions"] == {"14": 1}
