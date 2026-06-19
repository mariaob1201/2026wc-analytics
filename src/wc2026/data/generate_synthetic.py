"""Generate realistic synthetic inputs so the whole pipeline runs offline.

Three tables are produced:

1. ``players.csv``  -- one row per player (squad of 26 x 48 teams). Carries raw
   attributes from which features are later engineered: birth/debut years,
   position, per-skill ratings, market value, and social-media following.
2. ``matches.csv``  -- historical results (qualifiers + friendlies) generated
   from each team's latent strength via a Poisson scoring process. This is what
   the Bayesian model is fit on.
3. ``fixtures.csv`` -- the 2026 group-stage schedule (every pair within a group).

Each generator is a thin, well-isolated function. To swap in REAL data, replace
the body of the relevant function with an API/CSV adapter that returns the same
columns -- nothing downstream needs to change.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from ..config import N_HISTORICAL_MATCHES, SEED, SQUAD_SIZE
from .teams import TEAMS, Team, by_group

POSITIONS = ["GK", "DF", "MF", "FW"]
# Rough share of a 26-man squad by position.
POSITION_WEIGHTS = np.array([0.12, 0.35, 0.31, 0.22])
SKILLS = ["pace", "shooting", "passing", "dribbling", "defending", "physical"]

# Social following scales steeply with stardom; we model log10(followers).
# A bench player ~ 4.5 (30k), a global superstar ~ 8.5 (300M).


def _rng(offset: int = 0) -> np.random.Generator:
    return np.random.default_rng(SEED + offset)


def generate_players() -> pd.DataFrame:
    """One row per player across all 48 squads."""
    rng = _rng(1)
    rows: list[dict] = []
    pid = 0
    for team in TEAMS:
        # A team's latent strength biases its players' skill distribution.
        team_skill_mean = 65 + 12 * team.latent_strength  # 0-100 FIFA-like scale

        n_pos = np.random.default_rng(SEED + 100 + hash(team.code) % 1000)
        counts = np.maximum(1, np.round(POSITION_WEIGHTS * SQUAD_SIZE)).astype(int)
        # Force the counts to sum to SQUAD_SIZE.
        while counts.sum() != SQUAD_SIZE:
            counts[counts.argmax()] += int(np.sign(SQUAD_SIZE - counts.sum()))
        positions = np.repeat(POSITIONS, counts)

        for pos in positions:
            age = int(np.clip(rng.normal(27, 3.5), 18, 39))
            debut_age = int(np.clip(rng.normal(20, 2.0), 16, 26))
            # Longevity proxies: career length so far + caps.
            career_years = max(1, age - debut_age)
            caps = int(np.clip(rng.poisson(career_years * 6), 1, 180))

            # Per-skill ratings centred on the team mean, with positional tilt.
            base = rng.normal(team_skill_mean, 6, size=len(SKILLS))
            tilt = _positional_tilt(pos)
            ratings = np.clip(base + tilt, 35, 99)
            overall = float(ratings.mean())

            # Market value (EUR) rises with overall and falls with age past peak.
            age_factor = np.exp(-((age - 25) ** 2) / 120)
            market_value = float(
                np.clip(rng.lognormal(mean=0, sigma=0.4) *
                        (overall / 70) ** 6 * 8e6 * age_factor, 2e5, 2e8)
            )

            # Social following: superstars (high overall) skew hard right.
            star = (overall - 70) / 10
            log_followers = np.clip(rng.normal(5.2 + 0.9 * star, 0.7), 3.5, 8.7)
            followers = int(10 ** log_followers)
            # Engagement rate tends to fall as following grows.
            engagement = float(np.clip(rng.normal(0.06 - 0.004 * log_followers, 0.01),
                                       0.002, 0.12))

            rows.append({
                "player_id": pid,
                "team": team.name,
                "team_code": team.code,
                "position": pos,
                "age": age,
                "debut_age": debut_age,
                "career_years": career_years,
                "caps": caps,
                "overall": round(overall, 1),
                **{f"skill_{s}": round(float(r), 1) for s, r in zip(SKILLS, ratings)},
                "market_value_eur": round(market_value),
                "followers": followers,
                "engagement_rate": round(engagement, 4),
            })
            pid += 1
    return pd.DataFrame(rows)


def _positional_tilt(pos: str) -> np.ndarray:
    """Add/subtract from each skill depending on position."""
    # order: pace, shooting, passing, dribbling, defending, physical
    table = {
        "GK": [-8, -20, -2, -10, 6, 4],
        "DF": [0, -8, 0, -4, 12, 8],
        "MF": [2, 2, 10, 6, 2, 0],
        "FW": [8, 12, 2, 10, -10, 0],
    }
    return np.array(table[pos], dtype=float)


def generate_matches() -> pd.DataFrame:
    """Historical results generated from latent strengths (Poisson goals)."""
    rng = _rng(2)
    strength = {t.name: t.latent_strength for t in TEAMS}
    intercept = 0.15      # baseline log goal rate (~1.16 goals)
    home_adv = 0.25       # home/designated-home advantage on log scale
    names = [t.name for t in TEAMS]

    rows = []
    for m in range(N_HISTORICAL_MATCHES):
        h, a = rng.choice(names, size=2, replace=False)
        lam_h = np.exp(intercept + home_adv + strength[h] - strength[a])
        lam_a = np.exp(intercept + strength[a] - strength[h])
        gh, ga = rng.poisson(lam_h), rng.poisson(lam_a)
        rows.append({
            "match_id": m,
            "home_team": h,
            "away_team": a,
            "home_goals": int(gh),
            "away_goals": int(ga),
        })
    return pd.DataFrame(rows)


def generate_fixtures() -> pd.DataFrame:
    """Group-stage schedule: round-robin within each group of 4 (6 games/group)."""
    rows = []
    fid = 0
    for group, teams in by_group().items():
        for i in range(len(teams)):
            for j in range(i + 1, len(teams)):
                rows.append({
                    "fixture_id": fid,
                    "group": group,
                    "home_team": teams[i].name,
                    "away_team": teams[j].name,
                })
                fid += 1
    return pd.DataFrame(rows)
