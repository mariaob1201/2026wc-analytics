# 🔮 WC 2026 — Winners: next-day picks + champion scorecard

_A simple **Elo** model, conditioned on the **72 matches played so far** and the real 2026 bracket. Updated 2026-06-28._

## Next match day — who wins (Elo goals model)

_Elo gap → two Poisson scoring rates → 1X2 + likely score. Date: **2026-06-29**._

| Fixture | Elo | Pred goals | Likely | P(H/D/A) | **Pick** |
|---|---|---|---|---|---|
| Germany v Paraguay | 1580 v 1492 | 1.5-1.2 | 1-1 | 45%/25%/30% | **Germany** (45%) |
| Netherlands v Morocco | 1608 v 1612 | 1.3-1.4 | 1-1 | 37%/26%/37% | **Morocco** (37%) |
| Brazil v Japan | 1670 v 1586 | 1.5-1.2 | 1-1 | 45%/25%/30% | **Brazil** (45%) |

## Champion scorecard — simulated from today's state

_8,000 Elo tournaments. Played group games are held fixed; the rest of the groups + the knockout bracket are simulated. Teams already out fall to ~0%._

| # | Team | R16 | QF | SF | Final | **Champion** |
|--:|---|---|---|---|---|---|
| 1 | France | 89% | 49% | 28% | 18% | **13%** |
| 2 | Spain | 87% | 51% | 26% | 17% | **12%** |
| 3 | Argentina | 87% | 46% | 24% | 16% | **11%** |
| 4 | Portugal | 81% | 42% | 20% | 12% | **8%** |
| 5 | Brazil | 77% | 45% | 28% | 12% | **8%** |
| 6 | Colombia | 74% | 40% | 24% | 10% | **6%** |
| 7 | Netherlands | 67% | 37% | 21% | 13% | **6%** |
| 8 | Mexico | 68% | 39% | 18% | 7% | **4%** |
| 9 | England | 65% | 35% | 20% | 11% | **4%** |
| 10 | Morocco | 67% | 36% | 17% | 6% | **3%** |
| 11 | Japan | 62% | 34% | 18% | 9% | **3%** |
| 12 | Switzerland | 59% | 32% | 16% | 8% | **3%** |
| 13 | Ecuador | 57% | 31% | 17% | 8% | **3%** |
| 14 | Germany | 57% | 29% | 16% | 8% | **3%** |
| 15 | Ivory Coast | 51% | 26% | 13% | 6% | **2%** |
| 16 | Belgium | 54% | 28% | 14% | 7% | **2%** |

## Track record — predicted vs true winners (out-of-sample)

_Each WC match was predicted from Elo as it stood **before** that game (then the rating updated). Running accuracy: **60%** on 72 matches. Full log: `data/processed/winners_track.csv`._

| Date | Fixture | Score | Predicted | Actual | ✓ |
|---|---|---|---|---|:--:|
| 2026-06-26 | Cape Verde v Saudi Arabia | 0-0 | Cape Verde | **Draw** | — |
| 2026-06-26 | Egypt v Iran | 1-1 | Egypt | **Draw** | — |
| 2026-06-26 | New Zealand v Belgium | 1-5 | Belgium | **Belgium** | ✅ |
| 2026-06-26 | Norway v France | 1-4 | France | **France** | ✅ |
| 2026-06-26 | Senegal v Iraq | 5-0 | Senegal | **Senegal** | ✅ |
| 2026-06-26 | Uruguay v Spain | 0-1 | Spain | **Spain** | ✅ |
| 2026-06-27 | Congo DR v Uzbekistan | 3-1 | Congo DR | **Congo DR** | ✅ |
| 2026-06-27 | Panama v England | 0-2 | England | **England** | ✅ |
| 2026-06-27 | Algeria v Austria | 3-3 | Austria | **Draw** | — |
| 2026-06-27 | Jordan v Argentina | 1-3 | Argentina | **Argentina** | ✅ |
| 2026-06-27 | Colombia v Portugal | 0-0 | Portugal | **Draw** | — |
| 2026-06-27 | Croatia v Ghana | 2-1 | Croatia | **Croatia** | ✅ |

_Showing the latest 12 of 72. Elo hit-rate vs a coin-flip baseline is the honest scoreboard for these picks._


## Method (simple by design)

- **Elo** is walked over all real results to today (recency- & WC-weighted K, goal-diff multiplier, host edge) — `models/elo.py`.
- **Goals**: Elo gap → two Poisson rates around a 1.35-goal baseline; the scoreline distribution gives 1X2.
- **Conditioning**: completed group games are fixed, so the scorecard reflects the actual standings — not a fresh re-roll.
- **LLM judge** (`--llm`) is an optional qualitative overlay on the next-day picks; see `models/llm_judge.py`.
- For the fuller Bayesian goals model (squad-skill prior + form + sentiment) see [CHAMPION_TRACKER.md](CHAMPION_TRACKER.md).