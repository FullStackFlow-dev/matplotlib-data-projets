"""Script 7 — Dashboard temps réel : débit et latence d'un flux (type Kafka)."""
import numpy as np
import matplotlib.pyplot as plt
from collections import deque
from matplotlib.animation import FuncAnimation
from hover_summaries import add_hover_summaries

rng = np.random.default_rng()
N = 120  # fenêtre glissante de 120 points
buf_t, buf_debit, buf_lat = deque(maxlen=N), deque(maxlen=N), deque(maxlen=N)

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 7), constrained_layout=True)
fig.suptitle("Monitoring temps réel du flux", fontsize=15, fontweight="bold")
line1, = ax1.plot([], [], color="#2563eb", lw=1.5)
line2, = ax2.plot([], [], color="#f59e0b", lw=1.5)
ax1.set_ylabel("Débit (msg/s)"); ax2.set_ylabel("Latence (ms)"); ax2.set_xlabel("Temps (ticks)")
ax2.axhline(200, color="red", ls="--", lw=1, label="Seuil latence : 200 ms"); ax2.legend(fontsize=8)
for ax in (ax1, ax2):
    ax.grid(alpha=.3)
txt1 = ax1.text(.99, .88, "", transform=ax1.transAxes, ha="right", fontweight="bold", color="#2563eb")
txt2 = ax2.text(.99, .88, "", transform=ax2.transAxes, ha="right", fontweight="bold", color="#f59e0b")

step = 0
def update(frame):
    global step
    step += 1
    debit = max(0, 500 + 150 * np.sin(step / 12) + rng.normal(0, 40))
    lat = max(5, 80 + 30 * np.sin(step / 25) + rng.normal(0, 15)
            + (150 if rng.random() < .03 else 0))  # pics aléatoires
    buf_t.append(step); buf_debit.append(debit); buf_lat.append(lat)
    line1.set_data(buf_t, buf_debit); line2.set_data(buf_t, buf_lat)
    for ax in (ax1, ax2):
        ax.relim(); ax.autoscale_view()
        ax.set_xlim(buf_t[0], buf_t[-1] + 1)
    txt1.set_text(f"{debit:,.0f} msg/s"); txt2.set_text(f"{lat:.0f} ms")
    return line1, line2, txt1, txt2

add_hover_summaries(fig, {
    ax1: "Le débit mesure les messages traités par seconde.\nLa courbe suit les variations d'activité du flux.",
    ax2: "La latence mesure le délai de traitement en millisecondes.\nAu-dessus de la ligne rouge, le seuil de 200 ms est dépassé.",
})

ani = FuncAnimation(fig, update, interval=400, blit=False)  # garder une référence à `ani` !
plt.show()