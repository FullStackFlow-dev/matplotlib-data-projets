"""Script 5 — Rapport qualité : manquants, invalides, outliers, doublons, fraîcheur."""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from hover_summaries import add_hover_summaries

rng = np.random.default_rng(5)
plt.rcParams.update({"axes.spines.top": False, "axes.spines.right": False,
                     "axes.grid": True, "grid.alpha": 0.3, "axes.titleweight": "bold"})

# --- Dataset avec problèmes injectés volontairement ---
n = 5000
df = pd.DataFrame({
    "id": np.arange(n),
    "timestamp": pd.date_range("2026-11-01", periods=n, freq="min"),
    "user_id": rng.integers(1000, 9999, n).astype(float),
    "email": [f"user{i}@exemple.com" for i in range(n)],
    "montant": rng.lognormal(3, .8, n).round(2),
    "pays": rng.choice(["SN", "FR", "US", "CI", "MA"], n),
    "score": rng.uniform(0, 1, n).round(3),
})
for col, frac in {"user_id": .08, "email": .03, "montant": .12, "pays": .05, "score": .20}.items():
    df.loc[rng.choice(n, int(n * frac), replace=False), col] = np.nan
df.loc[rng.choice(n, 60, replace=False), "email"] = "invalide"          # formats cassés
df.loc[rng.choice(n, 25, replace=False), "montant"] *= 50               # outliers
df = pd.concat([df, df.sample(120, random_state=1)], ignore_index=True) # doublons

fig, axes = plt.subplots(2, 3, figsize=(16, 9), constrained_layout=True)
fig.suptitle(f"Rapport qualité — {len(df)} lignes, {df.shape[1]} colonnes", fontsize=16)

# 1. Matrice des valeurs manquantes (échantillon)
ax = axes[0, 0]
ech = df.sample(150, random_state=2).sort_index()
ax.imshow(ech.isna().values, aspect="auto", cmap="Reds", vmin=0, vmax=1, interpolation="nearest")
ax.set_xticks(range(df.shape[1])); ax.set_xticklabels(df.columns, rotation=45, ha="right")
ax.set_ylabel("Lignes (échantillon)"); ax.set_title("Matrice des manquants (rouge = NaN)"); ax.grid(False)

# 2. Complétude par colonne
ax = axes[0, 1]
comp = ((1 - df.isna().mean()) * 100).sort_values()
couleurs = ["#10b981" if v >= 95 else "#f59e0b" if v >= 85 else "#ef4444" for v in comp]
ax.barh(comp.index, comp.values, color=couleurs)
ax.axvline(95, color="black", ls="--", lw=1, label="Objectif 95 %")
for i, v in enumerate(comp.values):
    ax.text(v + .5, i, f"{v:.1f}%", va="center", fontsize=8)
ax.set_xlim(0, 105); ax.set_title("Complétude (% non-null)"); ax.legend(fontsize=8)

# 3. Outliers sur montant (règle IQR, échelle log)
ax = axes[0, 2]
vals = df["montant"].dropna().values
q1, q3 = np.percentile(vals, [25, 75]); iqr = q3 - q1
n_out = ((vals < q1 - 1.5 * iqr) | (vals > q3 + 1.5 * iqr)).sum()
ax.boxplot(vals, patch_artist=True, boxprops=dict(facecolor="#8b5cf6", alpha=.6))
ax.set_yscale("log"); ax.set_xticklabels(["montant"])
ax.set_title(f"Outliers (IQR) : {n_out} détectés — échelle log")

# 4. Valides / invalides / manquants par colonne
ax = axes[1, 0]
cols = ["user_id", "email", "montant", "pays", "score"]
manquants = df[cols].isna().sum().values
invalides = np.array([(df[c].notna() & ~df[c].astype(str).str.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")).sum()
            if c == "email" else 0 for c in cols])
valides = len(df) - manquants - invalides  
ax.bar(cols, valides, color="#10b981", label="Valides")
ax.bar(cols, invalides, bottom=valides, color="#ef4444", label="Invalides")
ax.bar(cols, manquants, bottom=valides + invalides, color="#94a3b8", label="Manquants")
ax.tick_params(axis="x", rotation=30); ax.set_title("Validation par colonne"); ax.legend(fontsize=8)

# 5. Doublons par jour
ax = axes[1, 1]
df["jour"] = df["timestamp"].dt.normalize()
dups = df[df.duplicated(keep="first")].groupby("jour").size()
dups = dups.reindex(pd.date_range(df["jour"].min(), df["jour"].max()), fill_value=0)
ax.bar(dups.index, dups.values, color="#ef4444")
ax.tick_params(axis="x", rotation=30); ax.set_title(f"Doublons par jour (total : {dups.sum()})")

# 6. Fraîcheur des tables (heures depuis la dernière ingestion)
ax = axes[1, 2]
tables = ["raw_events", "dim_users", "fact_orders", "agg_daily", "ml_features"]
retard = rng.uniform(.2, 30, len(tables))
ax.barh(tables, retard, color=["#ef4444" if r > 6 else "#10b981" for r in retard])
ax.axvline(6, color="black", ls="--", lw=1, label="SLA fraîcheur : 6 h")
ax.set_xlabel("Heures depuis ingestion"); ax.set_title("Fraîcheur des tables"); ax.legend(fontsize=8)

add_hover_summaries(fig, {
    axes[0, 0]: "Rouge indique une valeur manquante dans l'échantillon de 150 lignes.\nChaque colonne correspond à un champ du jeu de données.",
    axes[0, 1]: "Chaque barre montre le pourcentage de valeurs renseignées.\nLa ligne pointillée fixe l'objectif de complétude à 95 %.",
    axes[0, 2]: "La boîte résume les montants sur une échelle logarithmique.\nLes valeurs isolées sont les outliers détectés par la règle IQR.",
    axes[1, 0]: "Les barres séparent les valeurs valides, invalides et manquantes.\nCompare leur répartition entre les différents champs.",
    axes[1, 1]: "Chaque barre compte les doublons détectés ce jour-là.\nUne valeur nulle signifie qu'aucun doublon n'a été trouvé.",
    axes[1, 2]: "La barre indique les heures depuis la dernière ingestion.\nAu-delà de la ligne des 6 h, le SLA de fraîcheur est dépassé.",
})

fig.savefig("05_data_quality.png", dpi=150, bbox_inches="tight")
plt.show()