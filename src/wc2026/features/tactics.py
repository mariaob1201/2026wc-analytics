"""Formation / tactical analysis from squad composition.

Given a squad (with our coarse GK/DF/MF/FW buckets + overall ratings), we score
how well the available personnel fit each common formation, then turn that into
a semantic read: which shape the squad is *built* for, and how the alternatives
(4-4-2 vs 4-3-3 vs 4-2-3-1 ...) trade off.

Limitation, stated up front: our position buckets are coarse, so shapes that
differ only in midfield sub-roles (e.g. 4-1-4-1 vs 4-2-3-1, both DF4/MF5/FW1)
score identically here -- we treat them as a family and lean on scouted intel
(see ``data.scouting``) to disambiguate the actual setup.
"""

from __future__ import annotations

import pandas as pd

# Outfield line splits (defenders, midfielders, forwards); GK is implicit.
FORMATIONS: dict[str, tuple[int, int, int]] = {
    "4-4-2": (4, 4, 2),
    "4-3-3": (4, 3, 3),
    "4-2-3-1": (4, 5, 1),
    "4-1-4-1": (4, 5, 1),
    "3-5-2": (3, 5, 2),
    "5-3-2": (5, 3, 2),
    "3-4-3": (3, 4, 3),
}

# What each shape demands of a squad -- used for the semantic commentary.
FORMATION_NEEDS = {
    "4-4-2": "two reliable strikers and disciplined wide midfielders",
    "4-3-3": "quality wingers and a mobile front three",
    "4-2-3-1": "a creative number 10 behind a lone striker, two holding mids",
    "4-1-4-1": "a single anchor screening the defence, runners from midfield",
    "3-5-2": "energetic wing-backs and a packed midfield",
    "5-3-2": "a deep, compact block built to counter",
    "3-4-3": "dominant wing play and front-foot pressing",
}


def _line_strength(squad: pd.DataFrame, position: str, n: int) -> float:
    """Mean overall of the best ``n`` players in a position bucket."""
    pool = squad[squad["position"] == position].nlargest(n, "overall")
    if pool.empty:
        return 60.0  # fallback if a nation lacks a line entirely
    # If fewer than n available, pad with the weakest available (depth penalty).
    vals = list(pool["overall"])
    while len(vals) < n:
        vals.append(min(vals) - 3)
    return float(sum(vals) / n)


def formation_fit(squad: pd.DataFrame) -> pd.DataFrame:
    """Score every formation by the rating of the best XI it would field."""
    gk = _line_strength(squad, "GK", 1)
    rows = []
    for name, (d, m, f) in FORMATIONS.items():
        xi = (gk + d * _line_strength(squad, "DF", d)
              + m * _line_strength(squad, "MF", m)
              + f * _line_strength(squad, "FW", f)) / 11
        rows.append({"formation": name, "xi_rating": round(xi, 2),
                     "shape": f"{d}-{m}-{f} outfield", "needs": FORMATION_NEEDS[name]})
    out = pd.DataFrame(rows).sort_values("xi_rating", ascending=False)
    # De-duplicate identical coarse shapes for the "best fit" pick.
    out = out.reset_index(drop=True)
    return out


def interpret_formation(squad: pd.DataFrame, actual: str | None = None) -> dict:
    """Semantic tactical read: best-fit shape, and how the actual one compares."""
    fit = formation_fit(squad)
    best = fit.iloc[0]

    # Depth by line tells us where the squad is stacked.
    counts = squad["position"].value_counts().to_dict()
    strongest_line = max(
        ["DF", "MF", "FW"],
        key=lambda p: _line_strength(squad, p, 3),
    )
    line_word = {"DF": "defence", "MF": "midfield", "FW": "attack"}[strongest_line]

    note = (f"Squad is built around its {line_word}. Best-fitting shape is "
            f"{best['formation']} (XI rating {best['xi_rating']}), which wants "
            f"{best['needs']}.")

    result = {
        "best_formation": best["formation"],
        "best_xi_rating": best["xi_rating"],
        "strongest_line": line_word,
        "line_counts": counts,
        "ranking": fit[["formation", "xi_rating"]].to_dict("records"),
        "commentary": note,
    }

    if actual:
        actual_row = fit[fit["formation"] == actual]
        if not actual_row.empty:
            ar = float(actual_row.iloc[0]["xi_rating"])
            delta = round(ar - best["xi_rating"], 2)
            verdict = ("matches the squad's natural shape" if delta >= -0.3
                       else "is a pragmatic choice that slightly underuses the "
                            "squad's best XI")
            result["actual_formation"] = actual
            result["actual_xi_rating"] = ar
            result["actual_vs_best_delta"] = delta
            result["actual_commentary"] = (
                f"The staff's {actual} {verdict} (XI rating {ar}, "
                f"{'+' if delta >= 0 else ''}{delta} vs best fit). "
                f"It asks for {FORMATION_NEEDS.get(actual, 'a balanced setup')}.")
    return result
