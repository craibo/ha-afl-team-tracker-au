export type HassEntity = { state: string; attributes: Record<string, unknown> };
export type TeamView = {
  name: string;
  /** Team abbreviation, e.g. "SYD"; used for the badge when there is no logo. */
  abbr?: string;
  logo?: string;
  score?: number;
  /** Goals.behinds.total, e.g. "20.12.132", if known. */
  scoreDetail?: string;
  /** Rank (ladder position, from the data source), if known. */
  rank?: number;
  /** `rank` formatted for the locale, e.g. "3rd" or "#3". */
  rankLabel?: string;
  /** Validated data-source page of the team, if known. */
  url?: string;
};
export type CardView = {
  mode: "upcoming" | "live" | "final" | "empty";
  home: TeamView;
  away: TeamView;
  headline: string;
  badge?: string;
  /** Upcoming only: the date, shown above the time (headline). */
  dateLine?: string;
  /** Upcoming only: the venue, shown under the start time. */
  venue?: string;
  /** Absolute data-source match page (validated). Not set for `empty` views. */
  matchUrl?: string;
};

const EMPTY: CardView = {
  mode: "empty",
  home: { name: "" },
  away: { name: "" },
  headline: "No game",
};

const empty = (): CardView => ({ ...EMPTY, home: { name: "" }, away: { name: "" } });

const str = (v: unknown): string | undefined =>
  typeof v === "string" && v !== "" ? v : undefined;
const num = (v: unknown): number | undefined =>
  typeof v === "number" && Number.isFinite(v) ? v : undefined;

const SOURCE_HOSTS = new Set(["www.afl.com.au", "afl.com.au"]);

/** An afl.com.au https URL (normalised), else undefined. Never throws. */
export function safeMatchUrl(value: unknown): string | undefined {
  if (typeof value !== "string" || value.trim() === "") return undefined;
  try {
    const u = new URL(value);
    if (u.protocol !== "https:" || !SOURCE_HOSTS.has(u.hostname)) return undefined;
    if (u.username !== "" || u.password !== "" || u.port !== "") return undefined;
    return u.href;
  } catch {
    return undefined;
  }
}

/** Alias for links that are not match pages (team pages): same allow-list. */
export const safeSourceUrl = safeMatchUrl;

/** Accessible name for a match link. */
export function matchLinkLabel(home: string, away: string): string {
  return `Open the match on the website: ${home} v ${away}`;
}

/** Accessible name for a team-page link. */
export const teamLinkLabel = (name: string): string => `Open ${name} on the website`;

/** Accessible name for the middle (game page) link of the team card. */
export const matchPartLabel = (): string => "Open the match on the website";

/** Badge text for a team without a logo: its abbreviation, else the first 3 letters of its name. */
export function teamAbbr(abbr: unknown, name: string): string {
  const a = typeof abbr === "string" ? abbr.trim() : "";
  return a !== "" ? a : name.trim().slice(0, 3).toUpperCase();
}

const venueOf = (v: unknown): string | undefined =>
  typeof v === "string" && v.trim() !== "" ? v.trim() : undefined;

const ORDINAL_SUFFIX: Record<string, string> = { one: "st", two: "nd", few: "rd", other: "th" };

/** A positive integer rank, else undefined. */
export const rankOf = (v: unknown): number | undefined =>
  typeof v === "number" && Number.isInteger(v) && v > 0 ? v : undefined;

/** Rank as text: English ordinals ("1st", "12th") or "#n" for other locales. */
export function formatRank(rank: number, locale: string): string {
  if (typeof locale !== "string" || !/^en(?:$|[-_])/i.test(locale)) return `#${rank}`;
  let rules: Intl.PluralRules;
  try {
    rules = new Intl.PluralRules(locale, { type: "ordinal" });
  } catch {
    rules = new Intl.PluralRules("en", { type: "ordinal" });
  }
  return `${rank}${ORDINAL_SUFFIX[rules.select(rank)] ?? "th"}`;
}

/** `{rank, rankLabel}` for a raw attribute value; empty when not a valid rank. */
export function rankFields(raw: unknown, locale: string): { rank?: number; rankLabel?: string } {
  const rank = rankOf(raw);
  return rank === undefined ? {} : { rank, rankLabel: formatRank(rank, locale) };
}

function formatKickoff(
  raw: unknown,
  locale: string,
  timeZone: string,
): { headline: string; dateLine?: string } {
  const s = str(raw);
  if (!s) return { headline: "TBC" };
  const d = new Date(s);
  if (Number.isNaN(d.getTime())) return { headline: s };
  try {
    return {
      dateLine: new Intl.DateTimeFormat(locale, {
        weekday: "short",
        day: "numeric",
        month: "short",
        timeZone,
      }).format(d),
      headline: new Intl.DateTimeFormat(locale, {
        hour: "2-digit",
        minute: "2-digit",
        timeZone,
      }).format(d),
    };
  } catch {
    return { headline: s };
  }
}

export function buildView(
  entity: HassEntity | undefined,
  locale: string,
  timeZone: string,
): CardView {
  try {
    if (!entity || entity.state === "unavailable" || entity.state === "unknown") return empty();
    const a = entity.attributes;
    if (!a || typeof a !== "object") return empty();
    const period = str(a.period);
    const homeName = str(a.home_team);
    const awayName = str(a.away_team);
    if (!period || !homeName || !awayName) return empty();

    const logos =
      a.logos && typeof a.logos === "object" ? (a.logos as Record<string, unknown>) : {};
    const hs = num(a.home_score);
    const as = num(a.away_score);
    const home: TeamView = {
      name: homeName,
      abbr: teamAbbr(a.home_abbr, homeName),
      logo: str(logos.home),
      score: hs,
      scoreDetail: str(a.home_score_detail),
      ...rankFields(a.home_rank, locale),
      url: safeSourceUrl(a.home_team_url),
    };
    const away: TeamView = {
      name: awayName,
      abbr: teamAbbr(a.away_abbr, awayName),
      logo: str(logos.away),
      score: as,
      scoreDetail: str(a.away_score_detail),
      ...rankFields(a.away_rank, locale),
      url: safeSourceUrl(a.away_team_url),
    };
    const score = `${hs ?? "-"} – ${as ?? "-"}`;

    switch (period) {
      case "Upcoming":
        return {
          mode: "upcoming",
          home,
          away,
          ...formatKickoff(a.kickoff, locale, timeZone),
          venue: venueOf(a.venue),
          matchUrl: safeMatchUrl(a.match_url),
        };
      case "Postponed":
      case "Cancelled":
        return {
          mode: "upcoming",
          home,
          away,
          ...formatKickoff(a.kickoff, locale, timeZone),
          badge: period,
          venue: venueOf(a.venue),
          matchUrl: safeMatchUrl(a.match_url),
        };
      case "Live":
        return {
          mode: "live",
          home,
          away,
          headline: score,
          badge: "Live",
          matchUrl: safeMatchUrl(a.match_url),
        };
      case "Result":
        return {
          mode: "final",
          home,
          away,
          headline: score,
          badge: "Full time",
          matchUrl: safeMatchUrl(a.match_url),
        };
      default:
        return empty();
    }
  } catch {
    return empty();
  }
}
