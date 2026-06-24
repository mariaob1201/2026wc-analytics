"""Stage 13: pre-tournament backtest + forward forecast, match by match.

Honest out-of-sample test:
  * Fit the Bayesian goals model on results STRICTLY BEFORE the tournament
    (matches up to 2026-06-10) + the FIFA squad prior.
  * Predict every WC 2026 group match already played (<= today) and compare the
    forecast to the actual scoreline.
  * Forecast the upcoming fixtures the same way.
  * Enrich every fixture with squad/player context (rating, seniority, key
    player, semantic tier) for both teams.

Writes docs/match_predictions.md and prints an accuracy summary.

    python scripts/13_match_predictions.py
"""

import arviz as az
import pandas as pd

from wc2026.config import ARTIFACTS, PROCESSED, ROOT, ensure_dirs
from wc2026.data.sources import INTL_NAME_ALIASES, build_real_matches, download_intl_results
from wc2026.data.scouting import MEXICO_SOCIAL
from wc2026.data.teams import HOSTS, TEAMS
from wc2026.models.bayesian_score import fit, predict_match
from wc2026.models.momentum import combined_shifts

from wc2026.config import today as _today
TODAY = _today()
TOURNAMENT_START = "2026-06-11"
# Forecast the next several days of fixtures (covers today's matches + next slate).
FORECAST_HORIZON = (pd.Timestamp(TODAY) + pd.Timedelta(days=4)).strftime("%Y-%m-%d")


def wc_matches() -> pd.DataFrame:
    """All WC 2026 matches in the results feed, names mapped to our canon."""
    df = download_intl_results()
    df = df[(df["tournament"] == "FIFA World Cup") & (df["date"] >= "2026-06-01")].copy()
    from_src = {v: k for k, v in
                {t.name: INTL_NAME_ALIASES.get(t.name, t.name) for t in TEAMS}.items()}
    df["home"] = df["home_team"].map(lambda x: from_src.get(x, x))
    df["away"] = df["away_team"].map(lambda x: from_src.get(x, x))
    valid = {t.name for t in TEAMS}
    df = df[df["home"].isin(valid) & df["away"].isin(valid)]
    return df.sort_values("date").reset_index(drop=True)


