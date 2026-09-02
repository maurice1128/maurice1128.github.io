# -*- coding: utf-8 -*-
"""r455: the manuscript's figures. Reads archived .sto only -- no simulation, no licence needed.

Fig 1  knee and ankle angle over the normalised gait cycle, three arms, seed bands, contact marked.
Fig 2  the sub-phase sign reversal (knee displacement from control, five stance windows).
Fig 3  within-round-151 replication: per-cell knee at contact, three arms.
Fig 4  spastic dose ladder, survival-matched cells highlighted.
"""
import glob
import io
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sto_utils as S

RES = r"C:\Users\maurice\Documents\SCONE\results"
OUT = r"C:\Users\maurice\Desktop\spasticity_paper\paper\figures"
if not os.path.isdir(OUT):
    os.makedirs(OUT)
SETTLE, T1 = 1.0, 9.73
SEEDS = range(101, 107)
ARMS = [("control", "R151C", "#4477AA"), ("dorsiflexor weakness", "R151W", "#228833"),
        ("plantarflexor hyperreflexia", "R151S", "#CC3311")]


def cycles(prefix):
    """return list of (t, knee, ankle, on) resampled to 101 points per admissible cycle"""
    g = [d for d in glob.glob(os.path.join(RES, prefix + ".*")) if os.path.isdir(d)]
    if not g:
        return None
    g = [max(g, key=lambda d: len(glob.glob(os.path.join(d, "[0-9]*.par"))))]
    st = sorted(glob.glob(os.path.join(g[0], "*.par.sto")))
    if not st:
        return None
    cols, dat = S.load_sto(st[-1])
    if dat.size == 0:
        return None
    t = dat[:, 0]
    grf, thr = S.grf_vertical(cols, dat, "l")
    hs = S.heel_strikes(t, grf, thresh=thr)
    allc = [(hs[k], hs[k + 1]) for k in range(len(hs) - 1) if t[hs[k]] >= SETTLE]
    win = [c for c in allc if t[c[1]] <= T1]
    win = win[:-1] if len(win) >= 2 else win
    if float(t[-1]) < T1 or len(win) < 5:
        return None
    kn = np.degrees(S.col(cols, dat, "knee_angle_l"))
    an = np.degrees(S.col(cols, dat, "ankle_angle_l"))
    on = grf > thr
    K, A, ST = [], [], []
    x = np.linspace(0, 100, 101)
    for a, b in win:
        p = np.linspace(0, 100, b - a)
        K.append(np.interp(x, p, kn[a:b]))
        A.append(np.interp(x, p, an[a:b]))
        ST.append(np.interp(x, p, on[a:b].astype(float)))
    return np.array(K), np.array(A), np.array(ST)


def arm_traces(fam):
    K, A, ST = [], [], []
    for s in SEEDS:
        c = cycles("%s_s%d" % (fam, s))
        if c:
            K.append(c[0].mean(0)); A.append(c[1].mean(0)); ST.append(c[2].mean(0))
    return (np.array(K), np.array(A), np.array(ST)) if K else None


# ------------------------------------------------------------------ Fig 1
print("building figure 1 ...")
fig, ax = plt.subplots(1, 2, figsize=(11, 4.2))
toe = []
for label, fam, col in ARMS:
    r = arm_traces(fam)
    if r is None:
        print("   missing", fam); continue
    K, A, ST = r
    x = np.linspace(0, 100, 101)
    for j, (Y, a) in enumerate([(K, ax[0]), (A, ax[1])]):
        m, sd = Y.mean(0), Y.std(0, ddof=1)
        a.plot(x, m, color=col, lw=2, label="%s (n=%d seeds)" % (label, len(Y)), zorder=3)
        a.fill_between(x, m - sd, m + sd, color=col, alpha=0.18, lw=0, zorder=2)
    toe.append(np.interp(0.5, ST.mean(0)[::-1], x[::-1]))
for a, ttl, yl in [(ax[0], "Knee", "knee angle (deg, flexion negative)"),
                   (ax[1], "Ankle", "ankle angle (deg)")]:
    a.axvline(0, color="k", lw=1.2, ls="-", zorder=1)
    a.annotate("foot contact", xy=(0, a.get_ylim()[1]), xytext=(3, -12),
               textcoords="offset points", fontsize=8, va="top")
    if toe:
        a.axvline(np.mean(toe), color="0.5", lw=1, ls="--", zorder=1)
    a.set_xlabel("gait cycle (%)"); a.set_ylabel(yl); a.set_title(ttl)
    a.spines[["top", "right"]].set_visible(False)
ax[0].legend(frameon=False, fontsize=8, loc="lower right")
fig.suptitle("Fig 1  Sagittal knee and ankle over the gait cycle, round 151. "
             "Bands are ±1 SD across six optimisation seeds.", fontsize=9, y=1.0)
fig.tight_layout(); fig.savefig(os.path.join(OUT, "fig1_traces.png"), dpi=200,
                                bbox_inches="tight"); plt.close(fig)

