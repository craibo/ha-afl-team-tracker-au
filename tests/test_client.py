"""Tests for the HTTP client."""

from __future__ import annotations

import json
import re
from pathlib import Path

import aiohttp
import pytest
from aioresponses import aioresponses

from custom_components.afl_team_tracker.client import (
    API_URL,
    MAX_PAGES,
    AflTrackerClient,
    AflTrackerError,
)

FIXTURES = Path(__file__).parent / "fixtures"


def load(name):
    return json.loads((FIXTURES / name).read_text())


@pytest.fixture
async def client():
    async with aiohttp.ClientSession() as session:
        yield AflTrackerClient(session)


def url(path, **params):
    # Query parameters are sorted by the client library: match in any order.
    wanted = "".join(rf"(?=(?:.*&)?{k}={v}(?:&|$))" for k, v in params.items())
    return re.compile(rf"^{re.escape(API_URL + path)}\?{wanted}.*$")


def test_competitions_listed(client):
    assert AflTrackerClient(None).list_competitions() == {
        1: "Toyota AFL Premiership",
        3: "NAB AFLW",
    }


async def test_fetch_matches_for_team(client):
    with aioresponses() as m:
        m.get(url("/matches", compSeasonId=102, teamId=13, pageSize=100), payload=load("matches_2027.json"))
        games = await client.fetch_matches(102, 13)
        (call,) = m.requests.values()
        assert call[0].kwargs["headers"]["User-Agent"].startswith("ha-afl-team-tracker-au/")
    assert [g.id for g in games] == [9091, 9098]


async def test_fetch_matches_without_team_filter_omits_param(client):
    with aioresponses() as m:
        m.get(url("/matches", compSeasonId=102), payload=load("matches_2027.json"))
        await client.fetch_matches(102)
        (key,) = m.requests
        assert "teamId" not in str(key[1])


async def test_pagination_follows_all_pages(client):
    page = load("matches_2027.json")
    page["meta"]["pagination"]["numPages"] = 3
    with aioresponses() as m:
        for _ in range(3):
            m.get(url("/matches"), payload=page)
        games = await client.fetch_matches(102)
        assert sum(len(c) for c in m.requests.values()) == 3
    assert len(games) == 6


async def test_pagination_is_capped(client):
    page = load("matches_2027.json")
    page["meta"]["pagination"]["numPages"] = 10_000
    with aioresponses() as m:
        for _ in range(MAX_PAGES):
            m.get(url("/matches"), payload=page)
        await client.fetch_matches(102)
        assert sum(len(c) for c in m.requests.values()) == MAX_PAGES


async def test_comp_seasons(client):
    with aioresponses() as m:
        m.get(url("/compseasons"), payload=load("compseasons.json"))
        seasons = await client.fetch_comp_seasons()
    assert {s.id for s in seasons} == {85, 102, 96}


async def test_ladder(client):
    with aioresponses() as m:
        m.get(f"{API_URL}/compseasons/85/ladders", payload=load("ladder.json"))
        assert await client.fetch_ladder(85) == {14: 1, 13: 2}


async def test_ladder_404_is_empty(client):
    with aioresponses() as m:
        m.get(f"{API_URL}/compseasons/102/ladders", status=404)
        assert await client.fetch_ladder(102) == {}


@pytest.mark.parametrize("status", [404, 500, 503])
async def test_http_errors_raise(client, status):
    with aioresponses() as m:
        m.get(url("/matches"), status=status)
        with pytest.raises(AflTrackerError, match=str(status)):
            await client.fetch_matches(102)


async def test_ladder_500_raises(client):
    with aioresponses() as m:
        m.get(f"{API_URL}/compseasons/85/ladders", status=500)
        with pytest.raises(AflTrackerError):
            await client.fetch_ladder(85)


async def test_connection_error_and_timeout_raise(client):
    with aioresponses() as m:
        m.get(url("/matches"), exception=aiohttp.ClientConnectionError("down"))
        with pytest.raises(AflTrackerError, match="down"):
            await client.fetch_matches(102)
    with aioresponses() as m:
        m.get(url("/matches"), exception=TimeoutError())
        with pytest.raises(AflTrackerError, match="Timed out"):
            await client.fetch_matches(102)


async def test_invalid_json_and_unexpected_shape_raise(client):
    with aioresponses() as m:
        m.get(url("/matches"), body="<html>", content_type="text/html")
        with pytest.raises(AflTrackerError):
            await client.fetch_matches(102)
    with aioresponses() as m:
        m.get(url("/matches"), payload={"nope": 1})
        with pytest.raises(AflTrackerError, match="Unexpected data"):
            await client.fetch_matches(102)
