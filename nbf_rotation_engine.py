import json
from collections import Counter

SNAPSHOT_FILE = "public_era_snapshot.json"
TENDENCIES_FILE = "player_tendencies.json"
COACH_SYSTEMS_FILE = "coach_systems.json"
OUTPUT_FILE = "rotation_engine.json"

REGULATION_TEAM_MINUTES = 240

POSITION_ORDER = {
    "PG": 1,
    "SG": 2,
    "SF": 3,
    "PF": 4,
    "C": 5,
}

ARCHETYPE_SYSTEM_BONUSES = {
    "Pace and Space": {
        "Floor General": 5,
        "Playmaking Superstar": 5,
        "Playmaking Wing": 4,
        "Point Forward": 4,
        "Stretch Big": 5,
        "Shot Creator": 3,
        "Scoring Guard": 3,
        "Athletic Slasher": 2,
    },
    "Balanced": {
        "Two-Way Star": 5,
        "Balanced Contributor": 4,
        "Floor General": 3,
        "Playmaking Wing": 3,
        "Interior Anchor": 3,
        "Point Forward": 3,
        "Defensive Specialist": 2,
        "Rebounding Specialist": 2,
    },
}

DEFENSIVE_ARCHETYPE_BONUSES = {
    "Switching": {
        "Two-Way Star": 5,
        "Playmaking Wing": 3,
        "Point Forward": 3,
        "Defensive Specialist": 4,
        "Athletic Slasher": 2,
    },
    "Drop Coverage": {
        "Interior Anchor": 5,
        "Rebounding Specialist": 4,
        "Stretch Big": 2,
        "Defensive Specialist": 3,
    },
}

ROLE_BASE_MINUTES = {
    "Franchise Star": 38.0,
    "Starter": 32.0,
    "Sixth Man": 26.0,
    "Rotation Player": 18.0,
    "Bench Player": 8.0,
    "Reserve": 2.0,
}

ROLE_MINIMUMS = {
    "Franchise Star": 32,
    "Starter": 24,
    "Sixth Man": 18,
    "Rotation Player": 8,
    "Bench Player": 0,
    "Reserve": 0,
}

ROLE_MAXIMUMS = {
    "Franchise Star": 40,
    "Starter": 38,
    "Sixth Man": 32,
    "Rotation Player": 26,
    "Bench Player": 16,
    "Reserve": 8,
}


def clamp(value, minimum, maximum):
    return max(minimum, min(maximum, value))


def load_json(filename):
    with open(filename, "r", encoding="utf-8") as file:
        return json.load(file)


def calculate_coach_trust(player, coach):
    experience_score = clamp(player["years_pro"] * 4, 0, 100)

    trust = (
        player["basketball_iq"] * 0.24
        + player["discipline"] * 0.20
        + player["leadership"] * 0.14
        + experience_score * 0.12
        + player["durability"] * 0.10
        + player["overall"] * 0.10
        + player["confidence"] * 0.05
        + coach["coach_overall"] * 0.05
    )

    age = player["age"]
    development_rating = coach["player_development"]

    if age <= 23:
        trust += (development_rating - 50) * 0.16
    elif age <= 26:
        trust += (development_rating - 50) * 0.08

    if coach["personality"] == "Development Guru" and age <= 24:
        trust += 4

    if coach["personality"] == "Defense Specialist":
        trust += (player["defense"] - 75) * 0.08
        trust += (player["discipline"] - 75) * 0.05

    if coach["personality"] == "Player's Coach":
        trust += (player["leadership"] - 70) * 0.06
        trust += (player["confidence"] - 70) * 0.04

    return round(clamp(trust, 0, 100), 2)


def trust_tier(score):
    if score >= 90:
        return "Elite Trust"
    if score >= 75:
        return "High Trust"
    if score >= 50:
        return "Medium Trust"
    if score >= 25:
        return "Low Trust"
    return "Minimal Trust"


