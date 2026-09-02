# -*- coding: utf-8 -*-
"""r611: animate one gait cycle of the control, hyperreflexia and weakness models side by side.

Drawn from the archived simulation output through the joint centres reconstructed in r610, with the
camera following the pelvis. Nothing is redrawn by hand and nothing is smoothed: the ankle angle
plotted underneath each figure is the column the paper's endpoint is taken from.

One cycle per condition is shown rather than an average over cycles, because averaging positions
across cycles would draw a posture the model never held. The cycle shown is the one whose swing
peak is closest to that run's own mean over its admitted cycles.
"""
import os, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import animation
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from skel_r610 import skeleton

OUT = r"C:\Users\maurice\Desktop\paper彙整\WEBSITE\site\assets\spasticity"
INK, ACC, GREY, RULE = "#000000", "#c1361f", "#a8a8a8", "#cccccc"
GRID = np.linspace(0, 100, 101)
PANELS = [("R151C", "Unlesioned control", INK),
          ("R151S", "Plantarflexor hyperreflexia\ndelivered gain 0.100", ACC),
          ("R151W", "Dorsiflexor weakness\ntibialis anterior \u00d70.80", "#1f5c8a")]
SEG = [("hip", "knee"), ("knee", "ankle"), ("heel", "toe"), ("ankle", "toe"), ("ankle", "heel")]
SEG_R = [("hip_r", "knee_r"), ("knee_r", "ankle_r"), ("heel_r", "toe_r"),
         ("ankle_r", "toe_r"), ("ankle_r", "heel_r")]


def cycles(s):
    """Each admitted cycle, resampled to 101 points, camera fixed on the pelvis."""
    t, J = s["t"], s["joints"]
    hs = s["heel_strikes_s"]
    out = []
    for a, b in zip(hs[:-1], hs[1:]):
        m = (t >= a) & (t <= b)
        if m.sum() < 20:
            continue
        u = np.linspace(0, 100, m.sum())
        px = J["pelvis"][m, 0]
        d = {k: np.c_[np.interp(GRID, u, v[m, 0] - px), np.interp(GRID, u, v[m, 1])]
             for k, v in J.items()}
        d["ankle_deg"] = np.interp(GRID, u, s["ankle_deg"][m])
        d["tib_ant"] = np.interp(GRID, u, s["tib_ant_l"][m])
        d["plantar"] = np.interp(GRID, u, np.maximum(s["soleus_l"][m], s["gastroc_l"][m]))
        out.append(d)
    return out[:-1] if len(out) >= 2 else out


def representative(cs):
    """The cycle whose swing peak is closest to this run's mean over its admitted cycles."""
    sw = slice(62, 101)
    pk = np.array([c["ankle_deg"][sw].max() for c in cs])
    return cs[int(np.argmin(abs(pk - pk.mean())))], float(pk.mean())


data = []
for fam, label, col in PANELS:
    s = skeleton(fam)
    cs = cycles(s)
    rep, mean_pk = representative(cs)
    data.append((label, col, rep, mean_pk, len(cs)))
    print("%-11s %d admitted cycles, mean swing peak %+.2f deg" % (fam, len(cs), mean_pk))

fig = plt.figure(figsize=(11.4, 7.2), dpi=100)
fig.patch.set_facecolor("white")
gs = fig.add_gridspec(2, 3, height_ratios=[2.3, 1.0], hspace=0.34, wspace=0.22,
                      left=0.085, right=0.965, top=0.815, bottom=0.135)
