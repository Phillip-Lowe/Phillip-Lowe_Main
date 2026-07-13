import json
from pathlib import Path
from datetime import datetime

SNAPSHOT_FILE = Path("public_era_snapshot.json")
OUT_TXT = Path("public_era_storyline_bible.txt")
OUT_JSON = Path("public_era_storyline_bible.json")
MANIFEST = Path("public_era_storyline_manifest.txt")


def load_snapshot():
    if not SNAPSHOT_FILE.exists():
        raise FileNotFoundError(
            "Missing public_era_snapshot.json. Run --resume-public-era export/repair first."
        )

    return json.loads(SNAPSHOT_FILE.read_text(encoding="utf-8"))


def safe(obj, key, default=None):
    if isinstance(obj, dict):
        return obj.get(key, default)
    return default


def team_record(team):
    record = safe(team, "record", {})
    return safe(record, "wins", 0), safe(record, "losses", 0)


def win_pct(team):
    w, l = team_record(team)
    total = w + l
    if total == 0:
        return 0
    return w / total


def roster(team):
    return safe(team, "roster", [])


def top_players(team, limit=3):
    players = roster(team)
    return sorted(
        players,
        key=lambda p: (
            safe(p, "value_score", 0),
            safe(p, "overall", 0),
            safe(p, "potential", 0),
        ),
        reverse=True,
    )[:limit]


def player_label(player):
    return (
        f"{safe(player, 'name', 'Unknown')} "
        f"({safe(player, 'position', 'N/A')}, "
        f"Age {safe(player, 'age', 'N/A')}, "
        f"{safe(player, 'tier', 'N/A')}, "
        f"OVR {safe(player, 'overall', 'N/A')})"
    )


def parse_championship_ledger(lines):
    result = {}

    for line in lines:
        if ":" not in line:
            continue
        name, titles = line.split(":", 1)
        try:
            result[name.strip()] = int(titles.strip())
        except ValueError:
            result[name.strip()] = 0

    return result


def last_award_line(snapshot, marker):
    for line in reversed(safe(snapshot, "award_history", [])):
        if marker in line:
            return line
    return None


def recent_team_summary(snapshot, team_name):
    hits = []

    for summary in safe(snapshot, "season_summaries", [])[-10:]:
        if team_name in summary:
            hits.append(summary)

    return hits[-2:]


def classify_legacy(titles):
    if titles >= 6:
        return "historic power"
    if titles >= 4:
        return "championship institution"
    if titles >= 2:
        return "proven winner"
    if titles == 1:
        return "one-title legacy"
    return "title-hungry franchise"


def classify_pressure(team, titles):
    w, l = team_record(team)
    owner = safe(team, "owner", {})
    market = safe(team, "market", {})

    media = safe(market, "media_pressure", 0)
    patience = safe(owner, "patience", 70)
    winning_desire = safe(owner, "winning_desire", 70)

    pressure = 0
    pressure += max(0, 30 - w) * 2
    pressure += max(0, media - 70)
    pressure += max(0, 60 - patience)
    pressure += max(0, winning_desire - 85)

    if titles >= 4 and w < 30:
        pressure += 20

    if pressure >= 60:
        return "extreme pressure"
    if pressure >= 35:
        return "high pressure"
    if pressure >= 15:
        return "moderate pressure"
    return "stable"


def build_league_storylines(snapshot):
    league = safe(snapshot, "league", {})
    ledger = parse_championship_ledger(safe(snapshot, "championship_ledger", []))

    champion_leader = None
    if ledger:
        champion_leader = max(ledger.items(), key=lambda item: item[1])

    season_mvp_award = safe(league, "season_mvp_award_name", "Season MVP Award")
    playoff_mvp_award = safe(league, "playoff_mvp_award_name", "Kanomi Jones Playoff MVP")

    storylines = []

    storylines.append(
        f"The Public Era begins in Season {safe(league, 'current_year', 51)} after 50 hidden Genesis seasons."
    )

    storylines.append(
        f"The regular-season MVP race now carries legacy weight as the {season_mvp_award}."
    )

    storylines.append(
        f"The postseason still belongs to the {playoff_mvp_award}, preserving a separate playoff mythology."
    )

    if champion_leader:
        storylines.append(
            f"{champion_leader[0]} enters the Public Era as the historical title leader with {champion_leader[1]} championships."
        )

    storylines.append(
        "The public inherits a league with established dynasties, aging legends, new stars, and rival fan expectations already in motion."
    )

    return storylines


