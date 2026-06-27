"""A simple, self-contained Elo Monte-Carlo for the 2026 tournament.

Goals are modelled straight from the Elo gap (two Poisson scoring rates around a
league-average baseline), and the full 2026 format is simulated — 12 groups,
top-2 + 8 best thirds, then an Elo-seeded single-elimination bracket. Completed
group games can be held FIXED so the odds are conditioned on the current state.

This is the lightweight counterpart to the Bayesian ``simulate_tournament``; it
needs no posterior, so it is fast enough to run at many checkpoints (e.g. for a
title-odds timeline) and to re-run every matchday.
"""

from __future__ import annotations

import math
from collections import defaultdict

import numpy as np
import pandas as pd

from ..config import SEED
from .elo import HFA, win_probability

BASE_GOALS = 1.35       # league-average goals per side; the Elo gap tilts it
N_SIMS_DEFAULT = 8000


def elo_goals(elo_a: float, elo_b: float, neutral: bool = True) -> tuple[float, float]:
    """Map an Elo matchup to two expected scoring rates (a, b)."""
    d = (elo_a + (0.0 if neutral else HFA) - elo_b) / 400.0
    return BASE_GOALS * 10 ** (d / 4), BASE_GOALS * 10 ** (-d / 4)


def poisson_1x2(lam_a: float, lam_b: float, max_goals: int = 8) -> dict:
    """1X2 probabilities + most-likely scoreline from two independent Poissons."""
    fac = np.array([math.factorial(k) for k in range(max_goals + 1)])
    ga = np.exp(-lam_a) * lam_a ** np.arange(max_goals + 1) / fac
    gb = np.exp(-lam_b) * lam_b ** np.arange(max_goals + 1) / fac
    m = np.outer(ga, gb)
    i, j = np.unravel_index(m.argmax(), m.shape)
    return {"p_a": float(np.tril(m, -1).sum()), "p_draw": float(np.trace(m)),
            "p_b": float(np.triu(m, 1).sum()), "score": f"{i}-{j}"}


def simulate_champion(elo: dict, groups: dict, played: dict,
                      n_sims: int = 8000, seed: int = SEED) -> pd.DataFrame:
    """Simulate the rest of the tournament from the current state.

    ``played`` ({(home, away): (gh, ga)}) holds completed group games FIXED;
    only the remaining group games + the knockout bracket are rolled. Returns a
    per-team progression table (p_round32 ... p_champion).
    """
    teams = list(elo)
    idx = {t: i for i, t in enumerate(teams)}
    elo_arr = np.array([elo[t] for t in teams])
    rng = np.random.default_rng(seed)
    group_members = {g: [idx[t] for t in ts] for g, ts in groups.items()}
    fixtures = [(idx[a], idx[b]) for ts in groups.values()
                for k, a in enumerate(ts) for b in ts[k + 1:]]
    played_idx = {(idx[h], idx[a]): (gh, ga)
                  for (h, a), (gh, ga) in played.items() if h in idx and a in idx}

    stages = ["round32", "round16", "quarter", "semi", "final", "champion"]
    cnt = {s: np.zeros(len(teams)) for s in stages}

    for _ in range(n_sims):
        pts, gd, gf = defaultdict(int), defaultdict(int), defaultdict(int)
        for i, j in fixtures:
            res = played_idx.get((i, j)) or (
                tuple(reversed(played_idx[(j, i)])) if (j, i) in played_idx else None)
            if res is None:
                la, lb = elo_goals(elo_arr[i], elo_arr[j])
                gi, gj = rng.poisson(la), rng.poisson(lb)
            else:
                gi, gj = res
            gd[i] += gi - gj; gd[j] += gj - gi; gf[i] += gi; gf[j] += gj
            if gi > gj:
                pts[i] += 3
            elif gj > gi:
                pts[j] += 3
            else:
                pts[i] += 1; pts[j] += 1

        key = lambda t: (pts[t], gd[t], gf[t], rng.random())
        qualifiers, thirds = [], []
        for members in group_members.values():
            ordered = sorted(members, key=key, reverse=True)
            qualifiers.extend(ordered[:2]); thirds.append(ordered[2])
        qualifiers.extend(sorted(thirds, key=key, reverse=True)[:8])
        for t in qualifiers:
            cnt["round32"][t] += 1

        # Seed by Elo into a standard bracket; trim to nearest power of 2
        # (no-op for the real 32-team field).
        ranked = sorted(qualifiers, key=lambda k: elo_arr[k], reverse=True)
        ranked = ranked[:1 << (len(ranked).bit_length() - 1)] if ranked else ranked
        bracket, lo, hi = [], 0, len(ranked) - 1
        while lo <= hi:
            bracket.append(ranked[lo])
            if lo != hi:
                bracket.append(ranked[hi])
            lo += 1; hi -= 1

        # Name rounds from the END so the final winner is always "champion".
        rounds = (len(bracket)).bit_length() - 1
        cur = bracket
        for s in stages[1:][-rounds:]:
            nxt = []
            for k in range(0, len(cur), 2):
                a, b = cur[k], cur[k + 1]
                w = a if rng.random() < win_probability(elo_arr[a], elo_arr[b]) else b
                nxt.append(w); cnt[s][w] += 1
            cur = nxt
            if len(cur) == 1:
                break

    df = pd.DataFrame({"team": teams})
    for s in stages:
        df[f"p_{s}"] = cnt[s] / n_sims
    return df.sort_values("p_champion", ascending=False).reset_index(drop=True)
