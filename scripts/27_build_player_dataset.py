"""Stage 27: build the two tabular 2026 World Cup datasets.

PLAYER schema (granular per-player characteristics)
    data/processed/wc2026_players.csv
    team, fifa_code, group, name, position, age, caps,
    overall, pace, shooting, passing, dribbling, defending, physical, rating_source

TEAM schema (results stats + aggregated player characteristics + model ratings)
    data/processed/wc2026_team_assessment.csv
    identity:   team, fifa_code, group, flag
    2026 games: played, wins, draws, losses, goals_for, goals_against, goal_diff, points
    model:      attack, defence, net_strength, model_rank, elo, elo_rank
    seniority:  squad_overall, avg_age, total_caps
    strength:   attack_strength, defence_strength   (aggregated player attributes)
    dynamics:   young_pace, senior_solidity, form_momentum
    semantics:  tier, style, star_player

Sources: open rezarahiminia/worldcup2026 repo (team metadata) + real squads
(Wikipedia) + FIFA attributes + the 2026 results feed + the model's posterior.

    python scripts/27_build_player_dataset.py
"""

import numpy as np
import pandas as pd

from wc2026.config import PROCESSED, ensure_dirs, today
from wc2026.data.live_squads import fetch_squads
from wc2026.data.sources import build_real_matches, download_fifa, wc2026_matches
from wc2026.data.teams import TEAMS
from wc2026.models.momentum import combined_shifts

SKILLS = ["pace", "shooting", "passing", "dribbling", "defending", "physic"]
ATT_ATTR = ["pace", "shooting", "dribbling"]
DEF_ATTR = ["defending", "physical"]


def _team_results(wc_scored, teams) -> pd.DataFrame:
    """Per-team 2026 match stats (every team, played or not)."""
    rec = {t: dict(played=0, wins=0, draws=0, losses=0, gf=0, ga=0) for t in teams}
    for r in wc_scored.itertuples():
        h, a, gh, ga = r.home, r.away, int(r.home_score), int(r.away_score)
        for tm, f, ag in ((h, gh, ga), (a, ga, gh)):
            if tm in rec:
                rec[tm]["played"] += 1; rec[tm]["gf"] += f; rec[tm]["ga"] += ag
        if h in rec and a in rec:
            if gh > ga:
                rec[h]["wins"] += 1; rec[a]["losses"] += 1
            elif ga > gh:
                rec[a]["wins"] += 1; rec[h]["losses"] += 1
            else:
                rec[h]["draws"] += 1; rec[a]["draws"] += 1
    rows = []
    for t, d in rec.items():
        rows.append({"team": t, "played": d["played"], "wins": d["wins"],
                     "draws": d["draws"], "losses": d["losses"],
                     "goals_for": d["gf"], "goals_against": d["ga"],
                     "goal_diff": d["gf"] - d["ga"], "points": d["wins"] * 3 + d["draws"]})
    return pd.DataFrame(rows)


