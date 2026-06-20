"""Stage 21: backtest the xG model vs the goals model on the same matches.

Decision rule (per the project's evaluation philosophy): keep the xG variant
only if it lowers RPS vs the goals model on held-out matches.

Data: needs an xG-labelled table at data/raw/xg_matches.csv with columns
  date, home_team, away_team, home_goals, away_goals, home_xg, away_xg
(harvest via FBref match reports or StatsBomb open data — see data/fbref.py).

    python scripts/21_xg_backtest.py            # real comparison (needs the CSV)
    python scripts/21_xg_backtest.py --demo     # synthetic sanity check (no data)

Honest note: a large-sample real comparison needs xG for many *training*
matches, which isn't cheaply scrapeable in this environment — so by default this
runs only when you've supplied the CSV. --demo proves the machinery on synthetic
data (NOT a real-world result).
"""

import argparse

import numpy as np
import pandas as pd
import pymc as pm

from wc2026.config import RAW
from wc2026.data.fbref import load_xg_csv
from wc2026.models.bayesian_score import build_model, build_xg_model, predict_match
from wc2026.models.metrics import evaluate


def _fit(builder, train, teams):
    with builder(train, teams, prior_strength=np.zeros(len(teams))):
        return pm.sample(draws=600, tune=600, chains=2, cores=1,
                         target_accept=0.9, progressbar=False, random_seed=11)


def _score(idata, teams, test):
    rows = []
    for m in test.itertuples():
        gh, ga = int(m.home_goals), int(m.away_goals)
        result = "H" if gh > ga else "A" if ga > gh else "D"
        p = predict_match(idata, teams, m.home_team, m.away_team, neutral=True)
        rows.append({"p_H": p["p_home_win"], "p_D": p["p_draw"], "p_A": p["p_away_win"],
                     "result": result,
                     "pred_total": p["exp_goals_home"] + p["exp_goals_away"],
                     "actual_total": gh + ga})
    return evaluate(rows)


def compare(df: pd.DataFrame, label: str):
    teams = sorted(set(df["home_team"]) | set(df["away_team"]))
    df = df.sort_values("date").reset_index(drop=True)
    cut = int(len(df) * 0.8)
    train, test = df.iloc[:cut], df.iloc[cut:]
    print(f"[{label}] fit on {len(train)} matches, score on {len(test)}; "
          f"{len(teams)} teams")

    goals = _score(_fit(build_model, train.rename(
        columns={"home_goals": "home_goals", "away_goals": "away_goals"}), teams),
        teams, test)
    xg = _score(_fit(build_xg_model, train, teams), teams, test)

    print(f"\n{'model':<10} {'RPS':>8} {'log_loss':>9} {'hit':>6} {'goalsMAE':>9}")
    for name, m in (("goals", goals), ("xG", xg)):
        print(f"{name:<10} {m['RPS']:>8.4f} {m['log_loss']:>9.4f} "
              f"{m['hit_rate']:>6.3f} {m.get('goals_MAE', float('nan')):>9.3f}")
    delta = xg["RPS"] - goals["RPS"]
    verdict = "xG WINS — keep it" if delta < 0 else "goals model still better"
    print(f"\nRPS delta (xG - goals): {delta:+.4f}  ->  {verdict}")


def _demo_data() -> pd.DataFrame:
    """Synthetic matches with goals + noisy xG — to exercise the harness only."""
    rng = np.random.default_rng(0)
    teams = [f"T{i}" for i in range(12)]
    strength = {t: rng.normal(0, 0.4) for t in teams}
    rows = []
    for k in range(400):
        h, a = rng.choice(teams, 2, replace=False)
        lam_h = np.exp(0.2 + strength[h] - strength[a])
        lam_a = np.exp(0.2 + strength[a] - strength[h])
        gh, ga = rng.poisson(lam_h), rng.poisson(lam_a)
        rows.append({"date": f"2024-{1 + k % 9:02d}-01", "home_team": h, "away_team": a,
                     "home_goals": gh, "away_goals": ga,
                     "home_xg": max(0.05, lam_h + rng.normal(0, 0.3)),
                     "away_xg": max(0.05, lam_a + rng.normal(0, 0.3))})
    return pd.DataFrame(rows)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--demo", action="store_true", help="synthetic sanity check")
    args = ap.parse_args()

    if args.demo:
        print("=== SYNTHETIC DEMO (not a real-world result) ===")
        compare(_demo_data(), "demo")
        return

    path = RAW / "xg_matches.csv"
    if not path.exists():
        print(f"No xG dataset at {path}.\n"
              "Harvest xG (FBref match reports or StatsBomb open data) into a CSV "
              "with columns: date, home_team, away_team, home_goals, away_goals, "
              "home_xg, away_xg — then re-run. Or try --demo for a synthetic check.")
        return
    compare(load_xg_csv(path).assign(
        home_goals=lambda d: d["home_goals"], away_goals=lambda d: d["away_goals"]),
        "real")


if __name__ == "__main__":
    main()
