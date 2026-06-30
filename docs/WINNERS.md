# 🔮 WC 2026 — Winners: next-day picks + champion scorecard

_A simple **Elo** model, conditioned on the **76 matches played so far** and the real 2026 bracket. Updated 2026-06-30._

## Next match day — who wins (Elo goals model)

_Elo gap → two Poisson scoring rates → 1X2 + likely score. Date: **2026-07-01**._

| Fixture | Elo | Pred goals | Likely | P(H/D/A) | **Pick** |
|---|---|---|---|---|---|
| England v Congo DR | 1602 v 1466 | 1.6-1.1 | 1-1 | 50%/25%/26% | **England** (50%) |
| Belgium v Senegal | 1566 v 1496 | 1.5-1.2 | 1-1 | 44%/25%/31% | **Belgium** (44%) |
| United States v Bosnia-Herzegovina | 1489 v 1400 | 1.7-1.1 | 1-1 | 52%/24%/24% | **United States** (52%) |

## Champion scorecard — simulated from today's state

_8,000 Elo tournaments. Played group games are held fixed; the rest of the groups + the knockout bracket are simulated. Teams already out fall to ~0%._

| # | Team | R16 | QF | SF | Final | **Champion** |
|--:|---|---|---|---|---|---|
| 1 | France | 89% | 49% | 28% | 18% | **13%** |
| 2 | Spain | 87% | 51% | 26% | 16% | **12%** |
| 3 | Argentina | 87% | 46% | 24% | 15% | **11%** |
| 4 | Brazil | 80% | 49% | 32% | 15% | **10%** |
| 5 | Portugal | 81% | 42% | 20% | 12% | **8%** |
| 6 | Colombia | 74% | 37% | 22% | 10% | **6%** |
| 7 | Netherlands | 66% | 36% | 21% | 13% | **6%** |
| 8 | Mexico | 67% | 38% | 17% | 6% | **4%** |
| 9 | England | 64% | 35% | 20% | 11% | **4%** |
| 10 | Switzerland | 61% | 34% | 18% | 9% | **3%** |
| 11 | Morocco | 66% | 36% | 16% | 6% | **3%** |
| 12 | Ecuador | 59% | 31% | 15% | 8% | **3%** |
| 13 | Germany | 56% | 30% | 16% | 8% | **2%** |
| 14 | Japan | 51% | 26% | 13% | 7% | **2%** |
| 15 | Belgium | 55% | 28% | 14% | 7% | **2%** |
| 16 | Ivory Coast | 53% | 27% | 14% | 7% | **2%** |

## Track record — predicted vs true winners (out-of-sample)

_Each WC match was predicted from Elo as it stood **before** that game (then the rating updated). Running accuracy: **58%** on 76 matches. Full log: `data/processed/winners_track.csv`._

| Date | Fixture | Score | Predicted | Actual | ✓ |
|---|---|---|---|---|:--:|
| 2026-06-26 | Norway v France | 1-4 | France | **France** | ✅ |
| 2026-06-26 | Senegal v Iraq | 5-0 | Senegal | **Senegal** | ✅ |
| 2026-06-27 | Algeria v Austria | 3-3 | Austria | **Draw** | — |
| 2026-06-27 | Jordan v Argentina | 1-3 | Argentina | **Argentina** | ✅ |
| 2026-06-27 | Colombia v Portugal | 0-0 | Portugal | **Draw** | — |
| 2026-06-27 | Congo DR v Uzbekistan | 3-1 | Congo DR | **Congo DR** | ✅ |
| 2026-06-27 | Panama v England | 0-2 | England | **England** | ✅ |
| 2026-06-27 | Croatia v Ghana | 2-1 | Croatia | **Croatia** | ✅ |
| 2026-06-28 | South Africa v Canada | 0-1 | South Africa | **Canada** | — |
| 2026-06-29 | Brazil v Japan | 2-1 | Brazil | **Brazil** | ✅ |
| 2026-06-29 | Germany v Paraguay | 1-1 | Germany | **Draw** | — |
| 2026-06-29 | Netherlands v Morocco | 1-1 | Morocco | **Draw** | — |

_Showing the latest 12 of 76. Elo hit-rate vs a coin-flip baseline is the honest scoreboard for these picks._


## Method (simple by design)

- **Elo** is walked over all real results to today (recency- & WC-weighted K, goal-diff multiplier, host edge) — `models/elo.py`.
- **Goals**: Elo gap → two Poisson rates around a 1.35-goal baseline; the scoreline distribution gives 1X2.
- **Conditioning**: completed group games are fixed, so the scorecard reflects the actual standings — not a fresh re-roll.
- **LLM judge** (`--llm`) is an optional qualitative overlay on the next-day picks; see `models/llm_judge.py`.
- For the fuller Bayesian goals model (squad-skill prior + form + sentiment) see [CHAMPION_TRACKER.md](CHAMPION_TRACKER.md).