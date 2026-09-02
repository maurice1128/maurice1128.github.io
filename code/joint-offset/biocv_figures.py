"""Figures for MANUSCRIPT_v4.md. Every value is transcribed from a verified result file
in D:/BioCV/ and is cited in the caption. Nothing here is recomputed or smoothed.

Sources: BIOCV_PERM_V3.txt (m=50 family), BIOCV_EQUIV.txt, BIOCV_PERJOINT_GN.txt,
BIOCV_MATCHED_K.txt, BIOCV_UNDISTORT.txt, BIOCV_POSTURE.txt.
-> D:/ROWV_paper/figures/fig1..fig5 .png and .pdf
"""
import io
import os
import re
import re as _re   # Figure 3 rebinds `re` to an array
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

OUT = "D:/ROWV_paper/figures"
os.makedirs(OUT, exist_ok=True)

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 8,
    "axes.linewidth": 0.7, "axes.edgecolor": "#333333",
    "axes.spines.top": False, "axes.spines.right": False,
    "xtick.major.width": 0.7, "ytick.major.width": 0.7,
    "xtick.color": "#333333", "ytick.color": "#333333",
    "axes.labelcolor": "#111111", "text.color": "#111111",
    "figure.dpi": 200, "savefig.dpi": 1000, "savefig.bbox": "tight",
    # The Guide for Authors asks for 1000 dpi on bitmapped line drawings, and for embedded
    # fonts in vector artwork. Matplotlib defaults to Type 3 subsets, which Elsevier's
    # artwork check rejects; fonttype 42 writes real TrueType instead.
    "pdf.fonttype": 42, "ps.fonttype": 42,
})
INK, MUTE, HARM, HELP = "#1a1a1a", "#8a8a8a", "#B23A48", "#2E6E8E"

def save(fig, name):
    for ext in ("png", "pdf"):
        fig.savefig(f"{OUT}/{name}.{ext}", facecolor="white")
    plt.close(fig)
    print("wrote", name)

# ---------------------------------------------------------------- Figure 1
# The dissociation: relative position effect vs relative angle effect, per intervention.
# Read from the artefact, never retyped. These nine rows were hardcoded until a watchdog audit
# found they still carried an abandoned denominator convention: the interaction family was
# recomputed to divide by the baseline arm rather than the treated arm, the published figure was
# not, and every value in it was an exact match to the superseded numbers.
_IF = "D:/BioCV/BIOCV_INTERACTION_FDR.txt"
_ROW = re.compile(r"^(.+?)\s{2,}([+-]\d+\.\d+)\s+([+-]\d+\.\d+)\s+([+-]\d+\.\d+)\s+"
                  r"(\d\.\d+)\s+(\d\.\d+)\s+\S")
_SHOW = {
    "LOO offset correction [knee flex]":            ("LOO offset correction", "thigh–shank", "offset"),
    "no rejection->objd rejection [knee flex]":     ("Object-space rejection", "thigh–shank", "discard"),
    "no rejection->objd rejection [hip flex]":      ("Object-space rejection", "trunk–thigh", "discard"),
    "no rejection->reproj rejection [knee flex]":   ("Reprojection rejection", "thigh–shank", "discard"),
    "criterion at matched k=1 [knee flex]":         ("Criterion, matched k=1", "thigh–shank", "discard"),
    "criterion at matched k=2 [knee flex]":         ("Criterion, matched k=2", "thigh–shank", "discard"),
    "uniform->confidence weighting [frontal knee]": ("Confidence weighting", "frontal-plane" + chr(10) + "thigh–shank", "weight"),
    "uniform->confidence weighting [hip flex]":     ("Confidence weighting", "trunk–thigh", "weight"),
    "uniform->confidence weighting [knee flex]":    ("Confidence weighting", "thigh–shank", "weight"),
}
_MINTER = _re.search(r"Family size m = (\d+)",
                     io.open(_IF, encoding="utf-8").read()).group(1)
_found = {}
for _line in io.open(_IF, encoding="utf-8"):
    _m = _ROW.match(_line.rstrip())
    if _m:
        _lab = " ".join(_m.group(1).split())
        if _lab in _SHOW:
            _n, _j, _grp = _SHOW[_lab]
            # group(5) is the UNADJUSTED p, group(6) the BH q. The figure's footnote promises
            # "q < 0.05 after Benjamini-Hochberg correction", and starring on p made it assert
            # corrected significance for a contrast the text restates as exploratory.
            _found[_lab] = (_n, _j, float(_m.group(2)), float(_m.group(3)),
                            float(_m.group(6)), _grp)
