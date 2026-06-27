"""Lightweight matplotlib helpers for inspecting the results."""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")  # headless: write files, never pop a window
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402


def plot_calibration(bt: pd.DataFrame, path, bins: int = 5) -> None:
    """Reliability diagram: pooled predicted prob vs observed frequency (1X2)."""
    import numpy as np

    probs, outcomes = [], []
    for r in bt.itertuples():
        probs += [r.p_H, r.p_D, r.p_A]
        outcomes += [r.result == "H", r.result == "D", r.result == "A"]
    probs, outcomes = np.array(probs), np.array(outcomes, dtype=float)
    edges = np.linspace(0, 1, bins + 1)
    xs, ys = [], []
    for lo, hi in zip(edges[:-1], edges[1:]):
        m = (probs >= lo) & (probs < hi) if hi < 1 else (probs >= lo) & (probs <= hi)
        if m.sum():
            xs.append(probs[m].mean())
            ys.append(outcomes[m].mean())
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.plot([0, 1], [0, 1], "--", color="grey", label="perfect")
    ax.plot(xs, ys, "o-", color="#2b8cbe", label="model")
    ax.set_xlabel("predicted probability")
    ax.set_ylabel("observed frequency")
    ax.set_title("Calibration (1X2, out-of-sample)")
    ax.legend()
    fig.tight_layout()
    fig.savefig(path, dpi=130)
    plt.close(fig)


def plot_goals_scatter(bt: pd.DataFrame, path) -> None:
    """Predicted total goals (expected) vs actual total goals per match."""
    fig, ax = plt.subplots(figsize=(6.5, 6))
    mx = max(bt["tot_pred"].max(), bt["tot_act"].max()) + 0.5
    ax.plot([0, mx], [0, mx], "--", color="grey")
    ax.scatter(bt["tot_pred"], bt["tot_act"], color="#cb181d", alpha=0.8)
    ax.set_xlabel("predicted total goals (expected)")
    ax.set_ylabel("actual total goals")
    ax.set_title("Predicted vs actual goals (played)")
    fig.tight_layout()
    fig.savefig(path, dpi=130)
    plt.close(fig)


def plot_forecast_probs(fc: pd.DataFrame, path) -> None:
    """Stacked W/D/L bars for upcoming fixtures."""
    d = fc.copy()
    labels = [f"{r.home} v {r.away}" for r in d.itertuples()][::-1]
    h, dr, a = d["p_H"][::-1], d["p_D"][::-1], d["p_A"][::-1]
    fig, ax = plt.subplots(figsize=(9, 0.42 * len(d) + 1))
    ax.barh(labels, 100 * h, color="#2b8cbe", label="home win")
    ax.barh(labels, 100 * dr, left=100 * h, color="#bdbdbd", label="draw")
    ax.barh(labels, 100 * a, left=100 * (h + dr), color="#cb181d", label="away win")
    ax.set_xlabel("probability [%]")
    ax.set_title("Forecast — win/draw/win for next fixtures")
    ax.legend(ncol=3, loc="lower center", bbox_to_anchor=(0.5, 1.02))
    ax.set_xlim(0, 100)
    fig.tight_layout()
    fig.savefig(path, dpi=130)
    plt.close(fig)


def social_card(strength: pd.DataFrame, facts: dict, path,
                handle: str = "@your_handle") -> None:
    """A portrait (1080x1350) Instagram/X-ready summary card — real data only.

    ``facts`` keys: team, flag, rank, n, group_line, formation, sentiment,
    refs (list of (team, net_strength) to show as comparison bars).
    """
    bg, fg, accent, muted = "#0b1f17", "#f2fff7", "#2ecc71", "#9fb4a8"
    fig = plt.figure(figsize=(9, 11.25), dpi=120)
    fig.patch.set_facecolor(bg)
    fig.subplots_adjust(left=0.08, right=0.92, top=0.99, bottom=0.04)

    def text(x, y, s, size, color=fg, weight="normal", ha="left"):
        fig.text(x, y, s, fontsize=size, color=color, weight=weight, ha=ha)

    t = facts
    # Tricolor accent stripe (emoji flags render as tofu in matplotlib fonts).
    import matplotlib.patches as mpatches
    for i, c in enumerate(t.get("colors", ["#006847", "#ffffff", "#ce1126"])):
        fig.patches.append(mpatches.Rectangle(
            (0.08 + i * 0.045, 0.955), 0.045, 0.013, facecolor=c, edgecolor="none",
            transform=fig.transFigure, figure=fig))
    text(0.08, 0.915, t["team"].upper(), 36, fg, "bold")
    text(0.08, 0.875, "World Cup 2026 — by the numbers", 17, accent, "bold")

    # Big headline stat: model rank.
    text(0.08, 0.80, f"#{t['rank']}", 80, fg, "bold")
    text(0.34, 0.805, f"of {t['n']}", 26, muted)
    text(0.08, 0.745, "Bayesian model strength (real international results, 2022–26)",
         13, muted)

    # Fact lines.
    rows = [("Group A", t["group_line"]),
            ("Formation", t["formation"]),
            ("Fan mood", t["sentiment"])]
    y = 0.685
    for label, val in rows:
        text(0.08, y, label.upper(), 13, accent, "bold")
        text(0.08, y - 0.028, val, 16, fg)
        y -= 0.075

    # Comparison bars (net strength vs reference teams).
    ax = fig.add_axes([0.17, 0.10, 0.75, 0.29])
    ax.set_facecolor(bg)
    refs = t["refs"]
    names = [r[0] for r in refs]
    vals = [r[1] for r in refs]
    colors = [accent if n == t["team"] else "#35506f" for n in names]
    ax.barh(names[::-1], vals[::-1], color=colors[::-1])
    ax.set_title("Net strength vs the field", color=fg, loc="left", fontsize=14)
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.tick_params(colors=fg, labelsize=12)
    ax.set_xticks([])

    text(0.08, 0.055, f"Bayesian Poisson model · {handle}", 12, muted)
    text(0.08, 0.030,
         "Data: FIFA player ratings · martj42 results · ESPN/SI. Illustrative, not betting advice.",
         9, muted)
    fig.savefig(path, facecolor=bg)
    plt.close(fig)


