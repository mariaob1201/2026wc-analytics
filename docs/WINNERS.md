# 🔮 WC 2026 — Winners: next-day picks + champion scorecard

_A simple **Elo** model, conditioned on the **100 matches played so far** and the real 2026 bracket. Updated 2026-07-14._

## Next match day — who wins (Elo goals model)

_Elo gap → two Poisson scoring rates → 1X2 + likely score. Date: **2026-07-15**._

| Fixture | Elo | Pred goals | Likely | P(H/D/A) | **Pick** |
|---|---|---|---|---|---|
| England v Argentina | 1682 v 1782 | 1.2-1.6 | 1-1 | 29%/25%/46% | **Argentina** (46%) |

## Champion scorecard — simulated from today's state

_8,000 Elo tournaments. Played group games are held fixed; the rest of the groups + the knockout bracket are simulated. Teams already out fall to ~0%._

| # | Team | R16 | QF | SF | Final | **Champion** |
|--:|---|---|---|---|---|---|
| 1 | Argentina | 91% | 62% | 31% | 21% | **17%** |
| 2 | Spain | 92% | 49% | 28% | 20% | **15%** |
| 3 | France | 92% | 49% | 28% | 19% | **15%** |
| 4 | England | 80% | 47% | 28% | 10% | **7%** |
| 5 | Morocco | 70% | 39% | 23% | 14% | **5%** |
| 6 | Colombia | 77% | 41% | 23% | 8% | **5%** |
| 7 | Brazil | 74% | 45% | 22% | 8% | **5%** |
| 8 | Portugal | 81% | 33% | 12% | 7% | **4%** |
| 9 | Mexico | 67% | 37% | 21% | 12% | **4%** |
| 10 | Netherlands | 65% | 37% | 20% | 11% | **4%** |
| 11 | Switzerland | 62% | 33% | 16% | 9% | **3%** |
| 12 | Belgium | 71% | 37% | 17% | 5% | **3%** |
| 13 | Germany | 57% | 31% | 17% | 8% | **2%** |
| 14 | Norway | 55% | 29% | 15% | 7% | **2%** |
| 15 | Japan | 57% | 29% | 15% | 7% | **2%** |
| 16 | Ecuador | 52% | 26% | 13% | 6% | **2%** |

## Track record — predicted vs true winners (out-of-sample)

_Each WC match was predicted from Elo as it stood **before** that game (then the rating updated). Running accuracy: **63%** on 100 matches. Full log: `data/processed/winners_track.csv`._

| Date | Fixture | Score | Predicted | Actual | ✓ |
|---|---|---|---|---|:--:|
| 2026-07-04 | Canada v Morocco | 0-3 | Morocco | **Morocco** | ✅ |
| 2026-07-04 | Paraguay v France | 0-1 | France | **France** | ✅ |
| 2026-07-05 | Brazil v Norway | 1-2 | Brazil | **Norway** | — |
| 2026-07-05 | Mexico v England | 2-3 | Mexico | **England** | — |
| 2026-07-06 | Portugal v Spain | 0-1 | Spain | **Spain** | ✅ |
| 2026-07-06 | United States v Belgium | 1-4 | Belgium | **Belgium** | ✅ |
| 2026-07-07 | Argentina v Egypt | 3-2 | Argentina | **Argentina** | ✅ |
| 2026-07-07 | Switzerland v Colombia | 0-0 | Colombia | **Draw** | — |
| 2026-07-09 | France v Morocco | 2-0 | France | **France** | ✅ |
| 2026-07-10 | Spain v Belgium | 2-1 | Spain | **Spain** | ✅ |
| 2026-07-11 | Norway v England | 1-2 | England | **England** | ✅ |
| 2026-07-11 | Argentina v Switzerland | 3-1 | Argentina | **Argentina** | ✅ |

_Showing the latest 12 of 100. Elo hit-rate vs a coin-flip baseline is the honest scoreboard for these picks._


## Method (simple by design)

- **Elo** is walked over all real results to today (recency- & WC-weighted K, goal-diff multiplier, host edge) — `models/elo.py`.
- **Goals**: Elo gap → two Poisson rates around a 1.35-goal baseline; the scoreline distribution gives 1X2.
- **Conditioning**: completed group games are fixed, so the scorecard reflects the actual standings — not a fresh re-roll.
- **LLM judge** (`--llm`) is an optional qualitative overlay on the next-day picks; see `models/llm_judge.py`.
- For the fuller Bayesian goals model (squad-skill prior + form + sentiment) see [CHAMPION_TRACKER.md](CHAMPION_TRACKER.md).