_missing = [k for k in _SHOW if k not in _found]
if _missing:
    raise SystemExit("Figure 1: not found in " + _IF + ": " + "; ".join(_missing))
rows = [_found[k] for k in _SHOW]

fig, (ax, bx) = plt.subplots(1, 2, figsize=(7.6, 3.6),
                             gridspec_kw={"width_ratios": [2.35, 1], "wspace": 0.62})

def dumbbell(a, items, xlim, title, show_ylab):
    y = np.arange(len(items))[::-1]
    a.axvline(0, color=INK, lw=0.8, zorder=2)
    for yi, (lab, ang, dp, da, p, kind) in zip(y, items):
        c = HARM if da < 0 else HELP
        a.plot([dp, da], [yi, yi], color=c, lw=1.4, alpha=0.55,
               solid_capstyle="round", zorder=3)
        # position marker: always grey ring, never filled -> "open" never means n.s. here
        a.scatter(dp, yi, s=40, marker="o", facecolor="white",
                  edgecolor="#666666", linewidth=1.3, zorder=5)
        # angle marker: always filled; shape encodes intervention class
        a.scatter(da, yi, s=46, marker="D" if kind == "offset" else
                  ("s" if kind == "weight" else "o"),
                  facecolor=c, edgecolor=c, linewidth=1.2, zorder=6)
        # Section 2.5 withholds the q on every leave-one-out row and Table 2(c) prints those
        # rows as withheld. Starring them here asserted, on the most prominent number in the
        # figure, the corrected verdict the paper spends two paragraphs refusing to issue.
        star = '‡' if kind == "offset" else ("*" if p < .05 else "")
        # interaction as defined in the paper: position effect MINUS angle effect
        a.text(xlim[1] * 0.99, yi, f"{dp - da:+.1f}{star}", fontsize=6.3,
               color=c, ha="right", va="center")
    a.set_yticks(y)
    a.set_yticklabels([f"{l}\n{ang}" for l, ang, *_ in items], fontsize=6.5,
                      linespacing=1.35)
    a.set_xlim(*xlim); a.set_ylim(-0.7, len(items) - 0.3)
    a.set_title(title, fontsize=7.8, loc="left", pad=6, color=INK)
    a.tick_params(axis="y", length=0)
    return a

dumbbell(ax, rows[1:], (-9.5, 12.6), "(a)  Triangulation interventions", True)
dumbbell(bx, rows[:1], (-26, 88), "(b)  Joint-centre offset correction", False)
bx.yaxis.tick_right()          # keep (b)'s label out of (a)'s interaction column
bx.tick_params(axis="y", length=0, pad=2)
ax.set_xticks([-8, -6, -4, -2, 0, 2, 4, 6, 8])
bx.set_xticks([-25, 0, 25, 50])
for a in (ax, bx):
    a.set_xlabel("improvement, % of baseline", fontsize=7)
    a.spines["bottom"].set_bounds(a.get_xticks()[0], a.get_xticks()[-1])
ax.axvspan(-9.5, 0, color="#B23A48", alpha=0.045, zorder=0)
bx.axvspan(-26, 0, color="#B23A48", alpha=0.045, zorder=0)
ax.text(-9.2, -0.5, "angle worse", fontsize=6.2, color=HARM, style="italic")
leg = [Line2D([], [], marker="o", ls="", mfc="white", mec="#666666", ms=5,
              label="3D position (hip/knee/ankle)"),
       Line2D([], [], marker="o", ls="", mfc=HARM, mec=HARM, ms=5,
              label="angle · discarding"),
       Line2D([], [], marker="s", ls="", mfc=HELP, mec=HELP, ms=5,
              label="angle · reweighting"),
       Line2D([], [], marker="D", ls="", mfc=HARM, mec=HARM, ms=5,
              label="angle · offset correction")]
fig.legend(handles=leg, fontsize=6.5, frameon=False, ncol=4,
           loc="lower left", bbox_to_anchor=(0.055, -0.10),
           handletextpad=0.35, columnspacing=1.5)
fig.text(0.055, -0.20,
         "Grey ring = 3D position; filled marker = joint angle, shaded red where the angle worsens. "
         "The line is the gap between them.\nRight-hand number is the interaction (position effect "
         "− angle effect, percentage points); * = q < 0.05 after Benjamini–Hochberg\ncorrection within "
         "the interaction family of " + _MINTER + "; ‡ = no q, the leave-one-out rows being"
         " non-exchangeable (Section 2.5). Where only one marker is visible the two coincide.",
         fontsize=6.2, color=MUTE, linespacing=1.5)
