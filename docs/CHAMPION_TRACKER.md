# 🏆 World Cup 2026 — Champion Tracker

_A living, state-aware forecast. Conditioned on the **90 matches played so far**: completed group games are held fixed; the rest of the tournament is simulated from a Bayesian goals model (squad-skill prior + current form + X/ESPN sentiment). Updated 2026-07-05._

## How to read this

1. **Next games** — predicted goals for the upcoming fixtures.
2. **The trophy** — each team's title probability, given everything that has already happened.

Both come from one model: goals are the primitive; the winner is a simulation over goals. See [METHODOLOGY.md](METHODOLOGY.md).

## Title odds — conditioned on current results

![Title probabilities](../artifacts/champion_tracker.png)

| Team | Quarter | Semi | Final | **Champion** |
|---|---|---|---|---|
| France | 50% | 27% | 17% | **12%** |
| Argentina | 46% | 25% | 14% | **9%** |
| Portugal | 45% | 24% | 14% | **9%** |
| Spain | 46% | 23% | 12% | **8%** |
| Belgium | 44% | 24% | 12% | **8%** |
| Brazil | 44% | 23% | 12% | **8%** |
| Colombia | 40% | 21% | 11% | **6%** |
| Morocco | 38% | 20% | 9% | **5%** |
| Switzerland | 36% | 19% | 10% | **4%** |
| Germany | 37% | 19% | 9% | **4%** |
| Netherlands | 33% | 18% | 9% | **4%** |
| Japan | 35% | 18% | 9% | **4%** |

_Mexico's Round-of-32 opponent odds (per candidate): [R32_ODDS.md](R32_ODDS.md) — `make r32-odds`._


## Title odds over time — the movie, not the snapshot

_How each contender's championship probability moved as matches were played. The x-axis is the **cumulative number of matches played across all teams** (the group stage has 72 in total; each team plays 3), not games-per-team and not an abstract t. Built with a fast Elo simulation re-run after every matchday, conditioned only on results known by then — no look-ahead. `make timeline`._

![Title odds timeline](../artifacts/champion_timeline.png)


## Next games — predicted goals

| Date | Fixture | Pred goals (xG) | Likely | P(H/D/A) | Home form |
|---|---|---|---|---|---|
| 2026-07-05 | Mexico v England | 1.3-1.1 | 1-1 | 41%/27%/32% | red-hot |
| 2026-07-05 | Brazil v Norway | 2.5-1.3 | 2-1 | 62%/18%/19% | red-hot |
| 2026-07-06 | Argentina v Egypt | 1.9-0.9 | 1-0 | 62%/21%/17% | red-hot |
| 2026-07-06 | Switzerland v Colombia | 1.3-1.5 | 1-1 | 32%/25%/43% | red-hot |
| 2026-07-06 | Portugal v Spain | 1.3-1.2 | 1-1 | 39%/26%/35% | red-hot |
| 2026-07-06 | United States v Belgium | 1.4-2.6 | 1-2 | 19%/17%/63% | rising |
| 2026-07-09 | France v Morocco | 1.6-1.0 | 1-0 | 51%/25%/24% | red-hot |

## Current group standings (played)

| Team | P | Pts | GD |
|---|---|---|---|
| France | 5 | 15 | +12 |
| Mexico | 4 | 12 | +8 |
| Argentina | 4 | 12 | +8 |
| Morocco | 5 | 11 | +6 |
| Spain | 4 | 10 | +8 |
| Brazil | 4 | 10 | +7 |
| Switzerland | 4 | 10 | +6 |
| England | 4 | 10 | +5 |
| Colombia | 4 | 10 | +4 |
| United States | 4 | 9 | +6 |
| Norway | 4 | 9 | +2 |
| Netherlands | 4 | 8 | +6 |
| Portugal | 4 | 8 | +6 |
| Belgium | 4 | 8 | +5 |
| Germany | 4 | 7 | +6 |
| Canada | 5 | 7 | +3 |
| Egypt | 4 | 6 | +2 |
| Ivory Coast | 4 | 6 | +1 |
| Croatia | 4 | 6 | -1 |
| Japan | 4 | 5 | +3 |
| Australia | 4 | 5 | +0 |
| Paraguay | 5 | 5 | -3 |
| Congo DR | 4 | 4 | +0 |
| Ghana | 4 | 4 | -1 |
| South Africa | 4 | 4 | -2 |
| Ecuador | 4 | 4 | -2 |
| Bosnia-Herzegovina | 4 | 4 | -3 |
| Sweden | 4 | 4 | -3 |
| Austria | 4 | 4 | -3 |
| Algeria | 4 | 4 | -4 |
| Senegal | 4 | 3 | +1 |
| Iran | 3 | 3 | +0 |
| South Korea | 3 | 3 | -1 |
| Cape Verde | 4 | 3 | -1 |
| Türkiye | 3 | 3 | -2 |
| Scotland | 3 | 3 | -3 |
| Uruguay | 3 | 2 | -1 |
| Saudi Arabia | 3 | 2 | -4 |
| Czechia | 3 | 1 | -4 |
| New Zealand | 3 | 1 | -6 |
| Qatar | 3 | 1 | -8 |
| Curaçao | 3 | 1 | -8 |
| Panama | 3 | 0 | -4 |
| Jordan | 3 | 0 | -5 |
| Haiti | 3 | 0 | -6 |
| Uzbekistan | 3 | 0 | -9 |
| Tunisia | 3 | 0 | -10 |
| Iraq | 3 | 0 | -11 |

## What feeds the prediction

- **Player skillsets** — squad ratings (pace/shooting/passing/…) and seniority form the model's prior, so squad quality shapes goals.
- **Current results** — the posterior is fit on matches through today and the simulation holds played games fixed.
- **Form + X/ESPN sentiment** — folded in as a small, capped goal-rate nudge (see `models/momentum.py`, `data/scouting.py`).
- **Charts:** `artifacts/champion_tracker.png` (title odds), `artifacts/forecast_probs.png`, `artifacts/calibration.png`.