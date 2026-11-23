"""Scaffold tests."""

import json
from pathlib import Path

ROOT = Path(__file__).parent.parent
MANIFEST = ROOT / "custom_components" / "afl_team_tracker" / "manifest.json"


def test_manifest_domain():
    assert json.loads(MANIFEST.read_text())["domain"] == "afl_team_tracker"
    assert json.loads((ROOT / "hacs.json").read_text())


def test_user_agent_version_matches_manifest():
    from custom_components.afl_team_tracker.const import USER_AGENT

    version = json.loads(MANIFEST.read_text())["version"]
    assert USER_AGENT.startswith(f"ha-afl-team-tracker-au/{version} ")
