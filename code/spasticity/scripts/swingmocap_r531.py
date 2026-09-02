# -*- coding: utf-8 -*-
"""r531: does the peak-swing-dorsiflexion separation survive being measured by motion capture?

The claim this paper would make is that a clinician with a gait lab can tell plantarflexor
overactivity from dorsiflexor weakness. That requires the separation to survive the measurement, not
only to exist in the simulation. VIDEOKNEE_r422 asked this of knee-at-contact and its protocol is
reused unchanged: Gaussian per-frame jitter, frame-rate reduction, out-of-plane yaw, and event-frame
error, scored by edge gap and leave-one-out accuracy.

One thing must be added, because this endpoint is a PEAK and the previous one was a point.
Averaging a point readout over cycles divides zero-mean noise by sqrt(n). Taking a MAXIMUM over a
noisy window does not average noise -- it rectifies it, and the peak is biased upward by roughly
sigma times the expected maximum of n standard normals, which for a 30-frame swing is about 2
sigma. At sigma = 3 deg that is a 6 deg bias, larger than the effect. Both arms are biased, so the
difference may survive, but the bias depends on the curvature near each arm's peak and there is no
reason for it to cancel exactly. Real motion capture low-pass filters before any peak is taken, so
the protocol is run both raw and with the 6 Hz Butterworth-equivalent smoothing that ref [15] used,
and the difference between the two is itself the result.
"""
import glob, io, json, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sto_utils as S

RES = r"C:\Users\maurice\Documents\SCONE\results"
P = r"C:\Users\maurice\Desktop\spasticity_paper\paper"
SETTLE, T1 = 1.0, 9.73
SEED, N_REP = 20260830, 200
SIGMAS = [0, 0.5, 1, 2, 3, 4, 5, 6, 8, 10]
FS_LIST = [30, 60, 100]
YAWS = [0, 10, 20, 30]
KFRAMES = [0, 1, 2]
SMOOTH = [None, 6.0]                       # None = raw; 6.0 Hz = the marker-data convention of [15]

HY = ["R151S", "R393SPg070", "R393SPg100", "R396SPg110", "R396SPg120"]
WK = ["R151W", "R174W870", "R174W892", "R169W090", "R174W915", "R169W095"]
SEEDS = range(101, 107)


def load(fam, sd):
    """-> resampled ankle trace per frame rate, plus the swing spans as frame index ranges."""
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
    an = np.degrees(S.col(c, dat, "ankle_angle_l"))
    on = grf > thr
    # swing spans as TIMES, so they survive resampling
    spans = []
    for a, b in w:
        idx = np.where(~on[a:b])[0]
        if idx.size:
            spans.append((float(t[a + idx[0]]), float(t[a + idx[-1]])))
    if not spans:
        return None
    out = {}
    for fs in FS_LIST:
        tg = np.arange(t[0], t[-1], 1.0 / fs)
        out[fs] = {"t": tg, "ank": np.interp(tg, t, an),
                   "spans": [(int(np.searchsorted(tg, a)), int(np.searchsorted(tg, b)))
                             for a, b in spans]}
    return out


def lowpass(x, fs, fc):
    """zero-phase 2nd-order Butterworth, implemented directly so scipy is not required"""
    import math
    wc = math.tan(math.pi * fc / fs)
    k1, k2 = math.sqrt(2.0) * wc, wc * wc
    a0 = k2 / (1 + k1 + k2)
    a1, a2 = 2 * a0, a0
    b1 = 2 * a0 * (1 / k2 - 1)
    b2 = 1 - (a0 + a1 + a2 + b1)

    def once(v):
        y = np.empty_like(v)
        y[0] = y[1] = v[0]
        for i in range(2, len(v)):
            y[i] = a0 * v[i] + a1 * v[i - 1] + a2 * v[i - 2] + b1 * y[i - 1] + b2 * y[i - 2]
        return y
    return once(once(x)[::-1])[::-1]        # forward-backward: zero phase


