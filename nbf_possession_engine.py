import hashlib
import json
import random
from pathlib import Path

SNAPSHOT_FILE = Path("public_era_snapshot.json")
TENDENCIES_FILE = Path("player_tendencies.json")
COACH_SYSTEMS_FILE = Path("coach_systems.json")
ROTATION_FILE = Path("rotation_engine.json")

OUTPUT_FILE = Path("possession_engine_prototype_game.json")

ENGINE_NAME = "NBF Possession Engine Prototype"
ENGINE_VERSION = "0.1"
SEASON = 51
GAME_NUMBER = 1

HOME_TEAM = "Atlanta Monarchs"
AWAY_TEAM = "Philadelphia Riders"

REGULATION_QUARTERS = 4
REGULATION_SECONDS_PER_QUARTER = 12 * 60
OVERTIME_SECONDS = 5 * 60
SHOT_CLOCK_SECONDS = 24

REQUIRED_SNAPSHOT_FIELDS = {
    "player_id",
    "name",
    "team",
    "position",
    "overall",
    "offense",
    "defense",
    "shooting",
    "playmaking",
    "rebounding",
    "basketball_iq",
    "athleticism",
    "discipline",
    "confidence",
    "durability",
    "injury_risk",
}

REQUIRED_TENDENCY_FIELDS = {
    "player_id",
    "archetype",
    "shoot_tendency",
    "three_point_tendency",
    "midrange_tendency",
    "drive_tendency",
    "pass_tendency",
    "usage_tendency",
    "defensive_aggression",
    "rebound_focus",
    "clutch_tendency",
    "ball_dominance",
}

REQUIRED_ROTATION_FIELDS = {
    "player_id",
    "role",
    "minutes",
    "starter",
    "closer",
    "coach_trust",
    "system_fit",
}

REQUIRED_COACH_FIELDS = {
    "team",
    "offensive_system",
    "defensive_system",
    "pace",
    "rotation_tightness",
    "risk_tolerance",
    "player_development",
    "star_dependency",
}


def load_json(path):
    if not path.exists():
        raise FileNotFoundError(f"Required input file not found: {path}")

    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def deterministic_seed(*parts):
    seed_text = ":".join(str(part) for part in parts)

    return int(
        hashlib.sha256(seed_text.encode("utf-8")).hexdigest()[:16],
        16,
    )


def build_game_rng():
    seed = deterministic_seed(
        "NBF-LBU",
        "possession-prototype",
        ENGINE_VERSION,
        SEASON,
        GAME_NUMBER,
        HOME_TEAM,
        AWAY_TEAM,
    )

    return random.Random(seed), seed


def build_input_context():
    snapshot = load_json(SNAPSHOT_FILE)
    tendency_records = load_json(TENDENCIES_FILE)
    coach_records = load_json(COACH_SYSTEMS_FILE)
    rotation_data = load_json(ROTATION_FILE)

    errors = []

    snapshot_players = {}
    tendency_lookup = {}
    coach_lookup = {}
    rotation_lookup = {}

    snapshot_teams = snapshot.get("teams", {})
    rotation_teams = rotation_data.get("teams", {})

    for team_name, team in snapshot_teams.items():
        roster = team.get("roster", [])

        if not isinstance(roster, list):
            errors.append(f"{team_name} roster is not a list")
            continue

        for player in roster:
            player_id = player.get("player_id")
            missing = sorted(REQUIRED_SNAPSHOT_FIELDS - set(player))

            if missing:
                errors.append(
                    f"Snapshot player_id {player_id} missing fields: {missing}"
                )

            if player_id in snapshot_players:
                errors.append(
                    f"Duplicate snapshot player_id: {player_id}"
                )

            snapshot_players[player_id] = player

    for tendency in tendency_records:
        player_id = tendency.get("player_id")
        missing = sorted(REQUIRED_TENDENCY_FIELDS - set(tendency))

        if missing:
            errors.append(
                f"Tendency player_id {player_id} missing fields: {missing}"
            )

        if player_id in tendency_lookup:
            errors.append(
                f"Duplicate tendency player_id: {player_id}"
            )

        tendency_lookup[player_id] = tendency

    for coach in coach_records:
        team_name = coach.get("team")
        missing = sorted(REQUIRED_COACH_FIELDS - set(coach))

        if missing:
            errors.append(
                f"Coach system for {team_name} missing fields: {missing}"
            )

        if team_name in coach_lookup:
            errors.append(
                f"Duplicate coach-system team: {team_name}"
            )

        coach_lookup[team_name] = coach

    for team_name, team_rotation in rotation_teams.items():
        team_minutes = team_rotation.get("team_minutes")

        if team_minutes != 240:
            errors.append(
                f"{team_name} has {team_minutes} rotation minutes; expected 240"
            )

        for player in team_rotation.get("players", []):
            player_id = player.get("player_id")
            missing = sorted(REQUIRED_ROTATION_FIELDS - set(player))

            if missing:
                errors.append(
                    f"Rotation player_id {player_id} missing fields: {missing}"
                )

            if player_id in rotation_lookup:
                errors.append(
                    f"Duplicate rotation player_id: {player_id}"
                )

            rotation_lookup[player_id] = player

    snapshot_player_ids = set(snapshot_players)
    tendency_player_ids = set(tendency_lookup)
    rotation_player_ids = set(rotation_lookup)

    snapshot_team_names = set(snapshot_teams)
    rotation_team_names = set(rotation_teams)
    coach_team_names = set(coach_lookup)

    if snapshot_player_ids != tendency_player_ids:
        errors.append(
            "Snapshot and tendency player_id sets do not match"
        )

    if snapshot_player_ids != rotation_player_ids:
        errors.append(
            "Snapshot and rotation player_id sets do not match"
        )

    if snapshot_team_names != rotation_team_names:
        errors.append(
            "Snapshot and rotation team sets do not match"
        )

    if snapshot_team_names != coach_team_names:
        errors.append(
            "Snapshot and coach-system team sets do not match"
        )

    for required_team in [HOME_TEAM, AWAY_TEAM]:
        if required_team not in snapshot_teams:
            errors.append(
                f"Prototype team missing from snapshot: {required_team}"
            )

        if required_team not in rotation_teams:
            errors.append(
                f"Prototype team missing from rotations: {required_team}"
            )

        if required_team not in coach_lookup:
            errors.append(
                f"Prototype team missing from coach systems: {required_team}"
            )

    if errors:
        error_text = "\n".join(f"- {error}" for error in errors)

        raise ValueError(
            "Possession prototype input validation failed:\n"
            f"{error_text}"
        )

    joined_players = {}

    for player_id, snapshot_player in snapshot_players.items():
        joined_players[player_id] = {
            **snapshot_player,
            "tendencies": tendency_lookup[player_id],
            "rotation": rotation_lookup[player_id],
        }

    return {
        "snapshot": snapshot,
        "rotations": rotation_data,
        "players": joined_players,
        "coaches": coach_lookup,
    }


def get_team_context(context, team_name):
    snapshot_team = context["snapshot"]["teams"][team_name]
    rotation_team = context["rotations"]["teams"][team_name]

    players = []

    for rotation_player in rotation_team["players"]:
        player_id = rotation_player["player_id"]
        players.append(context["players"][player_id])

    players.sort(
        key=lambda player: (
            -player["rotation"]["minutes"],
            -player["rotation"]["deployment_score"],
            player["player_id"],
        )
    )

    starters = [
        player
        for player in players
        if player["rotation"]["starter"]
    ]

    closers = [
        player
        for player in players
        if player["rotation"]["closer"]
    ]

    if len(starters) != 5:
        raise ValueError(
            f"{team_name} has {len(starters)} starters; expected 5"
        )

    if len(closers) != 5:
        raise ValueError(
            f"{team_name} has {len(closers)} closers; expected 5"
        )

    return {
        "name": team_name,
        "snapshot": snapshot_team,
        "coach": context["coaches"][team_name],
        "players": players,
        "starters": starters,
        "closers": closers,
    }


def possession_controller_weight(player):
    rotation = player["rotation"]
    tendencies = player["tendencies"]

    minute_share = rotation["minutes"] / 48.0

    role_bonus = {
        "Franchise Star": 1.20,
        "Starter": 1.08,
        "Sixth Man": 1.04,
        "Rotation Player": 0.96,
        "Bench Player": 0.88,
        "Reserve": 0.80,
    }.get(rotation["role"], 1.00)

    opportunity_weight = (
        minute_share
        * (
            tendencies["usage_tendency"] * 0.45
            + tendencies["ball_dominance"] * 0.30
            + tendencies["pass_tendency"] * 0.10
            + player["playmaking"] * 0.08
            + rotation["coach_trust"] * 0.07
        )
        * role_bonus
    )

    return max(0.0001, opportunity_weight)


def select_active_lineup(team_context, game_phase="opening"):
    if game_phase == "closing":
        lineup = list(team_context["closers"])
    else:
        lineup = list(team_context["starters"])

    player_ids = [
        player["player_id"]
        for player in lineup
    ]

    if len(lineup) != 5:
        raise ValueError(
            f"{team_context['name']} active lineup contains "
            f"{len(lineup)} players; expected 5"
        )

    if len(set(player_ids)) != 5:
        raise ValueError(
            f"{team_context['name']} active lineup contains "
            "duplicate player_id values"
        )

    for player in lineup:
        if player["rotation"]["minutes"] <= 0:
            raise ValueError(
                f"{team_context['name']} active player has no "
                f"rotation opportunity: player_id {player['player_id']}"
            )

    return lineup


def select_possession_controller(active_lineup, rng):
    if len(active_lineup) != 5:
        raise ValueError(
            f"Possession controller requires five active players; "
            f"found {len(active_lineup)}"
        )

    weights = [
        possession_controller_weight(player)
        for player in active_lineup
    ]

    selected = rng.choices(
        active_lineup,
        weights=weights,
        k=1,
    )[0]

    return selected, weights


def validate_controller_selection(
    team_context,
    active_lineup,
    controller,
):
    team_player_ids = {
        player["player_id"]
        for player in team_context["players"]
    }

    active_player_ids = {
        player["player_id"]
        for player in active_lineup
    }

    if controller["player_id"] not in team_player_ids:
        raise ValueError(
            f"Selected controller is not on {team_context['name']}"
        )

    if controller["player_id"] not in active_player_ids:
        raise ValueError(
            f"Selected controller is not in the active lineup for "
            f"{team_context['name']}"
        )

    if controller["rotation"]["minutes"] <= 0:
        raise ValueError(
            f"Selected controller has no rotation opportunity: "
            f"player_id {controller['player_id']}"
        )


def position_number(position):
    position_numbers = {
        "PG": 1,
        "SG": 2,
        "SF": 3,
        "PF": 4,
        "C": 5,
    }

    if position not in position_numbers:
        raise ValueError(
            f"Unsupported basketball position: {position}"
        )

    return position_numbers[position]


def defender_matchup_weight(
    controller,
    defender,
    defensive_team_context,
):
    controller_position = position_number(
        controller["position"]
    )

    defender_position = position_number(
        defender["position"]
    )

    position_distance = abs(
        controller_position - defender_position
    )

    position_fit = {
        0: 100,
        1: 72,
        2: 34,
        3: 10,
        4: 2,
    }[position_distance]

    defensive_aggression = defender[
        "tendencies"
    ]["defensive_aggression"]

    defensive_system = defensive_team_context[
        "coach"
    ]["defensive_system"]

    system_bonus = 0.0

    if defensive_system == "Switching":
        if position_distance <= 1:
            system_bonus = 8.0
        elif position_distance == 2:
            system_bonus = 3.0

    elif defensive_system == "Drop Coverage":
        if defender["position"] in {"PF", "C"}:
            system_bonus = 6.0

        if controller["position"] in {"PG", "SG"}:
            system_bonus -= position_distance * 2.0

    matchup_weight = (
        position_fit * 0.42
        + defender["defense"] * 0.25
        + defender["athleticism"] * 0.12
        + defender["basketball_iq"] * 0.10
        + defensive_aggression * 0.07
        + defender["rotation"]["coach_trust"] * 0.04
        + system_bonus
    )

    return round(max(0.0001, matchup_weight), 4)


