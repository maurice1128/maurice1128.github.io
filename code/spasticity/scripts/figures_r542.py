# -*- coding: utf-8 -*-
"""r542: the figure set for the reported endpoint.

The previous figures were built for knee angle at contact. The manuscript now reports peak ankle
dorsiflexion in swing, selected from a scan of 81 candidates, so the figures have to show the ankle
trace, the scan that chose from it, the endpoint cell by cell, the asymmetry that is the paper's
principal result, and what motion-capture error leaves of it.

No simulation is run: everything is read from the archived .sto files and the deposited containers.
"""
import glob, io, json, os, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sto_utils as S

RES = r"C:\Users\maurice\Documents\SCONE\results"
P = r"C:\Users\maurice\Desktop\spasticity_paper\paper"
OUT = os.path.join(P, "figures")
SETTLE, T1 = 1.0, 9.73
CTRL = "R151C"
HY = [("R151S", 0.100), ("R393SPg070", 0.140), ("R393SPg100", 0.200),
      ("R396SPg110", 0.220), ("R396SPg120", 0.240)]
WK = [("R151W", 0.80), ("R174W870", 0.87), ("R174W892", 0.892),
      ("R169W090", 0.90), ("R174W915", 0.915), ("R169W095", 0.95)]
C_CT, C_WK, C_HY = "#444444", "#1f77b4", "#d62728"


def load(fam, sd):
    g = [d for d in glob.glob(os.path.join(RES, "%s_s%d.*" % (fam, sd))) if os.path.isdir(d)]
    if not g:
        return None
    g = [max(g, key=lambda d: len(glob.glob(os.path.join(d, "[0-9]*.par"))))]
    st = sorted(glob.glob(os.path.join(g[0], "*.par.sto")))
    if not st:
        return None
    c, dat = S.load_sto(st[-1])
    if dat.size == 0:
        return None
    t = dat[:, 0]
    grf, thr = S.grf_vertical(c, dat, "l")
    hs = S.heel_strikes(t, grf, thresh=thr)
    allc = [(hs[k], hs[k + 1]) for k in range(len(hs) - 1) if t[hs[k]] >= SETTLE]
    w = [x for x in allc if t[x[1]] <= T1]
    w = w[:-1] if len(w) >= 2 else w
    if float(t[-1]) < T1 or len(w) < 5:
        return None
    on = grf > thr
    an = np.degrees(S.col(c, dat, "ankle_angle_l"))
    cur, pk, tof = [], [], []
    for a, b in w:
        cur.append(np.interp(np.linspace(0, 100, 101), np.linspace(0, 100, b - a), an[a:b]))
        idx = np.where(~on[a:b])[0]
        if idx.size:
            pk.append(float(np.max(an[a:b][idx])))
            tof.append(100.0 * idx[0] / float(b - a))
    return {"curve": np.mean(cur, axis=0), "peak": float(np.mean(pk)) if pk else None,
            "toe_off": float(np.mean(tof)) if tof else None}


print("loading ...")
D = {}
for f in [CTRL] + [x[0] for x in HY + WK]:
    D[f] = [d for d in (load(f, s) for s in range(101, 107)) if d]
    print("   %-12s n=%d" % (f, len(D[f])))
if not os.path.isdir(OUT):
    os.makedirs(OUT)


def band(ax, fams, colour, label):
    cur = np.array([d["curve"] for f in fams for d in D[f]])
    m, sd = cur.mean(axis=0), cur.std(axis=0, ddof=1)
    x = np.arange(101)
    ax.plot(x, m, color=colour, lw=1.8, label=label, zorder=3)
    ax.fill_between(x, m - sd, m + sd, color=colour, alpha=0.18, lw=0, zorder=2)
    return m


# ---- Fig 1: the ankle trace, three arms, with the endpoint marked ------------------------------
fig, ax = plt.subplots(1, 2, figsize=(11, 4.0), gridspec_kw={"width_ratios": [2, 1]})
tof = float(np.mean([d["toe_off"] for f in D for d in D[f] if d["toe_off"]]))
for a in ax:
    a.axhline(0, color="#bbbbbb", lw=0.7, zorder=1)
    a.axvline(tof, color="#999999", lw=0.9, ls=":", zorder=1)
mc = band(ax[0], [CTRL], C_CT, "control")
mw = band(ax[0], [f for f, _ in WK], C_WK, "weakness")
mh = band(ax[0], [f for f, _ in HY], C_HY, "hyperreflexia")
ax[0].annotate("toe-off\n%.0f%%" % tof, xy=(tof, -22), fontsize=8, color="#666666", ha="center")
ax[0].set_xlabel("% of gait cycle"); ax[0].set_ylabel("ankle angle (deg, dorsiflexion +)")
ax[0].set_title("A   ankle, whole cycle", loc="left", fontsize=10)
ax[0].legend(frameon=False, fontsize=9, loc="lower left")
for f, c in ((CTRL, C_CT),):
    pass
