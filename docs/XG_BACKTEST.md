# xG model vs goals model — backtest

_Fit on 102 matches, scored on 26 held-out matches (40 teams), using real per-match xG from StatsBomb open data (2018 + 2022 World Cups). Lower RPS/log-loss is better._

| Model | RPS ↓ | log-loss ↓ | hit-rate ↑ | goals MAE ↓ |
|---|---|---|---|---|
| goals | 0.2319 | 1.0734 | 0.423 | 1.447 |
| xG (expected goals) | 0.2294 | 1.0554 | 0.577 | 1.394 |

**RPS delta (xG − goals): -0.0025 → xG WINS — keep it.**

xG is a less-noisy measure of chance quality than goals, so abilities learned from it generalize better (a side that created more but lost is rated by what it created). Small test sample — directional, not final. Regenerate with `make xg-backtest` after `make fetch-xg`.

**Live use:** switching the 2026 forecast to xG needs per-match xG for current matches (StatsBomb hasn't released 2026; FBref match-report scraping is the fallback). Until then the live pipeline uses the goals model and this validates xG as the upgrade path.