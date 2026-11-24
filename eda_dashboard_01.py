"""Script 1 — Dashboard EDA complet sur un dataset de ventes."""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from hover_summaries import add_hover_summaries

rng = np.random.default_rng(42)
COLORS = ["#2563eb", "#f59e0b", "#10b981", "#ef4444", "#8b5cf6"]
plt.rcParams.update({"axes.spines.top": False, "axes.spines.right": False,
                     "axes.grid": True, "grid.alpha": 0.3, "axes.titleweight": "bold"})

# --- Données synthétiques ---
n = 1500
df = pd.DataFrame({
    "date": rng.choice(pd.date_range("2026-01-01", periods=300), n),
    "region": rng.choice(["Nord", "Sud", "Est", "Ouest"], n, p=[.3, .3, .2, .2]),
    "produit": rng.choice(["API", "Dashboard", "Pipeline", "ML Model"], n),
    "quantite": rng.integers(1, 50, n),
    "prix_unitaire": rng.uniform(5, 200, n).round(2),
    "satisfaction": rng.normal(4, 0.8, n).clip(1, 5).round(1),
})
df["ca"] = df["quantite"] * df["prix_unitaire"]
df["mois"] = df["date"].dt.to_period("M").dt.to_timestamp()

fig, axes = plt.subplots(2, 3, figsize=(16, 9), constrained_layout=True)
fig.suptitle("Analyse exploratoire — Ventes 2026", fontsize=16)

# 1. Histogramme du CA avec moyenne / médiane
ax = axes[0, 0]
ax.hist(df["ca"], bins=40, color=COLORS[0], alpha=.8, edgecolor="white")
ax.axvline(df["ca"].mean(), color="red", ls="--", label=f"Moyenne : {df['ca'].mean():,.0f}")
ax.axvline(df["ca"].median(), color="black", ls=":", label=f"Médiane : {df['ca'].median():,.0f}")
ax.set_title("Distribution du chiffre d'affaires"); ax.legend(fontsize=8)

# 2. Boxplots par région (détection d'outliers)
ax = axes[0, 1]
regions = sorted(df["region"].unique())
bp = ax.boxplot([df.loc[df["region"] == r, "ca"].values for r in regions],
                patch_artist=True, showmeans=True)
for patch, c in zip(bp["boxes"], COLORS):
    patch.set_facecolor(c); patch.set_alpha(.6)
ax.set_xticklabels(regions); ax.set_title("CA par région")

# 3. Scatter + droite de régression
ax = axes[0, 2]
for r, c in zip(regions, COLORS):
    sub = df[df["region"] == r]
    ax.scatter(sub["quantite"], sub["ca"], s=12, alpha=.5, color=c, label=r)
m, b = np.polyfit(df["quantite"], df["ca"], 1)
xs = np.linspace(df["quantite"].min(), df["quantite"].max(), 50)
ax.plot(xs, m * xs + b, "k--", lw=1.5, label="Tendance")
ax.set_xlabel("Quantité"); ax.set_ylabel("CA"); ax.set_title("Quantité vs CA"); ax.legend(fontsize=7)

# 4. Heatmap de corrélation
ax = axes[1, 0]
cols = ["quantite", "prix_unitaire", "satisfaction", "ca"]
corr = df[cols].corr()
im = ax.imshow(corr, cmap="RdBu_r", vmin=-1, vmax=1)
ax.set_xticks(range(len(cols))); ax.set_xticklabels(cols, rotation=30, ha="right")
ax.set_yticks(range(len(cols))); ax.set_yticklabels(cols)
for i in range(len(cols)):
    for j in range(len(cols)):
        ax.text(j, i, f"{corr.iloc[i, j]:.2f}", ha="center", va="center", fontsize=9)
fig.colorbar(im, ax=ax, fraction=.046); ax.set_title("Corrélations"); ax.grid(False)

# 5. Top produits (barres horizontales)
ax = axes[1, 1]
ca_prod = df.groupby("produit")["ca"].sum().sort_values()
ax.barh(ca_prod.index, ca_prod.values, color=COLORS[:len(ca_prod)])
ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _: f"{x/1000:.0f}k"))
ax.set_title("CA total par produit")

# 6. Évolution mensuelle
ax = axes[1, 2]
ca_m = df.groupby("mois")["ca"].sum()
ax.plot(ca_m.index, ca_m.values, marker="o", ms=4, color=COLORS[0])
ax.fill_between(ca_m.index, ca_m.values, alpha=.15, color=COLORS[0])
ax.tick_params(axis="x", rotation=30); ax.set_title("CA mensuel")

add_hover_summaries(fig, {
    axes[0, 0]: "La hauteur compte les ventes par tranche de chiffre d'affaires.\nLes traits rouge et noir indiquent moyenne et médiane.",
    axes[0, 1]: "La boîte couvre la moitié centrale des CA de la région.\nLe trait marque la médiane; les points isolés sont atypiques.",
    axes[0, 2]: "Chaque point est une vente: quantité en bas, CA à gauche.\nLa droite résume la tendance, sans prouver une causalité.",
    axes[1, 0]: "La corrélation va de -1 à +1: elle indique le sens et la force du lien.\nUne corrélation ne prouve pas une relation de cause à effet.",
    axes[1, 1]: "Chaque barre représente le CA total d'un produit.\nPlus elle est longue, plus le chiffre d'affaires est élevé.",
    axes[1, 2]: "Chaque point correspond au CA total d'un mois.\nLa courbe permet de suivre son évolution dans le temps.",
})

fig.savefig("01_eda_dashboard.png", dpi=150, bbox_inches="tight")
plt.show()