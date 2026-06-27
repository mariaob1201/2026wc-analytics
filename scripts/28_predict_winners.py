"""Stage 28: winners — next-day match picks + a champion scorecard.

One simple, transparent entry point that answers the two questions directly,
**conditioned on the real 2026 bracket and every game played up to today**:

  1. NEXT MATCH DAY — who wins each upcoming fixture? A simple Elo goals model
     (Elo gap -> two Poisson scoring rates -> 1X2 + likely scoreline).
  2. THE TROPHY — simulate the rest of the tournament thousands of times from
     the CURRENT state (played group games held fixed) and tally how often each
     surviving team lifts the cup. Output is a scorecard (R16 -> ... -> champion).

Both use ELO scoring by default (no API key, fully reproducible). Pass --llm to
re-judge the next-day fixtures with the LLM-as-a-Judge layer (OpenAI/Claude;
falls back to Elo if no key is set).

    python scripts/28_predict_winners.py            # Elo only
    python scripts/28_predict_winners.py --llm      # + LLM judge on next day
"""

import argparse

import pandas as pd

from wc2026.config import PROCESSED, ROOT, ensure_dirs
from wc2026.config import today as _today
from wc2026.data.sources import build_real_matches, wc2026_matches
from wc2026.data.teams import HOSTS, TEAMS, by_group
from wc2026.models.elo import elo_lookup, rolling_backtest, run_elo
from wc2026.models.elo_sim import N_SIMS_DEFAULT, elo_goals, poisson_1x2, simulate_champion

TOURNAMENT_START = "2026-06-11"
TODAY = _today()
N_SIMS = N_SIMS_DEFAULT


# --- Part 1: next match-day winner picks (simple Elo model) ----------------
def next_day_picks(elo: dict, rank: dict) -> pd.DataFrame:
    wc = wc2026_matches()
    # The "next match day" is the soonest fixture STRICTLY AFTER today — today's
    # slate has already kicked off, so the next forecastable day is tomorrow+.
    future = wc[wc["home_score"].isna() & (wc["date"] > TODAY)].sort_values("date")
    # Fall back to any remaining unplayed (e.g. a delayed/late-listed today game).
    unplayed = future if not future.empty else \
        wc[wc["home_score"].isna() & (wc["date"] >= TODAY)].sort_values("date")
    if unplayed.empty:
        return pd.DataFrame()
    day = unplayed["date"].min()
    fixtures = unplayed[unplayed["date"] == day]
    rows = []
    for r in fixtures.itertuples():
        neutral = (bool(r.neutral) if "neutral" in wc.columns else True) and r.home not in HOSTS
        la, lb = elo_goals(elo[r.home], elo[r.away], neutral=neutral)
        p = poisson_1x2(la, lb)
        pick = max([(r.home, p["p_a"]), ("Draw", p["p_draw"]), (r.away, p["p_b"])],
                   key=lambda t: t[1])
        rows.append({"date": str(r.date.date()), "home": r.home, "away": r.away,
                     "elo": f"{elo[r.home]:.0f} v {elo[r.away]:.0f}",
                     "xg": f"{la:.1f}-{lb:.1f}", "score": p["score"],
                     "p_H": p["p_a"], "p_D": p["p_draw"], "p_A": p["p_b"],
                     "pick": pick[0], "conf": pick[1]})
    return pd.DataFrame(rows)


