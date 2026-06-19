"""Fast smoke tests: data shapes, features, and a tiny end-to-end model fit.

These run in seconds (a deliberately tiny sampler) so CI can catch breakage
without waiting for a full inference run.
"""

import numpy as np

from wc2026.data.generate_synthetic import (
    generate_fixtures,
    generate_matches,
    generate_players,
)
from wc2026.data.teams import TEAMS, by_group
from wc2026.features.player_features import add_player_features, build_team_features


def test_team_structure():
    assert len(TEAMS) == 48
    assert all(len(v) == 4 for v in by_group().values())


def test_synthetic_shapes():
    players = generate_players()
    assert len(players) == 48 * 26
    assert players["followers"].min() > 0

    fixtures = generate_fixtures()
    assert len(fixtures) == 12 * 6  # 6 games per group

    matches = generate_matches()
    assert {"home_team", "away_team", "home_goals", "away_goals"} <= set(matches.columns)
    assert (matches["home_goals"] >= 0).all()


def test_features():
    players = generate_players()
    feat = add_player_features(players)
    for col in ["longevity", "skill_index", "social_score"]:
        assert col in feat.columns
    team = build_team_features(feat)
    assert len(team) == 48
    assert np.isfinite(team["prior_strength"]).all()


def test_model_fits_tiny():
    """A minimal NUTS run just to prove the model compiles and samples."""
    import pymc as pm  # imported here so non-model tests don't pay the cost

    from wc2026.models.bayesian_score import build_model, posterior_strength_table
    from wc2026.models.bayesian_score import FitResult

    matches = generate_matches().head(200)
    teams = [t.name for t in TEAMS]
    model = build_model(matches, teams, prior_strength=np.zeros(len(teams)))
    with model:
        idata = pm.sample(draws=50, tune=50, chains=2, cores=1,
                          progressbar=False, random_seed=1)
    fr = FitResult(idata=idata, teams=teams,
                   team_to_idx={t: i for i, t in enumerate(teams)})
    strength = posterior_strength_table(fr)
    assert len(strength) == 48
