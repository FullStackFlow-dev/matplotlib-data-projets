"""Script 2 — Analyse de série temporelle + détection d'anomalies (z-score glissant)."""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from hover_summaries import add_hover_summaries

rng = np.random.default_rng(7)
plt.rcParams.update({"axes.spines.top": False, "axes.spines.right": False,
                     "axes.grid": True, "grid.alpha": 0.3, "axes.titleweight": "bold"})

# --- Série : tendance + saisonnalité annuelle/hebdo + bruit + anomalies ---
dates = pd.date_range("2025-01-01", "2026-11-24", freq="D")
t = np.arange(len(dates))
y = 100 + 0.05 * t + 15 * np.sin(2 * np.pi * t / 365.25) + 6 * np.sin(2 * np.pi * t / 7) \
    + rng.normal(0, 4, len(t))
idx = rng.choice(len(t), 8, replace=False)
y[idx] += rng.choice([-1, 1], 8) * rng.uniform(25, 45, 8)   # anomalies injectées
s = pd.Series(y, index=dates, name="valeur")

# Statistiques glissantes + z-score
roll_mean = s.rolling(7, center=True).mean()
roll_std = s.rolling(7, center=True).std()
z = (s - roll_mean) / roll_std
anomalies = s[z.abs() > 3]

fig = plt.figure(figsize=(15, 10), constrained_layout=True)
gs = fig.add_gridspec(3, 2, height_ratios=[2, 1, 1])
fig.suptitle("Analyse de série temporelle", fontsize=16, fontweight="bold")

# 1. Série brute + moyenne glissante + bande ±2σ + anomalies
ax = fig.add_subplot(gs[0, :])
ax_series = ax
ax.plot(s.index, s.values, lw=.7, alpha=.5, color="#94a3b8", label="Brut")
ax.plot(roll_mean.index, roll_mean, color="#2563eb", lw=1.8, label="Moyenne glissante 7j")
ax.fill_between(roll_mean.index, roll_mean - 2 * roll_std, roll_mean + 2 * roll_std,
                color="#2563eb", alpha=.15, label="±2σ")
ax.scatter(anomalies.index, anomalies.values, color="red", marker="x", s=60,
        zorder=5, label=f"Anomalies (|z|>3) : {len(anomalies)}")
ax.legend(ncol=4, fontsize=9); ax.set_title("Tendance, volatilité et anomalies")

# 2. Profil hebdomadaire
ax = fig.add_subplot(gs[1, 0])
ax_weekday = ax
profil = s.groupby(s.index.dayofweek).mean()
ax.bar(["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"], profil.values, color="#10b981")
ax.set_title("Saisonnalité hebdomadaire (moyenne par jour)")

# 3. Heatmap année × mois
ax = fig.add_subplot(gs[1, 1])
ax_month = ax
tmp = s.to_frame("v")
tmp["annee"], tmp["mois"] = tmp.index.year, tmp.index.month
piv = tmp.pivot_table(index="annee", columns="mois", values="v", aggfunc="mean")
piv = piv.reindex(columns=range(1, 13))
im = ax.imshow(np.ma.masked_invalid(piv.values), cmap="YlOrRd", aspect="auto")
ax.set_xticks(range(12)); ax.set_xticklabels(["J", "F", "M", "A", "M", "J", "J", "A", "S", "O", "N", "D"])
ax.set_yticks(range(len(piv.index))); ax.set_yticklabels(piv.index)
fig.colorbar(im, ax=ax, fraction=.046); ax.set_title("Intensité moyenne par mois"); ax.grid(False)

# 4. Z-score des résidus
ax = fig.add_subplot(gs[2, :])
ax_zscore = ax
ax.plot(z.index, z.values, lw=.8, color="#8b5cf6")
ax.axhline(3, color="red", ls="--", lw=1); ax.axhline(-3, color="red", ls="--", lw=1)
ax.axhline(0, color="gray", lw=.8)
ax.set_title("Z-score glissant (seuils ±3)"); ax.set_ylabel("z")

add_hover_summaries(fig, {
    ax_series: "Gris: mesures quotidiennes; bleu: moyenne sur 7 jours.\nLa bande montre ±2 écarts-types; les croix signalent les anomalies.",
    ax_weekday: "Chaque barre donne la valeur moyenne du jour correspondant.\nCompare les jours pour repérer une saisonnalité hebdomadaire.",
    ax_month: "Chaque case montre la moyenne d'un mois et d'une année.\nUne couleur plus chaude indique une valeur plus élevée.",
    ax_zscore: "Le z-score mesure l'écart à la moyenne en écarts-types.\nAu-delà de +3 ou -3, le point est considéré comme atypique.",
})

fig.savefig("02_serie_temporelle.png", dpi=150, bbox_inches="tight")
plt.show()