# 🔮 WC 2026 — Winners: next-day picks + champion scorecard

_A simple **Elo** model, conditioned on the **97 matches played so far** and the real 2026 bracket. Updated 2026-07-10._

## Next match day — who wins (Elo goals model)

_Elo gap → two Poisson scoring rates → 1X2 + likely score. Date: **2026-07-11**._

| Fixture | Elo | Pred goals | Likely | P(H/D/A) | **Pick** |
|---|---|---|---|---|---|
| Norway v England | 1579 v 1659 | 1.2-1.5 | 1-1 | 30%/25%/44% | **England** (44%) |
| Argentina v Switzerland | 1752 v 1627 | 1.6-1.1 | 1-1 | 49%/25%/27% | **Argentina** (49%) |

## Champion scorecard — simulated from today's state

_8,000 Elo tournaments. Played group games are held fixed; the rest of the groups + the knockout bracket are simulated. Teams already out fall to ~0%._

| # | Team | R16 | QF | SF | Final | **Champion** |
|--:|---|---|---|---|---|---|
| 1 | France | 92% | 51% | 31% | 22% | **17%** |
| 2 | Spain | 91% | 47% | 27% | 18% | **14%** |
| 3 | Argentina | 90% | 58% | 28% | 18% | **13%** |
| 4 | Switzerland | 72% | 40% | 24% | 15% | **6%** |
| 5 | England | 77% | 43% | 24% | 9% | **6%** |
| 6 | Colombia | 78% | 43% | 24% | 9% | **6%** |
| 7 | Portugal | 81% | 36% | 14% | 8% | **5%** |
| 8 | Brazil | 74% | 44% | 22% | 8% | **5%** |
| 9 | Belgium | 73% | 40% | 20% | 7% | **4%** |
| 10 | Mexico | 66% | 37% | 20% | 11% | **4%** |
| 11 | Morocco | 68% | 37% | 21% | 12% | **4%** |
| 12 | Netherlands | 64% | 34% | 17% | 10% | **3%** |
| 13 | Norway | 58% | 32% | 18% | 8% | **2%** |
| 14 | Germany | 58% | 30% | 16% | 8% | **2%** |
| 15 | Japan | 56% | 30% | 15% | 7% | **2%** |
| 16 | Ecuador | 52% | 26% | 12% | 6% | **2%** |

## Track record — predicted vs true winners (out-of-sample)

_Each WC match was predicted from Elo as it stood **before** that game (then the rating updated). Running accuracy: **62%** on 97 matches. Full log: `data/processed/winners_track.csv`._

| Date | Fixture | Score | Predicted | Actual | ✓ |
|---|---|---|---|---|:--:|
| 2026-07-03 | Argentina v Cape Verde | 3-2 | Argentina | **Argentina** | ✅ |
| 2026-07-03 | Colombia v Ghana | 1-0 | Colombia | **Colombia** | ✅ |
| 2026-07-03 | Australia v Egypt | 1-1 | Egypt | **Draw** | — |
| 2026-07-04 | Canada v Morocco | 0-3 | Morocco | **Morocco** | ✅ |
| 2026-07-04 | Paraguay v France | 0-1 | France | **France** | ✅ |
| 2026-07-05 | Brazil v Norway | 1-2 | Brazil | **Norway** | — |
| 2026-07-05 | Mexico v England | 2-3 | Mexico | **England** | — |
| 2026-07-06 | Portugal v Spain | 0-1 | Spain | **Spain** | ✅ |
| 2026-07-06 | United States v Belgium | 1-4 | Belgium | **Belgium** | ✅ |
| 2026-07-07 | Argentina v Egypt | 3-2 | Argentina | **Argentina** | ✅ |
| 2026-07-07 | Switzerland v Colombia | 0-0 | Colombia | **Draw** | — |
| 2026-07-09 | France v Morocco | 2-0 | France | **France** | ✅ |

_Showing the latest 12 of 97. Elo hit-rate vs a coin-flip baseline is the honest scoreboard for these picks._


## Method (simple by design)

- **Elo** is walked over all real results to today (recency- & WC-weighted K, goal-diff multiplier, host edge) — `models/elo.py`.
- **Goals**: Elo gap → two Poisson rates around a 1.35-goal baseline; the scoreline distribution gives 1X2.
- **Conditioning**: completed group games are fixed, so the scorecard reflects the actual standings — not a fresh re-roll.
- **LLM judge** (`--llm`) is an optional qualitative overlay on the next-day picks; see `models/llm_judge.py`.
- For the fuller Bayesian goals model (squad-skill prior + form + sentiment) see [CHAMPION_TRACKER.md](CHAMPION_TRACKER.md).