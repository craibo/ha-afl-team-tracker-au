"""HTTP client for the AFL data source (JSON API)."""

from __future__ import annotations

import asyncio
from typing import Any

import aiohttp

from .const import USER_AGENT
from .models import CompSeason, Game
from .source import (
    ParseError,
    num_pages,
    parse_comp_seasons,
    parse_ladder,
    parse_matches,
)

API_URL = "https://aflapi.afl.com.au/afl/v2"
REQUEST_TIMEOUT = 15
PAGE_SIZE = 100
# Safety net against a response that never ends its pagination.
MAX_PAGES = 10

# competition id -> title; ids verified against the live API.
COMPETITIONS: dict[int, str] = {
    1: "Toyota AFL Premiership",
    3: "NAB AFLW",
}


class AflTrackerError(Exception):
    """Raised when data cannot be fetched or understood."""


class AflTrackerClient:
    """Fetches and parses seasons, matches and ladders."""

    def __init__(self, session: aiohttp.ClientSession) -> None:
        self._session = session

    def list_competitions(self) -> dict[int, str]:
        """Return the competitions offered by the integration (id -> title)."""
        return dict(COMPETITIONS)

    async def fetch_comp_seasons(self) -> list[CompSeason]:
        """Fetch every season of every competition."""
        seasons: list[CompSeason] = []
        for payload in await self._get_pages("/compseasons", {}):
            seasons.extend(self._parse(parse_comp_seasons, payload, "/compseasons"))
        return seasons

    async def fetch_matches(
        self, comp_season_id: int, team_id: int | None = None
    ) -> list[Game]:
        """Fetch the matches of a season, optionally only those of one team."""
        params: dict[str, Any] = {"compSeasonId": comp_season_id}
        if team_id is not None:
            params["teamId"] = team_id
        games: list[Game] = []
        for payload in await self._get_pages("/matches", params):
            games.extend(self._parse(parse_matches, payload, "/matches"))
        return games

    async def fetch_ladder(self, comp_season_id: int) -> dict[int, int]:
        """Fetch a season's ladder (team id -> position).

        Empty when the season has no ladder yet (HTTP 404, e.g. before round 1).
        """
        path = f"/compseasons/{comp_season_id}/ladders"
        payload = await self._get_json(path, {}, missing_ok=True)
        if payload is None:
            return {}
        return self._parse(parse_ladder, payload, path)

    @staticmethod
    def _parse(parser: Any, payload: Any, what: str) -> Any:
        try:
            return parser(payload)
        except ParseError as err:
            raise AflTrackerError(f"Unexpected data from {what}: {err}") from err

    async def _get_pages(self, path: str, params: dict[str, Any]) -> list[Any]:
        pages: list[Any] = []
        page = 0
        while True:
            payload = await self._get_json(
                path, {**params, "pageSize": PAGE_SIZE, "page": page}
            )
            assert payload is not None
            pages.append(payload)
            page += 1
            if page >= min(num_pages(payload), MAX_PAGES):
                return pages

    async def _get_json(
        self, path: str, params: dict[str, Any], *, missing_ok: bool = False
    ) -> Any:
        """GET JSON; any failure is an ``AflTrackerError``.

        With ``missing_ok``, HTTP 404 returns None instead of raising.
        """
        url = f"{API_URL}{path}"
        try:
            async with asyncio.timeout(REQUEST_TIMEOUT):
                async with self._session.get(
                    url, params=params, headers={"User-Agent": USER_AGENT}
                ) as resp:
                    if missing_ok and resp.status == 404:
                        return None
                    if resp.status != 200:
                        raise AflTrackerError(f"{url} returned HTTP {resp.status}")
                    return await resp.json(content_type=None)
        except TimeoutError as err:
            raise AflTrackerError(f"Timed out fetching {url}") from err
        except (aiohttp.ClientError, ValueError) as err:
            raise AflTrackerError(f"Error fetching {url}: {err}") from err
