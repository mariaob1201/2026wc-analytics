# 🔮 WC 2026 — Winners: next-day picks + champion scorecard

_A simple **Elo** model, conditioned on the **92 matches played so far** and the real 2026 bracket. Updated 2026-07-06._

## Next match day — who wins (Elo goals model)

_Elo gap → two Poisson scoring rates → 1X2 + likely score. Date: **2026-07-09**._

| Fixture | Elo | Pred goals | Likely | P(H/D/A) | **Pick** |
|---|---|---|---|---|---|
| France v Morocco | 1763 v 1647 | 1.6-1.1 | 1-1 | 48%/25%/27% | **France** (48%) |

## Champion scorecard — simulated from today's state

_8,000 Elo tournaments. Played group games are held fixed; the rest of the groups + the knockout bracket are simulated. Teams already out fall to ~0%._

| # | Team | R16 | QF | SF | Final | **Champion** |
|--:|---|---|---|---|---|---|
| 1 | France | 91% | 50% | 29% | 19% | **14%** |
| 2 | Argentina | 89% | 52% | 26% | 17% | **12%** |
| 3 | Spain | 90% | 47% | 25% | 16% | **12%** |
| 4 | Portugal | 83% | 42% | 20% | 12% | **8%** |
| 5 | Colombia | 78% | 44% | 25% | 10% | **6%** |
| 6 | England | 77% | 43% | 24% | 10% | **6%** |
| 7 | Switzerland | 69% | 39% | 23% | 14% | **6%** |
| 8 | Morocco | 74% | 44% | 22% | 8% | **5%** |
| 9 | Mexico | 66% | 36% | 20% | 12% | **4%** |
| 10 | Netherlands | 63% | 35% | 19% | 11% | **4%** |
| 11 | Brazil | 71% | 38% | 19% | 7% | **4%** |
| 12 | Norway | 62% | 32% | 16% | 9% | **3%** |
| 13 | Belgium | 59% | 33% | 19% | 9% | **3%** |
| 14 | Germany | 57% | 29% | 16% | 7% | **2%** |
| 15 | Japan | 56% | 30% | 15% | 7% | **2%** |
| 16 | Ecuador | 52% | 26% | 12% | 6% | **2%** |

## Track record — predicted vs true winners (out-of-sample)

_Each WC match was predicted from Elo as it stood **before** that game (then the rating updated). Running accuracy: **61%** on 92 matches. Full log: `data/processed/winners_track.csv`._

| Date | Fixture | Score | Predicted | Actual | ✓ |
|---|---|---|---|---|:--:|
| 2026-07-01 | England v Congo DR | 2-1 | England | **England** | ✅ |
| 2026-07-01 | Belgium v Senegal | 3-2 | Belgium | **Belgium** | ✅ |
| 2026-07-02 | Spain v Austria | 3-0 | Spain | **Spain** | ✅ |
| 2026-07-02 | Portugal v Croatia | 2-1 | Portugal | **Portugal** | ✅ |
| 2026-07-02 | Switzerland v Algeria | 2-0 | Switzerland | **Switzerland** | ✅ |
| 2026-07-03 | Australia v Egypt | 1-1 | Egypt | **Draw** | — |
| 2026-07-03 | Argentina v Cape Verde | 3-2 | Argentina | **Argentina** | ✅ |
| 2026-07-03 | Colombia v Ghana | 1-0 | Colombia | **Colombia** | ✅ |
| 2026-07-04 | Canada v Morocco | 0-3 | Morocco | **Morocco** | ✅ |
| 2026-07-04 | Paraguay v France | 0-1 | France | **France** | ✅ |
| 2026-07-05 | Brazil v Norway | 0-2 | Brazil | **Norway** | — |
| 2026-07-05 | Mexico v England | 2-3 | Mexico | **England** | — |

_Showing the latest 12 of 92. Elo hit-rate vs a coin-flip baseline is the honest scoreboard for these picks._


## Method (simple by design)

- **Elo** is walked over all real results to today (recency- & WC-weighted K, goal-diff multiplier, host edge) — `models/elo.py`.
- **Goals**: Elo gap → two Poisson rates around a 1.35-goal baseline; the scoreline distribution gives 1X2.
- **Conditioning**: completed group games are fixed, so the scorecard reflects the actual standings — not a fresh re-roll.
- **LLM judge** (`--llm`) is an optional qualitative overlay on the next-day picks; see `models/llm_judge.py`.
- For the fuller Bayesian goals model (squad-skill prior + form + sentiment) see [CHAMPION_TRACKER.md](CHAMPION_TRACKER.md).