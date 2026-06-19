"""Turn raw player rows into the features the user asked for and roll them up
to a single per-team covariate that the Bayesian model can use as prior info.

Per-player features
-------------------
* longevity   -- experience: blends career length and international caps.
* position    -- kept categorical; also one-hot encoded for modelling.
* skill_index -- weighted blend of the six skill ratings.
* social_score-- log-following x engagement (a "reach x stickiness" proxy).

Team rollup
-----------
We aggregate players into ``team_features.csv`` with one row per nation, then
combine the columns into a single standardized ``prior_strength`` number. That
number is fed to the model as the *mean of the prior* on each team's attacking
ability -- so your player/social analytics literally inform the prediction,
while the match data is still allowed to override it.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

SKILL_COLS = [
    "skill_pace", "skill_shooting", "skill_passing",
    "skill_dribbling", "skill_defending", "skill_physical",
]

# Weights for a single attacking-leaning skill index (sums to 1).
SKILL_WEIGHTS = {
    "skill_pace": 0.15,
    "skill_shooting": 0.25,
    "skill_passing": 0.20,
    "skill_dribbling": 0.20,
    "skill_defending": 0.10,
    "skill_physical": 0.10,
}


def add_player_features(players: pd.DataFrame) -> pd.DataFrame:
    """Return a copy of ``players`` with engineered per-player feature columns."""
    df = players.copy()

    # Longevity: standardized career length + standardized caps, averaged.
    df["longevity"] = (_z(df["career_years"]) + _z(df["caps"])) / 2

    # Skill index: weighted blend of the six ratings (already 35-99 scale).
    df["skill_index"] = sum(df[col] * w for col, w in SKILL_WEIGHTS.items())

    # Social score: reach (log10 followers) modulated by engagement, standardized.
    df["log_followers"] = np.log10(df["followers"].clip(lower=1))
    df["social_score"] = _z(df["log_followers"] * (1 + df["engagement_rate"]))

    # Position one-hots (handy for downstream per-position analysis).
    pos_dummies = pd.get_dummies(df["position"], prefix="pos").astype(int)
    df = pd.concat([df, pos_dummies], axis=1)

    return df


def build_team_features(players_feat: pd.DataFrame) -> pd.DataFrame:
    """Aggregate player features to one row per team and derive prior_strength."""
    # Use the squad's strongest 16 by overall -- a nation is carried by its best,
    # not its bench. (mean of top-N is more discriminating than a flat mean.)
    def top_n_mean(g: pd.DataFrame, col: str, n: int = 16) -> float:
        return g.nlargest(n, "overall")[col].mean()

    grouped = players_feat.groupby(["team", "team_code"], sort=False)
    rows = []
    for (team, code), g in grouped:
        rows.append({
            "team": team,
            "team_code": code,
            "squad_overall": top_n_mean(g, "overall"),
            "skill_index": top_n_mean(g, "skill_index"),
            "longevity": g["longevity"].mean(),
            "social_score": g["social_score"].mean(),
            "squad_market_value_eur": g["market_value_eur"].sum(),
            "star_power": g["social_score"].max(),  # single biggest name
        })
    team_df = pd.DataFrame(rows)

    # Combine standardized signals into one prior-strength covariate.
    # Skill carries most weight; experience and star power add smaller nudges.
    composite = (
        0.70 * _z(team_df["skill_index"])
        + 0.15 * _z(team_df["longevity"])
        + 0.10 * _z(np.log10(team_df["squad_market_value_eur"]))
        + 0.05 * _z(team_df["star_power"])
    )
    # Scale to roughly the log-goal-rate range the model works in (~[-1, 1]).
    team_df["prior_strength"] = _z(composite) * 0.5
    return team_df


def _z(s: pd.Series) -> pd.Series:
    """Standardize to mean 0, sd 1 (guards against zero variance)."""
    sd = s.std(ddof=0)
    return (s - s.mean()) / sd if sd > 0 else s * 0.0
