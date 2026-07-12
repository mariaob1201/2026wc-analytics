"""Stage 30: daily Gaussian goal-difference forecast.

The script version of `notebooks/goal_difference_gaussian.ipynb`, built to run in
the daily pipeline. It pulls the most recent results, refits a simple Bayesian
**Gaussian model of the signed goal difference** (home - away), and forecasts the
next unplayed fixtures.

    goal_diff ~ Normal(mu, sigma),  mu = home_adv + strength[home] - strength[away]
    strength  = beta_prior * prior_strength + tau * s_raw   (player-informed prior)

Publishes docs/GOAL_DIFF_FORECAST.md and data/processed/goal_diff_forecast.csv.

    python scripts/30_gaussian_goal_diff.py
"""

import numpy as np
import pandas as pd
import pymc as pm
import arviz as az

from wc2026.config import PROCESSED, ROOT, SEED, ensure_dirs
from wc2026.config import today as _today
from wc2026.data.sources import build_real_matches, wc2026_matches

TODAY = _today()


def _load_prior(teams: list[str]) -> np.ndarray:
    """Per-team squad prior_strength, aligned to `teams`, standardized, 0-filled."""
    try:
        pf = pd.read_csv(PROCESSED / "team_features_real.csv").set_index("team")["prior_strength"]
        prior = pf.reindex(teams).fillna(0.0).to_numpy()
        sd = prior.std()
        return (prior - prior.mean()) / sd if sd > 0 else prior * 0.0
    except Exception:
        return np.zeros(len(teams))


def main() -> None:
    ensure_dirs()

    # --- 1. Pull the most recent results ---
    matches = build_real_matches(start="2022-01-01", end=TODAY)
    teams = sorted(set(matches["home_team"]) | set(matches["away_team"]))
    team_idx = {t: i for i, t in enumerate(teams)}
    n_teams = len(teams)
    home_i = matches["home_team"].map(team_idx).to_numpy()
    away_i = matches["away_team"].map(team_idx).to_numpy()
    y = (matches["home_goals"] - matches["away_goals"]).to_numpy().astype(float)
    prior_z = _load_prior(teams)

    # --- 2. Fit the player-informed Gaussian goal-difference model ---
    with pm.Model():
        beta_prior = pm.Normal("beta_prior", 0.0, 1.0)
        tau = pm.HalfNormal("tau", 1.0)
        s_raw = pm.Normal("s_raw", 0.0, 1.0, shape=n_teams)
        strength = pm.Deterministic("strength", beta_prior * prior_z + tau * s_raw)
        home_adv = pm.Normal("home_adv", 0.3, 0.5)
        sigma = pm.HalfNormal("sigma", 3.0)
        mu = home_adv + strength[home_i] - strength[away_i]
        pm.Normal("obs", mu=mu, sigma=sigma, observed=y)
        idata = pm.sample(1000, tune=1000, chains=4, target_accept=0.9,
                          random_seed=SEED, progressbar=False)

    post = idata.posterior
    st = post["strength"].stack(s=("chain", "draw")).to_numpy()
    ha = post["home_adv"].stack(s=("chain", "draw")).to_numpy()
    sg = post["sigma"].stack(s=("chain", "draw")).to_numpy()
    beta = float(post["beta_prior"].mean())
    strength_mean = st.mean(axis=1)

    def forecast(home: str, away: str, neutral: bool = True, seed: int = 0) -> dict:
        mu = (0.0 if neutral else ha) + st[team_idx[home]] - st[team_idx[away]]
        rng = np.random.default_rng(seed)
        diff = mu + sg * rng.standard_normal(mu.shape)
        return {"exp_margin": round(float(diff.mean()), 2),
                "p_home": round(float((diff > 0.5).mean()), 2),
                "p_draw": round(float((np.abs(diff) <= 0.5).mean()), 2),
                "p_away": round(float((diff < -0.5).mean()), 2)}

    # --- 3. Forecast the next unplayed fixtures ---
    wc = wc2026_matches()
    upcoming = wc[wc["home_score"].isna() & (wc["date"] >= TODAY)].sort_values("date")
    rows = []
    for r in upcoming.itertuples():
        if r.home not in team_idx or r.away not in team_idx:
            continue
        f = forecast(r.home, r.away, neutral=True)
        rows.append({"date": str(r.date.date()), "home": r.home, "away": r.away, **f})
    fc = pd.DataFrame(rows)
    fc.to_csv(PROCESSED / "goal_diff_forecast.csv", index=False)

    # --- 4. Publish the report ---
    md = _render(fc, beta, teams, strength_mean, len(matches))
    out = ROOT / "docs" / "GOAL_DIFF_FORECAST.md"
    out.write_text(md)

    print(f"Fit on {len(matches)} matches to {TODAY}; beta_prior={beta:.2f}")
    if len(fc):
        print(fc.to_string(index=False))
    else:
        print("No upcoming fixtures in the feed.")
    print(f"saved -> {out}, goal_diff_forecast.csv")


def _pct(x):
    return f"{100*x:.0f}%"


def _render(fc, beta, teams, strength_mean, n_matches) -> str:
    ranking = (pd.DataFrame({"team": teams, "strength": strength_mean})
               .sort_values("strength", ascending=False).reset_index(drop=True))
    L = ["# Goal-difference forecast (Gaussian model)\n",
         f"_A simple Bayesian model of the **signed goal difference** "
         f"(home - away): `goal_diff ~ Normal(mu, sigma)`, "
         f"`mu = home_adv + strength[home] - strength[away]`, with a "
         f"player-informed prior on strength. Refit daily on the latest results. "
         f"Fit on **{n_matches} matches** through {TODAY}._\n",
         f"_Player-data weight `beta_prior` = **{beta:.2f}** "
         "(how much the model leans on squad ratings vs. results).\n"]

    L.append("## Next games — predicted margin & outcome\n")
    if fc.empty:
        L.append("_No upcoming fixtures in the feed right now._\n")
    else:
        L.append("_`E[margin]` = expected goal difference (sign = favourite). "
                 "Probabilities are from the posterior-predictive margin._\n")
        L.append("| Date | Fixture | E[margin] | P(home) | P(draw) | P(away) |")
        L.append("|---|---|--:|--:|--:|--:|")
        for r in fc.itertuples():
            L.append(f"| {r.date} | {r.home} v {r.away} | {r.exp_margin:+.2f} | "
                     f"{_pct(r.p_home)} | {_pct(r.p_draw)} | {_pct(r.p_away)} |")

    L.append("\n## Team strength (posterior mean, top 12)\n")
    L.append("| # | Team | strength |")
    L.append("|--:|---|--:|")
    for i, r in enumerate(ranking.head(12).itertuples(), 1):
        L.append(f"| {i} | {r.team} | {r.strength:+.2f} |")

    L.append("\n## Method\n")
    L.append("- **Target:** the signed goal difference — its sign is the result "
             "(negative = away won), modelled with a **Gaussian**.")
    L.append("- **Strength prior:** `strength = beta_prior * prior_strength + "
             "residual`; `prior_strength` is the squad rating built from player "
             "attributes, and `beta_prior` is learned. See "
             "[notebooks/goal_difference_gaussian.ipynb](../notebooks/goal_difference_gaussian.ipynb) "
             "for the full teaching walkthrough.")
    L.append("- **Simpler cousin** of the production Poisson scoreline model "
             "([CHAMPION_TRACKER.md](CHAMPION_TRACKER.md)); it forecasts the "
             "*margin* rather than full scorelines.")
    L.append(f"\n_Updated {TODAY} by the daily tracker._")
    return "\n".join(L)


if __name__ == "__main__":
    main()
