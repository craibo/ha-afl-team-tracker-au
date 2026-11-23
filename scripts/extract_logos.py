"""Extract the club logos from the data source website's SVG sprite.

Usage (from the repository root):

    curl -o /tmp/icons.svg https://www.afl.com.au/resources/<version>/i/svg-output/icons.svg
    python scripts/extract_logos.py /tmp/icons.svg

Writes one standalone SVG per club to custom_components/afl_team_tracker/www/logos/
named after the team abbreviation used by the data source's API, lower case
(``syd.svg``). The logos are the property of the AFL and its clubs (see the README).
Only the abbreviations in ``ABBREVIATIONS`` are extracted; update ``LOGOS`` in
custom_components/afl_team_tracker/const.py when you change it (a test checks they agree).
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

OUT = (
    Path(__file__).resolve().parent.parent
    / "custom_components"
    / "afl_team_tracker"
    / "www"
    / "logos"
)
# AFL, AFLW and representative sides, as named by the API's team abbreviations.
ABBREVIATIONS = (
    "adel alls aus bl carl coll ess fre gcfc geel gws haw ias irl "
    "melb nmfc port rich stk syd wb wce"
).split()
UNSAFE = re.compile(r"<script|\son\w+\s*=|javascript:|<foreignObject|<iframe", re.I)


def extract(sprite: str, abbreviation: str) -> str:
    """Return the standalone SVG for one club symbol."""
    match = re.search(
        rf'<symbol([^>]*)\sid="icn-aflc-{abbreviation}"([^>]*)>(.*?)</symbol>',
        sprite,
        re.S,
    )
    if match is None:
        raise SystemExit(f"no symbol for {abbreviation!r} in the sprite")
    attrs = (match.group(1) + match.group(2)).strip()
    if "xmlns=" not in attrs:
        attrs += ' xmlns="http://www.w3.org/2000/svg"'
    if "xmlns:xlink=" not in attrs:
        attrs += ' xmlns:xlink="http://www.w3.org/1999/xlink"'
    svg = f"<svg {attrs}>{match.group(3)}</svg>\n"
    if UNSAFE.search(svg):
        raise SystemExit(f"{abbreviation}: symbol contains script or event handlers")
    return svg


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    sprite = Path(sys.argv[1]).read_text(encoding="utf-8")
    OUT.mkdir(parents=True, exist_ok=True)
    for abbreviation in ABBREVIATIONS:
        (OUT / f"{abbreviation}.svg").write_text(extract(sprite, abbreviation), encoding="utf-8")
    print(f"wrote {len(ABBREVIATIONS)} logos to {OUT}")


if __name__ == "__main__":
    main()
