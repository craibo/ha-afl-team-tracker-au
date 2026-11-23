"""Config flow and options flow for AFL Team Tracker."""

from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult, OptionsFlow
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.selector import (
    SelectOptionDict,
    SelectSelector,
    SelectSelectorConfig,
)

from .client import AflTrackerClient, AflTrackerError
from .const import DOMAIN
from .coordinator import AflTrackerConfigEntry
from .models import pick_seasons


async def _fetch_team_options(
    hass: HomeAssistant, competitions: list[int]
) -> tuple[list[SelectOptionDict], dict[str, str], dict[str, int]]:
    """Fetch the teams of the competitions.

    Returns select options, team id -> name and team id -> competition id.
    Raises AflTrackerError when the data source cannot be read.
    """
    client = AflTrackerClient(async_get_clientsession(hass))
    titles = client.list_competitions()
    seasons = await client.fetch_comp_seasons()
    names: dict[int, str] = {}
    where: dict[int, int] = {}
    for competition in competitions:
        # The newest season may have no fixtures yet; fall back to the last.
        for season in pick_seasons(seasons, competition):
            games = await client.fetch_matches(season.id)
            if games:
                for game in games:
                    for team in (game.home, game.away):
                        names[team.id] = team.name
                        where.setdefault(team.id, competition)
                break
    ordered = sorted(names, key=lambda i: (names[i].casefold(), i))
    options = [
        SelectOptionDict(
            value=str(i),
            label=f"{names[i]} ({titles.get(where[i], where[i])})",
        )
        for i in ordered
    ]
    return (
        options,
        {str(i): names[i] for i in ordered},
        {str(i): where[i] for i in ordered},
    )


def _select(options: list[SelectOptionDict]) -> SelectSelector:
    return SelectSelector(SelectSelectorConfig(options=options, multiple=True))


class AflTrackerConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle the AFL Team Tracker config flow."""

    VERSION = 1

    def __init__(self) -> None:
        self._competitions: list[int] = []
        self._team_names: dict[str, str] = {}
        self._team_competitions: dict[str, int] = {}
        self._team_options: list[SelectOptionDict] = []

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: AflTrackerConfigEntry) -> OptionsFlow:
        return AflTrackerOptionsFlow()

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()

        errors: dict[str, str] = {}
        if user_input is not None:
            self._competitions = [int(c) for c in user_input["competitions"]]
            try:
                (
                    self._team_options,
                    self._team_names,
                    self._team_competitions,
                ) = await _fetch_team_options(self.hass, self._competitions)
            except AflTrackerError:
                errors["base"] = "cannot_connect"
            else:
                if self._team_options:
                    return await self.async_step_teams()
                errors["base"] = "no_teams"

        titles = AflTrackerClient(async_get_clientsession(self.hass)).list_competitions()
        options = [SelectOptionDict(value=str(c), label=t) for c, t in titles.items()]
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        "competitions", default=[str(c) for c in self._competitions]
                    ): vol.All(_select(options), vol.Length(min=1))
                }
            ),
            errors=errors,
        )

    async def async_step_teams(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        if user_input is not None:
            ids = [int(t) for t in user_input["teams"]]
            return self.async_create_entry(
                title="AFL Team Tracker",
                data={
                    "competitions": self._competitions,
                    "teams": ids,
                    "team_names": {str(i): self._team_names[str(i)] for i in ids},
                    "team_competitions": {
                        str(i): self._team_competitions[str(i)] for i in ids
                    },
                },
            )
        return self.async_show_form(
            step_id="teams",
            data_schema=vol.Schema(
                {
                    vol.Required("teams"): vol.All(
                        _select(self._team_options), vol.Length(min=1)
                    )
                }
            ),
        )


class AflTrackerOptionsFlow(OptionsFlow):
    """Edit the followed teams."""

    def __init__(self) -> None:
        # Names and competitions of the teams offered when the form was shown.
        self._team_names: dict[str, str] = {}
        self._team_competitions: dict[str, int] = {}

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        entry = self.config_entry
        stored_names = {
            **entry.data.get("team_names", {}),
            **entry.options.get("team_names", {}),
        }
        stored_comps = {
            **entry.data.get("team_competitions", {}),
            **entry.options.get("team_competitions", {}),
        }

        if user_input is not None:
            # No refetch: submitting must work even while the data source is down.
            ids = [int(t) for t in user_input["teams"]]
            names = {**stored_names, **self._team_names}
            comps = {**stored_comps, **self._team_competitions}
            return self.async_create_entry(
                data={
                    "teams": ids,
                    "team_names": {str(i): names[str(i)] for i in ids if str(i) in names},
                    "team_competitions": {
                        str(i): comps[str(i)] for i in ids if str(i) in comps
                    },
                }
            )

        errors: dict[str, str] = {}
        options: list[SelectOptionDict] = []
        try:
            (
                options,
                self._team_names,
                self._team_competitions,
            ) = await _fetch_team_options(
                self.hass, [int(c) for c in entry.data["competitions"]]
            )
        except AflTrackerError:
            # Still offer the followed teams (stored names) so they can be
            # unfollowed while the data source is unreachable.
            errors["base"] = "cannot_connect"

        current = [str(t) for t in entry.options.get("teams", entry.data["teams"])]
        # Keep currently followed teams selectable even if absent from the fetch.
        have = {o["value"] for o in options}
        for t in current:
            if t not in have:
                options.append(SelectOptionDict(value=t, label=stored_names.get(t, t)))
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required("teams", default=current): vol.All(
                        _select(options), vol.Length(min=1)
                    )
                }
            ),
            errors=errors,
        )
