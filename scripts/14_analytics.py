"""Stage 14: tracking analytics + visualizations, match sentiment, and tactics.

Consumes the backtest/forecast tables saved by stage 13 (run 13 first) and:
  * draws tracking charts (calibration, predicted-vs-actual goals, forecast bars),
  * adds a per-fixture **sentiment/momentum** readout (form + scouted sentiment),
  * adds a per-fixture **tactical** read (best shapes + line-by-line battles).

Writes docs/analytics.md and charts to artifacts/. Re-run after each matchday to
keep tracking the model.

    python scripts/14_analytics.py
"""

import pandas as pd

from wc2026.config import ARTIFACTS, PROCESSED, ROOT, ensure_dirs
from wc2026.data.scouting import MEXICO_SOCIAL
from wc2026.features.interpretation import add_player_interpretation
from wc2026.features.tactics import matchup_tactics
from wc2026.models.momentum import combined_shifts, match_sentiment
from wc2026.viz.plots import plot_calibration, plot_forecast_probs, plot_goals_scatter

TODAY = "2026-06-19"
MEX_FORMATION = "4-1-4-1"


def main() -> None:
    ensure_dirs()
    bt = pd.read_csv(PROCESSED / "backtest.csv")
    fc = pd.read_csv(PROCESSED / "forecast.csv")
    players = add_player_interpretation(pd.read_csv(PROCESSED / "players_real_features.csv"))

    # --- Charts ---
    plot_calibration(bt, ARTIFACTS / "calibration.png")
    plot_goals_scatter(bt, ARTIFACTS / "goals_pred_vs_actual.png")
    if len(fc):
        plot_forecast_probs(fc, ARTIFACTS / "forecast_probs.png")

    # --- Per-fixture sentiment + tactics for the forecast slate ---
    from wc2026.data.sources import build_real_matches
    shifts = combined_shifts(build_real_matches(start="2022-01-01", end=TODAY), TODAY,
                             scouted={"Mexico": MEXICO_SOCIAL["net_mood"]})

    def squad(team):
        return players[players["team"] == team]

    rows = []
    for r in fc.itertuples():
        sent = match_sentiment(r.home, r.away, shifts)
        tac = matchup_tactics(
            squad(r.home), squad(r.away),
            home_actual=MEX_FORMATION if r.home == "Mexico" else None,
            away_actual=MEX_FORMATION if r.away == "Mexico" else None,
        )
        rows.append({"fixture": f"{r.home} v {r.away}", "date": r.date,
                     "sent": sent, "tac": tac})

    md = _render(bt, fc, rows)
    out = ROOT / "docs" / "analytics.md"
    out.write_text(md)

    print("Charts saved to artifacts/: calibration.png, goals_pred_vs_actual.png, "
          "forecast_probs.png")
    print(f"Analytics report -> {out}")


def _render(bt, fc, rows) -> str:
    L = ["# WC 2026 — Tracking Analytics, Sentiment & Tactics\n",
         "_Run after each matchday to track model calibration and read the next "
         "slate. Charts in `artifacts/`. Compiled 2026-06-19._\n"]

    L.append("## Tracking charts\n")
    L.append("- **Calibration** (`artifacts/calibration.png`) — are our "
             "probabilities honest? Points on the diagonal = well-calibrated.")
    L.append("- **Predicted vs actual goals** (`artifacts/goals_pred_vs_actual.png`) "
             "— scatter of expected vs real total goals per played match.")
    L.append("- **Forecast win/draw/win** (`artifacts/forecast_probs.png`) — stacked "
             "1X2 bars for upcoming fixtures.\n")

    n = len(bt)
    hit = bt["hit"].mean() if n else float("nan")
    mae = (bt["tot_pred"] - bt["tot_act"]).abs().mean() if n else float("nan")
    L.append(f"**Tracking metrics ({n} matches):** outcome hit-rate "
             f"{100*hit:.0f}% · total-goals MAE {mae:.2f}. Re-run to update as "
             "results come in.\n")

    L.append("## Match sentiment & momentum (next fixtures)\n")
    L.append("| Fixture | Home form | Away form | Momentum edge |")
    L.append("|---|---|---|---|")
    for x in rows:
        s = x["sent"]
        L.append(f"| {x['fixture']} | {s['home_form']} ({s['home_shift']:+.2f}) | "
                 f"{s['away_form']} ({s['away_shift']:+.2f}) | **{s['momentum_edge']}** |")

    L.append("\n## Tactical read (next fixtures)\n")
    for x in rows:
        t = x["tac"]
        L.append(f"**{x['fixture']}** — best shapes {t['home_best']} vs "
                 f"{t['away_best']}.")
        L.append(f"  - " + " · ".join(t["line_battles"]))
        L.append(f"  - {t['verdict']}\n")

    L.append("## Keep working on it\n")
    L.append("- Re-run stages 13 → 14 after each matchday; calibration and MAE "
             "track model health over time.")
    L.append("- Sentiment is form-based for all teams + scouted for Mexico; add "
             "per-team scouting / X-collector output to enrich others.")
    L.append("- Tactical reads use coarse position buckets — see "
             "[METHODOLOGY.md](METHODOLOGY.md) for the upgrade path.")
    return "\n".join(L)


if __name__ == "__main__":
    main()
