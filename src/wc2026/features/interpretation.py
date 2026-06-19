"""Semantic interpretation: turn the numeric features into meaning.

Two levels:

* ``interpret_player`` -- a role/archetype label for each player, derived from
  position + age + which skills stand out (e.g. "Veteran talisman",
  "Ball-playing defender", "Clinical finisher").
* ``interpret_team``   -- a structured profile + a one-paragraph narrative per
  nation: quality tier, age profile, stylistic tilt (attack vs defence), squad
  depth (top-heavy vs deep), and star power.

These are deterministic, rule-based "semantics" -- transparent and auditable,
not a black box. Every threshold lives here so you can tune the vocabulary.
"""

from __future__ import annotations

import pandas as pd

ATTACK_SKILLS = ["skill_pace", "skill_shooting", "skill_dribbling"]
DEFENCE_SKILLS = ["skill_defending", "skill_physical"]


def _name(row: pd.Series) -> str:
    """Display name; synthetic players have no 'name' column, so fall back."""
    n = row.get("name")
    if isinstance(n, str) and n:
        return n
    return f"{row['team_code']} #{row['player_id']}"


# --------------------------------------------------------------------------- #
# Player level
# --------------------------------------------------------------------------- #
def interpret_player(row: pd.Series) -> str:
    """Return a short archetype label for one player row."""
    pos, age, ovr = row["position"], row["age"], row["overall"]

    # Age/quality framing first -- these read as the headline trait.
    if age >= 31 and ovr >= 82:
        return "Veteran talisman"
    if age >= 33:
        return "Experienced elder"
    if age <= 21 and ovr >= 78:
        return "Star prospect"
    if age <= 21:
        return "Rising youngster"
    if ovr < 72:
        return "Squad depth"

    # Otherwise label by where the player is strongest relative to position.
    if pos == "GK":
        return "Goalkeeper" if ovr < 84 else "Elite goalkeeper"
    if pos == "DF":
        return ("Ball-playing defender"
                if row["skill_passing"] >= row["skill_defending"] - 4
                else "Defensive rock")
    if pos == "MF":
        if row["skill_passing"] >= 82:
            return "Creative hub"
        if row["skill_defending"] >= 78:
            return "Defensive midfielder"
        return "Box-to-box midfielder"
    if pos == "FW":
        if row["skill_shooting"] >= 84:
            return "Clinical finisher"
        if row["skill_dribbling"] >= 85:
            return "Dribbling threat"
        return "Forward"
    return "Squad player"


def add_player_interpretation(players: pd.DataFrame) -> pd.DataFrame:
    df = players.copy()
    df["role"] = df.apply(interpret_player, axis=1)
    return df


# --------------------------------------------------------------------------- #
# Team level
# --------------------------------------------------------------------------- #
def _tier(overall: float) -> str:
    if overall >= 82:
        return "Elite contender"
    if overall >= 79:
        return "Strong side"
    if overall >= 76:
        return "Solid outfit"
    return "Developing team"


def _age_profile(avg_age: float) -> str:
    if avg_age >= 29:
        return "veteran-heavy"
    if avg_age >= 27:
        return "balanced age"
    return "youthful"


def _style(att: float, deff: float) -> str:
    diff = att - deff
    if diff >= 4:
        return "attack-leaning"
    if diff <= -4:
        return "defensively grounded"
    return "well-balanced"


def _depth(top11: float, rest: float) -> str:
    gap = top11 - rest
    if gap <= 3:
        return "deep squad"
    if gap >= 6:
        return "top-heavy"
    return "moderate depth"


def interpret_team(team: str, squad: pd.DataFrame) -> dict:
    """Structured profile + narrative for one nation's squad."""
    s = squad.sort_values("overall", ascending=False)
    core = s.head(16)
    top11 = s.head(11)
    rest = s.iloc[11:]

    avg_overall = float(core["overall"].mean())
    avg_age = float(core["age"].mean())
    att = float(core[ATTACK_SKILLS].mean().mean())
    deff = float(core[DEFENCE_SKILLS].mean().mean())
    top11_ovr = float(top11["overall"].mean())
    rest_ovr = float(rest["overall"].mean()) if len(rest) else top11_ovr

    # "Talisman" reads as an outfield leader; use the best non-GK if one exists.
    outfield = s[s["position"] != "GK"]
    star = outfield.iloc[0] if len(outfield) else s.iloc[0]

    tier = _tier(avg_overall)
    age_profile = _age_profile(avg_age)
    style = _style(att, deff)
    depth = _depth(top11_ovr, rest_ovr)
    star_power = ("galactico-level" if star["overall"] >= 88
                  else "marquee" if star["overall"] >= 84
                  else "modest")

    narrative = (
        f"{team}: {tier.lower()} (avg top-16 rating "
        f"{avg_overall:.1f}). The squad is {age_profile} (mean age "
        f"{avg_age:.1f}) and {style} in skill balance, with {depth}. "
        f"Talisman: {_name(star)} ({star['overall']:.0f} ovr), giving "
        f"{star_power} star power."
    )

    return {
        "team": team,
        "tier": tier,
        "avg_overall": round(avg_overall, 1),
        "avg_age": round(avg_age, 1),
        "age_profile": age_profile,
        "attack_index": round(att, 1),
        "defence_index": round(deff, 1),
        "style": style,
        "depth": depth,
        "star_player": _name(star),
        "star_overall": float(star["overall"]),
        "star_power": star_power,
        "narrative": narrative,
    }


def interpret_all_teams(players: pd.DataFrame) -> pd.DataFrame:
    """One interpretation row per team, ordered by squad quality."""
    rows = [interpret_team(team, g) for team, g in players.groupby("team", sort=False)]
    return (pd.DataFrame(rows)
            .sort_values("avg_overall", ascending=False)
            .reset_index(drop=True))


def team_profiles_markdown(interp: pd.DataFrame, players: pd.DataFrame) -> str:
    """Render a human-readable markdown report of every team's profile."""
    lines = ["# World Cup 2026 — Squad Semantic Profiles\n",
             "_Rule-based interpretation of real player data (FIFA 22 vintage)._\n"]
    roles = add_player_interpretation(players)
    for _, r in interp.iterrows():
        lines.append(f"## {r['team']}  —  {r['tier']}")
        lines.append(f"> {r['narrative']}\n")
        lines.append(f"- **Rating / age**: {r['avg_overall']} ovr · "
                     f"{r['age_profile']} ({r['avg_age']})")
        lines.append(f"- **Style**: {r['style']} "
                     f"(attack {r['attack_index']} vs defence {r['defence_index']})")
        lines.append(f"- **Depth**: {r['depth']} · **Star power**: {r['star_power']}")
        key = roles[roles["team"] == r["team"]].nlargest(3, "overall")
        bullets = ", ".join(f"{_name(p)} ({p['role']})" for _, p in key.iterrows())
        lines.append(f"- **Key players**: {bullets}\n")
    return "\n".join(lines)
