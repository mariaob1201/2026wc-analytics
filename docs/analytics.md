# WC 2026 — Tracking Analytics, Sentiment & Tactics

_Run after each matchday to track model calibration and read the next slate. Charts in `artifacts/`. Compiled 2026-06-19._

## Tracking charts

![Calibration](../artifacts/calibration.png)
![Predicted vs actual goals](../artifacts/goals_pred_vs_actual.png)
![Forecast probabilities](../artifacts/forecast_probs.png)

- **Calibration** (`artifacts/calibration.png`) — are our probabilities honest? Points on the diagonal = well-calibrated.
- **Predicted vs actual goals** (`artifacts/goals_pred_vs_actual.png`) — scatter of expected vs real total goals per played match.
- **Forecast win/draw/win** (`artifacts/forecast_probs.png`) — stacked 1X2 bars for upcoming fixtures.

**Tracking metrics (28 matches):** outcome hit-rate 54% · total-goals MAE 1.54. Re-run to update as results come in.

## Match sentiment & momentum (next fixtures)

| Fixture | Home form | Away form | Momentum edge |
|---|---|---|---|
| Netherlands v Sweden | steady (+0.02) | steady (+0.04) | **even** |
| Tunisia v Japan | cold (-0.13) | steady (+0.04) | **Japan** |
| Germany v Ivory Coast | red-hot (+0.18) | rising (+0.10) | **Germany** |
| Ecuador v Curaçao | steady (+0.02) | cold (-0.18) | **Ecuador** |
| Belgium v Iran | red-hot (+0.18) | steady (-0.00) | **Belgium** |
| New Zealand v Egypt | cold (-0.12) | steady (+0.01) | **Egypt** |
| Spain v Saudi Arabia | steady (+0.04) | dipping (-0.06) | **Spain** |
| Uruguay v Cape Verde | steady (-0.03) | steady (+0.01) | **even** |
| France v Iraq | rising (+0.08) | dipping (-0.11) | **France** |
| Norway v Senegal | rising (+0.09) | dipping (-0.07) | **Norway** |
| Argentina v Austria | red-hot (+0.18) | red-hot (+0.16) | **even** |
| Jordan v Algeria | dipping (-0.10) | steady (-0.01) | **Algeria** |
| Portugal v Uzbekistan | rising (+0.06) | dipping (-0.09) | **Portugal** |
| Colombia v Congo DR | rising (+0.09) | steady (-0.02) | **Colombia** |
| England v Ghana | rising (+0.06) | dipping (-0.11) | **England** |
| Panama v Croatia | dipping (-0.08) | dipping (-0.09) | **even** |
| Morocco v Haiti | rising (+0.06) | steady (+0.05) | **even** |
| Bosnia-Herzegovina v Qatar | dipping (-0.08) | cold (-0.18) | **Bosnia-Herzegovina** |
| Scotland v Brazil | rising (+0.07) | rising (+0.11) | **even** |
| South Africa v South Korea | dipping (-0.07) | dipping (-0.05) | **even** |
| Mexico v Czechia | rising (+0.09) | steady (-0.04) | **Mexico** |
| Canada v Switzerland | red-hot (+0.15) | rising (+0.11) | **even** |

## Tactical read (next fixtures)

**Netherlands v Sweden** — best shapes 5-3-2 vs 3-4-3.
  - Defence: home edge (85 vs 76) · Midfield: home edge (84 vs 77) · Attack: even (83 vs 82)
  - home controls midfield; home built around its defence, away around its attack.

**Tunisia v Japan** — best shapes 3-5-2 vs 3-5-2.
  - Defence: away edge (71 vs 74) · Midfield: away edge (74 vs 78) · Attack: away edge (72 vs 75)
  - away controls midfield; home built around its midfield, away around its midfield.

**Germany v Ivory Coast** — best shapes 4-2-3-1 vs 3-5-2.
  - Defence: home edge (84 vs 78) · Midfield: home edge (88 vs 80) · Attack: home edge (82 vs 80)
  - home controls midfield; home built around its midfield, away around its midfield.

**Ecuador v Curaçao** — best shapes 3-4-3 vs 3-4-3.
  - Defence: home edge (74 vs 64) · Midfield: home edge (75 vs 68) · Attack: home edge (76 vs 68)
  - home controls midfield; home built around its midfield, away around its midfield.

**Belgium v Iran** — best shapes 3-4-3 vs 4-3-3.
  - Defence: home edge (81 vs 70) · Midfield: home edge (86 vs 69) · Attack: home edge (86 vs 75)
  - home controls midfield; home built around its midfield, away around its attack.

**New Zealand v Egypt** — best shapes 4-4-2 vs 3-4-3.
  - Defence: even (70 vs 70) · Midfield: away edge (69 vs 72) · Attack: away edge (71 vs 79)
  - away controls midfield; home built around its defence, away around its attack.

