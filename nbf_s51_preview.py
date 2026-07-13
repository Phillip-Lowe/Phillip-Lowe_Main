import json
from pathlib import Path
from datetime import datetime

SNAPSHOT_FILE = Path("public_era_snapshot.json")
BIBLE_FILE = Path("public_era_storyline_bible.json")

OUT_PREVIEW = Path("season_51_preview.txt")
OUT_POWER = Path("season_51_power_rankings.txt")
OUT_AWARDS = Path("season_51_award_watchlist.txt")
OUT_PRESSURE = Path("season_51_team_pressure_report.txt")
OUT_HEADLINES = Path("season_51_headlines.txt")
OUT_MANIFEST = Path("season_51_preview_manifest.txt")


def load_json(path):
    if not path.exists():
        raise FileNotFoundError(f"Missing required file: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def safe(obj, key, default=None):
    if isinstance(obj, dict):
        return obj.get(key, default)
    return default


def record_tuple(team):
    record = safe(team, "record", {})
    return safe(record, "wins", 0), safe(record, "losses", 0)


def win_pct(team):
    wins, losses = record_tuple(team)
    total = wins + losses
    return wins / total if total else 0


def roster(team):
    return safe(team, "roster", [])


def top_roster_players(team, limit=3):
    return sorted(
        roster(team),
        key=lambda p: (
            safe(p, "value_score", 0),
            safe(p, "overall", 0),
            safe(p, "potential", 0),
        ),
        reverse=True,
    )[:limit]


def player_line(player):
    return (
        f"{safe(player, 'name')} | {safe(player, 'team')} | "
        f"{safe(player, 'position')} | Age {safe(player, 'age')} | "
        f"{safe(player, 'tier')} | OVR {safe(player, 'overall')} | "
        f"POT {safe(player, 'potential')} | Value {safe(player, 'value_score')}"
    )


def parse_ledger(snapshot):
    ledger = {}

    for line in safe(snapshot, "championship_ledger", []):
        if ":" not in line:
            continue
        team, titles = line.split(":", 1)
        try:
            ledger[team.strip()] = int(titles.strip())
        except ValueError:
            ledger[team.strip()] = 0

    return ledger


def team_strength_score(team, titles=0):
    wins, losses = record_tuple(team)
    top_players = top_roster_players(team, limit=5)

    score = wins * 2
    score += titles * 6

    for idx, player in enumerate(top_players):
        weight = max(1, 5 - idx)
        score += safe(player, "value_score", 0) * weight * 0.35
        score += safe(player, "overall", 0) * weight * 0.10

    roster_count = safe(team, "roster_count", len(roster(team)))
    if roster_count < 12:
        score -= (12 - roster_count) * 10

    return round(score, 2)


def pressure_score(team, titles=0):
    wins, losses = record_tuple(team)
    owner = safe(team, "owner", {})
    market = safe(team, "market", {})

    pressure = 0
    pressure += max(0, 34 - wins) * 2
    pressure += max(0, safe(market, "media_pressure", 0) - 70)
    pressure += max(0, 60 - safe(owner, "patience", 70))
    pressure += max(0, safe(owner, "winning_desire", 70) - 85)

    if titles >= 4 and wins < 34:
        pressure += 15

    if titles == 0:
        pressure += 8

    return pressure


def pressure_label(score):
    if score >= 65:
        return "Extreme"
    if score >= 40:
        return "High"
    if score >= 20:
        return "Moderate"
    return "Stable"


def build_power_rankings(snapshot):
    teams = safe(snapshot, "teams", {})
    ledger = parse_ledger(snapshot)

    ranked = []

    for team_name, team in teams.items():
        titles = ledger.get(team_name, safe(team, "championships", 0))
        score = team_strength_score(team, titles=titles)
        wins, losses = record_tuple(team)

        stars = top_roster_players(team, limit=3)
        star_text = "; ".join(
            f"{safe(p, 'name')} ({safe(p, 'position')}, OVR {safe(p, 'overall')})"
            for p in stars
        )

        ranked.append(
            {
                "team": team_name,
                "score": score,
                "record": f"{wins}-{losses}",
                "titles": titles,
                "stars": star_text,
            }
        )

    return sorted(ranked, key=lambda x: x["score"], reverse=True)


def build_award_watchlist(snapshot, bible):
    top_players = safe(snapshot, "top_active_players", [])
    award_storylines = safe(bible, "award_storylines", {})
    mvp_award = safe(snapshot, "league", {}).get("season_mvp_award_name", "Season MVP Award")
    playoff_award = safe(snapshot, "league", {}).get("playoff_mvp_award_name", "Kanomi Jones Playoff MVP")

    mvp_watch = top_players[:15]

    rookie_watch = [
        p for p in top_players
        if safe(p, "age", 99) <= 23
    ][:10]

    dpoy_watch = sorted(
        top_players,
        key=lambda p: (
            safe(p, "defense", 0),
            safe(p, "rebounding", 0),
            safe(p, "basketball_iq", 0),
        ),
        reverse=True,
    )[:10]

    playoff_watch = sorted(
        top_players,
        key=lambda p: (
            safe(p, "overall", 0),
            safe(p, "leadership", 0),
            safe(p, "confidence", 0),
            safe(p, "basketball_iq", 0),
        ),
        reverse=True,
    )[:12]

    return {
        "mvp_award": mvp_award,
        "playoff_award": playoff_award,
        "mvp_watch": mvp_watch,
        "rookie_watch": rookie_watch,
        "dpoy_watch": dpoy_watch,
        "playoff_watch": playoff_watch,
        "award_storylines": safe(award_storylines, "storylines", []),
    }


def build_pressure_report(snapshot):
    teams = safe(snapshot, "teams", {})
    ledger = parse_ledger(snapshot)

    rows = []

    for team_name, team in teams.items():
        titles = ledger.get(team_name, safe(team, "championships", 0))
        score = pressure_score(team, titles=titles)
        label = pressure_label(score)
        wins, losses = record_tuple(team)

        owner = safe(team, "owner", {})
        market = safe(team, "market", {})

        reasons = []

        if wins < 30:
            reasons.append("recent losing pressure")

        if titles >= 4:
            reasons.append("championship standard")

        if safe(owner, "patience", 70) < 55:
            reasons.append("impatient ownership")

        if safe(owner, "winning_desire", 70) >= 90:
            reasons.append("win-now owner")

        if safe(market, "media_pressure", 0) >= 80:
            reasons.append("media heat")

        if titles == 0:
            reasons.append("first-title hunger")

        if not reasons:
            reasons.append("stable operating environment")

        rows.append(
            {
                "team": team_name,
                "record": f"{wins}-{losses}",
                "titles": titles,
                "score": score,
                "label": label,
                "owner": safe(owner, "name", "Unknown Owner"),
                "owner_type": safe(owner, "owner_type", "Unknown"),
                "reasons": reasons,
            }
        )

    return sorted(rows, key=lambda x: x["score"], reverse=True)


def write_headlines(bible, snapshot):
    headlines = list(safe(bible, "headline_board", []))

    top_players = safe(snapshot, "top_active_players", [])

    if top_players:
        p = top_players[0]
        headlines.append(
            f"{safe(p, 'name')} enters Season 51 as the top-ranked active player."
        )

    league = safe(snapshot, "league", {})
    headlines.append(
        f"The first public race for the {safe(league, 'season_mvp_award_name')} is officially open."
    )

    OUT_HEADLINES.write_text(
        "SEASON 51 HEADLINES\n"
        "===================\n"
        + "\n".join(f"- {line}" for line in headlines)
        + "\n",
        encoding="utf-8",
    )


def write_power_rankings(rankings):
    lines = [
        "SEASON 51 POWER RANKINGS",
        "========================",
        "",
    ]

    for idx, team in enumerate(rankings, start=1):
        lines.append(
            f"{idx}. {team['team']} | Record {team['record']} | "
            f"Titles {team['titles']} | Score {team['score']}"
        )
        lines.append(f"   Core: {team['stars']}")

    OUT_POWER.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_award_watchlist(awards):
    lines = [
        "SEASON 51 AWARD WATCHLIST",
        "=========================",
        "",
        f"{awards['mvp_award']} Watchlist",
        "-" * (len(awards['mvp_award']) + 10),
    ]

    for idx, player in enumerate(awards["mvp_watch"], start=1):
        lines.append(f"{idx}. {player_line(player)}")

    lines.extend(
        [
            "",
            "Rookie / Young Star Watch",
            "-------------------------",
        ]
    )

    for idx, player in enumerate(awards["rookie_watch"], start=1):
        lines.append(f"{idx}. {player_line(player)}")

    lines.extend(
        [
            "",
            "Defensive Player Watch",
            "----------------------",
        ]
    )

    for idx, player in enumerate(awards["dpoy_watch"], start=1):
        lines.append(
            f"{idx}. {player_line(player)} | "
            f"DEF {safe(player, 'defense')} | REB {safe(player, 'rebounding')} | IQ {safe(player, 'basketball_iq')}"
        )

    lines.extend(
        [
            "",
            f"{awards['playoff_award']} Watch",
            "-" * (len(awards["playoff_award"]) + 6),
        ]
    )

    for idx, player in enumerate(awards["playoff_watch"], start=1):
        lines.append(f"{idx}. {player_line(player)}")

    lines.extend(
        [
            "",
            "Award Narrative Rules",
            "---------------------",
        ]
    )

    for item in awards["award_storylines"]:
        lines.append(f"- {item}")

    OUT_AWARDS.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_pressure_report(report):
    lines = [
        "SEASON 51 TEAM PRESSURE REPORT",
        "==============================",
        "",
    ]

    for idx, row in enumerate(report, start=1):
        lines.append(
            f"{idx}. {row['team']} | {row['label']} Pressure | "
            f"Record {row['record']} | Titles {row['titles']} | Score {row['score']}"
        )
        lines.append(f"   Owner: {row['owner']} ({row['owner_type']})")
        lines.append(f"   Reasons: {', '.join(row['reasons'])}")

    OUT_PRESSURE.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_main_preview(snapshot, bible, rankings, awards, pressure):
    league = safe(snapshot, "league", {})
    headlines = safe(bible, "headline_board", [])

    lines = [
        "NBF SEASON 51 PUBLIC ERA PREVIEW",
        "================================",
        "",
        f"League: {safe(league, 'name')}",
        f"Current Year: {safe(league, 'current_year')}",
        f"Public Era Begins: Season {safe(league, 'public_era_start_year')}",
        f"Season MVP Award: {safe(league, 'season_mvp_award_name')}",
        f"Playoff MVP Award: {safe(league, 'playoff_mvp_award_name')}",
        "",
        "Opening Thesis",
        "--------------",
        (
            "Season 51 is the first public season after 50 hidden Genesis years. "
            "The league already has dynasties, scars, legacy awards, pressure markets, "
            "aging legends, and new faces ready to define the public era."
        ),
        "",
        "Top Headlines",
        "-------------",
    ]

    for headline in headlines[:10]:
        lines.append(f"- {headline}")

    lines.extend(
        [
            "",
            "Top 5 Power Rankings",
            "--------------------",
        ]
    )

    for idx, item in enumerate(rankings[:5], start=1):
        lines.append(
            f"{idx}. {item['team']} | Record {item['record']} | "
            f"Titles {item['titles']} | Score {item['score']}"
        )

    lines.extend(
        [
            "",
            f"Top 5 {awards['mvp_award']} Candidates",
            "----------------------------------------",
        ]
    )

    for idx, player in enumerate(awards["mvp_watch"][:5], start=1):
        lines.append(f"{idx}. {player_line(player)}")

    lines.extend(
        [
            "",
            "Highest Pressure Teams",
            "----------------------",
        ]
    )

    for idx, row in enumerate(pressure[:5], start=1):
        lines.append(
            f"{idx}. {row['team']} | {row['label']} | "
            f"Record {row['record']} | Titles {row['titles']} | Reasons: {', '.join(row['reasons'])}"
        )

    lines.extend(
        [
            "",
            "Season 51 Narrative Mandate",
            "---------------------------",
            "- Use real simulation history as the source of drama.",
            "- Treat awards as prestige systems, not random labels.",
            "- Let owners, markets, records, and titles create pressure.",
            "- Make every major injury, rumor, rivalry, or award race tie back to league history.",
            "- Do not simulate Season 51 until these storylines are approved.",
        ]
    )

    OUT_PREVIEW.write_text("\n".join(lines) + "\n", encoding="utf-8")


def validate_outputs():
    files = [
        OUT_PREVIEW,
        OUT_POWER,
        OUT_AWARDS,
        OUT_PRESSURE,
        OUT_HEADLINES,
        OUT_MANIFEST,
    ]

    errors = []

    for path in files:
        if not path.exists():
            errors.append(f"Missing output: {path}")
        elif path.stat().st_size == 0:
            errors.append(f"Empty output: {path}")

    if errors:
        print("SEASON 51 PREVIEW VALIDATION: FAILED")
        for error in errors:
            print(f"- {error}")
        raise SystemExit(1)

    print("SEASON 51 PREVIEW VALIDATION: PASS")


def main():
    snapshot = load_json(SNAPSHOT_FILE)
    bible = load_json(BIBLE_FILE)

    rankings = build_power_rankings(snapshot)
    awards = build_award_watchlist(snapshot, bible)
    pressure = build_pressure_report(snapshot)

    write_main_preview(snapshot, bible, rankings, awards, pressure)
    write_power_rankings(rankings)
    write_award_watchlist(awards)
    write_pressure_report(pressure)
    write_headlines(bible, snapshot)

    OUT_MANIFEST.write_text(
        "\n".join(
            [
                "SEASON 51 PREVIEW PACKAGE MANIFEST",
                "==================================",
                f"Created: {datetime.now().isoformat(timespec='seconds')}",
                f"Source Snapshot: {SNAPSHOT_FILE}",
                f"Source Storyline Bible: {BIBLE_FILE}",
                "",
                "Files:",
                f"- {OUT_PREVIEW}",
                f"- {OUT_POWER}",
                f"- {OUT_AWARDS}",
                f"- {OUT_PRESSURE}",
                f"- {OUT_HEADLINES}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    validate_outputs()

    print("SEASON 51 PREVIEW PACKAGE CREATED")
    print(f"- {OUT_PREVIEW}")
    print(f"- {OUT_POWER}")
    print(f"- {OUT_AWARDS}")
    print(f"- {OUT_PRESSURE}")
    print(f"- {OUT_HEADLINES}")
    print(f"- {OUT_MANIFEST}")


if __name__ == "__main__":
    main()
