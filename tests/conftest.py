"""Shared test fixtures."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Enable loading of custom integrations in all tests."""
    yield


@pytest.fixture(autouse=True)
def frontend(hass):
    """Stub the http/frontend dependencies; yield (register_static, add_js)."""
    register = AsyncMock()
    hass.http = MagicMock()
    hass.http.async_register_static_paths = register
    with (
        patch("homeassistant.components.http.async_setup", return_value=True),
        patch("homeassistant.components.frontend.async_setup", return_value=True),
        patch("custom_components.afl_team_tracker.add_extra_js_url") as add_js,
    ):
        yield register, add_js


@pytest.fixture(autouse=True)
def stub_network(request):
    """Stub the season list and ladder unless a test patches them.

    The client tests exercise the real methods, so they opt out.
    """
    if request.module.__name__.endswith("test_client"):
        yield None
        return
    from custom_components.afl_team_tracker.models import CompSeason

    seasons = [
        CompSeason(85, 1, 2026, "2026 Toyota AFL Premiership"),
        CompSeason(102, 1, 2027, "2027 Toyota AFL Premiership"),
        CompSeason(96, 3, 2026, "2026 NAB AFLW Season"),
    ]
    with (
        patch(
            "custom_components.afl_team_tracker.client.AflTrackerClient.fetch_comp_seasons",
            AsyncMock(return_value=seasons),
        ),
        patch(
            "custom_components.afl_team_tracker.client.AflTrackerClient.fetch_ladder",
            AsyncMock(return_value={}),
        ) as ladder,
    ):
        yield ladder
