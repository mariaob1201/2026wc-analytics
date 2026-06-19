# 🏆 World Cup 2026 — Champion Tracker

_A living, state-aware forecast. Conditioned on the **28 matches played so far**: completed group games are held fixed; the rest of the tournament is simulated from a Bayesian goals model (squad-skill prior + current form + X/ESPN sentiment). Updated 2026-06-19._

## How to read this

1. **Next games** — predicted goals for the upcoming fixtures.
2. **The trophy** — each team's title probability, given everything that has already happened.

Both come from one model: goals are the primitive; the winner is a simulation over goals. See [METHODOLOGY.md](METHODOLOGY.md).

## Title odds — conditioned on current results

| Team | Quarter | Semi | Final | **Champion** |
|---|---|---|---|---|
| Argentina | 49% | 28% | 18% | **13%** |
| France | 46% | 24% | 14% | **10%** |
| Portugal | 42% | 23% | 13% | **8%** |
| Brazil | 42% | 22% | 11% | **7%** |
| Belgium | 42% | 21% | 11% | **6%** |
| Colombia | 42% | 22% | 11% | **6%** |
| Germany | 42% | 23% | 11% | **6%** |
| England | 36% | 18% | 9% | **5%** |
| Spain | 34% | 18% | 8% | **4%** |
| Austria | 34% | 19% | 10% | **4%** |
| Uruguay | 28% | 15% | 7% | **4%** |
| Switzerland | 29% | 15% | 7% | **3%** |

## Next games — predicted goals

| Date | Fixture | Pred goals (xG) | Likely | P(H/D/A) | Home form |
|---|---|---|---|---|---|
| 2026-06-20 | Netherlands v Sweden | 2.0-1.3 | 1-1 | 54%/22%/25% | steady |
| 2026-06-20 | Tunisia v Japan | 0.6-1.2 | 0-1 | 19%/30%/50% | cold |
| 2026-06-20 | Germany v Ivory Coast | 1.9-1.3 | 1-1 | 50%/23%/27% | red-hot |
| 2026-06-20 | Ecuador v Curaçao | 1.9-0.4 | 1-0 | 72%/20%/7% | steady |
| 2026-06-21 | Belgium v Iran | 2.3-0.8 | 2-0 | 71%/18%/12% | red-hot |
| 2026-06-21 | New Zealand v Egypt | 0.7-1.2 | 0-1 | 21%/31%/48% | cold |
| 2026-06-21 | Spain v Saudi Arabia | 1.6-0.6 | 1-0 | 61%/25%/14% | steady |
| 2026-06-21 | Uruguay v Cape Verde | 1.4-0.5 | 1-0 | 58%/28%/14% | steady |
| 2026-06-22 | France v Iraq | 2.2-0.5 | 2-0 | 76%/17%/7% | rising |
| 2026-06-22 | Norway v Senegal | 1.4-1.2 | 1-1 | 40%/26%/33% | rising |
| 2026-06-22 | Argentina v Austria | 1.8-1.1 | 1-1 | 53%/23%/24% | red-hot |
| 2026-06-22 | Jordan v Algeria | 0.6-1.9 | 0-1 | 12%/21%/67% | dipping |
| 2026-06-23 | Portugal v Uzbekistan | 2.0-0.4 | 1-0 | 74%/19%/8% | rising |
| 2026-06-23 | Colombia v Congo DR | 1.6-0.7 | 1-0 | 59%/25%/16% | rising |
| 2026-06-23 | England v Ghana | 2.2-0.8 | 2-0 | 69%/19%/12% | rising |
| 2026-06-23 | Panama v Croatia | 0.5-1.6 | 0-1 | 12%/24%/64% | dipping |
| 2026-06-24 | Morocco v Haiti | 1.7-0.5 | 1-0 | 66%/23%/11% | rising |
| 2026-06-24 | Bosnia-Herzegovina v Qatar | 1.6-1.3 | 1-1 | 46%/24%/30% | dipping |
| 2026-06-24 | Scotland v Brazil | 1.1-2.2 | 1-2 | 18%/20%/63% | rising |
| 2026-06-24 | South Africa v South Korea | 0.9-1.1 | 0-1 | 30%/31%/39% | dipping |
| 2026-06-24 | Mexico v Czechia | 2.0-1.1 | 1-1 | 57%/22%/22% | rising |
| 2026-06-24 | Canada v Switzerland | 1.4-1.4 | 1-1 | 39%/25%/36% | red-hot |

## Current group standings (played)

| Team | P | Pts | GD |
|---|---|---|---|
| Mexico | 2 | 6 | +3 |
| Canada | 2 | 4 | +6 |
| Switzerland | 2 | 4 | +3 |
| Germany | 1 | 3 | +6 |
| Sweden | 1 | 3 | +4 |
| United States | 1 | 3 | +3 |
| Norway | 1 | 3 | +3 |
| Argentina | 1 | 3 | +3 |
| Australia | 1 | 3 | +2 |
| France | 1 | 3 | +2 |
| Austria | 1 | 3 | +2 |
| Colombia | 1 | 3 | +2 |
| England | 1 | 3 | +2 |
| Scotland | 1 | 3 | +1 |
| Ivory Coast | 1 | 3 | +1 |
| Ghana | 1 | 3 | +1 |
| South Korea | 2 | 3 | +0 |
| Brazil | 1 | 1 | +0 |
| Morocco | 1 | 1 | +0 |
| Netherlands | 1 | 1 | +0 |
| Japan | 1 | 1 | +0 |
| Belgium | 1 | 1 | +0 |
| Egypt | 1 | 1 | +0 |
| Iran | 1 | 1 | +0 |
| New Zealand | 1 | 1 | +0 |
| Spain | 1 | 1 | +0 |
| Cape Verde | 1 | 1 | +0 |
| Saudi Arabia | 1 | 1 | +0 |
| Uruguay | 1 | 1 | +0 |
| Portugal | 1 | 1 | +0 |
| Congo DR | 1 | 1 | +0 |
| Czechia | 2 | 1 | -1 |
| South Africa | 2 | 1 | -2 |
| Bosnia-Herzegovina | 2 | 1 | -3 |
| Qatar | 2 | 1 | -6 |
| Haiti | 1 | 0 | -1 |
| Ecuador | 1 | 0 | -1 |
| Panama | 1 | 0 | -1 |
| Türkiye | 1 | 0 | -2 |
| Senegal | 1 | 0 | -2 |
| Jordan | 1 | 0 | -2 |
| Uzbekistan | 1 | 0 | -2 |
| Croatia | 1 | 0 | -2 |
| Paraguay | 1 | 0 | -3 |
| Iraq | 1 | 0 | -3 |
| Algeria | 1 | 0 | -3 |
| Tunisia | 1 | 0 | -4 |
| Curaçao | 1 | 0 | -6 |

## What feeds the prediction

- **Player skillsets** — squad ratings (pace/shooting/passing/…) and seniority form the model's prior, so squad quality shapes goals.
- **Current results** — the posterior is fit on matches through today and the simulation holds played games fixed.
- **Form + X/ESPN sentiment** — folded in as a small, capped goal-rate nudge (see `models/momentum.py`, `data/scouting.py`).
- **Charts:** `artifacts/champion_tracker.png` (title odds), `artifacts/forecast_probs.png`, `artifacts/calibration.png`.