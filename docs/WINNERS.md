# 🔮 WC 2026 — Winners: next-day picks + champion scorecard

_A simple **Elo** model, conditioned on the **88 matches played so far** and the real 2026 bracket. Updated 2026-07-04._

## Next match day — who wins (Elo goals model)

_Elo gap → two Poisson scoring rates → 1X2 + likely score. Date: **2026-07-05**._

| Fixture | Elo | Pred goals | Likely | P(H/D/A) | **Pick** |
|---|---|---|---|---|---|
| Brazil v Norway | 1693 v 1537 | 1.7-1.1 | 1-1 | 52%/24%/24% | **Brazil** (52%) |
| Mexico v England | 1652 v 1621 | 1.6-1.2 | 1-1 | 46%/25%/29% | **Mexico** (46%) |

## Champion scorecard — simulated from today's state

_8,000 Elo tournaments. Played group games are held fixed; the rest of the groups + the knockout bracket are simulated. Teams already out fall to ~0%._

| # | Team | R16 | QF | SF | Final | **Champion** |
|--:|---|---|---|---|---|---|
| 1 | France | 90% | 49% | 27% | 17% | **13%** |
| 2 | Spain | 90% | 49% | 26% | 16% | **12%** |
| 3 | Argentina | 89% | 52% | 26% | 17% | **12%** |
| 4 | Brazil | 81% | 48% | 30% | 13% | **9%** |
| 5 | Portugal | 83% | 42% | 20% | 12% | **8%** |
| 6 | Colombia | 77% | 40% | 23% | 10% | **6%** |
| 7 | England | 67% | 38% | 22% | 14% | **6%** |
| 8 | Mexico | 73% | 44% | 21% | 8% | **5%** |
| 9 | Netherlands | 63% | 36% | 19% | 11% | **4%** |
| 10 | Morocco | 65% | 36% | 20% | 12% | **4%** |
| 11 | Switzerland | 67% | 35% | 16% | 6% | **3%** |
| 12 | Belgium | 60% | 31% | 15% | 9% | **3%** |
| 13 | Germany | 57% | 31% | 18% | 8% | **2%** |
| 14 | Japan | 56% | 28% | 15% | 7% | **2%** |
| 15 | Ecuador | 54% | 28% | 14% | 6% | **2%** |
| 16 | Norway | 51% | 25% | 12% | 5% | **1%** |

## Track record — predicted vs true winners (out-of-sample)

_Each WC match was predicted from Elo as it stood **before** that game (then the rating updated). Running accuracy: **61%** on 88 matches. Full log: `data/processed/winners_track.csv`._

| Date | Fixture | Score | Predicted | Actual | ✓ |
|---|---|---|---|---|:--:|
| 2026-06-30 | Ivory Coast v Norway | 1-2 | Ivory Coast | **Norway** | — |
| 2026-06-30 | France v Sweden | 3-0 | France | **France** | ✅ |
| 2026-06-30 | Mexico v Ecuador | 2-0 | Mexico | **Mexico** | ✅ |
| 2026-07-01 | England v Congo DR | 2-1 | England | **England** | ✅ |
| 2026-07-01 | Belgium v Senegal | 3-2 | Belgium | **Belgium** | ✅ |
| 2026-07-01 | United States v Bosnia-Herzegovina | 2-0 | United States | **United States** | ✅ |
| 2026-07-02 | Spain v Austria | 3-0 | Spain | **Spain** | ✅ |
| 2026-07-02 | Portugal v Croatia | 2-1 | Portugal | **Portugal** | ✅ |
| 2026-07-02 | Switzerland v Algeria | 2-0 | Switzerland | **Switzerland** | ✅ |
| 2026-07-03 | Australia v Egypt | 1-1 | Egypt | **Draw** | — |
| 2026-07-03 | Argentina v Cape Verde | 3-2 | Argentina | **Argentina** | ✅ |
| 2026-07-03 | Colombia v Ghana | 1-0 | Colombia | **Colombia** | ✅ |

_Showing the latest 12 of 88. Elo hit-rate vs a coin-flip baseline is the honest scoreboard for these picks._


## Method (simple by design)

- **Elo** is walked over all real results to today (recency- & WC-weighted K, goal-diff multiplier, host edge) — `models/elo.py`.
- **Goals**: Elo gap → two Poisson rates around a 1.35-goal baseline; the scoreline distribution gives 1X2.
- **Conditioning**: completed group games are fixed, so the scorecard reflects the actual standings — not a fresh re-roll.
- **LLM judge** (`--llm`) is an optional qualitative overlay on the next-day picks; see `models/llm_judge.py`.
- For the fuller Bayesian goals model (squad-skill prior + form + sentiment) see [CHAMPION_TRACKER.md](CHAMPION_TRACKER.md).