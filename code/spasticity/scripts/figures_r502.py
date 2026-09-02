# -*- coding: utf-8 -*-
"""r502: the manuscript's figures, rebuilt to the specifications a referee set.

Changes from r455, each because a figure was carrying less than the claim it illustrated:
  Fig 1  inset over the first 15% of the cycle, where the contact-instant difference lives; the
         seed bands were previously legible as inter-subject variability, which they are not.
  Fig 2  the 0.586 deg artefact floor drawn as a band, and seed dispersion added -- one plotted bar
         (+0.063 deg) is an order of magnitude below that floor and was drawn as though real.
  Fig 3  unchanged in content; the arms' unequal seed dispersion is now visible and captioned.
  Fig 4  replaced. The dose ladder had six points, no error bars and a distorted axis; the mixed
         grid and the cancellation it shows are the finding with the most direct clinical bearing.
  Fig 5  cell-level, not family means. The claim it exists to support is that every hyperreflexia
         cell is more flexed than every weakness cell, which family means cannot show. Both panels
         share a seed-SD-normalised scale so the visual gap is not an artefact of axis choice.

Reads archived .sto and the deposited caches only -- no simulator licence needed.
"""
import glob
import io
import json
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sto_utils as S

RES = r"C:\Users\maurice\Documents\SCONE\results"
PAP = r"C:\Users\maurice\Desktop\spasticity_paper\paper"
OUT = os.path.join(PAP, "figures")
if not os.path.isdir(OUT):
    os.makedirs(OUT)
SETTLE, T1 = 1.0, 9.73
SHAM = 0.5860145801831838
CTRL, WEAK, HYPER = "#4477AA", "#228833", "#CC3311"
plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False})


def load_cache():
    p = os.path.join(PAP, "CELL_CACHE_r501.json")
    if not os.path.exists(p):
        sys.exit("CELL_CACHE_r501.json missing -- run cellcache_r501.py first")
    return json.load(io.open(p, encoding="utf-8"))


# ------------------------------------------------------------------ Fig 1: traces with an inset
def traces(prefix):
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
    x = np.linspace(0, 100, 101)
    K = [np.interp(x, np.linspace(0, 100, b - a), kn[a:b]) for a, b in win]
    A = [np.interp(x, np.linspace(0, 100, b - a), an[a:b]) for a, b in win]
    return np.mean(K, 0), np.mean(A, 0)


def fig1():
    """Three panels rather than an inset: the knee's swing excursion reaches -65 deg, so any inset
    large enough to read occludes the phase the paper is about. Panel B is the same knee data over
    the first 15% of the cycle, where the contact-instant difference lives."""
    x = np.linspace(0, 100, 101)
    arms = [("control", "R151C", CTRL), ("dorsiflexor weakness", "R151W", WEAK),
            ("plantarflexor hyperreflexia", "R151S", HYPER)]
    data = {}
    for lab, fam, col in arms:
        K, A = [], []
        for sd in range(101, 107):
            r = traces("%s_s%d" % (fam, sd))
            if r:
                K.append(r[0]); A.append(r[1])
        if K:
            data[lab] = (np.array(K), np.array(A), col)
    fig, axes = plt.subplots(1, 3, figsize=(12.6, 4.0))
    panels = [(axes[0], "knee", 0, None), (axes[1], "knee", 0, 15), (axes[2], "ankle", 1, None)]
    for ax, name, unit, xmax in panels:
        for lab, (K, A, col) in data.items():
            Y = K if unit == 0 else A
            m, sd = Y.mean(0), Y.std(0, ddof=1)
            n = 16 if xmax else 101
            ax.plot(x[:n], m[:n], color=col, lw=1.7, label=lab)
            ax.fill_between(x[:n], (m - sd)[:n], (m + sd)[:n], color=col, alpha=0.20, lw=0)
        ax.axvline(0, color="0.4", lw=0.8, ls=":")
        ax.set_xlabel("gait cycle (%)")
        if xmax:
            ax.set_xlim(0, xmax)
            ax.set_title("B  knee, first 15% of the cycle", fontsize=9, loc="left")
            ax.set_ylabel("knee angle (deg)")
        elif unit == 0:
            ax.set_title("A  knee, whole cycle", fontsize=9, loc="left")
            ax.set_ylabel("knee angle (deg)")
            ax.legend(frameon=False, fontsize=8, loc="lower left")
        else:
            ax.set_title("C  ankle, whole cycle", fontsize=9, loc="left")
            ax.set_ylabel("ankle angle (deg)")
    fig.suptitle("Optimisation round 151: one control, one weakness and one hyperreflexia lineage."
                 "   Knee flexion negative; ankle dorsiflexion positive.", fontsize=9, y=0.99)
    fig.tight_layout(rect=[0, 0, 1, 0.94])
    fig.savefig(os.path.join(OUT, "fig1_traces.png"), dpi=200)
    plt.close(fig)
    print("fig1 ok  (three panels, no inset)")