def readout(cell, fs, sigma, yaw, kmax, fc, rng):
    d = cell[fs]
    a = d["ank"] * np.cos(np.radians(yaw))
    if sigma > 0:
        a = a + rng.normal(0.0, sigma, size=a.shape)
    if fc:
        a = lowpass(a, fs, fc)
    pk = []
    for s, e in d["spans"]:
        if kmax > 0:
            s = int(np.clip(s + rng.integers(-kmax, kmax + 1), 0, len(a) - 1))
            e = int(np.clip(e + rng.integers(-kmax, kmax + 1), 0, len(a) - 1))
        if e > s:
            pk.append(float(np.max(a[s:e])))
    return float(np.mean(pk)) if pk else float("nan")


def loo(hv, wv):
    lab = [("H", v) for v in hv] + [("W", v) for v in wv]
    ok = 0
    for i in range(len(lab)):
        rest = lab[:i] + lab[i + 1:]
        h = [v for c, v in rest if c == "H"]
        w = [v for c, v in rest if c == "W"]
        th = 0.5 * (np.mean(h) + np.mean(w))
        ok += (("H" if lab[i][1] < th else "W") == lab[i][0])   # hyperreflexia is the LOW arm
    return ok / len(lab)


print("loading ...")
cells, lab = {}, {}
for f in HY + WK:
    for sd in SEEDS:
        c = load(f, sd)
        if c:
            k = "%s_s%d" % (f, sd)
            cells[k] = c
            lab[k] = "H" if f in HY else "W"
kh = [k for k in cells if lab[k] == "H"]
kw = [k for k in cells if lab[k] == "W"]
print("cells: hyper %d  weak %d" % (len(kh), len(kw)))

rng0 = np.random.default_rng(0)
clean_h = [readout(cells[k], 100, 0, 0, 0, None, rng0) for k in kh]
clean_w = [readout(cells[k], 100, 0, 0, 0, None, rng0) for k in kw]
print("clean at fs100, no noise: hyper %.3f  weak %.3f  edge gap %+.3f"
      % (np.mean(clean_h), np.mean(clean_w), min(clean_w) - max(clean_h)))

# --- the bias a maximum picks up from noise, measured rather than assumed --------------------
print("\nupward bias of the peak readout from noise alone (deg), hyperreflexia arm / weakness arm:")
print("   %-8s %-6s %-16s %-16s %s" % ("sigma", "fc", "bias hyper", "bias weak", "bias difference"))
bias = {}
rng = np.random.default_rng(SEED)
for fc in SMOOTH:
    for sg in (0, 1, 2, 3, 5, 8):
        bh = np.mean([np.mean([readout(cells[k], 100, sg, 0, 0, fc, rng) for _ in range(20)])
                      - clean_h[i] for i, k in enumerate(kh[:6])])
        bw = np.mean([np.mean([readout(cells[k], 100, sg, 0, 0, fc, rng) for _ in range(20)])
                      - clean_w[i] for i, k in enumerate(kw[:6])])
        bias[(fc, sg)] = (float(bh), float(bw))
        print("   %-8.1f %-6s %+15.3f %+16.3f %+16.3f"
              % (sg, "raw" if fc is None else "%.0fHz" % fc, bh, bw, bh - bw))

# --- the full grid ----------------------------------------------------------------------------
print("\n%-5s %-6s %-4s %-3s %-6s  %-10s %-8s %s"
      % ("fs", "fc", "yaw", "k", "sigma", "disjoint%", "LOO acc", "median gap"))
grid = {}
rng = np.random.default_rng(SEED)
for fs in FS_LIST:
    for fc in SMOOTH:
        for yaw in YAWS:
            for kmax in KFRAMES:
                for sg in SIGMAS:
                    gaps, accs, dis = [], [], 0
                    reps = 1 if sg == 0 else N_REP
                    for _ in range(reps):
                        hv = [readout(cells[k], fs, sg, yaw, kmax, fc, rng) for k in kh]
                        wv = [readout(cells[k], fs, sg, yaw, kmax, fc, rng) for k in kw]
                        g = min(wv) - max(hv)
                        gaps.append(g)
                        dis += (g > 0)
                        accs.append(loo(hv, wv))
                    key = "fs%d_%s_yaw%d_k%d_sig%g" % (fs, "raw" if fc is None else "fc%.0f" % fc,
                                                       yaw, kmax, sg)
                    grid[key] = {"fs": fs, "fc": fc, "yaw": yaw, "kmax": kmax, "sigma": sg,
                                 "disjoint_frac": dis / float(reps),
                                 "acc_mean": float(np.mean(accs)),
                                 "gap_median": float(np.median(gaps))}
                    if yaw in (0, 20) and kmax in (0, 2) and sg in (0, 1, 3, 5, 8):
                        print("%-5d %-6s %-4d %-3d %-6g  %-10.3f %-8.3f %+.3f"
                              % (fs, "raw" if fc is None else "%.0fHz" % fc, yaw, kmax, sg,
                                 dis / float(reps), np.mean(accs), np.median(gaps)))