def select_primary_defender(
    controller,
    defensive_lineup,
    defensive_team_context,
):
    if len(defensive_lineup) != 5:
        raise ValueError(
            "Primary defender selection requires five active defenders; "
            f"found {len(defensive_lineup)}"
        )

    ranked_defenders = sorted(
        defensive_lineup,
        key=lambda defender: (
            defender_matchup_weight(
                controller,
                defender,
                defensive_team_context,
            ),
            defender["defense"],
            defender["athleticism"],
            defender["basketball_iq"],
            -defender["player_id"],
        ),
        reverse=True,
    )

    return ranked_defenders[0]


def validate_primary_defender(
    offensive_team_context,
    defensive_team_context,
    defensive_lineup,
    controller,
    defender,
):
    defensive_player_ids = {
        player["player_id"]
        for player in defensive_team_context["players"]
    }

    active_defender_ids = {
        player["player_id"]
        for player in defensive_lineup
    }

    offensive_player_ids = {
        player["player_id"]
        for player in offensive_team_context["players"]
    }

    if defender["player_id"] not in defensive_player_ids:
        raise ValueError(
            f"Selected defender is not on "
            f"{defensive_team_context['name']}"
        )

    if defender["player_id"] not in active_defender_ids:
        raise ValueError(
            f"Selected defender is not in the active lineup for "
            f"{defensive_team_context['name']}"
        )

    if defender["player_id"] in offensive_player_ids:
        raise ValueError(
            "Selected defender belongs to the offensive team"
        )

    if defender["player_id"] == controller["player_id"]:
        raise ValueError(
            "Possession controller and defender share a player_id"
        )


def possession_action_weights(
    controller,
    team_context,
):
    tendencies = controller["tendencies"]
    coach = team_context["coach"]
    position = controller["position"]
    archetype = tendencies["archetype"]

    weights = {
        "three_point_attempt": max(
            1.0,
            tendencies["three_point_tendency"],
        ),
        "midrange_attempt": max(
            1.0,
            tendencies["midrange_tendency"],
        ),
        "drive": max(
            1.0,
            tendencies["drive_tendency"],
        ),
        "post_up": max(
            1.0,
            (
                controller["offense"] * 0.35
                + controller["rebounding"] * 0.25
                + (
                    controller["strength"]
                    if "strength" in controller
                    else controller["athleticism"]
                ) * 0.20
                + controller["basketball_iq"] * 0.20
            ),
        ),
        "pass": max(
            1.0,
            tendencies["pass_tendency"],
        ),
        "draw_foul": max(
            1.0,
            (
                tendencies["drive_tendency"] * 0.45
                + controller["athleticism"] * 0.25
                + controller["offense"] * 0.20
                + controller["confidence"] * 0.10
            ),
        ),
    }

    if position in {"PG", "SG"}:
        weights["pass"] *= 1.08
        weights["three_point_attempt"] *= 1.05
        weights["post_up"] *= 0.45

    elif position == "SF":
        weights["drive"] *= 1.06
        weights["midrange_attempt"] *= 1.04
        weights["post_up"] *= 0.80

    elif position == "PF":
        weights["post_up"] *= 1.15
        weights["drive"] *= 1.04
        weights["three_point_attempt"] *= 0.90

    elif position == "C":
        weights["post_up"] *= 1.35
        weights["draw_foul"] *= 1.10
        weights["three_point_attempt"] *= 0.55
        weights["midrange_attempt"] *= 0.80

    archetype_adjustments = {
        "Playmaking Superstar": {
            "pass": 1.18,
            "drive": 1.12,
            "three_point_attempt": 1.08,
        },
        "Floor General": {
            "pass": 1.30,
            "drive": 0.95,
        },
        "Shot Creator": {
            "midrange_attempt": 1.25,
            "three_point_attempt": 1.12,
        },
        "Scoring Guard": {
            "three_point_attempt": 1.20,
            "drive": 1.12,
            "pass": 0.88,
        },
        "Playmaking Wing": {
            "pass": 1.16,
            "drive": 1.08,
        },
        "Point Forward": {
            "pass": 1.20,
            "drive": 1.08,
            "post_up": 1.08,
        },
        "Interior Anchor": {
            "post_up": 1.60,
            "three_point_attempt": 0.35,
        },
        "Stretch Big": {
            "three_point_attempt": 1.35,
            "post_up": 0.82,
        },
        "Athletic Slasher": {
            "drive": 1.35,
            "draw_foul": 1.22,
            "midrange_attempt": 0.82,
        },
        "Sixth-Man Scorer": {
            "three_point_attempt": 1.12,
            "midrange_attempt": 1.12,
            "drive": 1.08,
            "pass": 0.90,
        },
        "Rebounding Specialist": {
            "post_up": 1.12,
            "three_point_attempt": 0.72,
        },
    }

    for action, multiplier in archetype_adjustments.get(
        archetype,
        {},
    ).items():
        weights[action] *= multiplier

    if coach["offensive_system"] == "Pace and Space":
        weights["three_point_attempt"] *= 1.18
        weights["drive"] *= 1.08
        weights["pass"] *= 1.06
        weights["post_up"] *= 0.82

    elif coach["offensive_system"] == "Balanced":
        weights["pass"] *= 1.05
        weights["midrange_attempt"] *= 1.03

    normalized_weights = {
        action: round(max(0.01, weight), 4)
        for action, weight in weights.items()
    }

    return normalized_weights


def select_possession_action(
    controller,
    team_context,
    rng,
):
    action_weights = possession_action_weights(
        controller,
        team_context,
    )

    actions = list(action_weights)
    weights = [
        action_weights[action]
        for action in actions
    ]

    selected_action = rng.choices(
        actions,
        weights=weights,
        k=1,
    )[0]

    return selected_action, action_weights


def pass_target_weight(
    passer,
    receiver,
    offensive_team_context,
):
    receiver_tendencies = receiver["tendencies"]
    receiver_rotation = receiver["rotation"]
    offensive_system = offensive_team_context[
        "coach"
    ]["offensive_system"]

    scoring_readiness = (
        receiver["shooting"] * 0.28
        + receiver["offense"] * 0.20
        + receiver["athleticism"] * 0.12
        + receiver["basketball_iq"] * 0.10
        + receiver["confidence"] * 0.08
        + receiver_tendencies["shoot_tendency"] * 0.08
        + receiver_tendencies["three_point_tendency"] * 0.06
        + receiver_tendencies["drive_tendency"] * 0.04
        + receiver_rotation["coach_trust"] * 0.04
    )

    role_multiplier = {
        "Franchise Star": 1.20,
        "Starter": 1.08,
        "Sixth Man": 1.05,
        "Rotation Player": 0.98,
        "Bench Player": 0.90,
        "Reserve": 0.82,
    }.get(receiver_rotation["role"], 1.00)

    archetype_multiplier = {
        "Playmaking Superstar": 1.08,
        "Shot Creator": 1.10,
        "Scoring Guard": 1.10,
        "Playmaking Wing": 1.05,
        "Point Forward": 1.04,
        "Stretch Big": 1.08,
        "Athletic Slasher": 1.08,
        "Sixth-Man Scorer": 1.08,
        "Two-Way Star": 1.06,
    }.get(receiver_tendencies["archetype"], 1.00)

    system_multiplier = 1.00

    if offensive_system == "Pace and Space":
        system_multiplier += (
            receiver_tendencies["three_point_tendency"] - 70
        ) * 0.0025

        if receiver["position"] in {"PG", "SG", "SF"}:
            system_multiplier += 0.04

    elif offensive_system == "Balanced":
        system_multiplier += (
            receiver["basketball_iq"] - 70
        ) * 0.0015

    passer_receiver_fit = 1.00

    if passer["position"] in {"PG", "SG"}:
        if receiver["position"] in {"PF", "C"}:
            passer_receiver_fit += 0.03

    if passer["position"] in {"PF", "C"}:
        if receiver["position"] in {"PG", "SG", "SF"}:
            passer_receiver_fit += 0.04

    weight = (
        scoring_readiness
        * role_multiplier
        * archetype_multiplier
        * max(0.70, system_multiplier)
        * passer_receiver_fit
    )

    return round(max(0.0001, weight), 4)


def select_pass_target(
    passer,
    active_lineup,
    offensive_team_context,
    rng,
):
    eligible_receivers = [
        player
        for player in active_lineup
        if player["player_id"] != passer["player_id"]
    ]

    if len(eligible_receivers) != 4:
        raise ValueError(
            "Pass-target selection requires exactly four eligible "
            f"receivers; found {len(eligible_receivers)}"
        )

    weights = [
        pass_target_weight(
            passer,
            receiver,
            offensive_team_context,
        )
        for receiver in eligible_receivers
    ]

    receiver = rng.choices(
        eligible_receivers,
        weights=weights,
        k=1,
    )[0]

    return receiver, weights, eligible_receivers


def validate_pass_target(
    team_context,
    active_lineup,
    passer,
    receiver,
):
    team_player_ids = {
        player["player_id"]
        for player in team_context["players"]
    }

    active_player_ids = {
        player["player_id"]
        for player in active_lineup
    }

    if passer["player_id"] == receiver["player_id"]:
        raise ValueError(
            "Passer and receiver share the same player_id"
        )

    if receiver["player_id"] not in team_player_ids:
        raise ValueError(
            f"Pass receiver is not on {team_context['name']}"
        )

    if receiver["player_id"] not in active_player_ids:
        raise ValueError(
            f"Pass receiver is not in the active lineup for "
            f"{team_context['name']}"
        )

    if receiver["rotation"]["minutes"] <= 0:
        raise ValueError(
            f"Pass receiver has no rotation opportunity: "
            f"player_id {receiver['player_id']}"
        )


def clamp_probability(value, minimum, maximum):
    return max(minimum, min(maximum, value))


def calculate_pass_completion_probability(
    passer,
    receiver,
    primary_defender,
    offensive_team_context,
    defensive_team_context,
):
    passer_creation = (
        passer["playmaking"] * 0.38
        + passer["basketball_iq"] * 0.24
        + passer["discipline"] * 0.14
        + passer["confidence"] * 0.08
        + passer["tendencies"]["pass_tendency"] * 0.10
        + passer["rotation"]["coach_trust"] * 0.06
    )

    receiver_readiness = (
        receiver["basketball_iq"] * 0.35
        + receiver["athleticism"] * 0.25
        + receiver["confidence"] * 0.20
        + receiver["rotation"]["coach_trust"] * 0.20
    )

    defensive_pressure = (
        primary_defender["defense"] * 0.40
        + primary_defender["basketball_iq"] * 0.22
        + primary_defender["athleticism"] * 0.16
        + primary_defender["tendencies"]["defensive_aggression"] * 0.14
        + primary_defender["rotation"]["coach_trust"] * 0.08
    )

    probability = (
        0.865
        + (passer_creation - 75.0) * 0.0022
        + (receiver_readiness - 75.0) * 0.0008
        - (defensive_pressure - 75.0) * 0.0015
    )

    offensive_system = offensive_team_context[
        "coach"
    ]["offensive_system"]

    defensive_system = defensive_team_context[
        "coach"
    ]["defensive_system"]

    if offensive_system == "Pace and Space":
        probability += 0.012

    elif offensive_system == "Balanced":
        probability += 0.006

    if defensive_system == "Switching":
        probability -= 0.008

    elif defensive_system == "Drop Coverage":
        if receiver["position"] in {"PF", "C"}:
            probability -= 0.005

    if passer["position"] in {"PG", "SG"}:
        probability += 0.008

    if passer["tendencies"]["archetype"] in {
        "Floor General",
        "Playmaking Superstar",
        "Playmaking Wing",
        "Point Forward",
    }:
        probability += 0.012

    return round(
        clamp_probability(
            probability,
            0.70,
            0.97,
        ),
        4,
    )


