"""Tests for the JSON parsers."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from custom_components.afl_team_tracker.models import (
    CANCELLED,
    FIXTURE,
    LIVE,
    POSTPONED,
    RESULT,
    CompSeason,
    pick_seasons,
)
from custom_components.afl_team_tracker.source import (
    ParseError,
    categorise_status,
    num_pages,
    parse_comp_seasons,
    parse_ladder,
    parse_match,
    parse_matches,
)

FIXTURES = Path(__file__).parent / "fixtures"


def load(name: str):
    return json.loads((FIXTURES / name).read_text())


def test_parse_scheduled_matches_skips_placeholders():
    games = parse_matches(load("matches_2027.json"))
    assert [g.id for g in games] == [9091, 9098]
    first = games[0]
    assert (first.home.id, first.home.name, first.home.abbreviation) == (13, "Sydney Swans", "SYD")
    assert first.away.nickname == "Cats"
    assert first.status == FIXTURE
    assert first.venue == "SCG"
    assert first.home_score is None and first.home_detail is None
    assert first.kickoff.isoformat() == "2027-03-17T08:30:00+00:00"
    assert first.competition_id == 1
    assert first.competition == "Toyota AFL Premiership"
    assert first.round_name == "Round 1"
    assert first.live is False


def test_parse_concluded_match_scores():
    (game,) = parse_matches(load("matches_2026.json"))
    assert game.status == RESULT
    assert (game.home_score, game.away_score) == (132, 69)
    assert (game.home_detail, game.away_detail) == ("20.12.132", "10.9.69")


@pytest.mark.parametrize(
    ("raw", "category"),
    [
        ("SCHEDULED", FIXTURE),
        ("scheduled", FIXTURE),
        ("CONFIRMED_TEAMS", FIXTURE),
        ("", FIXTURE),
        ("CONCLUDED", RESULT),
        ("COMPLETE", RESULT),
        ("POSTPONED", POSTPONED),
        ("CANCELLED", CANCELLED),
        ("CANCELED", CANCELLED),
        ("LIVE", LIVE),
        ("IN_PROGRESS", LIVE),
        ("In Progress", LIVE),
        ("QUARTER_TIME", LIVE),
        ("HALF_TIME", LIVE),
        ("SOMETHING_NEW", FIXTURE),
    ],
)
def test_categorise_status(raw, category):
    assert categorise_status(raw) == category


def test_live_match_with_running_score():
    item = load("matches_2026.json")["matches"][0]
    item["status"] = "LIVE"
    item["home"]["score"] = {"goals": 3, "behinds": 2, "totalScore": 20}
    item["away"]["score"] = {"goals": 1, "behinds": 1, "totalScore": 7}
    game = parse_match(item)
    assert game.live
    assert (game.home_score, game.away_score) == (20, 7)


def test_score_without_goal_breakdown():
    item = load("matches_2026.json")["matches"][0]
    item["home"]["score"] = {"totalScore": 50}
    game = parse_match(item)
    assert game.home_score == 50 and game.home_detail is None


def test_match_without_teams_is_skipped():
    item = load("matches_2027.json")["matches"][0]
    del item["away"]
    assert parse_match(item) is None


@pytest.mark.parametrize(
    "mutate",
    [
        lambda m: m.pop("id"),
        lambda m: m.update(utcStartTime="soon"),
        lambda m: m.update(utcStartTime=None),
        lambda m: m.update(utcStartTime="2027-03-17T08:30:00"),
    ],
)
def test_malformed_match_raises(mutate):
    item = load("matches_2027.json")["matches"][0]
    mutate(item)
    with pytest.raises(ParseError):
        parse_match(item)


@pytest.mark.parametrize("payload", [None, [], {}, {"matches": "x"}])
def test_parse_matches_rejects_bad_payload(payload):
    with pytest.raises(ParseError):
        parse_matches(payload)


def test_num_pages():
    assert num_pages({"meta": {"pagination": {"numPages": 3}}}) == 3
    assert num_pages({"meta": {}}) == 1
    assert num_pages(None) == 1
    assert num_pages({"meta": {"pagination": {"numPages": 0}}}) == 1


def test_parse_comp_seasons_and_pick():
    seasons = parse_comp_seasons(load("compseasons.json"))
    assert seasons[0] == CompSeason(85, 1, 2026, "2026 Toyota AFL Premiership")
    assert [s.id for s in pick_seasons(seasons, 1)] == [102, 85]
    assert [s.id for s in pick_seasons(seasons, 3)] == [96]
    assert pick_seasons(seasons, 99) == []


def test_pick_seasons_one_per_year_highest_id_and_two_newest():
    seasons = [CompSeason(i, 1, y, "") for i, y in [(1, 2024), (2, 2025), (3, 2026), (4, 2026), (5, 2027)]]
    assert [s.id for s in pick_seasons(seasons, 1)] == [5, 4]


def test_parse_comp_seasons_skips_incomplete_and_rejects_bad():
    assert parse_comp_seasons({"compSeasons": [{"id": 1}, "x"]}) == []
    with pytest.raises(ParseError):
        parse_comp_seasons({})


def test_parse_ladder():
    assert parse_ladder(load("ladder.json")) == {14: 1, 13: 2}
    assert parse_ladder({"ladders": []}) == {}
    with pytest.raises(ParseError):
        parse_ladder({})
