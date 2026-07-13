from dataclasses import dataclass, field
from typing import List, Dict, Optional
import random
import csv
import re
from pathlib import Path


# ============================================================
# NBF / LBU v1.0
# National Basketball Federation
# Living Basketball Universe
#
# Genesis Era: Seasons 1-50
# Public Era: Begins Season 51
# ============================================================


# ============================================================
# CORE DATA MODELS
# ============================================================

@dataclass
class Commissioner:
    name: str
    age: int
    integrity: int
    popularity: int
    aggression: int
    discipline: int
    greed: int
    philosophy: str


@dataclass
class Owner:
    name: str
    owner_type: str
    net_worth_b: float
    age: int = 0
    industry: str = ""
    winning_desire: int = 0
    patience: int = 0
    greed: int = 0
    control: int = 0
    pr_awareness: int = 0
    philosophy: str = ""
    hidden_traits: List[str] = field(default_factory=list)


@dataclass
class StaffMember:
    name: str
    age: int
    role: str
    offense: int
    defense: int
    scouting: int
    development: int
    leadership: int
    discipline: int
    ambition: int
    loyalty: int
    adaptability: int
    personality: str
    employed_by: Optional[str] = None

    @property
    def overall(self) -> int:
        return round(
            (
                self.offense
                + self.defense
                + self.scouting
                + self.development
                + self.leadership
                + self.discipline
                + self.adaptability
            ) / 7
        )




@dataclass
class Player:
    player_id: int
    name: str
    position: str
    age: int
    tier: str
    overall: int
    potential: int = 0
    offense: int = 0
    defense: int = 0
    shooting: int = 0
    playmaking: int = 0
    rebounding: int = 0
    basketball_iq: int = 0
    athleticism: int = 0
    leadership: int = 0
    discipline: int = 0
    confidence: int = 0
    popularity: int = 0
    durability: int = 0
    injury_risk: int = 0
    motivation: str = "Balanced"
    team: Optional[str] = None
    draft_year: Optional[int] = None
    draft_pick: Optional[int] = None
    drafted_by: Optional[str] = None
    draft_rights_team: Optional[str] = None
    draft_signed: bool = False
    retired: bool = False
    years_pro: int = 0
    championships: int = 0
    mvp_awards: int = 0
    finals_mvp_awards: int = 0
    all_star_appearances: int = 0
    career_points: int = 0
    career_rebounds: int = 0
    career_assists: int = 0
    season_games: int = 0
    season_points: int = 0
    season_rebounds: int = 0
    season_assists: int = 0
    season_impact: float = 0.0
    playoff_games: int = 0
    playoff_points: int = 0
    playoff_rebounds: int = 0
    playoff_assists: int = 0
    playoff_impact: float = 0.0
    playoff_finals_games: int = 0
    playoff_mvp_awards: int = 0
    rookie_of_year_awards: int = 0
    defensive_player_awards: int = 0
    sixth_man_awards: int = 0
    most_improved_awards: int = 0

    @property
    def value_score(self):
        tier_bonus = {
            "Generational": 18,
            "Superstar": 14,
            "Star": 10,
            "Starter": 6,
            "Role": 3,
            "Fringe": 0,
        }.get(self.tier, 0)

        age_bonus = 0
        if self.age <= 23:
            age_bonus = 5
        elif self.age <= 27:
            age_bonus = 3
        elif self.age >= 34:
            age_bonus = -4

        return self.overall + tier_bonus + age_bonus

    @property
    def two_way_score(self):
        return round((self.offense + self.defense) / 2)

    @property
    def prime_window_score(self):
        if self.age <= 22:
            return 5
        if self.age <= 26:
            return 4
        if self.age <= 30:
            return 3
        if self.age <= 34:
            return 1
        return -2


@dataclass
class TeamIdentity:
    name: str
    conference: str
    mascot: str
    colors: List[str]
    arena: Optional[str]
    culture: Optional[str]
    logo: str
    rivals: List[str]
    blood_rivals: List[str] = field(default_factory=list)



@dataclass
class MarketProfile:
    arena: str = ""
    capacity: int = 0
    atmosphere: int = 0
    luxury: int = 0
    ticket_price_index: int = 0
    market_size: str = ""
    fan_passion: int = 0
    fan_loyalty: int = 0
    fan_patience: int = 0
    media_pressure: int = 0
    free_agent_appeal: int = 0
    corporate_power: int = 0


@dataclass
class Team:
    identity: TeamIdentity
    owner: Owner
    gm: Optional[StaffMember] = None
    coach: Optional[StaffMember] = None
    roster: List[Player] = field(default_factory=list)
    wins: int = 0
    losses: int = 0
    championships: int = 0
    market_profile: Optional[MarketProfile] = None



@dataclass
class Referee:
    referee_id: int
    name: str
    tier: str
    accuracy: Optional[int] = None
    consistency: int = 70
    confidence: int = 70
    popularity: int = 50
    pressure_resistance: int = 70
    retired: bool = False


@dataclass
class Reporter:
    name: str
    team: str
    reporter_type: str
    integrity: Optional[int] = None
    aggression: Optional[int] = None
    sources: Optional[int] = None
    popularity: Optional[int] = None
    hidden_traits: List[str] = field(default_factory=list)


@dataclass
class AwardsCommitteeMember:
    member_id: int
    name: str
    category: str
    outlet: Optional[str] = None
    member_type: Optional[str] = None
    integrity: Optional[int] = None
    popularity: Optional[int] = None
    bias: Optional[int] = None


@dataclass
class HallOfFameCommitteeMember:
    member_id: int
    name: str
    role: str
    age: Optional[int] = None
    profession: Optional[str] = None
    integrity: Optional[int] = None
    historical_knowledge: Optional[int] = None
    popularity: Optional[int] = None
    bias: Optional[int] = None
    leadership: Optional[int] = None


@dataclass
class LeagueRules:
    salary_floor_m: int
    soft_cap_m: int
    luxury_tax_tier_1_min_m: int
    luxury_tax_tier_1_max_m: int
    luxury_tax_tier_2_min_m: int
    luxury_tax_tier_2_max_m: int
    hard_cap_m: int
    playoff_teams_per_conference: int
    playoff_series_length: int
    owner_override_percentage: float
    expansion_requires_unanimous: bool
    relocation_requires_unanimous: bool


@dataclass
class League:
    name: str
    motto: str
    championship_trophy: str
    hall_of_fame_name: str
    hall_of_fame_location: str
    commissioner: Commissioner
    rules: LeagueRules
    teams: Dict[str, Team]
    current_year: int = 0
    public_era_start_year: int = 51
    history: List[str] = field(default_factory=list)
    current_champion: Optional[str] = None
    playoff_results: List[str] = field(default_factory=list)
    award_results: List[str] = field(default_factory=list)
    season_summaries: List[str] = field(default_factory=list)
    retired_players_log: List[str] = field(default_factory=list)
    offseason_log: List[str] = field(default_factory=list)
    genesis_test_log: List[str] = field(default_factory=list)
    playoff_mvp_award_name: str = "Kanomi Jones Playoff MVP"
    season_mvp_award_name: str = "MVP"
    season_mvp_legacy_player_id: Optional[int] = None
    season_mvp_legacy_player_name: Optional[str] = None
    playoff_mvp_player_id: Optional[int] = None
    playoff_mvp_name: Optional[str] = None
    playoff_mvp_team: Optional[str] = None
    gm_pool: List[StaffMember] = field(default_factory=list)
    coach_pool: List[StaffMember] = field(default_factory=list)
    player_pool: List[Player] = field(default_factory=list)
    referee_pool: List[Referee] = field(default_factory=list)
    team_reporters: List[Reporter] = field(default_factory=list)
    awards_committee: List[AwardsCommitteeMember] = field(default_factory=list)
    hall_of_fame_committee: List[HallOfFameCommitteeMember] = field(default_factory=list)


# ============================================================
# FOUNDATION REGISTRY
# ============================================================

def build_commissioner() -> Commissioner:
    return Commissioner(
        name="Victor Hale",
        age=58,
        integrity=78,
        popularity=64,
        aggression=55,
        discipline=91,
        greed=39,
        philosophy="League First. Institution Builder."
    )


def build_rules() -> LeagueRules:
    return LeagueRules(
        salary_floor_m=110,
        soft_cap_m=165,
        luxury_tax_tier_1_min_m=165,
        luxury_tax_tier_1_max_m=185,
        luxury_tax_tier_2_min_m=185,
        luxury_tax_tier_2_max_m=210,
        hard_cap_m=210,
        playoff_teams_per_conference=4,
        playoff_series_length=7,
        owner_override_percentage=0.75,
        expansion_requires_unanimous=True,
        relocation_requires_unanimous=True
    )


def build_owners() -> Dict[str, Owner]:
    return {
        "Little Rock Bandits": Owner("William Mercer", "Loyal Builder", 4.8),
        "Dallas Outlaws": Owner("Lucas Sterling", "Win At All Costs", 19.7),
        "Houston Cosmos": Owner("Dr. Elena Vasquez", "Innovator", 11.2),
        "Denver Peaks": Owner("Michael Harlan", "Hands-Off Steward", 5.9),
        "Phoenix Fire": Owner("Sophia Kane", "Celebrity Owner", 7.4),
        "Los Angeles Stars": Owner("Jordan Vale", "Global Mogul", 24.3),
        "Seattle Sound": Owner("Nathan Brooks", "Basketball Purist", 15.4),
        "Portland Lumberjacks": Owner("Evelyn Ward", "Traditionalist", 6.1),
        "New York Empire": Owner("Vincent Roth", "Control Freak", 28.9),
        "Boston Guardians": Owner("Charles Whitmore IV", "Steward", 14.3),
        "Philadelphia Riders": Owner("Patrick Doyle", "Blue-Collar Competitor", 7.8),
        "Chicago Union": Owner("Margaret Walsh", "Builder", 13.1),
        "Detroit Forge": Owner("Anthony Greco", "Loyal Owner", 8.5),
        "Atlanta Monarchs": Owner("Travis King", "Celebrity Owner", 9.7),
        "Charlotte Crown": Owner("Rachel Morgan", "Growth Investor", 7.2),
        "Miami Tide": Owner("Alejandro Cruz", "Lifestyle Mogul", 16.8),
    }


def build_team_identities() -> Dict[str, TeamIdentity]:
    blood_rivalries = {
        "Little Rock Bandits": ["Dallas Outlaws"],
        "Dallas Outlaws": ["Little Rock Bandits"],
        "Seattle Sound": ["Portland Lumberjacks"],
        "Portland Lumberjacks": ["Seattle Sound"],
        "New York Empire": ["Boston Guardians"],
        "Boston Guardians": ["New York Empire"],
        "Chicago Union": ["Detroit Forge"],
        "Detroit Forge": ["Chicago Union"],
    }

    teams = {
        "Little Rock Bandits": TeamIdentity(
            name="Little Rock Bandits",
            conference="Western",
            mascot="Cash",
            colors=["Electric Blue", "Steel Gray", "White"],
            arena="Bandit Colosseum",
            culture="We're Gonna Take Our Respect",
            logo="Bandit Mask + Arkansas Star",
            rivals=["Dallas Outlaws", "Houston Cosmos"],
        ),
        "Dallas Outlaws": TeamIdentity(
            name="Dallas Outlaws",
            conference="Western",
            mascot="Marshal",
            colors=["Crimson", "Black", "Silver"],
            arena=None,
            culture=None,
            logo="Western Star Revolver",
            rivals=["Little Rock Bandits", "Houston Cosmos"],
        ),
        "Houston Cosmos": TeamIdentity(
            name="Houston Cosmos",
            conference="Western",
            mascot="Nova",
            colors=["Deep Navy", "Orange", "White"],
            arena=None,
            culture=None,
            logo="Orbit / Aerospace",
            rivals=["Dallas Outlaws", "Little Rock Bandits", "Denver Peaks"],
        ),
        "Denver Peaks": TeamIdentity(
            name="Denver Peaks",
            conference="Western",
            mascot="Summit",
            colors=["Mountain Blue", "Gold", "White"],
            arena=None,
            culture=None,
            logo="Mountain Peak",
            rivals=["Phoenix Fire", "Houston Cosmos"],
        ),
        "Phoenix Fire": TeamIdentity(
            name="Phoenix Fire",
            conference="Western",
            mascot="Blaze",
            colors=["Purple", "Orange", "Black"],
            arena=None,
            culture=None,
            logo="Phoenix Flame",
            rivals=["Denver Peaks", "Los Angeles Stars"],
        ),
        "Los Angeles Stars": TeamIdentity(
            name="Los Angeles Stars",
            conference="Western",
            mascot="Starlight",
            colors=["Gold", "Black", "White"],
            arena=None,
            culture=None,
            logo="Luxury Star",
            rivals=["Phoenix Fire", "Seattle Sound", "New York Empire"],
        ),
        "Seattle Sound": TeamIdentity(
            name="Seattle Sound",
            conference="Western",
            mascot="Breaker",
            colors=["Emerald", "Navy", "Silver"],
            arena=None,
            culture=None,
            logo="Wave / Orca",
            rivals=["Portland Lumberjacks", "Los Angeles Stars"],
        ),
        "Portland Lumberjacks": TeamIdentity(
            name="Portland Lumberjacks",
            conference="Western",
            mascot="Timber",
            colors=["Forest Green", "Cream", "Brown"],
            arena=None,
            culture=None,
            logo="Axe & Pine",
            rivals=["Seattle Sound", "Denver Peaks"],
        ),
        "New York Empire": TeamIdentity(
            name="New York Empire",
            conference="Eastern",
            mascot="Crown",
            colors=["Royal Blue", "Black", "Silver"],
            arena=None,
            culture=None,
            logo="Crown + Skyline",
            rivals=["Boston Guardians", "Philadelphia Riders", "Los Angeles Stars"],
        ),
        "Boston Guardians": TeamIdentity(
            name="Boston Guardians",
            conference="Eastern",
            mascot="Sentinel",
            colors=["Green", "Gold", "White"],
            arena=None,
            culture=None,
            logo="Shield Guardian",
            rivals=["New York Empire", "Philadelphia Riders"],
        ),
        "Philadelphia Riders": TeamIdentity(
            name="Philadelphia Riders",
            conference="Eastern",
            mascot="Liberty Bell",
            colors=["Red", "Navy", "White"],
            arena=None,
            culture=None,
            logo="Liberty Bell",
            rivals=["New York Empire", "Boston Guardians"],
        ),
        "Chicago Union": TeamIdentity(
            name="Chicago Union",
            conference="Eastern",
            mascot="Hammer",
            colors=["Red", "Black", "Cream"],
            arena=None,
            culture=None,
            logo="Industrial Gear",
            rivals=["Detroit Forge", "Atlanta Monarchs"],
        ),
        "Detroit Forge": TeamIdentity(
            name="Detroit Forge",
            conference="Eastern",
            mascot="Anvil",
            colors=["Steel", "Red", "Black"],
            arena=None,
            culture=None,
            logo="Forge & Sparks",
            rivals=["Chicago Union", "Charlotte Crown"],
        ),
        "Atlanta Monarchs": TeamIdentity(
            name="Atlanta Monarchs",
            conference="Eastern",
            mascot="King",
            colors=["Purple", "Gold", "Black"],
            arena=None,
            culture=None,
            logo="Crown & Lion",
            rivals=["Charlotte Crown", "Chicago Union", "Miami Tide"],
        ),
        "Charlotte Crown": TeamIdentity(
            name="Charlotte Crown",
            conference="Eastern",
            mascot="Regent",
            colors=["Teal", "Black", "White"],
            arena=None,
            culture=None,
            logo="Crown & Hawk",
            rivals=["Atlanta Monarchs", "Detroit Forge"],
        ),
        "Miami Tide": TeamIdentity(
            name="Miami Tide",
            conference="Eastern",
            mascot="Surge",
            colors=["Aqua", "Pink", "Black"],
            arena=None,
            culture=None,
            logo="Wave & Sunset",
            rivals=["Atlanta Monarchs", "New York Empire"],
        ),
    }

    for team_name, rivals in blood_rivalries.items():
        teams[team_name].blood_rivals = rivals

    return teams


def build_teams() -> Dict[str, Team]:
    owners = build_owners()
    identities = build_team_identities()

    teams = {}

    for team_name, identity in identities.items():
        teams[team_name] = Team(
            identity=identity,
            owner=owners[team_name]
        )

    return teams


# ============================================================
# STAFF GENERATION
# ============================================================



# ============================================================
# FOUNDATION POOL LOADERS
# ============================================================

FOUNDATION_TEXT_DIR = Path("Foundation_Text")
FOUNDATION_PLAYER_FILE = FOUNDATION_TEXT_DIR / "NBF 500 Player Talent Pool.txt"
FOUNDATION_GM_FILE = FOUNDATION_TEXT_DIR / "NBF GM CANDIDATE POOL.txt"
FOUNDATION_COACH_FILE = FOUNDATION_TEXT_DIR / "NBF COACH CANDIDATE POOL.txt"


def clamp_rating(value):
    return max(35, min(99, value))


def load_foundation_player_pool():
    if not FOUNDATION_PLAYER_FILE.exists():
        raise FileNotFoundError(f"Missing foundation player file: {FOUNDATION_PLAYER_FILE}")

    players = []

    with FOUNDATION_PLAYER_FILE.open("r", encoding="utf-8", errors="replace", newline="") as f:
        reader = csv.DictReader(f)

        required = ["ID", "Name", "Position", "Age", "Tier", "Overall"]
        missing = [col for col in required if col not in reader.fieldnames]

        if missing:
            raise ValueError(f"Player file missing columns: {missing}")

        for row in reader:
            players.append(
                Player(
                    player_id=int(row["ID"]),
                    name=row["Name"].strip(),
                    position=row["Position"].strip(),
                    age=int(row["Age"]),
                    tier=row["Tier"].strip(),
                    overall=int(row["Overall"]),
                )
            )

    return players