def resolve_pass_outcome(
    passer,
    receiver,
    primary_defender,
    offensive_team_context,
    defensive_team_context,
    rng,
):
    completion_probability = (
        calculate_pass_completion_probability(
            passer,
            receiver,
            primary_defender,
            offensive_team_context,
            defensive_team_context,
        )
    )

    resolution_roll = rng.random()
    completed = resolution_roll < completion_probability

    if completed:
        outcome = "completed_pass"
        possession_continues = True
        next_controller_id = receiver["player_id"]
        turnover_player_id = None
        steal_player_id = None
    else:
        outcome = "turnover"
        possession_continues = False
        next_controller_id = None
        turnover_player_id = passer["player_id"]

        steal_probability = clamp_probability(
            0.38
            + (
                primary_defender["tendencies"]["defensive_aggression"]
                - 70
            ) * 0.004
            + (primary_defender["defense"] - 70) * 0.003,
            0.25,
            0.75,
        )

        steal_player_id = (
            primary_defender["player_id"]
            if rng.random() < steal_probability
            else None
        )

    return {
        "outcome": outcome,
        "completed": completed,
        "completion_probability": completion_probability,
        "resolution_roll": round(resolution_roll, 6),
        "possession_continues": possession_continues,
        "passer_player_id": passer["player_id"],
        "receiver_player_id": receiver["player_id"],
        "next_controller_player_id": next_controller_id,
        "turnover_player_id": turnover_player_id,
        "steal_player_id": steal_player_id,
        "points_scored": 0,
    }


def validate_pass_outcome(
    passer,
    receiver,
    primary_defender,
    outcome,
):
    required_fields = {
        "outcome",
        "completed",
        "completion_probability",
        "resolution_roll",
        "possession_continues",
        "passer_player_id",
        "receiver_player_id",
        "next_controller_player_id",
        "turnover_player_id",
        "steal_player_id",
        "points_scored",
    }

    missing_fields = sorted(
        required_fields - set(outcome)
    )

    if missing_fields:
        raise ValueError(
            f"Pass outcome missing fields: {missing_fields}"
        )

    if outcome["outcome"] not in {
        "completed_pass",
        "turnover",
    }:
        raise ValueError(
            f"Invalid pass outcome: {outcome['outcome']}"
        )

    if not 0.70 <= outcome["completion_probability"] <= 0.97:
        raise ValueError(
            "Pass completion probability is outside the "
            "approved 0.70-0.97 range"
        )

    if not 0.0 <= outcome["resolution_roll"] <= 1.0:
        raise ValueError(
            "Pass resolution roll is outside the 0.0-1.0 range"
        )

    if outcome["passer_player_id"] != passer["player_id"]:
        raise ValueError(
            "Pass outcome passer_player_id does not match the passer"
        )

    if outcome["receiver_player_id"] != receiver["player_id"]:
        raise ValueError(
            "Pass outcome receiver_player_id does not match the receiver"
        )

    if outcome["points_scored"] != 0:
        raise ValueError(
            "A pass event cannot directly score points"
        )

    if outcome["completed"]:
        if outcome["outcome"] != "completed_pass":
            raise ValueError(
                "Completed pass has an inconsistent outcome label"
            )

        if not outcome["possession_continues"]:
            raise ValueError(
                "Completed pass must continue the possession"
            )

        if (
            outcome["next_controller_player_id"]
            != receiver["player_id"]
        ):
            raise ValueError(
                "Completed pass must transfer control to the receiver"
            )

        if outcome["turnover_player_id"] is not None:
            raise ValueError(
                "Completed pass cannot assign a turnover"
            )

        if outcome["steal_player_id"] is not None:
            raise ValueError(
                "Completed pass cannot assign a steal"
            )

    else:
        if outcome["outcome"] != "turnover":
            raise ValueError(
                "Failed pass has an inconsistent outcome label"
            )

        if outcome["possession_continues"]:
            raise ValueError(
                "Turnover cannot continue the offensive possession"
            )

        if outcome["next_controller_player_id"] is not None:
            raise ValueError(
                "Turnover cannot assign a next offensive controller"
            )

        if outcome["turnover_player_id"] != passer["player_id"]:
            raise ValueError(
                "Failed pass must assign the turnover to the passer"
            )

        if (
            outcome["steal_player_id"] is not None
            and outcome["steal_player_id"]
            != primary_defender["player_id"]
        ):
            raise ValueError(
                "Steal player_id does not match the primary defender"
            )


def calculate_terminal_action_probabilities(
    action,
    controller,
    primary_defender,
    offensive_team_context,
    defensive_team_context,
):
    terminal_actions = {
        "three_point_attempt",
        "midrange_attempt",
        "drive",
        "post_up",
        "draw_foul",
    }

    if action not in terminal_actions:
        raise ValueError(
            f"Terminal probability calculation does not support: {action}"
        )

    offensive_system = offensive_team_context[
        "coach"
    ]["offensive_system"]

    defensive_system = defensive_team_context[
        "coach"
    ]["defensive_system"]

    offensive_quality = (
        controller["offense"] * 0.26
        + controller["shooting"] * 0.22
        + controller["athleticism"] * 0.14
        + controller["basketball_iq"] * 0.14
        + controller["confidence"] * 0.10
        + controller["rotation"]["coach_trust"] * 0.08
        + controller["tendencies"]["clutch_tendency"] * 0.06
    )

    defensive_pressure = (
        primary_defender["defense"] * 0.38
        + primary_defender["athleticism"] * 0.18
        + primary_defender["basketball_iq"] * 0.16
        + primary_defender["tendencies"][
            "defensive_aggression"
        ] * 0.16
        + primary_defender["rotation"]["coach_trust"] * 0.12
    )

    quality_margin = offensive_quality - defensive_pressure

    if action == "three_point_attempt":
        make_probability = (
            0.335
            + (controller["shooting"] - 75) * 0.0040
            + (
                controller["tendencies"]["three_point_tendency"] - 75
            ) * 0.0007
            + quality_margin * 0.0016
        )

        foul_probability = (
            0.025
            + (
                primary_defender["tendencies"][
                    "defensive_aggression"
                ] - 70
            ) * 0.0005
        )

        turnover_probability = 0.015

        block_probability = (
            0.012
            + (primary_defender["defense"] - 75) * 0.0004
        )

        if offensive_system == "Pace and Space":
            make_probability += 0.010

        if defensive_system == "Switching":
            make_probability -= 0.008

    elif action == "midrange_attempt":
        make_probability = (
            0.405
            + (controller["shooting"] - 75) * 0.0035
            + (
                controller["tendencies"]["midrange_tendency"] - 75
            ) * 0.0008
            + quality_margin * 0.0017
        )

        foul_probability = (
            0.035
            + (
                primary_defender["tendencies"][
                    "defensive_aggression"
                ] - 70
            ) * 0.0006
        )

        turnover_probability = 0.018

        block_probability = (
            0.020
            + (primary_defender["defense"] - 75) * 0.0006
        )

        if offensive_system == "Balanced":
            make_probability += 0.006

    elif action == "drive":
        make_probability = (
            0.490
            + (controller["athleticism"] - 75) * 0.0028
            + (controller["offense"] - 75) * 0.0020
            + (
                controller["tendencies"]["drive_tendency"] - 75
            ) * 0.0010
            + quality_margin * 0.0013
        )

        foul_probability = (
            0.160
            + (controller["athleticism"] - 75) * 0.0015
            + (
                primary_defender["tendencies"][
                    "defensive_aggression"
                ] - 70
            ) * 0.0012
        )

        turnover_probability = (
            0.085
            - (controller["basketball_iq"] - 75) * 0.0010
            - (controller["discipline"] - 75) * 0.0007
            + (primary_defender["defense"] - 75) * 0.0010
        )

        block_probability = (
            0.055
            + (primary_defender["defense"] - 75) * 0.0010
            + (primary_defender["athleticism"] - 75) * 0.0007
        )

        if offensive_system == "Pace and Space":
            make_probability += 0.008

        if defensive_system == "Drop Coverage":
            block_probability += 0.010

    elif action == "post_up":
        interior_offense = (
            controller["offense"] * 0.36
            + controller["rebounding"] * 0.22
            + controller["athleticism"] * 0.16
            + controller["basketball_iq"] * 0.16
            + controller["confidence"] * 0.10
        )

        interior_defense = (
            primary_defender["defense"] * 0.44
            + primary_defender["rebounding"] * 0.20
            + primary_defender["athleticism"] * 0.16
            + primary_defender["basketball_iq"] * 0.20
        )

        interior_margin = interior_offense - interior_defense

        make_probability = (
            0.475
            + interior_margin * 0.0022
        )

        foul_probability = (
            0.145
            + (
                primary_defender["tendencies"][
                    "defensive_aggression"
                ] - 70
            ) * 0.0012
        )

        turnover_probability = (
            0.075
            - (controller["discipline"] - 75) * 0.0008
            + (primary_defender["defense"] - 75) * 0.0009
        )

        block_probability = (
            0.050
            + (primary_defender["defense"] - 75) * 0.0009
            + (primary_defender["athleticism"] - 75) * 0.0005
        )

        if defensive_system == "Drop Coverage":
            make_probability -= 0.008
            block_probability += 0.008

    else:
        make_probability = (
            0.445
            + (controller["offense"] - 75) * 0.0022
            + (controller["athleticism"] - 75) * 0.0018
            + quality_margin * 0.0012
        )

        foul_probability = (
            0.520
            + (
                controller["tendencies"]["drive_tendency"] - 75
            ) * 0.0015
            + (
                primary_defender["tendencies"][
                    "defensive_aggression"
                ] - 70
            ) * 0.0014
        )

        turnover_probability = (
            0.060
            - (controller["discipline"] - 75) * 0.0006
            + (primary_defender["defense"] - 75) * 0.0007
        )

        block_probability = (
            0.030
            + (primary_defender["defense"] - 75) * 0.0006
        )

    probabilities = {
        "make_probability": round(
            clamp_probability(
                make_probability,
                0.20,
                0.72,
            ),
            4,
        ),
        "foul_probability": round(
            clamp_probability(
                foul_probability,
                0.01,
                0.70,
            ),
            4,
        ),
        "turnover_probability": round(
            clamp_probability(
                turnover_probability,
                0.01,
                0.20,
            ),
            4,
        ),
        "block_probability": round(
            clamp_probability(
                block_probability,
                0.005,
                0.18,
            ),
            4,
        ),
    }

    return probabilities


def validate_terminal_action_probabilities(
    action,
    probabilities,
):
    expected_fields = {
        "make_probability",
        "foul_probability",
        "turnover_probability",
        "block_probability",
    }

    if set(probabilities) != expected_fields:
        raise ValueError(
            "Terminal action probability fields are invalid"
        )

    approved_ranges = {
        "make_probability": (0.20, 0.72),
        "foul_probability": (0.01, 0.70),
        "turnover_probability": (0.01, 0.20),
        "block_probability": (0.005, 0.18),
    }

    for field, value in probabilities.items():
        minimum, maximum = approved_ranges[field]

        if not minimum <= value <= maximum:
            raise ValueError(
                f"{action} {field}={value} is outside "
                f"the approved {minimum}-{maximum} range"
            )