def main() -> None:
    ensure_dirs()
    teams = [t.name for t in TEAMS]

    # --- 1. Fit on PRE-tournament data only (true out-of-sample backtest) ---
    pre = build_real_matches(start="2022-01-01", end="2026-06-10")
    prior = (pd.read_csv(PROCESSED / "team_features_real.csv")
             .set_index("team")["prior_strength"].reindex(teams).fillna(0.0).to_numpy())
    print(f"Fitting on {len(pre)} pre-tournament matches (<= 2026-06-10)...")
    res = fit(pre, teams, prior_strength=prior, draws=1000, tune=1000, chains=4)
    idata = res.idata
    res.idata.to_netcdf(ARTIFACTS / "posterior_pretournament.nc")

    # Squad/player context per team (from stage 05).
    interp = pd.read_csv(PROCESSED / "team_interpretation.csv").set_index("team")

    def ctx(team: str) -> dict:
        if team in interp.index:
            r = interp.loc[team]
            return {"ovr": r["avg_overall"], "age": r["avg_age"],
                    "tier": r["tier"], "star": r["star_player"], "style": r["style"]}
        return {"ovr": float("nan"), "age": float("nan"), "tier": "no data",
                "star": "-", "style": "-"}

    wc = wc_matches()
    scored = wc["home_score"].notna() & wc["away_score"].notna()
    # Resolved = actually played (has a score, on/before today). Upcoming = every
    # not-yet-resolved fixture within the horizon — INCLUDING today's matches and
    # any the results feed hasn't scored yet (so nothing falls through the gap).
    played_mask = (wc["date"] <= TODAY) & scored
    played = wc[played_mask]
    upcoming = wc[(~played_mask) & (wc["date"] <= FORECAST_HORIZON)]

    def neutral_for(home: str, row) -> bool:
        # WC games are neutral except host nations at home; trust the feed's flag.
        flag = bool(row.neutral) if "neutral" in wc.columns else True
        return flag and home not in HOSTS

    # --- 2. Backtest: predict each played match, compare to actual ---
    back = []
    for r in played.itertuples():
        p = predict_match(idata, teams, r.home, r.away,
                          neutral=neutral_for(r.home, r))
        gh, ga = int(r.home_score), int(r.away_score)
        actual = "H" if gh > ga else "A" if ga > gh else "D"
        pred = max([("H", p["p_home_win"]), ("D", p["p_draw"]), ("A", p["p_away_win"])],
                   key=lambda t: t[1])[0]
        p_actual = {"H": p["p_home_win"], "D": p["p_draw"], "A": p["p_away_win"]}[actual]
        back.append({
            "date": str(r.date.date()), "home": r.home, "away": r.away,
            "pred_xg": f"{p['exp_goals_home']:.1f}-{p['exp_goals_away']:.1f}",
            "pred_score": p["most_likely_score"],
            "p_H": p["p_home_win"], "p_D": p["p_draw"], "p_A": p["p_away_win"],
            "actual": f"{gh}-{ga}", "result": actual, "pred_result": pred,
            "hit": pred == actual, "p_actual": p_actual,
            "tot_pred": p["exp_goals_home"] + p["exp_goals_away"], "tot_act": gh + ga,
        })
    bt = pd.DataFrame(back)

    # Metrics.
    n = len(bt)
    hit_rate = bt["hit"].mean()
    brier = ((bt["p_H"] - (bt.result == "H")) ** 2 + (bt["p_D"] - (bt.result == "D")) ** 2
             + (bt["p_A"] - (bt.result == "A")) ** 2).mean()
    mae_goals = (bt["tot_pred"] - bt["tot_act"]).abs().mean()
    mean_p_actual = bt["p_actual"].mean()

    # --- 3. Forecast upcoming, WITH a momentum/sentiment nudge ---
    # Form is computed from all matches up to today (incl. in-tournament games),
    # so the forecast reflects who is hot. Mexico carries scouted sentiment too.
    form_matches = build_real_matches(start="2022-01-01", end=TODAY)
    shifts = combined_shifts(form_matches, TODAY,
                             scouted={"Mexico": MEXICO_SOCIAL["net_mood"]})
    fwd = []
    for r in upcoming.itertuples():
        p = predict_match(idata, teams, r.home, r.away,
                          neutral=neutral_for(r.home, r), shifts=shifts)
        fwd.append({
            "date": str(r.date.date()), "home": r.home, "away": r.away,
            "xg": f"{p['exp_goals_home']:.1f}-{p['exp_goals_away']:.1f}",
            "score": p["most_likely_score"],
            "p_H": p["p_home_win"], "p_D": p["p_draw"], "p_A": p["p_away_win"],
            "over25": p["p_over_2_5"],
            "mom": f"{shifts.get(r.home, 0):+.2f}/{shifts.get(r.away, 0):+.2f}",
        })
    fc = pd.DataFrame(fwd)

    # Persist tables so the analytics stage (14) can build charts without refit.
    bt.to_csv(PROCESSED / "backtest.csv", index=False)
    fc.to_csv(PROCESSED / "forecast.csv", index=False)

    # --- 4. Write report ---
    md = _render(bt, fc, ctx, n, hit_rate, brier, mae_goals, mean_p_actual)
    out = ROOT / "docs" / "match_predictions.md"
    out.write_text(md)

    print(f"\nBacktest on {n} played WC matches (model trained pre-tournament):")
    print(f"  outcome hit-rate : {100*hit_rate:.0f}%")
    print(f"  mean P(actual)   : {mean_p_actual:.2f}  (Brier {brier:.3f})")
    print(f"  total-goals MAE  : {mae_goals:.2f}")
    print(f"\nForecast rows: {len(fc)}")
    print(f"saved -> {out}")


def _pct(x):
    return f"{100*x:.0f}%"