fig.suptitle("Position and angle move apart, and a pooled position summary hides it",
             fontsize=8.8, x=0.055, ha="left", y=1.03, color=INK)
save(fig, "fig1_dissociation")

# ---------------------------------------------------------------- Figure 2
# The per-joint decomposition: the null is two significant effects cancelling.
# Read from the artefacts. These twelve p-values were hardcoded, and were the UNADJUSTED p,
# so when the per-joint family was declared and BH-corrected the figure kept marking the
# adaptive ankle effect as significant (p = 0.035) after the paper had restated it as
# exploratory (q = 0.053). Significance in this figure is now q < 0.05, as in the text.
_PJ = "D:/BioCV/BIOCV_PERJOINT_FDR.txt"
_R5 = "D:/BioCV/BIOCV_PERJOINT_GN.txt"
_PJROW = re.compile(r"^(.{10,44}?)\s{2,}(hip|knee|ankle)\s+\d+\.\d+\s+([+-]\d+\.\d+)\s+"
                    r"[+-]\d+\.\d+\s+(\d\.\d+)\s+(\d\.\d+)")
_MEANROW = re.compile(r"^(.{10,44}?)\s{2,}posl\s+\d+\.\d+\s+([+-]\d+\.\d+)\s+"
                      r"[+-]\d+\.\d+\s+(\d\.\d+)")

_eff, _q = {}, {}
for _line in io.open(_PJ, encoding="utf-8"):
    _m = _PJROW.match(_line.rstrip())
    if _m:
        _lab = " ".join(_m.group(1).split())
        _eff[(_lab, _m.group(2))] = float(_m.group(3))
        _q[(_lab, _m.group(2))] = float(_m.group(5))
for _line in io.open(_R5, encoding="utf-8"):
    _m = _MEANROW.match(_line.rstrip())
    if _m:
        _lab = " ".join(_m.group(1).split())
        _eff[(_lab, "mean")] = float(_m.group(2))
        _q[(_lab, "mean")] = float(_m.group(3))   # unadjusted; the pooled rows sit in the m=50 family

_PANELS = [
    ("criterion at matched k=2", "Criterion,\nmatched $k$=2"),
    ("adaptive criterion", "Criterion,\nadaptive"),
    ("uniform -> confidence", "Confidence\nweighting"),
]
pj = {}
for _key, _disp in _PANELS:
    _cells = [(_eff.get((_key, j)), _q.get((_key, j))) for j in ("hip", "knee", "ankle", "mean")]
    if any(c[0] is None for c in _cells):
        raise SystemExit("Figure 2: missing rows for " + _key + " in " + _PJ + " / " + _R5)
    pj[_disp] = ([c[0] for c in _cells], [c[1] for c in _cells])

fig, axes = plt.subplots(1, 3, figsize=(7.2, 3.0), sharey=True)
names = ["hip", "knee", "ankle", "mean"]
for ax, (title, (vals, ps)) in zip(axes, pj.items()):
    x = np.arange(4)
    for i, (v, p) in enumerate(zip(vals, ps)):
        sig = p < 0.05
        c = HELP if v > 0 else HARM
        if i == 3:
            c = INK
        ax.bar(i, v, width=0.62, color=c if sig else "white",
               edgecolor=c, linewidth=1.1, zorder=3,
               hatch="" if sig else "")
        ax.text(i, v + (0.06 if v >= 0 else -0.06), f"{v:+.2f}",
                ha="center", va="bottom" if v >= 0 else "top",
                fontsize=6.3, color=INK)
        if not sig:
            ax.text(i, v + (0.22 if v >= 0 else -0.26), "n.s.", ha="center",
                    va="bottom" if v >= 0 else "top", fontsize=5.8,
                    color=MUTE, style="italic")
    ax.axhline(0, color=INK, lw=0.8, zorder=4)
    ax.axvline(2.5, color=MUTE, lw=0.7, ls=(0, (2, 2)), zorder=1)
    ax.set_xticks(x); ax.set_xticklabels(names, fontsize=7)
    ax.set_title(title, fontsize=7.6, pad=6, color=INK, linespacing=1.2)
    ax.set_ylim(-0.95, 1.85)
axes[0].set_ylabel("3D position improvement (mm)\npositive = object-space / confidence better",
                   fontsize=7, linespacing=1.3)
fig.suptitle("A null in the three-joint mean can be two significant effects of opposite sign",
             fontsize=8.6, x=0.012, ha="left", y=1.035, color=INK)