# ------------------------------------------------- Fig 2: sub-phases against the artefact floor
def fig2():
    """Sub-phase displacement from control, with within-cell seed SD and the artefact floor.

    One bar in the r455 version (+0.063 deg at terminal stance) is an order of magnitude below the
    floor and was drawn as though it were a measurement.
    """
    sp = json.load(io.open(os.path.join(PAP, "SUBPHASE_r441.json"), encoding="utf-8"))["windows"]
    order = [("initial_contact", "initial\ncontact"), ("loading_response", "loading\nresponse"),
             ("midstance", "midstance"), ("terminal_stance", "terminal\nstance"),
             ("pre_swing", "pre-swing")]
    W, H, E = [], [], []
    for k, _ in order:
        w = sp[k]
        W.append(w["displacement_from_control"]["weakness"])
        H.append(w["displacement_from_control"]["spastic"])
        E.append(w["within_cell_seed_SD_deg"])
    i = np.arange(len(order)); wd = 0.36
    fig, ax = plt.subplots(figsize=(7.4, 4.0))
    ax.axhspan(-SHAM, SHAM, color="0.75", alpha=0.55, lw=0, zorder=0,
               label="largest measured protocol artefact (±0.586°)")
    ax.bar(i - wd / 2, W, wd, yerr=E, color=WEAK, capsize=3, zorder=3,
           error_kw={"lw": 1, "ecolor": "0.25"}, label="dorsiflexor weakness − control")
    ax.bar(i + wd / 2, H, wd, yerr=E, color=HYPER, capsize=3, zorder=3,
           error_kw={"lw": 1, "ecolor": "0.25"}, label="plantarflexor hyperreflexia − control")
    ax.axhline(0, color="0.3", lw=0.8, zorder=2)
    ax.set_xticks(i); ax.set_xticklabels([lab for _, lab in order], fontsize=8)
    ax.set_ylabel("knee displacement from control (deg)")
    ax.legend(frameon=False, fontsize=8, loc="lower right")
    ax.set_title("Opposite signs at contact and loading response, same sign thereafter.\n"
                 "Error bars are the within-cell seed SD of that window.", fontsize=9)
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "fig3_subphase.png"), dpi=200); plt.close(fig)
    print("fig2 ok  (values read from SUBPHASE_r441, seed SD as error bars)")


# ------------------------------------------------------------- Fig 3: within round 151, per cell
def fig3(cache):
    fig, ax = plt.subplots(figsize=(5.6, 4.0))
    for j, (fam, lab, col) in enumerate([("R151C", "control", CTRL),
                                         ("R151W", "weakness \u00d70.80", WEAK),
                                         ("R151S", "hyperreflexia KV 0.100", HYPER)]):
        v = [c["knee_ic_deg"] for c in cache[fam]["cells"]]
        ax.scatter([j] * len(v), v, s=34, color=col, zorder=3)
        ax.plot([j - 0.22, j + 0.22], [np.mean(v)] * 2, color=col, lw=2.2, zorder=4)
        ax.text(j, max(v) + 0.45, "SD %.2f\u00b0" % np.std(v, ddof=1), ha="center", fontsize=7.5,
                color="0.35")
    ax.set_xticks([0, 1, 2])
    ax.set_xticklabels(["control", "weakness\n\u00d70.80", "hyperreflexia\nKV 0.100"], fontsize=8)
    ax.set_ylabel("knee angle at foot contact (deg)")
    ax.set_title("One optimisation round, one control lineage, six seeds each", fontsize=9)
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "fig4_withinround.png"), dpi=200)
    plt.close(fig); print("fig3 ok")


