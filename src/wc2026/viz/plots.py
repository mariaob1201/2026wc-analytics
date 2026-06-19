"""Lightweight matplotlib helpers for inspecting the results."""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")  # headless: write files, never pop a window
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402


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