def resolve_terminal_action_outcome(
    action,
    controller,
    primary_defender,
    offensive_team_context,
    defensive_team_context,
    rng,
):
    probabilities = calculate_terminal_action_probabilities(
        action,
        controller,
        primary_defender,
        offensive_team_context,
        defensive_team_context,
    )

    validate_terminal_action_probabilities(
        action,
        probabilities,
    )

    turnover_roll = rng.random()
    foul_roll = rng.random()
    block_roll = rng.random()
    make_roll = rng.random()

    points_available = (
        3
        if action == "three_point_attempt"
        else 2
    )

    if turnover_roll < probabilities["turnover_probability"]:
        outcome = "turnover"
        points_scored = 0
        possession_continues = False
        shot_attempted = False
        shot_made = False
        foul_drawn = False
        blocked = False
        rebound_required = False
        turnover_player_id = controller["player_id"]

        steal_probability = clamp_probability(
            0.32
            + (
                primary_defender["tendencies"][
                    "defensive_aggression"
                ] - 70
            ) * 0.004
            + (primary_defender["defense"] - 70) * 0.003,
            0.20,
            0.72,
        )

        steal_player_id = (
            primary_defender["player_id"]
            if rng.random() < steal_probability
            else None
        )

    elif foul_roll < probabilities["foul_probability"]:
        outcome = "shooting_foul"
        points_scored = 0
        possession_continues = False
        shot_attempted = False
        shot_made = False
        foul_drawn = True
        blocked = False
        rebound_required = False
        turnover_player_id = None
        steal_player_id = None

    elif block_roll < probabilities["block_probability"]:
        outcome = "blocked_shot"
        points_scored = 0
        possession_continues = True
        shot_attempted = True
        shot_made = False
        foul_drawn = False
        blocked = True
        rebound_required = True
        turnover_player_id = None
        steal_player_id = None

    elif make_roll < probabilities["make_probability"]:
        outcome = "made_shot"
        points_scored = points_available
        possession_continues = False
        shot_attempted = True
        shot_made = True
        foul_drawn = False
        blocked = False
        rebound_required = False
        turnover_player_id = None
        steal_player_id = None

    else:
        outcome = "missed_shot"
        points_scored = 0
        possession_continues = True
        shot_attempted = True
        shot_made = False
        foul_drawn = False
        blocked = False
        rebound_required = True
        turnover_player_id = None
        steal_player_id = None

    return {
        "action": action,
        "outcome": outcome,
        "controller_player_id": controller["player_id"],
        "primary_defender_player_id": primary_defender["player_id"],
        "points_available": points_available,
        "points_scored": points_scored,
        "possession_continues": possession_continues,
        "shot_attempted": shot_attempted,
        "shot_made": shot_made,
        "foul_drawn": foul_drawn,
        "blocked": blocked,
        "rebound_required": rebound_required,
        "turnover_player_id": turnover_player_id,
        "steal_player_id": steal_player_id,
        "probabilities": probabilities,
        "rolls": {
            "turnover_roll": round(turnover_roll, 6),
            "foul_roll": round(foul_roll, 6),
            "block_roll": round(block_roll, 6),
            "make_roll": round(make_roll, 6),
        },
    }


def validate_terminal_action_outcome(
    action,
    controller,
    primary_defender,
    outcome,
):
    valid_actions = {
        "three_point_attempt",
        "midrange_attempt",
        "drive",
        "post_up",
        "draw_foul",
    }

    valid_outcomes = {
        "turnover",
        "shooting_foul",
        "blocked_shot",
        "made_shot",
        "missed_shot",
    }

    required_fields = {
        "action",
        "outcome",
        "controller_player_id",
        "primary_defender_player_id",
        "points_available",
        "points_scored",
        "possession_continues",
        "shot_attempted",
        "shot_made",
        "foul_drawn",
        "blocked",
        "rebound_required",
        "turnover_player_id",
        "steal_player_id",
        "probabilities",
        "rolls",
    }

    missing_fields = sorted(required_fields - set(outcome))

    if missing_fields:
        raise ValueError(
            f"Terminal outcome missing fields: {missing_fields}"
        )

    if action not in valid_actions:
        raise ValueError(
            f"Unsupported terminal action: {action}"
        )

    if outcome["action"] != action:
        raise ValueError(
            "Terminal outcome action does not match the input action"
        )

    if outcome["outcome"] not in valid_outcomes:
        raise ValueError(
            f"Invalid terminal outcome: {outcome['outcome']}"
        )

    if outcome["controller_player_id"] != controller["player_id"]:
        raise ValueError(
            "Terminal outcome controller_player_id is invalid"
        )

    if (
        outcome["primary_defender_player_id"]
        != primary_defender["player_id"]
    ):
        raise ValueError(
            "Terminal outcome primary_defender_player_id is invalid"
        )

    expected_points_available = (
        3
        if action == "three_point_attempt"
        else 2
    )

    if outcome["points_available"] != expected_points_available:
        raise ValueError(
            "Terminal outcome points_available is invalid"
        )

    if outcome["points_scored"] not in {
        0,
        expected_points_available,
    }:
        raise ValueError(
            f"Invalid points_scored: {outcome['points_scored']}"
        )

    validate_terminal_action_probabilities(
        action,
        outcome["probabilities"],
    )

    expected_rolls = {
        "turnover_roll",
        "foul_roll",
        "block_roll",
        "make_roll",
    }

    if set(outcome["rolls"]) != expected_rolls:
        raise ValueError(
            "Terminal outcome roll fields are invalid"
        )

    for roll_name, roll_value in outcome["rolls"].items():
        if not 0.0 <= roll_value <= 1.0:
            raise ValueError(
                f"{roll_name} is outside the 0.0-1.0 range"
            )

    if outcome["outcome"] == "turnover":
        if outcome["points_scored"] != 0:
            raise ValueError(
                "Turnover cannot score points"
            )

        if outcome["possession_continues"]:
            raise ValueError(
                "Turnover cannot continue the offensive possession"
            )

        if outcome["turnover_player_id"] != controller["player_id"]:
            raise ValueError(
                "Turnover must be assigned to the controller"
            )

        if (
            outcome["steal_player_id"] is not None
            and outcome["steal_player_id"]
            != primary_defender["player_id"]
        ):
            raise ValueError(
                "Steal must be assigned to the primary defender"
            )

    elif outcome["outcome"] == "shooting_foul":
        if not outcome["foul_drawn"]:
            raise ValueError(
                "Shooting-foul outcome must mark foul_drawn"
            )

        if outcome["points_scored"] != 0:
            raise ValueError(
                "Free-throw points must not be awarded by this event"
            )

        if outcome["rebound_required"]:
            raise ValueError(
                "Shooting foul cannot require a rebound yet"
            )

    elif outcome["outcome"] == "blocked_shot":
        if not outcome["blocked"]:
            raise ValueError(
                "Blocked-shot outcome must mark blocked"
            )

        if not outcome["shot_attempted"]:
            raise ValueError(
                "Blocked shot must count as a shot attempt"
            )

        if not outcome["rebound_required"]:
            raise ValueError(
                "Blocked shot must require rebound resolution"
            )

    elif outcome["outcome"] == "made_shot":
        if not outcome["shot_attempted"]:
            raise ValueError(
                "Made shot must count as a shot attempt"
            )

        if not outcome["shot_made"]:
            raise ValueError(
                "Made-shot outcome must mark shot_made"
            )

        if outcome["points_scored"] != expected_points_available:
            raise ValueError(
                "Made shot awarded an incorrect point value"
            )

        if outcome["possession_continues"]:
            raise ValueError(
                "Made shot must end the offensive possession"
            )

        if outcome["rebound_required"]:
            raise ValueError(
                "Made shot cannot require a rebound"
            )

    elif outcome["outcome"] == "missed_shot":
        if not outcome["shot_attempted"]:
            raise ValueError(
                "Missed shot must count as a shot attempt"
            )

        if outcome["shot_made"]:
            raise ValueError(
                "Missed-shot outcome cannot mark shot_made"
            )

        if outcome["points_scored"] != 0:
            raise ValueError(
                "Missed shot cannot score points"
            )

        if not outcome["rebound_required"]:
            raise ValueError(
                "Missed shot must require rebound resolution"
            )


def rebound_player_weight(
    player,
    rebound_type,
):
    tendencies = player["tendencies"]
    rotation = player["rotation"]

    position_multiplier = {
        "PG": 0.72,
        "SG": 0.82,
        "SF": 1.00,
        "PF": 1.18,
        "C": 1.28,
    }.get(player["position"], 1.00)

    if rebound_type == "offensive":
        weight = (
            player["rebounding"] * 0.38
            + player["athleticism"] * 0.22
            + tendencies["rebound_focus"] * 0.22
            + player["offense"] * 0.08
            + player["basketball_iq"] * 0.06
            + rotation["coach_trust"] * 0.04
        )

        archetype_multiplier = {
            "Rebounding Specialist": 1.22,
            "Interior Anchor": 1.12,
            "Athletic Slasher": 1.04,
            "Stretch Big": 0.94,
        }.get(tendencies["archetype"], 1.00)

    elif rebound_type == "defensive":
        weight = (
            player["rebounding"] * 0.42
            + player["athleticism"] * 0.18
            + tendencies["rebound_focus"] * 0.20
            + player["defense"] * 0.08
            + player["basketball_iq"] * 0.08
            + rotation["coach_trust"] * 0.04
        )

        archetype_multiplier = {
            "Rebounding Specialist": 1.25,
            "Interior Anchor": 1.16,
            "Defensive Specialist": 1.06,
            "Two-Way Star": 1.04,
        }.get(tendencies["archetype"], 1.00)

    else:
        raise ValueError(
            f"Unsupported rebound type: {rebound_type}"
        )

    final_weight = (
        weight
        * position_multiplier
        * archetype_multiplier
    )

    return round(max(0.0001, final_weight), 4)


def calculate_offensive_rebound_probability(
    offensive_lineup,
    defensive_lineup,
    offensive_team_context,
    defensive_team_context,
):
    if len(offensive_lineup) != 5:
        raise ValueError(
            "Offensive rebound calculation requires five "
            f"offensive players; found {len(offensive_lineup)}"
        )

    if len(defensive_lineup) != 5:
        raise ValueError(
            "Offensive rebound calculation requires five "
            f"defensive players; found {len(defensive_lineup)}"
        )

    offensive_strength = sum(
        rebound_player_weight(
            player,
            "offensive",
        )
        for player in offensive_lineup
    )

    defensive_strength = sum(
        rebound_player_weight(
            player,
            "defensive",
        )
        for player in defensive_lineup
    )

    total_strength = offensive_strength + defensive_strength

    if total_strength <= 0:
        raise ValueError(
            "Combined rebound strength must be positive"
        )

    raw_offensive_share = (
        offensive_strength / total_strength
    )

    probability = (
        0.255
        + (raw_offensive_share - 0.50) * 0.55
    )

    offensive_system = offensive_team_context[
        "coach"
    ]["offensive_system"]

    defensive_system = defensive_team_context[
        "coach"
    ]["defensive_system"]

    if offensive_system == "Pace and Space":
        probability -= 0.008

    elif offensive_system == "Balanced":
        probability += 0.004

    if defensive_system == "Drop Coverage":
        probability -= 0.010

    elif defensive_system == "Switching":
        probability += 0.004

    return round(
        clamp_probability(
            probability,
            0.16,
            0.38,
        ),
        4,
    )


