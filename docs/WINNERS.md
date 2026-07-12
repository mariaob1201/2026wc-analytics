# 🔮 WC 2026 — Winners: next-day picks + champion scorecard

_A simple **Elo** model, conditioned on the **98 matches played so far** and the real 2026 bracket. Updated 2026-07-12._

## Next match day — who wins (Elo goals model)

_No upcoming fixtures in the feed._


## Champion scorecard — simulated from today's state

_8,000 Elo tournaments. Played group games are held fixed; the rest of the groups + the knockout bracket are simulated. Teams already out fall to ~0%._

| # | Team | R16 | QF | SF | Final | **Champion** |
|--:|---|---|---|---|---|---|
| 1 | Spain | 92% | 49% | 30% | 21% | **16%** |
| 2 | France | 92% | 49% | 29% | 21% | **16%** |
| 3 | Argentina | 90% | 58% | 27% | 17% | **13%** |
| 4 | Belgium | 71% | 40% | 23% | 14% | **6%** |
| 5 | England | 77% | 43% | 25% | 9% | **6%** |
| 6 | Colombia | 78% | 43% | 25% | 9% | **6%** |
| 7 | Portugal | 81% | 36% | 14% | 8% | **5%** |
| 8 | Brazil | 74% | 45% | 23% | 8% | **5%** |
| 9 | Mexico | 66% | 37% | 20% | 12% | **4%** |
| 10 | Morocco | 68% | 38% | 21% | 12% | **4%** |
| 11 | Netherlands | 64% | 34% | 17% | 10% | **3%** |
| 12 | Switzerland | 72% | 38% | 18% | 6% | **3%** |
| 13 | Norway | 58% | 32% | 18% | 8% | **2%** |
| 14 | Germany | 58% | 30% | 16% | 8% | **2%** |
| 15 | Japan | 56% | 30% | 15% | 7% | **2%** |
| 16 | Ecuador | 52% | 26% | 12% | 6% | **2%** |

## Track record — predicted vs true winners (out-of-sample)

_Each WC match was predicted from Elo as it stood **before** that game (then the rating updated). Running accuracy: **62%** on 98 matches. Full log: `data/processed/winners_track.csv`._

| Date | Fixture | Score | Predicted | Actual | ✓ |
|---|---|---|---|---|:--:|
| 2026-07-03 | Australia v Egypt | 1-1 | Egypt | **Draw** | — |
| 2026-07-03 | Argentina v Cape Verde | 3-2 | Argentina | **Argentina** | ✅ |
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

_Showing the latest 12 of 98. Elo hit-rate vs a coin-flip baseline is the honest scoreboard for these picks._


## Method (simple by design)

- **Elo** is walked over all real results to today (recency- & WC-weighted K, goal-diff multiplier, host edge) — `models/elo.py`.
- **Goals**: Elo gap → two Poisson rates around a 1.35-goal baseline; the scoreline distribution gives 1X2.
- **Conditioning**: completed group games are fixed, so the scorecard reflects the actual standings — not a fresh re-roll.
- **LLM judge** (`--llm`) is an optional qualitative overlay on the next-day picks; see `models/llm_judge.py`.
- For the fuller Bayesian goals model (squad-skill prior + form + sentiment) see [CHAMPION_TRACKER.md](CHAMPION_TRACKER.md).