# WC 2026 — Tracking Analytics, Sentiment & Tactics

_Run after each matchday to track model calibration and read the next slate. Charts in `artifacts/`. Compiled 2026-07-17._

## Tracking charts

![Calibration](../artifacts/calibration.png)
![Predicted vs actual goals](../artifacts/goals_pred_vs_actual.png)
![Forecast probabilities](../artifacts/forecast_probs.png)

- **Calibration** (`artifacts/calibration.png`) — are our probabilities honest? Points on the diagonal = well-calibrated.
- **Predicted vs actual goals** (`artifacts/goals_pred_vs_actual.png`) — scatter of expected vs real total goals per played match.
- **Forecast win/draw/win** (`artifacts/forecast_probs.png`) — stacked 1X2 bars for upcoming fixtures.

**Tracking metrics (102 matches):** outcome hit-rate 66% · total-goals MAE 1.37. Re-run to update as results come in.

## Match sentiment & momentum (next fixtures)

| Fixture | Home form | Away form | Momentum edge |
|---|---|---|---|
| France v England | red-hot (+0.15) | rising (+0.08) | **France** |
| Spain v Argentina | red-hot (+0.16) | red-hot (+0.18) | **even** |

## Tactical read (next fixtures)

**France v England** — best shapes 3-4-3 vs 4-3-3.
  - Defence: even (84 vs 85) · Midfield: home edge (87 vs 85) · Attack: even (88 vs 88)
  - home controls midfield; home built around its attack, away around its attack.

**Spain v Argentina** — best shapes 4-2-3-1 vs 4-3-3.
  - Defence: home edge (86 vs 82) · Midfield: home edge (86 vs 82) · Attack: away edge (85 vs 89)
  - home controls midfield; home built around its defence, away around its attack.

## Keep working on it

- Re-run stages 13 → 14 after each matchday; calibration and MAE track model health over time.
- Sentiment is form-based for all teams + scouted for Mexico; add per-team scouting / X-collector output to enrich others.
- Tactical reads use coarse position buckets — see [METHODOLOGY.md](METHODOLOGY.md) for the upgrade path.