def build_team_storylines(snapshot):
    teams = safe(snapshot, "teams", {})
    ledger = parse_championship_ledger(safe(snapshot, "championship_ledger", []))

    team_stories = []

    for team_name, team in teams.items():
        titles = ledger.get(team_name, safe(team, "championships", 0))
        w, l = team_record(team)
        pct = win_pct(team)
        legacy = classify_legacy(titles)
        pressure = classify_pressure(team, titles)

        owner = safe(team, "owner", {})
        market = safe(team, "market", {})
        coach = safe(team, "coach", {})
        gm = safe(team, "gm", {})

        stars = top_players(team, limit=3)
        star_text = ", ".join(player_label(p) for p in stars) if stars else "No clear star core"

        hooks = []

        if titles >= 5:
            hooks.append("legacy defense")
        elif titles == 0:
            hooks.append("first-title chase")
        else:
            hooks.append("status climb")

        if w >= 38:
            hooks.append("immediate contender")
        elif w <= 24:
            hooks.append("rebuild pressure")
        else:
            hooks.append("uncertain middle")

        if safe(market, "media_pressure", 0) >= 80:
            hooks.append("media heat")

        if safe(owner, "patience", 70) < 55:
            hooks.append("ownership impatience")

        if any(safe(p, "age", 0) >= 34 and safe(p, "tier", "") in ["Generational", "Superstar"] for p in stars):
            hooks.append("aging-star clock")

        if any(safe(p, "age", 99) <= 24 and safe(p, "tier", "") in ["Generational", "Superstar"] for p in stars):
            hooks.append("new-face rise")

        team_stories.append(
            {
                "team": team_name,
                "record": f"{w}-{l}",
                "titles": titles,
                "legacy_class": legacy,
                "pressure_level": pressure,
                "owner": safe(owner, "name", "Unknown Owner"),
                "owner_type": safe(owner, "owner_type", "Unknown"),
                "gm": safe(gm, "name", "Unknown GM"),
                "coach": safe(coach, "name", "Unknown Coach"),
                "market": safe(market, "market_size", "Unknown"),
                "arena": safe(market, "arena", safe(team, "arena", "Unknown Arena")),
                "top_core": star_text,
                "hooks": hooks,
                "storyline": (
                    f"{team_name} enters Season 51 as a {legacy} with a {w}-{l} public-entry record. "
                    f"The franchise pressure is {pressure}. Owner {safe(owner, 'name', 'Unknown Owner')} "
                    f"sets the tone as a {safe(owner, 'owner_type', 'Unknown')} while GM "
                    f"{safe(gm, 'name', 'Unknown GM')} and Coach {safe(coach, 'name', 'Unknown Coach')} "
                    f"manage a core led by {star_text}."
                ),
                "recent_history": recent_team_summary(snapshot, team_name),
            }
        )

    return sorted(
        team_stories,
        key=lambda t: (
            t["titles"],
            int(t["record"].split("-")[0]),
        ),
        reverse=True,
    )


def build_player_storylines(snapshot):
    players = safe(snapshot, "top_active_players", [])

    stories = []

    for idx, player in enumerate(players[:40], start=1):
        name = safe(player, "name", "Unknown")
        team = safe(player, "team", "Unknown")
        age = safe(player, "age", 0)
        tier = safe(player, "tier", "")
        overall = safe(player, "overall", 0)
        potential = safe(player, "potential", 0)
        position = safe(player, "position", "")

        tags = []

        if idx == 1:
            tags.append("public-era face candidate")

        if tier == "Generational":
            tags.append("generational talent")

        if age <= 24:
            tags.append("future-builder")
        elif age >= 34:
            tags.append("legacy-clock")
        else:
            tags.append("prime-window")

        if overall >= 95:
            tags.append("MVP favorite")

        if potential >= 99 and age <= 25:
            tags.append("ceiling storyline")

        stories.append(
            {
                "rank": idx,
                "player": name,
                "team": team,
                "position": position,
                "age": age,
                "tier": tier,
                "overall": overall,
                "potential": potential,
                "tags": tags,
                "storyline": (
                    f"{name} of the {team} enters Season 51 ranked #{idx} among active players. "
                    f"As a {age}-year-old {tier} {position} with OVR {overall} and POT {potential}, "
                    f"his public-era arc centers on {', '.join(tags)}."
                ),
            }
        )

    return stories


