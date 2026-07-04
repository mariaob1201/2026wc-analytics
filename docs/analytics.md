# WC 2026 — Tracking Analytics, Sentiment & Tactics

_Run after each matchday to track model calibration and read the next slate. Charts in `artifacts/`. Compiled 2026-07-04._

## Tracking charts

![Calibration](../artifacts/calibration.png)
![Predicted vs actual goals](../artifacts/goals_pred_vs_actual.png)
![Forecast probabilities](../artifacts/forecast_probs.png)

- **Calibration** (`artifacts/calibration.png`) — are our probabilities honest? Points on the diagonal = well-calibrated.
- **Predicted vs actual goals** (`artifacts/goals_pred_vs_actual.png`) — scatter of expected vs real total goals per played match.
- **Forecast win/draw/win** (`artifacts/forecast_probs.png`) — stacked 1X2 bars for upcoming fixtures.

**Tracking metrics (88 matches):** outcome hit-rate 65% · total-goals MAE 1.41. Re-run to update as results come in.

## Match sentiment & momentum (next fixtures)

| Fixture | Home form | Away form | Momentum edge |
|---|---|---|---|
| Canada v Morocco | rising (+0.11) | rising (+0.08) | **even** |
| Paraguay v France | steady (-0.03) | red-hot (+0.18) | **France** |
| Brazil v Norway | red-hot (+0.16) | steady (+0.05) | **Brazil** |
| Mexico v England | red-hot (+0.13) | rising (+0.09) | **Mexico** |
| Argentina v Egypt | red-hot (+0.18) | steady (+0.04) | **Argentina** |
| Portugal v Spain | red-hot (+0.14) | red-hot (+0.15) | **even** |
| United States v Belgium | steady (+0.05) | red-hot (+0.18) | **Belgium** |
| Switzerland v Colombia | red-hot (+0.13) | rising (+0.08) | **Switzerland** |

## Tactical read (next fixtures)

**Canada v Morocco** — best shapes 3-4-3 vs 4-3-3.
  - Defence: away edge (73 vs 81) · Midfield: away edge (74 vs 76) · Attack: away edge (75 vs 82)
  - away controls midfield; home built around its attack, away around its defence.

**Paraguay v France** — best shapes 4-2-3-1 vs 3-4-3.
  - Defence: away edge (74 vs 84) · Midfield: away edge (76 vs 87) · Attack: away edge (74 vs 88)
  - away controls midfield; home built around its midfield, away around its attack.

**Brazil v Norway** — best shapes 4-4-2 vs 3-5-2.
  - Defence: home edge (85 vs 75) · Midfield: home edge (86 vs 78) · Attack: home edge (86 vs 80)
  - home controls midfield; home built around its midfield, away around its attack.

**Mexico v England** — best shapes 3-4-3 vs 4-3-3.
  - Defence: away edge (77 vs 85) · Midfield: away edge (80 vs 85) · Attack: away edge (82 vs 88)
  - away controls midfield; home built around its attack, away around its attack.

**Argentina v Egypt** — best shapes 4-3-3 vs 3-4-3.
  - Defence: home edge (82 vs 70) · Midfield: home edge (82 vs 72) · Attack: home edge (89 vs 79)
  - home controls midfield; home built around its attack, away around its attack.

**Portugal v Spain** — best shapes 4-3-3 vs 4-2-3-1.
  - Defence: away edge (85 vs 86) · Midfield: away edge (84 vs 86) · Attack: home edge (86 vs 85)
  - midfield finely balanced; home built around its attack, away around its defence.

**United States v Belgium** — best shapes 4-4-2 vs 3-4-3.
  - Defence: away edge (76 vs 81) · Midfield: away edge (76 vs 86) · Attack: away edge (76 vs 86)
  - away controls midfield; home built around its midfield, away around its midfield.

**Switzerland v Colombia** — best shapes 3-5-2 vs 4-3-3.
  - Defence: away edge (78 vs 80) · Midfield: even (79 vs 79) · Attack: away edge (78 vs 82)
  - midfield finely balanced; home built around its midfield, away around its attack.

## Keep working on it

- Re-run stages 13 → 14 after each matchday; calibration and MAE track model health over time.
- Sentiment is form-based for all teams + scouted for Mexico; add per-team scouting / X-collector output to enrich others.
- Tactical reads use coarse position buckets — see [METHODOLOGY.md](METHODOLOGY.md) for the upgrade path.