axf, axa, art = [], [], []
for i, (label, col, rep, mean_pk, ncyc) in enumerate(data):
    a = fig.add_subplot(gs[0, i]); axf.append(a)
    a.set_xlim(-0.95, 0.95); a.set_ylim(-0.06, 1.85); a.set_aspect("equal")
    a.axis("off")
    a.plot([-0.95, 0.95], [0, 0], color=RULE, lw=1.1, zorder=0)
    a.set_title(label, fontsize=10.5, color=INK, pad=11, linespacing=1.6)
    b = fig.add_subplot(gs[1, i]); axa.append(b)
    b.set_xlim(0, 100); b.set_ylim(-26, 16)
    b.spines[["top", "right"]].set_visible(False)
    for sp in b.spines.values():
        sp.set_color(RULE)
    b.tick_params(colors="#767676", labelsize=8.5, length=3)
    b.axhline(0, color=RULE, lw=.8)
    b.axvspan(62, 100, color="#f2f2f2", zorder=0)
    bg = b.twinx()
    bg.set_ylim(0, 1.0); bg.set_xlim(0, 100); bg.axis("off")
    bg.fill_between(GRID, 0, rep["plantar"], color=col, alpha=.13, lw=0, zorder=0)
    b.set_zorder(bg.get_zorder() + 1); b.patch.set_visible(False)
    b.plot(GRID, rep["ankle_deg"], color=col, lw=1.8, zorder=3)
    pk = rep["ankle_deg"][62:].max(); pki = 62 + int(np.argmax(rep["ankle_deg"][62:]))
    b.plot([pki], [pk], "o", color=col, ms=5.5, zorder=5)
    b.annotate("%+.2f\u00b0" % pk, (pki, pk), textcoords="offset points", xytext=(0, 9),
               ha="center", fontsize=9.5, color=col, weight="bold")
    b.set_xlabel("% gait cycle", fontsize=9, color="#767676")
    if i == 0:
        b.set_ylabel("ankle angle (\u00b0)\ndorsiflexion +", fontsize=9, color="#767676")
        b.text(81, -23.5, "swing", fontsize=8.5, color="#999999", ha="center")
        b.text(2, -25.4, "shaded: plantarflexor activation", fontsize=7.8,
               color="#9a9a9a", va="bottom")
    L = dict(solid_capstyle="round", zorder=4)
    art.append({
        "R": [a.plot([], [], color=GREY, lw=3.0, **L)[0] for _ in SEG_R],
        "L": [a.plot([], [], color=col, lw=4.2, **L)[0] for _ in SEG],
        "trunk": a.plot([], [], color=INK, lw=5.0, **L)[0],
        "head": a.plot([], [], "o", color=INK, ms=13, zorder=5)[0],
        "cursor": b.axvline(0, color=INK, lw=1.0, alpha=.65),
    })

fig.text(.5, .962, "One gait cycle from each condition, drawn from the archived simulation output",
         ha="center", fontsize=13.5, color=INK)
fig.text(.5, .922, "Left leg is the lesioned side; the camera follows the pelvis. One cycle of one "
                   "seed, not a group mean:", ha="center", fontsize=9.5, color="#767676")
fig.text(.5, .893, "nothing is smoothed and no posture is averaged across cycles.",
         ha="center", fontsize=9.5, color="#767676")
fig.text(.5, .055, "Read the two lesions against each other, not against normality: in this model "
                   "the unlesioned control's swing peak sits outside",
         ha="center", fontsize=8.5, color="#8a8a8a")
fig.text(.5, .022, "the normal adult range of 0-5 deg, and the hyperreflexia model's sits inside it. "
                   "Hyperreflexia runs fall later than the cycle shown.",
         ha="center", fontsize=8.5, color="#8a8a8a")

NF, LOOPS = 101, 3


def draw(k):
    j = k % NF
    for (label, col, rep, mp, nc), A in zip(data, art):
        for ln, (p, q) in zip(A["L"], SEG):
            ln.set_data([rep[p][j, 0], rep[q][j, 0]], [rep[p][j, 1], rep[q][j, 1]])
        for ln, (p, q) in zip(A["R"], SEG_R):
            ln.set_data([rep[p][j, 0], rep[q][j, 0]], [rep[p][j, 1], rep[q][j, 1]])
        A["trunk"].set_data([rep["pelvis"][j, 0], rep["neck"][j, 0]],
                            [rep["pelvis"][j, 1], rep["neck"][j, 1]])
        A["head"].set_data([rep["neck"][j, 0]], [rep["neck"][j, 1] + .09])
        A["cursor"].set_xdata([GRID[j]])
    return []


ani = animation.FuncAnimation(fig, draw, frames=NF * LOOPS, interval=33, blit=False)
os.makedirs(OUT, exist_ok=True)
p = os.path.join(OUT, "vid_gait.mp4")
ani.save(p, writer=animation.FFMpegWriter(fps=30, bitrate=2600,
         extra_args=["-pix_fmt", "yuv420p", "-movflags", "+faststart"]))
print("-> %s  (%.1f MB)" % (p, os.path.getsize(p) / 1048576))