def system_fit_score(player, tendency, coach):
    archetype = tendency["archetype"]

    offensive_bonus = ARCHETYPE_SYSTEM_BONUSES.get(
        coach["offensive_system"], {}
    ).get(archetype, 0)

    defensive_bonus = DEFENSIVE_ARCHETYPE_BONUSES.get(
        coach["defensive_system"], {}
    ).get(archetype, 0)

    fit = 50 + offensive_bonus + defensive_bonus

    if coach["offensive_system"] == "Pace and Space":
        fit += (tendency["three_point_tendency"] - 70) * 0.08
        fit += (tendency["pass_tendency"] - 70) * 0.05

    if coach["offensive_system"] == "Balanced":
        fit += (player["basketball_iq"] - 70) * 0.06

    if coach["defensive_system"] == "Switching":
        fit += (player["defense"] - 70) * 0.07
        fit += (player["athleticism"] - 70) * 0.04

    if coach["defensive_system"] == "Drop Coverage":
        fit += (player["rebounding"] - 70) * 0.06
        if player["position"] in {"PF", "C"}:
            fit += 3

    return round(clamp(fit, 0, 100), 2)


def deployment_score(player, trust, fit):
    return round(
        player["overall"] * 0.50
        + trust * 0.25
        + player["value_score"] * 0.15
        + fit * 0.10,
        2,
    )


def choose_starters(players):
    starters = []

    for position in ["PG", "SG", "SF", "PF", "C"]:
        candidates = [
            player
            for player in players
            if player["position"] == position
        ]

        if not candidates:
            raise ValueError(f"No eligible player found at {position}")

        selected = max(
            candidates,
            key=lambda player: (
                player["deployment_score"],
                player["coach_trust"],
                player["overall"],
                -player["player_id"],
            ),
        )

        starters.append(selected)

    return starters


def assign_roles(players, starters):
    starter_ids = {player["player_id"] for player in starters}

    ordered_starters = sorted(
        starters,
        key=lambda player: (
            player["deployment_score"],
            player["coach_trust"],
            player["overall"],
        ),
        reverse=True,
    )

    franchise_candidate = ordered_starters[0]

    franchise_eligible = (
        franchise_candidate["overall"] >= 90
        or franchise_candidate["tier"] in {"Generational", "Superstar"}
    )

    for player in starters:
        player["role"] = "Starter"

    if franchise_eligible:
        franchise_candidate["role"] = "Franchise Star"

    bench = sorted(
        [
            player
            for player in players
            if player["player_id"] not in starter_ids
        ],
        key=lambda player: (
            player["deployment_score"],
            player["coach_trust"],
            player["overall"],
            -player["player_id"],
        ),
        reverse=True,
    )

    if bench:
        bench[0]["role"] = "Sixth Man"

    for player in bench[1:4]:
        player["role"] = "Rotation Player"

    for player in bench[4:6]:
        player["role"] = "Bench Player"

    for player in bench[6:]:
        player["role"] = "Reserve"


def role_weight(player, coach):
    role = player["role"]
    weight = ROLE_BASE_MINUTES[role]

    trust_modifier = (player["coach_trust"] - 65) * 0.08
    fit_modifier = (player["system_fit"] - 50) * 0.05

    weight += trust_modifier
    weight += fit_modifier

    tightness = coach["rotation_tightness"]
    star_dependency = coach["star_dependency"]

    if role == "Franchise Star":
        weight += (star_dependency - 50) * 0.06
        weight += (tightness - 50) * 0.04
    elif role == "Starter":
        weight += (tightness - 50) * 0.025
    elif role == "Sixth Man":
        weight += (tightness - 50) * 0.005
    elif role in {"Rotation Player", "Bench Player", "Reserve"}:
        weight -= (tightness - 50) * 0.025

    if coach["personality"] == "Development Guru" and player["age"] <= 24:
        weight += 2.5

    if coach["personality"] == "Defense Specialist":
        weight += (player["defense"] - 75) * 0.025

    if player["age"] >= 35:
        weight -= max(0, player["age"] - 34) * 0.35

    durability_modifier = (player["durability"] - 75) * 0.025
    weight += durability_modifier

    return max(0.25, weight)