def validate_offensive_rebound_probability(
    probability,
):
    if not isinstance(probability, (int, float)):
        raise ValueError(
            "Offensive-rebound probability must be numeric"
        )

    if not 0.16 <= probability <= 0.38:
        raise ValueError(
            "Offensive-rebound probability is outside the "
            "approved 0.16-0.38 range"
        )


def select_rebounder(
    lineup,
    rebound_type,
    rng,
):
    if len(lineup) != 5:
        raise ValueError(
            "Rebounder selection requires five active players; "
            f"found {len(lineup)}"
        )

    if rebound_type not in {
        "offensive",
        "defensive",
    }:
        raise ValueError(
            f"Unsupported rebound type: {rebound_type}"
        )

    player_ids = [
        player["player_id"]
        for player in lineup
    ]

    if len(set(player_ids)) != 5:
        raise ValueError(
            "Rebounder selection lineup contains duplicate "
            "player_id values"
        )

    weights = [
        rebound_player_weight(
            player,
            rebound_type,
        )
        for player in lineup
    ]

    if any(weight <= 0 for weight in weights):
        raise ValueError(
            "All rebounder-selection weights must be positive"
        )

    rebounder = rng.choices(
        lineup,
        weights=weights,
        k=1,
    )[0]

    return rebounder, weights


def validate_rebounder_selection(
    lineup,
    rebound_type,
    rebounder,
    weights,
):
    if len(lineup) != 5:
        raise ValueError(
            "Rebounder validation requires five active players"
        )

    if rebound_type not in {
        "offensive",
        "defensive",
    }:
        raise ValueError(
            f"Unsupported rebound type: {rebound_type}"
        )

    lineup_player_ids = {
        player["player_id"]
        for player in lineup
    }

    if rebounder["player_id"] not in lineup_player_ids:
        raise ValueError(
            "Selected rebounder is not in the active lineup"
        )

    if len(weights) != 5:
        raise ValueError(
            f"Rebounder selection returned {len(weights)} weights; "
            "expected 5"
        )

    if any(
        not isinstance(weight, (int, float))
        for weight in weights
    ):
        raise ValueError(
            "Rebounder-selection weights must be numeric"
        )

    if any(weight <= 0 for weight in weights):
        raise ValueError(
            "Rebounder-selection weights must be positive"
        )

    expected_weights = [
        rebound_player_weight(
            player,
            rebound_type,
        )
        for player in lineup
    ]

    if weights != expected_weights:
        raise ValueError(
            "Rebounder-selection weights do not match the "
            "active lineup"
        )


def resolve_rebound(
    offensive_lineup,
    defensive_lineup,
    offensive_team_context,
    defensive_team_context,
    rng,
):
    offensive_rebound_probability = (
        calculate_offensive_rebound_probability(
            offensive_lineup,
            defensive_lineup,
            offensive_team_context,
            defensive_team_context,
        )
    )

    validate_offensive_rebound_probability(
        offensive_rebound_probability,
    )

    resolution_roll = rng.random()

    offensive_rebound = (
        resolution_roll < offensive_rebound_probability
    )

    if offensive_rebound:
        rebound_type = "offensive"

        rebounder, rebound_weights = select_rebounder(
            offensive_lineup,
            rebound_type,
            rng,
        )

        validate_rebounder_selection(
            offensive_lineup,
            rebound_type,
            rebounder,
            rebound_weights,
        )

        possession_continues = True
        possession_changes = False
        next_offense_team = offensive_team_context["name"]
        next_controller_player_id = rebounder["player_id"]

    else:
        rebound_type = "defensive"

        rebounder, rebound_weights = select_rebounder(
            defensive_lineup,
            rebound_type,
            rng,
        )

        validate_rebounder_selection(
            defensive_lineup,
            rebound_type,
            rebounder,
            rebound_weights,
        )

        possession_continues = False
        possession_changes = True
        next_offense_team = defensive_team_context["name"]
        next_controller_player_id = rebounder["player_id"]

    return {
        "outcome": f"{rebound_type}_rebound",
        "rebound_type": rebound_type,
        "offensive_rebound": offensive_rebound,
        "offensive_rebound_probability": (
            offensive_rebound_probability
        ),
        "resolution_roll": round(resolution_roll, 6),
        "rebounder_player_id": rebounder["player_id"],
        "rebounder_name": rebounder["name"],
        "rebounder_team": rebounder["team"],
        "possession_continues": possession_continues,
        "possession_changes": possession_changes,
        "next_offense_team": next_offense_team,
        "next_controller_player_id": next_controller_player_id,
        "points_scored": 0,
        "rebound_weights": [
            round(weight, 4)
            for weight in rebound_weights
        ],
    }


def validate_rebound_outcome(
    offensive_team_context,
    defensive_team_context,
    offensive_lineup,
    defensive_lineup,
    outcome,
):
    required_fields = {
        "outcome",
        "rebound_type",
        "offensive_rebound",
        "offensive_rebound_probability",
        "resolution_roll",
        "rebounder_player_id",
        "rebounder_name",
        "rebounder_team",
        "possession_continues",
        "possession_changes",
        "next_offense_team",
        "next_controller_player_id",
        "points_scored",
        "rebound_weights",
    }

    missing_fields = sorted(
        required_fields - set(outcome)
    )

    if missing_fields:
        raise ValueError(
            f"Rebound outcome missing fields: {missing_fields}"
        )

    if outcome["rebound_type"] not in {
        "offensive",
        "defensive",
    }:
        raise ValueError(
            f"Invalid rebound type: {outcome['rebound_type']}"
        )

    expected_outcome = (
        f"{outcome['rebound_type']}_rebound"
    )

    if outcome["outcome"] != expected_outcome:
        raise ValueError(
            "Rebound outcome label is inconsistent"
        )

    validate_offensive_rebound_probability(
        outcome["offensive_rebound_probability"],
    )

    if not 0.0 <= outcome["resolution_roll"] <= 1.0:
        raise ValueError(
            "Rebound resolution roll is outside the 0.0-1.0 range"
        )

    if outcome["points_scored"] != 0:
        raise ValueError(
            "A rebound event cannot directly score points"
        )

    if len(outcome["rebound_weights"]) != 5:
        raise ValueError(
            "Rebound outcome must contain five rebound weights"
        )

    if any(
        not isinstance(weight, (int, float))
        for weight in outcome["rebound_weights"]
    ):
        raise ValueError(
            "Rebound weights must be numeric"
        )

    if any(
        weight <= 0
        for weight in outcome["rebound_weights"]
    ):
        raise ValueError(
            "Rebound weights must all be positive"
        )

    offensive_players = {
        player["player_id"]: player
        for player in offensive_lineup
    }

    defensive_players = {
        player["player_id"]: player
        for player in defensive_lineup
    }

    combined_player_ids = (
        set(offensive_players)
        | set(defensive_players)
    )

    if (
        outcome["rebounder_player_id"]
        not in combined_player_ids
    ):
        raise ValueError(
            "Rebounder is not in either active lineup"
        )

    if (
        outcome["next_controller_player_id"]
        != outcome["rebounder_player_id"]
    ):
        raise ValueError(
            "Next controller must be the selected rebounder"
        )

    if outcome["offensive_rebound"]:
        if outcome["rebound_type"] != "offensive":
            raise ValueError(
                "Offensive rebound has an inconsistent rebound type"
            )

        if (
            outcome["rebounder_player_id"]
            not in offensive_players
        ):
            raise ValueError(
                "Offensive rebounder is not in the offensive lineup"
            )

        rebounder = offensive_players[
            outcome["rebounder_player_id"]
        ]

        if outcome["rebounder_name"] != rebounder["name"]:
            raise ValueError(
                "Offensive rebounder name is inconsistent"
            )

        if (
            outcome["rebounder_team"]
            != offensive_team_context["name"]
        ):
            raise ValueError(
                "Offensive rebounder team is invalid"
            )

        if not outcome["possession_continues"]:
            raise ValueError(
                "Offensive rebound must continue the possession"
            )

        if outcome["possession_changes"]:
            raise ValueError(
                "Offensive rebound cannot change possession"
            )

        if (
            outcome["next_offense_team"]
            != offensive_team_context["name"]
        ):
            raise ValueError(
                "Offensive rebound assigned the wrong next offense"
            )

    else:
        if outcome["rebound_type"] != "defensive":
            raise ValueError(
                "Defensive rebound has an inconsistent rebound type"
            )

        if (
            outcome["rebounder_player_id"]
            not in defensive_players
        ):
            raise ValueError(
                "Defensive rebounder is not in the defensive lineup"
            )

        rebounder = defensive_players[
            outcome["rebounder_player_id"]
        ]

        if outcome["rebounder_name"] != rebounder["name"]:
            raise ValueError(
                "Defensive rebounder name is inconsistent"
            )

        if (
            outcome["rebounder_team"]
            != defensive_team_context["name"]
        ):
            raise ValueError(
                "Defensive rebounder team is invalid"
            )

        if outcome["possession_continues"]:
            raise ValueError(
                "Defensive rebound cannot continue the old possession"
            )

        if not outcome["possession_changes"]:
            raise ValueError(
                "Defensive rebound must change possession"
            )

        if (
            outcome["next_offense_team"]
            != defensive_team_context["name"]
        ):
            raise ValueError(
                "Defensive rebound assigned the wrong next offense"
            )


def calculate_free_throw_probability(
    shooter,
):
    probability = (
        0.625
        + (shooter["shooting"] - 70) * 0.0040
        + (shooter["confidence"] - 70) * 0.0015
        + (shooter["discipline"] - 70) * 0.0010
        + (shooter["basketball_iq"] - 70) * 0.0008
    )

    return round(
        clamp_probability(
            probability,
            0.55,
            0.95,
        ),
        4,
    )


def determine_free_throw_attempts(
    action,
    terminal_outcome,
):
    if terminal_outcome["outcome"] != "shooting_foul":
        raise ValueError(
            "Free throws require a shooting-foul terminal outcome"
        )

    if action == "three_point_attempt":
        return 3

    if action in {
        "midrange_attempt",
        "drive",
        "post_up",
        "draw_foul",
    }:
        return 2

    raise ValueError(
        f"Unsupported free-throw action: {action}"
    )


def resolve_free_throws(
    action,
    shooter,
    terminal_outcome,
    rng,
):
    attempts = determine_free_throw_attempts(
        action,
        terminal_outcome,
    )

    make_probability = calculate_free_throw_probability(
        shooter,
    )

    attempt_results = []
    makes = 0

    for attempt_number in range(1, attempts + 1):
        resolution_roll = rng.random()
        made = resolution_roll < make_probability

        if made:
            makes += 1

        attempt_results.append(
            {
                "attempt_number": attempt_number,
                "made": made,
                "resolution_roll": round(
                    resolution_roll,
                    6,
                ),
                "make_probability": make_probability,
                "points_scored": 1 if made else 0,
            }
        )

    final_attempt_made = attempt_results[-1]["made"]
    rebound_required = not final_attempt_made

    return {
        "outcome": "free_throws",
        "action": action,
        "shooter_player_id": shooter["player_id"],
        "shooter_name": shooter["name"],
        "attempts": attempts,
        "makes": makes,
        "misses": attempts - makes,
        "points_scored": makes,
        "make_probability": make_probability,
        "attempt_results": attempt_results,
        "final_attempt_made": final_attempt_made,
        "rebound_required": rebound_required,
        "possession_continues": rebound_required,
        "possession_changes": final_attempt_made,
    }


