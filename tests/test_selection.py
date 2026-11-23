"""Tests for current/next/previous selection."""

from __future__ import annotations

from datetime import timedelta

from custom_components.afl_team_tracker.models import CANCELLED, LIVE, POSTPONED, RESULT, derive_period
from custom_components.afl_team_tracker.selection import MAX_PREVIOUS, merge_games, select_team_games

from .common import FRE, GEEL, NOW, SYD, g

D = timedelta


def test_next_is_earliest_future_fixture():
    sel = select_team_games([g(1, D(days=9)), g(2, D(days=2)), g(3, D(days=5))], 13, NOW)
    assert sel.next.id == 2
    assert sel.current is None and sel.previous == []


def test_other_teams_games_ignored():
    sel = select_team_games([g(1, D(days=1), home=FRE, away=GEEL)], 13, NOW)
    assert sel.next is None


def test_postponed_and_cancelled_never_next():
    games = [g(1, D(days=1), POSTPONED), g(2, D(days=2), CANCELLED), g(3, D(days=3))]
    assert select_team_games(games, 13, NOW).next.id == 3


def test_current_is_live_game():
    sel = select_team_games([g(1, D(minutes=-30), LIVE, scores=(20, 7)), g(2, D(days=7))], 13, NOW)
    assert sel.current.id == 1
    assert sel.next.id == 2


def test_live_with_future_start_still_current():
    assert select_team_games([g(1, D(minutes=10), LIVE)], 13, NOW).current.id == 1


def test_previous_newest_first_capped_at_five():
    games = [g(i, D(days=-i), RESULT, scores=(80, 70)) for i in range(1, 9)]
    sel = select_team_games(games, 13, NOW)
    assert [x.id for x in sel.previous] == [1, 2, 3, 4, 5]
    assert len(sel.previous) == MAX_PREVIOUS


def test_merge_prefers_live_or_result_over_fixture():
    fixture = g(1, D(days=-1))
    result = g(1, D(days=-1), RESULT, scores=(80, 70))
    assert merge_games([fixture], [result])[0].status == RESULT
    assert merge_games([result], [fixture])[0].status == RESULT
    assert [x.id for x in merge_games([g(1, D(days=1))], [g(2, D(days=2))])] == [1, 2]


def test_derive_period():
    assert derive_period(g(1, D(days=1))) == "Upcoming"
    assert derive_period(g(1, D(), LIVE)) == "Live"
    assert derive_period(g(1, D(), RESULT)) == "Result"
    assert derive_period(g(1, D(), POSTPONED)) == "Postponed"
    assert derive_period(g(1, D(), CANCELLED)) == "Cancelled"