def main() -> None:
    ensure_dirs()
    teams = [t.name for t in TEAMS]
    code_by_team = {t.name: t.code for t in TEAMS}
    group_by_team = {t.name: t.group for t in TEAMS}

    # 1. Team metadata from the open World Cup repo (graceful fallback).
    try:
        from wc2026.data.worldcup_repo import fetch_team_metadata
        flag_by_code = dict(zip(*[fetch_team_metadata()[c] for c in ("fifa_code", "flag")]))
        print(f"Team metadata from rezarahiminia/worldcup2026 (flags/codes).")
    except Exception as e:
        flag_by_code = {}
        print(f"[warn] worldcup repo unavailable ({e}); using local metadata")

    # 2. PLAYER table: real squads + FIFA attributes joined by name.
    live = fetch_squads()
    fifa = download_fifa()
    last = lambda n: str(n).split()[-1].lower()
    rt = fifa[["short_name", "overall", *SKILLS]].copy()
    rt["_last"] = rt["short_name"].map(last)
    rt = rt.sort_values("overall", ascending=False).drop_duplicates("_last")
    pl = live.copy()
    pl["_last"] = pl["name"].map(last)
    pl = pl.merge(rt.drop(columns="short_name"), on="_last", how="left")
    pl["rating_source"] = np.where(pl["overall"].notna(), "fifa-match", "team-median")
    for c in ["overall", *SKILLS]:
        pl[c] = pl.groupby("team")[c].transform(lambda s: s.fillna(s.median()))
        pl[c] = pl[c].fillna(pl[c].median()).round(0)
    pl = pl.rename(columns={"physic": "physical"})
    pl["fifa_code"] = pl["team"].map(code_by_team)
    pl["group"] = pl["team"].map(group_by_team)
    players = pl[["team", "fifa_code", "group", "name", "position", "age", "caps",
                  "overall", "pace", "shooting", "passing", "dribbling",
                  "defending", "physical", "rating_source"]]
    players.to_csv(PROCESSED / "wc2026_players.csv", index=False)

    # 3. TEAM table: results + model + aggregated player characteristics.
    wc = wc2026_matches()
    results = _team_results(wc[wc.home_score.notna()], teams)

    strength = pd.read_csv(PROCESSED / "posterior_strength_real.csv").rename(
        columns={"rank": "model_rank"})[["team", "attack", "defence",
                                         "net_strength", "model_rank"]]
    elo = pd.read_csv(PROCESSED / "elo_ratings.csv").rename(
        columns={"rank": "elo_rank"})[["team", "elo", "elo_rank"]]

    agg = players.groupby("team").apply(lambda g: pd.Series({
        "squad_overall": g.nlargest(16, "overall")["overall"].mean().round(1),
        "avg_age": g["age"].mean().round(1),
        "total_caps": int(g["caps"].sum()),
        "attack_strength": g[ATT_ATTR].mean().mean().round(1),
        "defence_strength": g[g.position == "DF"]["defending"].mean().round(1),
        "young_pace": g[g.position.isin(["FW", "MF"])]["pace"].mean().round(1),
        "senior_solidity": (g[g.position == "DF"]["age"].mean()
                            * g[g.position == "DF"]["defending"].mean() / 100).round(1),
    })).reset_index()

    # tier/style/talisman from the REAL 2026 squad (not the FIFA-vintage pool,
    # which still lists retired players like Sergio Ramos).
    def _tier(o):
        return ("Elite contender" if o >= 82 else "Strong side" if o >= 79
                else "Solid outfit" if o >= 76 else "Developing team")
    agg["tier"] = agg["squad_overall"].map(_tier)
    d = agg["attack_strength"] - agg["defence_strength"]
    agg["style"] = np.select([d >= 2, d <= -2],
                             ["attack-leaning", "defensively grounded"],
                             default="well-balanced")
    # Talisman = best outfield player actually in the squad.
    nongk = players[players.position != "GK"].sort_values("overall", ascending=False)
    star = nongk.drop_duplicates("team")[["team", "name"]].rename(
        columns={"name": "star_player"})
    agg = agg.merge(star, on="team", how="left")

    shifts = combined_shifts(build_real_matches(end=today()), today())
    team = (pd.DataFrame({"team": teams})
            .merge(results, on="team", how="left")
            .merge(strength, on="team", how="left")
            .merge(elo, on="team", how="left")
            .merge(agg, on="team", how="left"))
    team["form_momentum"] = team["team"].map(lambda t: round(shifts.get(t, 0.0), 3))
    team["fifa_code"] = team["team"].map(code_by_team)
    team["group"] = team["team"].map(group_by_team)
    team["flag"] = team["fifa_code"].map(flag_by_code)
    team = team[["team", "fifa_code", "group", "flag",
                 "played", "wins", "draws", "losses", "goals_for", "goals_against",
                 "goal_diff", "points",
                 "attack", "defence", "net_strength", "model_rank", "elo", "elo_rank",
                 "squad_overall", "avg_age", "total_caps",
                 "attack_strength", "defence_strength",
                 "young_pace", "senior_solidity", "form_momentum",
                 "tier", "style", "star_player"]]
    team = team.sort_values("net_strength", ascending=False).reset_index(drop=True)
    team.to_csv(PROCESSED / "wc2026_team_assessment.csv", index=False)

    cov = (players.rating_source == "fifa-match").mean()
    print(f"\nplayers -> wc2026_players.csv ({len(players)} rows, {cov:.0%} attr coverage)")
    print(f"teams   -> wc2026_team_assessment.csv ({len(team)} teams)")
    print("\nTop 8 (results + ratings + aggregated player strength):")
    print(team.head(8)[["team", "played", "goals_for", "goals_against", "points",
                        "attack", "defence", "attack_strength", "defence_strength"]]
          .to_string(index=False))


if __name__ == "__main__":
    main()
