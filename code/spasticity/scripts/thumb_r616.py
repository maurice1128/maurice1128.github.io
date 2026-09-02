# -*- coding: utf-8 -*-
"""r616: the card thumbnail for the index page.

The full animation carries three panels of analysis and a caption; at the 460-pixel width the index
cards use, none of that is readable. This is the same three models from the same three cycles, drawn
larger and with everything else stripped out. It makes no claim on its own -- at this size the seven
degrees that separate the two lesions are a couple of pixels -- so it carries no numbers.
"""
import os, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import animation
from matplotlib.patches import Polygon
from matplotlib.colors import LinearSegmentedColormap
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import video_r615 as V

OUT = os.path.join(V.OUT, "thumb.mp4")
W, HGT, DPI = 460, 440, 100

fig = plt.figure(figsize=(W / DPI, HGT / DPI), dpi=DPI)
fig.patch.set_facecolor("white")
gs = fig.add_gridspec(1, 3, wspace=0.0, left=0.005, right=0.995, top=0.905, bottom=0.012)

art = []
for i, d in enumerate(V.data):
    a = fig.add_subplot(gs[0, i])
    a.set_xlim(-0.36, 0.36); a.set_ylim(-0.045, 1.80)
    a.set_aspect("equal"); a.axis("off")
    a.axhline(0, color=V.RULE, lw=1.2, zorder=1)
    a.text(0, 1.86, ["control", "hyperreflexia", "weakness"][i], ha="center",
           fontsize=8.5, color=d["col"], weight="bold")
    A = {"bones": {}, "muscles": {}}
    for b in V.DRAW:
        right = b.endswith("_r")
        A["bones"][b] = [a.add_patch(Polygon([[0, 0]], closed=True,
                                             facecolor=V.BONE_R if right else V.BONE_L,
                                             edgecolor=V.EDGE, lw=.45,
                                             zorder=2 if right else 4))
                         for _ in V.SIL[b]]
    for mn in V.M["muscles"]:
        right = mn.endswith("_r")
        A["muscles"][mn] = a.plot([], [], lw=1.0 if right else 2.2, color="#96a0ad",
                                  solid_capstyle="round", zorder=3 if right else 5,
                                  alpha=.45 if right else 1.0)[0]
    art.append(A)


def draw(k):
    j = k % 101
    for d, A in zip(V.data, art):
        pose = d["pose"]
        for b in V.DRAW:
            O, R = pose[b][0][j], pose[b][1][j]
            for patch, (poly, _) in zip(A["bones"][b], V.SIL[b]):
                patch.set_xy((poly @ R.T + O)[:, :2])
        for mn, path in V.M["muscles"].items():
            P = np.array([pose[bn][1][j] @ ps + pose[bn][0][j] for bn, ps in path if bn in pose])
            if len(P) < 2:
                continue
            A["muscles"][mn].set_data(P[:, 0], P[:, 1])
            A["muscles"][mn].set_color(V.MCMAP(min(max(d["act"].get(mn, np.zeros(101))[j], 0.), 1.) ** .40))
    return []


ani = animation.FuncAnimation(fig, draw, frames=101 * 2, interval=33, blit=False)
ani.save(OUT, writer=animation.FFMpegWriter(fps=30, bitrate=1500,
         extra_args=["-pix_fmt", "yuv420p", "-movflags", "+faststart"]))
print("-> %s  (%.0f KB)" % (OUT, os.path.getsize(OUT) / 1024))
