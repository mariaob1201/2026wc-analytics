"""Stage 23: knockout-opponent odds for one team.

For a set of candidate opponents, computes the goal forecast + win/draw/loss and
an Elo cross-check, with each side's squad style and current form — Mexico's
Round-of-32 view by default (at the Estadio Azteca). Writes docs/R32_ODDS.md and
prints the table; refresh as the draw firms up.

    python scripts/23_r32_odds.py
    python scripts/23_r32_odds.py --team Mexico --opponents Scotland Ecuador "Cape Verde"
    python scripts/23_r32_odds.py --neutral --stage "Round of 16"
"""

import argparse

import arviz as az
import pandas as pd

from wc2026.config import ARTIFACTS, PROCESSED, ROOT, ensure_dirs
from wc2026.data.scouting import MEXICO_SOCIAL
from wc2026.data.sources import build_real_matches, wc2026_matches
from wc2026.data.teams import HOSTS, TEAMS
from wc2026.models.bayesian_score import FitResult, predict_match
from wc2026.models.elo import win_probability
from wc2026.models.momentum import combined_shifts

TODAY = "2026-06-19"


def _form(wc, team):
    g = wc[(wc.home == team) | (wc.away == team)]
    return "; ".join(f"{r.home} {int(r.home_score)}-{int(r.away_score)} {r.away}"
                     for r in g.itertuples()) or "—"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--team", default="Mexico")
    ap.add_argument("--opponents", nargs="+",
                    default=["Scotland", "Ecuador", "Cape Verde"])
    ap.add_argument("--stage", default="Round of 32")
    ap.add_argument("--venue", default="Estadio Azteca (home)")
    ap.add_argument("--neutral", action="store_true",
                    help="force a neutral venue (default: home if team is a host)")
    args = ap.parse_args()

    ensure_dirs()
    teams = [t.name for t in TEAMS]
    idata = az.from_netcdf(ARTIFACTS / "posterior_real.nc")
    FitResult(idata=idata, teams=teams, team_to_idx={t: i for i, t in enumerate(teams)})
    elo = pd.read_csv(PROCESSED / "elo_ratings.csv").set_index("team")
    interp = pd.read_csv(PROCESSED / "team_interpretation.csv").set_index("team")
    shifts = combined_shifts(build_real_matches(end=TODAY), TODAY,
                             scouted={"Mexico": MEXICO_SOCIAL["net_mood"]})
    wc = wc2026_matches()
    wc = wc[wc.home_score.notna()]

    neutral = args.neutral or (args.team not in HOSTS)
    rows = []
    for o in args.opponents:
        if o not in teams:
            print(f"  [skip] {o!r} not in the 48-team field")
            continue
        p = predict_match(idata, teams, args.team, o, neutral=neutral, shifts=shifts)
        ew = win_probability(elo.loc[args.team, "elo"], elo.loc[o, "elo"],
                             neutral=neutral)
        pr = interp.loc[o] if o in interp.index else None
        rows.append({
            "opp": o, "xg": f"{p['exp_goals_home']:.2f}-{p['exp_goals_away']:.2f}",
            "score": p["most_likely_score"], "win": p["p_home_win"],
            "draw": p["p_draw"], "loss": p["p_away_win"], "over25": p["p_over_2_5"],
            "elo_win": ew, "elo_rank": int(elo.loc[o, "rank"]),
            "tier": pr["tier"] if pr is not None else "?",
            "style": pr["style"] if pr is not None else "?",
            "star": pr["star_player"] if pr is not None else "?",
            "form": _form(wc, o),
        })
    rows.sort(key=lambda r: r["win"])   # hardest first

    md = _render(args, rows, int(elo.loc[args.team, "rank"]))
    out = ROOT / "docs" / "R32_ODDS.md"
    out.write_text(md)

    print(f"=== {args.team} — {args.stage} opponent odds ({args.venue}) ===\n")
    print(f"{'opponent':<13}{'win':>6}{'draw':>6}{'loss':>6}{'xG':>11}  elo")
    for r in rows:
        print(f"{r['opp']:<13}{100*r['win']:>5.0f}%{100*r['draw']:>5.0f}%"
              f"{100*r['loss']:>5.0f}%{r['xg']:>11}  {100*r['elo_win']:.0f}%")
    print(f"\nsaved -> {out}")


def _pct(x):
    return f"{100*x:.0f}%"


def _render(args, rows, team_elo_rank) -> str:
    venue = "neutral" if (args.neutral or args.team not in HOSTS) else args.venue
    L = [f"# {args.team} — {args.stage} Opponent Odds\n",
         f"_Goal forecast + win/draw/loss vs each candidate opponent, at **{venue}**. "
         "Model = Bayesian goals (with home edge + current form); Elo = recency "
         "cross-check (win excl. draw). Sorted hardest-first. Compiled 2026-06-19._\n",
         "| Opponent | Likely | **Win** | Draw | Loss | Over 2.5 | Elo win | Opp Elo rank |",
         "|---|---|---|---|---|---|---|---|"]
    for r in rows:
        L.append(f"| {r['opp']} | {r['score']} | **{_pct(r['win'])}** | "
                 f"{_pct(r['draw'])} | {_pct(r['loss'])} | {_pct(r['over25'])} | "
                 f"{_pct(r['elo_win'])} | {r['elo_rank']} |")
    if rows:
        hardest = rows[0]
        L.append(f"\n**Toughest draw: {hardest['opp']}** "
                 f"({_pct(hardest['win'])} win) — lowest win probability of the set.\n")
    L.append("## Opponent notes (style · form)\n")
    for r in rows:
        L.append(f"- **{r['opp']}** — {r['tier']}, {r['style']}; talisman "
                 f"{r['star']}. Form: {r['form']}")
    L.append("\n_Caveat: Bayesian (pooled, ~mid-table view of the favourite) and Elo "
             "(recency, hot-form view) often disagree on the margin; they agree on "
             "the ranking. Refresh with `make r32-odds` as the draw firms up._")
    return "\n".join(L)


if __name__ == "__main__":
    main()