**Spain v Saudi Arabia** — best shapes 4-2-3-1 vs 4-2-3-1.
  - Defence: home edge (86 vs 73) · Midfield: home edge (86 vs 73) · Attack: home edge (85 vs 65)
  - home controls midfield; home built around its defence, away around its midfield.

**Uruguay v Cape Verde** — best shapes 3-4-3 vs 4-3-3.
  - Defence: home edge (81 vs 70) · Midfield: home edge (80 vs 70) · Attack: home edge (84 vs 76)
  - home controls midfield; home built around its attack, away around its attack.

**France v Iraq** — best shapes 3-4-3 vs 3-5-2.
  - Defence: home edge (84 vs 58) · Midfield: home edge (87 vs 67) · Attack: home edge (88 vs 60)
  - home controls midfield; home built around its attack, away around its midfield.

**Norway v Senegal** — best shapes 3-5-2 vs 4-3-3.
  - Defence: away edge (75 vs 80) · Midfield: even (78 vs 78) · Attack: away edge (80 vs 81)
  - midfield finely balanced; home built around its attack, away around its attack.

**Argentina v Austria** — best shapes 4-3-3 vs 4-2-3-1.
  - Defence: home edge (82 vs 80) · Midfield: home edge (82 vs 81) · Attack: home edge (89 vs 77)
  - home controls midfield; home built around its attack, away around its midfield.

**Jordan v Algeria** — best shapes 3-5-2 vs 4-4-2.
  - Defence: away edge (60 vs 78) · Midfield: away edge (64 vs 78) · Attack: away edge (57 vs 81)
  - away controls midfield; home built around its midfield, away around its attack.

**Portugal v Uzbekistan** — best shapes 4-3-3 vs 3-4-3.
  - Defence: home edge (85 vs 62) · Midfield: home edge (84 vs 67) · Attack: home edge (86 vs 68)
  - home controls midfield; home built around its attack, away around its midfield.

**Colombia v Congo DR** — best shapes 4-3-3 vs 4-4-2.
  - Defence: home edge (80 vs 76) · Midfield: home edge (79 vs 75) · Attack: home edge (82 vs 75)
  - home controls midfield; home built around its attack, away around its defence.

**England v Ghana** — best shapes 4-3-3 vs 3-5-2.
  - Defence: home edge (85 vs 76) · Midfield: home edge (85 vs 78) · Attack: home edge (88 vs 76)
  - home controls midfield; home built around its attack, away around its midfield.

**Panama v Croatia** — best shapes 4-4-2 vs 3-5-2.
  - Defence: away edge (70 vs 78) · Midfield: away edge (70 vs 84) · Attack: away edge (68 vs 79)
  - away controls midfield; home built around its defence, away around its midfield.

**Morocco v Haiti** — best shapes 4-3-3 vs 3-4-3.
  - Defence: home edge (81 vs 61) · Midfield: home edge (76 vs 63) · Attack: home edge (82 vs 65)
  - home controls midfield; home built around its defence, away around its attack.

**Bosnia-Herzegovina v Qatar** — best shapes 4-3-3 vs 4-4-2.
  - Defence: home edge (74 vs 60) · Midfield: home edge (78 vs 60) · Attack: home edge (77 vs 60)
  - home controls midfield; home built around its midfield, away around its defence.

**Scotland v Brazil** — best shapes 4-4-2 vs 4-4-2.
  - Defence: away edge (79 vs 85) · Midfield: away edge (78 vs 86) · Attack: away edge (75 vs 86)
  - away controls midfield; home built around its defence, away around its midfield.

**South Africa v South Korea** — best shapes 3-4-3 vs 3-4-3.
  - Defence: away edge (70 vs 73) · Midfield: away edge (70 vs 78) · Attack: away edge (73 vs 75)
  - away controls midfield; home built around its attack, away around its midfield.

**Mexico v Czechia** — best shapes 3-4-3 vs 4-4-2.
  - Defence: away edge (77 vs 78) · Midfield: home edge (80 vs 78) · Attack: home edge (82 vs 78)
  - midfield finely balanced; home built around its attack, away around its midfield.

**Canada v Switzerland** — best shapes 3-4-3 vs 3-5-2.
  - Defence: away edge (73 vs 78) · Midfield: away edge (74 vs 79) · Attack: away edge (75 vs 78)
  - away controls midfield; home built around its attack, away around its midfield.

## Keep working on it

- Re-run stages 13 → 14 after each matchday; calibration and MAE track model health over time.
- Sentiment is form-based for all teams + scouted for Mexico; add per-team scouting / X-collector output to enrich others.
- Tactical reads use coarse position buckets — see [METHODOLOGY.md](METHODOLOGY.md) for the upgrade path.