band(ax[1], [CTRL], C_CT, None)
band(ax[1], [f for f, _ in WK], C_WK, None)
band(ax[1], [f for f, _ in HY], C_HY, None)
ax[1].set_xlim(62, 100); ax[1].set_ylim(-10, 16)
pk = int(np.argmax(mc[65:])) + 65
ax[1].axvline(pk, color="#666666", lw=0.9, ls="--")
ax[1].annotate("peak in swing\n(reported endpoint)", xy=(pk, 13), fontsize=8, ha="center",
               color="#333333")
ax[1].set_xlabel("% of gait cycle")
ax[1].set_title("B   swing, where the endpoint is taken", loc="left", fontsize=10)
for a in ax:
    a.spines["top"].set_visible(False); a.spines["right"].set_visible(False)
fig.tight_layout(); fig.savefig(os.path.join(OUT, "fig1_ankle_trace.png"), dpi=200)
plt.close(fig); print("fig1 ok")

# ---- Fig 2: the endpoint cell by cell ----------------------------------------------------------
fig, ax = plt.subplots(figsize=(7.2, 4.2))
rows = [(CTRL, None, "control", C_CT)] + [(f, d, "KV %.3f" % d, C_HY) for f, d in HY] + \
       [(f, d, "x%.3f" % d, C_WK) for f, d in WK]
y = 0
ticks, labs = [], []
for f, dose, lab, col in rows:
    v = [d["peak"] for d in D[f] if d["peak"] is not None]
    if not v:
        continue
    ax.scatter(v, [y] * len(v), s=26, color=col, zorder=3, edgecolor="white", linewidth=0.5)
    ax.plot([min(v), max(v)], [y, y], color=col, lw=1.2, alpha=0.5, zorder=2)
    ticks.append(y); labs.append(lab); y -= 1
hv = [d["peak"] for f, _ in HY for d in D[f] if d["peak"] is not None]
wv = [d["peak"] for f, _ in WK for d in D[f] if d["peak"] is not None]
ax.axvspan(max(hv), min(wv), color="#ffd27f", alpha=0.35, lw=0, zorder=1)
ax.annotate("cell gap %.3f\u00b0\n= 76.5 seed SD" % (min(wv) - max(hv)),
            xy=((max(hv) + min(wv)) / 2, y + 0.6), ha="center", fontsize=8.5, color="#7a5200")
ax.set_yticks(ticks); ax.set_yticklabels(labs, fontsize=8.5)
ax.set_xlabel("peak ankle dorsiflexion in swing (deg)")
ax.set_title("Every hyperreflexia cell is less dorsiflexed than every weakness cell",
             loc="left", fontsize=10)
ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
fig.tight_layout(); fig.savefig(os.path.join(OUT, "fig2_endpoint_cells.png"), dpi=200)
plt.close(fig); print("fig2 ok")

# ---- Fig 3: the 81-candidate scan --------------------------------------------------------------
sw = json.load(io.open(os.path.join(P, "SWEEP_r532.json"), encoding="utf-8"))["all_candidates"]
fig, ax = plt.subplots(figsize=(8.4, 4.2))
for j, col, mk in (("ankle", "#2ca02c", "o"), ("knee", "#9467bd", "s"), ("hip", "#8c564b", "^")):
    pts = [(int(r["name"].split(" at ")[1].split("%")[0]), r["gap_in_seed_SD"], r["two_sided"])
           for r in sw if r["joint"] == j and " at " in r["name"] and "of cycle" in r["name"]]
    pts.sort()
    ax.plot([p[0] for p in pts], [max(p[1], -2) for p in pts], color=col, lw=1.3, alpha=0.75,
            label=j, zorder=2)
    ts = [p for p in pts if p[2]]
    if ts:
        ax.scatter([p[0] for p in ts], [p[1] for p in ts], s=52, facecolor="none",
                   edgecolor=col, linewidth=1.8, zorder=4)
ax.axhline(0, color="#bbbbbb", lw=0.7)
ax.axvline(tof, color="#999999", lw=0.9, ls=":")
ax.scatter([81], [76.5], marker="*", s=210, color=C_HY, zorder=5)
ax.annotate("peak in swing\n76.5", xy=(81, 76.5), xytext=(64, 62), fontsize=8.5, color=C_HY,
            arrowprops=dict(arrowstyle="-", color=C_HY, lw=0.9))
