"""Constants for the AFL Team Tracker integration."""

DOMAIN = "afl_team_tracker"
USER_AGENT = (
    "ha-afl-team-tracker-au/0.1.0 "
    "(+https://github.com/craibo/ha-afl-team-tracker-au)"
)
PERIODS = (
    "Upcoming",
    "Live",
    "Result",
    "Postponed",
    "Cancelled",
)

# Club logos bundled in www/logos/<abbreviation>.svg, by the (lower case) team
# abbreviation used by the data source. A test checks this against the files.
LOGOS = frozenset(
    "adel alls aus bl carl coll ess fre gcfc geel gws haw ias irl "
    "melb nmfc port rich stk syd wb wce".split()
)
LOGOS_URL = "/afl_team_tracker/logos"
