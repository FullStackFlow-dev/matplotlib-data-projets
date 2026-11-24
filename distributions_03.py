"""Script 3 — Comparer 3 distributions : latences de 3 versions d'API."""
import numpy as np
import matplotlib.pyplot as plt
from statistics import NormalDist

rng = np.random.default_rng(3)
plt.rcParams.update({"axes.spines.top": False, "axes.spines.right": False,
                     "axes.grid": True, "grid.alpha": 0.3, "axes.titleweight": "bold"})
COLORS = ["#2563eb", "#f59e0b", "#10b981"]

data = {
    "API v1": rng.lognormal(4.5, .50, 800),
    "API v2": rng.lognormal(4.2, .35, 800),
    "API v3": rng.lognormal(4.0, .60, 800),
}

fig, axes = plt.subplots(2, 2, figsize=(14, 9), constrained_layout=True)
fig.suptitle("Comparaison des latences (ms) par version d'API", fontsize=16)

# 1. Violin plots
ax = axes[0, 0]
parts = ax.violinplot(list(data.values()), showmeans=True, showextrema=False)
for pc, c in zip(parts["bodies"], COLORS):
    pc.set_facecolor(c); pc.set_alpha(.6)
ax.set_xticks(range(1, len(data) + 1)); ax.set_xticklabels(data.keys())
ax.set_ylabel("Latence (ms)"); ax.set_title("Violin plots (forme des distributions)")

# 2. ECDF (fonction de répartition empirique) — idéal pour lire les percentiles
ax = axes[0, 1]
for (nom, v), c in zip(data.items(), COLORS):
    xs = np.sort(v)
    ax.step(xs, np.arange(1, len(xs) + 1) / len(xs), where="post", color=c, label=nom)
ax.axhline(.95, color="red", ls="--", lw=1, label="p95")
ax.set_xlabel("Latence (ms)"); ax.set_ylabel("Proportion cumulée")
ax.set_title("ECDF — lire p50, p95, p99"); ax.legend(fontsize=8)

# 3. QQ-plot vs loi normale (normalité des données standardisées)
ax = axes[1, 0]
norm = NormalDist()
for (nom, v), c in zip(data.items(), COLORS):
    v = np.sort((v - v.mean()) / v.std())
    theo = np.array([norm.inv_cdf((i + .5) / len(v)) for i in range(len(v))])
    ax.scatter(theo, v, s=6, alpha=.5, color=c, label=nom)
ax.plot([-3.5, 3.5], [-3.5, 3.5], "k--", lw=1)
ax.set_xlabel("Quantiles théoriques (normale)"); ax.set_ylabel("Quantiles observés")
ax.set_title("QQ-plot : écart à la normalité"); ax.legend(fontsize=8)

# 4. Histogrammes superposés (densité)
ax = axes[1, 1]
for (nom, v), c in zip(data.items(), COLORS):
    ax.hist(v, bins=40, density=True, alpha=.45, color=c, label=nom)
ax.set_xlabel("Latence (ms)"); ax.set_title("Densités superposées"); ax.legend(fontsize=8)

fig.savefig("03_distributions.png", dpi=150, bbox_inches="tight")
plt.show()