raw = [v for v in grid.values() if v["fc"] is None]
sm = [v for v in grid.values() if v["fc"] is not None]
print("\nover the whole grid:")
for nm, s in (("raw peak", raw), ("6 Hz smoothed peak", sm)):
    print("   %-20s disjoint in %5.1f%% of conditions   LOO accuracy %.3f to %.3f (median %.3f)"
          % (nm, 100 * np.mean([v["disjoint_frac"] for v in s]),
             min(v["acc_mean"] for v in s), max(v["acc_mean"] for v in s),
             float(np.median([v["acc_mean"] for v in s]))))

# realistic clinical condition: 100 Hz, 6 Hz filter, small yaw, 1 frame event error
real = [v for v in grid.values() if v["fs"] == 100 and v["fc"] == 6.0 and v["yaw"] <= 10
        and v["kmax"] <= 1 and v["sigma"] <= 3]
print("\nunder realistic laboratory conditions (100 Hz, 6 Hz filter, yaw <= 10 deg, "
      "event error <= 1 frame, jitter <= 3 deg):")
print("   disjoint in %.1f%% of conditions, LOO accuracy %.3f to %.3f"
      % (100 * np.mean([v["disjoint_frac"] for v in real]),
         min(v["acc_mean"] for v in real), max(v["acc_mean"] for v in real)))

dep = {
 "id": "SWINGMOCAP_r531",
 "why": ("The paper's claim is that a clinician with a gait lab can apportion the two lesions. That "
         "requires the separation to survive the measurement. VIDEOKNEE_r422's protocol is reused, "
         "with the addition that a PEAK readout rectifies noise where a point readout averages it."),
 "protocol_from": "VIDEOKNEE_r422, unchanged, plus low-pass smoothing before the peak is taken",
 "n_cells": {"hyperreflexia": len(kh), "weakness": len(kw)},
 "clean": {"hyper_mean": float(np.mean(clean_h)), "weak_mean": float(np.mean(clean_w)),
           "edge_gap_deg": float(min(clean_w) - max(clean_h))},
 "peak_bias_from_noise_deg": {"%s_sigma%g" % ("raw" if k[0] is None else "fc%.0f" % k[0], k[1]):
                              {"hyper": v[0], "weak": v[1], "difference": v[0] - v[1]}
                              for k, v in bias.items()},
 "grid": grid,
 "summary": {
    "raw_peak": {"disjoint_frac_mean": float(np.mean([v["disjoint_frac"] for v in raw])),
                 "acc_min": min(v["acc_mean"] for v in raw),
                 "acc_max": max(v["acc_mean"] for v in raw),
                 "acc_median": float(np.median([v["acc_mean"] for v in raw]))},
    "smoothed_peak": {"disjoint_frac_mean": float(np.mean([v["disjoint_frac"] for v in sm])),
                      "acc_min": min(v["acc_mean"] for v in sm),
                      "acc_max": max(v["acc_mean"] for v in sm),
                      "acc_median": float(np.median([v["acc_mean"] for v in sm]))},
    "realistic_laboratory": {"disjoint_frac_mean": float(np.mean([v["disjoint_frac"] for v in real])),
                             "acc_min": min(v["acc_mean"] for v in real),
                             "acc_max": max(v["acc_mean"] for v in real)}},
}
io.open(os.path.join(P, "SWINGMOCAP_r531.json"), "w", encoding="utf-8",
        newline="").write(json.dumps(dep, indent=1, ensure_ascii=False))
print("\n-> SWINGMOCAP_r531.json")
