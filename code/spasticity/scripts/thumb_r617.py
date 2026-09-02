# -*- coding: utf-8 -*-
"""r617: the card thumbnail, showing the ankles rather than the whole walker.

Three whole skeletons look like biomechanics but show nothing at 220 pixels, because the difference
between the two lesions lives in the ankle and is about seven degrees. This draws only that: the
same three calcaneus meshes from the same three cycles, each rotated so its own shank stands
vertical, so that what separates the outlines is the ankle angle and nothing else.

The angles printed are the live value of the ankle column for that cycle, not a group mean.
"""
import os, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import animation
from matplotlib.patches import Polygon
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import video_r615 as V

OUT = os.path.join(V.OUT, "thumb.mp4")
W, HGT, DPI = 460, 272, 100
NAMES = ["control", "hyperreflexia", "weakness"]

fig = plt.figure(figsize=(W / DPI, HGT / DPI), dpi=DPI)
fig.patch.set_facecolor("white")
ax = fig.add_axes([0.015, 0.315, 0.97, 0.575])
ax.set_xlim(-0.086, 0.231); ax.set_ylim(-0.139, 0.024)
ax.set_aspect("equal"); ax.axis("off")

ax.plot([-0.082, 0.228], [0, 0], color=V.FAINT, lw=1.0, zorder=0)
ax.plot([0, 0], [-0.004, 0.032], color="#d4d4d4", lw=13, solid_capstyle="round", zorder=1)
ZO, LW = [7, 4, 5], [2.0, 2.9, 3.2]
feet = [[ax.add_patch(Polygon([[0, 0]], closed=True, facecolor="none",
                              edgecolor=d["col"], lw=LW[k], zorder=ZO[k]))
         for _ in V.SIL["calcn_l"]] for k, d in enumerate(V.data)]
ax.plot([0], [0], "o", color="#1a1a1a", ms=4.0, zorder=20)

fig.text(.5, .948, "one ankle angle, three conditions", ha="center",
         fontsize=11.5, color="#1a1a1a")
fig.text(.5, .898, "each rotated so its own shank stands vertical", ha="center",
         fontsize=8.6, color="#8f8f8f", style="italic")
lab = []
for k, d in enumerate(V.data):
    x = 0.185 + 0.315 * k
    fig.text(x, .175, NAMES[k], ha="center", fontsize=9.4, color=d["col"], weight="bold")
    lab.append(fig.text(x, .048, "", ha="center", fontsize=14.5, color=d["col"], weight="bold"))


def draw(k):
    j = k % 101
    for d, patches in zip(V.data, feet):
        for patch, poly in zip(patches, V.aligned_foot(d, j)):
            patch.set_xy(poly)
    for t, d in zip(lab, V.data):
        t.set_text("%+.1f°" % d["ankle_deg"][j])
    return []


ani = animation.FuncAnimation(fig, draw, frames=101 * 2, interval=33, blit=False)
ani.save(OUT, writer=animation.FFMpegWriter(fps=30, bitrate=1400,
         extra_args=["-pix_fmt", "yuv420p", "-movflags", "+faststart"]))
print("-> %s  (%.0f KB)" % (OUT, os.path.getsize(OUT) / 1024))
