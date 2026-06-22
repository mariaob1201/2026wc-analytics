# 🏆 World Cup 2026 — Champion Tracker

_A living, state-aware forecast. Conditioned on the **36 matches played so far**: completed group games are held fixed; the rest of the tournament is simulated from a Bayesian goals model (squad-skill prior + current form + X/ESPN sentiment). Updated 2026-06-21._

## How to read this

1. **Next games** — predicted goals for the upcoming fixtures.
2. **The trophy** — each team's title probability, given everything that has already happened.

Both come from one model: goals are the primitive; the winner is a simulation over goals. See [METHODOLOGY.md](METHODOLOGY.md).

## Title odds — conditioned on current results

![Title probabilities](../artifacts/champion_tracker.png)

| Team | Quarter | Semi | Final | **Champion** |
|---|---|---|---|---|
| Argentina | 49% | 28% | 18% | **13%** |
| France | 45% | 23% | 13% | **8%** |
| Belgium | 42% | 23% | 13% | **8%** |
| Brazil | 46% | 23% | 12% | **7%** |
| Portugal | 38% | 20% | 10% | **6%** |
| Germany | 43% | 22% | 12% | **6%** |
| Colombia | 42% | 22% | 11% | **6%** |
| Japan | 36% | 20% | 9% | **5%** |
| Austria | 36% | 19% | 9% | **5%** |
| Spain | 34% | 18% | 9% | **4%** |
| Morocco | 33% | 17% | 8% | **3%** |
| Netherlands | 31% | 17% | 8% | **3%** |

_Mexico's Round-of-32 opponent odds (per candidate): [R32_ODDS.md](R32_ODDS.md) — `make r32-odds`._


## Next games — predicted goals

| Date | Fixture | Pred goals (xG) | Likely | P(H/D/A) | Home form |
|---|---|---|---|---|---|
| 2026-06-22 | France v Iraq | 2.3-0.4 | 2-0 | 80%/15%/5% | rising |
| 2026-06-22 | Norway v Senegal | 1.5-1.2 | 1-1 | 45%/25%/30% | rising |
| 2026-06-22 | Argentina v Austria | 1.7-1.1 | 1-1 | 50%/24%/26% | red-hot |
| 2026-06-22 | Jordan v Algeria | 0.7-1.8 | 0-1 | 14%/23%/63% | dipping |
| 2026-06-23 | Portugal v Uzbekistan | 1.8-0.5 | 1-0 | 69%/21%/10% | rising |
| 2026-06-23 | Colombia v Congo DR | 1.7-0.8 | 1-0 | 58%/24%/18% | rising |
| 2026-06-23 | England v Ghana | 1.9-0.7 | 1-0 | 67%/21%/12% | rising |
| 2026-06-23 | Panama v Croatia | 0.8-1.6 | 0-1 | 19%/25%/56% | dipping |
| 2026-06-24 | Morocco v Haiti | 1.8-0.6 | 1-0 | 66%/22%/12% | rising |
| 2026-06-24 | Bosnia-Herzegovina v Qatar | 1.7-1.0 | 1-0 | 53%/24%/23% | dipping |
| 2026-06-24 | Scotland v Brazil | 0.9-2.0 | 0-1 | 16%/20%/63% | steady |
| 2026-06-24 | South Africa v South Korea | 0.9-0.8 | 0-0 | 36%/33%/31% | dipping |
| 2026-06-24 | Mexico v Czechia | 1.9-0.8 | 1-0 | 62%/22%/16% | rising |
| 2026-06-24 | Canada v Switzerland | 1.4-1.3 | 1-1 | 38%/26%/36% | red-hot |

## Current group standings (played)

| Team | P | Pts | GD |
|---|---|---|---|
| Germany | 2 | 6 | +7 |
| United States | 2 | 6 | +5 |
| Mexico | 2 | 6 | +3 |
| Canada | 2 | 4 | +6 |
| Netherlands | 2 | 4 | +4 |
| Japan | 2 | 4 | +4 |
| Switzerland | 2 | 4 | +3 |
| Brazil | 2 | 4 | +3 |
| Morocco | 2 | 4 | +1 |
| Norway | 1 | 3 | +3 |
| Argentina | 1 | 3 | +3 |
| France | 1 | 3 | +2 |
| Austria | 1 | 3 | +2 |
| Colombia | 1 | 3 | +2 |
| England | 1 | 3 | +2 |
| Ghana | 1 | 3 | +1 |
| South Korea | 2 | 3 | +0 |
| Scotland | 2 | 3 | +0 |
| Australia | 2 | 3 | +0 |
| Ivory Coast | 2 | 3 | +0 |
| Sweden | 2 | 3 | +0 |
| Paraguay | 2 | 3 | -2 |
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
| Ecuador | 2 | 1 | -1 |
| South Africa | 2 | 1 | -2 |
| Bosnia-Herzegovina | 2 | 1 | -3 |
| Qatar | 2 | 1 | -6 |
| Curaçao | 2 | 1 | -6 |
| Panama | 1 | 0 | -1 |
| Senegal | 1 | 0 | -2 |
| Jordan | 1 | 0 | -2 |
| Uzbekistan | 1 | 0 | -2 |
| Croatia | 1 | 0 | -2 |
| Türkiye | 2 | 0 | -3 |
| Iraq | 1 | 0 | -3 |
| Algeria | 1 | 0 | -3 |
| Haiti | 2 | 0 | -4 |
| Tunisia | 2 | 0 | -8 |

## What feeds the prediction

- **Player skillsets** — squad ratings (pace/shooting/passing/…) and seniority form the model's prior, so squad quality shapes goals.
- **Current results** — the posterior is fit on matches through today and the simulation holds played games fixed.
- **Form + X/ESPN sentiment** — folded in as a small, capped goal-rate nudge (see `models/momentum.py`, `data/scouting.py`).
- **Charts:** `artifacts/champion_tracker.png` (title odds), `artifacts/forecast_probs.png`, `artifacts/calibration.png`.