def llm_repredict(picks: pd.DataFrame, elo: dict, rank: dict) -> pd.DataFrame:
    """Re-judge each next-day fixture with the LLM judge (Elo fallback if no key)."""
    from wc2026.models.llm_judge import Fixture, TeamContext, judge_match
    # judge_match returns a Verdict object (pydantic present) or a plain dict
    # (fallback path without pydantic); read both the same way.
    get = lambda v, k: v[k] if isinstance(v, dict) else getattr(v, k)
    out = []
    for r in picks.itertuples():
        host = r.home in HOSTS
        fx = Fixture(
            a=TeamContext(r.home, elo[r.home], rank[r.home]),
            b=TeamContext(r.away, elo[r.away], rank[r.away]),
            stage="Group stage", venue=("host" if host else "neutral"))
        v = judge_match(fx)
        pa, pd_, pb = get(v, "p_a_win"), get(v, "p_draw"), get(v, "p_b_win")
        pick = max([(r.home, pa), ("Draw", pd_), (r.away, pb)], key=lambda t: t[1])
        out.append({"date": r.date, "home": r.home, "away": r.away,
                    "score": get(v, "likely_score"), "p_H": round(pa, 3),
                    "p_D": round(pd_, 3), "p_A": round(pb, 3),
                    "pick": pick[0], "conf": round(pick[1], 3),
                    "why": (get(v, "rationale") or "")[:90]})
    return pd.DataFrame(out)


# Part 2 (Elo champion scorecard) lives in models/elo_sim.simulate_champion,
# shared with the title-odds timeline (stage 29).


def track_record() -> pd.DataFrame:
    """Rolling out-of-sample predicted-vs-true winner log over WC 2026.

    Elo is seeded on pre-tournament history; each WC match is predicted from
    PRE-match ratings, then the rating updates with the real result. Persisted
    to data/processed/winners_track.csv so the track accumulates over time.
    """
    history = build_real_matches(start="2022-01-01", end="2026-06-10")
    wc_played = build_real_matches(start=TOURNAMENT_START, end=TODAY)
    track = rolling_backtest(history, wc_played)
    if not track.empty:
        track.to_csv(PROCESSED / "winners_track.csv", index=False)
    return track


def _pct(x):
    return f"{100*x:.0f}%"


