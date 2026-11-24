"""Script 4 — Dashboard de monitoring d'un pipeline ETL (runs horaires sur 7 jours)."""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from hover_summaries import add_hover_summaries

rng = np.random.default_rng(11)
plt.rcParams.update({"axes.spines.top": False, "axes.spines.right": False,
"axes.grid": True, "grid.alpha": 0.3, "axes.titleweight": "bold"})

# --- Logs de runs simulés ---
heures = pd.date_range("2026-11-17", periods=24 * 7, freq="h")
n = len(heures)
statut = rng.choice(["succes", "echec", "retry"], n, p=[.90, .06, .04])
duree = rng.lognormal(3.4, .45, n)
duree[statut == "echec"] *= rng.uniform(1.5, 3, (statut == "echec").sum())
df = pd.DataFrame({"start": heures, "statut": statut,
"duree_s": duree.round(1), "rows": rng.integers(5_000, 80_000, n)})
df["jour"] = df["start"].dt.normalize()
df["heure"] = df["start"].dt.hour

fig, axes = plt.subplots(3, 2, figsize=(16, 12), constrained_layout=True)
fig.suptitle("Monitoring pipeline ETL — semaine du 17 au 23 nov. 2026", fontsize=16)
C_STAT = {"succes": "#10b981", "retry": "#f59e0b", "echec": "#ef4444"}

# 1. Volume traité par jour, empilé par statut
ax = axes[0, 0]
piv = df.pivot_table(index="jour", columns="statut", values="rows", aggfunc="sum") \
        .reindex(columns=["succes", "retry", "echec"]).fillna(0)
ax.stackplot(piv.index, piv["succes"], piv["retry"], piv["echec"],
labels=["succes", "retry", "echec"], colors=[C_STAT[s] for s in piv.columns], alpha=.85)
ax.tick_params(axis="x", rotation=30); ax.set_title("Volume de lignes traitées / jour")
ax.legend(fontsize=8, loc="upper left")

# 2. Percentiles de durée (p50 / p95 / p99) vs SLA
ax = axes[0, 1]
perc = df.groupby("jour")["duree_s"].quantile([.5, .95, .99]).unstack()
for col, c, lab in zip(perc.columns, ["#10b981", "#f59e0b", "#ef4444"], ["p50", "p95", "p99"]):
    ax.plot(perc.index, perc[col], marker="o", ms=4, color=c, label=lab)
ax.axhline(120, color="black", ls="--", lw=1.2, label="SLA = 120 s")
ax.set_ylabel("Durée (s)"); ax.tick_params(axis="x", rotation=30)
ax.set_title("Latence du pipeline : percentiles vs SLA"); ax.legend(fontsize=8)

# 3. Taux d'échec par jour avec seuil d'alerte
ax = axes[1, 0]
err = df.groupby("jour")["statut"].apply(lambda s: (s != "succes").mean() * 100)
couleurs = ["#ef4444" if v > 8 else "#2563eb" for v in err]
ax.bar(err.index, err.values, color=couleurs)
ax.axhline(8, color="red", ls="--", lw=1.2, label="Seuil d'alerte : 8 %")
ax.set_ylabel("% runs non réussis"); ax.tick_params(axis="x", rotation=30)
ax.set_title("Taux d'échec quotidien"); ax.legend(fontsize=8)

# 4. Donut des statuts
ax = axes[1, 1]
counts = df["statut"].value_counts()
ax.pie(counts, labels=counts.index, autopct="%1.1f%%",
    colors=[C_STAT[s] for s in counts.index], startangle=90,
    wedgeprops=dict(width=.4, edgecolor="white"))
ax.text(0, 0, f"{n}\nruns", ha="center", va="center", fontweight="bold", fontsize=13)
ax.set_title("Répartition des statuts")

# 5. Heatmap des échecs : jour × heure (trouver les créneaux problématiques)
ax = axes[2, 0]
fail = df[df["statut"] == "echec"].pivot_table(index="jour", columns="heure",
values="rows", aggfunc="count")
fail = fail.reindex(columns=range(24)).fillna(0)
im = ax.imshow(fail.values, cmap="Reds", aspect="auto")
ax.set_xticks(range(0, 24, 2)); ax.set_xticklabels([f"{h}h" for h in range(0, 24, 2)])
ax.set_yticks(range(len(fail.index)))
ax.set_yticklabels([d.strftime("%a %d") for d in fail.index])
fig.colorbar(im, ax=ax, fraction=.046, label="nb échecs")
ax.set_title("Échecs par jour et heure"); ax.grid(False)

# 6. Durée vs volume, coloré par statut (les échecs sont-ils liés aux gros volumes ?)
ax = axes[2, 1]
for s, c in C_STAT.items():
    sub = df[df["statut"] == s]
    ax.scatter(sub["rows"], sub["duree_s"], s=18, alpha=.6, color=c, label=s)
ax.set_xlabel("Lignes traitées"); ax.set_ylabel("Durée (s)"); ax.set_yscale("log")
ax.set_title("Durée vs volume (échelle log)"); ax.legend(fontsize=8)

add_hover_summaries(fig, {
    axes[0, 0]: "L'aire empilée montre le volume quotidien par statut.\nLa hauteur totale compare les lignes traitées chaque jour.",
    axes[0, 1]: "p50 est la médiane; p95 et p99 indiquent les durées élevées.\nAu-dessus de la ligne grise, le SLA de 120 s est dépassé.",
    axes[1, 0]: "Chaque barre donne la part des runs échoués ou relancés.\nLa ligne rouge marque le seuil d'alerte de 8 %.",
    axes[1, 1]: "Chaque secteur représente la part d'un statut parmi les runs.\nLe nombre au centre indique le total observé.",
    axes[2, 0]: "La couleur montre les échecs selon le jour et l'heure.\nPlus le rouge est foncé, plus les échecs sont nombreux.",
    axes[2, 1]: "Chaque point représente un run; l'axe vertical est logarithmique.\nCompare sa durée au volume et à son statut.",
})

fig.savefig("04_monitoring_etl.png", dpi=150, bbox_inches="tight")
plt.show()