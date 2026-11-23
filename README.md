# AFL Team Tracker for Home Assistant

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)
[![hacs][hacsbadge]][hacs]

An **unofficial** Home Assistant integration that follows AFL and AFLW teams. Each team gets a device with its current, next and previous five games, with ladder positions, plus two bundled Lovelace cards: a game card and a team card.

---

## Support this project

[![Sponsor me on GitHub](https://img.shields.io/badge/Sponsor-craibo%20on%20GitHub-blue.svg?logo=github)](https://github.com/sponsors/craibo)
[![Donate with PayPal](https://img.shields.io/badge/Donate-PayPal-blue.svg?logo=paypal)](https://paypal.me/craibo?country.x=AU&locale.x=en_AU)

---

## Features

- **Follow your teams**: pick competitions, then the teams you care about; each team becomes a Home Assistant device
- **Current, next and previous five games**: opposition, start date and time, venue, round, score (with goals and behinds) and period (Upcoming, Live, Result, Postponed, Cancelled)
- **Ladder positions**: shown after team names, from the competition's current ladder (the last ladder of the previous season until round 1 is played)
- **Two bundled Lovelace cards**: a game card and a team card (current or next game plus the previous five results), with visual editors and no separate download
- **Club logos**: bundled with the integration for all 18 AFL clubs (also used for the AFLW teams); see [Club logos](#club-logos)
- **Light on the data source**: adaptive polling, from every 60 seconds while a followed game is on to every 6 hours when nothing is (see [Polling and data usage](#polling-and-data-usage))
- **UI-first setup**: everything is configured from Home Assistant; no YAML needed

## Quick Start

Requires Home Assistant 2024.11 or newer.

### Installation via HACS (Recommended)

1. Install [HACS](https://hacs.xyz/docs/use/) if you have not already.
2. [![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=craibo&repository=ha-afl-team-tracker-au&category=integration)
   (or in HACS open the menu > **Custom repositories**, add `https://github.com/craibo/ha-afl-team-tracker-au` with type **Integration**)
3. Press the **Download** button.
4. Restart Home Assistant.
5. [![Open your Home Assistant instance and start setting up a new integration.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=afl_team_tracker)

### Manual installation

1. Download `afl_team_tracker.zip` from the [latest release][releases], or copy the `custom_components/afl_team_tracker` folder from this repository.
2. Put the `afl_team_tracker` folder in your Home Assistant `custom_components` directory.
3. Restart Home Assistant.

### Updating

HACS shows a new version when a [release][releases] is published. Update it there, restart Home Assistant, then hard-refresh your browser (Ctrl+Shift+R) so the cards load the new version.

## Setup

1. Go to **Settings > Devices & services > Add integration** and choose **AFL Team Tracker**.
2. Pick the competitions to follow: **Toyota AFL Premiership** and/or **NAB AFLW**.
3. Pick the teams to follow (the list is built from the season's fixtures).
4. To change teams later, open the integration and choose **Configure**.

Each followed team becomes a device. The integration follows the newest season of the competition (during the off-season that is the upcoming one) and uses the season before it for past results.

## Entities

Seven sensors per team:

| Entity | State |
|---|---|
| Current game | `Live` while a followed game is being played, otherwise "No game in progress" |
| Next game | Start date and time (timestamp) |
| Previous game 1 to 5 | Result from the team's side, for example `W 132–69` (1 is the most recent) |

Current game and Previous game 1 to 5 use the Australian football icon. Next game keeps Home Assistant's default clock icon (it is a timestamp sensor).

Attributes on each (empty for Current game when nothing is live): `opposition`, `home_away`, `kickoff`, `venue`, `round`, `competition`, `home_team`, `away_team`, `home_abbr`, `away_abbr` (for example `SYD`), `home_score`, `away_score` (total points), `home_score_detail`, `away_score_detail` (goals.behinds.total, for example `20.12.132`), `period`, `status`, `match_url`, `logos` (`home` and `away`: path of the bundled logo, for example `/afl_team_tracker/logos/syd.svg`, or empty when a team has none), `home_rank` and `away_rank` (ladder positions, or none when unknown) and `home_team_url` and `away_team_url` (the team's page on afl.com.au, or none when unknown).

## Game card

The cards are bundled with the integration, which loads them into the frontend as an extra JavaScript module; no manual resource setup is needed (reload the browser after installing). Add the card from the card picker (it has a visual editor) or in YAML:

```yaml
type: custom:afl-tracker-game-card
entity: sensor.sydney_swans_next_game
```

It shows both teams, each name followed by the team's ladder position in lighter text when known (for example `Sydney Swans 3rd`), and:

- **Upcoming:** start date and time, with the venue (when known) under the time.
- **Live:** current score and a `Live` badge.
- **Final:** the final score, with goals and behinds under it.

Each team is shown with its club logo on a light round backdrop (so dark crests stay legible in dark themes). A team without a logo is shown as a round badge with its abbreviation (for example `SYD`).

When the card shows a current (live) or previous game, clicking the game block opens the match page on afl.com.au in a new browser tab. The next game is not clickable.

**Long press:** pressing and holding anywhere on the card opens Home Assistant's more-info dialog for the card's sensor.

Current game is empty when nothing is live, so use a Next game or Previous game sensor for a card that always shows something.

### Markdown card alternative

```yaml
type: markdown
content: >
  {% if has_value('sensor.sydney_swans_next_game') %}
  {% set g = states.sensor.sydney_swans_next_game %}
  **{{ g.attributes.home_team }}** v **{{ g.attributes.away_team }}**
  {{ as_timestamp(g.state) | timestamp_custom('%a %d %b, %H:%M') }}
  at {{ g.attributes.venue }}
  {% else %}
  No game scheduled
  {% endif %}
```

Replace `sensor.sydney_swans_next_game` with your own entity ID.

## Team card

One card per team: the current game if one is live, otherwise the next game, with the team's previous five results listed underneath. It ships in the same bundle as the game card. Add it from the card picker or in YAML:

```yaml
type: custom:afl-tracker-team-card
title: Sydney Swans         # optional, defaults to the team name
show_header: true           # optional, set false to hide the header
current: sensor.sydney_swans_current_game
next: sensor.sydney_swans_next_game
previous:
  - sensor.sydney_swans_previous_game_1
  - sensor.sydney_swans_previous_game_2
  - sensor.sydney_swans_previous_game_3
  - sensor.sydney_swans_previous_game_4
  - sensor.sydney_swans_previous_game_5
```

At least one of `next`, `current` or a non-empty `previous` is required; entries in `previous` beyond five are ignored. Each previous result shows the date, the opposition, its ladder position and the venue in brackets (for example `Geelong Cats 4th (MCG)`), and the score coloured green for a win, red for a loss and amber for a draw; hovering the score shows the goals and behinds. Slots with no game are left out. With nothing live or scheduled the top block reads "No game". Ranks use English ordinals (1st, 2nd, 3rd) when Home Assistant's language is English and `#1`, `#2` otherwise.

**Header:** the card starts with a header showing the followed team's name. Set `title` to use your own text instead, or `show_header: false` to hide it.

**Clicks:** everything opens in a new tab on afl.com.au. In the top block, the team name opens the team page (men's competition only) and the middle opens the game page; a previous-result row opens its match. Anything without a known link stays plain text.

**Long press:** opens the more-info dialog for the current game sensor while a game is live, otherwise for the next game sensor.

**Visual editor:** pick any one of the team's game sensors and the editor fills in the other six from the entity-id naming (`..._current_game`, `..._next_game`, `..._previous_game_1` to `5`). If you have renamed the entities, set the entity ids explicitly in YAML as above.

## Club logos

The logos of the 18 AFL clubs, plus the AFLW international sides (Australia, Ireland) and the All Stars sides, are bundled in `custom_components/afl_team_tracker/www/logos/` and served by the integration at `/afl_team_tracker/logos/<abbreviation>.svg` (for example `syd.svg`; the abbreviation is the data source's team abbreviation in lower case). AFLW teams use the same club logos as their AFL club. They appear in the `logos` attribute and on the cards.

The files were extracted from the SVG sprite that afl.com.au itself uses (`scripts/extract_logos.py` repeats this for a new sprite). **The logos are trademarks and artwork of the AFL and its clubs, are included only to identify the teams, and are not covered by this project's MIT licence.** If you are a rights holder and want a logo removed, please open an issue.

## Polling and data usage

Polling is deliberately light: every 60 seconds only while a followed game is live, every 15 minutes when a followed game starts within 2 hours, and every 6 hours otherwise (shortened so the integration wakes no later than 2 hours before the next start). A followed game that is past its start time but not yet flagged live is also polled every 60 seconds, for up to 4 hours, so the start of a match is not missed.

Each refresh makes one request per followed team for the newest season (about 25 matches). The previous season's games are refetched every 6 hours, the season list once a day and each competition's ladder at most once an hour; a failed ladder request never affects the entities. When every request fails, the integration retries every 5 minutes; entities go unavailable only after 3 consecutive failures, and after that the retry delay doubles (10, 20, then 40 minutes), never waiting longer than the normal polling interval.

## Known limitations

- **Live information is limited.** The data source's match list carries the status and, for finished games, the score, but the live minute, quarter and running score come from a separate feed that this integration does not use. While a game is live the card shows `Live`, and a running score only when the match list includes one. The live status names could not be sampled out of season: `SCHEDULED`, `PLACEHOLDER` and `CONCLUDED` were observed, `LIVE`, `IN_PROGRESS`, `POSTPONED` and `CANCELLED` are assumed, and an unknown status that looks in play (it contains LIVE, PROGRESS, QUARTER, HALF or TIME) is treated as live. If you see live games not detected, please open an issue with the status shown in the `status` attribute's raw value (enable debug logging for `custom_components.afl_team_tracker`).
- **Logos are static**: the data source's API publishes no logo URLs, so the logos are bundled files and will not update if a club changes its logo until they are re-extracted (see [Club logos](#club-logos)).
- **AFLW links**: match pages for AFLW use `afl.com.au/aflw/matches/<id>`, which is the expected pattern but was not verified; AFLW team pages are not linked.
- A postponed or cancelled game is not shown in any sensor; Next game skips to the next playable fixture. Finals fixtures appear once their teams are known.
- Only the Toyota AFL Premiership and NAB AFLW are offered. Other competitions on the data source (VFL, Preseason and so on) can be added on request.
- Relies on an undocumented API and may stop working if it changes.

## Support

- **Issues**: report bugs or request features via [GitHub Issues](https://github.com/craibo/ha-afl-team-tracker-au/issues). Please include your Home Assistant and integration versions and any relevant log lines.
- **Releases**: [release notes and downloads][releases]

## Development

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements_test.txt
.venv/bin/pytest
```

Card (TypeScript and Lit, in `card/`):

```bash
cd card
npm ci
npm run typecheck && npm test
npm run build   # writes custom_components/afl_team_tracker/www/afl-tracker-cards.js
```

The built bundle is committed, and CI fails if it is out of date. Release steps are in [docs/RELEASING.md](docs/RELEASING.md); notes on the data source are in [docs/DATA_SOURCE.md](docs/DATA_SOURCE.md).

## Licence

Released under the [MIT License](LICENSE).

The integration uses its own original icon (`custom_components/afl_team_tracker/brand/`, generated by `scripts/make_icon.py`), which is covered by the same licence. The club logos in `custom_components/afl_team_tracker/www/logos/` are the exception: see [Club logos](#club-logos).

## Data source and terms

The integration reads fixtures, results and ladders from the JSON API (`aflapi.afl.com.au`) that the [afl.com.au](https://www.afl.com.au) website itself uses to show its fixture, ladder and match pages. The API is undocumented and not offered as a public product.

- This project is unofficial and is not affiliated with, endorsed by or connected to the AFL or any club.
- AFL names and club names belong to their owners; the integration only displays the data it reads.
- The website's terms of use may restrict automated access to its data. You use this integration at your own risk and must check and accept those terms yourself before using it.
- The API may change or block access at any time, which would break the integration.

[commits-shield]: https://img.shields.io/github/commit-activity/y/craibo/ha-afl-team-tracker-au.svg?style=for-the-badge
[commits]: https://github.com/craibo/ha-afl-team-tracker-au/commits/main
[hacs]: https://github.com/hacs/integration
[hacsbadge]: https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge
[license-shield]: https://img.shields.io/github/license/craibo/ha-afl-team-tracker-au.svg?style=for-the-badge
[releases-shield]: https://img.shields.io/github/release/craibo/ha-afl-team-tracker-au.svg?style=for-the-badge
[releases]: https://github.com/craibo/ha-afl-team-tracker-au/releases