# ------------------------------------------------------- Fig 4: the mixed grid and cancellation
def fig4():
    m = json.load(io.open(os.path.join(PAP, "MIXED_RESULT_r424.json"), encoding="utf-8"))
    grid = m.get("grid", {})
    pts = []
    for k, v in grid.items():
        if not isinstance(v, dict) or "KNEE_ic" not in v:
            continue
        pts.append((v.get("weak", 1.0), v.get("KV", 0.0) * 2.0,   # delivered = 2 x archived label
                    v["KNEE_ic"]["mean"], v.get("t_end", {}).get("mean", np.nan)))
    if not pts:
        print("fig4 skipped: no grid"); return
    fig, ax = plt.subplots(figsize=(6.4, 4.2))
    # x0.60 has no cell reaching the four-seed bar, and the right-hand gain column was added
    # after the registration was hashed; both are drawn so the eye does not read them as registered
    POSTHOC_GAIN = 0.220
    for wk in sorted(set(p[0] for p in pts)):
        row = sorted([p for p in pts if p[0] == wk], key=lambda z: z[1])
        thin = abs(wk - 0.60) < 1e-9            # below the four-seed bar
        subs = abs(wk - 0.70) < 1e-9            # post-hoc substitute for the x0.60 root
        ax.plot([r[1] for r in row], [r[2] for r in row],
                "o--" if (thin or subs) else "o-",
                lw=1.6, ms=6, mfc="none" if thin else None, alpha=0.55 if thin else 1.0,
                label=("weakness ×0.60 (below the four-seed bar)" if thin else
                       "weakness ×0.70 (post-hoc substitute)" if subs else
                       "weakness ×%.2f (registered)" % wk))
        for r in row:
            if abs(r[1] - POSTHOC_GAIN) < 1e-9:
                ax.annotate("post hoc", (r[1], r[2]), textcoords="offset points",
                            xytext=(4, 4), fontsize=6.5, color="0.35")
            if not np.isnan(r[3]) and r[3] >= 19.999:
                ax.scatter([r[1]], [r[2]], s=150, facecolors="none", edgecolors="0.25",
                           lw=1.2, zorder=5)
    ax.set_xlabel("delivered reflex gain KV")
    ax.set_ylabel("knee angle at foot contact (deg)")
    ax.legend(frameon=False, fontsize=8)
    ax.set_title("Ringed cells survive the full 20 s. The weakness rows lie within 0.52° of\n"
                 "one another at the two lowest gains and separate from KV 0.100 upward.\n"
                 "Dashed rows and the right-hand column are not registered.",
                 fontsize=9)
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "fig5_mixedgrid.png"), dpi=200)
    plt.close(fig); print("fig4 ok")


# ---------------------------------------- Fig 5: both joints, CELL level, shared normalised scale
def fig5(cache):
    HY = ["R151S", "R393SPg070", "R393SPg100", "R396SPg110", "R396SPg120"]
    WK = ["R151W", "R174W870", "R174W892", "R169W090", "R174W915", "R169W095"]
    sd_k = np.mean([cache[f]["knee_sd"] for f in HY + WK if cache[f]["knee_sd"]])
    sd_a = np.mean([cache[f]["ankle_sd"] for f in HY + WK if cache[f]["ankle_sd"]])
    fig, axes = plt.subplots(1, 2, figsize=(9.6, 4.3))
    for ax, key, sd, name in [(axes[0], "knee_ic_deg", sd_k, "knee"),
                              (axes[1], "ankle_ic_deg", sd_a, "ankle")]:
        cm = cache["R151C"][("knee_mean" if name == "knee" else "ankle_mean")]
        wall = [c[key] for f in WK for c in cache[f]["cells"]]
        ax.axhspan((min(wall) - cm) / sd, (max(wall) - cm) / sd, color=WEAK, alpha=0.14, lw=0,
                   label="range of all weakness cells")
        for j, f in enumerate(HY):
            v = [(c[key] - cm) / sd for c in cache[f]["cells"]]
            ax.scatter([cache[f]["kv_delivered"]] * len(v), v, s=26, color=HYPER, zorder=3)
        ax.plot([cache[f]["kv_delivered"] for f in HY],
                [(cache[f][("knee_mean" if name == "knee" else "ankle_mean")] - cm) / sd for f in HY],
                color=HYPER, lw=1.5, zorder=4, label="hyperreflexia family means")
        for f in WK:
            v = [(c[key] - cm) / sd for c in cache[f]["cells"]]
            ax.scatter([0.086] * len(v), v, s=18, color=WEAK, zorder=3)
        ax.axhline(0, color=CTRL, lw=1.2, ls="--", label="control")
        ax.set_xlabel("delivered reflex gain KV      (weakness cells at left)")
        ax.set_ylabel("displacement from control (within-cell seed SD)")
        ax.set_title("%s at foot contact" % name, fontsize=9)
        if name == "knee":
            ax.legend(frameon=False, fontsize=7.5, loc="lower left")
    lo = min(a.get_ylim()[0] for a in axes); hi = max(a.get_ylim()[1] for a in axes)
    for a in axes:
        a.set_ylim(lo, hi)
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "fig2_cells_both_joints.png"), dpi=200)
    plt.close(fig); print("fig5 ok  (shared scale, knee SD %.3f  ankle SD %.3f)" % (sd_k, sd_a))


if __name__ == "__main__":
    cache = load_cache()
    fig2(); fig3(cache); fig4(); fig5(cache); fig1()
