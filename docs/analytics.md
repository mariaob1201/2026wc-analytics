# WC 2026 — Tracking Analytics, Sentiment & Tactics

_Run after each matchday to track model calibration and read the next slate. Charts in `artifacts/`. Compiled 2026-06-25._

## Tracking charts

![Calibration](../artifacts/calibration.png)
![Predicted vs actual goals](../artifacts/goals_pred_vs_actual.png)
![Forecast probabilities](../artifacts/forecast_probs.png)

- **Calibration** (`artifacts/calibration.png`) — are our probabilities honest? Points on the diagonal = well-calibrated.
- **Predicted vs actual goals** (`artifacts/goals_pred_vs_actual.png`) — scatter of expected vs real total goals per played match.
- **Forecast win/draw/win** (`artifacts/forecast_probs.png`) — stacked 1X2 bars for upcoming fixtures.

**Tracking metrics (54 matches):** outcome hit-rate 65% · total-goals MAE 1.50. Re-run to update as results come in.

## Match sentiment & momentum (next fixtures)

| Fixture | Home form | Away form | Momentum edge |
|---|---|---|---|
| United States v Türkiye | steady (+0.04) | cold (-0.13) | **United States** |
| Paraguay v Australia | dipping (-0.06) | steady (+0.03) | **Australia** |
| Curaçao v Ivory Coast | cold (-0.18) | rising (+0.06) | **Ivory Coast** |
| Ecuador v Germany | steady (+0.02) | red-hot (+0.18) | **Germany** |
| Japan v Sweden | rising (+0.12) | dipping (-0.08) | **Japan** |
| Tunisia v Netherlands | cold (-0.17) | rising (+0.09) | **Netherlands** |
| Senegal v Iraq | dipping (-0.07) | cold (-0.15) | **Senegal** |
| Norway v France | rising (+0.09) | red-hot (+0.13) | **even** |
| Uruguay v Spain | steady (-0.02) | rising (+0.11) | **Spain** |
| New Zealand v Belgium | cold (-0.13) | red-hot (+0.15) | **Belgium** |
| Egypt v Iran | steady (+0.04) | steady (+0.00) | **even** |
| Cape Verde v Saudi Arabia | steady (+0.01) | dipping (-0.11) | **Cape Verde** |
| Panama v England | dipping (-0.08) | steady (+0.05) | **England** |
| Algeria v Austria | steady (+0.02) | rising (+0.09) | **Austria** |
| Jordan v Argentina | dipping (-0.10) | red-hot (+0.18) | **Argentina** |
| Colombia v Portugal | rising (+0.09) | red-hot (+0.17) | **Portugal** |
| Congo DR v Uzbekistan | steady (-0.04) | cold (-0.16) | **Congo DR** |
| Croatia v Ghana | dipping (-0.05) | dipping (-0.08) | **even** |

## Tactical read (next fixtures)

**United States v Türkiye** — best shapes 4-4-2 vs 4-4-2.
  - Defence: away edge (76 vs 78) · Midfield: away edge (76 vs 78) · Attack: away edge (76 vs 78)
  - midfield finely balanced; home built around its midfield, away around its defence.

**Paraguay v Australia** — best shapes 4-2-3-1 vs 4-4-2.
  - Defence: home edge (74 vs 72) · Midfield: home edge (76 vs 74) · Attack: home edge (74 vs 72)
  - home controls midfield; home built around its midfield, away around its midfield.

**Curaçao v Ivory Coast** — best shapes 3-4-3 vs 3-5-2.
  - Defence: away edge (64 vs 78) · Midfield: away edge (68 vs 80) · Attack: away edge (68 vs 80)
  - away controls midfield; home built around its midfield, away around its midfield.

**Ecuador v Germany** — best shapes 3-4-3 vs 4-2-3-1.
  - Defence: away edge (74 vs 84) · Midfield: away edge (75 vs 88) · Attack: away edge (76 vs 82)
  - away controls midfield; home built around its midfield, away around its midfield.

