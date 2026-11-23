# Data source notes

Sampled on 2026-11-23. All endpoints are plain GETs under `https://aflapi.afl.com.au/afl/v2`; the afl.com.au fixture page is rendered client-side and carries no data itself (its page config points at this API).

| Need | Endpoint | Notes |
|---|---|---|
| Seasons | `/compseasons?pageSize=100` | One page, 99 entries. The `competitionId` filter is **not** honoured: filter on `competition.id` client-side. 2026 Premiership is id 85, 2027 Premiership 102, 2026 AFLW 96. |
| Matches | `/matches?compSeasonId=<id>&teamId=<team>&pageSize=100` | `teamId` is honoured (`teamIds` and `roundId` are not). `pageSize=100` is honoured. ~23 matches per team per season. |
| Ladder | `/compseasons/<id>/ladders` | `ladders[].entries[].position` and `.team.id`. HTTP 404 before round 1. |
| Competitions | `/competitions?pageSize=50` | 1 Toyota AFL Premiership, 3 NAB AFLW, 2 AFL Preseason, 7 VFL, 11 VFLW, ... |

Match fields: `id`, `compSeason`, `round{name,roundNumber}`, `home`/`away` (`team{id,name,abbreviation,nickname}`, `score{goals,behinds,totalScore}` once played), `venue{name,timezone}`, `utcStartTime` (`+0000` offset), `status`. Seen statuses: `SCHEDULED`, `CONCLUDED`, `PLACEHOLDER` (finals before the teams are known; no teams, skipped). No logos, no live minute or quarter.

Site pages: `https://www.afl.com.au/afl/matches/<id>` and `https://www.afl.com.au/teams/<slug>` (for example `sydney-swans`) exist and show the match / team.

Live scores and the minute come from `api.afl.com.au/cfs/afl` which needs a token exchange; deliberately not used.

## Logos

The API has no logo fields (`/teams`, `/matches` and `/clubs` were checked). The website draws club logos from the SVG sprite `https://www.afl.com.au/resources/<version>/i/svg-output/icons.svg`: one `<symbol id="icn-aflc-<abbr>">` per club (plus `-light` and `-flag` variants), where `<abbr>` is the API's team abbreviation in lower case. The sprite has no CORS header and its path changes with each site release, so a card cannot load it directly; the logos are extracted by `scripts/extract_logos.py` and bundled instead. The `/resources/club-watermarks/...` PNGs are faded background graphics, not logos.
