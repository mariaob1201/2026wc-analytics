"""Stage 24: the performance-form signal — condition next-game scores on how
recent matches actually went (via xG / shots, not just the result).

Reads the per-match stats table (data/raw/xg_matches.csv from `make fetch-xg`),
computes each team's recency-weighted recent-xG form, and shows the goal-rate
nudge it produces. That nudge feeds straight into the score forecast:

    predict_match(idata, teams, home, away, shifts=performance_form(stats, asof))

so a side that has been *creating* more than it concedes is bumped up even if
the scoreline hasn't caught up yet — the "how the game went" conditioning.

    python scripts/24_form_signal.py --asof 2018-07-01 --metric xg
"""

import argparse

import pandas as pd

from wc2026.config import RAW
from wc2026.models.momentum import momentum_label, performance_form


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--asof", default="2018-07-01")
    ap.add_argument("--metric", default="xg", help="xg | shots | sot (column suffix)")
    ap.add_argument("--csv", default=str(RAW / "xg_matches.csv"))
    args = ap.parse_args()

    try:
        stats = pd.read_csv(args.csv, parse_dates=["date"])
    except FileNotFoundError:
        print(f"No match-stats table at {args.csv}. Run `make fetch-xg` first "
              "(StatsBomb xG), or supply your own with home_/away_<metric> columns.")
        return

    shifts = performance_form(stats, asof=args.asof, metric=args.metric)
    s = sorted(shifts.items(), key=lambda kv: kv[1], reverse=True)
    print(f"Performance-form by recent {args.metric} as of {args.asof} "
          f"(nudge to predicted goal rate, capped ±0.18):\n")
    print("  In form (creating > conceding):")
    for t, v in s[:6]:
        print(f"    {t:<16} {v:+.3f}  {momentum_label(v)}")
    print("  Out of form:")
    for t, v in s[-6:]:
        print(f"    {t:<16} {v:+.3f}  {momentum_label(v)}")
    print("\nThis dict feeds predict_match(shifts=...) — the next-game score is "
          "conditioned on these recent-performance signals.")


if __name__ == "__main__":
    main()