def allocate_minutes(players):
    total_weight = sum(player["minute_weight"] for player in players)

    for player in players:
        raw_minutes = (
            player["minute_weight"]
            / total_weight
            * REGULATION_TEAM_MINUTES
        )

        role = player["role"]
        minimum_minutes = ROLE_MINIMUMS[role]

        if not player.get("starter", False) and player["overall"] >= 90:
            minimum_minutes = max(minimum_minutes, 28)

        raw_minutes = clamp(
            raw_minutes,
            minimum_minutes,
            ROLE_MAXIMUMS[role],
        )

        player["_raw_minutes"] = raw_minutes
        player["minutes"] = int(raw_minutes)

    current_total = sum(player["minutes"] for player in players)

    while current_total < REGULATION_TEAM_MINUTES:
        eligible = [
            player
            for player in players
            if player["minutes"] < ROLE_MAXIMUMS[player["role"]]
        ]

        if not eligible:
            raise ValueError("Unable to allocate all 240 team minutes")

        selected = max(
            eligible,
            key=lambda player: (
                player["_raw_minutes"] - player["minutes"],
                player["deployment_score"],
                player["coach_trust"],
                -player["player_id"],
            ),
        )

        selected["minutes"] += 1
        current_total += 1

    while current_total > REGULATION_TEAM_MINUTES:
        eligible = []

        for player in players:
            minimum_minutes = ROLE_MINIMUMS[player["role"]]

            if not player.get("starter", False) and player["overall"] >= 90:
                minimum_minutes = max(minimum_minutes, 28)

            if player["minutes"] > minimum_minutes:
                eligible.append(player)

        if not eligible:
            raise ValueError("Unable to reduce rotation to 240 team minutes")

        selected = min(
            eligible,
            key=lambda player: (
                player["_raw_minutes"] - player["minutes"],
                player["deployment_score"],
                player["coach_trust"],
                -player["player_id"],
            ),
        )

        selected["minutes"] -= 1
        current_total -= 1

    for player in players:
        del player["_raw_minutes"]


def choose_closing_lineup(players):
    from itertools import combinations

    def closing_score(player):
        return (
            player["deployment_score"] * 0.50
            + player["coach_trust"] * 0.25
            + player["overall"] * 0.15
            + player["clutch_tendency"] * 0.10
        )

    valid_lineups = []

    for lineup in combinations(players, 5):
        guard_count = sum(
            player["position"] in {"PG", "SG"}
            for player in lineup
        )
        wing_count = sum(
            player["position"] in {"SG", "SF"}
            for player in lineup
        )
        big_count = sum(
            player["position"] in {"PF", "C"}
            for player in lineup
        )

        if not 1 <= guard_count <= 3:
            continue

        if wing_count < 1:
            continue

        if not 1 <= big_count <= 3:
            continue

        total_score = sum(
            closing_score(player)
            for player in lineup
        )

        total_minutes = sum(
            player["minutes"]
            for player in lineup
        )

        player_id_key = tuple(
            sorted(player["player_id"] for player in lineup)
        )

        valid_lineups.append(
            (
                total_score,
                total_minutes,
                tuple(-player_id for player_id in player_id_key),
                lineup,
            )
        )

    if not valid_lineups:
        raise ValueError(
            "No positionally valid closing lineup could be generated"
        )

    selected = max(
        valid_lineups,
        key=lambda item: (
            item[0],
            item[1],
            item[2],
        ),
    )[3]

    return sorted(
        selected,
        key=lambda player: (
            -closing_score(player),
            -player["minutes"],
            player["player_id"],
        ),
    )


def build_explanation(player, coach):
    reasons = [
        f"{player['role']} assignment",
        f"{player['coach_trust_tier'].lower()}",
        f"{player['system_fit']:.2f} system-fit score",
        f"{player['overall']} overall rating",
    ]

    if coach["personality"] == "Development Guru" and player["age"] <= 24:
        reasons.append("development-coach youth priority")

    if coach["personality"] == "Defense Specialist":
        reasons.append("defensive-coach deployment influence")

    if player["age"] >= 35:
        reasons.append("veteran workload adjustment")

    return "; ".join(reasons)


