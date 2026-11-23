"""Tests for config entry setup, reload and unload, and card registration."""

from __future__ import annotations

import json
from datetime import timedelta
from pathlib import Path
from unittest.mock import patch

import pytest
from homeassistant.config_entries import ConfigEntryState
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.afl_team_tracker.client import AflTrackerClient, AflTrackerError
from custom_components.afl_team_tracker.const import DOMAIN
from custom_components.afl_team_tracker.coordinator import AflTrackerCoordinator

from .common import NOW, g

COMPONENT = Path(__file__).parent.parent / "custom_components" / "afl_team_tracker"
URL = "/afl_team_tracker/afl-tracker-cards.js"


@pytest.fixture(autouse=True)
def frozen_now():
    with patch("custom_components.afl_team_tracker.coordinator.dt_util.utcnow") as now:
        now.return_value = NOW
        yield


async def fetch(self, comp_season_id, team_id=None):
    return [g(1, timedelta(days=1))] if comp_season_id == 102 else []


def entry_for(hass):
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={"competitions": [1], "teams": [13], "team_competitions": {"13": 1}},
    )
    entry.add_to_hass(hass)
    return entry


async def test_setup_and_unload(hass):
    entry = entry_for(hass)
    with patch.object(AflTrackerClient, "fetch_matches", fetch):
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()
        assert entry.state is ConfigEntryState.LOADED
        assert isinstance(entry.runtime_data, AflTrackerCoordinator)
        assert entry.runtime_data.data[13].next.id == 1
        assert await hass.config_entries.async_unload(entry.entry_id)
        await hass.async_block_till_done()
        assert entry.state is ConfigEntryState.NOT_LOADED


async def test_first_refresh_failure_retries(hass):
    async def boom(self, comp_season_id, team_id=None):
        raise AflTrackerError("boom")

    entry = entry_for(hass)
    with patch.object(AflTrackerClient, "fetch_matches", boom):
        assert not await hass.config_entries.async_setup(entry.entry_id)
    assert entry.state is ConfigEntryState.SETUP_RETRY


async def test_options_change_reloads(hass):
    entry = entry_for(hass)
    with patch.object(AflTrackerClient, "fetch_matches", fetch):
        await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()
        first = entry.runtime_data
        hass.config_entries.async_update_entry(
            entry, options={"teams": [14], "team_competitions": {"14": 1}}
        )
        await hass.async_block_till_done()
        assert entry.state is ConfigEntryState.LOADED
        assert entry.runtime_data is not first
        assert list(entry.runtime_data.data) == [14]


async def test_registers_static_path_and_resource(hass, frontend):
    version = json.loads((COMPONENT / "manifest.json").read_text())["version"]
    register, add_js = frontend
    entry = entry_for(hass)
    with patch.object(AflTrackerClient, "fetch_matches", fetch):
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()
    configs = register.call_args.args[0]
    assert len(configs) == 1
    assert configs[0].url_path == URL
    assert Path(configs[0].path) == COMPONENT / "www" / "afl-tracker-cards.js"
    assert Path(configs[0].path).is_file()
    assert add_js.call_args.args[1] == f"{URL}?v={version}"


async def test_registers_once_across_reload_and_entries(hass, frontend):
    register, add_js = frontend
    with patch.object(AflTrackerClient, "fetch_matches", fetch):
        first, second = entry_for(hass), entry_for(hass)
        assert await hass.config_entries.async_setup(first.entry_id)
        await hass.async_block_till_done()
        assert await hass.config_entries.async_reload(first.entry_id)
        await hass.async_block_till_done()
        assert await hass.config_entries.async_reload(second.entry_id)
        await hass.async_block_till_done()
    assert register.await_count == 1
    assert add_js.call_count == 1


def test_bundle_defines_both_cards():
    bundle = (COMPONENT / "www" / "afl-tracker-cards.js").read_text()
    assert "afl-tracker-game-card" in bundle
    assert "afl-tracker-team-card" in bundle