def gm_archetype_to_staff(name, age, archetype, ratings):
    base = 68

    scouting = ratings.get("Scouting", base)
    drafting = ratings.get("Drafting", scouting)
    negotiation = ratings.get("Negotiation", base)
    reputation = ratings.get("Reputation", base)

    offense = base
    defense = base
    development = base
    leadership = max(base, reputation)
    discipline = base
    ambition = 70
    loyalty = 65
    adaptability = base

    arch = archetype.lower()

    if "analytics" in arch or "modern" in arch:
        scouting += 8
        adaptability += 10

    if "draft" in arch or "talent" in arch:
        scouting += 12
        development += 8

    if "veteran" in arch:
        leadership += 10
        discipline += 8

    if "win-now" in arch or "star hunter" in arch:
        ambition += 14
        negotiation += 8
        loyalty -= 8

    if "culture" in arch:
        leadership += 12
        loyalty += 10
        discipline += 6

    if "risk" in arch:
        ambition += 12
        adaptability += 8
        discipline -= 6

    if "traditional" in arch:
        discipline += 10
        loyalty += 8
        adaptability -= 4

    return StaffMember(
        name=name,
        age=age,
        role="GM",
        offense=clamp_rating(offense),
        defense=clamp_rating(defense),
        scouting=clamp_rating(max(scouting, drafting)),
        development=clamp_rating(development),
        leadership=clamp_rating(leadership),
        discipline=clamp_rating(discipline),
        ambition=clamp_rating(max(ambition, negotiation // 1)),
        loyalty=clamp_rating(loyalty),
        adaptability=clamp_rating(adaptability),
        personality=archetype,
        employed_by=None
    )


def coach_archetype_to_staff(name, age, archetype, hidden_tendency):
    base = 68

    offense = base
    defense = base
    scouting = base
    development = base
    leadership = base
    discipline = base
    ambition = 68
    loyalty = 65
    adaptability = base

    arch = archetype.lower()

    if "development" in arch:
        development += 18
        adaptability += 8

    if "defense" in arch:
        defense += 18
        discipline += 10

    if "offense" in arch:
        offense += 18
        adaptability += 6

    if "player" in arch:
        leadership += 12
        loyalty += 8

    if "veteran" in arch:
        discipline += 12
        leadership += 8

    if "analytics" in arch or "modern" in arch:
        scouting += 8
        adaptability += 12

    if "motivator" in arch or "culture" in arch:
        leadership += 15
        loyalty += 8

    if hidden_tendency:
        h = hidden_tendency.lower()

        if "rookie" in h or "young" in h or "prospect" in h:
            development += 5

        if "stars" in h or "superstars" in h:
            leadership += 4

        if "stubborn" in h or "old school" in h:
            discipline += 4
            adaptability -= 5

        if "weak in-game" in h:
            adaptability -= 6

    return StaffMember(
        name=name,
        age=age,
        role="Coach",
        offense=clamp_rating(offense),
        defense=clamp_rating(defense),
        scouting=clamp_rating(scouting),
        development=clamp_rating(development),
        leadership=clamp_rating(leadership),
        discipline=clamp_rating(discipline),
        ambition=clamp_rating(ambition),
        loyalty=clamp_rating(loyalty),
        adaptability=clamp_rating(adaptability),
        personality=archetype,
        employed_by=None
    )


def generate_gm_pool(size=32):
    if not FOUNDATION_GM_FILE.exists():
        raise FileNotFoundError(f"Missing foundation GM file: {FOUNDATION_GM_FILE}")

    text = FOUNDATION_GM_FILE.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()

    gms = []
    current = None

    for line in lines:
        clean = line.strip()

        match = re.match(r"^(\d+)\.\s+(.+)$", clean)
        if match:
            if current:
                gms.append(current)

            current = {
                "name": match.group(2).strip(),
                "age": None,
                "archetype": "General Manager",
                "ratings": {},
            }
            continue

        if current is None:
            continue

        if clean.startswith("Age:"):
            age_match = re.search(r"Age:\s*(\d+)", clean)
            if age_match:
                current["age"] = int(age_match.group(1))

            archetype_match = re.search(r"Archetype:\s*(.+)$", clean)
            if archetype_match:
                current["archetype"] = archetype_match.group(1).strip()

            continue

        if clean.startswith("Archetype:"):
            current["archetype"] = clean.replace("Archetype:", "").strip()
            continue

        rating_match = re.search(r"([A-Za-z ]+)\s+(\d+)$", clean.replace("•", "").strip())
        if rating_match:
            current["ratings"][rating_match.group(1).strip()] = int(rating_match.group(2))

    if current:
        gms.append(current)

    staff_pool = []

    for gm in gms:
        if gm["age"] is None:
            gm["age"] = 45

        staff_pool.append(
            gm_archetype_to_staff(
                name=gm["name"],
                age=gm["age"],
                archetype=gm["archetype"],
                ratings=gm["ratings"],
            )
        )

    return staff_pool


def generate_coach_pool(size=32):
    if not FOUNDATION_COACH_FILE.exists():
        raise FileNotFoundError(f"Missing foundation coach file: {FOUNDATION_COACH_FILE}")

    text = FOUNDATION_COACH_FILE.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()

    coaches = []
    current = None

    for line in lines:
        clean = line.strip()

        match = re.match(r"^(\d+)\.\s+(.+?)\s+\((\d+)\)$", clean)
        if match:
            if current:
                coaches.append(current)

            current = {
                "name": match.group(2).strip(),
                "age": int(match.group(3)),
                "archetype": None,
                "hidden_tendency": None,
            }
            continue

        if current is None:
            continue

        if clean and not clean.startswith("•") and current["archetype"] is None:
            current["archetype"] = clean
            continue

        if clean.startswith("•"):
            note = clean.replace("•", "").strip()

            if note.lower().startswith("hidden:"):
                current["hidden_tendency"] = note.split(":", 1)[1].strip()

    if current:
        coaches.append(current)

    staff_pool = []

    for coach in coaches:
        staff_pool.append(
            coach_archetype_to_staff(
                name=coach["name"],
                age=coach["age"],
                archetype=coach["archetype"] or "Coach",
                hidden_tendency=coach["hidden_tendency"],
            )
        )

    return staff_pool


# ============================================================
# HIRING LOGIC
# ============================================================

def owner_hiring_preference(owner_type: str) -> Dict[str, float]:
    preferences = {
        "Win At All Costs": {
            "overall": 1.25,
            "ambition": 1.15,
            "leadership": 1.10,
            "loyalty": 0.75
        },
        "Loyal Builder": {
            "overall": 1.00,
            "ambition": 0.85,
            "leadership": 1.15,
            "loyalty": 1.30
        },
        "Innovator": {
            "overall": 1.05,
            "ambition": 1.05,
            "leadership": 1.00,
            "loyalty": 0.95
        },
        "Hands-Off Steward": {
            "overall": 1.00,
            "ambition": 0.80,
            "leadership": 1.15,
            "loyalty": 1.15
        },
        "Celebrity Owner": {
            "overall": 1.00,
            "ambition": 1.20,
            "leadership": 1.05,
            "loyalty": 0.85
        },
        "Global Mogul": {
            "overall": 1.15,
            "ambition": 1.15,
            "leadership": 1.10,
            "loyalty": 0.80
        },
        "Basketball Purist": {
            "overall": 1.15,
            "ambition": 0.90,
            "leadership": 1.05,
            "loyalty": 1.10
        },
        "Traditionalist": {
            "overall": 1.00,
            "ambition": 0.75,
            "leadership": 1.15,
            "loyalty": 1.25
        },
        "Control Freak": {
            "overall": 1.10,
            "ambition": 0.85,
            "leadership": 0.95,
            "loyalty": 1.35
        },
        "Steward": {
            "overall": 1.00,
            "ambition": 0.85,
            "leadership": 1.10,
            "loyalty": 1.20
        },
        "Blue-Collar Competitor": {
            "overall": 1.05,
            "ambition": 1.00,
            "leadership": 1.20,
            "loyalty": 1.00
        },
        "Builder": {
            "overall": 1.05,
            "ambition": 0.95,
            "leadership": 1.15,
            "loyalty": 1.10
        },
        "Loyal Owner": {
            "overall": 1.00,
            "ambition": 0.85,
            "leadership": 1.10,
            "loyalty": 1.35
        },
        "Growth Investor": {
            "overall": 1.10,
            "ambition": 1.20,
            "leadership": 1.00,
            "loyalty": 0.90
        },
        "Lifestyle Mogul": {
            "overall": 1.00,
            "ambition": 1.15,
            "leadership": 1.05,
            "loyalty": 0.85
        },
    }

    return preferences.get(
        owner_type,
        {
            "overall": 1.00,
            "ambition": 1.00,
            "leadership": 1.00,
            "loyalty": 1.00
        }
    )


def score_gm_for_owner(gm: StaffMember, owner: Owner) -> float:
    pref = owner_hiring_preference(owner.owner_type)

    score = (
        gm.overall * pref["overall"]
        + gm.ambition * pref["ambition"]
        + gm.leadership * pref["leadership"]
        + gm.loyalty * pref["loyalty"]
    )

    score += random.uniform(-5, 5)

    return score


def score_coach_for_gm(coach: StaffMember, gm: StaffMember) -> float:
    score = coach.overall

    if gm.scouting + gm.development >= 150:
        score += coach.development * 0.35

    if gm.defense >= gm.offense:
        score += coach.defense * 0.30

    if gm.offense > gm.defense:
        score += coach.offense * 0.30

    if gm.discipline >= 75:
        score += coach.discipline * 0.25

    if gm.ambition >= 75:
        score += coach.leadership * 0.25

    score += random.uniform(-5, 5)

    return score


def run_initial_gm_hiring(league: League) -> None:
    for team in league.teams.values():
        available_gms = [gm for gm in league.gm_pool if gm.employed_by is None]

        if not available_gms:
            raise RuntimeError("No available GMs left in pool.")

        best_gm = max(
            available_gms,
            key=lambda gm: score_gm_for_owner(gm, team.owner)
        )

        best_gm.employed_by = team.identity.name
        team.gm = best_gm

        league.history.append(
            f"Year 1: {team.owner.name} hired {best_gm.name} as GM of the {team.identity.name}."
        )


def run_initial_coach_hiring(league: League) -> None:
    for team in league.teams.values():
        if team.gm is None:
            raise RuntimeError(f"{team.identity.name} cannot hire coach without GM.")

        available_coaches = [coach for coach in league.coach_pool if coach.employed_by is None]

        if not available_coaches:
            raise RuntimeError("No available coaches left in pool.")

        best_coach = max(
            available_coaches,
            key=lambda coach: score_coach_for_gm(coach, team.gm)
        )

        best_coach.employed_by = team.identity.name
        team.coach = best_coach

        league.history.append(
            f"Year 1: GM {team.gm.name} hired {best_coach.name} as head coach of the {team.identity.name}."
        )


def run_year_1_staff_setup(league: League) -> None:
    league.current_year = 1

    run_initial_gm_hiring(league)
    run_initial_coach_hiring(league)

    league.history.append(
        "Year 1: All 16 franchises completed initial GM and head coach hiring."
    )



# ============================================================
# FOUNDATION DATA LOADERS
# ============================================================

FOUNDATION_TEXT_DIR = Path("Foundation_Text")
FOUNDATION_PLAYER_FILE = FOUNDATION_TEXT_DIR / "NBF 500 Player Talent Pool.txt"


def load_foundation_player_pool():
    if not FOUNDATION_PLAYER_FILE.exists():
        raise FileNotFoundError(
            f"Missing foundation player file: {FOUNDATION_PLAYER_FILE}"
        )

    players = []

    with FOUNDATION_PLAYER_FILE.open("r", encoding="utf-8", errors="replace", newline="") as f:
        reader = csv.DictReader(f)

        required_columns = ["ID", "Name", "Position", "Age", "Tier", "Overall"]
        missing_columns = [col for col in required_columns if col not in reader.fieldnames]

        if missing_columns:
            raise ValueError(f"Player file missing required columns: {missing_columns}")

        for row in reader:
            player = Player(
                player_id=int(row["ID"]),
                name=row["Name"].strip(),
                position=row["Position"].strip(),
                age=int(row["Age"]),
                tier=row["Tier"].strip(),
                overall=int(row["Overall"]),
            )
            players.append(player)

    return players


def validate_foundation_player_pool(league):
    errors = []

    players = league.player_pool

    if len(players) != 500:
        errors.append(f"Expected 500 foundation players, found {len(players)}.")

    player_ids = [player.player_id for player in players]

    if len(player_ids) != len(set(player_ids)):
        errors.append("Duplicate player IDs detected.")

    valid_positions = {"PG", "SG", "SF", "PF", "C"}
    valid_tiers = {"Generational", "Superstar", "Star", "Starter", "Role", "Fringe"}

    for player in players:
        if player.position not in valid_positions:
            errors.append(f"Invalid position for player ID {player.player_id}: {player.position}")

        if player.tier not in valid_tiers:
            errors.append(f"Invalid tier for player ID {player.player_id}: {player.tier}")

        if player.overall < 1 or player.overall > 100:
            errors.append(f"Invalid overall for player ID {player.player_id}: {player.overall}")

        if player.age < 18 or player.age > 45:
            errors.append(f"Unusual age for player ID {player.player_id}: {player.age}")

    if errors:
        print("FOUNDATION PLAYER POOL VALIDATION: FAILED")
        for error in errors:
            print(f"- {error}")
        raise SystemExit(1)

    print("FOUNDATION PLAYER POOL VALIDATION: PASS")


def print_foundation_player_summary(league):
    print("\n============================================")
    print("FOUNDATION PLAYER POOL LOADED")
    print("============================================")
    print(f"Total Players: {len(league.player_pool)}")

    tier_counts = {}
    position_counts = {}

    for player in league.player_pool:
        tier_counts[player.tier] = tier_counts.get(player.tier, 0) + 1
        position_counts[player.position] = position_counts.get(player.position, 0) + 1

    print("\nTier Counts:")
    for tier in sorted(tier_counts):
        print(f"- {tier}: {tier_counts[tier]}")

    print("\nPosition Counts:")
    for position in sorted(position_counts):
        print(f"- {position}: {position_counts[position]}")

    print("\nTop 10 Foundation Players by Overall:")
    top_players = sorted(
        league.player_pool,
        key=lambda player: player.overall,
        reverse=True
    )[:10]

    for player in top_players:
        print(
            f"- ID {player.player_id}: {player.name} | {player.position} | "
            f"Age {player.age} | {player.tier} | OVR {player.overall}"
        )

    print("============================================\n")



# ============================================================
# PLAYER ENRICHMENT SYSTEM
# ============================================================

def clamp_player_rating(value):
    return max(35, min(99, int(round(value))))


def player_rng(player, label):
    return random.Random(f"NBF-LBU-v1:{player.player_id}:{player.name}:{label}")


def tier_potential_bonus(tier):
    bonuses = {
        "Generational": 8,
        "Superstar": 7,
        "Star": 5,
        "Starter": 3,
        "Role": 2,
        "Fringe": 1,
    }
    return bonuses.get(tier, 2)


def age_potential_modifier(age):
    if age <= 20:
        return 9
    if age <= 22:
        return 7
    if age <= 24:
        return 5
    if age <= 27:
        return 2
    if age <= 30:
        return 0
    if age <= 34:
        return -2
    return -5


def position_attribute_modifiers(position):
    profiles = {
        "PG": {
            "shooting": 4,
            "playmaking": 12,
            "basketball_iq": 8,
            "athleticism": 3,
            "rebounding": -9,
            "defense": 0,
            "offense": 4,
        },
        "SG": {
            "shooting": 10,
            "playmaking": 4,
            "basketball_iq": 3,
            "athleticism": 5,
            "rebounding": -5,
            "defense": 1,
            "offense": 7,
        },
        "SF": {
            "shooting": 4,
            "playmaking": 3,
            "basketball_iq": 4,
            "athleticism": 6,
            "rebounding": 2,
            "defense": 4,
            "offense": 4,
        },
        "PF": {
            "shooting": -1,
            "playmaking": -2,
            "basketball_iq": 3,
            "athleticism": 5,
            "rebounding": 9,
            "defense": 6,
            "offense": 2,
        },
        "C": {
            "shooting": -7,
            "playmaking": -5,
            "basketball_iq": 4,
            "athleticism": 2,
            "rebounding": 13,
            "defense": 10,
            "offense": 0,
        },
    }

    return profiles.get(position, {})


def tier_personality_floor(tier):
    floors = {
        "Generational": 72,
        "Superstar": 68,
        "Star": 62,
        "Starter": 55,
        "Role": 48,
        "Fringe": 42,
    }
    return floors.get(tier, 48)


def assign_player_motivation(player):
    rng = player_rng(player, "motivation")

    if player.tier in ["Generational", "Superstar"]:
        options = ["Legacy", "Dominance", "Championships", "Immortality"]
    elif player.age <= 23:
        options = ["Prove Himself", "Development", "Opportunity", "Respect"]
    elif player.age >= 34:
        options = ["Final Run", "Mentorship", "Ring Chase", "Respect"]
    else:
        options = ["Winning", "Security", "Recognition", "Role Growth"]

    return rng.choice(options)


def enrich_player(player):
    base = player.overall
    mods = position_attribute_modifiers(player.position)

    for attr in [
        "offense",
        "defense",
        "shooting",
        "playmaking",
        "rebounding",
        "basketball_iq",
        "athleticism",
    ]:
        rng = player_rng(player, attr)
        modifier = mods.get(attr, 0)
        variance = rng.randint(-7, 7)
        setattr(player, attr, clamp_player_rating(base + modifier + variance))

    potential_rng = player_rng(player, "potential")
    potential = (
        player.overall
        + tier_potential_bonus(player.tier)
        + age_potential_modifier(player.age)
        + potential_rng.randint(-3, 5)
    )
    player.potential = clamp_player_rating(max(player.overall, potential))

    personality_floor = tier_personality_floor(player.tier)

    player.leadership = clamp_player_rating(
        max(personality_floor, base + player_rng(player, "leadership").randint(-18, 10))
    )

    player.discipline = clamp_player_rating(
        max(35, base + player_rng(player, "discipline").randint(-20, 12))
    )

    player.confidence = clamp_player_rating(
        max(personality_floor, base + player_rng(player, "confidence").randint(-10, 15))
    )

    popularity_bonus = {
        "Generational": 18,
        "Superstar": 14,
        "Star": 9,
        "Starter": 4,
        "Role": 0,
        "Fringe": -4,
    }.get(player.tier, 0)

    player.popularity = clamp_player_rating(
        base + popularity_bonus + player_rng(player, "popularity").randint(-12, 12)
    )

    age_durability_penalty = 0
    if player.age >= 34:
        age_durability_penalty = 10
    elif player.age >= 30:
        age_durability_penalty = 5

    player.durability = clamp_player_rating(
        base + player_rng(player, "durability").randint(-8, 12) - age_durability_penalty
    )

    injury_raw = 100 - player.durability
    if player.age >= 34:
        injury_raw += 8
    elif player.age >= 30:
        injury_raw += 4

    player.injury_risk = max(1, min(60, injury_raw))

    player.motivation = assign_player_motivation(player)


def enrich_foundation_players(players):
    for player in players:
        enrich_player(player)


def validate_enriched_players(league):
    errors = []

    required_attrs = [
        "potential",
        "offense",
        "defense",
        "shooting",
        "playmaking",
        "rebounding",
        "basketball_iq",
        "athleticism",
        "leadership",
        "discipline",
        "confidence",
        "popularity",
        "durability",
        "injury_risk",
    ]

    for player in league.player_pool:
        for attr in required_attrs:
            value = getattr(player, attr)

            if value is None:
                errors.append(f"Player {player.player_id} missing {attr}.")
                continue

            if attr == "injury_risk":
                if value < 1 or value > 60:
                    errors.append(f"Player {player.player_id} invalid injury_risk {value}.")
            else:
                if value < 35 or value > 99:
                    errors.append(f"Player {player.player_id} invalid {attr} {value}.")

        if not player.motivation:
            errors.append(f"Player {player.player_id} missing motivation.")

        if player.potential < player.overall:
            errors.append(
                f"Player {player.player_id} potential lower than overall: "
                f"{player.potential} < {player.overall}."
            )

    if errors:
        print("PLAYER ENRICHMENT VALIDATION: FAILED")
        for error in errors[:50]:
            print(f"- {error}")

        if len(errors) > 50:
            print(f"...and {len(errors) - 50} more errors.")

        raise SystemExit(1)

    print("PLAYER ENRICHMENT VALIDATION: PASS")


def print_player_enrichment_summary(league):
    print("\n============================================")
    print("PLAYER ENRICHMENT SUMMARY")
    print("============================================")

    print("Top 10 Enriched Players by Value Score:")

    top_players = sorted(
        league.player_pool,
        key=lambda player: player.value_score,
        reverse=True
    )[:10]

    for player in top_players:
        print(
            f"- ID {player.player_id}: {player.name} | {player.position} | "
            f"Age {player.age} | {player.tier} | OVR {player.overall} | "
            f"POT {player.potential} | OFF {player.offense} | DEF {player.defense} | "
            f"REB {player.rebounding} | IQ {player.basketball_iq} | "
            f"DUR {player.durability} | Risk {player.injury_risk} | "
            f"Motivation: {player.motivation}"
        )

    print("\nTier Potential Averages:")
    tier_groups = {}

    for player in league.player_pool:
        tier_groups.setdefault(player.tier, []).append(player)

    for tier in sorted(tier_groups):
        group = tier_groups[tier]
        avg_overall = round(sum(p.overall for p in group) / len(group), 1)
        avg_potential = round(sum(p.potential for p in group) / len(group), 1)
        print(f"- {tier}: OVR {avg_overall} | POT {avg_potential} | Count {len(group)}")

    print("============================================\n")



# ============================================================
# OWNER / MARKET FOUNDATION LOADERS
# ============================================================

FOUNDATION_OWNER_FILE = FOUNDATION_TEXT_DIR / "NBF FOUNDING OWNERSHIP ERA v1.0.txt"
FOUNDATION_MARKET_FILE = FOUNDATION_TEXT_DIR / "NBF MARKET and ARENA DATABASE.txt"


def parse_int_from_line(line):
    match = re.search(r"(\d+)", line)
    if match:
        return int(match.group(1))
    return 0


def normalize_money_to_billions(text):
    match = re.search(r"\$([0-9.]+)", text)
    if match:
        return float(match.group(1))
    return 0.0


def get_team_blocks(text, team_names):
    blocks = {}

    markers = []
    for team_name in team_names:
        pattern = re.compile(rf"(?m)^\s*{re.escape(team_name)}\s*$|^\s*{re.escape(team_name.upper())}\s*$")
        match = pattern.search(text)
        if match:
            markers.append((match.start(), team_name))

    markers.sort()

    for idx, (start, team_name) in enumerate(markers):
        end = markers[idx + 1][0] if idx + 1 < len(markers) else len(text)
        blocks[team_name] = text[start:end]

    return blocks


def apply_foundation_owner_profiles(league):
    if not FOUNDATION_OWNER_FILE.exists():
        raise FileNotFoundError(f"Missing foundation ownership file: {FOUNDATION_OWNER_FILE}")

    text = FOUNDATION_OWNER_FILE.read_text(encoding="utf-8", errors="replace")
    team_names = list(league.teams.keys())
    blocks = get_team_blocks(text, team_names)

    for team_name, team in league.teams.items():
        block = blocks.get(team_name, "")

        if not block:
            continue

        lines = [line.strip() for line in block.splitlines() if line.strip()]

        # Owner name appears after a line that says Owner.
        for idx, line in enumerate(lines):
            if line == "Owner" and idx + 1 < len(lines):
                team.owner.name = lines[idx + 1].replace('"', "").strip()
                break

        for line in lines:
            if line.startswith("Age:"):
                team.owner.age = parse_int_from_line(line)

            elif line.startswith("Industry:"):
                team.owner.industry = line.replace("Industry:", "").strip()

            elif line.startswith("Net Worth:"):
                worth = normalize_money_to_billions(line)
                if worth:
                    team.owner.net_worth_b = worth

            elif line.startswith("Owner Type:"):
                team.owner.owner_type = line.replace("Owner Type:", "").strip()

            elif "Winning Desire:" in line:
                team.owner.winning_desire = parse_int_from_line(line)

            elif "Patience:" in line:
                team.owner.patience = parse_int_from_line(line)

            elif "Greed:" in line:
                team.owner.greed = parse_int_from_line(line)

            elif "Control:" in line:
                team.owner.control = parse_int_from_line(line)

            elif "PR Awareness:" in line:
                team.owner.pr_awareness = parse_int_from_line(line)

        if "Philosophy" in lines:
            idx = lines.index("Philosophy")
            if idx + 1 < len(lines):
                team.owner.philosophy = lines[idx + 1].strip().strip('"')

        if "Hidden Traits" in lines:
            idx = lines.index("Hidden Traits")
            traits = []
            for line in lines[idx + 1:]:
                if line.startswith("•"):
                    traits.append(line.replace("•", "").strip())
                elif line in ["Ratings", "Philosophy"] or line.isupper():
                    break
            team.owner.hidden_traits = traits


def apply_foundation_market_profiles(league):
    if not FOUNDATION_MARKET_FILE.exists():
        raise FileNotFoundError(f"Missing foundation market file: {FOUNDATION_MARKET_FILE}")

    text = FOUNDATION_MARKET_FILE.read_text(encoding="utf-8", errors="replace")
    team_names = list(league.teams.keys())
    blocks = get_team_blocks(text, team_names)

    market_size_labels = {"Small", "Medium", "Large", "Major", "Mega"}

    for team_name, team in league.teams.items():
        block = blocks.get(team_name, "")

        if not block:
            continue

        profile = MarketProfile()
        lines = [line.strip().replace("•", "").strip() for line in block.splitlines() if line.strip()]

        for line in lines:
            if line.startswith("Arena:"):
                profile.arena = line.replace("Arena:", "").strip()

            elif line.startswith("Capacity:"):
                profile.capacity = parse_int_from_line(line.replace(",", ""))

            elif line.startswith("Atmosphere:"):
                profile.atmosphere = parse_int_from_line(line)

            elif line.startswith("Luxury:"):
                profile.luxury = parse_int_from_line(line)

            elif line.startswith("Ticket Price Index:"):
                profile.ticket_price_index = parse_int_from_line(line)

            elif line.startswith("Market Size:"):
                profile.market_size = line.replace("Market Size:", "").strip()

            elif line in market_size_labels and not profile.market_size:
                profile.market_size = line

            elif line.startswith("Fan Passion:") or line.startswith("Passion:"):
                profile.fan_passion = parse_int_from_line(line)

            elif line.startswith("Fan Loyalty:") or line.startswith("Loyalty:"):
                profile.fan_loyalty = parse_int_from_line(line)

            elif line.startswith("Fan Patience:") or line.startswith("Patience:"):
                profile.fan_patience = parse_int_from_line(line)

            elif line.startswith("Media Pressure:"):
                profile.media_pressure = parse_int_from_line(line)

            elif line.startswith("Free Agent Appeal:"):
                profile.free_agent_appeal = parse_int_from_line(line)

            elif line.startswith("Corporate Power:"):
                profile.corporate_power = parse_int_from_line(line)

        team.market_profile = profile


def apply_foundation_owner_and_market_profiles(league):
    apply_foundation_owner_profiles(league)
    apply_foundation_market_profiles(league)


def validate_owner_market_profiles(league):
    errors = []

    for team_name, team in league.teams.items():
        owner = team.owner
        market = team.market_profile

        if owner.age <= 0:
            errors.append(f"{team_name} owner missing age.")

        if not owner.industry:
            errors.append(f"{team_name} owner missing industry.")

        if owner.winning_desire <= 0:
            errors.append(f"{team_name} owner missing winning desire.")

        if market is None:
            errors.append(f"{team_name} missing market profile.")
            continue

        if not market.arena:
            errors.append(f"{team_name} missing arena.")

        if market.capacity <= 0:
            errors.append(f"{team_name} missing arena capacity.")

        if market.atmosphere <= 0:
            errors.append(f"{team_name} missing atmosphere.")

        if not market.market_size:
            errors.append(f"{team_name} missing market size.")

    if errors:
        print("OWNER / MARKET VALIDATION: FAILED")
        for error in errors:
            print(f"- {error}")
        raise SystemExit(1)

    print("OWNER / MARKET VALIDATION: PASS")


def print_owner_market_summary(league):
    print("\n============================================")
    print("OWNER / MARKET FOUNDATION SUMMARY")
    print("============================================")

    for team in league.teams.values():
        owner = team.owner
        market = team.market_profile

        print(f"\n{team.identity.name}")
        print(
            f"Owner: {owner.name} | Age {owner.age} | {owner.owner_type} | "
            f"Industry: {owner.industry} | Net Worth: ${owner.net_worth_b}B"
        )
        print(
            f"Owner Ratings: Win {owner.winning_desire} | Patience {owner.patience} | "
            f"Greed {owner.greed} | Control {owner.control} | PR {owner.pr_awareness}"
        )

        if owner.philosophy:
            print(f"Philosophy: {owner.philosophy}")

        if owner.hidden_traits:
            print(f"Hidden Traits: {', '.join(owner.hidden_traits)}")

        if market:
            print(
                f"Arena: {market.arena} | Capacity {market.capacity} | "
                f"Atmosphere {market.atmosphere} | Luxury {market.luxury}"
            )
            print(
                f"Market: {market.market_size} | Passion {market.fan_passion} | "
                f"Loyalty {market.fan_loyalty} | Patience {market.fan_patience} | "
                f"Media {market.media_pressure} | FA Appeal {market.free_agent_appeal}"
            )

    print("============================================\n")



# ============================================================
# INSTITUTIONAL FOUNDATION LOADERS
# ============================================================

FOUNDATION_REFEREE_FILE = FOUNDATION_TEXT_DIR / "NBF REFEREE POOL.txt"
FOUNDATION_REPORTER_FILE = FOUNDATION_TEXT_DIR / "NBF TEAM REPORTER POOL.txt"
FOUNDATION_AWARDS_FILE = FOUNDATION_TEXT_DIR / "NBF Awards Committee.txt"
FOUNDATION_HOF_FILE = FOUNDATION_TEXT_DIR / "Hall of Fame Committee.txt"


def institution_safe_int_from_line(line):
    match = re.search(r"(\d+)", line)
    return int(match.group(1)) if match else None


def load_foundation_referees():
    if not FOUNDATION_REFEREE_FILE.exists():
        raise FileNotFoundError(f"Missing referee file: {FOUNDATION_REFEREE_FILE}")

    text = FOUNDATION_REFEREE_FILE.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()

    referees = []
    current_tier = None
    current = None

    for line in lines:
        clean = line.strip()

        if not clean:
            continue

        if clean.isupper() and "TIER" in clean:
            current_tier = clean
            continue

        match = re.match(r"^(\d+)\.\s+(.+)$", clean)
        if match:
            if current:
                referees.append(current)

            current = Referee(
                referee_id=int(match.group(1)),
                name=match.group(2).strip(),
                tier=current_tier or "UNKNOWN TIER",
                accuracy=None,
            )
            continue

        if current and clean.startswith("Accuracy:"):
            current.accuracy = institution_safe_int_from_line(clean)

    if current:
        referees.append(current)

    return referees


def load_foundation_team_reporters():
    if not FOUNDATION_REPORTER_FILE.exists():
        raise FileNotFoundError(f"Missing reporter file: {FOUNDATION_REPORTER_FILE}")

    text = FOUNDATION_REPORTER_FILE.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()

    reporters = []
    current_team = None
    current = None

    team_names = [
        "Little Rock Bandits",
        "Dallas Outlaws",
        "Houston Cosmos",
        "Denver Peaks",
        "Phoenix Fire",
        "Los Angeles Stars",
        "Seattle Sound",
        "Portland Lumberjacks",
        "New York Empire",
        "Boston Guardians",
        "Philadelphia Riders",
        "Chicago Union",
        "Detroit Forge",
        "Atlanta Monarchs",
        "Charlotte Crown",
        "Miami Tide",
    ]

    team_upper_map = {team.upper(): team for team in team_names}

    for line in lines:
        clean = line.strip()

        if not clean:
            continue

        if clean == "NATIONAL MEDIA STARS":
            if current:
                reporters.append(current)
                current = None
            break

        if clean.upper() in team_upper_map:
            if current:
                reporters.append(current)
                current = None

            current_team = team_upper_map[clean.upper()]
            continue

        if current_team and not clean.startswith("•") and not clean.startswith("Type:") and ":" not in clean and clean != "Hidden:":
            if current:
                reporters.append(current)

            current = Reporter(
                name=clean,
                team=current_team,
                reporter_type="Unknown",
            )
            continue

        if current is None:
            continue

        if clean.startswith("Type:"):
            current.reporter_type = clean.replace("Type:", "").strip()
            continue

        if "Integrity:" in clean:
            current.integrity = institution_safe_int_from_line(clean)
            continue

        if "Aggression:" in clean:
            current.aggression = institution_safe_int_from_line(clean)
            continue

        if "Sources:" in clean:
            current.sources = institution_safe_int_from_line(clean)
            continue

        if "Popularity:" in clean:
            current.popularity = institution_safe_int_from_line(clean)
            continue

        if clean.startswith("•"):
            current.hidden_traits.append(clean.replace("•", "").strip())

    if current:
        reporters.append(current)

    return reporters


def load_foundation_awards_committee():
    if not FOUNDATION_AWARDS_FILE.exists():
        raise FileNotFoundError(f"Missing awards committee file: {FOUNDATION_AWARDS_FILE}")

    text = FOUNDATION_AWARDS_FILE.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()

    members = []
    current_category = None
    current = None

    category_patterns = [
        "National Media Voters",
        "Team Reporter Representatives",
        "Former Players",
        "Former Coaches & Executives",
        "Hall Representatives",
    ]

    for line in lines:
        clean = line.strip()

        if not clean:
            continue

        if clean.startswith("Albert Green Basketball Hall of Fame Committee"):
            break

        for category in category_patterns:
            if clean.startswith(category):
                current_category = category
                break

        match = re.match(r"^(\d+)\.\s+(.+)$", clean)
        if match:
            member_id = int(match.group(1))

            if member_id > 25:
                break

            if current:
                members.append(current)

            current = AwardsCommitteeMember(
                member_id=member_id,
                name=match.group(2).strip(),
                category=current_category or "Unknown",
            )
            continue

        if current is None:
            continue

        if clean.startswith("Outlet:") and " Type:" in clean:
            parts = clean.split(" Type:", 1)
            current.outlet = parts[0].replace("Outlet:", "").strip()
            current.member_type = parts[1].strip()
            continue

        if clean.startswith("Outlet:"):
            current.outlet = clean.replace("Outlet:", "").strip()
            continue

        if "Integrity:" in clean:
            current.integrity = institution_safe_int_from_line(clean)
            continue

        if "Popularity:" in clean:
            current.popularity = institution_safe_int_from_line(clean)
            continue

        if "Bias:" in clean:
            current.bias = institution_safe_int_from_line(clean)
            continue

    if current:
        members.append(current)

    return members[:25]


def load_foundation_hall_of_fame_committee():
    if not FOUNDATION_HOF_FILE.exists():
        raise FileNotFoundError(f"Missing Hall of Fame committee file: {FOUNDATION_HOF_FILE}")

    text = FOUNDATION_HOF_FILE.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()

    detailed = {}
    current = None

    for line in lines:
        clean = line.strip()

        if not clean:
            continue

        if clean.startswith("Hall of Fame Committee Status"):
            if current:
                detailed[current.member_id] = current
                current = None
            break

        match = re.match(r"^(\d+)\.\s+(.+)$", clean)
        if match:
            if current:
                detailed[current.member_id] = current

            current = HallOfFameCommitteeMember(
                member_id=int(match.group(1)),
                name=match.group(2).strip(),
                role="Unknown",
            )
            continue

        if current is None:
            continue

        if clean.startswith("Role:"):
            current.role = clean.replace("Role:", "").strip()
            continue

        if clean.startswith("Age:"):
            current.age = institution_safe_int_from_line(clean)
            continue

        if clean.startswith("Profession:"):
            current.profession = clean.replace("Profession:", "").strip()
            continue

        if "Integrity:" in clean:
            current.integrity = institution_safe_int_from_line(clean)
            continue

        if "Historical Knowledge:" in clean:
            current.historical_knowledge = institution_safe_int_from_line(clean)
            continue

        if "Popularity:" in clean:
            current.popularity = institution_safe_int_from_line(clean)
            continue

        if "Bias:" in clean:
            current.bias = institution_safe_int_from_line(clean)
            continue

        if "Leadership:" in clean:
            current.leadership = institution_safe_int_from_line(clean)
            continue

    if current:
        detailed[current.member_id] = current

    role_context = None
    roster_members = {}

    role_map = {
        "Chairperson": "Hall Chairperson",
        "Historians": "Historian",
        "Former Players": "Former Player Voter",
        "Former Coaches": "Former Coach Voter",
        "Former Executives": "Former Executive Voter",
        "Former Media": "Former Media Voter",
    }

    for line in lines:
        clean = line.strip().replace("✅", "").strip()

        if clean in role_map:
            role_context = role_map[clean]
            continue

        match = re.match(r"^(\d+)\s+(.+)$", clean)
        if match and role_context:
            member_id = int(match.group(1))
            name = match.group(2).strip()

            roster_members[member_id] = HallOfFameCommitteeMember(
                member_id=member_id,
                name=name,
                role=role_context,
            )

    for member_id, member in detailed.items():
        if member_id in roster_members:
            destination = roster_members[member_id]
            for attr in [
                "name",
                "role",
                "age",
                "profession",
                "integrity",
                "historical_knowledge",
                "popularity",
                "bias",
                "leadership",
            ]:
                value = getattr(member, attr)
                if value is not None and value != "Unknown":
                    setattr(destination, attr, value)
        else:
            roster_members[member_id] = member

    return [roster_members[k] for k in sorted(roster_members)]


def load_foundation_institutional_pools(league):
    league.referee_pool = load_foundation_referees()
    league.team_reporters = load_foundation_team_reporters()
    league.awards_committee = load_foundation_awards_committee()
    league.hall_of_fame_committee = load_foundation_hall_of_fame_committee()


def validate_foundation_institutional_pools(league):
    errors = []

    if len(league.referee_pool) != 50:
        errors.append(f"Expected 50 referees, found {len(league.referee_pool)}.")

    if len(league.team_reporters) != 32:
        errors.append(f"Expected 32 team reporters, found {len(league.team_reporters)}.")

    if len(league.awards_committee) != 25:
        errors.append(f"Expected 25 awards committee members, found {len(league.awards_committee)}.")

    if len(league.hall_of_fame_committee) != 15:
        errors.append(f"Expected 15 Hall of Fame committee members, found {len(league.hall_of_fame_committee)}.")

    reporters_by_team = {}

    for reporter in league.team_reporters:
        reporters_by_team[reporter.team] = reporters_by_team.get(reporter.team, 0) + 1

    for team_name in league.teams:
        if reporters_by_team.get(team_name, 0) != 2:
            errors.append(f"{team_name} expected 2 reporters, found {reporters_by_team.get(team_name, 0)}.")

    if errors:
        print("INSTITUTIONAL POOLS VALIDATION: FAILED")
        for error in errors:
            print(f"- {error}")
        raise SystemExit(1)

    print("INSTITUTIONAL POOLS VALIDATION: PASS")


def print_institutional_pool_summary(league):
    print("\n============================================")
    print("INSTITUTIONAL FOUNDATION SUMMARY")
    print("============================================")
    print(f"Referees: {len(league.referee_pool)}")
    print(f"Team Reporters: {len(league.team_reporters)}")
    print(f"Awards Committee: {len(league.awards_committee)}")
    print(f"Hall of Fame Committee: {len(league.hall_of_fame_committee)}")

    print("\nTop Referees:")
    for referee in league.referee_pool[:10]:
        print(
            f"- ID {referee.referee_id}: {referee.name} | "
            f"{referee.tier} | Accuracy {referee.accuracy}"
        )

    print("\nTeam Reporter Assignment:")
    for team_name in league.teams:
        reporters = [reporter for reporter in league.team_reporters if reporter.team == team_name]
        names = ", ".join(f"{reporter.name} ({reporter.reporter_type})" for reporter in reporters)
        print(f"- {team_name}: {names}")

    print("\nAwards Committee Categories:")
    category_counts = {}
    for member in league.awards_committee:
        category_counts[member.category] = category_counts.get(member.category, 0) + 1

    for category in sorted(category_counts):
        print(f"- {category}: {category_counts[category]}")

    print("\nHall of Fame Committee:")
    for member in league.hall_of_fame_committee:
        print(f"- ID {member.member_id}: {member.name} | {member.role}")

    print("============================================\n")


# ============================================================
# LEAGUE BUILD
# ============================================================

def build_league() -> League:
    league = League(
        name="National Basketball Federation",
        motto="Ball On 'Em",
        championship_trophy="Albert Green Championship Trophy",
        hall_of_fame_name="Albert Green Basketball Hall of Fame",
        hall_of_fame_location="Springfield, Missouri",
        commissioner=build_commissioner(),
        rules=build_rules(),
        teams=build_teams(),
        current_year=0,
        public_era_start_year=51,
        gm_pool=generate_gm_pool(32),
        coach_pool=generate_coach_pool(32),
        player_pool=load_foundation_player_pool()
    )

    enrich_foundation_players(league.player_pool)

    league.history.append(
        "Year 0: The National Basketball Federation was founded by Albert Green."
    )

    return league


# ============================================================
# VALIDATION
# ============================================================

def validate_league_foundation(league: League) -> None:
    errors = []

    if len(league.teams) != 16:
        errors.append(f"Expected 16 teams, found {len(league.teams)}.")

    eastern = [team for team in league.teams.values() if team.identity.conference == "Eastern"]
    western = [team for team in league.teams.values() if team.identity.conference == "Western"]

    if len(eastern) != 8:
        errors.append(f"Expected 8 Eastern teams, found {len(eastern)}.")

    if len(western) != 8:
        errors.append(f"Expected 8 Western teams, found {len(western)}.")

    if league.rules.hard_cap_m != 210:
        errors.append("Hard cap must be $210M.")

    if league.public_era_start_year != 51:
        errors.append("Public Era must begin in Season 51.")

    if len(league.gm_pool) < 16:
        errors.append("GM pool must have at least 16 candidates.")

    if len(league.coach_pool) < 16:
        errors.append("Coach pool must have at least 16 candidates.")

    for team_name, team in league.teams.items():
        if team.gm is not None:
            errors.append(f"{team_name} should not have an assigned GM at Year 0.")

        if team.coach is not None:
            errors.append(f"{team_name} should not have an assigned coach at Year 0.")

        if len(team.roster) != 0:
            errors.append(f"{team_name} should not have active players at Year 0.")

    if errors:
        print("FOUNDATION VALIDATION: FAILED")
        for error in errors:
            print(f"- {error}")
        raise SystemExit(1)

    print("FOUNDATION VALIDATION: PASS")


def validate_year_1_staff_setup(league: League) -> None:
    errors = []

    for team_name, team in league.teams.items():
        if team.gm is None:
            errors.append(f"{team_name} does not have a GM after Year 1 staff setup.")

        if team.coach is None:
            errors.append(f"{team_name} does not have a coach after Year 1 staff setup.")

        if team.gm and team.gm.employed_by != team_name:
            errors.append(f"{team.gm.name} employment mismatch for {team_name}.")

        if team.coach and team.coach.employed_by != team_name:
            errors.append(f"{team.coach.name} employment mismatch for {team_name}.")

    hired_gms = [team.gm.name for team in league.teams.values() if team.gm]
    hired_coaches = [team.coach.name for team in league.teams.values() if team.coach]

    if len(hired_gms) != len(set(hired_gms)):
        errors.append("Duplicate GM assignment detected.")

    if len(hired_coaches) != len(set(hired_coaches)):
        errors.append("Duplicate coach assignment detected.")

    if errors:
        print("YEAR 1 STAFF VALIDATION: FAILED")
        for error in errors:
            print(f"- {error}")
        raise SystemExit(1)

    print("YEAR 1 STAFF VALIDATION: PASS")



def validate_foundation_pools(league: League) -> None:
    errors = []

    if len(league.player_pool) != 500:
        errors.append(f"Expected 500 foundation players, found {len(league.player_pool)}.")

    if len(league.gm_pool) != 50:
        errors.append(f"Expected 50 foundation GMs, found {len(league.gm_pool)}.")

    if len(league.coach_pool) != 60:
        errors.append(f"Expected 60 foundation coaches, found {len(league.coach_pool)}.")

    player_ids = [player.player_id for player in league.player_pool]

    if len(player_ids) != len(set(player_ids)):
        errors.append("Duplicate player IDs detected.")

    valid_positions = {"PG", "SG", "SF", "PF", "C"}
    valid_tiers = {"Generational", "Superstar", "Star", "Starter", "Role", "Fringe"}

    for player in league.player_pool:
        if player.position not in valid_positions:
            errors.append(f"Invalid player position: ID {player.player_id} {player.position}")

        if player.tier not in valid_tiers:
            errors.append(f"Invalid player tier: ID {player.player_id} {player.tier}")

    if errors:
        print("FOUNDATION POOLS VALIDATION: FAILED")
        for error in errors:
            print(f"- {error}")
        raise SystemExit(1)

    print("FOUNDATION POOLS VALIDATION: PASS")


def print_foundation_pool_summary(league: League) -> None:
    print("\n============================================")
    print("FOUNDATION POOLS LOADED")
    print("============================================")
    print(f"Players: {len(league.player_pool)}")
    print(f"GMs: {len(league.gm_pool)}")
    print(f"Coaches: {len(league.coach_pool)}")

    print("\nTop 10 Players by Overall:")
    top_players = sorted(league.player_pool, key=lambda p: p.overall, reverse=True)[:10]

    for player in top_players:
        print(
            f"- ID {player.player_id}: {player.name} | {player.position} | "
            f"Age {player.age} | {player.tier} | OVR {player.overall}"
        )

    print("\nFirst 10 GM Candidates:")
    for gm in league.gm_pool[:10]:
        print(f"- {gm.name} | Age {gm.age} | {gm.personality} | OVR {gm.overall}")

    print("\nFirst 10 Coach Candidates:")
    for coach in league.coach_pool[:10]:
        print(f"- {coach.name} | Age {coach.age} | {coach.personality} | OVR {coach.overall}")

    print("============================================\n")


# ============================================================
# DISPLAY
# ============================================================

def print_league_summary(league: League) -> None:
    print("\n============================================")
    print("NBF / LBU FOUNDATION LOADED")
    print("============================================")
    print(f"League: {league.name}")
    print(f"Motto: {league.motto}")
    print(f"Trophy: {league.championship_trophy}")
    print(f"Commissioner: {league.commissioner.name}")
    print(f"Hall of Fame: {league.hall_of_fame_name}")
    print(f"Hall Location: {league.hall_of_fame_location}")
    print(f"Current Year: {league.current_year}")
    print(f"Public Era Begins: Season {league.public_era_start_year}")
    print(f"GM Pool Size: {len(league.gm_pool)}")
    print(f"Coach Pool Size: {len(league.coach_pool)}")
    print(f"Player Pool Size: {len(league.player_pool)}")

    print("\nEastern Conference:")
    for team in league.teams.values():
        if team.identity.conference == "Eastern":
            print(f"- {team.identity.name} | Owner: {team.owner.name}")

    print("\nWestern Conference:")
    for team in league.teams.values():
        if team.identity.conference == "Western":
            print(f"- {team.identity.name} | Owner: {team.owner.name}")

    print("\nHistory Log:")
    for event in league.history:
        print(f"- {event}")

    print("============================================\n")


def print_staff_assignments(league: League) -> None:
    print("\n============================================")
    print("YEAR 1 STAFF ASSIGNMENTS")
    print("============================================")

    for team in league.teams.values():
        gm = team.gm
        coach = team.coach

        print(f"\n{team.identity.name}")
        print(f"Owner: {team.owner.name} | Type: {team.owner.owner_type}")

        if gm:
            print(
                f"GM: {gm.name} | OVR {gm.overall} | "
                f"Scouting {gm.scouting} | Development {gm.development} | "
                f"Leadership {gm.leadership} | Personality: {gm.personality}"
            )

        if coach:
            print(
                f"Coach: {coach.name} | OVR {coach.overall} | "
                f"Offense {coach.offense} | Defense {coach.defense} | "
                f"Development {coach.development} | Personality: {coach.personality}"
            )

    print("============================================\n")



# ============================================================
# INAUGURAL DRAFT
# ============================================================

def tier_draft_bonus(tier):
    bonuses = {
        "Generational": 30,
        "Superstar": 24,
        "Star": 17,
        "Starter": 10,
        "Role": 4,
        "Fringe": 0,
    }
    return bonuses.get(tier, 0)


def team_position_need_score(team, player):
    position_counts = {
        "PG": 0,
        "SG": 0,
        "SF": 0,
        "PF": 0,
        "C": 0,
    }

    for roster_player in team.roster:
        position_counts[roster_player.position] += 1

    count = position_counts[player.position]

    if count == 0:
        return 20
    if count == 1:
        return 10
    if count == 2:
        return 3

    return -8


def score_player_for_team(player, team):
    if team.gm is None:
        raise RuntimeError(f"{team.identity.name} cannot draft without a GM.")

    if team.coach is None:
        raise RuntimeError(f"{team.identity.name} cannot draft without a coach.")

    score = 0

    # Base player value.
    score += player.overall
    score += tier_draft_bonus(player.tier)

    # Younger players carry more future value.
    if player.age <= 22:
        score += 8
    elif player.age <= 25:
        score += 5
    elif player.age <= 29:
        score += 2
    elif player.age >= 35:
        score -= 7

    # GM influence.
    score += team.gm.scouting * 0.12
    score += team.gm.development * 0.05

    # Coach influence.
    if team.coach.offense >= team.coach.defense:
        if player.position in ["PG", "SG", "SF"]:
            score += 4
    else:
        if player.position in ["PF", "C", "SF"]:
            score += 4

    # Roster construction.
    score += team_position_need_score(team, player)

    # Team identity flavor.
    if team.identity.name == "Little Rock Bandits":
        # Bandits culture: "We're Gonna Take Our Respect"
        if player.tier in ["Generational", "Superstar", "Star"]:
            score += 2
        if player.position in ["PF", "C"]:
            score += 1

    # Organic uncertainty.
    score += random.uniform(-4, 4)

    return score


def run_inaugural_draft(league, rounds=12):
    if len(league.player_pool) < len(league.teams) * rounds:
        raise RuntimeError("Not enough players in Foundation pool for inaugural draft.")

    teams = list(league.teams.values())

    # Randomized inaugural order.
    draft_order = teams[:]
    random.shuffle(draft_order)

    league.history.append("Year 1: The first NBF Inaugural Draft began.")

    pick_number = 1

    for round_number in range(1, rounds + 1):
        # Snake draft for competitive balance.
        if round_number % 2 == 1:
            round_order = draft_order
        else:
            round_order = list(reversed(draft_order))

        for team in round_order:
            available_players = [
                player for player in league.player_pool
                if player.team is None and not player.retired
            ]

            if not available_players:
                raise RuntimeError("No available players left during inaugural draft.")

            selected_player = max(
                available_players,
                key=lambda player: score_player_for_team(player, team)
            )

            selected_player.team = team.identity.name
            selected_player.draft_year = league.current_year
            selected_player.draft_pick = pick_number

            team.roster.append(selected_player)

            if pick_number <= 16:
                league.history.append(
                    f"Year 1 Inaugural Draft Pick {pick_number}: "
                    f"{team.identity.name} selected {selected_player.name}, "
                    f"{selected_player.position}, {selected_player.tier}, "
                    f"OVR {selected_player.overall}."
                )

            pick_number += 1

    league.history.append(
        f"Year 1: The inaugural NBF Draft concluded after {rounds} rounds."
    )


def validate_inaugural_draft(league, expected_roster_size=12):
    errors = []

    drafted_player_ids = []

    for team_name, team in league.teams.items():
        if len(team.roster) != expected_roster_size:
            errors.append(
                f"{team_name} expected {expected_roster_size} players, found {len(team.roster)}."
            )

        for player in team.roster:
            drafted_player_ids.append(player.player_id)

            if player.team != team_name:
                errors.append(
                    f"Player/team mismatch: {player.name} says {player.team}, expected {team_name}."
                )

            if player.draft_year != 1:
                errors.append(f"{player.name} should have draft year 1.")

            if player.draft_pick is None:
                errors.append(f"{player.name} is missing draft pick.")

    if len(drafted_player_ids) != len(set(drafted_player_ids)):
        errors.append("Duplicate drafted player ID detected.")

    total_drafted = len(drafted_player_ids)

    if total_drafted != len(league.teams) * expected_roster_size:
        errors.append(
            f"Expected {len(league.teams) * expected_roster_size} drafted players, found {total_drafted}."
        )

    if errors:
        print("INAUGURAL DRAFT VALIDATION: FAILED")
        for error in errors:
            print(f"- {error}")
        raise SystemExit(1)

    print("INAUGURAL DRAFT VALIDATION: PASS")


def print_inaugural_draft_summary(league):
    print("\n============================================")
    print("YEAR 1 INAUGURAL DRAFT SUMMARY")
    print("============================================")

    drafted_count = len([player for player in league.player_pool if player.team is not None])
    available_count = len([player for player in league.player_pool if player.team is None])

    print(f"Drafted Players: {drafted_count}")
    print(f"Remaining Available Players: {available_count}")

    print("\nFirst Round:")
    first_round = sorted(
        [player for player in league.player_pool if player.draft_pick and player.draft_pick <= 16],
        key=lambda player: player.draft_pick
    )

    for player in first_round:
        print(
            f"- Pick {player.draft_pick}: {player.team} selected "
            f"{player.name} | {player.position} | Age {player.age} | "
            f"{player.tier} | OVR {player.overall}"
        )

    print("\nTeam Roster Cores:")
    for team in league.teams.values():
        top_players = sorted(
            team.roster,
            key=lambda player: player.value_score,
            reverse=True
        )[:5]

        print(f"\n{team.identity.name}")
        for player in top_players:
            print(
                f"- Pick {player.draft_pick}: {player.name} | {player.position} | "
                f"Age {player.age} | {player.tier} | OVR {player.overall}"
            )

    print("============================================\n")



# ============================================================
# INAUGURAL DRAFT ENGINE
# ============================================================

INITIAL_DRAFT_ROUNDS = 12


def get_player_value(player) -> float:
    overall = getattr(player, "overall", 65)
    potential = getattr(player, "potential", overall)

    tier = str(getattr(player, "tier", "")).lower()

    tier_bonus = 0
    if "generational" in tier:
        tier_bonus = 18
    elif "superstar" in tier:
        tier_bonus = 12
    elif "star" in tier:
        tier_bonus = 7
    elif "starter" in tier:
        tier_bonus = 3

    age = getattr(player, "age", 24)
    age_bonus = 0

    if age <= 21:
        age_bonus = 6
    elif age <= 24:
        age_bonus = 4
    elif age <= 28:
        age_bonus = 2
    elif age >= 34:
        age_bonus = -5

    return (overall * 1.0) + (potential * 0.35) + tier_bonus + age_bonus


def get_position_need_bonus(team, player) -> float:
    position = getattr(player, "position", None)

    if not position:
        return 0

    position_counts = {}

    for roster_player in team.roster:
        roster_position = getattr(roster_player, "position", None)
        if roster_position:
            position_counts[roster_position] = position_counts.get(roster_position, 0) + 1

    current_count = position_counts.get(position, 0)

    if current_count == 0:
        return 16
    if current_count == 1:
        return 8
    if current_count == 2:
        return 2

    return -6


def score_player_for_draft_team(player, team) -> float:
    score = get_player_value(player)
    score += get_position_need_bonus(team, player)

    gm = team.gm
    coach = team.coach

    if gm:
        scouting = getattr(gm, "scouting", 68)
        development = getattr(gm, "development", 68)
        score += scouting * 0.05
        score += development * 0.03

    if coach:
        offense = getattr(coach, "offense", 68)
        defense = getattr(coach, "defense", 68)

        # If coach leans offensive, prioritize offensive player value if available.
        if offense >= defense:
            scoring = getattr(player, "scoring", getattr(player, "overall", 65))
            shooting = getattr(player, "shooting", getattr(player, "overall", 65))
            playmaking = getattr(player, "playmaking", getattr(player, "overall", 65))
            score += (scoring + shooting + playmaking) / 45
        else:
            defense_rating = getattr(player, "defense", getattr(player, "overall", 65))
            rebounding = getattr(player, "rebounding", getattr(player, "overall", 65))
            score += (defense_rating + rebounding) / 30

    # Little Rock culture flavor.
    if team.identity.name == "Little Rock Bandits":
        ambition = getattr(player, "ambition", 68)
        defense_rating = getattr(player, "defense", getattr(player, "overall", 65))
        score += ambition * 0.04
        score += defense_rating * 0.03

    # Organic uncertainty.
    score += random.uniform(-3.5, 3.5)

    return score


def run_inaugural_draft(league, rounds: int = INITIAL_DRAFT_ROUNDS) -> None:
    if not league.player_pool:
        raise RuntimeError("Cannot run inaugural draft: player_pool is empty.")

    if any(len(team.roster) > 0 for team in league.teams.values()):
        raise RuntimeError("Cannot run inaugural draft: at least one team already has players.")

    league.history.append("Year 1: The first NBF Inaugural Draft began.")

    teams = list(league.teams.values())
    draft_order = teams[:]
    random.shuffle(draft_order)

    pick_number = 1

    for round_number in range(1, rounds + 1):
        if round_number % 2 == 1:
            round_order = draft_order
        else:
            round_order = list(reversed(draft_order))

        for team in round_order:
            available_players = [
                player for player in league.player_pool
                if getattr(player, "team", None) is None
            ]

            if not available_players:
                raise RuntimeError("Cannot continue draft: no available players left.")

            selected_player = max(
                available_players,
                key=lambda player: score_player_for_draft_team(player, team)
            )

            selected_player.team = team.identity.name
            selected_player.draft_year = league.current_year
            selected_player.draft_pick = pick_number
            selected_player.drafted_by = team.identity.name

            team.roster.append(selected_player)

            if pick_number <= 16:
                league.history.append(
                    f"Year 1 Draft Pick {pick_number}: {team.identity.name} selected "
                    f"{getattr(selected_player, 'name', 'Unknown Player')} "
                    f"({getattr(selected_player, 'position', 'N/A')}), "
                    f"OVR {getattr(selected_player, 'overall', 'N/A')}."
                )

            pick_number += 1

    league.history.append(
        f"Year 1: The inaugural NBF Draft concluded after {rounds} rounds."
    )


def validate_inaugural_draft(league, expected_roster_size: int = INITIAL_DRAFT_ROUNDS) -> None:
    errors = []
    drafted_player_keys = []

    for team_name, team in league.teams.items():
        if len(team.roster) != expected_roster_size:
            errors.append(
                f"{team_name} expected {expected_roster_size} players, found {len(team.roster)}."
            )

        for player in team.roster:
            player_key = getattr(player, "player_id", None) or getattr(player, "id", None) or getattr(player, "name", None)
            drafted_player_keys.append(player_key)

            if getattr(player, "team", None) != team_name:
                errors.append(
                    f"{getattr(player, 'name', 'Unknown Player')} team mismatch. "
                    f"Expected {team_name}, found {getattr(player, 'team', None)}."
                )

            if getattr(player, "draft_year", None) != league.current_year:
                errors.append(
                    f"{getattr(player, 'name', 'Unknown Player')} has invalid draft year."
                )

            if getattr(player, "draft_pick", None) is None:
                errors.append(
                    f"{getattr(player, 'name', 'Unknown Player')} missing draft pick."
                )

    if len(drafted_player_keys) != len(set(drafted_player_keys)):
        errors.append("Duplicate drafted player detected.")

    if errors:
        print("INAUGURAL DRAFT VALIDATION: FAILED")
        for error in errors:
            print(f"- {error}")
        raise SystemExit(1)

    print("INAUGURAL DRAFT VALIDATION: PASS")


def print_inaugural_draft_summary(league) -> None:
    print("\n============================================")
    print("YEAR 1 INAUGURAL DRAFT SUMMARY")
    print("============================================")

    all_drafted = []

    for team in league.teams.values():
        for player in team.roster:
            all_drafted.append(player)

    all_drafted = sorted(
        all_drafted,
        key=lambda player: getattr(player, "draft_pick", 9999)
    )

    print("\nTop 16 Draft Picks:")
    for player in all_drafted[:16]:
        print(
            f"- Pick {getattr(player, 'draft_pick', 'N/A')}: "
            f"{getattr(player, 'name', 'Unknown Player')} | "
            f"{getattr(player, 'position', 'N/A')} | "
            f"Age {getattr(player, 'age', 'N/A')} | "
            f"{getattr(player, 'tier', 'N/A')} | "
            f"OVR {getattr(player, 'overall', 'N/A')} | "
            f"Team: {getattr(player, 'team', 'N/A')}"
        )

    print("\nTeam Roster Cores:")
    for team in league.teams.values():
        sorted_roster = sorted(
            team.roster,
            key=lambda player: get_player_value(player),
            reverse=True
        )

        print(f"\n{team.identity.name}")
        print(f"GM: {team.gm.name if team.gm else 'None'} | Coach: {team.coach.name if team.coach else 'None'}")

        for player in sorted_roster[:5]:
            print(
                f"- Pick {getattr(player, 'draft_pick', 'N/A')}: "
                f"{getattr(player, 'name', 'Unknown Player')} | "
                f"{getattr(player, 'position', 'N/A')} | "
                f"Age {getattr(player, 'age', 'N/A')} | "
                f"{getattr(player, 'tier', 'N/A')} | "
                f"OVR {getattr(player, 'overall', 'N/A')}"
            )

    print("============================================\n")



# ============================================================
# REGULAR SEASON ENGINE
# ============================================================

REGULAR_SEASON_GAMES_PER_TEAM = 30


def reset_team_records(league) -> None:
    for team in league.teams.values():
        team.wins = 0
        team.losses = 0


def get_team_core_players(team, core_size: int = 8):
    return sorted(
        team.roster,
        key=lambda player: get_player_value(player),
        reverse=True
    )[:core_size]


def calculate_team_strength(team) -> float:
    if not team.roster:
        return 0.0

    core_players = get_team_core_players(team, core_size=8)

    roster_score = sum(get_player_value(player) for player in core_players) / len(core_players)

    gm_bonus = 0
    coach_bonus = 0

    if team.gm:
        gm_bonus += getattr(team.gm, "scouting", 68) * 0.025
        gm_bonus += getattr(team.gm, "development", 68) * 0.020
        gm_bonus += getattr(team.gm, "leadership", 68) * 0.025

    if team.coach:
        coach_bonus += getattr(team.coach, "offense", 68) * 0.030
        coach_bonus += getattr(team.coach, "defense", 68) * 0.030
        coach_bonus += getattr(team.coach, "development", 68) * 0.015
        coach_bonus += getattr(team.coach, "leadership", 68) * 0.020

    chemistry_bonus = calculate_team_chemistry(team)

    return roster_score + gm_bonus + coach_bonus + chemistry_bonus


def calculate_team_chemistry(team) -> float:
    if not team.roster:
        return 0.0

    avg_discipline = sum(getattr(player, "discipline", 68) for player in team.roster) / len(team.roster)
    avg_loyalty = sum(getattr(player, "loyalty", 68) for player in team.roster) / len(team.roster)

    coach_leadership = getattr(team.coach, "leadership", 68) if team.coach else 68
    gm_leadership = getattr(team.gm, "leadership", 68) if team.gm else 68

    chemistry = (
        avg_discipline * 0.025
        + avg_loyalty * 0.020
        + coach_leadership * 0.030
        + gm_leadership * 0.020
    )

    return chemistry


def simulate_regular_season_game(home_team, away_team) -> None:
    home_strength = calculate_team_strength(home_team)
    away_strength = calculate_team_strength(away_team)

    # Home court advantage.
    home_strength += 2.5

    # Rivalry intensity increases volatility.
    rivalry_game = away_team.identity.name in home_team.identity.rivals
    blood_rivalry_game = away_team.identity.name in home_team.identity.blood_rivals

    volatility = 8.0

    if rivalry_game:
        volatility += 2.5

    if blood_rivalry_game:
        volatility += 4.0

    home_score = home_strength + random.uniform(-volatility, volatility)
    away_score = away_strength + random.uniform(-volatility, volatility)

    if home_score >= away_score:
        home_team.wins += 1
        away_team.losses += 1
    else:
        away_team.wins += 1
        home_team.losses += 1


def build_regular_season_schedule(league):
    teams = list(league.teams.values())
    schedule = []

    for i in range(len(teams)):
        for j in range(i + 1, len(teams)):
            team_a = teams[i]
            team_b = teams[j]

            # Each pair plays twice, swapping home court.
            schedule.append((team_a, team_b))
            schedule.append((team_b, team_a))

    random.shuffle(schedule)
    return schedule


def run_regular_season(league) -> None:
    if any(len(team.roster) == 0 for team in league.teams.values()):
        raise RuntimeError("Cannot run regular season: at least one team has no roster.")

    reset_team_records(league)

    schedule = build_regular_season_schedule(league)

    league.history.append(f"Year {league.current_year}: The NBF regular season began.")

    for home_team, away_team in schedule:
        simulate_regular_season_game(home_team, away_team)

    league.history.append(f"Year {league.current_year}: The NBF regular season concluded.")


def validate_regular_season(league, expected_games_per_team: int = REGULAR_SEASON_GAMES_PER_TEAM) -> None:
    errors = []

    total_wins = 0
    total_losses = 0

    for team_name, team in league.teams.items():
        games_played = team.wins + team.losses

        total_wins += team.wins
        total_losses += team.losses

        if games_played != expected_games_per_team:
            errors.append(
                f"{team_name} expected {expected_games_per_team} games, found {games_played}."
            )

    if total_wins != total_losses:
        errors.append(f"Total wins/losses mismatch: wins {total_wins}, losses {total_losses}.")

    expected_total_games = (len(league.teams) * expected_games_per_team) // 2

    if total_wins != expected_total_games:
        errors.append(
            f"Expected {expected_total_games} total games, found {total_wins}."
        )

    if errors:
        print("REGULAR SEASON VALIDATION: FAILED")
        for error in errors:
            print(f"- {error}")
        raise SystemExit(1)

    print("REGULAR SEASON VALIDATION: PASS")


def get_sorted_standings(league):
    return sorted(
        league.teams.values(),
        key=lambda team: (
            team.wins,
            calculate_team_strength(team)
        ),
        reverse=True
    )


def print_regular_season_summary(league) -> None:
    print("\n============================================")
    print(f"YEAR {league.current_year} REGULAR SEASON SUMMARY")
    print("============================================")

    overall_standings = get_sorted_standings(league)

    print("\nOverall Standings:")
    for rank, team in enumerate(overall_standings, start=1):
        strength = calculate_team_strength(team)
        print(
            f"{rank}. {team.identity.name} | "
            f"{team.wins}-{team.losses} | "
            f"Strength {strength:.1f}"
        )

    print("\nEastern Conference:")
    eastern = [
        team for team in overall_standings
        if team.identity.conference == "Eastern"
    ]

    for rank, team in enumerate(eastern, start=1):
        print(f"{rank}. {team.identity.name} | {team.wins}-{team.losses}")

    print("\nWestern Conference:")
    western = [
        team for team in overall_standings
        if team.identity.conference == "Western"
    ]

    for rank, team in enumerate(western, start=1):
        print(f"{rank}. {team.identity.name} | {team.wins}-{team.losses}")

    print("\nTop Team Cores After Regular Season:")
    for team in overall_standings[:5]:
        core = get_team_core_players(team, core_size=3)
        print(f"\n{team.identity.name} | {team.wins}-{team.losses}")
        for player in core:
            print(
                f"- {getattr(player, 'name', 'Unknown Player')} | "
                f"{getattr(player, 'position', 'N/A')} | "
                f"{getattr(player, 'tier', 'N/A')} | "
                f"OVR {getattr(player, 'overall', 'N/A')}"
            )

    print("============================================\n")




# ============================================================
# REGULAR SEASON PLAYER STATS
# ============================================================

def reset_regular_season_player_stats(league):
    for player in league.player_pool:
        player.season_games = 0
        player.season_points = 0
        player.season_rebounds = 0
        player.season_assists = 0
        player.season_impact = 0.0


def regular_season_player_game_rng(league, player, opponent_name, game_number):
    seed = (
        f"NBF-LBU-v1:regular-player:{league.current_year}:"
        f"G{game_number}:{player.player_id}:{player.name}:{opponent_name}"
    )
    return random.Random(seed)


def record_regular_season_game_performances(league, winning_team, losing_team, game_number):
    for team, won_game in [(winning_team, True), (losing_team, False)]:
        opponent = losing_team if won_game else winning_team
        rotation = top_rotation(team, size=8)

        for rotation_index, player in enumerate(rotation):
            rng = regular_season_player_game_rng(
                league,
                player,
                opponent.identity.name,
                game_number
            )

            role_multiplier = max(0.45, 1.10 - (rotation_index * 0.085))

            tier_multiplier = {
                "Generational": 1.32,
                "Superstar": 1.20,
                "Star": 1.08,
                "Starter": 0.94,
                "Role": 0.76,
                "Fringe": 0.55,
            }.get(player.tier, 0.76)

            points = max(
                0,
                int(
                    ((player.offense + player.shooting + player.confidence) / 15)
                    * role_multiplier
                    * tier_multiplier
                    + rng.gauss(0, 4)
                )
            )

            rebounds = max(
                0,
                int(
                    ((player.rebounding + player.athleticism) / 22)
                    * role_multiplier
                    * tier_multiplier
                    + rng.gauss(0, 2)
                )
            )

            assists = max(
                0,
                int(
                    ((player.playmaking + player.basketball_iq) / 24)
                    * role_multiplier
                    * tier_multiplier
                    + rng.gauss(0, 2)
                )
            )

            impact = (
                points * 0.50
                + rebounds * 0.32
                + assists * 0.38
                + player.defense * 0.06
                + player.basketball_iq * 0.04
                + player.leadership * 0.03
            )

            if won_game:
                impact += 5

            player.season_games += 1
            player.season_points += points
            player.season_rebounds += rebounds
            player.season_assists += assists
            player.season_impact += impact

            player.career_points += points
            player.career_rebounds += rebounds
            player.career_assists += assists


def validate_regular_season_player_stats(league):
    errors = []

    active_players = [
        player for player in league.player_pool
        if player.team is not None
    ]

    if not active_players:
        errors.append("No active players found for regular season stat validation.")

    players_with_games = [
        player for player in active_players
        if player.season_games > 0
    ]

    if len(players_with_games) == 0:
        errors.append("No players recorded regular season games.")

    for team in league.teams.values():
        rotation = top_rotation(team, size=8)

        for player in rotation:
            if player.season_games <= 0:
                errors.append(f"{player.name} on {team.identity.name} has no regular season games.")

    if errors:
        print("REGULAR SEASON PLAYER STATS VALIDATION: FAILED")
        for error in errors[:50]:
            print(f"- {error}")

        if len(errors) > 50:
            print(f"...and {len(errors) - 50} more errors.")

        raise SystemExit(1)

    print("REGULAR SEASON PLAYER STATS VALIDATION: PASS")


def player_points_per_game(player):
    if player.season_games == 0:
        return 0
    return player.season_points / player.season_games


def player_rebounds_per_game(player):
    if player.season_games == 0:
        return 0
    return player.season_rebounds / player.season_games


def player_assists_per_game(player):
    if player.season_games == 0:
        return 0
    return player.season_assists / player.season_games


def print_regular_season_player_summary(league):
    print("\n============================================")
    print("YEAR 1 REGULAR SEASON PLAYER LEADERS")
    print("============================================")

    active_players = [
        player for player in league.player_pool
        if player.team is not None and player.season_games > 0
    ]

    top_impact = sorted(
        active_players,
        key=lambda player: player.season_impact,
        reverse=True
    )[:15]

    print("\nTop 15 by Season Impact:")
    for rank, player in enumerate(top_impact, start=1):
        print(
            f"{rank}. {player.name} | {player.team} | {player.position} | "
            f"{player.tier} | GP {player.season_games} | "
            f"PPG {player_points_per_game(player):.1f} | "
            f"RPG {player_rebounds_per_game(player):.1f} | "
            f"APG {player_assists_per_game(player):.1f} | "
            f"Impact {player.season_impact:.1f}"
        )

    top_scorers = sorted(
        active_players,
        key=lambda player: player_points_per_game(player),
        reverse=True
    )[:10]

    print("\nTop 10 Scorers:")
    for rank, player in enumerate(top_scorers, start=1):
        print(
            f"{rank}. {player.name} | {player.team} | "
            f"PPG {player_points_per_game(player):.1f}"
        )

    print("============================================\n")


# ============================================================
# REGULAR SEASON SIMULATION
# ============================================================

REGULAR_SEASON_SERIES_PER_MATCHUP = 4
EXPECTED_REGULAR_SEASON_GAMES = 60


def reset_team_records(league):
    for team in league.teams.values():
        team.wins = 0
        team.losses = 0


def top_rotation(team, size=8):
    return sorted(
        team.roster,
        key=lambda player: player.value_score,
        reverse=True
    )[:size]


def team_roster_strength(team):
    rotation = top_rotation(team)

    if not rotation:
        return 0

    avg_overall = sum(player.overall for player in rotation) / len(rotation)
    avg_potential = sum(player.potential for player in rotation) / len(rotation)
    avg_offense = sum(player.offense for player in rotation) / len(rotation)
    avg_defense = sum(player.defense for player in rotation) / len(rotation)
    avg_iq = sum(player.basketball_iq for player in rotation) / len(rotation)
    avg_durability = sum(player.durability for player in rotation) / len(rotation)

    star_bonus = 0
    for player in rotation[:3]:
        if player.tier == "Generational":
            star_bonus += 7
        elif player.tier == "Superstar":
            star_bonus += 5
        elif player.tier == "Star":
            star_bonus += 3

    return (
        avg_overall * 0.45
        + avg_potential * 0.10
        + avg_offense * 0.14
        + avg_defense * 0.14
        + avg_iq * 0.08
        + avg_durability * 0.04
        + star_bonus
    )


def team_staff_strength(team):
    gm_bonus = 0
    coach_bonus = 0

    if team.gm:
        gm_bonus = (
            team.gm.scouting * 0.03
            + team.gm.development * 0.03
            + team.gm.leadership * 0.03
        )

    if team.coach:
        coach_bonus = (
            team.coach.offense * 0.05
            + team.coach.defense * 0.05
            + team.coach.development * 0.02
            + team.coach.leadership * 0.03
            + team.coach.adaptability * 0.02
        )

    return gm_bonus + coach_bonus


def team_market_home_bonus(team):
    if not team.market_profile:
        return 2.5

    atmosphere = team.market_profile.atmosphere or 70
    fan_passion = team.market_profile.fan_passion or 70

    return 1.5 + ((atmosphere + fan_passion) / 100)


def total_team_strength(team, home=False):
    strength = team_roster_strength(team) + team_staff_strength(team)

    if home:
        strength += team_market_home_bonus(team)

    return strength


def game_rng(league, home_team, away_team, game_number):
    seed = (
        f"NBF-LBU-v1:season:{league.current_year}:"
        f"{home_team.identity.name}:{away_team.identity.name}:{game_number}"
    )
    return random.Random(seed)


def simulate_game(league, home_team, away_team, game_number):
    rng = game_rng(league, home_team, away_team, game_number)

    home_strength = total_team_strength(home_team, home=True)
    away_strength = total_team_strength(away_team, home=False)

    # Referee variance. High-accuracy refs reduce chaos.
    referee = rng.choice(league.referee_pool) if league.referee_pool else None

    if referee and referee.accuracy:
        chaos = max(3, 18 - (referee.accuracy / 8))
    else:
        chaos = 8

    home_roll = home_strength + rng.gauss(0, chaos)
    away_roll = away_strength + rng.gauss(0, chaos)

    if home_roll >= away_roll:
        home_team.wins += 1
        away_team.losses += 1
        winner = home_team
        loser = away_team
    else:
        away_team.wins += 1
        home_team.losses += 1
        winner = away_team
        loser = home_team

    record_regular_season_game_performances(
        league=league,
        winning_team=winner,
        losing_team=loser,
        game_number=game_number,
    )

    margin = abs(home_roll - away_roll)

    return {
        "home": home_team.identity.name,
        "away": away_team.identity.name,
        "winner": winner.identity.name,
        "loser": loser.identity.name,
        "margin_signal": round(margin, 2),
        "referee": referee.name if referee else None,
    }


def run_regular_season(league):
    reset_team_records(league)
    reset_regular_season_player_stats(league)

    teams = list(league.teams.values())
    game_number = 1

    if league.current_year == 1:
        league.history.append(f"Year {league.current_year}: The first NBF regular season began.")
    else:
        league.history.append(f"Year {league.current_year}: The NBF regular season began.")

    for i in range(len(teams)):
        for j in range(i + 1, len(teams)):
            team_a = teams[i]
            team_b = teams[j]

            for matchup_game in range(REGULAR_SEASON_SERIES_PER_MATCHUP):
                if matchup_game % 2 == 0:
                    home_team = team_a
                    away_team = team_b
                else:
                    home_team = team_b
                    away_team = team_a

                simulate_game(league, home_team, away_team, game_number)
                game_number += 1

    league.history.append(f"Year {league.current_year}: The regular season concluded.")


def validate_regular_season(league):
    errors = []

    total_wins = sum(team.wins for team in league.teams.values())
    total_losses = sum(team.losses for team in league.teams.values())

    if total_wins != total_losses:
        errors.append(f"Wins/losses mismatch: {total_wins} wins vs {total_losses} losses.")

    for team in league.teams.values():
        games_played = team.wins + team.losses

        if games_played != EXPECTED_REGULAR_SEASON_GAMES:
            errors.append(
                f"{team.identity.name} expected {EXPECTED_REGULAR_SEASON_GAMES} games, found {games_played}."
            )

    expected_total_games = (len(league.teams) * EXPECTED_REGULAR_SEASON_GAMES) // 2

    if total_wins != expected_total_games:
        errors.append(f"Expected {expected_total_games} league games, found {total_wins}.")

    if errors:
        print("REGULAR SEASON VALIDATION: FAILED")
        for error in errors:
            print(f"- {error}")
        raise SystemExit(1)

    print("REGULAR SEASON VALIDATION: PASS")


def winning_percentage(team):
    games = team.wins + team.losses
    if games == 0:
        return 0
    return team.wins / games


def standings_sort_key(team):
    return (
        team.wins,
        winning_percentage(team),
        team_roster_strength(team),
    )


def print_regular_season_summary(league):
    print("\n============================================")
    print("YEAR 1 REGULAR SEASON SUMMARY")
    print("============================================")

    standings = sorted(
        league.teams.values(),
        key=standings_sort_key,
        reverse=True
    )

    print("\nOverall Standings:")
    for rank, team in enumerate(standings, start=1):
        pct = winning_percentage(team)
        print(
            f"{rank}. {team.identity.name} | {team.wins}-{team.losses} | "
            f"PCT {pct:.3f} | Strength {team_roster_strength(team):.1f}"
        )

    print("\nEastern Conference:")
    east = [team for team in standings if team.identity.conference == "Eastern"]
    for rank, team in enumerate(east, start=1):
        print(f"{rank}. {team.identity.name} | {team.wins}-{team.losses}")

    print("\nWestern Conference:")
    west = [team for team in standings if team.identity.conference == "Western"]
    for rank, team in enumerate(west, start=1):
        print(f"{rank}. {team.identity.name} | {team.wins}-{team.losses}")

    best_team = standings[0]
    worst_team = standings[-1]

    league.history.append(
        f"Year {league.current_year}: {best_team.identity.name} finished with the league's best record at {best_team.wins}-{best_team.losses}."
    )

    league.history.append(
        f"Year {league.current_year}: {worst_team.identity.name} finished with the league's worst record at {worst_team.wins}-{worst_team.losses}."
    )

    print("============================================\n")



# ============================================================
# PLAYOFF SIMULATION + KANOMI JONES PLAYOFF MVP
# ============================================================

def qualify_playoff_teams(league):
    eastern = [
        team for team in league.teams.values()
        if team.identity.conference == "Eastern"
    ]

    western = [
        team for team in league.teams.values()
        if team.identity.conference == "Western"
    ]

    eastern_top_4 = sorted(eastern, key=standings_sort_key, reverse=True)[:4]
    western_top_4 = sorted(western, key=standings_sort_key, reverse=True)[:4]

    qualifiers = eastern_top_4 + western_top_4

    seeds = sorted(
        qualifiers,
        key=standings_sort_key,
        reverse=True
    )

    return seeds


def reset_playoff_player_stats(league):
    for player in league.player_pool:
        player.playoff_games = 0
        player.playoff_points = 0
        player.playoff_rebounds = 0
        player.playoff_assists = 0
        player.playoff_impact = 0.0
        player.playoff_finals_games = 0


def playoff_game_rng(league, home_team, away_team, round_name, game_number):
    seed = (
        f"NBF-LBU-v1:playoffs:{league.current_year}:"
        f"{round_name}:{home_team.identity.name}:{away_team.identity.name}:G{game_number}"
    )
    return random.Random(seed)


def playoff_player_game_rng(league, player, round_name, game_number):
    seed = (
        f"NBF-LBU-v1:playoff-player:{league.current_year}:"
        f"{round_name}:G{game_number}:{player.player_id}:{player.name}"
    )
    return random.Random(seed)


def record_playoff_game_performances(league, winning_team, losing_team, round_name, game_number):
    is_finals = round_name == "NBF Finals"

    for team, won_game in [(winning_team, True), (losing_team, False)]:
        rotation = top_rotation(team, size=8)

        for rotation_index, player in enumerate(rotation):
            rng = playoff_player_game_rng(league, player, round_name, game_number)

            role_multiplier = max(0.45, 1.15 - (rotation_index * 0.09))

            star_multiplier = {
                "Generational": 1.35,
                "Superstar": 1.22,
                "Star": 1.08,
                "Starter": 0.92,
                "Role": 0.75,
                "Fringe": 0.55,
            }.get(player.tier, 0.75)

            points = max(
                0,
                int(
                    ((player.offense + player.shooting + player.confidence) / 15)
                    * role_multiplier
                    * star_multiplier
                    + rng.gauss(0, 3)
                )
            )

            rebounds = max(
                0,
                int(
                    ((player.rebounding + player.athleticism) / 22)
                    * role_multiplier
                    * star_multiplier
                    + rng.gauss(0, 2)
                )
            )

            assists = max(
                0,
                int(
                    ((player.playmaking + player.basketball_iq) / 24)
                    * role_multiplier
                    * star_multiplier
                    + rng.gauss(0, 2)
                )
            )

            impact = (
                points * 0.55
                + rebounds * 0.35
                + assists * 0.40
                + player.defense * 0.08
                + player.basketball_iq * 0.05
                + player.leadership * 0.04
            )

            if won_game:
                impact += 6

            if is_finals:
                impact += 4

            player.playoff_games += 1
            player.playoff_points += points
            player.playoff_rebounds += rebounds
            player.playoff_assists += assists
            player.playoff_impact += impact

            if is_finals:
                player.playoff_finals_games += 1


def simulate_playoff_game(league, home_team, away_team, round_name, game_number):
    rng = playoff_game_rng(league, home_team, away_team, round_name, game_number)

    home_strength = total_team_strength(home_team, home=True)
    away_strength = total_team_strength(away_team, home=False)

    home_rotation = top_rotation(home_team)
    away_rotation = top_rotation(away_team)

    home_pressure_bonus = 0
    away_pressure_bonus = 0

    if home_rotation:
        home_pressure_bonus += sum(
            player.basketball_iq + player.leadership
            for player in home_rotation[:5]
        ) / 100

    if away_rotation:
        away_pressure_bonus += sum(
            player.basketball_iq + player.leadership
            for player in away_rotation[:5]
        ) / 100

    if home_team.coach:
        home_pressure_bonus += home_team.coach.discipline / 35
        home_pressure_bonus += home_team.coach.adaptability / 40

    if away_team.coach:
        away_pressure_bonus += away_team.coach.discipline / 35
        away_pressure_bonus += away_team.coach.adaptability / 40

    referee = rng.choice(league.referee_pool) if league.referee_pool else None

    if referee and referee.accuracy:
        chaos = max(2.5, 14 - (referee.accuracy / 9))
    else:
        chaos = 6

    home_roll = home_strength + home_pressure_bonus + rng.gauss(0, chaos)
    away_roll = away_strength + away_pressure_bonus + rng.gauss(0, chaos)

    if home_roll >= away_roll:
        winner = home_team
        loser = away_team
    else:
        winner = away_team
        loser = home_team

    record_playoff_game_performances(
        league=league,
        winning_team=winner,
        losing_team=loser,
        round_name=round_name,
        game_number=game_number,
    )

    return winner


def home_court_team(team_a, team_b):
    if team_a.wins > team_b.wins:
        return team_a

    if team_b.wins > team_a.wins:
        return team_b

    if team_roster_strength(team_a) >= team_roster_strength(team_b):
        return team_a

    return team_b


def simulate_best_of_7_series(league, team_a, team_b, round_name):
    home_court = home_court_team(team_a, team_b)
    road_team = team_b if home_court == team_a else team_a

    wins = {
        team_a.identity.name: 0,
        team_b.identity.name: 0,
    }

    home_pattern = [
        home_court,
        home_court,
        road_team,
        road_team,
        home_court,
        road_team,
        home_court,
    ]

    game_logs = []

    for game_index in range(7):
        game_number = game_index + 1
        home_team = home_pattern[game_index]
        away_team = team_b if home_team == team_a else team_a

        winner = simulate_playoff_game(
            league=league,
            home_team=home_team,
            away_team=away_team,
            round_name=round_name,
            game_number=game_number,
        )

        loser = away_team if winner == home_team else home_team

        wins[winner.identity.name] += 1

        game_logs.append(
            f"G{game_number}: {winner.identity.name} def. {loser.identity.name}"
        )

        if wins[winner.identity.name] == 4:
            series_result = {
                "round": round_name,
                "winner": winner,
                "loser": loser,
                "winner_wins": wins[winner.identity.name],
                "loser_wins": wins[loser.identity.name],
                "games": game_number,
                "logs": game_logs,
            }

            league.playoff_results.append(
                f"{round_name}: {winner.identity.name} defeated "
                f"{loser.identity.name} in {game_number} games."
            )

            return series_result

    raise RuntimeError("Best-of-7 series ended without a winner.")


def kanomi_jones_mvp_score(player, champion_name):
    if player.playoff_games == 0:
        return -9999

    score = player.playoff_impact

    # Usually a Finals player.
    score += player.playoff_finals_games * 8

    # Usually from winning team, but not a hard rule.
    if player.team == champion_name:
        score += 18

    # Reward sustained playoff production.
    score += player.playoff_points * 0.10
    score += player.playoff_rebounds * 0.08
    score += player.playoff_assists * 0.08

    # Narrative lift for elite players without forcing the choice.
    if player.tier == "Generational":
        score += 8
    elif player.tier == "Superstar":
        score += 5
    elif player.tier == "Star":
        score += 2

    return score


def select_kanomi_jones_playoff_mvp(league, champion_name):
    candidates = [
        player for player in league.player_pool
        if player.playoff_games > 0
    ]

    if not candidates:
        raise RuntimeError("Cannot select Kanomi Jones Playoff MVP without playoff participants.")

    winner = max(
        candidates,
        key=lambda player: kanomi_jones_mvp_score(player, champion_name)
    )

    winner.playoff_mvp_awards += 1

    league.playoff_mvp_player_id = winner.player_id
    league.playoff_mvp_name = winner.name
    league.playoff_mvp_team = winner.team

    league.history.append(
        f"Year {league.current_year}: {winner.name} of the {winner.team} won the "
        f"{league.playoff_mvp_award_name}."
    )

    league.playoff_results.append(
        f"{league.playoff_mvp_award_name}: {winner.name}, {winner.team} "
        f"({winner.playoff_points} PTS, {winner.playoff_rebounds} REB, "
        f"{winner.playoff_assists} AST in playoffs)."
    )

    return winner


def run_playoffs(league):
    reset_playoff_player_stats(league)
    league.playoff_results = []
    league.current_champion = None
    league.playoff_mvp_player_id = None
    league.playoff_mvp_name = None
    league.playoff_mvp_team = None

    seeds = qualify_playoff_teams(league)

    if len(seeds) != 8:
        raise RuntimeError(f"Expected 8 playoff teams, found {len(seeds)}.")

    league.history.append(f"Year {league.current_year}: The first NBF Playoffs began.")

    league.playoff_results.append("PLAYOFF SEEDS")

    for idx, team in enumerate(seeds, start=1):
        league.playoff_results.append(
            f"{idx}. {team.identity.name} ({team.wins}-{team.losses})"
        )

    round_1_matchups = [
        (seeds[0], seeds[7]),
        (seeds[1], seeds[6]),
        (seeds[2], seeds[5]),
        (seeds[3], seeds[4]),
    ]

    round_1_winners = []

    for team_a, team_b in round_1_matchups:
        result = simulate_best_of_7_series(
            league,
            team_a,
            team_b,
            "Round 1"
        )
        round_1_winners.append(result["winner"])

    semifinal_matchups = [
        (round_1_winners[0], round_1_winners[3]),
        (round_1_winners[1], round_1_winners[2]),
    ]

    semifinal_winners = []

    for team_a, team_b in semifinal_matchups:
        result = simulate_best_of_7_series(
            league,
            team_a,
            team_b,
            "Semifinals"
        )
        semifinal_winners.append(result["winner"])

    finals_result = simulate_best_of_7_series(
        league,
        semifinal_winners[0],
        semifinal_winners[1],
        "NBF Finals"
    )

    champion = finals_result["winner"]
    champion.championships += 1
    league.current_champion = champion.identity.name

    select_kanomi_jones_playoff_mvp(league, champion.identity.name)

    league.history.append(
        f"Year {league.current_year}: {champion.identity.name} won the "
        f"{league.championship_trophy}."
    )

    league.playoff_results.append(
        f"CHAMPION: {champion.identity.name} won the {league.championship_trophy}."
    )

    return champion



def validate_playoffs(league):
    """
    Multi-year compatible playoff validator.

    In Year 1, exactly one team has a championship.
    In later Genesis years, multiple teams may have championships.
    Therefore, this validates the current season champion only.
    """

    errors = []

    if not league.current_champion:
        errors.append("No current champion set after playoffs.")

    if league.current_champion:
        champion_team = league.teams.get(league.current_champion)

        if champion_team is None:
            errors.append(f"Champion {league.current_champion} not found in league teams.")
        elif champion_team.championships <= 0:
            errors.append(f"Champion {league.current_champion} has no recorded championships.")

    if not league.playoff_results:
        errors.append("Playoff results log is empty.")

    if not any("CHAMPION:" in line for line in league.playoff_results):
        errors.append("Current playoff results missing CHAMPION line.")

    if not league.playoff_mvp_name:
        errors.append("Kanomi Jones Playoff MVP was not selected.")

    if league.playoff_mvp_player_id is None:
        errors.append("Kanomi Jones Playoff MVP player ID missing.")

    if errors:
        print("PLAYOFF VALIDATION: FAILED")
        for error in errors:
            print(f"- {error}")
        raise SystemExit(1)

    print("PLAYOFF VALIDATION: PASS")


def print_playoff_summary(league):
    print("\n============================================")
    print("YEAR 1 PLAYOFF SUMMARY")
    print("============================================")

    for line in league.playoff_results:
        print(f"- {line}")

    print(f"\nChampion: {league.current_champion}")
    print(f"Trophy: {league.championship_trophy}")
    print(f"Kanomi Jones Playoff MVP: {league.playoff_mvp_name} ({league.playoff_mvp_team})")
    print("============================================\n")



# ============================================================
# AWARDS SYSTEM
# ============================================================

def team_win_bonus_for_player(player, league):
    if not player.team or player.team not in league.teams:
        return 0

    team = league.teams[player.team]
    return team.wins * 0.75




def select_mvp(league):
    candidates = [
        player for player in league.player_pool
        if player.team is not None and player.season_games > 0
    ]

    winner = max(
        candidates,
        key=lambda player: (
            player.season_impact
            + team_win_bonus_for_player(player, league)
            + player.popularity * 0.18
            + player.leadership * 0.15
        )
    )

    winner.mvp_awards += 1

    league.award_results.append(
        f"{league.season_mvp_award_name}: {winner.name}, {winner.team} "
        f"({player_points_per_game(winner):.1f} PPG, "
        f"{player_rebounds_per_game(winner):.1f} RPG, "
        f"{player_assists_per_game(winner):.1f} APG)"
    )

    return winner


def select_rookie_of_year(league):
    candidates = [
        player for player in league.player_pool
        if player.team is not None
        and player.season_games > 0
        and player.draft_year == league.current_year
        and player.age <= 23
    ]

    if not candidates:
        candidates = [
            player for player in league.player_pool
            if player.team is not None
            and player.season_games > 0
            and player.draft_year == league.current_year
        ]

    # Multi-year guardrail:
    # Until annual rookie drafts are implemented, some years may have no rookie class.
    if not candidates:
        league.award_results.append(
            f"Rookie of the Year: Not awarded in Year {league.current_year} "
            f"(no rookie class available)."
        )
        return None

    winner = max(
        candidates,
        key=lambda player: (
            player.season_impact
            + player.potential * 2
            + player.prime_window_score * 20
        )
    )

    winner.rookie_of_year_awards += 1

    league.award_results.append(
        f"Rookie of the Year: {winner.name}, {winner.team} "
        f"(Age {winner.age}, {winner.tier}, OVR {winner.overall}, POT {winner.potential})"
    )

    return winner


def select_defensive_player_of_year(league):
    candidates = [
        player for player in league.player_pool
        if player.team is not None and player.season_games > 0
    ]

    winner = max(
        candidates,
        key=lambda player: (
            player.defense * 4
            + player.rebounding * 1.35
            + player.basketball_iq * 0.9
            + player.durability * 0.5
            + team_win_bonus_for_player(player, league)
        )
    )

    winner.defensive_player_awards += 1

    league.award_results.append(
        f"Defensive Player of the Year: {winner.name}, {winner.team} "
        f"(DEF {winner.defense}, REB {winner.rebounding}, IQ {winner.basketball_iq})"
    )

    return winner


def select_sixth_man(league):
    candidates = []

    for team in league.teams.values():
        rotation = top_rotation(team, size=8)
        starters = set(player.player_id for player in top_rotation(team, size=5))

        for player in rotation:
            if player.player_id not in starters and player.season_games > 0:
                candidates.append(player)

    if not candidates:
        candidates = [
            player for player in league.player_pool
            if player.team is not None and player.season_games > 0
        ]

    winner = max(
        candidates,
        key=lambda player: (
            player.season_impact
            + player.offense * 1.1
            + player.confidence * 0.8
        )
    )

    winner.sixth_man_awards += 1

    league.award_results.append(
        f"Sixth Man of the Year: {winner.name}, {winner.team} "
        f"({player_points_per_game(winner):.1f} PPG)"
    )

    return winner


def select_most_improved(league):
    candidates = [
        player for player in league.player_pool
        if player.team is not None and player.season_games > 0
    ]

    winner = max(
        candidates,
        key=lambda player: (
            (player.potential - player.overall) * 8
            + player.season_impact * 0.35
            + player.age * -0.5
            + player.confidence
        )
    )

    winner.most_improved_awards += 1

    league.award_results.append(
        f"Most Improved Player: {winner.name}, {winner.team} "
        f"(OVR {winner.overall}, POT {winner.potential})"
    )

    return winner


def select_coach_of_year(league):
    winner = max(
        league.teams.values(),
        key=lambda team: (
            team.wins * 3
            + (team.coach.leadership if team.coach else 0)
            + (team.coach.adaptability if team.coach else 0)
            + (team.coach.discipline if team.coach else 0)
            - team_roster_strength(team) * 0.35
        )
    )

    league.award_results.append(
        f"Coach of the Year: {winner.coach.name}, {winner.identity.name} "
        f"({winner.wins}-{winner.losses})"
    )

    return winner.coach


def select_executive_of_year(league):
    winner = max(
        league.teams.values(),
        key=lambda team: (
            team.wins * 2.5
            + (team.gm.scouting if team.gm else 0)
            + (team.gm.development if team.gm else 0)
            + (team.gm.leadership if team.gm else 0)
            + sum(player.value_score for player in top_rotation(team, size=8)) * 0.08
        )
    )

    league.award_results.append(
        f"Executive of the Year: {winner.gm.name}, {winner.identity.name} "
        f"({winner.wins}-{winner.losses})"
    )

    return winner.gm


def select_owner_of_year(league):
    winner = max(
        league.teams.values(),
        key=lambda team: (
            team.wins * 2.2
            + team.owner.winning_desire
            + team.owner.patience * 0.65
            + team.owner.pr_awareness * 0.45
            - team.owner.greed * 0.25
        )
    )

    league.award_results.append(
        f"Owner of the Year: {winner.owner.name}, {winner.identity.name} "
        f"({winner.wins}-{winner.losses})"
    )

    return winner.owner


def reporter_score(reporter, league):
    team = league.teams.get(reporter.team)

    team_bonus = team.wins * 1.5 if team else 0
    integrity = reporter.integrity if reporter.integrity is not None else 70
    sources = reporter.sources if reporter.sources is not None else 70
    aggression = reporter.aggression if reporter.aggression is not None else 60
    popularity = reporter.popularity if reporter.popularity is not None else 60

    return (
        integrity * 1.1
        + sources * 1.15
        + aggression * 0.55
        + popularity * 0.45
        + team_bonus
    )


def select_reporter_of_year(league):
    winner = max(
        league.team_reporters,
        key=lambda reporter: reporter_score(reporter, league)
    )

    league.award_results.append(
        f"Reporter of the Year: {winner.name}, {winner.team} "
        f"({winner.reporter_type})"
    )

    return winner


def run_year_end_awards(league):
    league.award_results = []

    league.history.append(f"Year {league.current_year}: The NBF Awards Committee voted on annual awards.")

    select_mvp(league)
    select_rookie_of_year(league)
    select_defensive_player_of_year(league)
    select_sixth_man(league)
    select_most_improved(league)
    select_coach_of_year(league)
    select_executive_of_year(league)
    select_owner_of_year(league)
    select_reporter_of_year(league)

    for result in league.award_results:
        league.history.append(f"Year {league.current_year}: {result}")




def validate_year_end_awards(league):
    errors = []

    required_awards = [
        "Rookie of the Year:",
        "Defensive Player of the Year:",
        "Sixth Man of the Year:",
        "Most Improved Player:",
        "Coach of the Year:",
        "Executive of the Year:",
        "Owner of the Year:",
        "Reporter of the Year:",
    ]

    mvp_found = any(
        result.startswith("MVP:")
        or result.startswith(league.season_mvp_award_name + ":")
        or "Season MVP" in result
        for result in league.award_results
    )

    if not mvp_found:
        errors.append("Missing award result: MVP / Season MVP")

    for award_label in required_awards:
        if not any(result.startswith(award_label) for result in league.award_results):
            errors.append(f"Missing award result: {award_label}")

    if errors:
        print("YEAR END AWARDS VALIDATION: FAILED")
        for error in errors:
            print(f"- {error}")
        raise SystemExit(1)

    print("YEAR END AWARDS VALIDATION: PASS")


def print_year_end_awards_summary(league):
    print("\n============================================")
    print("YEAR 1 AWARDS SUMMARY")
    print("============================================")

    for result in league.award_results:
        print(f"- {result}")

    print("============================================\n")



# ============================================================
# YEAR-END TRANSITION: RETIREMENTS, AGING, MEMORY
# ============================================================

def year_end_rng(league, label):
    return random.Random(f"NBF-LBU-v1:year-end:{league.current_year}:{label}")



def player_retirement_probability(player):
    """
    Normal basketball retirement probability.

    Guardrails:
    - No normal retirement under age 30.
    - Young retirements should only happen later through special event systems
      like injury, scandal, personal leave, or crisis.
    """

    if player.age < 30:
        return 0.0

    probability = 0.0

    # Age pressure.
    if player.age <= 32:
        probability += 0.005
    elif player.age <= 34:
        probability += 0.02
    elif player.age <= 36:
        probability += 0.07
    elif player.age <= 38:
        probability += 0.16
    else:
        probability += 0.32

    # Injury / durability pressure.
    probability += player.injury_risk / 400

    if player.durability <= 55:
        probability += 0.04

    # Low role players retire earlier, but not too aggressively.
    if player.tier == "Fringe":
        probability += 0.06
    elif player.tier == "Role":
        probability += 0.025

    # Great players usually hold on longer.
    if player.tier == "Generational":
        probability -= 0.12
    elif player.tier == "Superstar":
        probability -= 0.07
    elif player.tier == "Star":
        probability -= 0.035

    # Championships can motivate one more run.
    if player.championships > 0:
        probability -= 0.025

    # Older ringless veterans may decide to walk away.
    if player.age >= 35 and player.championships == 0:
        probability += 0.025

    return max(0.0, min(0.65, probability))



def should_player_retire(league, player):
    if player.retired:
        return False

    # Final guardrail:
    # Players under 30 cannot retire through normal retirement logic.
    if player.age < 30:
        return False

    # Zero-stat players below 34 should remain available/developing.
    # This prevents unrealistic immediate retirements for deep bench players.
    if has_zero_career_stats(player) and player.age < 34:
        return False

    # Zero-stat players age 34-35 only retire if they are fringe/role players.
    if has_zero_career_stats(player) and player.age < 36:
        if player.tier not in ["Fringe", "Role"]:
            return False

    rng = year_end_rng(league, f"retire:{player.player_id}:{player.name}")
    probability = player_retirement_probability(player)

    # Zero-stat depth players have reduced retirement odds unless clearly old.
    if has_zero_career_stats(player):
        if player.age >= 36:
            probability *= 0.65
        else:
            probability *= 0.35

    return rng.random() < probability


def has_zero_career_stats(player):
    return (
        player.career_points == 0
        and player.career_rebounds == 0
        and player.career_assists == 0
    )


def retirement_reason(player):
    if has_zero_career_stats(player):
        if player.age >= 36:
            return "veteran depth player left professional basketball"
        if player.age >= 34:
            return "lost active roster traction before establishing a role"

    if player.age >= 37 and player.tier in ["Fringe", "Role"]:
        return "veteran roster attrition"

    if player.age >= 36 and player.durability <= 60:
        return "declining durability"

    if player.age >= 35 and player.championships > 0:
        return "left after a completed championship chase"

    if player.age >= 35 and player.championships == 0:
        return "stepped away after a long title chase"

    if player.age >= 33 and player.tier == "Fringe":
        return "lost active roster traction"

    return "standard veteran retirement"



def run_player_retirements(league):
    retired_this_year = []

    for player in league.player_pool:
        if player.retired:
            continue

        # Keep untouched free agents in the ecosystem for future free agency,
        # injuries, roster churn, and expansion depth.
        if player.team is None:
            continue

        if should_player_retire(league, player):
            player.retired = True
            retired_this_year.append(player)

    for team in league.teams.values():
        team.roster = [player for player in team.roster if not player.retired]

    for player in retired_this_year:
        reason = retirement_reason(player)

        line = (
            f"Year {league.current_year}: {player.name} retired at age {player.age} "
            f"after {player.years_pro + 1} NBF season(s) due to {reason}. "
            f"Career: {player.career_points} PTS, {player.career_rebounds} REB, "
            f"{player.career_assists} AST."
        )

        league.retired_players_log.append(line)
        league.history.append(line)

    return retired_this_year


def age_players_one_year(league):
    for player in league.player_pool:
        if not player.retired:
            player.age += 1
            player.years_pro += 1

            # Minor post-season development/regression.
            rng = year_end_rng(league, f"development:{player.player_id}:{player.name}")

            if player.age <= 24:
                growth_chance = 0.45 + ((player.potential - player.overall) / 120)
                if rng.random() < growth_chance and player.overall < player.potential:
                    player.overall = min(player.potential, player.overall + 1)

            elif player.age >= 33:
                decline_chance = 0.20 + ((player.age - 33) * 0.06)
                if rng.random() < decline_chance:
                    player.overall = max(35, player.overall - 1)


def age_staff_and_institutions_one_year(league):
    for gm in league.gm_pool:
        gm.age += 1

    for coach in league.coach_pool:
        coach.age += 1

    for team in league.teams.values():
        team.owner.age += 1

    for referee in league.referee_pool:
        if not referee.retired:
            # Referees age, but referee retirement comes later in Genesis expansion.
            pass

    for member in league.hall_of_fame_committee:
        if member.age is not None:
            member.age += 1




def get_award_result(league, label):
    for result in league.award_results:
        if result.startswith(label):
            return result

    # Compatibility:
    # After Genesis, regular season MVP may be renamed after the best player
    # of the first 50 years, e.g. "Nolan Ward Season MVP Award:".
    if label == "MVP:":
        for result in league.award_results:
            if "Season MVP" in result or result.startswith(league.season_mvp_award_name + ":"):
                return result

    return None


def build_year_end_summary(league):
    standings = sorted(
        league.teams.values(),
        key=standings_sort_key,
        reverse=True
    )

    best_team = standings[0]
    worst_team = standings[-1]

    mvp = get_award_result(league, "MVP:")
    roy = get_award_result(league, "Rookie of the Year:")
    dpoy = get_award_result(league, "Defensive Player of the Year:")

    summary_parts = [
        f"Year {league.current_year} Summary:",
        f"Champion: {league.current_champion}",
        f"Trophy: {league.championship_trophy}",
        f"Kanomi Jones Playoff MVP: {league.playoff_mvp_name}, {league.playoff_mvp_team}",
        f"Best Record: {best_team.identity.name} ({best_team.wins}-{best_team.losses})",
        f"Worst Record: {worst_team.identity.name} ({worst_team.wins}-{worst_team.losses})",
    ]

    if mvp:
        summary_parts.append(mvp)

    if roy:
        summary_parts.append(roy)

    if dpoy:
        summary_parts.append(dpoy)

    # Keep the first segment clean: "Year 1 Summary: Champion..."
    if len(summary_parts) > 1:
        summary = summary_parts[0] + " " + " | ".join(summary_parts[1:])
    else:
        summary = summary_parts[0]

    league.season_summaries.append(summary)
    league.history.append(summary)

    return summary


def run_year_end_transition(league):
    build_year_end_summary(league)

    retired_this_year = run_player_retirements(league)

    league.history.append(
        f"Year {league.current_year}: {len(retired_this_year)} player(s) retired after the season."
    )

    age_players_one_year(league)
    age_staff_and_institutions_one_year(league)

    previous_year = league.current_year
    league.current_year += 1

    league.history.append(
        f"League calendar advanced from Year {previous_year} to Year {league.current_year}."
    )


def validate_year_end_transition(league):
    errors = []

    if league.current_year != 2:
        errors.append(f"Expected league current_year to be 2 after Year 1 transition, found {league.current_year}.")

    if not league.season_summaries:
        errors.append("No season summaries recorded.")

    if not any("Year 1 Summary:" in summary for summary in league.season_summaries):
        errors.append("Year 1 summary missing from season summaries.")

    for team in league.teams.values():
        for player in team.roster:
            if player.retired:
                errors.append(f"Retired player {player.name} still on active roster for {team.identity.name}.")

    active_players = [player for player in league.player_pool if player.team is not None and not player.retired]

    if not active_players:
        errors.append("No active players remain after retirements.")

    if errors:
        print("YEAR-END TRANSITION VALIDATION: FAILED")
        for error in errors:
            print(f"- {error}")
        raise SystemExit(1)

    print("YEAR-END TRANSITION VALIDATION: PASS")


def print_year_end_memory_summary(league):
    print("\n============================================")
    print("YEAR 1 HISTORICAL MEMORY / YEAR-END TRANSITION")
    print("============================================")

    print("\nSeason Summary:")
    print(f"- {league.season_summaries[-1] if league.season_summaries else 'None'}")

    print("\nRetirements:")
    if league.retired_players_log:
        for line in league.retired_players_log[-20:]:
            print(f"- {line}")
    else:
        print("- No player retirements recorded.")

    print(f"\nLeague Calendar: Year {league.current_year}")
    print("Status: Year 2 ready for offseason systems.")
    print("============================================\n")



# ============================================================
# YEAR 2 OFFSEASON ENGINE
# ============================================================

MIN_ACTIVE_ROSTER_SIZE = INITIAL_DRAFT_ROUNDS



def available_free_agents(league):
    return [
        player for player in league.player_pool
        if player.team is None
        and not player.retired
        and getattr(player, "draft_rights_team", None) is None
    ]


def team_position_counts(team):
    counts = {
        "PG": 0,
        "SG": 0,
        "SF": 0,
        "PF": 0,
        "C": 0,
    }

    for player in team.roster:
        counts[player.position] = counts.get(player.position, 0) + 1

    return counts


def free_agent_position_need_score(team, player):
    counts = team_position_counts(team)
    current_count = counts.get(player.position, 0)

    if current_count == 0:
        return 22
    if current_count == 1:
        return 12
    if current_count == 2:
        return 5
    if current_count == 3:
        return 1

    return -6


def score_free_agent_for_team(player, team):
    score = player.value_score

    # Roster need.
    score += free_agent_position_need_score(team, player)

    # GM influence.
    if team.gm:
        score += team.gm.scouting * 0.08
        score += team.gm.development * 0.04
        score += team.gm.leadership * 0.03

        if "Star" in team.gm.personality or "Hunter" in team.gm.personality:
            if player.tier in ["Generational", "Superstar", "Star"]:
                score += 8

        if "Draft" in team.gm.personality or "Development" in team.gm.personality:
            if player.age <= 24:
                score += 6

        if "Veteran" in team.gm.personality or "Win-Now" in team.gm.personality:
            if player.age >= 30 and player.overall >= 72:
                score += 5

    # Coach style influence.
    if team.coach:
        if team.coach.offense >= team.coach.defense:
            score += player.offense * 0.06
            score += player.shooting * 0.04
            score += player.playmaking * 0.03
        else:
            score += player.defense * 0.06
            score += player.rebounding * 0.04

        if "Development" in team.coach.personality and player.age <= 24:
            score += 5

    # Market influence.
    if team.market_profile:
        score += team.market_profile.free_agent_appeal * 0.05
        score += team.market_profile.media_pressure * 0.01

    # Owner pressure.
    score += team.owner.winning_desire * 0.03
    score -= team.owner.greed * 0.015

    return score


def sign_free_agent_to_team(league, team, player):
    player.team = team.identity.name
    team.roster.append(player)

    line = (
        f"Year {league.current_year} Offseason: {team.identity.name} signed "
        f"{player.name}, {player.position}, {player.tier}, OVR {player.overall}."
    )

    league.offseason_log.append(line)
    league.history.append(line)



def repair_team_roster_from_free_agency(league, team):
    while len(team.roster) < MIN_ACTIVE_ROSTER_SIZE:
        candidates = available_free_agents(league)

        if not candidates:
            ensure_free_agent_depth(league)
            candidates = available_free_agents(league)

        if not candidates:
            raise RuntimeError("Free agent pool exhausted during roster repair even after replenishment.")

        selected = max(
            candidates,
            key=lambda player: score_free_agent_for_team(player, team)
        )

        sign_free_agent_to_team(league, team, selected)


def run_year_2_offseason(league):
    if league.current_year != 2:
        raise RuntimeError(
            f"Year 2 offseason expected league.current_year == 2, found {league.current_year}."
        )

    league.offseason_log.append(f"Year {league.current_year} Offseason: Free agency opened.")
    league.history.append(f"Year {league.current_year} Offseason: Free agency opened.")

    teams_needing_repairs = [
        team for team in league.teams.values()
        if len(team.roster) < MIN_ACTIVE_ROSTER_SIZE
    ]

    if not teams_needing_repairs:
        line = (
            f"Year {league.current_year} Offseason: No roster repair signings were required. "
            f"All teams retained at least {MIN_ACTIVE_ROSTER_SIZE} active players."
        )
        league.offseason_log.append(line)
        league.history.append(line)
        return

    for team in teams_needing_repairs:
        repair_team_roster_from_free_agency(league, team)

    league.history.append(f"Year {league.current_year} Offseason: Roster repair phase completed.")


def validate_year_2_offseason(league):
    errors = []

    if league.current_year != 2:
        errors.append(f"Expected league year 2 during offseason validation, found {league.current_year}.")

    if not league.offseason_log:
        errors.append("Offseason log is empty.")

    for team in league.teams.values():
        if len(team.roster) < MIN_ACTIVE_ROSTER_SIZE:
            errors.append(
                f"{team.identity.name} has {len(team.roster)} players; expected at least {MIN_ACTIVE_ROSTER_SIZE}."
            )

        player_ids = [player.player_id for player in team.roster]

        if len(player_ids) != len(set(player_ids)):
            errors.append(f"Duplicate player on {team.identity.name} roster.")

        for player in team.roster:
            if player.retired:
                errors.append(f"Retired player {player.name} is still on {team.identity.name}.")
            if player.team != team.identity.name:
                errors.append(
                    f"Roster/team mismatch: {player.name} has team={player.team}, expected {team.identity.name}."
                )

    if errors:
        print("YEAR 2 OFFSEASON VALIDATION: FAILED")
        for error in errors:
            print(f"- {error}")
        raise SystemExit(1)

    print("YEAR 2 OFFSEASON VALIDATION: PASS")


def print_year_2_offseason_summary(league):
    print("\n============================================")
    print("YEAR 2 OFFSEASON SUMMARY")
    print("============================================")

    for line in league.offseason_log:
        print(f"- {line}")

    print("\nRoster Counts:")
    for team in league.teams.values():
        print(f"- {team.identity.name}: {len(team.roster)} players")

    print(f"\nAvailable Free Agents: {len(available_free_agents(league))}")
    print("Status: Year 2 offseason roster repair complete.")
    print("============================================\n")



# ============================================================
# GENERALIZED SEASON ENGINE
# ============================================================


def run_competitive_season(league, print_outputs=True):
    """
    Runs one full competitive NBF season for the league's current year.

    Correct order:
    - Regular season
    - Player stats
    - Regular season awards
    - Playoffs
    - Kanomi Jones Playoff MVP
    - Historical memory
    - Retirements / aging / calendar advancement
    """

    starting_year = league.current_year

    # 1. Regular Season
    run_regular_season(league)
    validate_regular_season(league)
    validate_regular_season_player_stats(league)

    if print_outputs:
        print_regular_season_summary(league)
        print_regular_season_player_summary(league)

    # 2. Regular Season Awards
    run_year_end_awards(league)
    validate_year_end_awards(league)

    if print_outputs:
        print_year_end_awards_summary(league)

    # 3. Playoffs + Kanomi Jones Playoff MVP
    run_playoffs(league)
    validate_playoffs(league)

    if print_outputs:
        print_playoff_summary(league)

    # 4. Historical Memory + Retirements / Aging
    run_year_end_transition(league)
    validate_year_end_transition_after_season(league, expected_previous_year=starting_year)

    if print_outputs:
        print_year_end_memory_summary(league)


def validate_year_end_transition_after_season(league, expected_previous_year):
    errors = []

    expected_current_year = expected_previous_year + 1

    if league.current_year != expected_current_year:
        errors.append(
            f"Expected league.current_year to be {expected_current_year}, found {league.current_year}."
        )

    if not league.season_summaries:
        errors.append("No season summaries recorded after competitive season.")

    expected_summary_prefix = f"Year {expected_previous_year} Summary:"

    if not any(summary.startswith(expected_summary_prefix) for summary in league.season_summaries):
        errors.append(f"Missing season summary for Year {expected_previous_year}.")

    if errors:
        print("REUSABLE SEASON ENGINE VALIDATION: FAILED")
        for error in errors:
            print(f"- {error}")
        raise SystemExit(1)

    print("REUSABLE SEASON ENGINE VALIDATION: PASS")



# ============================================================
# ENHANCED YEARLY OFFSEASON / FREE AGENCY
# ============================================================

OFFSEASON_TARGET_ROSTER_SIZE = INITIAL_DRAFT_ROUNDS
OFFSEASON_MAX_ROSTER_SIZE = INITIAL_DRAFT_ROUNDS


def team_missed_playoffs(team, league):
    playoff_team_names = set()

    for line in league.playoff_results:
        if line.startswith("1.") or line.startswith("2.") or line.startswith("3.") or line.startswith("4.") or line.startswith("5.") or line.startswith("6.") or line.startswith("7.") or line.startswith("8."):
            # Example: "1. Miami Tide (47-13)"
            clean = line.split(".", 1)[1].strip()
            team_name = clean.rsplit("(", 1)[0].strip()
            playoff_team_names.add(team_name)

    return team.identity.name not in playoff_team_names


def offseason_upgrade_slots(team, league):
    slots = 0

    if team.wins < 25:
        slots += 2
    elif team.wins < 35:
        slots += 1

    # Impatient owners push harder.
    if team.owner.patience and team.owner.patience < 55:
        slots += 1

    # Win-at-all-costs pressure.
    if team.owner.winning_desire >= 90:
        slots += 1

    # Cap at 2 so rosters do not churn too aggressively.
    return min(2, slots)


def weakest_roster_player(team):
    if not team.roster:
        return None

    return min(
        team.roster,
        key=lambda player: (
            player.value_score,
            player.overall,
            player.potential
        )
    )


def upgrade_threshold(team, league):
    threshold = 8

    if team.wins < 25:
        threshold -= 2

    if team.owner.winning_desire >= 90:
        threshold -= 1

    if team.market_profile and team.market_profile.free_agent_appeal >= 85:
        threshold -= 1

    if team.identity.name == league.current_champion:
        threshold += 3

    return max(4, threshold)


def waive_player_from_team(league, team, player, reason):
    if player not in team.roster:
        return

    team.roster.remove(player)
    player.team = None

    line = (
        f"Year {league.current_year} Offseason: {team.identity.name} waived "
        f"{player.name}, {player.position}, {player.tier}, OVR {player.overall} "
        f"({reason})."
    )

    league.offseason_log.append(line)
    league.history.append(line)


def best_free_agent_upgrade_for_team(league, team):
    candidates = available_free_agents(league)

    if not candidates:
        return None

    return max(
        candidates,
        key=lambda player: score_free_agent_for_team(player, team)
    )


def attempt_roster_upgrade(league, team):
    if len(team.roster) < OFFSEASON_TARGET_ROSTER_SIZE:
        repair_team_roster_from_free_agency(league, team)
        return True

    if len(team.roster) > OFFSEASON_MAX_ROSTER_SIZE:
        return False

    weakest = weakest_roster_player(team)
    candidate = best_free_agent_upgrade_for_team(league, team)

    if weakest is None or candidate is None:
        return False

    threshold = upgrade_threshold(team, league)
    improvement = candidate.value_score - weakest.value_score

    if improvement < threshold:
        return False

    waive_player_from_team(
        league,
        team,
        weakest,
        reason=f"upgrade opportunity; incoming value improvement {improvement}"
    )

    sign_free_agent_to_team(league, team, candidate)
    return True


def offseason_team_priority(team, league):
    # Lower wins = higher priority.
    pressure = 0

    pressure += max(0, 40 - team.wins) * 3
    pressure += team.owner.winning_desire * 0.7
    pressure += max(0, 70 - team.owner.patience) * 0.6

    if team_missed_playoffs(team, league):
        pressure += 25

    if team.market_profile:
        pressure += team.market_profile.media_pressure * 0.25

    return pressure



def run_yearly_offseason(league):
    league.offseason_log = []

    opening_line = f"Year {league.current_year} Offseason: Free agency opened."
    league.offseason_log.append(opening_line)
    league.history.append(opening_line)

    # Phase 0: rookie class and annual draft.
    ensure_annual_rookie_class(league)
    run_annual_rookie_draft(league, rounds=ANNUAL_DRAFT_ROUNDS)

    # Ensure long-term free agent depth before repairs.
    ensure_free_agent_depth(league)

    # Phase 1: roster repair.
    repair_count = 0

    for team in league.teams.values():
        before = len(team.roster)
        repair_team_roster_from_free_agency(league, team)
        after = len(team.roster)

        if after > before:
            repair_count += after - before

    if repair_count == 0:
        line = (
            f"Year {league.current_year} Offseason: No roster repair signings were required. "
            f"All teams retained at least {OFFSEASON_TARGET_ROSTER_SIZE} active players."
        )
        league.offseason_log.append(line)
        league.history.append(line)
    else:
        line = f"Year {league.current_year} Offseason: {repair_count} roster repair signing(s) completed."
        league.offseason_log.append(line)
        league.history.append(line)

    # Phase 2: upgrade market.
    prioritized_teams = sorted(
        league.teams.values(),
        key=lambda team: offseason_team_priority(team, league),
        reverse=True
    )

    upgrades_completed = 0

    for team in prioritized_teams:
        slots = offseason_upgrade_slots(team, league)

        for _ in range(slots):
            upgraded = attempt_roster_upgrade(league, team)

            if upgraded:
                upgrades_completed += 1
            else:
                break

    if upgrades_completed == 0:
        line = f"Year {league.current_year} Offseason: No upgrade signings cleared the market threshold."
        league.offseason_log.append(line)
        league.history.append(line)
    else:
        line = f"Year {league.current_year} Offseason: {upgrades_completed} upgrade signing(s) completed."
        league.offseason_log.append(line)
        league.history.append(line)

    closing_line = f"Year {league.current_year} Offseason: Free agency roster phase closed."
    league.offseason_log.append(closing_line)
    league.history.append(closing_line)



def validate_draft_rights_integrity(league):
    errors = []

    drafted_players = [
        player for player in league.player_pool
        if getattr(player, "drafted_by", None) is not None
        and player.draft_year == league.current_year
    ]

    draft_picks = [
        player.draft_pick for player in drafted_players
        if player.draft_pick is not None
    ]

    if len(draft_picks) != len(set(draft_picks)):
        errors.append(
            f"Duplicate draft pick numbers detected in Year {league.current_year} rookie draft."
        )

    rights_pairs = []

    for player in drafted_players:
        if player.draft_rights_team is None:
            errors.append(f"Drafted player {player.name} has no draft_rights_team.")

        rights_pairs.append((player.player_id, player.draft_rights_team))

        if player.team is not None and player.team != player.draft_rights_team:
            errors.append(
                f"Draft rights/team mismatch for {player.name}: "
                f"team={player.team}, rights={player.draft_rights_team}."
            )

    player_ids = [pair[0] for pair in rights_pairs]

    if len(player_ids) != len(set(player_ids)):
        errors.append("Duplicate drafted player IDs detected in draft rights registry.")

    if errors:
        print("DRAFT RIGHTS VALIDATION: FAILED")
        for error in errors:
            print(f"- {error}")
        raise SystemExit(1)

    print("DRAFT RIGHTS VALIDATION: PASS")


def validate_yearly_offseason(league):
    errors = []

    if not league.offseason_log:
        errors.append("Offseason log is empty.")

    all_rostered_ids = []

    for team in league.teams.values():
        if len(team.roster) < OFFSEASON_TARGET_ROSTER_SIZE:
            errors.append(
                f"{team.identity.name} has {len(team.roster)} players; expected at least {OFFSEASON_TARGET_ROSTER_SIZE}."
            )

        if len(team.roster) > OFFSEASON_MAX_ROSTER_SIZE:
            errors.append(
                f"{team.identity.name} has {len(team.roster)} players; max allowed is {OFFSEASON_MAX_ROSTER_SIZE}."
            )

        for player in team.roster:
            all_rostered_ids.append(player.player_id)

            if player.retired:
                errors.append(f"Retired player {player.name} is still on {team.identity.name}.")

            if player.team != team.identity.name:
                errors.append(
                    f"Roster/team mismatch: {player.name} has team={player.team}, expected {team.identity.name}."
                )

    if len(all_rostered_ids) != len(set(all_rostered_ids)):
        errors.append("Duplicate active roster player detected across teams.")

    if errors:
        print("YEARLY OFFSEASON VALIDATION: FAILED")
        for error in errors:
            print(f"- {error}")
        raise SystemExit(1)

    validate_draft_rights_integrity(league)

    print("YEARLY OFFSEASON VALIDATION: PASS")


def run_year_2_offseason(league):
    if league.current_year != 2:
        raise RuntimeError(
            f"Year 2 offseason expected league.current_year == 2, found {league.current_year}."
        )

    run_yearly_offseason(league)


def validate_year_2_offseason(league):
    errors = []

    if league.current_year != 2:
        errors.append(f"Expected league year 2 during offseason validation, found {league.current_year}.")

    try:
        validate_yearly_offseason(league)
    except SystemExit:
        raise

    if errors:
        print("YEAR 2 OFFSEASON VALIDATION: FAILED")
        for error in errors:
            print(f"- {error}")
        raise SystemExit(1)

    print("YEAR 2 OFFSEASON VALIDATION: PASS")



# ============================================================
# CONTROLLED GENESIS TEST LOOP
# ============================================================

def summarize_current_year_result(league, completed_year):
    mvp = get_award_result(league, "MVP:")
    roy = get_award_result(league, "Rookie of the Year:")

    summary = (
        f"Year {completed_year}: Champion={league.current_champion}; "
        f"Kanomi Jones Playoff MVP={league.playoff_mvp_name} ({league.playoff_mvp_team}); "
        f"{mvp if mvp else 'MVP: None'}; "
        f"{roy if roy else 'Rookie of the Year: None'}"
    )

    league.genesis_test_log.append(summary)
    return summary


def run_genesis_test_loop(league, start_year=2, end_year=5):
    if league.current_year != start_year:
        raise RuntimeError(
            f"Genesis test loop expected current_year {start_year}, found {league.current_year}."
        )

    league.genesis_test_log = []
    league.genesis_test_log.append(
        f"Genesis test loop started: Years {start_year}-{end_year}."
    )

    for season_year in range(start_year, end_year + 1):
        if league.current_year != season_year:
            raise RuntimeError(
                f"Expected league year {season_year} before season run, found {league.current_year}."
            )

        run_competitive_season(league, print_outputs=False)
        summarize_current_year_result(league, completed_year=season_year)

        # Run offseason only if another test season remains.
        if league.current_year <= end_year:
            run_yearly_offseason(league)
            validate_yearly_offseason(league)

    league.genesis_test_log.append(
        f"Genesis test loop completed. League calendar now at Year {league.current_year}."
    )



def validate_genesis_test_loop(league, start_year=2, end_year=5):
    errors = []

    expected_current_year = end_year + 1

    if league.current_year != expected_current_year:
        errors.append(
            f"Expected current_year {expected_current_year}, found {league.current_year}."
        )

    for year in range(1, end_year + 1):
        prefix = f"Year {year} Summary:"
        if not any(summary.startswith(prefix) for summary in league.season_summaries):
            errors.append(f"Missing historical season summary for Year {year}.")

    expected_total_championships = end_year
    actual_total_championships = sum(team.championships for team in league.teams.values())

    if actual_total_championships != expected_total_championships:
        errors.append(
            f"Expected {expected_total_championships} total championships, "
            f"found {actual_total_championships}."
        )

    expected_test_year_count = end_year - start_year + 1
    completed_year_lines = [
        line for line in league.genesis_test_log
        if line.startswith("Year ")
    ]

    if len(completed_year_lines) != expected_test_year_count:
        errors.append(
            f"Expected {expected_test_year_count} Genesis test year summaries, "
            f"found {len(completed_year_lines)}."
        )

    # Final-year roster note:
    # The test loop intentionally does NOT run offseason after the final simulated season.
    # Therefore, post-Year-5 retirements may leave some teams below the target roster size.
    # That is valid. The next offseason would repair those rosters.
    #
    # Still validate roster integrity:
    # - no retired player remains on an active roster
    # - no duplicated player ID exists across active rosters
    # - every rostered player points back to the correct team

    all_rostered_ids = []

    for team in league.teams.values():
        for player in team.roster:
            all_rostered_ids.append(player.player_id)

            if player.retired:
                errors.append(
                    f"Retired player {player.name} still exists on {team.identity.name} roster."
                )

            if player.team != team.identity.name:
                errors.append(
                    f"Roster/team mismatch: {player.name} has team={player.team}, "
                    f"expected {team.identity.name}."
                )

    if len(all_rostered_ids) != len(set(all_rostered_ids)):
        errors.append("Duplicate active roster player detected after Genesis test loop.")

    if errors:
        print("GENESIS TEST LOOP VALIDATION: FAILED")
        for error in errors:
            print(f"- {error}")
        raise SystemExit(1)

    print("GENESIS TEST LOOP VALIDATION: PASS")



def print_genesis_test_loop_summary(league):
    print("\n============================================")
    print("GENESIS TEST LOOP SUMMARY — YEARS 2-5")
    print("============================================")

    for line in league.genesis_test_log:
        print(f"- {line}")

    print("\nChampionship Ledger:")
    champions = [
        team for team in league.teams.values()
        if team.championships > 0
    ]

    for team in sorted(champions, key=lambda t: t.championships, reverse=True):
        print(f"- {team.identity.name}: {team.championships}")

    print("\nFinal Roster Counts After Year-End Retirements:")
    for team in league.teams.values():
        shortage = OFFSEASON_TARGET_ROSTER_SIZE - len(team.roster)

        if shortage > 0:
            print(
                f"- {team.identity.name}: {len(team.roster)} players "
                f"(needs {shortage} offseason repair signing(s))"
            )
        else:
            print(f"- {team.identity.name}: {len(team.roster)} players")

    print("\nRecent Historical Summaries:")
    for summary in league.season_summaries[-5:]:
        print(f"- {summary}")

    print(f"\nLeague Calendar: Year {league.current_year}")
    print("Status: Controlled Genesis test complete.")
    print("Note: Final-year roster shortages are valid because no offseason runs after the final test season.")
    print("============================================\n")



# ============================================================
# FULL GENESIS ERA RUNNER
# ============================================================

FULL_GENESIS_START_YEAR = 2
FULL_GENESIS_END_YEAR = 50
PUBLIC_ERA_ENTRY_YEAR = 51


def run_full_genesis_era(league, start_year=FULL_GENESIS_START_YEAR, end_year=FULL_GENESIS_END_YEAR):
    """
    Runs the hidden Genesis Era after Year 1.

    Year 1 is formation:
    - Staff hiring
    - Inaugural draft
    - First competitive season
    - Year 2 offseason bridge

    Years 2-50 are the hidden living-history simulation.
    Public Era begins at Season 51.
    """

    league.history.append(
        f"Genesis Era: Hidden simulation began for Years {start_year}-{end_year}."
    )

    run_genesis_test_loop(league, start_year=start_year, end_year=end_year)

    league.history.append(
        f"Genesis Era: Hidden simulation completed through Year {end_year}. "
        f"Public Era is ready to begin in Season {PUBLIC_ERA_ENTRY_YEAR}."
    )




def get_public_era_start_year(league):
    return getattr(
        league,
        "public_era_start_year",
        getattr(league, "public_era_begins", PUBLIC_ERA_ENTRY_YEAR)
    )


def validate_public_era_readiness(league):
    errors = []

    expected_public_year = get_public_era_start_year(league)

    if league.current_year != expected_public_year:
        errors.append(
            f"Expected league current year {expected_public_year}, found {league.current_year}."
        )

    expected_completed_seasons = expected_public_year - 1

    if len(league.season_summaries) < expected_completed_seasons:
        errors.append(
            f"Expected at least {expected_completed_seasons} season summaries, "
            f"found {len(league.season_summaries)}."
        )

    total_championships = sum(team.championships for team in league.teams.values())

    if total_championships != expected_completed_seasons:
        errors.append(
            f"Expected {expected_completed_seasons} total championships, "
            f"found {total_championships}."
        )

    if not any(team.championships > 0 for team in league.teams.values()):
        errors.append("No championship history exists.")

    active_rostered_players = [
        player for player in league.player_pool
        if player.team is not None and not player.retired
    ]

    if len(active_rostered_players) == 0:
        errors.append("No active rostered players exist at public era readiness.")

    if not league.history:
        errors.append("League history log is empty.")

    if errors:
        print("PUBLIC ERA READINESS VALIDATION: FAILED")
        for error in errors:
            print(f"- {error}")
        raise SystemExit(1)

    print("PUBLIC ERA READINESS VALIDATION: PASS")



def print_public_era_readiness_summary(league):
    print("\n============================================")
    print("PUBLIC ERA READINESS REPORT")
    print("============================================")
    print(f"League: {league.name}")
    print(f"Current Year: {league.current_year}")
    print(f"Public Era Begins: Season {get_public_era_start_year(league)}")
    print(f"Teams: {len(league.teams)}")
    print(f"History Events Recorded: {len(league.history)}")

    print("\nChampionship Ledger:")
    championship_leaders = sorted(
        league.teams.values(),
        key=lambda team: getattr(team, "championships", 0),
        reverse=True
    )

    for team in championship_leaders:
        titles = getattr(team, "championships", 0)
        if titles > 0:
            print(f"- {team.identity.name}: {titles}")

    print("\nCurrent Team Snapshot:")
    standings = sorted(
        league.teams.values(),
        key=lambda team: (
            getattr(team, "wins", 0),
            -getattr(team, "losses", 0)
        ),
        reverse=True
    )

    for rank, team in enumerate(standings, start=1):
        print(
            f"{rank}. {team.identity.name} | "
            f"Record {getattr(team, 'wins', 0)}-{getattr(team, 'losses', 0)} | "
            f"GM: {team.gm.name if team.gm else 'None'} | "
            f"Coach: {team.coach.name if team.coach else 'None'} | "
            f"Roster: {len(team.roster)}"
        )

    active_players = [
        player for player in getattr(league, "player_pool", [])
        if getattr(player, "team", None) is not None
        and not getattr(player, "retired", False)
    ]

    if active_players:
        print("\nTop 25 Active Players Entering Public Era:")

        ranked_players = sorted(
            active_players,
            key=lambda player: get_player_value(player),
            reverse=True
        )

        for rank, player in enumerate(ranked_players[:25], start=1):
            print(
                f"{rank}. {getattr(player, 'name', 'Unknown Player')} | "
                f"{getattr(player, 'team', 'N/A')} | "
                f"{getattr(player, 'position', 'N/A')} | "
                f"Age {getattr(player, 'age', 'N/A')} | "
                f"{getattr(player, 'tier', 'N/A')} | "
                f"OVR {getattr(player, 'overall', 'N/A')} | "
                f"POT {getattr(player, 'potential', 'N/A')}"
            )

    print("\nRecent Award Results:")
    for result in league.award_results[-20:]:
        print(f"- {result}")

    print("\nRecent History:")
    for event in league.history[-40:]:
        print(f"- {event}")

    print("============================================\n")


# ============================================================
# ANNUAL ROOKIE CLASS / YEARLY DRAFT SYSTEM
# ============================================================

ANNUAL_ROOKIE_CLASS_SIZE = 64
ANNUAL_DRAFT_ROUNDS = 2
MIN_FREE_AGENT_DEPTH = 80

ROOKIE_FIRST_NAMES = [
    "Malik", "Jalen", "Cameron", "Isaiah", "Darius", "Andre", "Tyrese", "Miles",
    "Jordan", "Xavier", "Micah", "Amari", "Kendrick", "Devin", "Elijah", "Bryce",
    "Nolan", "Roman", "Ashton", "Corey", "Lamar", "Quentin", "Tobias", "Donovan",
]

ROOKIE_LAST_NAMES = [
    "Harris", "Brooks", "Walker", "Carter", "Mitchell", "Reed", "Parker", "Foster",
    "Bell", "Coleman", "Sanders", "Bennett", "Price", "Watson", "King", "Dawson",
    "Hayes", "Morris", "Graves", "Wallace", "Porter", "Wright", "Knight", "Lawson",
]


def next_player_id(league):
    if not league.player_pool:
        return 1
    return max(player.player_id for player in league.player_pool) + 1


def annual_rookie_rng(league, label):
    return random.Random(f"NBF-LBU-v1:rookie-class:{league.current_year}:{label}")


def annual_rookie_tier(rng):
    roll = rng.random()

    if roll < 0.005:
        return "Generational"
    if roll < 0.035:
        return "Superstar"
    if roll < 0.115:
        return "Star"
    if roll < 0.355:
        return "Starter"
    if roll < 0.805:
        return "Role"

    return "Fringe"


def overall_for_rookie_tier(tier, rng):
    ranges = {
        "Generational": (90, 97),
        "Superstar": (84, 91),
        "Star": (78, 85),
        "Starter": (70, 78),
        "Role": (62, 72),
        "Fringe": (52, 64),
    }

    low, high = ranges.get(tier, (58, 70))
    return rng.randint(low, high)


def generate_rookie_name(league, rng):
    existing_names = set(player.name for player in league.player_pool)

    for _ in range(200):
        name = f"{rng.choice(ROOKIE_FIRST_NAMES)} {rng.choice(ROOKIE_LAST_NAMES)}"

        if name not in existing_names:
            return name

    return f"{rng.choice(ROOKIE_FIRST_NAMES)} {rng.choice(ROOKIE_LAST_NAMES)} Jr."


def generate_annual_rookie_class(league, size=ANNUAL_ROOKIE_CLASS_SIZE):
    rng = annual_rookie_rng(league, "class")
    rookies = []

    for index in range(size):
        local_rng = annual_rookie_rng(league, f"rookie:{index}")

        tier = annual_rookie_tier(local_rng)
        position = local_rng.choice(["PG", "SG", "SF", "PF", "C"])
        age = local_rng.randint(19, 22)
        overall = overall_for_rookie_tier(tier, local_rng)

        rookie = Player(
            player_id=next_player_id(league),
            name=generate_rookie_name(league, local_rng),
            position=position,
            age=age,
            tier=tier,
            overall=overall,
            draft_year=league.current_year,
        )

        enrich_player(rookie)

        league.player_pool.append(rookie)
        rookies.append(rookie)

    league.history.append(
        f"Year {league.current_year}: A rookie class of {len(rookies)} players entered the league ecosystem."
    )

    return rookies


def rookie_class_exists_for_year(league, year):
    return any(
        player.draft_year == year
        and player.age <= 23
        and player.years_pro == 0
        for player in league.player_pool
    )


def ensure_annual_rookie_class(league):
    if rookie_class_exists_for_year(league, league.current_year):
        return []

    return generate_annual_rookie_class(league, size=ANNUAL_ROOKIE_CLASS_SIZE)


def annual_draft_order(league):
    return sorted(
        league.teams.values(),
        key=lambda team: (
            team.wins,
            winning_percentage(team),
            team_roster_strength(team),
        )
    )



def available_rookies_for_current_draft(league):
    return [
        player for player in league.player_pool
        if player.draft_year == league.current_year
        and player.team is None
        and not player.retired
        and getattr(player, "draft_rights_team", None) is None
        and getattr(player, "drafted_by", None) is None
    ]


def score_rookie_for_team(player, team):
    score = score_free_agent_for_team(player, team)

    # Young upside matters more in the draft.
    score += player.potential * 0.35

    if player.age <= 20:
        score += 4

    if team.gm:
        if "Draft" in team.gm.personality or "Talent" in team.gm.personality:
            score += 7
        if "Development" in team.gm.personality:
            score += 4

    return score



def assign_draft_rights(player, team, pick_number):
    player.draft_pick = pick_number
    player.drafted_by = team.identity.name
    player.draft_rights_team = team.identity.name
    player.draft_signed = False


def run_annual_rookie_draft(league, rounds=ANNUAL_DRAFT_ROUNDS):
    rookies = available_rookies_for_current_draft(league)

    if not rookies:
        return 0

    draft_order = annual_draft_order(league)
    pick_number = 1
    signed_count = 0

    league.offseason_log.append(f"Year {league.current_year} Offseason: Annual rookie draft opened.")
    league.history.append(league.offseason_log[-1])

    for round_number in range(1, rounds + 1):
        for team in draft_order:
            candidates = available_rookies_for_current_draft(league)

            if not candidates:
                break

            selected = max(
                candidates,
                key=lambda player: score_rookie_for_team(player, team)
            )

            # Critical invariant:
            # Once selected, the player leaves the draft pool whether signed immediately or not.
            assign_draft_rights(selected, team, pick_number)

            # If there is room, sign the rookie.
            if len(team.roster) < OFFSEASON_MAX_ROSTER_SIZE:
                sign_free_agent_to_team(league, team, selected)
                selected.draft_signed = True
                selected.draft_rights_team = team.identity.name
                signed_count += 1

            else:
                weakest = weakest_roster_player(team)

                # Drafted rookies can replace weak roster pieces if clearly better.
                if weakest and selected.value_score >= weakest.value_score + 4:
                    waive_player_from_team(
                        league,
                        team,
                        weakest,
                        reason=f"annual draft upgrade; rookie pick {pick_number}"
                    )
                    sign_free_agent_to_team(league, team, selected)
                    selected.draft_signed = True
                    selected.draft_rights_team = team.identity.name
                    signed_count += 1
                else:
                    line = (
                        f"Year {league.current_year} Offseason: {team.identity.name} selected "
                        f"{selected.name}, {selected.position}, {selected.tier}, OVR {selected.overall} "
                        f"with pick {pick_number}; draft rights retained, no roster spot opened."
                    )
                    league.offseason_log.append(line)
                    league.history.append(line)

            pick_number += 1

    league.offseason_log.append(
        f"Year {league.current_year} Offseason: Annual rookie draft completed with {signed_count} rookie signing(s)."
    )
    league.history.append(league.offseason_log[-1])

    return signed_count


def ensure_free_agent_depth(league):
    available_count = len(available_free_agents(league))

    if available_count >= MIN_FREE_AGENT_DEPTH:
        return 0

    needed = MIN_FREE_AGENT_DEPTH - available_count
    generated = generate_annual_rookie_class(league, size=needed)

    line = (
        f"Year {league.current_year} Offseason: Emergency talent replenishment added "
        f"{len(generated)} player(s) to the free agent ecosystem."
    )

    league.offseason_log.append(line)
    league.history.append(line)

    return len(generated)



# ============================================================
# GENESIS ERA SEASON MVP LEGACY NAMING
# ============================================================

def genesis_era_greatness_score(player):
    """
    Scores the best player of the first 50 years.

    Built from:
    - regular-season MVPs
    - playoff MVPs
    - championships
    - defensive awards
    - production
    - longevity
    - peak tier
    """

    score = 0

    score += player.mvp_awards * 1000
    score += player.playoff_mvp_awards * 850
    score += player.championships * 700
    score += player.defensive_player_awards * 350
    score += player.rookie_of_year_awards * 150
    score += player.most_improved_awards * 80
    score += player.all_star_appearances * 90

    score += player.career_points * 0.08
    score += player.career_rebounds * 0.06
    score += player.career_assists * 0.06

    score += player.overall * 6
    score += player.potential * 3
    score += player.years_pro * 45

    if player.tier == "Generational":
        score += 750
    elif player.tier == "Superstar":
        score += 450
    elif player.tier == "Star":
        score += 200

    return score


def select_genesis_era_greatest_player(league):
    candidates = [
        player for player in league.player_pool
        if player.years_pro > 0
        or player.mvp_awards > 0
        or player.playoff_mvp_awards > 0
        or player.championships > 0
        or player.career_points > 0
    ]

    if not candidates:
        raise RuntimeError("Cannot name Season MVP award: no Genesis player candidates found.")

    winner = max(
        candidates,
        key=lambda player: genesis_era_greatness_score(player)
    )

    return winner



def name_season_mvp_award_after_genesis_greatest(league):
    public_year = get_public_era_start_year(league)

    if league.current_year != public_year:
        raise RuntimeError(
            f"Cannot name public era Season MVP award before Season {public_year}. "
            f"Current year: {league.current_year}."
        )

    if league.season_mvp_legacy_player_id is not None:
        return league.season_mvp_legacy_player_name

    greatest = select_genesis_era_greatest_player(league)

    league.season_mvp_legacy_player_id = greatest.player_id
    league.season_mvp_legacy_player_name = greatest.name
    league.season_mvp_award_name = f"{greatest.name} Season MVP Award"

    line = (
        f"After the 50-year Genesis Era, the NBF named its regular-season MVP award "
        f"the {league.season_mvp_award_name}, honoring {greatest.name} as the defining "
        f"player of the league's first 50 seasons."
    )

    league.history.append(line)

    return greatest.name



def validate_season_mvp_legacy_name(league):
    errors = []

    public_year = get_public_era_start_year(league)

    if league.current_year != public_year:
        errors.append(
            f"Expected league to be at public era Season {public_year}, found Year {league.current_year}."
        )

    if not league.season_mvp_legacy_player_name:
        errors.append("Season MVP legacy player name was not set.")

    if not league.season_mvp_award_name.endswith("Season MVP Award"):
        errors.append(f"Invalid Season MVP award name: {league.season_mvp_award_name}")

    if league.season_mvp_legacy_player_id is None:
        errors.append("Season MVP legacy player ID was not set.")

    if errors:
        print("SEASON MVP LEGACY NAMING VALIDATION: FAILED")
        for error in errors:
            print(f"- {error}")
        raise SystemExit(1)

    print("SEASON MVP LEGACY NAMING VALIDATION: PASS")


def print_season_mvp_legacy_summary(league):
    print("\n============================================")
    print("GENESIS ERA SEASON MVP LEGACY NAME")
    print("============================================")
    print(f"Legacy Player: {league.season_mvp_legacy_player_name}")
    print(f"Public Era Award Name: {league.season_mvp_award_name}")

    player = None
    if league.season_mvp_legacy_player_id is not None:
        for candidate in league.player_pool:
            if candidate.player_id == league.season_mvp_legacy_player_id:
                player = candidate
                break

    if player:
        print(
            f"Career Snapshot: {player.career_points} PTS | "
            f"{player.career_rebounds} REB | {player.career_assists} AST | "
            f"MVPs {player.mvp_awards} | Playoff MVPs {player.playoff_mvp_awards} | "
            f"Championships {player.championships}"
        )

    print("============================================\n")



# ============================================================
# PUBLIC ERA SNAPSHOT EXPORT
# ============================================================

PUBLIC_ERA_EXPORT_FILES = [
    "public_era_snapshot.json",
    "public_era_summary.txt",
    "championship_ledger.txt",
    "season_summaries.txt",
    "award_history.txt",
    "top_active_players.txt",
    "public_era_export_manifest.txt",
]


def player_to_snapshot_dict(player):
    return {
        "player_id": player.player_id,
        "name": player.name,
        "team": player.team,
        "position": player.position,
        "age": player.age,
        "tier": player.tier,
        "overall": player.overall,
        "potential": player.potential,
        "offense": player.offense,
        "defense": player.defense,
        "shooting": player.shooting,
        "playmaking": player.playmaking,
        "rebounding": player.rebounding,
        "basketball_iq": player.basketball_iq,
        "athleticism": player.athleticism,
        "leadership": player.leadership,
        "discipline": player.discipline,
        "confidence": player.confidence,
        "popularity": player.popularity,
        "durability": player.durability,
        "injury_risk": player.injury_risk,
        "motivation": player.motivation,
        "draft_year": player.draft_year,
        "draft_pick": player.draft_pick,
        "drafted_by": getattr(player, "drafted_by", None),
        "draft_rights_team": getattr(player, "draft_rights_team", None),
        "draft_signed": getattr(player, "draft_signed", False),
        "retired": player.retired,
        "years_pro": player.years_pro,
        "championships": player.championships,
        "mvp_awards": player.mvp_awards,
        "playoff_mvp_awards": player.playoff_mvp_awards,
        "rookie_of_year_awards": getattr(player, "rookie_of_year_awards", 0),
        "defensive_player_awards": getattr(player, "defensive_player_awards", 0),
        "career_points": player.career_points,
        "career_rebounds": player.career_rebounds,
        "career_assists": player.career_assists,
        "value_score": player.value_score,
    }


def team_to_snapshot_dict(team):
    market = team.market_profile

    return {
        "name": team.identity.name,
        "conference": team.identity.conference,
        "mascot": team.identity.mascot,
        "colors": team.identity.colors,
        "rivals": team.identity.rivals,
        "blood_rivals": team.identity.blood_rivals,
        "owner": {
            "name": team.owner.name,
            "owner_type": team.owner.owner_type,
            "age": team.owner.age,
            "industry": team.owner.industry,
            "net_worth_b": team.owner.net_worth_b,
            "winning_desire": team.owner.winning_desire,
            "patience": team.owner.patience,
            "greed": team.owner.greed,
            "control": team.owner.control,
            "pr_awareness": team.owner.pr_awareness,
            "philosophy": team.owner.philosophy,
            "hidden_traits": team.owner.hidden_traits,
        },
        "market": {
            "arena": market.arena if market else "",
            "capacity": market.capacity if market else 0,
            "atmosphere": market.atmosphere if market else 0,
            "luxury": market.luxury if market else 0,
            "ticket_price_index": market.ticket_price_index if market else 0,
            "market_size": market.market_size if market else "",
            "fan_passion": market.fan_passion if market else 0,
            "fan_loyalty": market.fan_loyalty if market else 0,
            "fan_patience": market.fan_patience if market else 0,
            "media_pressure": market.media_pressure if market else 0,
            "free_agent_appeal": market.free_agent_appeal if market else 0,
            "corporate_power": market.corporate_power if market else 0,
        },
        "gm": {
            "name": team.gm.name if team.gm else None,
            "age": team.gm.age if team.gm else None,
            "personality": team.gm.personality if team.gm else None,
            "overall": team.gm.overall if team.gm else None,
        },
        "coach": {
            "name": team.coach.name if team.coach else None,
            "age": team.coach.age if team.coach else None,
            "personality": team.coach.personality if team.coach else None,
            "overall": team.coach.overall if team.coach else None,
        },
        "record": {
            "wins": team.wins,
            "losses": team.losses,
        },
        "championships": team.championships,
        "roster_count": len(team.roster),
        "roster": [player_to_snapshot_dict(player) for player in team.roster],
    }


def championship_ledger_lines(league):
    teams = sorted(
        league.teams.values(),
        key=lambda team: team.championships,
        reverse=True
    )

    lines = []

    for team in teams:
        if team.championships > 0:
            lines.append(f"{team.identity.name}: {team.championships}")

    return lines


def active_players_ranked(league):
    active_players = [
        player for player in league.player_pool
        if player.team is not None and not player.retired
    ]

    return sorted(
        active_players,
        key=lambda player: player.value_score,
        reverse=True
    )


def award_history_lines(league):
    markers = [
        ": MVP:",
        ": Rookie of the Year:",
        ": Defensive Player of the Year:",
        ": Sixth Man of the Year:",
        ": Most Improved Player:",
        ": Coach of the Year:",
        ": Executive of the Year:",
        ": Owner of the Year:",
        ": Reporter of the Year:",
        "Kanomi Jones Playoff MVP",
        "Season MVP Award",
    ]

    lines = []

    for event in league.history:
        if any(marker in event for marker in markers):
            lines.append(event)

    return lines



def safe_league_attr(league, *names, default=None):
    for name in names:
        if hasattr(league, name):
            value = getattr(league, name)
            if value is not None:
                return value
    return default


def build_public_era_snapshot_dict(league):
    active_players = active_players_ranked(league)

    return {
        "league": {
            "name": safe_league_attr(league, "name", default="National Basketball Federation"),
            "motto": safe_league_attr(league, "motto", default="Ball On 'Em"),
            "championship_trophy": safe_league_attr(
                league,
                "championship_trophy",
                default="Albert Green Championship Trophy"
            ),
            "commissioner": safe_league_attr(
                league,
                "commissioner",
                "commissioner_name",
                default="Victor Hale"
            ),
            "hall_of_fame": safe_league_attr(
                league,
                "hall_of_fame",
                "hall_of_fame_name",
                default="Albert Green Basketball Hall of Fame"
            ),
            "hall_location": safe_league_attr(
                league,
                "hall_location",
                "hall_of_fame_location",
                default="Springfield, Missouri"
            ),
            "current_year": league.current_year,
            "public_era_start_year": get_public_era_start_year(league),
            "season_mvp_award_name": safe_league_attr(
                league,
                "season_mvp_award_name",
                default="MVP"
            ),
            "season_mvp_legacy_player_id": safe_league_attr(
                league,
                "season_mvp_legacy_player_id",
                default=None
            ),
            "season_mvp_legacy_player_name": safe_league_attr(
                league,
                "season_mvp_legacy_player_name",
                default=None
            ),
            "playoff_mvp_award_name": safe_league_attr(
                league,
                "playoff_mvp_award_name",
                default="Kanomi Jones Playoff MVP"
            ),
        },
        "counts": {
            "teams": len(league.teams),
            "player_pool": len(league.player_pool),
            "active_rostered_players": len(active_players),
            "free_agents": len(available_free_agents(league)),
            "history_events": len(league.history),
            "season_summaries": len(league.season_summaries),
        },
        "championship_ledger": championship_ledger_lines(league),
        "teams": {
            team_name: team_to_snapshot_dict(team)
            for team_name, team in league.teams.items()
        },
        "top_active_players": [
            player_to_snapshot_dict(player)
            for player in active_players[:100]
        ],
        "season_summaries": league.season_summaries,
        "recent_history": league.history[-250:],
        "award_history": award_history_lines(league),
    }


def export_public_era_snapshot(league):
    import json
    from pathlib import Path

    snapshot = build_public_era_snapshot_dict(league)

    Path("public_era_snapshot.json").write_text(
        json.dumps(snapshot, indent=2),
        encoding="utf-8"
    )

    summary_lines = [
        "PUBLIC ERA SUMMARY",
        "===================",
        f"League: {league.name}",
        f"Current Year: {league.current_year}",
        f"Public Era Begins: Season {get_public_era_start_year(league)}",
        f"Teams: {len(league.teams)}",
        f"History Events: {len(league.history)}",
        f"Season MVP Award: {league.season_mvp_award_name}",
        f"Playoff MVP Award: {league.playoff_mvp_award_name}",
        "",
        "Championship Ledger:",
    ]

    summary_lines.extend(f"- {line}" for line in championship_ledger_lines(league))

    Path("public_era_summary.txt").write_text(
        "\n".join(summary_lines) + "\n",
        encoding="utf-8"
    )

    Path("championship_ledger.txt").write_text(
        "\n".join(championship_ledger_lines(league)) + "\n",
        encoding="utf-8"
    )

    Path("season_summaries.txt").write_text(
        "\n".join(league.season_summaries) + "\n",
        encoding="utf-8"
    )

    Path("award_history.txt").write_text(
        "\n".join(award_history_lines(league)) + "\n",
        encoding="utf-8"
    )

    top_lines = []

    for rank, player in enumerate(active_players_ranked(league)[:100], start=1):
        top_lines.append(
            f"{rank}. {player.name} | {player.team} | {player.position} | "
            f"Age {player.age} | {player.tier} | OVR {player.overall} | "
            f"POT {player.potential} | Value {player.value_score}"
        )

    Path("top_active_players.txt").write_text(
        "\n".join(top_lines) + "\n",
        encoding="utf-8"
    )

    manifest_lines = [
        "PUBLIC ERA EXPORT MANIFEST",
        "==========================",
        f"League: {league.name}",
        f"Export Year: {league.current_year}",
        f"Public Era Begins: Season {get_public_era_start_year(league)}",
        "",
        "Files:",
    ]

    for filename in PUBLIC_ERA_EXPORT_FILES:
        manifest_lines.append(f"- {filename}")

    Path("public_era_export_manifest.txt").write_text(
        "\n".join(manifest_lines) + "\n",
        encoding="utf-8"
    )

    league.history.append(
        f"Public Era snapshot exported for Season {get_public_era_start_year(league)}."
    )


def validate_public_era_export():
    import json
    from pathlib import Path

    errors = []

    for filename in PUBLIC_ERA_EXPORT_FILES:
        path = Path(filename)

        if not path.exists():
            errors.append(f"Missing export file: {filename}")
            continue

        if path.stat().st_size == 0:
            errors.append(f"Export file is empty: {filename}")

    try:
        data = json.loads(Path("public_era_snapshot.json").read_text(encoding="utf-8"))

        if "league" not in data:
            errors.append("public_era_snapshot.json missing league key.")

        if "teams" not in data:
            errors.append("public_era_snapshot.json missing teams key.")

        if "championship_ledger" not in data:
            errors.append("public_era_snapshot.json missing championship_ledger key.")

    except Exception as exc:
        errors.append(f"public_era_snapshot.json could not be parsed: {exc}")

    if errors:
        print("PUBLIC ERA EXPORT VALIDATION: FAILED")
        for error in errors:
            print(f"- {error}")
        raise SystemExit(1)

    print("PUBLIC ERA EXPORT VALIDATION: PASS")


def print_public_era_export_summary():
    from pathlib import Path

    print("\n============================================")
    print("PUBLIC ERA EXPORT SUMMARY")
    print("============================================")

    for filename in PUBLIC_ERA_EXPORT_FILES:
        path = Path(filename)
        size = path.stat().st_size if path.exists() else 0
        print(f"- {filename} | {size} bytes")

    print("============================================\n")



# ============================================================
# PUBLIC ERA SNAPSHOT EXPORT V2 — FORCED FINAL EXPORT
# ============================================================

PUBLIC_ERA_EXPORT_FILES_V2 = [
    "public_era_snapshot.json",
    "public_era_summary.txt",
    "championship_ledger.txt",
    "season_summaries.txt",
    "award_history.txt",
    "top_active_players.txt",
    "public_era_export_manifest.txt",
]


def safe_attr_v2(obj, *names, default=None):
    for name in names:
        if hasattr(obj, name):
            value = getattr(obj, name)
            if value is not None:
                return value
    return default


def public_era_start_year_v2(league):
    return safe_attr_v2(
        league,
        "public_era_start_year",
        "public_era_begins",
        default=51,
    )


def player_snapshot_v2(player):
    return {
        "player_id": player.player_id,
        "name": player.name,
        "team": player.team,
        "position": player.position,
        "age": player.age,
        "tier": player.tier,
        "overall": player.overall,
        "potential": player.potential,
        "offense": player.offense,
        "defense": player.defense,
        "shooting": player.shooting,
        "playmaking": player.playmaking,
        "rebounding": player.rebounding,
        "basketball_iq": player.basketball_iq,
        "athleticism": player.athleticism,
        "leadership": player.leadership,
        "discipline": player.discipline,
        "confidence": player.confidence,
        "popularity": player.popularity,
        "durability": player.durability,
        "injury_risk": player.injury_risk,
        "motivation": player.motivation,
        "draft_year": player.draft_year,
        "draft_pick": player.draft_pick,
        "drafted_by": safe_attr_v2(player, "drafted_by", default=None),
        "draft_rights_team": safe_attr_v2(player, "draft_rights_team", default=None),
        "draft_signed": safe_attr_v2(player, "draft_signed", default=False),
        "retired": player.retired,
        "years_pro": player.years_pro,
        "championships": player.championships,
        "mvp_awards": player.mvp_awards,
        "playoff_mvp_awards": safe_attr_v2(player, "playoff_mvp_awards", default=0),
        "rookie_of_year_awards": safe_attr_v2(player, "rookie_of_year_awards", default=0),
        "defensive_player_awards": safe_attr_v2(player, "defensive_player_awards", default=0),
        "career_points": player.career_points,
        "career_rebounds": player.career_rebounds,
        "career_assists": player.career_assists,
        "value_score": player.value_score,
    }


def team_snapshot_v2(team):
    market = safe_attr_v2(team, "market_profile", default=None)

    return {
        "name": team.identity.name,
        "conference": team.identity.conference,
        "mascot": team.identity.mascot,
        "colors": team.identity.colors,
        "arena": team.identity.arena,
        "culture": team.identity.culture,
        "rivals": team.identity.rivals,
        "blood_rivals": team.identity.blood_rivals,
        "owner": {
            "name": team.owner.name,
            "owner_type": team.owner.owner_type,
            "age": safe_attr_v2(team.owner, "age", default=0),
            "industry": safe_attr_v2(team.owner, "industry", default=""),
            "net_worth_b": team.owner.net_worth_b,
            "winning_desire": safe_attr_v2(team.owner, "winning_desire", default=0),
            "patience": safe_attr_v2(team.owner, "patience", default=0),
            "greed": safe_attr_v2(team.owner, "greed", default=0),
            "control": safe_attr_v2(team.owner, "control", default=0),
            "pr_awareness": safe_attr_v2(team.owner, "pr_awareness", default=0),
            "philosophy": safe_attr_v2(team.owner, "philosophy", default=""),
            "hidden_traits": safe_attr_v2(team.owner, "hidden_traits", default=[]),
        },
        "market": {
            "arena": safe_attr_v2(market, "arena", default="") if market else "",
            "capacity": safe_attr_v2(market, "capacity", default=0) if market else 0,
            "atmosphere": safe_attr_v2(market, "atmosphere", default=0) if market else 0,
            "luxury": safe_attr_v2(market, "luxury", default=0) if market else 0,
            "market_size": safe_attr_v2(market, "market_size", default="") if market else "",
            "fan_passion": safe_attr_v2(market, "fan_passion", default=0) if market else 0,
            "fan_loyalty": safe_attr_v2(market, "fan_loyalty", default=0) if market else 0,
            "fan_patience": safe_attr_v2(market, "fan_patience", default=0) if market else 0,
            "media_pressure": safe_attr_v2(market, "media_pressure", default=0) if market else 0,
            "free_agent_appeal": safe_attr_v2(market, "free_agent_appeal", default=0) if market else 0,
        },
        "gm": {
            "name": team.gm.name if team.gm else None,
            "age": team.gm.age if team.gm else None,
            "personality": team.gm.personality if team.gm else None,
            "overall": team.gm.overall if team.gm else None,
        },
        "coach": {
            "name": team.coach.name if team.coach else None,
            "age": team.coach.age if team.coach else None,
            "personality": team.coach.personality if team.coach else None,
            "overall": team.coach.overall if team.coach else None,
        },
        "record": {
            "wins": team.wins,
            "losses": team.losses,
        },
        "championships": team.championships,
        "roster_count": len(team.roster),
        "roster": [player_snapshot_v2(player) for player in team.roster],
    }


def championship_ledger_v2(league):
    lines = []
    teams = sorted(
        league.teams.values(),
        key=lambda team: team.championships,
        reverse=True,
    )

    for team in teams:
        if team.championships > 0:
            lines.append(f"{team.identity.name}: {team.championships}")

    return lines


def active_players_v2(league):
    players = [
        player for player in league.player_pool
        if player.team is not None and not player.retired
    ]

    return sorted(
        players,
        key=lambda player: player.value_score,
        reverse=True,
    )


def award_history_v2(league):
    markers = [
        "MVP:",
        "Rookie of the Year:",
        "Defensive Player of the Year:",
        "Sixth Man of the Year:",
        "Most Improved Player:",
        "Coach of the Year:",
        "Executive of the Year:",
        "Owner of the Year:",
        "Reporter of the Year:",
        "Kanomi Jones Playoff MVP",
        "Season MVP Award",
    ]

    return [
        event for event in league.history
        if any(marker in event for marker in markers)
    ]



def build_public_era_snapshot_v2(league):
    active = active_players_v2(league)
    free_agents = available_free_agents(league)

    return {
        "league": {
            "name": safe_attr_v2(league, "name", default="National Basketball Federation"),
            "motto": safe_attr_v2(league, "motto", default="Ball On 'Em"),
            "championship_trophy": safe_attr_v2(
                league,
                "championship_trophy",
                default="Albert Green Championship Trophy",
            ),
            "commissioner": safe_attr_v2(
                league,
                "commissioner",
                "commissioner_name",
                default="Victor Hale",
            ),
            "hall_of_fame": safe_attr_v2(
                league,
                "hall_of_fame",
                "hall_of_fame_name",
                default="Albert Green Basketball Hall of Fame",
            ),
            "hall_location": safe_attr_v2(
                league,
                "hall_location",
                "hall_of_fame_location",
                default="Springfield, Missouri",
            ),
            "current_year": league.current_year,
            "public_era_start_year": public_era_start_year_v2(league),
            "season_mvp_award_name": safe_attr_v2(
                league,
                "season_mvp_award_name",
                default="MVP",
            ),
            "season_mvp_legacy_player_id": safe_attr_v2(
                league,
                "season_mvp_legacy_player_id",
                default=None,
            ),
            "season_mvp_legacy_player_name": safe_attr_v2(
                league,
                "season_mvp_legacy_player_name",
                default=None,
            ),
            "playoff_mvp_award_name": safe_attr_v2(
                league,
                "playoff_mvp_award_name",
                default="Kanomi Jones Playoff MVP",
            ),
        },
        "counts": {
            "teams": len(league.teams),
            "player_pool": len(league.player_pool),
            "active_rostered_players": len(active),
            "free_agents": len(free_agents),
            "history_events": len(league.history),
            "season_summaries": len(league.season_summaries),
        },
        "championship_ledger": championship_ledger_v2(league),
        "teams": {
            team_name: team_snapshot_v2(team)
            for team_name, team in league.teams.items()
        },
        "top_active_players": [
            player_snapshot_v2(player)
            for player in active[:100]
        ],
        "free_agents": [
            player_snapshot_v2(player)
            for player in free_agents
        ],
        "season_summaries": league.season_summaries,
        "award_history": award_history_v2(league),
        "recent_history": league.history[-250:],
    }


def export_public_era_snapshot_v2(league):
    import json
    from pathlib import Path

    snapshot = build_public_era_snapshot_v2(league)

    Path("public_era_snapshot.json").write_text(
        json.dumps(snapshot, indent=2, default=str),
        encoding="utf-8",
    )

    summary_lines = [
        "PUBLIC ERA SUMMARY",
        "===================",
        f"League: {snapshot['league']['name']}",
        f"Current Year: {snapshot['league']['current_year']}",
        f"Public Era Begins: Season {snapshot['league']['public_era_start_year']}",
        f"Teams: {snapshot['counts']['teams']}",
        f"History Events: {snapshot['counts']['history_events']}",
        f"Season MVP Award: {snapshot['league']['season_mvp_award_name']}",
        f"Playoff MVP Award: {snapshot['league']['playoff_mvp_award_name']}",
        "",
        "Championship Ledger:",
    ]

    summary_lines.extend(f"- {line}" for line in championship_ledger_v2(league))

    Path("public_era_summary.txt").write_text(
        "\n".join(summary_lines) + "\n",
        encoding="utf-8",
    )

    Path("championship_ledger.txt").write_text(
        "\n".join(championship_ledger_v2(league)) + "\n",
        encoding="utf-8",
    )

    Path("season_summaries.txt").write_text(
        "\n".join(league.season_summaries) + "\n",
        encoding="utf-8",
    )

    Path("award_history.txt").write_text(
        "\n".join(award_history_v2(league)) + "\n",
        encoding="utf-8",
    )

    top_lines = []

    for rank, player in enumerate(active_players_v2(league)[:100], start=1):
        top_lines.append(
            f"{rank}. {player.name} | {player.team} | {player.position} | "
            f"Age {player.age} | {player.tier} | OVR {player.overall} | "
            f"POT {player.potential} | Value {player.value_score}"
        )

    Path("top_active_players.txt").write_text(
        "\n".join(top_lines) + "\n",
        encoding="utf-8",
    )

    manifest_lines = [
        "PUBLIC ERA EXPORT MANIFEST",
        "==========================",
        f"League: {snapshot['league']['name']}",
        f"Export Year: {snapshot['league']['current_year']}",
        f"Public Era Begins: Season {snapshot['league']['public_era_start_year']}",
        "",
        "Files:",
    ]

    for filename in PUBLIC_ERA_EXPORT_FILES_V2:
        manifest_lines.append(f"- {filename}")

    Path("public_era_export_manifest.txt").write_text(
        "\n".join(manifest_lines) + "\n",
        encoding="utf-8",
    )

    league.history.append(
        f"Public Era snapshot exported for Season {public_era_start_year_v2(league)}."
    )


def validate_public_era_export_v2():
    import json
    from pathlib import Path

    errors = []

    for filename in PUBLIC_ERA_EXPORT_FILES_V2:
        path = Path(filename)

        if not path.exists():
            errors.append(f"Missing export file: {filename}")
            continue

        if path.stat().st_size == 0:
            errors.append(f"Export file is empty: {filename}")

    try:
        data = json.loads(Path("public_era_snapshot.json").read_text(encoding="utf-8"))

        for key in ["league", "counts", "teams", "championship_ledger", "top_active_players"]:
            if key not in data:
                errors.append(f"public_era_snapshot.json missing key: {key}")

    except Exception as exc:
        errors.append(f"public_era_snapshot.json parse failed: {exc}")

    if errors:
        print("PUBLIC ERA EXPORT VALIDATION: FAILED")
        for error in errors:
            print(f"- {error}")
        raise SystemExit(1)

    print("PUBLIC ERA EXPORT VALIDATION: PASS")


def print_public_era_export_summary_v2():
    from pathlib import Path

    print("\n============================================")
    print("PUBLIC ERA EXPORT SUMMARY")
    print("============================================")

    for filename in PUBLIC_ERA_EXPORT_FILES_V2:
        path = Path(filename)
        size = path.stat().st_size if path.exists() else 0
        print(f"- {filename} | {size} bytes")

    print("============================================\n")



# ============================================================

# ============================================================
# PUBLIC ERA SNAPSHOT ROSTER REPAIR MODE
# ============================================================

PUBLIC_ERA_REPAIR_TARGET_ROSTER_SIZE = 12
PUBLIC_ERA_REPAIRED_SNAPSHOT_FILE = "public_era_snapshot_repaired.json"
PUBLIC_ERA_REPAIR_LOG_FILE = "public_era_roster_repair_log.txt"


def free_agent_sort_key_from_snapshot(player):
    return (
        player.get("value_score", 0),
        player.get("overall", 0),
        player.get("potential", 0),
        -player.get("age", 99),
    )


def team_position_counts_from_snapshot(team):
    counts = {
        "PG": 0,
        "SG": 0,
        "SF": 0,
        "PF": 0,
        "C": 0,
    }

    for player in team.get("roster", []):
        position = player.get("position")
        counts[position] = counts.get(position, 0) + 1

    return counts


def score_free_agent_for_snapshot_team(player, team):
    score = player.get("value_score", 0) * 10
    score += player.get("overall", 0)
    score += player.get("potential", 0) * 0.25

    counts = team_position_counts_from_snapshot(team)
    position = player.get("position")
    position_count = counts.get(position, 0)

    if position_count == 0:
        score += 40
    elif position_count == 1:
        score += 20
    elif position_count == 2:
        score += 8
    elif position_count >= 4:
        score -= 12

    # Younger players carry public-era roster value.
    age = player.get("age", 30)
    if age <= 23:
        score += 10
    elif age >= 34:
        score -= 8

    return score


def repair_public_era_snapshot_rosters(snapshot):
    if "free_agents" not in snapshot:
        raise RuntimeError(
            "Snapshot missing free_agents list. Rerun full export after Step 3V patch, "
            "then rerun --resume-public-era --repair-rosters."
        )

    teams = snapshot.get("teams", {})
    free_agents = snapshot.get("free_agents", [])

    repair_log = []
    repair_log.append("PUBLIC ERA ROSTER REPAIR LOG")
    repair_log.append("============================")
    repair_log.append(
        f"Repair Target: {PUBLIC_ERA_REPAIR_TARGET_ROSTER_SIZE} players per team"
    )
    repair_log.append("")

    for team_name, team in teams.items():
        roster = team.get("roster", [])

        while len(roster) < PUBLIC_ERA_REPAIR_TARGET_ROSTER_SIZE:
            if not free_agents:
                raise RuntimeError("Free-agent list exhausted during Public Era roster repair.")

            selected = max(
                free_agents,
                key=lambda player: score_free_agent_for_snapshot_team(player, team)
            )

            free_agents.remove(selected)

            selected["team"] = team_name
            selected["draft_signed"] = True

            roster.append(selected)

            repair_log.append(
                f"{team_name} signed {selected.get('name')} | "
                f"{selected.get('position')} | {selected.get('tier')} | "
                f"OVR {selected.get('overall')} | POT {selected.get('potential')}"
            )

        team["roster"] = roster
        team["roster_count"] = len(roster)

    active_count = 0

    for team in teams.values():
        active_count += len(team.get("roster", []))

    snapshot["free_agents"] = free_agents
    snapshot["counts"]["active_rostered_players"] = active_count
    snapshot["counts"]["free_agents"] = len(free_agents)

    snapshot.setdefault("recent_history", []).append(
        "Public Era roster repair completed before Season 51."
    )

    repair_log.append("")
    repair_log.append(f"Remaining Free Agents: {len(free_agents)}")

    return snapshot, repair_log


def validate_repaired_public_era_snapshot(snapshot):
    errors = []

    teams = snapshot.get("teams", {})

    if len(teams) != 16:
        errors.append(f"Expected 16 teams, found {len(teams)}.")

    all_player_ids = []

    for team_name, team in teams.items():
        roster = team.get("roster", [])
        roster_count = team.get("roster_count", len(roster))

        if roster_count != len(roster):
            errors.append(
                f"{team_name} roster_count mismatch: {roster_count} vs {len(roster)}."
            )

        if len(roster) < PUBLIC_ERA_REPAIR_TARGET_ROSTER_SIZE:
            errors.append(
                f"{team_name} has {len(roster)} players after repair; "
                f"expected at least {PUBLIC_ERA_REPAIR_TARGET_ROSTER_SIZE}."
            )

        for player in roster:
            all_player_ids.append(player.get("player_id"))

            if player.get("team") != team_name:
                errors.append(
                    f"{team_name} roster/team mismatch for {player.get('name')}: "
                    f"{player.get('team')}"
                )

    if len(all_player_ids) != len(set(all_player_ids)):
        errors.append("Duplicate player IDs detected after Public Era roster repair.")

    if errors:
        print("PUBLIC ERA ROSTER REPAIR VALIDATION: FAILED")
        for error in errors:
            print(f"- {error}")
        raise SystemExit(1)

    print("PUBLIC ERA ROSTER REPAIR VALIDATION: PASS")


def save_repaired_public_era_snapshot(snapshot, repair_log):
    import json
    from pathlib import Path

    Path(PUBLIC_ERA_REPAIRED_SNAPSHOT_FILE).write_text(
        json.dumps(snapshot, indent=2, default=str),
        encoding="utf-8"
    )

    # Also overwrite main snapshot so normal resume uses the repaired Season 51 state.
    Path(PUBLIC_ERA_SNAPSHOT_FILE).write_text(
        json.dumps(snapshot, indent=2, default=str),
        encoding="utf-8"
    )

    Path(PUBLIC_ERA_REPAIR_LOG_FILE).write_text(
        "\n".join(repair_log) + "\n",
        encoding="utf-8"
    )


def main_public_era_roster_repair():
    snapshot = load_public_era_snapshot()
    validate_public_era_snapshot_structure(snapshot)

    repaired_snapshot, repair_log = repair_public_era_snapshot_rosters(snapshot)
    validate_repaired_public_era_snapshot(repaired_snapshot)
    save_repaired_public_era_snapshot(repaired_snapshot, repair_log)

    print("\n============================================")
    print("PUBLIC ERA ROSTER REPAIR SUMMARY")
    print("============================================")

    for line in repair_log:
        print(line)

    print("")
    print(f"Saved: {PUBLIC_ERA_REPAIRED_SNAPSHOT_FILE}")
    print(f"Updated: {PUBLIC_ERA_SNAPSHOT_FILE}")
    print(f"Log: {PUBLIC_ERA_REPAIR_LOG_FILE}")
    print("============================================\n")


# PUBLIC ERA SNAPSHOT RESUME MODE
# ============================================================

PUBLIC_ERA_SNAPSHOT_FILE = "public_era_snapshot.json"


def load_public_era_snapshot(path=PUBLIC_ERA_SNAPSHOT_FILE):
    import json
    from pathlib import Path

    snapshot_path = Path(path)

    if not snapshot_path.exists():
        raise FileNotFoundError(
            f"Missing Public Era snapshot file: {path}. "
            f"Run full Genesis export first."
        )

    return json.loads(snapshot_path.read_text(encoding="utf-8"))


def validate_public_era_snapshot_structure(snapshot):
    errors = []

    required_top_keys = [
        "league",
        "counts",
        "championship_ledger",
        "teams",
        "top_active_players",
        "season_summaries",
        "award_history",
    ]

    for key in required_top_keys:
        if key not in snapshot:
            errors.append(f"Snapshot missing top-level key: {key}")

    league = snapshot.get("league", {})
    counts = snapshot.get("counts", {})
    teams = snapshot.get("teams", {})

    if league.get("current_year") != league.get("public_era_start_year"):
        errors.append(
            f"Snapshot current_year/public_era_start_year mismatch: "
            f"{league.get('current_year')} vs {league.get('public_era_start_year')}"
        )

    if league.get("current_year") != 51:
        errors.append(f"Expected Public Era current year 51, found {league.get('current_year')}.")

    if counts.get("teams") != 16:
        errors.append(f"Expected 16 teams in snapshot counts, found {counts.get('teams')}.")

    if len(teams) != 16:
        errors.append(f"Expected 16 teams in teams object, found {len(teams)}.")

    if not league.get("season_mvp_award_name"):
        errors.append("Snapshot missing season MVP award name.")

    if league.get("season_mvp_award_name") != "Tyrese King Jr. Season MVP Award":
        errors.append(
            f"Expected Tyrese King Jr. Season MVP Award, found {league.get('season_mvp_award_name')}."
        )

    if league.get("playoff_mvp_award_name") != "Kanomi Jones Playoff MVP":
        errors.append(
            f"Expected Kanomi Jones Playoff MVP, found {league.get('playoff_mvp_award_name')}."
        )

    if not snapshot.get("championship_ledger"):
        errors.append("Snapshot championship ledger is empty.")

    if not snapshot.get("top_active_players"):
        errors.append("Snapshot top active players list is empty.")

    if not snapshot.get("season_summaries"):
        errors.append("Snapshot season summaries list is empty.")

    if errors:
        print("PUBLIC ERA SNAPSHOT VALIDATION: FAILED")
        for error in errors:
            print(f"- {error}")
        raise SystemExit(1)

    print("PUBLIC ERA SNAPSHOT VALIDATION: PASS")


def print_public_era_resume_summary(snapshot):
    league = snapshot["league"]
    counts = snapshot["counts"]
    teams = snapshot["teams"]

    print("\n============================================")
    print("PUBLIC ERA RESUME SUMMARY")
    print("============================================")
    print(f"League: {league.get('name')}")
    print(f"Current Year: {league.get('current_year')}")
    print(f"Public Era Begins: Season {league.get('public_era_start_year')}")
    print(f"Teams: {counts.get('teams')}")
    print(f"Player Pool: {counts.get('player_pool')}")
    print(f"Active Rostered Players: {counts.get('active_rostered_players')}")
    print(f"Free Agents: {counts.get('free_agents')}")
    print(f"History Events: {counts.get('history_events')}")
    print(f"Season Summaries: {counts.get('season_summaries')}")
    print(f"Season MVP Award: {league.get('season_mvp_award_name')}")
    print(f"Playoff MVP Award: {league.get('playoff_mvp_award_name')}")

    print("\nChampionship Ledger:")
    for line in snapshot.get("championship_ledger", []):
        print(f"- {line}")

    print("\nTop 25 Active Players Entering Public Era:")
    for rank, player in enumerate(snapshot.get("top_active_players", [])[:25], start=1):
        print(
            f"{rank}. {player.get('name')} | {player.get('team')} | "
            f"{player.get('position')} | Age {player.get('age')} | "
            f"{player.get('tier')} | OVR {player.get('overall')} | "
            f"POT {player.get('potential')} | Value {player.get('value_score')}"
        )

    print("\nTeam Roster Counts:")
    for team_name, team in teams.items():
        print(
            f"- {team_name}: {team.get('roster_count')} players | "
            f"Titles {team.get('championships')} | "
            f"Record {team.get('record', {}).get('wins')}-{team.get('record', {}).get('losses')}"
        )

    print("\nRecent Season Summaries:")
    for summary in snapshot.get("season_summaries", [])[-5:]:
        print(f"- {summary}")

    print("============================================\n")


def main_public_era_resume():
    snapshot = load_public_era_snapshot()
    validate_public_era_snapshot_structure(snapshot)
    print_public_era_resume_summary(snapshot)


# ============================================================
# MAIN ENTRY POINT
# ============================================================

def main() -> None:
    random.seed(1)

    league = build_league()

    apply_foundation_owner_and_market_profiles(league)
    load_foundation_institutional_pools(league)
    enrich_foundation_players(league.player_pool)

    validate_league_foundation(league)
    validate_foundation_pools(league)
    validate_owner_market_profiles(league)
    validate_foundation_institutional_pools(league)
    validate_enriched_players(league)

    print_league_summary(league)
    print_foundation_pool_summary(league)
    print_player_enrichment_summary(league)
    print_owner_market_summary(league)
    print_institutional_pool_summary(league)

    run_year_1_staff_setup(league)
    validate_year_1_staff_setup(league)
    print_staff_assignments(league)

    run_inaugural_draft(league, rounds=INITIAL_DRAFT_ROUNDS)
    validate_inaugural_draft(league, expected_roster_size=INITIAL_DRAFT_ROUNDS)
    print_inaugural_draft_summary(league)

    run_competitive_season(league, print_outputs=True)

    run_year_2_offseason(league)
    validate_year_2_offseason(league)
    print_year_2_offseason_summary(league)

    run_full_genesis_era(league, start_year=FULL_GENESIS_START_YEAR, end_year=FULL_GENESIS_END_YEAR)
    validate_genesis_test_loop(league, start_year=FULL_GENESIS_START_YEAR, end_year=FULL_GENESIS_END_YEAR)

    name_season_mvp_award_after_genesis_greatest(league)
    validate_season_mvp_legacy_name(league)
    print_season_mvp_legacy_summary(league)

    validate_public_era_readiness(league)
    print_genesis_test_loop_summary(league)
    print_public_era_readiness_summary(league)

    export_public_era_snapshot_v2(league)
    validate_public_era_export_v2()
    print_public_era_export_summary_v2()


if __name__ == "__main__":
    import sys

    if "--resume-public-era" in sys.argv and "--repair-rosters" in sys.argv:
        main_public_era_roster_repair()
    elif "--resume-public-era" in sys.argv:
        main_public_era_resume()
    else:
        main()

