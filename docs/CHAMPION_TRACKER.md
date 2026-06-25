# 🏆 World Cup 2026 — Champion Tracker

_A living, state-aware forecast. Conditioned on the **54 matches played so far**: completed group games are held fixed; the rest of the tournament is simulated from a Bayesian goals model (squad-skill prior + current form + X/ESPN sentiment). Updated 2026-06-25._

## How to read this

1. **Next games** — predicted goals for the upcoming fixtures.
2. **The trophy** — each team's title probability, given everything that has already happened.

Both come from one model: goals are the primitive; the winner is a simulation over goals. See [METHODOLOGY.md](METHODOLOGY.md).

## Title odds — conditioned on current results

![Title probabilities](../artifacts/champion_tracker.png)

| Team | Quarter | Semi | Final | **Champion** |
|---|---|---|---|---|
| Argentina | 49% | 27% | 18% | **13%** |
| Portugal | 47% | 26% | 16% | **11%** |
| France | 46% | 24% | 13% | **9%** |
| Brazil | 45% | 23% | 11% | **8%** |
| Belgium | 39% | 22% | 11% | **6%** |
| Colombia | 43% | 22% | 11% | **6%** |
| Spain | 43% | 23% | 11% | **6%** |
| Germany | 42% | 21% | 10% | **6%** |
| Japan | 37% | 19% | 10% | **4%** |
| Switzerland | 32% | 17% | 8% | **3%** |
| Morocco | 32% | 17% | 8% | **3%** |
| Netherlands | 31% | 16% | 8% | **3%** |

_Mexico's Round-of-32 opponent odds (per candidate): [R32_ODDS.md](R32_ODDS.md) — `make r32-odds`._


## Next games — predicted goals

| Date | Fixture | Pred goals (xG) | Likely | P(H/D/A) | Home form |
|---|---|---|---|---|---|
| 2026-06-25 | United States v Türkiye | 2.1-1.1 | 2-1 | 60%/20%/20% | steady |
| 2026-06-25 | Paraguay v Australia | 0.9-0.9 | 0-0 | 33%/32%/35% | dipping |
| 2026-06-25 | Curaçao v Ivory Coast | 0.7-2.8 | 0-2 | 8%/14%/78% | cold |
| 2026-06-25 | Ecuador v Germany | 0.8-1.1 | 0-1 | 26%/31%/43% | steady |
| 2026-06-25 | Japan v Sweden | 2.6-1.0 | 2-0 | 70%/17%/14% | rising |
| 2026-06-25 | Tunisia v Netherlands | 0.7-2.1 | 0-2 | 11%/19%/70% | cold |
| 2026-06-26 | Senegal v Iraq | 1.5-0.6 | 1-0 | 60%/26%/14% | dipping |
| 2026-06-26 | Norway v France | 1.0-2.1 | 0-2 | 18%/20%/62% | rising |
| 2026-06-26 | Uruguay v Spain | 1.0-1.6 | 0-1 | 24%/25%/52% | steady |
| 2026-06-26 | New Zealand v Belgium | 0.5-2.5 | 0-2 | 6%/14%/80% | cold |
| 2026-06-26 | Egypt v Iran | 1.1-0.7 | 1-0 | 45%/31%/23% | steady |
| 2026-06-26 | Cape Verde v Saudi Arabia | 1.1-0.5 | 1-0 | 50%/34%/17% | steady |
| 2026-06-27 | Panama v England | 0.7-1.8 | 0-1 | 16%/23%/61% | dipping |
| 2026-06-27 | Algeria v Austria | 1.1-1.3 | 0-1 | 30%/27%/43% | steady |
| 2026-06-27 | Jordan v Argentina | 0.5-3.1 | 0-2 | 3%/9%/87% | dipping |
| 2026-06-27 | Colombia v Portugal | 1.1-1.5 | 1-1 | 29%/26%/45% | rising |
| 2026-06-27 | Congo DR v Uzbekistan | 1.2-0.6 | 1-0 | 51%/31%/18% | steady |
| 2026-06-27 | Croatia v Ghana | 1.4-0.6 | 1-0 | 56%/27%/17% | dipping |

## Current group standings (played)

| Team | P | Pts | GD |
|---|---|---|---|
| Mexico | 3 | 9 | +6 |
| Brazil | 3 | 7 | +6 |
| Switzerland | 3 | 7 | +4 |
| Morocco | 3 | 7 | +3 |
| Germany | 2 | 6 | +7 |
| United States | 2 | 6 | +5 |
| France | 2 | 6 | +5 |
| Argentina | 2 | 6 | +5 |
| Norway | 2 | 6 | +4 |
| Colombia | 2 | 6 | +3 |
| Canada | 3 | 4 | +5 |
| Portugal | 2 | 4 | +5 |
| Netherlands | 2 | 4 | +4 |
| Japan | 2 | 4 | +4 |
| Spain | 2 | 4 | +4 |
| Egypt | 2 | 4 | +2 |
| England | 2 | 4 | +2 |
| Ghana | 2 | 4 | +1 |
| South Africa | 3 | 4 | -1 |
| Bosnia-Herzegovina | 3 | 4 | -1 |
| Australia | 2 | 3 | +0 |
| Ivory Coast | 2 | 3 | +0 |
| Sweden | 2 | 3 | +0 |
| Austria | 2 | 3 | +0 |
| South Korea | 3 | 3 | -1 |
| Croatia | 2 | 3 | -1 |
| Paraguay | 2 | 3 | -2 |
| Algeria | 2 | 3 | -2 |
| Scotland | 3 | 3 | -3 |
| Belgium | 2 | 2 | +0 |
| Iran | 2 | 2 | +0 |
| Cape Verde | 2 | 2 | +0 |
| Uruguay | 2 | 2 | +0 |
| Ecuador | 2 | 1 | -1 |
| Congo DR | 2 | 1 | -1 |
| New Zealand | 2 | 1 | -2 |
| Czechia | 3 | 1 | -4 |
| Saudi Arabia | 2 | 1 | -4 |
| Curaçao | 2 | 1 | -6 |
| Qatar | 3 | 1 | -8 |
| Panama | 2 | 0 | -2 |
| Türkiye | 2 | 0 | -3 |
| Senegal | 2 | 0 | -3 |
| Jordan | 2 | 0 | -3 |
| Haiti | 3 | 0 | -6 |
| Iraq | 2 | 0 | -6 |
| Uzbekistan | 2 | 0 | -7 |
| Tunisia | 2 | 0 | -8 |

## What feeds the prediction

- **Player skillsets** — squad ratings (pace/shooting/passing/…) and seniority form the model's prior, so squad quality shapes goals.
- **Current results** — the posterior is fit on matches through today and the simulation holds played games fixed.
- **Form + X/ESPN sentiment** — folded in as a small, capped goal-rate nudge (see `models/momentum.py`, `data/scouting.py`).
- **Charts:** `artifacts/champion_tracker.png` (title odds), `artifacts/forecast_probs.png`, `artifacts/calibration.png`.