def validate_free_throw_outcome(
    action,
    shooter,
    terminal_outcome,
    outcome,
):
    required_fields = {
        "outcome",
        "action",
        "shooter_player_id",
        "shooter_name",
        "attempts",
        "makes",
        "misses",
        "points_scored",
        "make_probability",
        "attempt_results",
        "final_attempt_made",
        "rebound_required",
        "possession_continues",
        "possession_changes",
    }

    missing_fields = sorted(
        required_fields - set(outcome)
    )

    if missing_fields:
        raise ValueError(
            f"Free-throw outcome missing fields: {missing_fields}"
        )

    if terminal_outcome["outcome"] != "shooting_foul":
        raise ValueError(
            "Free-throw outcome does not follow a shooting foul"
        )

    if outcome["outcome"] != "free_throws":
        raise ValueError(
            f"Invalid free-throw outcome: {outcome['outcome']}"
        )

    if outcome["action"] != action:
        raise ValueError(
            "Free-throw action does not match the terminal action"
        )

    if outcome["shooter_player_id"] != shooter["player_id"]:
        raise ValueError(
            "Free-throw shooter_player_id is invalid"
        )

    if outcome["shooter_name"] != shooter["name"]:
        raise ValueError(
            "Free-throw shooter name is invalid"
        )

    expected_attempts = determine_free_throw_attempts(
        action,
        terminal_outcome,
    )

    if outcome["attempts"] != expected_attempts:
        raise ValueError(
            f"Expected {expected_attempts} free throws, "
            f"found {outcome['attempts']}"
        )

    if len(outcome["attempt_results"]) != expected_attempts:
        raise ValueError(
            "Free-throw attempt-result count is invalid"
        )

    if not 0.55 <= outcome["make_probability"] <= 0.95:
        raise ValueError(
            "Free-throw probability is outside the "
            "approved 0.55-0.95 range"
        )

    calculated_makes = sum(
        1
        for attempt in outcome["attempt_results"]
        if attempt["made"]
    )

    calculated_points = sum(
        attempt["points_scored"]
        for attempt in outcome["attempt_results"]
    )

    if outcome["makes"] != calculated_makes:
        raise ValueError(
            "Free-throw make total does not reconcile"
        )

    if outcome["misses"] != expected_attempts - calculated_makes:
        raise ValueError(
            "Free-throw miss total does not reconcile"
        )

    if outcome["points_scored"] != calculated_points:
        raise ValueError(
            "Free-throw points do not reconcile"
        )

    if outcome["points_scored"] != outcome["makes"]:
        raise ValueError(
            "Each made free throw must equal exactly one point"
        )

    for expected_number, attempt in enumerate(
        outcome["attempt_results"],
        start=1,
    ):
        expected_attempt_fields = {
            "attempt_number",
            "made",
            "resolution_roll",
            "make_probability",
            "points_scored",
        }

        if set(attempt) != expected_attempt_fields:
            raise ValueError(
                "Free-throw attempt fields are invalid"
            )

        if attempt["attempt_number"] != expected_number:
            raise ValueError(
                "Free-throw attempt numbering is invalid"
            )

        if not 0.0 <= attempt["resolution_roll"] <= 1.0:
            raise ValueError(
                "Free-throw resolution roll is outside "
                "the 0.0-1.0 range"
            )

        if attempt["make_probability"] != outcome["make_probability"]:
            raise ValueError(
                "Free-throw attempt probability is inconsistent"
            )

        expected_points = 1 if attempt["made"] else 0

        if attempt["points_scored"] != expected_points:
            raise ValueError(
                "Free-throw attempt awarded incorrect points"
            )

    final_attempt = outcome["attempt_results"][-1]

    if outcome["final_attempt_made"] != final_attempt["made"]:
        raise ValueError(
            "Final free-throw result is inconsistent"
        )

    expected_rebound_required = not final_attempt["made"]

    if outcome["rebound_required"] != expected_rebound_required:
        raise ValueError(
            "Free-throw rebound requirement is inconsistent"
        )

    if outcome["possession_continues"] != expected_rebound_required:
        raise ValueError(
            "Free-throw possession-continuation state is invalid"
        )

    if outcome["possession_changes"] != final_attempt["made"]:
        raise ValueError(
            "Free-throw possession-change state is invalid"
        )


def validate_action_selection(
    selected_action,
    action_weights,
):
    valid_actions = {
        "three_point_attempt",
        "midrange_attempt",
        "drive",
        "post_up",
        "pass",
        "draw_foul",
    }

    if selected_action not in valid_actions:
        raise ValueError(
            f"Invalid possession action selected: {selected_action}"
        )

    if set(action_weights) != valid_actions:
        raise ValueError(
            "Possession action-weight keys do not match valid actions"
        )

    for action, weight in action_weights.items():
        if weight <= 0:
            raise ValueError(
                f"Possession action {action} has invalid weight {weight}"
            )


def get_active_player_by_id(
    active_lineup,
    player_id,
):
    matches = [
        player
        for player in active_lineup
        if player["player_id"] == player_id
    ]

    if len(matches) != 1:
        raise ValueError(
            f"Expected exactly one active player with player_id "
            f"{player_id}; found {len(matches)}"
        )

    return matches[0]


def simulate_single_possession(
    offense_team_context,
    defense_team_context,
    rng,
    game_phase="opening",
    possession_id=1,
    max_events=20,
):
    if max_events <= 0:
        raise ValueError(
            "max_events must be greater than zero"
        )

    offensive_lineup = select_active_lineup(
        offense_team_context,
        game_phase=game_phase,
    )

    defensive_lineup = select_active_lineup(
        defense_team_context,
        game_phase=game_phase,
    )

    controller, controller_weights = (
        select_possession_controller(
            offensive_lineup,
            rng,
        )
    )

    validate_controller_selection(
        offense_team_context,
        offensive_lineup,
        controller,
    )

    events = []
    total_points = 0
    possession_complete = False
    final_outcome = None
    next_offense_team = offense_team_context["name"]
    next_controller_player_id = controller["player_id"]

    for event_number in range(1, max_events + 1):
        primary_defender = select_primary_defender(
            controller,
            defensive_lineup,
            defense_team_context,
        )

        validate_primary_defender(
            offense_team_context,
            defense_team_context,
            defensive_lineup,
            controller,
            primary_defender,
        )

        action, action_weights = select_possession_action(
            controller,
            offense_team_context,
            rng,
        )

        validate_action_selection(
            action,
            action_weights,
        )

        event = {
            "event_number": event_number,
            "controller_player_id": controller["player_id"],
            "controller_name": controller["name"],
            "primary_defender_player_id": (
                primary_defender["player_id"]
            ),
            "primary_defender_name": primary_defender["name"],
            "action": action,
            "action_weights": action_weights,
            "points_scored": 0,
        }

        if action == "pass":
            receiver, pass_weights, pass_candidates = (
                select_pass_target(
                    controller,
                    offensive_lineup,
                    offense_team_context,
                    rng,
                )
            )

            validate_pass_target(
                offense_team_context,
                offensive_lineup,
                controller,
                receiver,
            )

            pass_outcome = resolve_pass_outcome(
                controller,
                receiver,
                primary_defender,
                offense_team_context,
                defense_team_context,
                rng,
            )

            validate_pass_outcome(
                controller,
                receiver,
                primary_defender,
                pass_outcome,
            )

            event["pass_target_player_id"] = receiver["player_id"]
            event["pass_target_name"] = receiver["name"]
            event["pass_weights"] = [
                round(weight, 4)
                for weight in pass_weights
            ]
            event["pass_candidate_player_ids"] = [
                player["player_id"]
                for player in pass_candidates
            ]
            event["pass_outcome"] = pass_outcome
            event["outcome"] = pass_outcome["outcome"]

            events.append(event)

            if pass_outcome["completed"]:
                controller = get_active_player_by_id(
                    offensive_lineup,
                    pass_outcome["next_controller_player_id"],
                )

                next_controller_player_id = controller["player_id"]
                continue

            possession_complete = True
            final_outcome = pass_outcome["outcome"]
            next_offense_team = defense_team_context["name"]
            next_controller_player_id = None
            break

        terminal_outcome = resolve_terminal_action_outcome(
            action,
            controller,
            primary_defender,
            offense_team_context,
            defense_team_context,
            rng,
        )

        validate_terminal_action_outcome(
            action,
            controller,
            primary_defender,
            terminal_outcome,
        )

        event["terminal_outcome"] = terminal_outcome
        event["outcome"] = terminal_outcome["outcome"]
        event["points_scored"] = terminal_outcome["points_scored"]

        total_points += terminal_outcome["points_scored"]

        free_throw_outcome = None
        rebound_outcome = None

        if terminal_outcome["outcome"] == "shooting_foul":
            free_throw_outcome = resolve_free_throws(
                action,
                controller,
                terminal_outcome,
                rng,
            )

            validate_free_throw_outcome(
                action,
                controller,
                terminal_outcome,
                free_throw_outcome,
            )

            event["free_throw_outcome"] = free_throw_outcome
            event["points_scored"] += (
                free_throw_outcome["points_scored"]
            )

            total_points += free_throw_outcome["points_scored"]

        rebound_required = (
            terminal_outcome["rebound_required"]
            or (
                free_throw_outcome is not None
                and free_throw_outcome["rebound_required"]
            )
        )

        if rebound_required:
            rebound_outcome = resolve_rebound(
                offensive_lineup,
                defensive_lineup,
                offense_team_context,
                defense_team_context,
                rng,
            )

            validate_rebound_outcome(
                offense_team_context,
                defense_team_context,
                offensive_lineup,
                defensive_lineup,
                rebound_outcome,
            )

            event["rebound_outcome"] = rebound_outcome

        events.append(event)

        if rebound_outcome is not None:
            if rebound_outcome["offensive_rebound"]:
                controller = get_active_player_by_id(
                    offensive_lineup,
                    rebound_outcome[
                        "next_controller_player_id"
                    ],
                )

                next_offense_team = offense_team_context["name"]
                next_controller_player_id = controller["player_id"]
                continue

            possession_complete = True
            final_outcome = rebound_outcome["outcome"]
            next_offense_team = defense_team_context["name"]
            next_controller_player_id = (
                rebound_outcome["next_controller_player_id"]
            )
            break

        if terminal_outcome["outcome"] == "made_shot":
            possession_complete = True
            final_outcome = "made_shot"
            next_offense_team = defense_team_context["name"]
            next_controller_player_id = None
            break

        if terminal_outcome["outcome"] == "turnover":
            possession_complete = True
            final_outcome = "turnover"
            next_offense_team = defense_team_context["name"]
            next_controller_player_id = None
            break

        if free_throw_outcome is not None:
            if free_throw_outcome["possession_changes"]:
                possession_complete = True
                final_outcome = "free_throws_complete"
                next_offense_team = defense_team_context["name"]
                next_controller_player_id = None
                break

        raise RuntimeError(
            "Possession reached an unresolved terminal state: "
            f"action={action}, "
            f"outcome={terminal_outcome['outcome']}"
        )

    if not possession_complete:
        raise RuntimeError(
            f"Possession {possession_id} exceeded the "
            f"{max_events}-event safety limit"
        )

    return {
        "possession_id": possession_id,
        "offense_team": offense_team_context["name"],
        "defense_team": defense_team_context["name"],
        "game_phase": game_phase,
        "initial_controller_player_id": (
            events[0]["controller_player_id"]
        ),
        "initial_controller_weights": [
            round(weight, 4)
            for weight in controller_weights
        ],
        "events": events,
        "event_count": len(events),
        "points_scored": total_points,
        "final_outcome": final_outcome,
        "possession_complete": possession_complete,
        "next_offense_team": next_offense_team,
        "next_controller_player_id": next_controller_player_id,
    }


