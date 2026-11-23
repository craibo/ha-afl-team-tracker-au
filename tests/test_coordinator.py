"""Tests for the update coordinator."""

from __future__ import annotations

from datetime import timedelta
from unittest.mock import AsyncMock, patch

import pytest
from homeassistant.helpers.update_coordinator import UpdateFailed
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.afl_team_tracker.client import AflTrackerClient, AflTrackerError
from custom_components.afl_team_tracker.const import DOMAIN
from custom_components.afl_team_tracker.coordinator import (
    IDLE_INTERVAL,
    LIVE_INTERVAL,
    MAX_RETRY_INTERVAL,
    MIN_INTERVAL,
    PREVIOUS_INTERVAL,
    RETRY_INTERVAL,
    SOON_INTERVAL,
    SOON_WINDOW,
    AflTrackerCoordinator,
    compute_interval,
    entry_team_competitions,
    entry_teams,
    is_in_play,
    retry_interval,
)
from custom_components.afl_team_tracker.models import LIVE, RESULT

from .common import FRE, GEEL, NOW, SYD, g

D = timedelta


@pytest.fixture(autouse=True)
def frozen_now():
    with patch("custom_components.afl_team_tracker.coordinator.dt_util.utcnow") as now:
        now.return_value = NOW
        yield now


def test_interval_live():
    assert compute_interval([g(1, D(minutes=-10), LIVE)], NOW) == LIVE_INTERVAL


def test_interval_fixture_past_start_is_polled_live():
    game = g(1, D(minutes=-30))
    assert is_in_play(game, NOW)
    assert compute_interval([game], NOW) == LIVE_INTERVAL


def test_not_in_play_after_window_or_when_finished():
    assert not is_in_play(g(1, D(hours=-5)), NOW)
    assert not is_in_play(g(1, D(minutes=-30), RESULT, scores=(80, 70)), NOW)
    assert not is_in_play(g(1, D(minutes=30)), NOW)


def test_interval_soon_and_wake_up_and_idle():
    assert compute_interval([g(1, D(minutes=30))], NOW) == SOON_INTERVAL
    assert compute_interval([g(1, D(hours=5))], NOW) == D(hours=3)
    assert compute_interval([g(1, D(days=3))], NOW) == IDLE_INTERVAL
    assert compute_interval([g(1, SOON_WINDOW + D(seconds=5))], NOW) == MIN_INTERVAL
    assert compute_interval([], NOW) == IDLE_INTERVAL
    assert compute_interval([g(1, D(days=-1), RESULT, scores=(80, 70))], NOW) == IDLE_INTERVAL


def test_retry_interval_backs_off_and_caps():
    assert retry_interval(1, IDLE_INTERVAL) == RETRY_INTERVAL
    assert retry_interval(3, IDLE_INTERVAL) == RETRY_INTERVAL
    assert retry_interval(4, IDLE_INTERVAL) == 2 * RETRY_INTERVAL
    assert retry_interval(20, IDLE_INTERVAL) == MAX_RETRY_INTERVAL
    assert retry_interval(1, LIVE_INTERVAL) == LIVE_INTERVAL


def test_entry_helpers_prefer_options():
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={"teams": [1], "team_competitions": {"1": 1}},
        options={"teams": [2, 3], "team_competitions": {"2": 1, "3": 3}},
    )
    assert entry_teams(entry) == [2, 3]
    assert entry_team_competitions(entry) == {2: 1, 3: 3}


SEASONS = {
    102: [g(1, D(days=2))],
    85: [
        g(8, D(days=-200), RESULT, scores=(132, 69)),
        g(7, D(days=-207), RESULT, scores=(70, 80), home=GEEL, away=SYD),
    ],
}


def make_fetch(by_season, calls):
    async def fetch(self, comp_season_id, team_id=None):
        calls.append((comp_season_id, team_id))
        return [
            x for x in by_season[comp_season_id] if team_id in (x.home.id, x.away.id)
        ]

    return fetch


def coordinator(hass, teams=(13,), competitions=None):
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            "competitions": [1],
            "teams": list(teams),
            "team_competitions": {str(t): (competitions or {}).get(t, 1) for t in teams},
        },
    )
    entry.add_to_hass(hass)
    from homeassistant.helpers.aiohttp_client import async_get_clientsession

    return AflTrackerCoordinator(hass, entry, AflTrackerClient(async_get_clientsession(hass)))


async def test_selects_next_from_new_season_and_previous_from_old(hass):
    calls = []
    coord = coordinator(hass)
    with patch.object(AflTrackerClient, "fetch_matches", make_fetch(SEASONS, calls)):
        await coord.async_refresh()
    sel = coord.data[13]
    assert sel.next.id == 1
    assert [x.id for x in sel.previous] == [8, 7]
    assert sel.current is None
    assert (102, 13) in calls and (85, 13) in calls
    assert coord.update_interval == IDLE_INTERVAL


async def test_previous_season_is_cached(hass, frozen_now):
    calls = []
    coord = coordinator(hass)
    with patch.object(AflTrackerClient, "fetch_matches", make_fetch(SEASONS, calls)):
        await coord.async_refresh()
        frozen_now.return_value = NOW + D(minutes=5)
        await coord.async_refresh()
        assert sorted(calls).count((85, 13)) == 1
        assert sorted(calls).count((102, 13)) == 2
        frozen_now.return_value = NOW + PREVIOUS_INTERVAL + D(minutes=1)
        await coord.async_refresh()
        assert sorted(calls).count((85, 13)) == 2


