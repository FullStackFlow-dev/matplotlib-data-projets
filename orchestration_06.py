"""Script 6 — Gantt d'exécution de jobs (DAG) + diagramme Sankey de lignage."""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Patch
from matplotlib.sankey import Sankey

plt.rcParams.update({"axes.titleweight": "bold", "grid.alpha": 0.3})
base = pd.Timestamp("2026-11-24 02:00")
C_STAT = {"succes": "#10b981", "echec": "#ef4444", "retry": "#f59e0b"}

# (nom, début en minutes, durée en minutes, statut)
jobs = [
    ("extract_api",     0,  25, "succes"), ("extract_db",     5,  35, "succes"),
    ("extract_files",  10,  15, "echec"),  ("retry_files",   30,  12, "succes"),
    ("validate",       45,  20, "succes"), ("transform",     65,  40, "succes"),
    ("quality_checks", 105, 15, "retry"),  ("load_warehouse",120, 30, "succes"),
    ("refresh_marts",  150, 20, "succes"), ("publish_reports",170, 10, "succes"),
]
deps = [(0, 4), (1, 4), (3, 4), (4, 5), (5, 6), (6, 7), (7, 8), (8, 9)]

fig = plt.figure(figsize=(15, 9), constrained_layout=True)
gs = fig.add_gridspec(2, 1, height_ratios=[1.6, 1])
fig.suptitle("Orchestration du pipeline — DAG du 24 nov. 2026", fontsize=16)

# --- Gantt ---
ax = fig.add_subplot(gs[0])
ypos = {i: len(jobs) - 1 - i for i in range(len(jobs))}  # premier job en haut
for i, (nom, debut, duree, statut) in enumerate(jobs):
    x0 = mdates.date2num(base + pd.Timedelta(minutes=debut))
    ax.broken_barh([(x0, duree / 1440)], (ypos[i], .6),
                facecolors=C_STAT[statut], edgecolor="white")
    ax.text(x0 + duree / 2880, ypos[i] + .3, f"{duree} min",
            ha="center", va="center", fontsize=8, color="white", fontweight="bold")
for a, b in deps:  # flèches de dépendance
    fin_a = mdates.date2num(base + pd.Timedelta(minutes=jobs[a][1] + jobs[a][2]))
    deb_b = mdates.date2num(base + pd.Timedelta(minutes=jobs[b][1]))
    ax.annotate("", xy=(deb_b, ypos[b] + .3), xytext=(fin_a, ypos[a] + .3),
                arrowprops=dict(arrowstyle="->", color="#6b7280", lw=1.2))
ax.set_yticks([y + .3 for y in ypos.values()])
ax.set_yticklabels([j[0] for j in jobs])
ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
ax.set_ylim(-.5, len(jobs)); ax.grid(axis="x")
ax.set_title("Gantt d'exécution des jobs"); ax.legend(handles=[Patch(color=c, label=s) for s, c in C_STAT.items()], fontsize=8)

# --- Sankey : flux de lignage (la somme des flows doit valoir 0) ---
ax2 = fig.add_subplot(gs[1]); ax2.axis("off")
sankey = Sankey(ax=ax2, scale=.008, offset=.25, head_angle=130, unit=" k")
sankey.add(flows=[60, 25, 15, -85, -15],          # entrées positives, sorties négatives
        labels=["API", "Base de données", "Fichiers", "Table propre", "Rejets"],
        orientations=[1, 1, 1, 0, -1],          # 1=haut, 0=horizontal, -1=bas
        facecolor="#2563eb", alpha=.85)
for d in sankey.finish():
    for t in d.texts:
        t.set_fontsize(9)
ax2.set_title("Lignage : volumes entrants / sortants du job de transformation")

fig.savefig("06_orchestration.png", dpi=150, bbox_inches="tight")
plt.show()