**Japan v Sweden** — best shapes 3-5-2 vs 3-4-3.
  - Defence: away edge (74 vs 76) · Midfield: even (78 vs 77) · Attack: away edge (75 vs 82)
  - midfield finely balanced; home built around its midfield, away around its attack.

**Tunisia v Netherlands** — best shapes 3-5-2 vs 5-3-2.
  - Defence: away edge (71 vs 85) · Midfield: away edge (74 vs 84) · Attack: away edge (72 vs 83)
  - away controls midfield; home built around its midfield, away around its defence.

**Senegal v Iraq** — best shapes 4-3-3 vs 3-5-2.
  - Defence: home edge (80 vs 58) · Midfield: home edge (78 vs 67) · Attack: home edge (81 vs 60)
  - home controls midfield; home built around its attack, away around its midfield.

**Norway v France** — best shapes 3-5-2 vs 3-4-3.
  - Defence: away edge (75 vs 84) · Midfield: away edge (78 vs 87) · Attack: away edge (80 vs 88)
  - away controls midfield; home built around its attack, away around its attack.

**Uruguay v Spain** — best shapes 3-4-3 vs 4-2-3-1.
  - Defence: away edge (81 vs 86) · Midfield: away edge (80 vs 86) · Attack: even (84 vs 85)
  - away controls midfield; home built around its attack, away around its defence.

**New Zealand v Belgium** — best shapes 4-4-2 vs 3-4-3.
  - Defence: away edge (70 vs 81) · Midfield: away edge (69 vs 86) · Attack: away edge (71 vs 86)
  - away controls midfield; home built around its defence, away around its midfield.

**Egypt v Iran** — best shapes 3-4-3 vs 4-3-3.
  - Defence: even (70 vs 70) · Midfield: home edge (72 vs 69) · Attack: home edge (79 vs 75)
  - home controls midfield; home built around its attack, away around its attack.

**Cape Verde v Saudi Arabia** — best shapes 4-3-3 vs 4-2-3-1.
  - Defence: away edge (70 vs 73) · Midfield: away edge (70 vs 73) · Attack: home edge (76 vs 65)
  - away controls midfield; home built around its attack, away around its midfield.

**Panama v England** — best shapes 4-4-2 vs 4-3-3.
  - Defence: away edge (70 vs 85) · Midfield: away edge (70 vs 85) · Attack: away edge (68 vs 88)
  - away controls midfield; home built around its defence, away around its attack.

**Algeria v Austria** — best shapes 4-4-2 vs 4-2-3-1.
  - Defence: away edge (78 vs 80) · Midfield: away edge (78 vs 81) · Attack: home edge (81 vs 77)
  - away controls midfield; home built around its attack, away around its midfield.

**Jordan v Argentina** — best shapes 3-5-2 vs 4-3-3.
  - Defence: away edge (60 vs 82) · Midfield: away edge (64 vs 82) · Attack: away edge (57 vs 89)
  - away controls midfield; home built around its midfield, away around its attack.

**Colombia v Portugal** — best shapes 4-3-3 vs 4-3-3.
  - Defence: away edge (80 vs 85) · Midfield: away edge (79 vs 84) · Attack: away edge (82 vs 86)
  - away controls midfield; home built around its attack, away around its attack.

**Congo DR v Uzbekistan** — best shapes 4-4-2 vs 3-4-3.
  - Defence: home edge (76 vs 62) · Midfield: home edge (75 vs 67) · Attack: home edge (75 vs 68)
  - home controls midfield; home built around its defence, away around its midfield.

**Croatia v Ghana** — best shapes 3-5-2 vs 3-5-2.
  - Defence: home edge (78 vs 76) · Midfield: home edge (84 vs 78) · Attack: home edge (79 vs 76)
  - home controls midfield; home built around its midfield, away around its midfield.

## Keep working on it

- Re-run stages 13 → 14 after each matchday; calibration and MAE track model health over time.
- Sentiment is form-based for all teams + scouted for Mexico; add per-team scouting / X-collector output to enrich others.
- Tactical reads use coarse position buckets — see [METHODOLOGY.md](METHODOLOGY.md) for the upgrade path.