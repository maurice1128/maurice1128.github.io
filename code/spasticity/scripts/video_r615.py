# -*- coding: utf-8 -*-
"""r615: the gait animation drawn as the model, with the endpoint made legible.

Two things were wrong with the earlier version. It drew stick figures, and it asked the reader to
see a seven-degree difference on a foot two centimetres tall. This one draws the archived model
itself -- the bone meshes it was built from, posed by its own recorded body poses, with its own
muscle paths coloured by its own recorded activation -- and then shows the difference three ways:
at true scale in the walkers, magnified and aligned on the shank so that only the ankle angle
remains, and as all three ankle traces on a single axis.

Nothing is exaggerated. The magnified panel says it is magnified, and the separation it shows is
the separation in the data.
"""
import os, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import animation
from matplotlib.patches import Polygon, FancyArrowPatch
from matplotlib.colors import LinearSegmentedColormap
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import glob
import hfd_r613 as H
from skel_r610 import skeleton

OUT = r"C:\Users\maurice\Desktop\paper彙整\WEBSITE\site\assets\spasticity"
MODEL = glob.glob(r"C:\Users\maurice\Documents\SCONE\results\R151C_s101.*\H1922v7b3.hfd")[0]
INK, MUTE, RULE, FAINT = "#1a1a1a", "#6e6e6e", "#c9c9c9", "#ededed"
BONE_L, BONE_R, EDGE = "#e7e2d7", "#cfcabf", "#8d867a"
GRID = np.linspace(0, 100, 101)
PANELS = [("R151C", "Unlesioned control", "reference", "#111111"),
          ("R151S", "Plantarflexor hyperreflexia", "delivered reflex gain 0.100", "#c1361f"),
          ("R151W", "Dorsiflexor weakness", "tibialis anterior \u00d70.80", "#1f5c8a")]
DRAW = ["torso", "pelvis", "femur_r", "tibia_r", "calcn_r", "femur_l", "tibia_l", "calcn_l"]
MCMAP = LinearSegmentedColormap.from_list("act", ["#96a0ad", "#c2564a", "#e00d20"])