def build_award_storylines(snapshot):
    league = safe(snapshot, "league", {})
    season_mvp_award = safe(league, "season_mvp_award_name", "Season MVP Award")
    playoff_mvp_award = safe(league, "playoff_mvp_award_name", "Kanomi Jones Playoff MVP")

    top_players = safe(snapshot, "top_active_players", [])[:12]

    mvp_watch = [
        f"{safe(p, 'name')} ({safe(p, 'team')})"
        for p in top_players
    ]

    year_50_mvp = last_award_line(snapshot, "Year 50: MVP:")
    year_50_roy = last_award_line(snapshot, "Year 50: Rookie of the Year:")
    year_50_dpoy = last_award_line(snapshot, "Year 50: Defensive Player of the Year:")
    year_50_playoff_mvp = last_award_line(snapshot, "Kanomi Jones Playoff MVP")

    return {
        "season_mvp_award": season_mvp_award,
        "playoff_mvp_award": playoff_mvp_award,
        "mvp_watchlist": mvp_watch,
        "storylines": [
            f"The first public race for the {season_mvp_award} will define Season 51's regular-season narrative.",
            f"The {playoff_mvp_award} remains the separate postseason immortality award.",
            "Voters now carry 50 years of hidden history into their first public-era debates.",
            "A player can dominate the regular season, lose the title, and still shape league mythology.",
        ],
        "recent_awards": {
            "year_50_mvp": year_50_mvp,
            "year_50_rookie_of_year": year_50_roy,
            "year_50_defensive_player": year_50_dpoy,
            "recent_kanomi_jones": year_50_playoff_mvp,
        },
    }


def build_rivalry_storylines(snapshot):
    teams = safe(snapshot, "teams", {})
    ledger = parse_championship_ledger(safe(snapshot, "championship_ledger", []))

    rivalries = []

    for team_name, team in teams.items():
        rivals = safe(team, "rivals", [])
        blood_rivals = safe(team, "blood_rivals", [])

        for rival in rivals:
            if rival in teams:
                rivalries.append(
                    {
                        "type": "rivalry",
                        "teams": [team_name, rival],
                        "storyline": (
                            f"{team_name} and {rival} carry an active rivalry into the Public Era. "
                            f"{team_name} has {ledger.get(team_name, 0)} titles while {rival} has {ledger.get(rival, 0)}."
                        ),
                    }
                )

        for rival in blood_rivals:
            if rival in teams:
                rivalries.append(
                    {
                        "type": "blood rivalry",
                        "teams": [team_name, rival],
                        "storyline": (
                            f"{team_name} and {rival} enter Season 51 with blood-rival stakes. "
                            f"Every matchup should be treated as a narrative event."
                        ),
                    }
                )

    # Deduplicate pairs.
    seen = set()
    unique = []

    for item in rivalries:
        pair = tuple(sorted(item["teams"]))

        if (pair, item["type"]) in seen:
            continue

        seen.add((pair, item["type"]))
        unique.append(item)

    return unique


def build_headline_board(snapshot, team_stories, player_stories, award_stories):
    headlines = []

    if player_stories:
        p = player_stories[0]
        headlines.append(
            f"Is {p['player']} the first true face of the Public Era?"
        )

    if team_stories:
        leader = team_stories[0]
        headlines.append(
            f"Can {leader['team']} defend the historical weight of {leader['titles']} championships?"
        )

    headlines.append(
        f"The first public race for the {award_stories['season_mvp_award']} begins now."
    )

    headlines.append(
        "Season 51 opens with 50 years of legacy already written and every franchise trying to control how the public remembers it."
    )

    high_pressure = [
        t for t in team_stories
        if "pressure" in t["pressure_level"]
    ]

    for team in high_pressure[:5]:
        headlines.append(
            f"{team['team']} enters Season 51 under {team['pressure_level']} after a {team['record']} finish."
        )

    return headlines


def build_storyline_bible(snapshot):
    league_storylines = build_league_storylines(snapshot)
    team_storylines = build_team_storylines(snapshot)
    player_storylines = build_player_storylines(snapshot)
    award_storylines = build_award_storylines(snapshot)
    rivalry_storylines = build_rivalry_storylines(snapshot)
    headline_board = build_headline_board(snapshot, team_storylines, player_storylines, award_storylines)

    return {
        "title": "NBF Public Era Storyline Bible",
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "league": safe(snapshot, "league", {}),
        "league_storylines": league_storylines,
        "headline_board": headline_board,
        "team_storylines": team_storylines,
        "player_storylines": player_storylines,
        "award_storylines": award_storylines,
        "rivalry_storylines": rivalry_storylines,
        "media_rules": [
            "Drama must emerge from simulation data, not random invention.",
            "Owner pressure should affect public tension.",
            "Championship history should affect franchise expectations.",
            "Aging stars should create urgency.",
            "Young generational players should create face-of-the-league narratives.",
            "The Tyrese King Jr. Season MVP Award is the primary regular-season prestige race.",
            "The Kanomi Jones Playoff MVP remains the postseason immortality race.",
        ],
        "completion_criteria": [
            "Every team has a storyline.",
            "Top active players have arcs.",
            "Award races are seeded.",
            "League-wide legacy stakes are defined.",
            "Season 51 can begin with narrative context.",
        ],
    }


