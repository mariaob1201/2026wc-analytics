"""Stage 20: the persistent forecast-vs-ground-truth log.

The accountability ledger. Each run it merges:
  * resolved matches (backtest.csv) — what we forecast vs what actually happened,
  * pending matches (forecast.csv) — forecasts for games not yet played,
into one growing `data/processed/predictions_log.csv`, and reports the running
accuracy of the GOAL forecasts against ground truth.

In the daily GitHub Action this becomes a live track record: forecasts are logged
before kickoff, then resolved with the real score once the result lands.

    python scripts/20_prediction_log.py
"""

import pandas as pd

from wc2026.config import PROCESSED, ROOT, ensure_dirs
from wc2026.models.metrics import evaluate


def main() -> None:
    ensure_dirs()
    bt = pd.read_csv(PROCESSED / "backtest.csv")        # resolved (out-of-sample)
    fc = pd.read_csv(PROCESSED / "forecast.csv")        # pending

    resolved = pd.DataFrame({
        "match_date": bt["date"], "home": bt["home"], "away": bt["away"],
        "pred_goals": bt["pred_xg"], "pred_score": bt["pred_score"],
        "p_H": bt["p_H"], "p_D": bt["p_D"], "p_A": bt["p_A"],
        "actual": bt["actual"], "result": bt["result"],
        "hit": bt["hit"], "goal_abs_err": (bt["tot_pred"] - bt["tot_act"]).abs().round(2),
        "status": "resolved",
    })
    pending = pd.DataFrame({
        "match_date": fc["date"], "home": fc["home"], "away": fc["away"],
        "pred_goals": fc["xg"], "pred_score": fc["score"],
        "p_H": fc["p_H"], "p_D": fc["p_D"], "p_A": fc["p_A"],
        "actual": "", "result": "", "hit": "", "goal_abs_err": "",
        "status": "pending",
    })
    log = pd.concat([resolved, pending], ignore_index=True)
    log.to_csv(PROCESSED / "predictions_log.csv", index=False)

    # Running accuracy of the GOAL forecasts vs ground truth (resolved rows).
    rows = [{"p_H": r.p_H, "p_D": r.p_D, "p_A": r.p_A, "result": r.result,
             "pred_total": bt.loc[i, "tot_pred"], "actual_total": bt.loc[i, "tot_act"]}
            for i, r in enumerate(bt.itertuples())]
    m = evaluate(rows)

    md = _render(log, m, resolved, pending)
    out = ROOT / "docs" / "FORECAST_LOG.md"
    out.write_text(md)

    print(f"Logged {len(resolved)} resolved + {len(pending)} pending forecasts "
          f"-> {PROCESSED / 'predictions_log.csv'}")
    print(f"Running goal-forecast accuracy: hit-rate {100*m['hit_rate']:.0f}%, "
          f"goals MAE {m.get('goals_MAE')}, RPS {m['RPS']}")
    print(f"saved -> {out}")


def _pct(x):
    try:
        return f"{100*float(x):.0f}%"
    except (ValueError, TypeError):
        return "—"


def _render(log, m, resolved, pending) -> str:
    L = ["# 📒 Forecast Log — Predictions vs Ground Truth\n",
         "_A growing, append-on-result ledger: every goal forecast and how it "
         "turned out. Updated by the daily GitHub Action. Compiled 2026-06-19._\n"]

    L.append("## Running accuracy (resolved matches)\n")
    L.append(f"- **Matches scored:** {m['n']}")
    L.append(f"- **Outcome hit-rate:** {_pct(m['hit_rate'])}")
    L.append(f"- **Goal-total MAE:** {m.get('goals_MAE', '—')} goals/match")
    L.append(f"- **RPS:** {m['RPS']} · **log-loss:** {m['log_loss']} (lower better)\n")

    L.append("## Resolved — forecast vs actual\n")
    L.append("| Date | Fixture | Forecast (xG) | Pred | Actual | ✓ |")
    L.append("|---|---|---|---|---|:--:|")
    for r in resolved.itertuples():
        L.append(f"| {r.match_date} | {r.home} v {r.away} | {r.pred_goals} | "
                 f"{r.pred_score} | **{r.actual}** | {'✅' if r.hit else '—'} |")

    if len(pending):
        L.append("\n## Pending — forecasts awaiting kickoff\n")
        L.append("| Date | Fixture | Forecast (xG) | Likely | P(H/D/A) |")
        L.append("|---|---|---|---|---|")
        for r in pending.itertuples():
            L.append(f"| {r.match_date} | {r.home} v {r.away} | {r.pred_goals} | "
                     f"{r.pred_score} | {_pct(r.p_H)}/{_pct(r.p_D)}/{_pct(r.p_A)} |")

    L.append("\n_Ground truth comes from the live results feed; the daily Action "
             "fills `actual` once each match is played and rolls the accuracy "
             "forward. See [LIVE_PIPELINE.md](LIVE_PIPELINE.md)._")
    return "\n".join(L)


if __name__ == "__main__":
    main()
