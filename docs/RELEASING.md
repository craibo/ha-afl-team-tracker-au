# Releasing

Releases are cut by pushing a `v*` tag; `.github/workflows/release.yml` checks the tag against the manifest version, runs the tests and publishes a GitHub release containing `afl_team_tracker.zip` (the contents of `custom_components/afl_team_tracker`). The zip is a convenience download only: HACS installs from the repository at the tag.

## Steps

1. Make sure `main` is green (CI: tests, card, hacs, hassfest).
2. Check `custom_components/afl_team_tracker/manifest.json` `version` matches the tag you are about to create; bump it first if not, and bump the version in `USER_AGENT` in `custom_components/afl_team_tracker/const.py` together with it (a test fails if they differ).
3. Tag and push: `git tag v0.1.0 && git push origin v0.1.0`.
4. Confirm the Release workflow succeeded and the release has `afl_team_tracker.zip`.
5. In Home Assistant, HACS > Custom repositories > add `https://github.com/craibo/ha-afl-team-tracker-au` as type Integration, download it, restart HA, then add **AFL Team Tracker**.

## Verifying live behaviour (still to do in season)

The live match statuses could not be sampled in the off-season. During the first live match of 2027, poll the matches request made by `custom_components/afl_team_tracker/client.py` for a followed team every few minutes, record the match `status` values and whether a running `score` is present, save a trimmed fixture under `tests/fixtures/` and adjust `categorise_status` in `custom_components/afl_team_tracker/parsing.py`.
