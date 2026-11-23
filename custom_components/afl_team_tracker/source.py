"""Parsing of the AFL data source's JSON (``aflapi.afl.com.au/afl/v2``)."""

from __future__ import annotations

from datetime import datetime
import logging
from typing import Any

from .models import (
    CANCELLED,
    FIXTURE,
    LIVE,
    POSTPONED,
    RESULT,
    CompSeason,
    Game,
    Team,
)

_LOGGER = logging.getLogger(__name__)
_UNKNOWN_LOGGED: set[str] = set()

_RESULT_STATUSES = {"CONCLUDED", "COMPLETE", "COMPLETED", "FINAL", "FULLTIME"}
_POSTPONED_STATUSES = {"POSTPONED"}
_CANCELLED_STATUSES = {"CANCELLED", "CANCELED", "ABANDONED"}
_UPCOMING_STATUSES = {
    "SCHEDULED",
    "UNCONFIRMED_TEAMS",
    "CONFIRMED_TEAMS",
    "TEAMS_CONFIRMED",
    "PRE_GAME",
    "PREGAME",
    "UPCOMING",
}
_LIVE_STATUSES = {"LIVE", "IN_PROGRESS", "INPROGRESS"}
# Substrings that mark a status the integration does not know as in play.
_LIVE_HINTS = ("LIVE", "PROGRESS", "QUARTER", "HALF", "TIME")
# Matches the data source lists before the teams are known (e.g. finals).
_SKIPPED_STATUSES = {"PLACEHOLDER"}


class ParseError(Exception):
    """Raised when the data source's JSON is not in the expected shape."""


def categorise_status(raw: str) -> str:
    """Map the data source's match status to a status category.

    ``CONCLUDED`` and ``SCHEDULED`` were observed on the real API. The live and
    postponed statuses could not be sampled out of season, so known names are
    mapped and anything unknown that looks in play is treated as live;
    everything else is an upcoming fixture.
    """
    status = raw.strip().upper().replace(" ", "_").replace("-", "_")
    if status in _RESULT_STATUSES:
        return RESULT
    if status in _POSTPONED_STATUSES:
        return POSTPONED
    if status in _CANCELLED_STATUSES:
        return CANCELLED
    if status in _LIVE_STATUSES:
        return LIVE
    if status in _UPCOMING_STATUSES or not status:
        return FIXTURE
    if any(hint in status for hint in _LIVE_HINTS):
        category = LIVE
    else:
        category = FIXTURE
    if raw not in _UNKNOWN_LOGGED:
        _UNKNOWN_LOGGED.add(raw)
        _LOGGER.debug("Unknown match status %r, treating it as %s", raw, category)
    return category


def _parse_time(value: Any) -> datetime:
    if not isinstance(value, str):
        raise ParseError(f"bad start time {value!r}")
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError as err:
        raise ParseError(f"bad start time {value!r}") from err
    if parsed.tzinfo is None:
        raise ParseError(f"start time without a time zone {value!r}")
    return parsed


def _parse_team(side: Any) -> Team | None:
    team = side.get("team") if isinstance(side, dict) else None
    if not isinstance(team, dict) or not isinstance(team.get("id"), int):
        return None
    name = team.get("name")
    if not isinstance(name, str) or not name:
        return None
    abbreviation = team.get("abbreviation")
    nickname = team.get("nickname")
    return Team(
        id=team["id"],
        name=name,
        abbreviation=abbreviation if isinstance(abbreviation, str) else "",
        nickname=nickname if isinstance(nickname, str) else "",
    )


def _parse_score(side: Any) -> tuple[int | None, str | None]:
    score = side.get("score") if isinstance(side, dict) else None
    if not isinstance(score, dict):
        return None, None
    total = score.get("totalScore")
    if not isinstance(total, int):
        return None, None
    goals, behinds = score.get("goals"), score.get("behinds")
    if isinstance(goals, int) and isinstance(behinds, int):
        return total, f"{goals}.{behinds}.{total}"
    return total, None


def parse_match(item: Any) -> Game | None:
    """Parse one match; None for a match without two known teams."""
    if not isinstance(item, dict) or not isinstance(item.get("id"), int):
        raise ParseError("match without an id")
    raw_status = item.get("status")
    raw_status = raw_status if isinstance(raw_status, str) else ""
    if raw_status.strip().upper() in _SKIPPED_STATUSES:
        return None
    home = _parse_team(item.get("home"))
    away = _parse_team(item.get("away"))
    if home is None or away is None:
        return None
    home_score, home_detail = _parse_score(item.get("home"))
    away_score, away_detail = _parse_score(item.get("away"))
    venue = item.get("venue")
    venue_name = venue.get("name") if isinstance(venue, dict) else None
    comp_season = item.get("compSeason")
    comp = comp_season.get("competition") if isinstance(comp_season, dict) else None
    comp = comp if isinstance(comp, dict) else {}
    round_info = item.get("round")
    round_name = round_info.get("name") if isinstance(round_info, dict) else ""
    return Game(
        id=item["id"],
        kickoff=_parse_time(item.get("utcStartTime")),
        home=home,
        away=away,
        home_score=home_score,
        away_score=away_score,
        home_detail=home_detail,
        away_detail=away_detail,
        venue=venue_name if isinstance(venue_name, str) and venue_name else None,
        competition_id=comp.get("id") if isinstance(comp.get("id"), int) else 0,
        competition=comp.get("name") if isinstance(comp.get("name"), str) else "",
        status=categorise_status(raw_status),
        raw_status=raw_status,
        round_name=round_name if isinstance(round_name, str) else "",
    )


def num_pages(payload: Any) -> int:
    """Number of result pages (1 when the payload carries no pagination)."""
    try:
        pages = payload["meta"]["pagination"]["numPages"]
    except (KeyError, TypeError):
        return 1
    return pages if isinstance(pages, int) and pages > 0 else 1


def parse_matches(payload: Any) -> list[Game]:
    """Parse a ``/matches`` response page."""
    items = payload.get("matches") if isinstance(payload, dict) else None
    if not isinstance(items, list):
        raise ParseError("no matches list")
    games = (parse_match(item) for item in items)
    return [g for g in games if g is not None]


def parse_comp_seasons(payload: Any) -> list[CompSeason]:
    """Parse a ``/compseasons`` response page."""
    items = payload.get("compSeasons") if isinstance(payload, dict) else None
    if not isinstance(items, list):
        raise ParseError("no compSeasons list")
    seasons: list[CompSeason] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        comp = item.get("competition")
        season = item.get("season")
        year = season.get("year") if isinstance(season, dict) else None
        comp_id = comp.get("id") if isinstance(comp, dict) else None
        if isinstance(item.get("id"), int) and isinstance(year, int) and isinstance(
            comp_id, int
        ):
            name = item.get("name")
            seasons.append(
                CompSeason(item["id"], comp_id, year, name if isinstance(name, str) else "")
            )
    return seasons


def parse_ladder(payload: Any) -> dict[int, int]:
    """Parse a ladder response into team id -> position."""
    ladders = payload.get("ladders") if isinstance(payload, dict) else None
    if not isinstance(ladders, list):
        raise ParseError("no ladders list")
    positions: dict[int, int] = {}
    for ladder in ladders:
        entries = ladder.get("entries") if isinstance(ladder, dict) else None
        for entry in entries if isinstance(entries, list) else []:
            team = entry.get("team") if isinstance(entry, dict) else None
            team_id = team.get("id") if isinstance(team, dict) else None
            position = entry.get("position")
            if isinstance(team_id, int) and isinstance(position, int):
                positions[team_id] = position
    return positions