save(fig, "fig2_perjoint")

# ---------------------------------------------------------------- Figure 3
# Dose-response and the distortion confound, side by side.
fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.2, 2.9))
# (a) dose-response, BIOCV_MATCHED_K.txt
k = np.array([0, 1, 2, 3])
re = np.array([2.570, 2.880, 3.090, 3.358])
ob = np.array([2.570, 2.966, 3.217, 3.412])
a1.plot(k, re, "-o", color=INK, lw=1.3, ms=4.5, label="reprojection criterion")
a1.plot(k, ob, "--s", color=HARM, lw=1.3, ms=4.2, mfc="white", label="object-space criterion")
a1.set_xticks(k)
a1.set_xlabel("cameras discarded per joint ($k$)")
a1.set_ylabel("thigh–shank angle error (°)")
a1.set_title("(a)  Discarding costs 0.24–0.38°/camera",
              fontsize=7.8, loc="left", pad=6)
a1.legend(fontsize=6.4, frameon=False, loc="upper left")
a1.annotate("", xy=(3, 3.358), xytext=(3, 2.570),
            arrowprops=dict(arrowstyle="<->", color=MUTE, lw=0.8))
a1.text(2.9, 2.96, "+0.79°", fontsize=6.5, color=MUTE, ha="right", rotation=90, va="center")
# (b) distortion, BIOCV_UNDISTORT.txt
bins = ["1.5–2", "2–2.5", "2.5–3", "3–4"]
unc = [-0.13, -0.13, 1.35, 4.62]
cor = [0.16, 0.47, 0.67, 0.68]
usig = [False, False, True, True]
csig = [True, True, True, False]
xx = np.arange(4)
a2.bar(xx - 0.19, unc, 0.36, color=[HARM if s else "white" for s in usig],
       edgecolor=HARM, lw=1.0, label="uncorrected", zorder=3)
a2.bar(xx + 0.19, cor, 0.36, color=[INK if s else "white" for s in csig],
       edgecolor=INK, lw=1.0, label="distortion-corrected", zorder=3)
a2.axhline(0, color=INK, lw=0.8)
a2.set_xticks(xx); a2.set_xticklabels(bins)
a2.set_xlabel("camera-distance asymmetry (max/min)")
a2.set_ylabel("object-space advantage (mm)")
a2.set_title("(b)  Before and after distortion correction",
             fontsize=7.8, loc="left", pad=6)
a2.legend(fontsize=6.4, frameon=False, loc="upper left")
a2.text(3, 4.62 + 0.25, "+4.62*", ha="center", fontsize=6.5, color=HARM)
a2.text(3.19, 0.68 + 0.25, "+0.68 n.s.", ha="center", fontsize=6.2, color=INK)
save(fig, "fig3_dose_distortion")

# ---------------------------------------------------------------- Figure 4
# Magnitude bounds: what the nulls actually rule out. Forest plot.
# Source: BIOCV_EQUIV.txt Part 1, BIOCV_PERJOINT_GN.txt Part 4.
eq = [
    ("thigh–shank: criterion",            0.047, -0.007,  0.100),
    ("frontal-plane thigh–shank: criterion",           -0.054, -0.099, -0.008),
    ("trunk–thigh: criterion",             0.025, -0.042,  0.090),
    ("thigh–shank: uniform vs confidence", 0.023, -0.050,  0.095),
    ("thigh–shank: matched $k$=3 criterion", -0.051, -0.145, 0.045),
    ("thigh–shank: 1/d weighting",         0.052, -0.048,  0.159),
]
fig, ax = plt.subplots(figsize=(5.6, 2.9))
y = np.arange(len(eq))[::-1]
for yi, (lab, e, lo, hi) in zip(y, eq):
    excl = not (lo <= 0 <= hi)
    c = HARM if excl else INK
    ax.plot([lo, hi], [yi, yi], color=c, lw=1.5, solid_capstyle="round", zorder=3)
    ax.plot([lo, lo], [yi - .13, yi + .13], color=c, lw=1.1)
    ax.plot([hi, hi], [yi - .13, yi + .13], color=c, lw=1.1)
    ax.scatter(e, yi, s=26, color=c, zorder=4)
ax.axvline(0, color=MUTE, lw=0.8, zorder=1)
for m, ls in ((2.0, (0, (5, 3))),):
    ax.axvspan(-0.10, 0.10, color="#2E6E8E", alpha=0.05, zorder=0)