ax.set_xlabel("% of gait cycle"); ax.set_ylabel("cell gap in seed SD")
ax.set_title("The scan: separation across the cycle. Rings mark the two-sided candidates.",
             loc="left", fontsize=10)
ax.legend(frameon=False, fontsize=9)
ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
fig.tight_layout(); fig.savefig(os.path.join(OUT, "fig3_scan.png"), dpi=200)
plt.close(fig); print("fig3 ok")

# ---- Fig 4: the asymmetry, on the mixed grid ---------------------------------------------------
mx = json.load(io.open(os.path.join(P, "MIXEDSWING_r526.json"), encoding="utf-8"))
cm = mx["cell_means_swing_df_deg"]
fig, ax = plt.subplots(1, 2, figsize=(10.4, 4.0), sharey=True)
ws = sorted(set(float(k.split("_KV")[0][1:]) for k in cm))
gs = sorted(set(float(k.split("_KV")[1]) for k in cm))
for w in ws:
    v = [(g, cm.get("x%.2f_KV%.3f" % (w, g))) for g in gs]
    v = [(g, y) for g, y in v if y is not None]
    ax[0].plot([g for g, _ in v], [y for _, y in v], "o-", lw=1.5, ms=5,
               label="TA x%.2f" % w)
for g in gs:
    v = [(w, cm.get("x%.2f_KV%.3f" % (w, g))) for w in ws]
    v = [(w, y) for w, y in v if y is not None]
    ax[1].plot([w for w, _ in v], [y for _, y in v], "s-", lw=1.5, ms=5,
               label="KV %.3f" % g)
ax[0].set_xlabel("delivered reflex gain"); ax[1].set_xlabel("tibialis anterior force scaling")
ax[0].set_ylabel("peak swing dorsiflexion (deg)")
ax[0].set_title("A   across the reflex axis: 8.21\u00b0", loc="left", fontsize=10)
ax[1].set_title("B   across the weakness axis: 1.45\u00b0 at most, and it reverses sign",
                loc="left", fontsize=10)
for a in ax:
    a.legend(frameon=False, fontsize=8); a.axhline(0, color="#bbbbbb", lw=0.7)
    a.spines["top"].set_visible(False); a.spines["right"].set_visible(False)
fig.tight_layout(); fig.savefig(os.path.join(OUT, "fig4_asymmetry.png"), dpi=200)
plt.close(fig); print("fig4 ok")

# ---- Fig 5: under motion-capture error ---------------------------------------------------------
cl = json.load(io.open(os.path.join(P, "CLAIMS_r537.json"), encoding="utf-8"))["results"]
fig, ax = plt.subplots(1, 2, figsize=(10.4, 3.9))
sig = [0.0, 1.0, 2.0, 3.0]
NAMES = [("ankle peak in swing", C_HY, "-"), ("ankle 40-50% window", "#2ca02c", "--"),
         ("knee at contact  [current]", "#9467bd", ":")]
for nm, col, ls in NAMES:
    if nm not in cl:
        continue
    lab = nm.replace("  [current]", "")
    ax[0].plot(sig, [cl[nm]["by_sigma"][str(s)]["claim2_arm_lofo_acc"] for s in sig],
               ls, color=col, lw=1.8, marker="o", ms=4, label=lab)
    ax[1].plot(sig, [cl[nm]["by_sigma"][str(s)]["claim3_tone_severity_rho"] for s in sig],
               ls, color=col, lw=1.8, marker="o", ms=4, label=lab)
ax[0].set_ylabel("leave-one-family-out accuracy"); ax[0].set_ylim(0.6, 1.02)
ax[1].set_ylabel("Spearman \u03c1 with delivered gain"); ax[1].set_ylim(0.4, 1.02)
ax[0].set_title("A   distinguishing the two lesions", loc="left", fontsize=10)
ax[1].set_title("B   grading tone severity", loc="left", fontsize=10)
for a in ax:
    a.set_xlabel("per-frame jitter \u03c3 (deg)"); a.legend(frameon=False, fontsize=8.5)
    a.spines["top"].set_visible(False); a.spines["right"].set_visible(False)
fig.tight_layout(); fig.savefig(os.path.join(OUT, "fig5_mocap.png"), dpi=200)
plt.close(fig); print("fig5 ok")

print("\nfigures in %s:" % OUT)
for f in sorted(os.listdir(OUT)):
    print("   %-32s %d bytes" % (f, os.path.getsize(os.path.join(OUT, f))))
