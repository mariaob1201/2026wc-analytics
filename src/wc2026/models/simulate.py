"""Monte-Carlo simulation of the 2026 tournament from the fitted posterior.

The Bayesian payoff
-------------------
Instead of plugging in a single "best guess" of each team's strength, we draw a
WHOLE PARAMETER SET from the posterior on every simulated tournament. Some
tournaments use a draw where, say, Brazil looks elite; others use a draw where
Brazil is merely good. Aggregating thousands of these tournaments propagates
*parameter uncertainty* into the final win probabilities -- the headline number
("Team X wins with p%") already accounts for how unsure we are about strengths.

Format implemented (2026)
--------------------------
* 12 groups of 4, round-robin (3 pts win / 1 draw).
* Group ranking by points, then goal difference, then goals for, then a coin
  flip (tie-break randomness).
* Top 2 of each group (24) + 8 best third-placed teams -> Round of 32.
* Single-elimination R32 -> R16 -> QF -> SF -> Final. Draws in knockout go to a
  near-coin-flip shootout, very slightly favouring the stronger side.

Note: the exact official R32 pairing map is intricate; we seed qualifiers by
posterior net strength into a standard bracket. Swap ``_seed_bracket`` for the
official crossing table once the draw is known.
"""

from __future__ import annotations

from collections import defaultdict

import numpy as np
import pandas as pd

from ..config import SEED
from .bayesian_score import FitResult


def _draw_params(fit: FitResult, rng: np.random.Generator):
    """Pull one posterior sample of all parameters."""
    post = fit.idata.posterior
    n_chain = post.sizes["chain"]
    n_draw = post.sizes["draw"]
    c = rng.integers(n_chain)
    d = rng.integers(n_draw)
    return {
        "intercept": float(post["intercept"][c, d]),
        "home_adv": float(post["home_adv"][c, d]),
        "att": post["att_eff"][c, d].to_numpy(),
        "deff": post["def"][c, d].to_numpy(),
    }


def _score(params, i: int, j: int, rng, neutral: bool = True):
    """Simulate one match's goals between team idx i (home) and j (away)."""
    # Group/knockout games at a World Cup are on neutral grounds, so no home
    # advantage unless a host is playing (left as an exercise / data flag).
    ha = 0.0 if neutral else params["home_adv"]
    lam_i = np.exp(params["intercept"] + ha + params["att"][i] - params["deff"][j])
    lam_j = np.exp(params["intercept"] + params["att"][j] - params["deff"][i])
    return rng.poisson(lam_i), rng.poisson(lam_j)


def _knockout_winner(params, i, j, rng):
    gi, gj = _score(params, i, j, rng)
    if gi > gj:
        return i
    if gj > gi:
        return j
    # Shootout: near coin flip, slight edge to stronger net strength.
    net = (params["att"] + params["deff"])
    p_i = 1 / (1 + np.exp(-0.3 * (net[i] - net[j])))
    return i if rng.random() < p_i else j


def _seed_bracket(qualifier_idxs: list[int], net: np.ndarray) -> list[int]:
    """Order 32 qualifiers into a standard 1-v-32 seeding."""
    ranked = sorted(qualifier_idxs, key=lambda k: net[k], reverse=True)
    # Standard seeding pairs: 1-32, 16-17, 8-25, ... we just interleave so the
    # top seed meets the bottom seed in round one.
    bracket = []
    lo, hi = 0, len(ranked) - 1
    while lo <= hi:
        bracket.append(ranked[lo])
        if lo != hi:
            bracket.append(ranked[hi])
        lo += 1
        hi -= 1
    return bracket


def simulate_tournament(fit: FitResult, fixtures: pd.DataFrame,
                        groups: dict[str, list[str]], n_sims: int = 5000,
                        shifts: dict | None = None,
                        played: dict | None = None) -> pd.DataFrame:
    """Run ``n_sims`` tournaments; return per-team progression probabilities.

    ``shifts`` (team name -> log-rate nudge) optionally folds current form /
    sentiment into every simulated match, so championship odds reflect momentum.

    ``played`` ({(home, away): (gh, ga)}) holds already-completed group matches
    FIXED and simulates only the remaining fixtures — so the odds are conditioned
    on the actual current state of the tournament, not re-rolled from scratch.
    """
    rng = np.random.default_rng(SEED)
    idx = fit.team_to_idx
    teams = fit.teams
    shift_arr = np.array([(shifts or {}).get(t, 0.0) for t in teams])

    # Already-played group results to hold FIXED (current-state conditioning):
    # {(home_name, away_name): (home_goals, away_goals)} -> indexed.
    played_idx = {(idx[h], idx[a]): (int(gh), int(ga))
                  for (h, a), (gh, ga) in (played or {}).items()
                  if h in idx and a in idx}

    # Pre-index group memberships.
    group_members = {g: [idx[t] for t in ts] for g, ts in groups.items()}
    fix = [(idx[r.home_team], idx[r.away_team], r.group)
           for r in fixtures.itertuples()]

    counters = {
        "round32": np.zeros(len(teams)),
        "round16": np.zeros(len(teams)),
        "quarter": np.zeros(len(teams)),
        "semi": np.zeros(len(teams)),
        "final": np.zeros(len(teams)),
        "champion": np.zeros(len(teams)),
    }

    for _ in range(n_sims):
        p = _draw_params(fit, rng)
        p["att"] = p["att"] + shift_arr      # fold in momentum/sentiment
        net = p["att"] + p["deff"]

        # --- Group stage ---
        pts = defaultdict(int)
        gd = defaultdict(int)
        gf = defaultdict(int)
        for i, j, _g in fix:
            # Hold completed matches fixed (either orientation); simulate the rest.
            res = played_idx.get((i, j))
            if res is None and (j, i) in played_idx:
                gj_act, gi_act = played_idx[(j, i)]
                res = (gi_act, gj_act)
            gi, gj = res if res is not None else _score(p, i, j, rng)
            gd[i] += gi - gj
            gd[j] += gj - gi
            gf[i] += gi
            gf[j] += gj
            if gi > gj:
                pts[i] += 3
            elif gj > gi:
                pts[j] += 3
            else:
                pts[i] += 1
                pts[j] += 1

        def rank_key(t):
            return (pts[t], gd[t], gf[t], rng.random())

        qualifiers: list[int] = []
        thirds: list[int] = []
        for g, members in group_members.items():
            ordered = sorted(members, key=rank_key, reverse=True)
            qualifiers.extend(ordered[:2])
            thirds.append(ordered[2])
        # 8 best third-placed teams.
        thirds_sorted = sorted(thirds, key=rank_key, reverse=True)
        qualifiers.extend(thirds_sorted[:8])

        for t in qualifiers:
            counters["round32"][t] += 1

        # --- Knockout ---
        bracket = _seed_bracket(qualifiers, net)
        round_names = ["round16", "quarter", "semi", "final", "champion"]
        current = bracket
        for rname in round_names:
            winners = []
            for k in range(0, len(current), 2):
                w = _knockout_winner(p, current[k], current[k + 1], rng)
                winners.append(w)
                counters[rname][w] += 1
            current = winners
            if len(current) == 1:
                break

    df = pd.DataFrame({"team": teams})
    for stage, arr in counters.items():
        df[f"p_{stage}"] = arr / n_sims
    return df.sort_values("p_champion", ascending=False).reset_index(drop=True)
