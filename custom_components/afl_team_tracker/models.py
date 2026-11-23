"""Data models for the AFL Team Tracker integration."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from .const import PERIODS

_UPCOMING, _LIVE, _RESULT, _POSTPONED, _CANCELLED = PERIODS

# Normalised status categories (see ``source.categorise_status``).
FIXTURE = "fixture"
LIVE = "live"
RESULT = "result"
POSTPONED = "postponed"
CANCELLED = "cancelled"


@dataclass(frozen=True)
class Team:
    """An AFL / AFLW team."""

    id: int
    name: str
    abbreviation: str
    nickname: str = ""
    # The data source publishes no logos; kept for forward compatibility.
    logo: str = ""


@dataclass(frozen=True)
class Game:
    """A single game (fixture, live or result)."""

    id: int
    kickoff: datetime
    home: Team
    away: Team
    # Total points (goals * 6 + behinds).
    home_score: int | None
    away_score: int | None
    # "goals.behinds.total", e.g. "20.12.132".
    home_detail: str | None
    away_detail: str | None
    venue: str | None
    competition_id: int
    competition: str
    # One of fixture, live, result, postponed, cancelled.
    status: str
    # The data source's own status text (for diagnostics).
    raw_status: str = ""
    round_name: str = ""

    @property
    def live(self) -> bool:
        """True while the game is being played."""
        return self.status == LIVE


def derive_period(game: Game) -> str:
    """Map a game's status category to the period shown to the user."""
    return {
        FIXTURE: _UPCOMING,
        LIVE: _LIVE,
        RESULT: _RESULT,
        POSTPONED: _POSTPONED,
        CANCELLED: _CANCELLED,
    }.get(game.status, _UPCOMING)


@dataclass(frozen=True)
class CompSeason:
    """A season of a competition (e.g. the 2027 Toyota AFL Premiership)."""

    id: int
    competition_id: int
    year: int
    name: str


def pick_seasons(seasons: list[CompSeason], competition_id: int) -> list[CompSeason]:
    """The newest season of a competition followed by the one before it.

    Newest first. A season that has not started yet (the off-season) counts as
    the newest, so its fixtures are the "next" games while the previous season
    supplies the results. One entry per year (the highest id wins).
    """
    by_year: dict[int, CompSeason] = {}
    for season in seasons:
        if season.competition_id != competition_id:
            continue
        existing = by_year.get(season.year)
        if existing is None or season.id > existing.id:
            by_year[season.year] = season
    return [by_year[y] for y in sorted(by_year, reverse=True)[:2]]