def _render(bt, fc, ctx, n, hit_rate, brier, mae_goals, mean_p_actual) -> str:
    L = ["# WC 2026 — Match Predictions vs Reality, and Forecasts\n",
         "_Model trained on pre-tournament data only (results to 2026-06-10 + FIFA "
         "squad prior). Backtest compares those out-of-sample forecasts to the "
         f"actual scorelines; forecasts cover the next slate. Compiled {TODAY}._\n"]

    L.append("## Accuracy so far (out-of-sample)\n")
    L.append(f"- **Matches scored:** {n}")
    L.append(f"- **Outcome hit-rate:** {_pct(hit_rate)} (predicted W/D/L matched actual)")
    L.append(f"- **Mean probability on the actual outcome:** {mean_p_actual:.2f} "
             f"· **Brier score:** {brier:.3f} (lower is better)")
    L.append(f"- **Total-goals mean abs error:** {mae_goals:.2f} goals/match\n")
    L.append("> Read these as a small-sample sanity check (one matchday), not a "
             "verdict. Blowouts like Germany 7-1 and Canada 6-0 inflate the goals "
             "error — the model is calibrated to typical scorelines, not outliers.\n")

    L.append("## Backtest — prediction vs actual (played)\n")
    L.append("| Date | Fixture | Pred xG | Likely | P(H/D/A) | Actual | ✓ |")
    L.append("|---|---|---|---|---|---|:--:|")
    for r in bt.itertuples():
        L.append(f"| {r.date} | {r.home} v {r.away} | {r.pred_xg} | {r.pred_score} | "
                 f"{_pct(r.p_H)}/{_pct(r.p_D)}/{_pct(r.p_A)} | **{r.actual}** | "
                 f"{'✅' if r.hit else '—'} |")

    if len(fc):
        L.append("\n## Forecast — next fixtures (with momentum nudge)\n")
        L.append("_`Mom` = recency-weighted form (+ scouted sentiment) applied as "
                 "a small, capped log-rate nudge to each side's goals (home/away)._\n")
        L.append("| Date | Fixture | Pred xG | Likely | P(H/D/A) | Over 2.5 | Mom H/A |")
        L.append("|---|---|---|---|---|---|---|")
        for r in fc.itertuples():
            L.append(f"| {r.date} | {r.home} v {r.away} | {r.xg} | {r.score} | "
                     f"{_pct(r.p_H)}/{_pct(r.p_D)}/{_pct(r.p_A)} | {_pct(r.over25)} | "
                     f"{r.mom} |")

    # Player/squad context for teams appearing in the forecast.
    L.append("\n## Squad & player context (forecast teams)\n")
    L.append("_From real player data: squad rating, average age (seniority), "
             "stylistic tilt, and talisman._\n")
    L.append("| Team | Tier | Squad ovr | Avg age | Style | Talisman |")
    L.append("|---|---|---|---|---|---|")
    seen = []
    teams_in_fc = (list(fc["home"]) + list(fc["away"])) if len(fc) else list(bt["home"]) + list(bt["away"])
    for team in dict.fromkeys(teams_in_fc):
        c = ctx(team)
        if team in seen:
            continue
        seen.append(team)
        L.append(f"| {team} | {c['tier']} | {c['ovr']} | {c['age']} | "
                 f"{c['style']} | {c['star']} |")

    L.append("\n## Notes on method\n")
    L.append("- **Goals model:** hierarchical Bayesian Poisson — each team's "
             "attack/defence fits the data, scorelines are posterior-predictive. "
             "See [METHODOLOGY.md](METHODOLOGY.md).")
    L.append("- **Player data** (skillsets, seniority/age, semantic tier) feeds the "
             "model's prior and the context table above (FIFA dataset).")
    L.append("- **Public/sentiment sources** (ESPN, SI, social) enrich the Mexico "
             "deep-dive ([../data/processed/mexico_assessment.md]) and are wired to "
             "extend to other teams via the scouting + X-collector modules.")
    L.append("- **Limitation:** scores are independent Poisson and there is no "
             "strength-of-schedule term yet — see METHODOLOGY §10–11.")
    return "\n".join(L)


if __name__ == "__main__":
    main()