ax.text(0.105, 5.42, "2% of a 5° MDC", fontsize=6.3, color=HELP, va="center")
ax.set_yticks(y); ax.set_yticklabels([e[0] for e in eq], fontsize=7)
ax.set_xlim(-0.22, 0.30)
ax.set_xlabel("effect on joint angle (°), exact 90% confidence interval")
ax.set_title("What the nulls rule out: the three criterion effects are bounded below 0.10°",
             fontsize=8.4, loc="left", pad=8, color=INK)
ax.text(0.29, 4.0, "interval excludes 0:\ndetected, but bounded", fontsize=6.2,
        color=HARM, ha="right", va="center", style="italic", linespacing=1.3)
save(fig, "fig4_bounds")

# ---------------------------------------------------------------- Figure 5
# The offset is posture-dependent. Source: BIOCV_POSTURE.txt
fig, ax = plt.subplots(figsize=(5.2, 3.0))
xb = np.arange(5)
lbls = ["104–133", "133–159", "159–168", "168–173", "173–180"]
# The q-values come from the corrected posture family, not from the hardcoded unadjusted p this
# figure used to print while the text quoted q. The quintile series stay literal -- they are the
# plotted curve, and BIOCV_POSTURE.txt prints them per joint in a layout this figure reshapes.
_PQ = {}
for _line in io.open("D:/BioCV/BIOCV_POSTURE_FDR.txt", encoding="utf-8"):
    _m = _re.match(r"^\s*(hip|knee|ankle)\s+\|off\|\s+([+-]\d+\.\d+)\s+\d\.\d+\s+(\d\.\d+)", _line.rstrip())
    if _m:
        _PQ[_m.group(1)] = (_m.group(2).replace("-", "−"), float(_m.group(3)))
if set(_PQ) != {"hip", "knee", "ankle"}:
    raise SystemExit("Figure 4: could not read the three |off| rows from BIOCV_POSTURE_FDR.txt")
# Table 3(c) and this figure's caption dagger the knee row, which survives Benjamini-Hochberg but
# not the arbitrary-dependence sensitivity. The figure printed a bare q, showing a verdict firmer
# than the tables do. The mark is read from the sensitivity artefact rather than hardcoded.
_BY = set()
_BYPAT = _re.compile(r"^\s+posture\s+(hip|knee|ankle) \|off\|\s*$")
for _line in io.open("D:/BioCV/BIOCV_BY_SENSITIVITY.txt", encoding="utf-8"):
    _b = _BYPAT.match(_line.rstrip())
    if _b:
        _BY.add(_b.group(1))
if not _BY:
    raise SystemExit("Figure 4: no posture |off| rows in BIOCV_BY_SENSITIVITY.txt")
series = [("hip",   [36.4, 38.6, 38.7, 42.9, 43.0], _PQ["hip"][0],   _PQ["hip"][1],   HELP),
          ("knee",  [32.2, 32.3, 29.1, 28.1, 28.5], _PQ["knee"][0],  _PQ["knee"][1],  HARM),
          ("ankle", [19.1, 16.3, 13.6, 14.0, 14.6], _PQ["ankle"][0], _PQ["ankle"][1], INK)]
for name, v, d, p, c in series:
    ax.plot(xb, v, "-o", color=c, lw=1.4, ms=4.2)
    _dag = "†" if name in _BY else ""
    ax.text(4.12, v[-1], f"  {name}\n  {d} mm, $q$={p:.3f}{_dag}", fontsize=6.4,
            color=c, va="center", linespacing=1.3)
ax.set_xticks(xb); ax.set_xticklabels(lbls, fontsize=6.8)
ax.set_xlim(-0.3, 6.1)
ax.set_xlabel("reference thigh–shank angle (°), quintiles\n180° = full extension, so flexion increases leftward",
              fontsize=7, linespacing=1.5)
ax.annotate("", xy=(0.05, 11.6), xytext=(2.6, 11.6),
            arrowprops=dict(arrowstyle="-|>", color=MUTE, lw=0.9))
ax.text(1.32, 12.1, "more flexed", fontsize=6.3, color=MUTE, ha="center", style="italic")
ax.set_ylabel("‖joint-centre offset‖ (mm)")
ax.set_title("The joint-centre offset is not fixed — it swings with posture",
             fontsize=8.4, loc="left", pad=8, color=INK)
ax.text(-0.25, 46.5, "a static correction table subtracts a constant from this",
        fontsize=6.5, color=MUTE, style="italic")
ax.set_ylim(10, 48)
save(fig, "fig5_posture")

print("\nAll figures written to", OUT)
