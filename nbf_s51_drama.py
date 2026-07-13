import json
import random
from pathlib import Path
from datetime import datetime

SNAPSHOT_FILE = Path("public_era_snapshot.json")
BIBLE_FILE = Path("public_era_storyline_bible.json")

OUT_EVENTS_JSON = Path("season_51_drama_events.json")
OUT_EVENTS_TXT = Path("season_51_drama_events.txt")
OUT_MEDIA = Path("season_51_media_board.txt")
OUT_HOT_SEAT = Path("season_51_hot_seat_report.txt")
OUT_RUMOR = Path("season_51_rumor_wire.txt")
OUT_AUDIT = Path("season_51_probability_audit.txt")
OUT_MANIFEST = Path("season_51_drama_manifest.txt")

SEASON = 51
BASE_SEED = "NBF-LBU:season51:drama"


def load_json(path):
    if not path.exists():
        raise FileNotFoundError(f"Missing required file: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def safe(obj, key, default=None):
    if isinstance(obj, dict):
        return obj.get(key, default)
    return default


def clamp(value, low=0, high=100):
    return max(low, min(high, value))


def deterministic_rng(*parts):
    seed = ":".join(str(part) for part in (BASE_SEED,) + parts)
    return random.Random(seed)


def record_tuple(team):
    record = safe(team, "record", {})
    return safe(record, "wins", 0), safe(record, "losses", 0)


def win_pct(team):
    w, l = record_tuple(team)
    total = w + l
    return w / total if total else 0


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


def pressure_score(team, titles):
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

    return clamp(pressure)


def pressure_label(score):
    if score >= 70:
        return "extreme"
    if score >= 50:
        return "very high"
    if score >= 35:
        return "high"
    if score >= 20:
        return "moderate"
    return "stable"


def probability_band(probability):
    if probability < 15:
        return "very unlikely"
    if probability < 30:
        return "possible"
    if probability < 50:
        return "plausible"
    if probability < 70:
        return "likely"
    if probability < 85:
        return "very likely"
    return "near certain"


def severity_from_probability(probability, rng, media_pressure=50):
    roll = rng.randint(1, 100)

    adjusted = probability + max(0, media_pressure - 70) * 0.25

    if adjusted >= 80:
        t1, t2, t3, t4 = 10, 25, 55, 80
    elif adjusted >= 60:
        t1, t2, t3, t4 = 20, 45, 75, 92
    elif adjusted >= 40:
        t1, t2, t3, t4 = 35, 65, 85, 96
    else:
        t1, t2, t3, t4 = 55, 80, 93, 99

    if roll <= t1:
        return 1
    if roll <= t2:
        return 2
    if roll <= t3:
        return 3
    if roll <= t4:
        return 4
    return 5

def roll_event(event_id, category, subject_type, team=None, player=None, plausibility=0, probability=0, headline="", summary="", factors=None, severity_context=None):
    rng = deterministic_rng(event_id, category, team or "", player or "")
    roll = rng.randint(1, 100)
    triggered = roll <= probability

    media_pressure = 50
    if severity_context:
        media_pressure = severity_context.get("media_pressure", 50)

    severity = severity_from_probability(probability, rng, media_pressure=media_pressure) if triggered else 0

    return {
        "event_id": event_id,
        "season": SEASON,
        "category": category,
        "subject_type": subject_type,
        "team": team,
        "player": player,
        "plausibility": clamp(round(plausibility)),
        "probability": clamp(round(probability)),
        "probability_band": probability_band(probability),
        "roll": roll,
        "triggered": triggered,
        "severity": severity,
        "headline": headline,
        "summary": summary,
        "source_factors": factors or [],
    }


def team_title_count(snapshot, team_name):
    return parse_ledger(snapshot).get(team_name, 0)


def coach_hot_seat_event(snapshot, team_name, team):
    titles = team_title_count(snapshot, team_name)
    wins, losses = record_tuple(team)
    owner = safe(team, "owner", {})
    market = safe(team, "market", {})
    coach = safe(team, "coach", {})

    factors = []
    plausibility = 5

    if wins < 30:
        plausibility += 25
        factors.append(f"{wins}-{losses} public-entry record")

    if titles >= 4:
        plausibility += 18
        factors.append(f"{titles} historical championships")

    if safe(owner, "patience", 70) < 55:
        plausibility += 18
        factors.append("impatient owner profile")

    if safe(owner, "winning_desire", 70) >= 90:
        plausibility += 14
        factors.append("win-now ownership expectation")

    if safe(market, "media_pressure", 0) >= 80:
        plausibility += 12
        factors.append("high media pressure market")

    probability = plausibility * 0.72

    headline = f"Pressure Builds Around {safe(coach, 'name', 'the head coach')} in {team_name}"
    summary = (
        f"{team_name} enters Season 51 with a {wins}-{losses} record and {titles} titles in its history. "
        f"That combination makes coaching scrutiny plausible before the first public-era game."
    )

    return roll_event(
        event_id=f"season51_{team_name.lower().replace(' ', '_')}_coach_hot_seat",
        category="coach_hot_seat",
        subject_type="team",
        team=team_name,
        plausibility=plausibility,
        probability=probability,
        headline=headline,
        summary=summary,
        factors=factors,
        severity_context={"media_pressure": safe(market, "media_pressure", 50)},
    )


def owner_pressure_event(snapshot, team_name, team):
    titles = team_title_count(snapshot, team_name)
    wins, losses = record_tuple(team)
    owner = safe(team, "owner", {})
    market = safe(team, "market", {})

    factors = []
    plausibility = 8

    if safe(owner, "winning_desire", 70) >= 85:
        plausibility += 22
        factors.append("high owner winning desire")

    if safe(owner, "patience", 70) < 60:
        plausibility += 20
        factors.append("low owner patience")

    if wins < 34:
        plausibility += 18
        factors.append(f"{wins}-{losses} record below contender standard")

    if titles >= 4:
        plausibility += 15
        factors.append(f"{titles} titles create franchise standard")

    if safe(market, "media_pressure", 0) >= 75:
        plausibility += 10
        factors.append("media pressure amplifies ownership tension")

    probability = plausibility * 0.70

    owner_name = safe(owner, "name", "Ownership")

    headline = f"{owner_name} Expectations Loom Over {team_name}"
    summary = (
        f"{team_name}'s ownership profile makes internal pressure a realistic Season 51 subplot, "
        f"especially with the public now watching every decision."
    )

    return roll_event(
        event_id=f"season51_{team_name.lower().replace(' ', '_')}_owner_pressure",
        category="owner_pressure_leak",
        subject_type="team",
        team=team_name,
        plausibility=plausibility,
        probability=probability,
        headline=headline,
        summary=summary,
        factors=factors,
        severity_context={"media_pressure": safe(market, "media_pressure", 50)},
    )


def trade_rumor_event(snapshot, team_name, team):
    titles = team_title_count(snapshot, team_name)
    wins, losses = record_tuple(team)
    owner = safe(team, "owner", {})
    market = safe(team, "market", {})
    stars = top_roster_players(team, 3)

    factors = []
    plausibility = 10

    if wins < 30:
        plausibility += 18
        factors.append("below-average record")

    if safe(owner, "winning_desire", 70) >= 85:
        plausibility += 18
        factors.append("win-now ownership")

    if titles >= 3:
        plausibility += 10
        factors.append("established title expectations")

    if any(safe(p, "age", 0) >= 34 and safe(p, "tier", "") in ["Generational", "Superstar"] for p in stars):
        plausibility += 18
        factors.append("aging star urgency")

    if safe(market, "media_pressure", 0) >= 75:
        plausibility += 8
        factors.append("media pressure feeds transaction speculation")

    probability = plausibility * 0.62

    primary = stars[0] if stars else None
    player_name = safe(primary, "name", None) if primary else None

    headline = f"{team_name} Linked to Early Season Trade Speculation"
    summary = (
        f"Roster pressure around {team_name} could generate trade chatter if Season 51 starts slowly."
    )

    return roll_event(
        event_id=f"season51_{team_name.lower().replace(' ', '_')}_trade_rumor",
        category="trade_rumor",
        subject_type="team",
        team=team_name,
        player=player_name,
        plausibility=plausibility,
        probability=probability,
        headline=headline,
        summary=summary,
        factors=factors,
        severity_context={"media_pressure": safe(market, "media_pressure", 50)},
    )


def mvp_narrative_event(player, rank):
    age = safe(player, "age", 0)
    tier = safe(player, "tier", "")
    overall = safe(player, "overall", 0)
    value = safe(player, "value_score", 0)
    name = safe(player, "name", "Unknown")
    team = safe(player, "team", "Unknown")

    factors = []
    plausibility = 15

    if rank <= 5:
        plausibility += 30
        factors.append(f"top-{rank} active player rank")

    if tier == "Generational":
        plausibility += 20
        factors.append("generational tier")

    if overall >= 95:
        plausibility += 15
        factors.append(f"elite OVR {overall}")

    if age <= 24:
        plausibility += 12
        factors.append("young face-of-league window")

    if value >= 110:
        plausibility += 10
        factors.append(f"elite value score {value}")

    probability = plausibility * 0.76

    headline = f"{name} Enters the First Public MVP Debate"
    summary = (
        f"{name} of the {team} has the profile to become one of the first public-era faces of the league."
    )

    return roll_event(
        event_id=f"season51_{name.lower().replace(' ', '_')}_mvp_narrative",
        category="mvp_narrative_surge",
        subject_type="player",
        team=team,
        player=name,
        plausibility=plausibility,
        probability=probability,
        headline=headline,
        summary=summary,
        factors=factors,
        severity_context={"media_pressure": 75},
    )


def aging_star_event(player):
    name = safe(player, "name", "Unknown")
    team = safe(player, "team", "Unknown")
    age = safe(player, "age", 0)
    tier = safe(player, "tier", "")
    overall = safe(player, "overall", 0)

    factors = []
    plausibility = 0

    if age >= 34:
        plausibility += 35
        factors.append(f"age {age}")

    if tier in ["Generational", "Superstar"]:
        plausibility += 25
        factors.append(f"{tier} tier")

    if overall >= 90:
        plausibility += 20
        factors.append(f"still elite at OVR {overall}")

    probability = plausibility * 0.70

    headline = f"{name}'s Legacy Clock Becomes a Season 51 Story"
    summary = (
        f"{name} remains elite, but age and public scrutiny make every playoff chase more urgent."
    )

    return roll_event(
        event_id=f"season51_{name.lower().replace(' ', '_')}_aging_star",
        category="aging_star_legacy_watch",
        subject_type="player",
        team=team,
        player=name,
        plausibility=plausibility,
        probability=probability,
        headline=headline,
        summary=summary,
        factors=factors,
        severity_context={"media_pressure": 70},
    )


def young_star_event(player):
    name = safe(player, "name", "Unknown")
    team = safe(player, "team", "Unknown")
    age = safe(player, "age", 0)
    tier = safe(player, "tier", "")
    potential = safe(player, "potential", 0)
    overall = safe(player, "overall", 0)

    factors = []
    plausibility = 0

    if age <= 24:
        plausibility += 30
        factors.append(f"age {age}")

    if potential >= 98:
        plausibility += 25
        factors.append(f"elite potential {potential}")

    if tier in ["Generational", "Superstar"]:
        plausibility += 25
        factors.append(f"{tier} tier")

    if overall >= 88:
        plausibility += 10
        factors.append(f"already productive at OVR {overall}")

    probability = plausibility * 0.72

    headline = f"{name} Draws Breakout Spotlight Entering Season 51"
    summary = (
        f"{name} has the youth and upside to become a public-era storyline immediately."
    )

    return roll_event(
        event_id=f"season51_{name.lower().replace(' ', '_')}_young_star",
        category="young_star_breakout_hype",
        subject_type="player",
        team=team,
        player=name,
        plausibility=plausibility,
        probability=probability,
        headline=headline,
        summary=summary,
        factors=factors,
        severity_context={"media_pressure": 65},
    )


def rivalry_event(rivalry):
    teams = safe(rivalry, "teams", [])
    story = safe(rivalry, "storyline", "")
    rtype = safe(rivalry, "type", "rivalry")

    if len(teams) != 2:
        return None

    plausibility = 35

    if rtype == "blood rivalry":
        plausibility += 25

    probability = plausibility * 0.68

    headline = f"{teams[0]} vs {teams[1]} Carries Early Public-Era Heat"
    summary = story or f"{teams[0]} and {teams[1]} enter Season 51 with rivalry stakes."

    return roll_event(
        event_id=f"season51_{teams[0].lower().replace(' ', '_')}_{teams[1].lower().replace(' ', '_')}_rivalry",
        category="rivalry_escalation",
        subject_type="rivalry",
        team=f"{teams[0]} / {teams[1]}",
        plausibility=plausibility,
        probability=probability,
        headline=headline,
        summary=summary,
        factors=[rtype, "existing rivalry relationship"],
        severity_context={"media_pressure": 70},
    )


def build_events(snapshot, bible):
    events = []
    teams = safe(snapshot, "teams", {})
    top_players = safe(snapshot, "top_active_players", [])

    for team_name, team in teams.items():
        events.append(coach_hot_seat_event(snapshot, team_name, team))
        events.append(owner_pressure_event(snapshot, team_name, team))
        events.append(trade_rumor_event(snapshot, team_name, team))

    for idx, player in enumerate(top_players[:15], start=1):
        events.append(mvp_narrative_event(player, idx))

    for player in top_players[:40]:
        if safe(player, "age", 0) >= 34 and safe(player, "tier", "") in ["Generational", "Superstar"]:
            events.append(aging_star_event(player))

        if safe(player, "age", 99) <= 24 and safe(player, "tier", "") in ["Generational", "Superstar"]:
            events.append(young_star_event(player))

    for rivalry in safe(bible, "rivalry_storylines", []):
        event = rivalry_event(rivalry)
        if event:
            events.append(event)

    return events


def write_events_txt(events):
    triggered = [e for e in events if e["triggered"]]
    untriggered = [e for e in events if not e["triggered"]]

    lines = [
        "SEASON 51 DRAMA EVENTS",
        "======================",
        "",
        f"Triggered Events: {len(triggered)}",
        f"Untriggered / Monitored Events: {len(untriggered)}",
        "",
        "TRIGGERED EVENTS",
        "----------------",
    ]

    for event in sorted(triggered, key=lambda e: (e["severity"], e["probability"]), reverse=True):
        lines.append("")
        lines.append(f"[Severity {event['severity']}] {event['headline']}")
        lines.append(f"Category: {event['category']} | Probability: {event['probability']}% | Roll: {event['roll']}")
        lines.append(f"Summary: {event['summary']}")
        lines.append(f"Factors: {', '.join(event['source_factors'])}")

    lines.append("")
    lines.append("MONITORED BUT NOT TRIGGERED")
    lines.append("---------------------------")

    for event in sorted(untriggered, key=lambda e: e["probability"], reverse=True)[:40]:
        lines.append(
            f"- {event['headline']} | Probability {event['probability']}% | Roll {event['roll']} | Band {event['probability_band']}"
        )

    OUT_EVENTS_TXT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_media_board(events):
    triggered = [e for e in events if e["triggered"]]

    lines = [
        "SEASON 51 MEDIA BOARD",
        "=====================",
        "",
    ]

    media_events = [
        e for e in triggered
        if e["severity"] >= 3
    ]

    if not media_events:
        lines.append("- No major national media stories triggered yet.")
    else:
        for event in sorted(media_events, key=lambda e: e["severity"], reverse=True):
            lines.append(f"- [S{event['severity']}] {event['headline']}")
            lines.append(f"  {event['summary']}")

    OUT_MEDIA.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_hot_seat_report(events):
    hot = [
        e for e in events
        if e["category"] == "coach_hot_seat"
    ]

    lines = [
        "SEASON 51 HOT SEAT REPORT",
        "=========================",
        "",
    ]

    for event in sorted(hot, key=lambda e: e["probability"], reverse=True):
        status = "TRIGGERED" if event["triggered"] else "MONITOR"
        lines.append(
            f"- {event['team']} | {status} | Probability {event['probability']}% | Roll {event['roll']} | Severity {event['severity']}"
        )
        lines.append(f"  {event['headline']}")
        lines.append(f"  Factors: {', '.join(event['source_factors'])}")

    OUT_HOT_SEAT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_rumor_wire(events):
    rumors = [
        e for e in events
        if e["category"] in ["trade_rumor", "owner_pressure_leak"]
    ]

    lines = [
        "SEASON 51 RUMOR WIRE",
        "====================",
        "",
    ]

    for event in sorted(rumors, key=lambda e: (e["triggered"], e["probability"]), reverse=True):
        status = "ACTIVE" if event["triggered"] else "WATCH"
        lines.append(
            f"- [{status}] {event['headline']} | Probability {event['probability']}% | Roll {event['roll']}"
        )
        lines.append(f"  {event['summary']}")

    OUT_RUMOR.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_probability_audit(events):
    lines = [
        "SEASON 51 PROBABILITY AUDIT",
        "===========================",
        "",
        "Format: Event | Plausibility | Probability | Roll | Triggered | Factors",
        "",
    ]

    for event in sorted(events, key=lambda e: e["probability"], reverse=True):
        lines.append(
            f"{event['event_id']} | Plausibility {event['plausibility']} | "
            f"Probability {event['probability']} | Roll {event['roll']} | "
            f"Triggered {event['triggered']} | Factors: {', '.join(event['source_factors'])}"
        )

    OUT_AUDIT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_manifest(events):
    triggered = [e for e in events if e["triggered"]]

    lines = [
        "SEASON 51 DRAMA ENGINE MANIFEST",
        "===============================",
        f"Created: {datetime.now().isoformat(timespec='seconds')}",
        f"Source Snapshot: {SNAPSHOT_FILE}",
        f"Source Storyline Bible: {BIBLE_FILE}",
        "",
        f"Total Events Evaluated: {len(events)}",
        f"Triggered Events: {len(triggered)}",
        "",
        "Files:",
        f"- {OUT_EVENTS_JSON}",
        f"- {OUT_EVENTS_TXT}",
        f"- {OUT_MEDIA}",
        f"- {OUT_HOT_SEAT}",
        f"- {OUT_RUMOR}",
        f"- {OUT_AUDIT}",
    ]

    OUT_MANIFEST.write_text("\n".join(lines) + "\n", encoding="utf-8")


def validate_outputs(events):
    errors = []

    if not events:
        errors.append("No events generated.")

    triggered = [e for e in events if e["triggered"]]

    if not triggered:
        errors.append("No drama events triggered. Probability model may be too strict.")

    for event in events:
        for key in ["event_id", "category", "plausibility", "probability", "roll", "triggered", "headline"]:
            if key not in event:
                errors.append(f"Event missing key {key}: {event}")

    files = [
        OUT_EVENTS_JSON,
        OUT_EVENTS_TXT,
        OUT_MEDIA,
        OUT_HOT_SEAT,
        OUT_RUMOR,
        OUT_AUDIT,
        OUT_MANIFEST,
    ]

    for path in files:
        if not path.exists():
            errors.append(f"Missing output file: {path}")
        elif path.stat().st_size == 0:
            errors.append(f"Empty output file: {path}")

    if errors:
        print("DRAMA ENGINE VALIDATION: FAILED")
        for error in errors:
            print(f"- {error}")
        raise SystemExit(1)

    print("DRAMA ENGINE VALIDATION: PASS")


def main():
    snapshot = load_json(SNAPSHOT_FILE)
    bible = load_json(BIBLE_FILE)

    events = build_events(snapshot, bible)

    OUT_EVENTS_JSON.write_text(
        json.dumps(events, indent=2),
        encoding="utf-8",
    )

    write_events_txt(events)
    write_media_board(events)
    write_hot_seat_report(events)
    write_rumor_wire(events)
    write_probability_audit(events)
    write_manifest(events)

    validate_outputs(events)

    triggered = [e for e in events if e["triggered"]]

    print("SEASON 51 PROBABILISTIC DRAMA ENGINE CREATED")
    print(f"- Events evaluated: {len(events)}")
    print(f"- Events triggered: {len(triggered)}")
    print(f"- {OUT_EVENTS_JSON}")
    print(f"- {OUT_EVENTS_TXT}")
    print(f"- {OUT_MEDIA}")
    print(f"- {OUT_HOT_SEAT}")
    print(f"- {OUT_RUMOR}")
    print(f"- {OUT_AUDIT}")
    print(f"- {OUT_MANIFEST}")


if __name__ == "__main__":
    main()
