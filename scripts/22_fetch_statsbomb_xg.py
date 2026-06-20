"""Stage 22: harvest real World Cup xG from StatsBomb open data.

Writes data/raw/xg_matches.csv (date, teams, goals, home_xg, away_xg) so the
xG-vs-goals backtest (stage 21) can run on real data.

    python scripts/22_fetch_statsbomb_xg.py            # 2018 + 2022
    python scripts/22_fetch_statsbomb_xg.py --years 2018
"""

import argparse

import pandas as pd

from wc2026.config import RAW, ensure_dirs
from wc2026.data.statsbomb import fetch_world_cup_xg


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--years", nargs="+", type=int, default=[2018, 2022])
    args = ap.parse_args()

    ensure_dirs()
    frames = []
    for y in args.years:
        print(f"Fetching {y} World Cup xG from StatsBomb (per-match event files)...")
        df = fetch_world_cup_xg(y)
        df["year"] = y
        frames.append(df)
        print(f"  {len(df)} matches, mean xG/side {df[['home_xg','away_xg']].mean().mean():.2f}")

    out = pd.concat(frames, ignore_index=True)
    out.to_csv(RAW / "xg_matches.csv", index=False)
    print(f"\nsaved {len(out)} matches -> {RAW / 'xg_matches.csv'}")
    print("\nSample (real xG vs goals):")
    print(out[["date", "home_team", "away_team", "home_goals", "away_goals",
               "home_xg", "away_xg"]].head(6).to_string(index=False))


if __name__ == "__main__":
    main()