def main():
    snapshot = load_json(SNAPSHOT_FILE)
    tendencies = load_json(TENDENCIES_FILE)
    coach_systems = load_json(COACH_SYSTEMS_FILE)

    tendency_lookup = {
        record["player_id"]: record
        for record in tendencies
    }

    coach_lookup = {
        record["team"]: record
        for record in coach_systems
    }

    output_teams = {}
    league_role_counts = Counter()

    for team_name, team in snapshot["teams"].items():
        if team_name not in coach_lookup:
            raise ValueError(f"Missing coach system for {team_name}")

        coach = coach_lookup[team_name]
        rotation_players = []

        for source_player in team["roster"]:
            player_id = source_player["player_id"]

            if player_id not in tendency_lookup:
                raise ValueError(
                    f"Missing tendency record for player_id {player_id}"
                )

            tendency = tendency_lookup[player_id]
            trust = calculate_coach_trust(source_player, coach)
            fit = system_fit_score(source_player, tendency, coach)

            rotation_player = {
                "player_id": player_id,
                "name": source_player["name"],
                "team": team_name,
                "position": source_player["position"],
                "age": source_player["age"],
                "tier": source_player["tier"],
                "overall": source_player["overall"],
                "potential": source_player["potential"],
                "defense": source_player["defense"],
                "archetype": tendency["archetype"],
                "coach_trust": trust,
                "coach_trust_tier": trust_tier(trust),
                "system_fit": fit,
                "deployment_score": deployment_score(
                    source_player,
                    trust,
                    fit,
                ),
                "clutch_tendency": tendency["clutch_tendency"],
                "durability": source_player["durability"],
                "injury_risk": source_player["injury_risk"],
                "health_status": "Available",
                "fatigue_status": "Not Tracked",
                "minutes_restriction": None,
                "_source_player": source_player,
            }

            rotation_players.append(rotation_player)

        starters = choose_starters(rotation_players)
        assign_roles(rotation_players, starters)

        for player in rotation_players:
            player["minute_weight"] = round(
                role_weight(player, coach),
                4,
            )

        allocate_minutes(rotation_players)
        closing_lineup = choose_closing_lineup(rotation_players)

        starter_ids = {
            player["player_id"]
            for player in starters
        }

        closing_ids = {
            player["player_id"]
            for player in closing_lineup
        }

        for player in rotation_players:
            source_player = player.pop("_source_player")
            player["starter"] = player["player_id"] in starter_ids
            player["closer"] = player["player_id"] in closing_ids
            player["rotation_explanation"] = build_explanation(
                {
                    **player,
                    "defense": source_player["defense"],
                },
                coach,
            )
            league_role_counts[player["role"]] += 1

        rotation_players.sort(
            key=lambda player: (
                not player["starter"],
                POSITION_ORDER[player["position"]]
                if player["starter"]
                else 99,
                -player["minutes"],
                -player["deployment_score"],
                player["player_id"],
            )
        )

        output_teams[team_name] = {
            "coach": coach,
            "rotation_size": sum(
                1
                for player in rotation_players
                if player["minutes"] > 0
            ),
            "team_minutes": sum(
                player["minutes"]
                for player in rotation_players
            ),
            "starting_lineup": [
                {
                    "player_id": player["player_id"],
                    "name": player["name"],
                    "position": player["position"],
                    "role": player["role"],
                    "minutes": player["minutes"],
                }
                for player in sorted(
                    starters,
                    key=lambda player: POSITION_ORDER[player["position"]],
                )
            ],
            "closing_lineup": [
                {
                    "player_id": player["player_id"],
                    "name": player["name"],
                    "position": player["position"],
                    "role": player["role"],
                    "minutes": player["minutes"],
                }
                for player in closing_lineup
            ],
            "players": rotation_players,
        }

    output = {
        "engine": "NBF Rotation Engine",
        "version": "1.0",
        "season": 51,
        "simulation_doctrine": (
            "Coaches determine deployment; rotations determine opportunity; "
            "possessions determine statistics."
        ),
        "health_model_status": (
            "Initial baseline only. Dynamic fatigue, injury status, and "
            "minutes restrictions are not present in the current snapshot."
        ),
        "team_count": len(output_teams),
        "player_count": sum(
            len(team["players"])
            for team in output_teams.values()
        ),
        "league_role_distribution": dict(league_role_counts),
        "teams": output_teams,
    }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump(output, file, indent=2)

    print("Rotation engine builder created output successfully.")
    print(f"Teams: {output['team_count']}")
    print(f"Players: {output['player_count']}")
    print(f"Saved: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
