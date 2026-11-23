"""Shared builders for tests."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from custom_components.afl_team_tracker.models import Game, Team

NOW = datetime(2027, 3, 20, 12, 0, tzinfo=timezone.utc)
SYD = Team(13, "Sydney Swans", "SYD", "Swans")
GEEL = Team(10, "Geelong Cats", "GEEL", "Cats")
FRE = Team(14, "Fremantle", "FRE", "Dockers")


def g(
    gid: int,
    delta: timedelta,
    status: str = "fixture",
    home: Team = SYD,
    away: Team = GEEL,
    scores: tuple[int, int] | None = None,
    competition_id: int = 1,
) -> Game:
    """A game starting ``delta`` after NOW."""
    hs, as_ = scores if scores else (None, None)
    return Game(
        id=gid,
        kickoff=NOW + delta,
        home=home,
        away=away,
        home_score=hs,
        away_score=as_,
        home_detail=f"{hs // 6}.{hs % 6}.{hs}" if hs is not None else None,
        away_detail=f"{as_ // 6}.{as_ % 6}.{as_}" if as_ is not None else None,
        venue="SCG",
        competition_id=competition_id,
        competition="Toyota AFL Premiership",
        status=status,
        raw_status=status.upper(),
        round_name="Round 1",
    )
