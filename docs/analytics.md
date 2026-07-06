# WC 2026 — Tracking Analytics, Sentiment & Tactics

_Run after each matchday to track model calibration and read the next slate. Charts in `artifacts/`. Compiled 2026-07-06._

## Tracking charts

![Calibration](../artifacts/calibration.png)
![Predicted vs actual goals](../artifacts/goals_pred_vs_actual.png)
![Forecast probabilities](../artifacts/forecast_probs.png)

- **Calibration** (`artifacts/calibration.png`) — are our probabilities honest? Points on the diagonal = well-calibrated.
- **Predicted vs actual goals** (`artifacts/goals_pred_vs_actual.png`) — scatter of expected vs real total goals per played match.
- **Forecast win/draw/win** (`artifacts/forecast_probs.png`) — stacked 1X2 bars for upcoming fixtures.

**Tracking metrics (92 matches):** outcome hit-rate 65% · total-goals MAE 1.41. Re-run to update as results come in.

## Match sentiment & momentum (next fixtures)

| Fixture | Home form | Away form | Momentum edge |
|---|---|---|---|
| Portugal v Spain | red-hot (+0.14) | red-hot (+0.15) | **even** |
| United States v Belgium | rising (+0.05) | red-hot (+0.18) | **Belgium** |
| Argentina v Egypt | red-hot (+0.18) | steady (+0.04) | **Argentina** |
| Switzerland v Colombia | red-hot (+0.13) | rising (+0.09) | **Switzerland** |
| France v Morocco | red-hot (+0.18) | rising (+0.11) | **France** |

## Tactical read (next fixtures)

**Portugal v Spain** — best shapes 4-3-3 vs 4-2-3-1.
  - Defence: away edge (85 vs 86) · Midfield: away edge (84 vs 86) · Attack: home edge (86 vs 85)
  - midfield finely balanced; home built around its attack, away around its defence.

**United States v Belgium** — best shapes 4-4-2 vs 3-4-3.
  - Defence: away edge (76 vs 81) · Midfield: away edge (76 vs 86) · Attack: away edge (76 vs 86)
  - away controls midfield; home built around its midfield, away around its midfield.

**Argentina v Egypt** — best shapes 4-3-3 vs 3-4-3.
  - Defence: home edge (82 vs 70) · Midfield: home edge (82 vs 72) · Attack: home edge (89 vs 79)
  - home controls midfield; home built around its attack, away around its attack.

**Switzerland v Colombia** — best shapes 3-5-2 vs 4-3-3.
  - Defence: away edge (78 vs 80) · Midfield: even (79 vs 79) · Attack: away edge (78 vs 82)
  - midfield finely balanced; home built around its midfield, away around its attack.

**France v Morocco** — best shapes 3-4-3 vs 4-3-3.
  - Defence: home edge (84 vs 81) · Midfield: home edge (87 vs 76) · Attack: home edge (88 vs 82)
  - home controls midfield; home built around its attack, away around its defence.

## Keep working on it

- Re-run stages 13 → 14 after each matchday; calibration and MAE track model health over time.
- Sentiment is form-based for all teams + scouted for Mexico; add per-team scouting / X-collector output to enrich others.
- Tactical reads use coarse position buckets — see [METHODOLOGY.md](METHODOLOGY.md) for the upgrade path.