def validate_single_possession_result(
    offense_team_context,
    defense_team_context,
    result,
):
    required_fields = {
        "possession_id",
        "offense_team",
        "defense_team",
        "game_phase",
        "initial_controller_player_id",
        "initial_controller_weights",
        "events",
        "event_count",
        "points_scored",
        "final_outcome",
        "possession_complete",
        "next_offense_team",
        "next_controller_player_id",
    }

    missing_fields = sorted(
        required_fields - set(result)
    )

    if missing_fields:
        raise ValueError(
            f"Single-possession result missing fields: "
            f"{missing_fields}"
        )

    if result["offense_team"] != offense_team_context["name"]:
        raise ValueError(
            "Single-possession offense team is invalid"
        )

    if result["defense_team"] != defense_team_context["name"]:
        raise ValueError(
            "Single-possession defense team is invalid"
        )

    if not result["possession_complete"]:
        raise ValueError(
            "Single-possession result is incomplete"
        )

    if result["event_count"] != len(result["events"]):
        raise ValueError(
            "Single-possession event count does not reconcile"
        )

    if result["event_count"] <= 0:
        raise ValueError(
            "Single possession must contain at least one event"
        )

    if len(result["initial_controller_weights"]) != 5:
        raise ValueError(
            "Initial controller weights must contain five values"
        )

    active_player_ids = {
        player["player_id"]
        for player in select_active_lineup(
            offense_team_context,
            game_phase=result["game_phase"],
        )
    }

    if (
        result["initial_controller_player_id"]
        not in active_player_ids
    ):
        raise ValueError(
            "Initial controller is not in the active lineup"
        )

    calculated_points = sum(
        event["points_scored"]
        for event in result["events"]
    )

    if result["points_scored"] != calculated_points:
        raise ValueError(
            "Possession points do not reconcile to event points"
        )

    if result["points_scored"] < 0:
        raise ValueError(
            "Possession points cannot be negative"
        )

    valid_next_offense_teams = {
        offense_team_context["name"],
        defense_team_context["name"],
    }

    if result["next_offense_team"] not in valid_next_offense_teams:
        raise ValueError(
            "Next offense team is invalid"
        )

    if result["final_outcome"] is None:
        raise ValueError(
            "Single possession is missing a final outcome"
        )

    for expected_event_number, event in enumerate(
        result["events"],
        start=1,
    ):
        if event["event_number"] != expected_event_number:
            raise ValueError(
                "Possession event numbering is invalid"
            )

        if event["points_scored"] < 0:
            raise ValueError(
                "Possession event points cannot be negative"
            )