def plot_champion_probs(sim: pd.DataFrame, path, top: int = 15) -> None:
    """Horizontal bar chart of the top-N title probabilities."""
    d = sim.nlargest(top, "p_champion").iloc[::-1]
    fig, ax = plt.subplots(figsize=(8, 0.4 * top + 1))
    ax.barh(d["team"], 100 * d["p_champion"], color="#2b8cbe")
    ax.set_xlabel("P(win World Cup 2026)  [%]")
    ax.set_title("Bayesian title probabilities")
    for y, v in enumerate(d["p_champion"]):
        ax.text(100 * v + 0.2, y, f"{100 * v:.1f}%", va="center", fontsize=8)
    fig.tight_layout()
    fig.savefig(path, dpi=130)
    plt.close(fig)


def plot_champion_timeline(timeline: pd.DataFrame, path, top: int = 8) -> None:
    """Title-odds over the tournament: x = games played, y = P(champion).

    ``timeline`` is long-form: columns games_played, team, p_champion. One line
    per team (the ``top`` with the highest current odds), so you can watch
    contenders rise and fall as results come in.
    """
    last = timeline["games_played"].max()
    leaders = (timeline[timeline["games_played"] == last]
               .nlargest(top, "p_champion")["team"].tolist())
    fig, ax = plt.subplots(figsize=(9, 5.5))
    cmap = plt.get_cmap("tab10")
    for k, team in enumerate(leaders):
        d = timeline[timeline["team"] == team].sort_values("games_played")
        ax.plot(d["games_played"], 100 * d["p_champion"], marker="o", ms=3,
                lw=2, color=cmap(k % 10), label=team)
        ax.text(d["games_played"].iloc[-1] + 0.5, 100 * d["p_champion"].iloc[-1],
                team, va="center", fontsize=8, color=cmap(k % 10))
    ax.set_xlabel("World Cup matches played")
    ax.set_ylabel("P(win World Cup 2026)  [%]")
    ax.set_title("Title odds over the tournament (Elo, conditioned on results so far)")
    ax.grid(alpha=0.25)
    ax.set_xlim(0, last + max(6, last * 0.12))
    ax.margins(y=0.05)
    fig.tight_layout()
    fig.savefig(path, dpi=130)
    plt.close(fig)


def plot_team_rank(strength: pd.DataFrame, path, highlight: str) -> None:
    """All 48 teams by net strength, with one team highlighted."""
    d = strength.sort_values("net_strength", ascending=False).reset_index(drop=True)
    colors = ["#d94801" if t == highlight else "#9ecae1" for t in d["team"]]
    fig, ax = plt.subplots(figsize=(8, 11))
    ax.barh(d["team"][::-1], d["net_strength"][::-1], color=colors[::-1])
    rank = int(d.index[d["team"] == highlight][0]) + 1
    ax.set_xlabel("posterior net strength (attack + defence)")
    ax.set_title(f"WC2026 team strength from real results — {highlight} = {rank}/48")
    fig.tight_layout()
    fig.savefig(path, dpi=130)
    plt.close(fig)


def plot_strength(strength: pd.DataFrame, path, top: int = 20) -> None:
    """Posterior attack vs defence scatter for the strongest teams."""
    d = strength.nlargest(top, "net_strength")
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.scatter(d["attack"], d["defence"], color="#cb181d")
    for _, r in d.iterrows():
        ax.annotate(r["team"], (r["attack"], r["defence"]), fontsize=8,
                    xytext=(3, 3), textcoords="offset points")
    ax.set_xlabel("attack (higher = scores more)")
    ax.set_ylabel("defence (higher = concedes less)")
    ax.set_title("Posterior mean team strengths")
    ax.axhline(0, color="grey", lw=0.5)
    ax.axvline(0, color="grey", lw=0.5)
    fig.tight_layout()
    fig.savefig(path, dpi=130)
    plt.close(fig)
