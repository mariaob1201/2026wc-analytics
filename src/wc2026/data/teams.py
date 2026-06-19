"""The 48 teams and 12-group structure for the 2026 format.

Each team carries a ``latent_strength`` used ONLY by the synthetic data
generator to produce plausible match scores. The Bayesian model never sees it
-- recovering something close to it is how we sanity-check the model.

To go live with real data, replace this module's contents with the actual
drawn groups and drop the ``latent_strength`` column (or repurpose it as a
prior mean, e.g. from the FIFA/Elo ranking).
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Team:
    name: str
    code: str
    confederation: str
    group: str
    latent_strength: float  # ground-truth "skill", synthetic only


# Strength is on a log-rate scale (~ goals advantage). ~1.0 = elite, ~-0.8 = weak.
# Groups A-L (12 groups). Values are illustrative, not predictions.
TEAMS: list[Team] = [
    Team("Mexico", "MEX", "CONCACAF", "A", 0.35),
    Team("Netherlands", "NED", "UEFA", "A", 0.78),
    Team("Ghana", "GHA", "CAF", "A", 0.05),
    Team("Saudi Arabia", "KSA", "AFC", "A", -0.45),

    Team("Canada", "CAN", "CONCACAF", "B", 0.10),
    Team("Croatia", "CRO", "UEFA", "B", 0.62),
    Team("Ecuador", "ECU", "CONMEBOL", "B", 0.22),
    Team("Qatar", "QAT", "AFC", "B", -0.55),

    Team("United States", "USA", "CONCACAF", "C", 0.30),
    Team("Germany", "GER", "UEFA", "C", 0.85),
    Team("Japan", "JPN", "AFC", "C", 0.40),
    Team("Tunisia", "TUN", "CAF", "C", -0.30),

    Team("Argentina", "ARG", "CONMEBOL", "D", 1.05),
    Team("Poland", "POL", "UEFA", "D", 0.28),
    Team("South Korea", "KOR", "AFC", "D", 0.32),
    Team("Honduras", "HON", "CONCACAF", "D", -0.50),

    Team("France", "FRA", "UEFA", "E", 1.00),
    Team("Senegal", "SEN", "CAF", "E", 0.42),
    Team("Uruguay", "URU", "CONMEBOL", "E", 0.55),
    Team("Iran", "IRN", "AFC", "E", -0.20),

    Team("Brazil", "BRA", "CONMEBOL", "F", 0.98),
    Team("Switzerland", "SUI", "UEFA", "F", 0.45),
    Team("Cameroon", "CMR", "CAF", "F", 0.00),
    Team("New Zealand", "NZL", "OFC", "F", -0.70),

    Team("Spain", "ESP", "UEFA", "G", 0.92),
    Team("Morocco", "MAR", "CAF", "G", 0.50),
    Team("Australia", "AUS", "AFC", "G", 0.05),
    Team("Panama", "PAN", "CONCACAF", "G", -0.40),

    Team("England", "ENG", "UEFA", "H", 0.88),
    Team("Colombia", "COL", "CONMEBOL", "H", 0.52),
    Team("Egypt", "EGY", "CAF", "H", 0.08),
    Team("Jamaica", "JAM", "CONCACAF", "H", -0.45),

    Team("Portugal", "POR", "UEFA", "I", 0.90),
    Team("Mali", "MLI", "CAF", "I", 0.02),
    Team("Costa Rica", "CRC", "CONCACAF", "I", -0.25),
    Team("Iraq", "IRQ", "AFC", "I", -0.40),

    Team("Belgium", "BEL", "UEFA", "J", 0.70),
    Team("Nigeria", "NGA", "CAF", "J", 0.30),
    Team("Peru", "PER", "CONMEBOL", "J", 0.10),
    Team("Uzbekistan", "UZB", "AFC", "J", -0.35),

    Team("Italy", "ITA", "UEFA", "K", 0.75),
    Team("Ivory Coast", "CIV", "CAF", "K", 0.25),
    Team("Paraguay", "PAR", "CONMEBOL", "K", 0.05),
    Team("Norway", "NOR", "UEFA", "K", 0.48),

    Team("Denmark", "DEN", "UEFA", "L", 0.58),
    Team("Algeria", "ALG", "CAF", "L", 0.18),
    Team("Chile", "CHI", "CONMEBOL", "L", 0.20),
    Team("South Africa", "RSA", "CAF", "L", -0.30),
]

GROUPS: list[str] = sorted({t.group for t in TEAMS})


def team_index() -> dict[str, int]:
    """Stable name -> integer id mapping (used to index model parameters)."""
    return {t.name: i for i, t in enumerate(TEAMS)}


def by_group() -> dict[str, list[Team]]:
    out: dict[str, list[Team]] = {g: [] for g in GROUPS}
    for t in TEAMS:
        out[t.group].append(t)
    return out


assert len(TEAMS) == 48, "2026 World Cup has 48 teams"
assert all(len(v) == 4 for v in by_group().values()), "12 groups of 4"