def _render(picks, llm, sc, track, n_played, use_llm) -> str:
    L = [f"# 🔮 WC 2026 — Winners: next-day picks + champion scorecard\n",
         f"_A simple **Elo** model, conditioned on the **{n_played} matches played "
         f"so far** and the real 2026 bracket. Updated {TODAY}._\n"]

    L.append("## Next match day — who wins (Elo goals model)\n")
    if picks.empty:
        L.append("_No upcoming fixtures in the feed._\n")
    else:
        L.append(f"_Elo gap → two Poisson scoring rates → 1X2 + likely score. "
                 f"Date: **{picks.iloc[0]['date']}**._\n")
        L.append("| Fixture | Elo | Pred goals | Likely | P(H/D/A) | **Pick** |")
        L.append("|---|---|---|---|---|---|")
        for r in picks.itertuples():
            L.append(f"| {r.home} v {r.away} | {r.elo} | {r.xg} | {r.score} | "
                     f"{_pct(r.p_H)}/{_pct(r.p_D)}/{_pct(r.p_A)} | "
                     f"**{r.pick}** ({_pct(r.conf)}) |")
    if use_llm and llm is not None and not llm.empty:
        L.append("\n### Same fixtures, LLM-as-a-Judge\n")
        L.append("_Fuses Elo + form + venue into a calibrated read (Elo fallback "
                 "if no API key)._\n")
        L.append("| Fixture | Likely | P(H/D/A) | **Pick** | Why |")
        L.append("|---|---|---|---|---|")
        for r in llm.itertuples():
            L.append(f"| {r.home} v {r.away} | {r.score} | "
                     f"{_pct(r.p_H)}/{_pct(r.p_D)}/{_pct(r.p_A)} | "
                     f"**{r.pick}** ({_pct(r.conf)}) | {r.why} |")

    L.append("\n## Champion scorecard — simulated from today's state\n")
    L.append(f"_{N_SIMS:,} Elo tournaments. Played group games are held fixed; the "
             "rest of the groups + the knockout bracket are simulated. Teams "
             "already out fall to ~0%._\n")
    L.append("| # | Team | R16 | QF | SF | Final | **Champion** |")
    L.append("|--:|---|---|---|---|---|---|")
    for i, r in enumerate(sc.head(16).itertuples(), 1):
        L.append(f"| {i} | {r.team} | {_pct(r.p_round16)} | {_pct(r.p_quarter)} | "
                 f"{_pct(r.p_semi)} | {_pct(r.p_final)} | **{_pct(r.p_champion)}** |")

    if track is not None and not track.empty:
        hit = track["hit"].mean()
        n = len(track)
        L.append("\n## Track record — predicted vs true winners (out-of-sample)\n")
        L.append(f"_Each WC match was predicted from Elo as it stood **before** "
                 f"that game (then the rating updated). Running accuracy: "
                 f"**{_pct(hit)}** on {n} matches. Full log: "
                 f"`data/processed/winners_track.csv`._\n")
        L.append("| Date | Fixture | Score | Predicted | Actual | ✓ |")
        L.append("|---|---|---|---|---|:--:|")
        for r in track.tail(12).itertuples():   # most recent dozen
            L.append(f"| {r.date} | {r.home} v {r.away} | {r.score} | "
                     f"{r.pred} | **{r.actual}** | {'✅' if r.hit else '—'} |")
        L.append(f"\n_Showing the latest 12 of {n}. Elo hit-rate vs a coin-flip "
                 "baseline is the honest scoreboard for these picks._\n")

    L.append("\n## Method (simple by design)\n")
    L.append("- **Elo** is walked over all real results to today (recency- & "
             "WC-weighted K, goal-diff multiplier, host edge) — `models/elo.py`.")
    L.append("- **Goals**: Elo gap → two Poisson rates around a 1.35-goal "
             "baseline; the scoreline distribution gives 1X2.")
    L.append("- **Conditioning**: completed group games are fixed, so the "
             "scorecard reflects the actual standings — not a fresh re-roll.")
    L.append("- **LLM judge** (`--llm`) is an optional qualitative overlay on the "
             "next-day picks; see `models/llm_judge.py`.")
    L.append("- For the fuller Bayesian goals model (squad-skill prior + form + "
             "sentiment) see [CHAMPION_TRACKER.md](CHAMPION_TRACKER.md).")
    return "\n".join(L)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--llm", action="store_true", help="re-judge next day with the LLM")
    ap.add_argument("--sims", type=int, default=N_SIMS)
    args = ap.parse_args()
    ensure_dirs()

    elo_tbl = run_elo(build_real_matches(start="2022-01-01", end=TODAY))
    elo = elo_lookup(elo_tbl)
    rank = {t: int(r) for t, r in zip(elo_tbl["team"], elo_tbl["rank"])}
    # Any team without a recent match defaults to base rating so sims still run.
    for t in (x.name for x in TEAMS):
        elo.setdefault(t, 1500.0); rank.setdefault(t, 48)

    groups = {g: [t.name for t in ts] for g, ts in by_group().items()}
    wc = wc2026_matches()
    scored = wc[wc["home_score"].notna() & (wc["date"] <= TODAY)]
    played = {(r.home, r.away): (int(r.home_score), int(r.away_score))
              for r in scored.itertuples()}

    picks = next_day_picks(elo, rank)
    llm = llm_repredict(picks, elo, rank) if (args.llm and not picks.empty) else None
    sc = simulate_champion(elo, groups, played, args.sims)
    track = track_record()

    md = _render(picks, llm, sc, track, len(played), args.llm)
    out = ROOT / "docs" / "WINNERS.md"
    out.write_text(md)

    if not track.empty:
        print(f"Track record: predicted vs true on {len(track)} played WC "
              f"matches — Elo hit-rate {100*track['hit'].mean():.0f}%")
    if not picks.empty:
        print(f"\nNext match day ({picks.iloc[0]['date']}) — Elo picks:")
        print(picks[["home", "away", "score", "pick", "conf"]].to_string(index=False))
    print(f"\nChampion scorecard (conditioned on {len(played)} played, "
          f"{args.sims:,} sims):")
    print(sc.head(10)[["team", "p_round16", "p_quarter", "p_semi", "p_final",
                       "p_champion"]]
          .assign(**{c: (100 * sc.head(10)[c]).round(1) for c in
                     ["p_round16", "p_quarter", "p_semi", "p_final", "p_champion"]})
          .to_string(index=False))
    print(f"\nsaved -> {out}")


if __name__ == "__main__":
    main()