def write_text_bible(bible):
    lines = []

    league = bible["league"]

    lines.append("NBF PUBLIC ERA STORYLINE BIBLE")
    lines.append("==============================")
    lines.append(f"Current Year: {safe(league, 'current_year')}")
    lines.append(f"Public Era Begins: Season {safe(league, 'public_era_start_year')}")
    lines.append(f"Season MVP Award: {safe(league, 'season_mvp_award_name')}")
    lines.append(f"Playoff MVP Award: {safe(league, 'playoff_mvp_award_name')}")
    lines.append("")

    lines.append("LEAGUE-WIDE STORYLINES")
    lines.append("----------------------")
    for item in bible["league_storylines"]:
        lines.append(f"- {item}")
    lines.append("")

    lines.append("SEASON 51 HEADLINE BOARD")
    lines.append("------------------------")
    for item in bible["headline_board"]:
        lines.append(f"- {item}")
    lines.append("")

    lines.append("AWARD STORYLINES")
    lines.append("----------------")
    for item in bible["award_storylines"]["storylines"]:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("MVP WATCHLIST:")
    for item in bible["award_storylines"]["mvp_watchlist"]:
        lines.append(f"- {item}")
    lines.append("")

    lines.append("TEAM STORYLINES")
    lines.append("---------------")
    for team in bible["team_storylines"]:
        lines.append(f"\n{team['team']}")
        lines.append(f"Record: {team['record']} | Titles: {team['titles']} | Legacy: {team['legacy_class']} | Pressure: {team['pressure_level']}")
        lines.append(f"Hooks: {', '.join(team['hooks'])}")
        lines.append(f"Core: {team['top_core']}")
        lines.append(f"Storyline: {team['storyline']}")

        if team["recent_history"]:
            lines.append("Recent History:")
            for item in team["recent_history"]:
                lines.append(f"- {item}")

    lines.append("")
    lines.append("TOP PLAYER STORYLINES")
    lines.append("---------------------")
    for player in bible["player_storylines"][:25]:
        lines.append(
            f"{player['rank']}. {player['player']} | {player['team']} | "
            f"{player['position']} | Age {player['age']} | {player['tier']} | "
            f"OVR {player['overall']} | POT {player['potential']}"
        )
        lines.append(f"   Arc: {player['storyline']}")

    lines.append("")
    lines.append("RIVALRY STORYLINES")
    lines.append("------------------")
    if bible["rivalry_storylines"]:
        for item in bible["rivalry_storylines"]:
            lines.append(f"- [{item['type']}] {item['storyline']}")
    else:
        lines.append("- No explicit rivalry storylines detected in snapshot.")

    lines.append("")
    lines.append("MEDIA / DRAMA RULES")
    lines.append("-------------------")
    for item in bible["media_rules"]:
        lines.append(f"- {item}")

    OUT_TXT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def validate_bible(bible):
    errors = []

    if not bible["league_storylines"]:
        errors.append("Missing league storylines.")

    if len(bible["team_storylines"]) != 16:
        errors.append(f"Expected 16 team storylines, found {len(bible['team_storylines'])}.")

    if not bible["player_storylines"]:
        errors.append("Missing player storylines.")

    if not bible["award_storylines"]["mvp_watchlist"]:
        errors.append("Missing MVP watchlist.")

    if not bible["headline_board"]:
        errors.append("Missing headline board.")

    if errors:
        print("STORYLINE BIBLE VALIDATION: FAILED")
        for error in errors:
            print(f"- {error}")
        raise SystemExit(1)

    print("STORYLINE BIBLE VALIDATION: PASS")


def main():
    snapshot = load_snapshot()
    bible = build_storyline_bible(snapshot)

    validate_bible(bible)

    OUT_JSON.write_text(
        json.dumps(bible, indent=2),
        encoding="utf-8",
    )

    write_text_bible(bible)

    MANIFEST.write_text(
        "\n".join(
            [
                "PUBLIC ERA STORYLINE BIBLE MANIFEST",
                "===================================",
                f"- {OUT_TXT.name}",
                f"- {OUT_JSON.name}",
                f"- Source: {SNAPSHOT_FILE.name}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    print("PUBLIC ERA STORYLINE BIBLE CREATED")
    print(f"- {OUT_TXT}")
    print(f"- {OUT_JSON}")
    print(f"- {MANIFEST}")


if __name__ == "__main__":
    main()