def main():
    context = build_input_context()
    rng, seed = build_game_rng()

    home = get_team_context(context, HOME_TEAM)
    away = get_team_context(context, AWAY_TEAM)

    print("=" * 72)
    print("STEP 5D.1 POSSESSION PROTOTYPE FOUNDATION")
    print("=" * 72)
    print(f"Engine: {ENGINE_NAME}")
    print(f"Version: {ENGINE_VERSION}")
    print(f"Season: {SEASON}")
    print(f"Game number: {GAME_NUMBER}")
    print(f"Home: {home['name']}")
    print(f"Away: {away['name']}")
    print(f"Home rotation players: {len(home['players'])}")
    print(f"Away rotation players: {len(away['players'])}")
    print(f"Home starters: {len(home['starters'])}")
    print(f"Away starters: {len(away['starters'])}")
    print(f"Deterministic seed: {seed}")
    print(f"Deterministic probe: {rng.random():.12f}")

    home_active_lineup = select_active_lineup(
        home,
        game_phase="opening",
    )

    away_active_lineup = select_active_lineup(
        away,
        game_phase="opening",
    )

    home_controller, home_weights = select_possession_controller(
        home_active_lineup,
        rng,
    )

    away_controller, away_weights = select_possession_controller(
        away_active_lineup,
        rng,
    )

    validate_controller_selection(
        home,
        home_active_lineup,
        home_controller,
    )

    validate_controller_selection(
        away,
        away_active_lineup,
        away_controller,
    )

    home_primary_defender = select_primary_defender(
        home_controller,
        away_active_lineup,
        away,
    )

    away_primary_defender = select_primary_defender(
        away_controller,
        home_active_lineup,
        home,
    )

    validate_primary_defender(
        home,
        away,
        away_active_lineup,
        home_controller,
        home_primary_defender,
    )

    validate_primary_defender(
        away,
        home,
        home_active_lineup,
        away_controller,
        away_primary_defender,
    )

    home_action, home_action_weights = select_possession_action(
        home_controller,
        home,
        rng,
    )

    away_action, away_action_weights = select_possession_action(
        away_controller,
        away,
        rng,
    )

    validate_action_selection(
        home_action,
        home_action_weights,
    )

    validate_action_selection(
        away_action,
        away_action_weights,
    )

    home_pass_target = None
    home_pass_weights = None
    home_pass_candidates = None

    if home_action == "pass":
        (
            home_pass_target,
            home_pass_weights,
            home_pass_candidates,
        ) = select_pass_target(
            home_controller,
            home_active_lineup,
            home,
            rng,
        )

        validate_pass_target(
            home,
            home_active_lineup,
            home_controller,
            home_pass_target,
        )

    home_pass_outcome = None

    if home_pass_target is not None:
        home_pass_outcome = resolve_pass_outcome(
            home_controller,
            home_pass_target,
            home_primary_defender,
            home,
            away,
            rng,
        )

        validate_pass_outcome(
            home_controller,
            home_pass_target,
            home_primary_defender,
            home_pass_outcome,
        )

    away_pass_target = None
    away_pass_weights = None
    away_pass_candidates = None

    if away_action == "pass":
        (
            away_pass_target,
            away_pass_weights,
            away_pass_candidates,
        ) = select_pass_target(
            away_controller,
            away_active_lineup,
            away,
            rng,
        )

        validate_pass_target(
            away,
            away_active_lineup,
            away_controller,
            away_pass_target,
        )

    away_pass_outcome = None

    if away_pass_target is not None:
        away_pass_outcome = resolve_pass_outcome(
            away_controller,
            away_pass_target,
            away_primary_defender,
            away,
            home,
            rng,
        )

        validate_pass_outcome(
            away_controller,
            away_pass_target,
            away_primary_defender,
            away_pass_outcome,
        )

    home_terminal_outcome = None

    if home_action != "pass":
        home_terminal_outcome = resolve_terminal_action_outcome(
            home_action,
            home_controller,
            home_primary_defender,
            home,
            away,
            rng,
        )

        validate_terminal_action_outcome(
            home_action,
            home_controller,
            home_primary_defender,
            home_terminal_outcome,
        )

    away_terminal_outcome = None

    if away_action != "pass":
        away_terminal_outcome = resolve_terminal_action_outcome(
            away_action,
            away_controller,
            away_primary_defender,
            away,
            home,
            rng,
        )

        validate_terminal_action_outcome(
            away_action,
            away_controller,
            away_primary_defender,
            away_terminal_outcome,
        )

    home_free_throw_outcome = None

    if (
        home_terminal_outcome is not None
        and home_terminal_outcome["outcome"] == "shooting_foul"
    ):
        home_free_throw_outcome = resolve_free_throws(
            home_action,
            home_controller,
            home_terminal_outcome,
            rng,
        )

        validate_free_throw_outcome(
            home_action,
            home_controller,
            home_terminal_outcome,
            home_free_throw_outcome,
        )

    away_free_throw_outcome = None

    if (
        away_terminal_outcome is not None
        and away_terminal_outcome["outcome"] == "shooting_foul"
    ):
        away_free_throw_outcome = resolve_free_throws(
            away_action,
            away_controller,
            away_terminal_outcome,
            rng,
        )

        validate_free_throw_outcome(
            away_action,
            away_controller,
            away_terminal_outcome,
            away_free_throw_outcome,
        )

    home_rebound_outcome = None

    home_rebound_required = (
        home_terminal_outcome is not None
        and home_terminal_outcome["rebound_required"]
    ) or (
        home_free_throw_outcome is not None
        and home_free_throw_outcome["rebound_required"]
    )

    if home_rebound_required:
        home_rebound_outcome = resolve_rebound(
            home_active_lineup,
            away_active_lineup,
            home,
            away,
            rng,
        )

        validate_rebound_outcome(
            home,
            away,
            home_active_lineup,
            away_active_lineup,
            home_rebound_outcome,
        )

    away_rebound_outcome = None

    away_rebound_required = (
        away_terminal_outcome is not None
        and away_terminal_outcome["rebound_required"]
    ) or (
        away_free_throw_outcome is not None
        and away_free_throw_outcome["rebound_required"]
    )

    if away_rebound_required:
        away_rebound_outcome = resolve_rebound(
            away_active_lineup,
            home_active_lineup,
            away,
            home,
            rng,
        )

        validate_rebound_outcome(
            away,
            home,
            away_active_lineup,
            home_active_lineup,
            away_rebound_outcome,
        )

    print()
    print("POSSESSION-CONTROLLER TEST")
    print("-" * 72)
    print(
        f"Home controller: {home_controller['name']} | "
        f"player_id={home_controller['player_id']} | "
        f"role={home_controller['rotation']['role']} | "
        f"minutes={home_controller['rotation']['minutes']} | "
        f"usage={home_controller['tendencies']['usage_tendency']} | "
        f"ball_dominance="
        f"{home_controller['tendencies']['ball_dominance']}"
    )
    print(
        f"Away controller: {away_controller['name']} | "
        f"player_id={away_controller['player_id']} | "
        f"role={away_controller['rotation']['role']} | "
        f"minutes={away_controller['rotation']['minutes']} | "
        f"usage={away_controller['tendencies']['usage_tendency']} | "
        f"ball_dominance="
        f"{away_controller['tendencies']['ball_dominance']}"
    )
    print(
        f"Home active controllers: {len(home_active_lineup)} | "
        f"Total weight: {sum(home_weights):.4f}"
    )
    print(
        f"Away active controllers: {len(away_active_lineup)} | "
        f"Total weight: {sum(away_weights):.4f}"
    )
    print()
    print("PRIMARY-DEFENDER TEST")
    print("-" * 72)
    print(
        f"Home controller matchup: {home_controller['name']} "
        f"({home_controller['position']}) vs "
        f"{home_primary_defender['name']} "
        f"({home_primary_defender['position']}) | "
        f"defense={home_primary_defender['defense']} | "
        f"matchup_weight="
        f"{defender_matchup_weight(home_controller, home_primary_defender, away):.4f}"
    )
    print(
        f"Away controller matchup: {away_controller['name']} "
        f"({away_controller['position']}) vs "
        f"{away_primary_defender['name']} "
        f"({away_primary_defender['position']}) | "
        f"defense={away_primary_defender['defense']} | "
        f"matchup_weight="
        f"{defender_matchup_weight(away_controller, away_primary_defender, home):.4f}"
    )

    print()
    print("POSSESSION-ACTION TEST")
    print("-" * 72)
    print(
        f"Home action: {home_action} | "
        f"controller={home_controller['name']} | "
        f"archetype={home_controller['tendencies']['archetype']} | "
        f"system={home['coach']['offensive_system']}"
    )
    print(
        f"Away action: {away_action} | "
        f"controller={away_controller['name']} | "
        f"archetype={away_controller['tendencies']['archetype']} | "
        f"system={away['coach']['offensive_system']}"
    )
    print(
        "Home action weights:",
        json.dumps(home_action_weights, sort_keys=True),
    )
    print(
        "Away action weights:",
        json.dumps(away_action_weights, sort_keys=True),
    )
    print()
    print("PASS-TARGET TEST")
    print("-" * 72)

    if home_action == "pass":
        print(
            f"Home pass: {home_controller['name']} -> "
            f"{home_pass_target['name']} | "
            f"receiver_player_id={home_pass_target['player_id']} | "
            f"receiver_position={home_pass_target['position']} | "
            f"candidate_count={len(home_pass_candidates)} | "
            f"selected_weight="
            f"{pass_target_weight(home_controller, home_pass_target, home):.4f}"
        )
    else:
        print(
            f"Home action is {home_action}; no pass target required."
        )

    if away_action == "pass":
        print(
            f"Away pass: {away_controller['name']} -> "
            f"{away_pass_target['name']} | "
            f"receiver_player_id={away_pass_target['player_id']} | "
            f"receiver_position={away_pass_target['position']} | "
            f"candidate_count={len(away_pass_candidates)} | "
            f"selected_weight="
            f"{pass_target_weight(away_controller, away_pass_target, away):.4f}"
        )
    else:
        print(
            f"Away action is {away_action}; no pass target required."
        )

    print()
    print("PASS-OUTCOME TEST")
    print("-" * 72)

    if home_pass_outcome is not None:
        print(
            f"Home pass outcome: {home_pass_outcome['outcome']} | "
            f"probability="
            f"{home_pass_outcome['completion_probability']:.4f} | "
            f"roll={home_pass_outcome['resolution_roll']:.6f} | "
            f"continues="
            f"{home_pass_outcome['possession_continues']} | "
            f"next_controller_player_id="
            f"{home_pass_outcome['next_controller_player_id']} | "
            f"turnover_player_id="
            f"{home_pass_outcome['turnover_player_id']} | "
            f"steal_player_id="
            f"{home_pass_outcome['steal_player_id']}"
        )
    else:
        print(
            f"Home action is {home_action}; "
            "no pass outcome required."
        )

    if away_pass_outcome is not None:
        print(
            f"Away pass outcome: {away_pass_outcome['outcome']} | "
            f"probability="
            f"{away_pass_outcome['completion_probability']:.4f} | "
            f"roll={away_pass_outcome['resolution_roll']:.6f} | "
            f"continues="
            f"{away_pass_outcome['possession_continues']} | "
            f"next_controller_player_id="
            f"{away_pass_outcome['next_controller_player_id']} | "
            f"turnover_player_id="
            f"{away_pass_outcome['turnover_player_id']} | "
            f"steal_player_id="
            f"{away_pass_outcome['steal_player_id']}"
        )
    else:
        print(
            f"Away action is {away_action}; "
            "no pass outcome required."
        )

    print()
    print("TERMINAL-ACTION OUTCOME TEST")
    print("-" * 72)

    if home_terminal_outcome is not None:
        print(
            f"Home terminal outcome: "
            f"{home_terminal_outcome['outcome']} | "
            f"action={home_terminal_outcome['action']} | "
            f"points_available="
            f"{home_terminal_outcome['points_available']} | "
            f"points_scored="
            f"{home_terminal_outcome['points_scored']} | "
            f"continues="
            f"{home_terminal_outcome['possession_continues']} | "
            f"rebound_required="
            f"{home_terminal_outcome['rebound_required']} | "
            f"turnover_player_id="
            f"{home_terminal_outcome['turnover_player_id']} | "
            f"steal_player_id="
            f"{home_terminal_outcome['steal_player_id']}"
        )
    else:
        print(
            f"Home action is {home_action}; "
            "pass resolution handled separately."
        )

    if away_terminal_outcome is not None:
        print(
            f"Away terminal outcome: "
            f"{away_terminal_outcome['outcome']} | "
            f"action={away_terminal_outcome['action']} | "
            f"points_available="
            f"{away_terminal_outcome['points_available']} | "
            f"points_scored="
            f"{away_terminal_outcome['points_scored']} | "
            f"continues="
            f"{away_terminal_outcome['possession_continues']} | "
            f"rebound_required="
            f"{away_terminal_outcome['rebound_required']} | "
            f"turnover_player_id="
            f"{away_terminal_outcome['turnover_player_id']} | "
            f"steal_player_id="
            f"{away_terminal_outcome['steal_player_id']}"
        )
    else:
        print(
            f"Away action is {away_action}; "
            "pass resolution handled separately."
        )

    print()
    print("FREE-THROW OUTCOME TEST")
    print("-" * 72)

    if home_free_throw_outcome is not None:
        print(
            f"Home free throws: "
            f"shooter={home_free_throw_outcome['shooter_name']} | "
            f"attempts={home_free_throw_outcome['attempts']} | "
            f"makes={home_free_throw_outcome['makes']} | "
            f"misses={home_free_throw_outcome['misses']} | "
            f"points_scored="
            f"{home_free_throw_outcome['points_scored']} | "
            f"make_probability="
            f"{home_free_throw_outcome['make_probability']:.4f} | "
            f"final_attempt_made="
            f"{home_free_throw_outcome['final_attempt_made']} | "
            f"rebound_required="
            f"{home_free_throw_outcome['rebound_required']} | "
            f"possession_changes="
            f"{home_free_throw_outcome['possession_changes']}"
        )
    else:
        print(
            "Home terminal outcome does not require "
            "free-throw resolution."
        )

    if away_free_throw_outcome is not None:
        print(
            f"Away free throws: "
            f"shooter={away_free_throw_outcome['shooter_name']} | "
            f"attempts={away_free_throw_outcome['attempts']} | "
            f"makes={away_free_throw_outcome['makes']} | "
            f"misses={away_free_throw_outcome['misses']} | "
            f"points_scored="
            f"{away_free_throw_outcome['points_scored']} | "
            f"make_probability="
            f"{away_free_throw_outcome['make_probability']:.4f} | "
            f"final_attempt_made="
            f"{away_free_throw_outcome['final_attempt_made']} | "
            f"rebound_required="
            f"{away_free_throw_outcome['rebound_required']} | "
            f"possession_changes="
            f"{away_free_throw_outcome['possession_changes']}"
        )
    else:
        print(
            "Away terminal outcome does not require "
            "free-throw resolution."
        )

    print()
    print("REBOUND OUTCOME TEST")
    print("-" * 72)

    if home_rebound_outcome is not None:
        print(
            f"Home rebound outcome: "
            f"{home_rebound_outcome['outcome']} | "
            f"rebounder={home_rebound_outcome['rebounder_name']} | "
            f"rebounder_player_id="
            f"{home_rebound_outcome['rebounder_player_id']} | "
            f"rebounder_team="
            f"{home_rebound_outcome['rebounder_team']} | "
            f"offensive_rebound_probability="
            f"{home_rebound_outcome['offensive_rebound_probability']:.4f} | "
            f"continues="
            f"{home_rebound_outcome['possession_continues']} | "
            f"changes="
            f"{home_rebound_outcome['possession_changes']} | "
            f"next_offense="
            f"{home_rebound_outcome['next_offense_team']} | "
            f"next_controller_player_id="
            f"{home_rebound_outcome['next_controller_player_id']}"
        )
    else:
        print(
            "Home terminal outcome does not require "
            "rebound resolution."
        )

    if away_rebound_outcome is not None:
        print(
            f"Away rebound outcome: "
            f"{away_rebound_outcome['outcome']} | "
            f"rebounder={away_rebound_outcome['rebounder_name']} | "
            f"rebounder_player_id="
            f"{away_rebound_outcome['rebounder_player_id']} | "
            f"rebounder_team="
            f"{away_rebound_outcome['rebounder_team']} | "
            f"offensive_rebound_probability="
            f"{away_rebound_outcome['offensive_rebound_probability']:.4f} | "
            f"continues="
            f"{away_rebound_outcome['possession_continues']} | "
            f"changes="
            f"{away_rebound_outcome['possession_changes']} | "
            f"next_offense="
            f"{away_rebound_outcome['next_offense_team']} | "
            f"next_controller_player_id="
            f"{away_rebound_outcome['next_controller_player_id']}"
        )
    else:
        print(
            "Away terminal outcome does not require "
            "rebound resolution."
        )

    orchestrator_seed = deterministic_seed(
        "NBF-LBU",
        "single-possession-main-test",
        ENGINE_VERSION,
        SEASON,
        GAME_NUMBER,
        HOME_TEAM,
        AWAY_TEAM,
    )

    orchestrator_result = simulate_single_possession(
        home,
        away,
        random.Random(orchestrator_seed),
        game_phase="opening",
        possession_id=1,
        max_events=20,
    )

    validate_single_possession_result(
        home,
        away,
        orchestrator_result,
    )

    print()
    print("UNIFIED SINGLE-POSSESSION TEST")
    print("-" * 72)
    print(
        f"Possession ID: "
        f"{orchestrator_result['possession_id']}"
    )
    print(
        f"Offense: {orchestrator_result['offense_team']} | "
        f"Defense: {orchestrator_result['defense_team']}"
    )
    print(
        f"Game phase: {orchestrator_result['game_phase']} | "
        f"Event count: {orchestrator_result['event_count']} | "
        f"Points scored: {orchestrator_result['points_scored']}"
    )
    print(
        f"Final outcome: "
        f"{orchestrator_result['final_outcome']} | "
        f"Possession complete: "
        f"{orchestrator_result['possession_complete']}"
    )
    print(
        f"Next offense: "
        f"{orchestrator_result['next_offense_team']} | "
        f"Next controller player ID: "
        f"{orchestrator_result['next_controller_player_id']}"
    )
    print(f"Orchestrator seed: {orchestrator_seed}")

    print()
    print("POSSESSION EVENT TRACE")
    print("-" * 72)

    for event in orchestrator_result["events"]:
        print(
            f"Event {event['event_number']}: "
            f"controller={event['controller_name']} | "
            f"defender={event['primary_defender_name']} | "
            f"action={event['action']} | "
            f"outcome={event['outcome']} | "
            f"points={event['points_scored']}"
        )

        if "pass_outcome" in event:
            print(
                f"  Pass target: {event['pass_target_name']} | "
                f"completed="
                f"{event['pass_outcome']['completed']} | "
                f"continues="
                f"{event['pass_outcome']['possession_continues']}"
            )

        if "free_throw_outcome" in event:
            free_throws = event["free_throw_outcome"]

            print(
                f"  Free throws: "
                f"{free_throws['makes']}/"
                f"{free_throws['attempts']} | "
                f"points={free_throws['points_scored']} | "
                f"rebound_required="
                f"{free_throws['rebound_required']}"
            )

        if "rebound_outcome" in event:
            rebound = event["rebound_outcome"]

            print(
                f"  Rebound: {rebound['outcome']} | "
                f"rebounder={rebound['rebounder_name']} | "
                f"next_offense={rebound['next_offense_team']}"
            )

    reconciled_orchestrator_points = sum(
        event["points_scored"]
        for event in orchestrator_result["events"]
    )

    if (
        reconciled_orchestrator_points
        != orchestrator_result["points_scored"]
    ):
        raise ValueError(
            "Main orchestrator points failed reconciliation"
        )

    print(
        "Orchestrator point reconciliation:",
        reconciled_orchestrator_points,
    )

    print("Canonical identity: player_id")
    print(
        "Pass, terminal action, free-throw, rebound, and unified "
        "possession outcomes are resolved."
    )
    print(
        "All points produced by the current single-action paths "
        "are traceable to made shots or made free throws."
    )
    print("No complete score or game result generated.")
    print("No canonical input files modified.")
    print("VALIDATION: UNIFIED SINGLE POSSESSION MAIN PASS")


if __name__ == "__main__":
    main()