M = H.read_model(MODEL)
SIL = {}
for b in DRAW:
    s = []
    for poly, z in H.silhouettes(M, b):
        step = max(1, len(poly) // 150)          # decimate; these are smooth contours
        s.append((np.c_[poly[::step], np.full(len(poly[::step]), z)], z))
    SIL[b] = s
print("silhouettes: " + ", ".join("%s %d" % (b, sum(len(p) for p, _ in SIL[b])) for b in DRAW))


def cycle_of(fam):
    """One representative cycle: body poses, muscle activations and the ankle trace."""
    s = skeleton(fam)
    t, J, hs = s["t"], s["joints"], s["heel_strikes_s"]
    reps = []
    for a, b in zip(hs[:-1], hs[1:]):
        m = (t >= a) & (t <= b)
        if m.sum() < 20:
            continue
        u = np.linspace(0, 100, m.sum())
        px = J["pelvis"][m, 0]
        d = {"ankle_deg": np.interp(GRID, u, s["ankle_deg"][m]),
             "knee": np.c_[np.interp(GRID, u, J["knee"][m, 0] - px),
                           np.interp(GRID, u, J["knee"][m, 1])],
             "ankle": np.c_[np.interp(GRID, u, J["ankle"][m, 0] - px),
                            np.interp(GRID, u, J["ankle"][m, 1])],
             "heel": np.c_[np.interp(GRID, u, J["heel"][m, 0] - px),
                           np.interp(GRID, u, J["heel"][m, 1])],
             "toe": np.c_[np.interp(GRID, u, J["toe"][m, 0] - px),
                          np.interp(GRID, u, J["toe"][m, 1])]}
        d["pose"] = {}
        for b_, (p, R) in s["body"].items():
            P = np.c_[np.interp(GRID, u, p[m, 0] - px), np.interp(GRID, u, p[m, 1]),
                      np.interp(GRID, u, p[m, 2])]
            Q = np.stack([np.stack([np.interp(GRID, u, R[m, i, j]) for j in range(3)], -1)
                          for i in range(3)], 1)
            # renormalise the interpolated rotation
            for i in range(len(Q)):
                U, _, Vt = np.linalg.svd(Q[i])
                Q[i] = U @ Vt
            O = P - np.einsum("nij,j->ni", Q, M["bodies"][b_]["com"])
            d["pose"][b_] = (O, Q)
        d["act"] = {k: np.interp(GRID, u, v[m]) for k, v in s["act"].items()}
        reps.append(d)
    reps = reps[:-1] if len(reps) >= 2 else reps
    pk = np.array([c["ankle_deg"][62:].max() for c in reps])
    return reps[int(np.argmin(abs(pk - pk.mean())))]


data = []
for fam, label, sub, col in PANELS:
    d = cycle_of(fam)
    d.update(label=label, sub=sub, col=col,
             pk=float(d["ankle_deg"][62:].max()),
             pki=62 + int(np.argmax(d["ankle_deg"][62:])))
    data.append(d)
    print("%-11s swing peak %+.2f deg at %d%%" % (fam, d["pk"], d["pki"]))


def foot_polys(d, j):
    """The calcaneus bone meshes of the lesioned foot, in the panel's own coordinates."""
    O, Rm = d["pose"]["calcn_l"][0][j], d["pose"]["calcn_l"][1][j]
    return [(poly @ Rm.T + O)[:, :2] for poly, _ in SIL["calcn_l"]]


def aligned_foot(d, j):
    """Those same bones with the shank rotated to vertical: what is left is the ankle angle."""
    a, k = d["ankle"][j], d["knee"][j]
    v = a - k
    th = np.arctan2(v[1], v[0]) + np.pi / 2.0
    c, s = np.cos(-th), np.sin(-th)
    Rz = np.array([[c, -s], [s, c]])
    return [(W - a) @ Rz.T for W in foot_polys(d, j)]


fig = plt.figure(figsize=(12.8, 8.0), dpi=150)
fig.patch.set_facecolor("white")
gs = fig.add_gridspec(1, 2, width_ratios=[1.30, 1.0], wspace=0.055,
                      left=0.018, right=0.975, top=0.855, bottom=0.118)
gsl = gs[0, 0].subgridspec(1, 3, wspace=0.02)
gsb = gs[0, 1].subgridspec(2, 1, height_ratios=[1.06, 1.0], hspace=0.30)

art = []
for i, d in enumerate(data):
    a = fig.add_subplot(gsl[0, i])
    a.set_xlim(-0.40, 0.40); a.set_ylim(-0.055, 1.80); a.set_aspect("equal"); a.axis("off")
    a.axhline(0, color=RULE, lw=1.4, zorder=1)
    a.text(0, 1.735, d["label"], ha="center", fontsize=11.5, color=INK)
    a.text(0, 1.655, d["sub"], ha="center", fontsize=8.8, color=MUTE, style="italic")
    A = {"bones": {}, "muscles": {}}
    for b in DRAW:
        right = b.endswith("_r")
        A["bones"][b] = [a.add_patch(Polygon([[0, 0]], closed=True,
                                             facecolor=BONE_R if right else BONE_L,
                                             edgecolor=EDGE, lw=.55,
                                             zorder=2 if right else 4))
                         for _ in SIL[b]]
    for mn in M["muscles"]:
        right = mn.endswith("_r")
        A["muscles"][mn] = a.plot([], [], lw=1.3 if right else 2.8,
                                  color="#96a0ad", solid_capstyle="round",
                                  zorder=3 if right else 5, alpha=.45 if right else 1.0)[0]
    if i:
        A["ghost"] = [a.add_patch(Polygon([[0, 0]], closed=True, facecolor="none",
                                          edgecolor="#8a8a8a", lw=1.0, ls=(0, (3, 2)),
                                          zorder=6)) for _ in SIL["calcn_l"]]
        a.text(0, -0.036, "dashed: the control, same instant",
               ha="center", fontsize=7.2, color="#a3a3a3")
    art.append(A)

# -- magnified, shank-aligned ankles --------------------------------------------------
az = fig.add_subplot(gsb[0, 0])
az.set_xlim(-0.10, 0.26); az.set_ylim(-0.150, 0.105); az.set_aspect("equal"); az.axis("off")
az.set_title("The same three ankles, magnified and aligned on the shank",
             fontsize=11, color=INK, pad=8)
az.plot([0, 0], [0, 0.088], color=RULE, lw=10, solid_capstyle="round", zorder=1)
az.text(0.017, 0.080, "shank held vertical", fontsize=8.5, color=MUTE, va="center")
az.plot([-0.085, 0.25], [0, 0], color=FAINT, lw=1.0, zorder=0)
zfeet = [[az.add_patch(Polygon([[0, 0]], closed=True, facecolor="none",
                               edgecolor=d["col"], lw=2.0, zorder=3 + k))
          for _ in SIL["calcn_l"]] for k, d in enumerate(data)]
az.text(-0.085, -0.116, "ankle angle\nat this instant", fontsize=8.6, color=MUTE,
        ha="left", va="center", linespacing=1.45)
zlab = [az.text(0.055 + 0.062 * k, -0.116, "", fontsize=11.5, color=d["col"],
                ha="center", va="center", weight="bold") for k, d in enumerate(data)]

# -- one shared ankle axis ------------------------------------------------------------
ab = fig.add_subplot(gsb[1, 0])
ab.set_xlim(0, 100); ab.set_ylim(-27, 17)
ab.spines[["top", "right"]].set_visible(False)
for sp in ab.spines.values():
    sp.set_color(RULE)
ab.tick_params(colors=MUTE, labelsize=9, length=3)
ab.axhline(0, color=FAINT, lw=1.0)
ab.axvspan(62, 100, color="#f6f6f6", zorder=0)
ab.text(81, -25, "swing", fontsize=9, color="#a5a5a5", ha="center")
ab.set_xlabel("% gait cycle", fontsize=9.5, color=MUTE)
ab.set_ylabel("ankle angle (\u00b0)   dorsiflexion +", fontsize=9.5, color=MUTE)
ab.set_title("All three ankle traces on one axis", fontsize=11, color=INK, pad=8)
for d in data:
    ab.plot(GRID, d["ankle_deg"], color=d["col"], lw=2.0, zorder=3)
    ab.plot([d["pki"]], [d["pk"]], "o", color=d["col"], ms=6, mec="white", mew=1.2, zorder=5)
lo, hi = min(d["pk"] for d in data), max(d["pk"] for d in data)
ab.add_patch(FancyArrowPatch((96.5, lo), (96.5, hi), arrowstyle="<->", mutation_scale=9,
                             color=INK, lw=1.1, zorder=6))
ab.text(94.6, (lo + hi) / 2, "%.1f\u00b0" % (hi - lo), fontsize=10.5, color=INK,
        ha="right", va="center", weight="bold")
cursor = ab.axvline(0, color=INK, lw=1.0, alpha=.55, zorder=7)

fig.text(.5, .962, "Where the two lesions separate: peak dorsiflexion during swing",
         ha="center", fontsize=16.5, color=INK)
fig.text(.5, .925, "The model itself, posed by its own recorded body poses: its bone meshes, and "
                   "its own muscle paths shaded by their recorded activation.",
         ha="center", fontsize=10, color=MUTE)
fig.text(.5, .898, "One gait cycle of one seed per condition. The left leg is lesioned and the "
                   "camera follows the pelvis. Nothing is smoothed; no posture is averaged.",
         ha="center", fontsize=10, color=MUTE)
fig.text(.5, .042, "The separation is about seven degrees, and it is magnified only in the panel "
                   "that says so. Read the two lesions against each other, not against normality:",
         ha="center", fontsize=8.8, color="#8f8f8f")
fig.text(.5, .014, "the control's swing peak sits outside the normal adult range of 0\u20135\u00b0 "
                   "and the hyperreflexia model's sits inside it. Hyperreflexia runs fall later "
                   "than the cycle shown.",
         ha="center", fontsize=8.8, color="#8f8f8f")

NF, LOOPS = 101, 3


def draw(k):
    j = k % NF
    ctrl_foot = None
    for i, (d, A) in enumerate(zip(data, art)):
        pose = d["pose"]
        for b in DRAW:
            O, R = pose[b][0][j], pose[b][1][j]
            for patch, (poly, _) in zip(A["bones"][b], SIL[b]):
                W = poly @ R.T + O
                patch.set_xy(W[:, :2])
        for mn, path in M["muscles"].items():
            W = np.array([pose[bn][1][j] @ ps + pose[bn][0][j] for bn, ps in path
                          if bn in pose])
            if len(W) < 2:
                continue
            A["muscles"][mn].set_data(W[:, 0], W[:, 1])
            act = d["act"].get(mn, np.zeros(101))[j]
            A["muscles"][mn].set_color(MCMAP(min(max(act, 0.0), 1.0) ** .40))
        if i == 0:
            ctrl_foot = foot_polys(d, j)
        elif ctrl_foot is not None:
            for patch, W in zip(A["ghost"], ctrl_foot):
                patch.set_xy(W)
    for d, patches in zip(data, zfeet):
        for patch, W in zip(patches, aligned_foot(d, j)):
            patch.set_xy(W)
    for lab, d in zip(zlab, data):
        lab.set_text("%+.1f°" % d["ankle_deg"][j])
    cursor.set_xdata([GRID[j]])
    return []


ani = animation.FuncAnimation(fig, draw, frames=NF * LOOPS, interval=33, blit=False)
os.makedirs(OUT, exist_ok=True)
p = os.path.join(OUT, "vid_gait.mp4")
ani.save(p, writer=animation.FFMpegWriter(fps=30, bitrate=5200,
         extra_args=["-pix_fmt", "yuv420p", "-movflags", "+faststart"]))
print("-> %s  (%.1f MB)" % (p, os.path.getsize(p) / 1048576))
