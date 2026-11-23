"""Update coordinator with adaptive polling."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable
from datetime import datetime, timedelta
import logging
from typing import TypeVar

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt as dt_util

from .client import AflTrackerClient, AflTrackerError
from .const import DOMAIN
from .models import FIXTURE, CompSeason, Game, Team, pick_seasons
from .selection import TeamGames, merge_games, select_team_games

_LOGGER = logging.getLogger(__name__)
_T = TypeVar("_T")

LIVE_INTERVAL = timedelta(seconds=60)
SOON_INTERVAL = timedelta(minutes=15)
IDLE_INTERVAL = timedelta(hours=6)
SOON_WINDOW = timedelta(hours=2)
MAX_CONSECUTIVE_FAILURES = 3
RETRY_INTERVAL = timedelta(minutes=5)
MAX_RETRY_INTERVAL = timedelta(minutes=40)
MIN_INTERVAL = timedelta(seconds=60)
# A game lasts about two and a half hours; allow for delays and breaks.
IN_PLAY_WINDOW = timedelta(hours=4)
# The season list is large and changes a few times a year.
SEASONS_INTERVAL = timedelta(hours=24)
SEASONS_RETRY = timedelta(minutes=10)
# The previous season is over; its games are refreshed rarely.
PREVIOUS_INTERVAL = timedelta(hours=6)
# Ladders change at most once a match day.
LADDER_INTERVAL = timedelta(hours=1)
LADDER_RETRY = timedelta(minutes=10)
# Overall cap (seconds) per ladder request, so it never holds up a refresh.
LADDER_TIMEOUT = 8

type AflTrackerConfigEntry = ConfigEntry[AflTrackerCoordinator]


def entry_teams(entry: ConfigEntry) -> list[int]:
    """Return followed team ids; options override data."""
    merged = {**entry.data, **entry.options}
    return [int(t) for t in merged.get("teams", [])]


def entry_team_competitions(entry: ConfigEntry) -> dict[int, int]:
    """Return followed team id -> competition id; options override data."""
    merged = {**entry.data, **entry.options}
    return {int(t): int(c) for t, c in merged.get("team_competitions", {}).items()}


def is_in_play(game: Game, now: datetime) -> bool:
    """A fixture past its start (by up to 4 h) that is not yet marked finished.

    The status can take a while to flip to live; such a game must
    be polled at the live rate rather than ignored.
    """
    return (
        game.status == FIXTURE and now - IN_PLAY_WINDOW <= game.kickoff <= now
    )


def compute_interval(games: list[Game], now: datetime) -> timedelta:
    """Choose the poll interval from the followed games."""
    if any(g.live or is_in_play(g, now) for g in games):
        return LIVE_INTERVAL
    upcoming = [g.kickoff for g in games if g.status == FIXTURE and g.kickoff > now]
    if not upcoming:
        return IDLE_INTERVAL
    earliest = min(upcoming)
    if earliest <= now + SOON_WINDOW:
        return SOON_INTERVAL
    # Wake up when the 2 h window opens rather than overshooting it.
    wait = earliest - SOON_WINDOW - now
    return max(MIN_INTERVAL, min(IDLE_INTERVAL, wait))


def retry_interval(failures: int, computed: timedelta) -> timedelta:
    """Retry delay after ``failures`` consecutive failures.

    5 min for failures 1-3, then 10, 20 and 40 min; never longer than the
    interval that would be used without errors.
    """
    steps = max(0, failures - MAX_CONSECUTIVE_FAILURES)
    backoff = min(RETRY_INTERVAL * (2**steps), MAX_RETRY_INTERVAL)
    return min(backoff, computed)


class AflTrackerCoordinator(DataUpdateCoordinator[dict[int, TeamGames]]):
    """Polls the followed teams' games and selects the ones to show."""

    config_entry: ConfigEntry

    def __init__(
        self, hass: HomeAssistant, entry: AflTrackerConfigEntry, client: AflTrackerClient
    ) -> None:
        super().__init__(
            hass,
            _LOGGER,
            config_entry=entry,
            name=DOMAIN,
            update_interval=IDLE_INTERVAL,
        )
        self.client = client
        self.games: list[Game] = []
        self._failures = 0
        # All seasons of all competitions, and when to refetch them.
        self._seasons: list[CompSeason] = []
        self._seasons_next: datetime | None = None
        # Per team: last good games of the current / previous season.
        self._current_games: dict[int, list[Game]] = {}
        self._previous_games: dict[int, list[Game]] = {}
        self._previous_next: dict[int, datetime] = {}
        self._team_failures: dict[int, int] = {}
        # Ladder positions per competition: competition id -> team id -> position.
        self.standings: dict[int, dict[int, int]] = {}
        self._ladder_next: dict[int, datetime] = {}

    def rank(self, competition_id: int, team: Team) -> int | None:
        """A team's ladder position in the game's competition, if known."""
        return self.standings.get(competition_id, {}).get(team.id)

    async def _refresh_seasons(self, now: datetime) -> None:
        """Refetch the season list when due; keep the old list on failure."""
        if self._seasons_next is not None and now < self._seasons_next:
            return
        try:
            self._seasons = await self.client.fetch_comp_seasons()
        except AflTrackerError as err:
            _LOGGER.debug("Season list unavailable, keeping the last: %s", err)
            self._seasons_next = now + SEASONS_RETRY
            if not self._seasons:
                raise
        else:
            self._seasons_next = now + SEASONS_INTERVAL

    async def _capped(self, fetch: Awaitable[_T]) -> _T:
        async with asyncio.timeout(LADDER_TIMEOUT):
            return await fetch

    async def _refresh_ladders(self, competitions: list[int], now: datetime) -> None:
        """Fetch due ladders concurrently.

        Never fatal: a failed fetch keeps the last ladder and is retried after
        ``LADDER_RETRY``. Before round 1 the newest season has no ladder, so the
        previous season's final ladder is used.
        """
        due = [
            c for c in competitions
            if (self._ladder_next.get(c) is None or now >= self._ladder_next[c])
        ]
        if not due:
            return

        async def one(competition: int) -> dict[int, int]:
            for season in pick_seasons(self._seasons, competition):
                ladder = await self.client.fetch_ladder(season.id)
                if ladder:
                    return ladder
            return {}

        results = await asyncio.gather(
            *(self._capped(one(c)) for c in due), return_exceptions=True
        )
        for competition, result in zip(due, results, strict=True):
            if isinstance(result, BaseException):
                if not isinstance(result, Exception):
                    raise result  # cancellation and the like must propagate
                _LOGGER.debug(
                    "Ladder for competition %s unavailable, keeping the last: %r",
                    competition,
                    result,
                )
                self._ladder_next[competition] = now + LADDER_RETRY
                continue
            self.standings[competition] = result
            self._ladder_next[competition] = now + LADDER_INTERVAL

    def _followed(self, games: list[Game]) -> list[Game]:
        teams = entry_teams(self.config_entry)
        return [g for g in games if g.home.id in teams or g.away.id in teams]

    async def _fetch_team(self, team_id: int, competition: int, now: datetime) -> None:
        seasons = pick_seasons(self._seasons, competition)
        if not seasons:
            raise AflTrackerError(f"No season found for competition {competition}")
        self._current_games[team_id] = await self.client.fetch_matches(
            seasons[0].id, team_id
        )
        if len(seasons) > 1 and (
            team_id not in self._previous_next or now >= self._previous_next[team_id]
        ):
            try:
                self._previous_games[team_id] = await self.client.fetch_matches(
                    seasons[1].id, team_id
                )
            except AflTrackerError as err:
                # Old results: not worth failing the refresh for.
                _LOGGER.debug("Previous season of team %s unavailable: %s", team_id, err)
                self._previous_next[team_id] = now + SEASONS_RETRY
            else:
                self._previous_next[team_id] = now + PREVIOUS_INTERVAL

    async def _async_update_data(self) -> dict[int, TeamGames]:
        now = dt_util.utcnow()
        team_competitions = entry_team_competitions(self.config_entry)
        teams = entry_teams(self.config_entry)
        errors: dict[int, AflTrackerError] = {}

        try:
            await self._refresh_seasons(now)
        except AflTrackerError as err:
            return self._all_failed(err, now)

        for team_id in teams:
            competition = team_competitions.get(team_id)
            if competition is None:
                continue
            try:
                await self._fetch_team(team_id, competition, now)
            except AflTrackerError as err:
                errors[team_id] = err
                self._team_failures[team_id] = self._team_failures.get(team_id, 0) + 1
                _LOGGER.warning(
                    "Fetch for team %s failed (%s in a row), keeping its last games: %s",
                    team_id,
                    self._team_failures[team_id],
                    err,
                )
            else:
                self._team_failures[team_id] = 0

        if teams and len(errors) == len(teams):
            return self._all_failed(next(iter(errors.values())), now)
        self._failures = 0

        self.games = merge_games(
            *self._current_games.values(), *self._previous_games.values()
        )
        computed = compute_interval(self._followed(self.games), now)
        if errors:
            worst = max(self._team_failures[t] for t in errors)
            self.update_interval = retry_interval(worst, computed)
            for team_id, err in errors.items():
                if (
                    self._team_failures[team_id] >= MAX_CONSECUTIVE_FAILURES
                    and team_id not in self._current_games
                ):
                    raise UpdateFailed(f"team {team_id}: {err}") from err
        else:
            self.update_interval = computed

        data = {t: select_team_games(self.games, t, now) for t in teams}
        # Last, so a slow ladder never holds up the games.
        await self._refresh_ladders(sorted(set(team_competitions.values())), now)
        return data

    def _all_failed(self, err: AflTrackerError, now: datetime) -> dict[int, TeamGames]:
        self._failures += 1
        self.update_interval = retry_interval(
            self._failures, compute_interval(self._followed(self.games), now)
        )
        if self.data is None or self._failures >= MAX_CONSECUTIVE_FAILURES:
            raise UpdateFailed(str(err)) from err
        _LOGGER.warning(
            "All fetches failed (%s/%s), keeping last data",
            self._failures,
            MAX_CONSECUTIVE_FAILURES,
        )
        return self.data

