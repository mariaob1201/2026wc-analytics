# 🔮 WC 2026 — Winners: next-day picks + champion scorecard

_A simple **Elo** model, conditioned on the **102 matches played so far** and the real 2026 bracket. Updated 2026-07-16._

## Next match day — who wins (Elo goals model)

_Elo gap → two Poisson scoring rates → 1X2 + likely score. Date: **2026-07-18**._

| Fixture | Elo | Pred goals | Likely | P(H/D/A) | **Pick** |
|---|---|---|---|---|---|
| France v England | 1749 v 1661 | 1.5-1.2 | 1-1 | 45%/25%/30% | **France** (45%) |

## Champion scorecard — simulated from today's state

_8,000 Elo tournaments. Played group games are held fixed; the rest of the groups + the knockout bracket are simulated. Teams already out fall to ~0%._

| # | Team | R16 | QF | SF | Final | **Champion** |
|--:|---|---|---|---|---|---|
| 1 | Spain | 94% | 54% | 36% | 27% | **22%** |
| 2 | Argentina | 92% | 45% | 28% | 20% | **16%** |
| 3 | France | 90% | 57% | 24% | 15% | **11%** |
| 4 | Colombia | 77% | 43% | 25% | 9% | **6%** |
| 5 | Morocco | 70% | 39% | 23% | 14% | **5%** |
| 6 | England | 78% | 44% | 25% | 8% | **5%** |
| 7 | Portugal | 81% | 37% | 12% | 7% | **5%** |
| 8 | Brazil | 74% | 45% | 23% | 7% | **5%** |
| 9 | Netherlands | 65% | 37% | 20% | 11% | **4%** |
| 10 | Mexico | 67% | 37% | 21% | 12% | **4%** |
| 11 | Belgium | 71% | 37% | 18% | 5% | **3%** |
| 12 | Switzerland | 62% | 33% | 16% | 9% | **3%** |
| 13 | Germany | 57% | 31% | 17% | 8% | **2%** |
| 14 | Norway | 55% | 29% | 15% | 7% | **2%** |
| 15 | Japan | 57% | 29% | 15% | 7% | **2%** |
| 16 | Ecuador | 52% | 26% | 13% | 6% | **2%** |

## Track record — predicted vs true winners (out-of-sample)

_Each WC match was predicted from Elo as it stood **before** that game (then the rating updated). Running accuracy: **64%** on 102 matches. Full log: `data/processed/winners_track.csv`._

| Date | Fixture | Score | Predicted | Actual | ✓ |
|---|---|---|---|---|:--:|
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
| 2026-07-14 | France v Spain | 0-2 | Spain | **Spain** | ✅ |
| 2026-07-15 | England v Argentina | 1-2 | Argentina | **Argentina** | ✅ |

_Showing the latest 12 of 102. Elo hit-rate vs a coin-flip baseline is the honest scoreboard for these picks._


## Method (simple by design)

- **Elo** is walked over all real results to today (recency- & WC-weighted K, goal-diff multiplier, host edge) — `models/elo.py`.
- **Goals**: Elo gap → two Poisson rates around a 1.35-goal baseline; the scoreline distribution gives 1X2.
- **Conditioning**: completed group games are fixed, so the scorecard reflects the actual standings — not a fresh re-roll.
- **LLM judge** (`--llm`) is an optional qualitative overlay on the next-day picks; see `models/llm_judge.py`.
- For the fuller Bayesian goals model (squad-skill prior + form + sentiment) see [CHAMPION_TRACKER.md](CHAMPION_TRACKER.md).