# ------------------------------------------------------------------ Fig 2
print("building figure 2 ...")
import json
sp = json.load(io.open(r"C:\Users\maurice\Desktop\spasticity_paper\paper\SUBPHASE_r441.json",
                       encoding="utf-8"))["windows"]
names = ["initial_contact", "loading_response", "midstance", "terminal_stance", "pre_swing"]
lab = ["initial\ncontact", "loading\nresponse", "midstance", "terminal\nstance", "pre-swing"]
wk = [sp[n]["displacement_from_control"]["weakness"] for n in names]
sps = [sp[n]["displacement_from_control"]["spastic"] for n in names]
fig, a = plt.subplots(figsize=(7, 4))
i = np.arange(5); w = 0.38
a.bar(i - w/2, wk, w, color="#228833", label="dorsiflexor weakness")
a.bar(i + w/2, sps, w, color="#CC3311", label="plantarflexor hyperreflexia")
a.axhline(0, color="k", lw=1)
a.axvspan(-0.5, 1.5, color="0.92", zorder=0)
a.annotate("opposite signs", xy=(0.5, min(sps) * 0.92), ha="center", fontsize=9, style="italic")
a.set_xticks(i); a.set_xticklabels(lab, fontsize=8)
a.set_ylabel("knee displacement from control (deg)")
a.set_title("Fig 2  The sign reversal is confined to contact and loading response", fontsize=10)
a.legend(frameon=False, fontsize=8); a.spines[["top", "right"]].set_visible(False)
fig.tight_layout(); fig.savefig(os.path.join(OUT, "fig2_subphase.png"), dpi=200); plt.close(fig)

# ------------------------------------------------------------------ Fig 3
print("building figure 3 ...")
d = json.load(io.open(r"C:\Users\maurice\Desktop\spasticity_paper\paper"
                      r"\KNEE_MDC_BATCHNULL_r399.json", encoding="utf-8"))["cells"]
fig, a = plt.subplots(figsize=(6, 4))
for k, (label, fam, col) in enumerate(ARMS):
    v = [c["knee_hs_L_deg"] for kk, c in d.items()
         if kk.rsplit("_s", 1)[0] == fam and c.get("gate_G")]
    a.scatter(np.full(len(v), k) + np.linspace(-.06, .06, len(v)), v, s=42, color=col, zorder=3)
    a.hlines(np.mean(v), k - .22, k + .22, color=col, lw=2.5, zorder=4)
a.set_xticks(range(3)); a.set_xticklabels([l for l, _, _ in ARMS], fontsize=8)
a.set_ylabel("knee angle at foot contact (deg)")
a.set_title("Fig 3  Within one optimisation round (151) the two lesions displace\n"
            "the knee in opposite directions; ranges are disjoint (edge gap 2.42 deg)",
            fontsize=9)
a.spines[["top", "right"]].set_visible(False)
fig.tight_layout(); fig.savefig(os.path.join(OUT, "fig3_withinround.png"), dpi=200); plt.close(fig)

# ------------------------------------------------------------------ Fig 4
print("building figure 4 ...")
m = json.load(io.open(r"C:\Users\maurice\Desktop\spasticity_paper\paper\MIXED_RESULT_r424.json",
                      encoding="utf-8"))
reg = m["REGISTRATION_DEVIATIONS_r438"]["REGISTERED_ONLY_P1"]
KV = [0.0125, 0.025, 0.050]
fig, a = plt.subplots(figsize=(6.6, 4))
for row, col, mk in [("W100", "#0077BB", "o"), ("W080", "#EE7733", "s")]:
    y = reg[row]["rung_means"]
    a.plot(KV, y, marker=mk, color=col, lw=2, label="%s weakness" % row.replace("W1", "x1.")
           .replace("W0", "x0."))
    a.scatter(KV[:2], y[:2], s=190, facecolors="none", edgecolors=col, lw=2.2, zorder=5)
a.set_xscale("log"); a.set_xticks(KV); a.set_xticklabels([str(k) for k in KV])
a.xaxis.set_minor_locator(plt.NullLocator()); a.set_xlim(0.011, 0.057)
a.set_xlabel("spastic reflex gain KV (nominal; delivered gain is 2x)")
a.set_ylabel("knee angle at foot contact (deg)")
a.set_title("Fig 4  Spastic dose response, registered rungs only.\n"
            "Circled cells reach the full 20 s horizon — the ladder between them\n"
            "is free of the survival confound.", fontsize=9)
a.legend(frameon=False, fontsize=8); a.spines[["top", "right"]].set_visible(False)
fig.tight_layout(); fig.savefig(os.path.join(OUT, "fig4_dose.png"), dpi=200); plt.close(fig)

print("\nwrote:")
for f in sorted(os.listdir(OUT)):
    print("  paper/figures/%s  (%d kB)" % (f, os.path.getsize(os.path.join(OUT, f)) // 1024))