async def test_seasons_fetched_once_a_day(hass, stub_network):
    from custom_components.afl_team_tracker.client import AflTrackerClient as C

    coord = coordinator(hass)
    with patch.object(C, "fetch_matches", make_fetch(SEASONS, [])):
        await coord.async_refresh()
        await coord.async_refresh()
        assert C.fetch_comp_seasons.await_count == 1


async def test_live_game_polled_every_minute(hass):
    live = g(2, D(minutes=-20), LIVE, scores=(20, 7))
    coord = coordinator(hass)
    with patch.object(
        AflTrackerClient, "fetch_matches", make_fetch({102: [live], 85: []}, [])
    ):
        await coord.async_refresh()
    assert coord.data[13].current.id == 2
    assert coord.update_interval == LIVE_INTERVAL


async def test_team_without_competition_is_skipped(hass):
    entry = MockConfigEntry(domain=DOMAIN, data={"competitions": [1], "teams": [13], "team_competitions": {}})
    entry.add_to_hass(hass)
    from homeassistant.helpers.aiohttp_client import async_get_clientsession

    coord = AflTrackerCoordinator(hass, entry, AflTrackerClient(async_get_clientsession(hass)))
    calls = []
    with patch.object(AflTrackerClient, "fetch_matches", make_fetch(SEASONS, calls)):
        await coord.async_refresh()
    assert calls == []
    assert coord.data[13].next is None


async def test_ladder_uses_previous_season_before_round_one(hass, stub_network):
    async def ladder(self, season_id):
        return {13: 2, 14: 1} if season_id == 85 else {}

    coord = coordinator(hass)
    with (
        patch.object(AflTrackerClient, "fetch_matches", make_fetch(SEASONS, [])),
        patch.object(AflTrackerClient, "fetch_ladder", ladder),
    ):
        await coord.async_refresh()
    assert coord.rank(1, SYD) == 2
    assert coord.rank(1, FRE) == 1
    assert coord.rank(1, GEEL) is None
    assert coord.rank(3, SYD) is None


async def test_ladder_prefers_current_season(hass):
    async def ladder(self, season_id):
        return {13: 1} if season_id == 102 else {13: 5}

    coord = coordinator(hass)
    with (
        patch.object(AflTrackerClient, "fetch_matches", make_fetch(SEASONS, [])),
        patch.object(AflTrackerClient, "fetch_ladder", ladder),
    ):
        await coord.async_refresh()
    assert coord.rank(1, SYD) == 1


async def test_ladder_failure_keeps_last_and_never_fails_refresh(hass, frozen_now):
    results = iter([{13: 3}, AflTrackerError("down")])

    async def ladder(self, season_id):
        r = next(results)
        if isinstance(r, Exception):
            raise r
        return r

    coord = coordinator(hass)
    with (
        patch.object(AflTrackerClient, "fetch_matches", make_fetch(SEASONS, [])),
        patch.object(AflTrackerClient, "fetch_ladder", ladder),
    ):
        await coord.async_refresh()
        frozen_now.return_value = NOW + D(hours=2)
        await coord.async_refresh()
    assert coord.last_update_success
    assert coord.rank(1, SYD) == 3


async def test_first_refresh_failure_raises(hass):
    coord = coordinator(hass)
    with patch.object(AflTrackerClient, "fetch_matches", AsyncMock(side_effect=AflTrackerError("boom"))):
        await coord.async_refresh()
    assert not coord.last_update_success
    assert isinstance(coord.last_exception, UpdateFailed)


async def test_failures_keep_last_data_then_fail(hass):
    coord = coordinator(hass)
    with patch.object(AflTrackerClient, "fetch_matches", make_fetch(SEASONS, [])):
        await coord.async_refresh()
    good = coord.data
    with patch.object(AflTrackerClient, "fetch_matches", AsyncMock(side_effect=AflTrackerError("boom"))):
        await coord.async_refresh()
        assert coord.last_update_success and coord.data is good
        assert coord.update_interval == RETRY_INTERVAL
        await coord.async_refresh()
        assert coord.last_update_success
        await coord.async_refresh()
        assert not coord.last_update_success


async def test_one_team_failing_keeps_the_other_working(hass):
    async def fetch(self, comp_season_id, team_id=None):
        if team_id == 14:
            raise AflTrackerError("boom")
        return [x for x in SEASONS[comp_season_id] if team_id in (x.home.id, x.away.id)]

    coord = coordinator(hass, teams=(13, 14))
    with patch.object(AflTrackerClient, "fetch_matches", fetch):
        await coord.async_refresh()
    assert coord.last_update_success
    assert coord.data[13].next.id == 1
    assert coord.update_interval <= RETRY_INTERVAL


async def test_season_list_failure_with_no_cache_fails(hass, stub_network):
    coord = coordinator(hass)
    with patch.object(AflTrackerClient, "fetch_comp_seasons", AsyncMock(side_effect=AflTrackerError("x"))):
        await coord.async_refresh()
    assert not coord.last_update_success


async def test_no_season_for_competition_fails_the_team(hass):
    coord = coordinator(hass, competitions={13: 99})
    with patch.object(AflTrackerClient, "fetch_matches", make_fetch(SEASONS, [])):
        await coord.async_refresh()
    assert not coord.last_update_success
