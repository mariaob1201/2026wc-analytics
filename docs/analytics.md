# WC 2026 — Tracking Analytics, Sentiment & Tactics

_Run after each matchday to track model calibration and read the next slate. Charts in `artifacts/`. Compiled 2026-07-12._

## Tracking charts

![Calibration](../artifacts/calibration.png)
![Predicted vs actual goals](../artifacts/goals_pred_vs_actual.png)
![Forecast probabilities](../artifacts/forecast_probs.png)

- **Calibration** (`artifacts/calibration.png`) — are our probabilities honest? Points on the diagonal = well-calibrated.
- **Predicted vs actual goals** (`artifacts/goals_pred_vs_actual.png`) — scatter of expected vs real total goals per played match.
- **Forecast win/draw/win** (`artifacts/forecast_probs.png`) — stacked 1X2 bars for upcoming fixtures.

**Tracking metrics (98 matches):** outcome hit-rate 65% · total-goals MAE 1.40. Re-run to update as results come in.

## Match sentiment & momentum (next fixtures)

| Fixture | Home form | Away form | Momentum edge |
|---|---|---|---|
| Norway v England | rising (+0.06) | rising (+0.10) | **even** |
| Argentina v Switzerland | red-hot (+0.18) | red-hot (+0.13) | **Argentina** |

## Tactical read (next fixtures)

**Norway v England** — best shapes 3-5-2 vs 4-3-3.
  - Defence: away edge (75 vs 85) · Midfield: away edge (78 vs 85) · Attack: away edge (80 vs 88)
  - away controls midfield; home built around its attack, away around its attack.

**Argentina v Switzerland** — best shapes 4-3-3 vs 3-5-2.
  - Defence: home edge (82 vs 78) · Midfield: home edge (82 vs 79) · Attack: home edge (89 vs 78)
  - home controls midfield; home built around its attack, away around its midfield.

## Keep working on it

- Re-run stages 13 → 14 after each matchday; calibration and MAE track model health over time.
- Sentiment is form-based for all teams + scouted for Mexico; add per-team scouting / X-collector output to enrich others.
- Tactical reads use coarse position buckets — see [METHODOLOGY.md](METHODOLOGY.md) for the upgrade path.