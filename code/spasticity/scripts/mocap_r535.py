# -*- coding: utf-8 -*-
"""r535: every candidate readout under motion-capture error, scored the same way.

The claim the paper would make is clinical, so separation in the simulation is not enough: it has to
survive being measured. VIDEOKNEE_r422 asked this of knee-at-contact and its protocol is reused
unchanged -- per-frame Gaussian jitter, frame-rate reduction, out-of-plane yaw, event-frame error --
scored by edge gap and leave-one-out accuracy.

The candidates differ in three ways that the old single-endpoint test could not expose, and each
predicts a different response to noise:

  POINT vs PEAK. Averaging a point readout over cycles divides zero-mean noise by sqrt(n). Taking a
  MAXIMUM over a window rectifies noise instead, biasing the reading upward by roughly sigma times
  the expected maximum of n standard normals. Peak swing dorsiflexion is a peak; everything else
  here is a point.

  STEEP vs FLAT. A readout taken where the joint is moving fast turns a phase error into a reading
  error. Ankle at 85 per cent sits where the control curve falls about 1.1 deg per one per cent of
  cycle; the 40 to 50 per cent band sits where it moves a sixth as fast.

  INSTANT vs WINDOW. A window mean over eleven samples divides jitter by sqrt(11) before anything
  else happens. That is free precision the instant readouts do not get.

Two-sidedness is re-checked under noise, because a readout that separates but loses its sign
reversal has stopped being an apportionment.
"""
import glob, io, json, math, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sto_utils as S

RES = r"C:\Users\maurice\Documents\SCONE\results"
P = r"C:\Users\maurice\Desktop\spasticity_paper\paper"
SETTLE, T1 = 1.0, 9.73
SEED, N_REP = 20260830, 120
SIGMAS = [0, 0.5, 1, 2, 3, 5, 8]
FS_LIST = [60, 100]
YAWS = [0, 10, 20]
KFRAMES = [0, 1, 2]
CTRL = ["R151C"]
HY = ["R151S", "R393SPg070", "R393SPg100", "R396SPg110", "R396SPg120"]
WK = ["R151W", "R174W870", "R174W892", "R169W090", "R174W915", "R169W095"]


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
    kn = np.degrees(S.col(c, dat, "knee_angle_l"))
    an = np.degrees(S.col(c, dat, "ankle_angle_l"))
    out = {"cycles": []}
    for a, b in w:
        idx = np.where(~on[a:b])[0]
        out["cycles"].append({"t": t[a:b] - t[a], "dur": float(t[b] - t[a]),
                              "knee": kn[a:b], "ankle": an[a:b],
                              "swing": (int(idx[0]), int(idx[-1])) if idx.size else None})
    return out


# readout(cycle_dict, noisy_knee, noisy_ankle, fs, rng, kmax) -> one cycle's value
def at_pct(joint, pct):
    def f(cy, nk, na, kerr):
        y = nk if joint == "knee" else na
        n = len(y)
        i = int(round((pct / 100.0) * (n - 1))) + kerr
        return float(y[int(np.clip(i, 0, n - 1))])
    return f


def win_pct(joint, lo, hi):
    def f(cy, nk, na, kerr):
        y = nk if joint == "knee" else na
        n = len(y)
        a = int(round((lo / 100.0) * (n - 1))) + kerr
        b = int(round((hi / 100.0) * (n - 1))) + kerr
        a, b = int(np.clip(a, 0, n - 2)), int(np.clip(b, 1, n - 1))
        return float(np.mean(y[min(a, b):max(a, b) + 1]))
    return f


def swing_peak(cy, nk, na, kerr):
    if cy["swing"] is None:
        return float("nan")
    a, b = cy["swing"]
    a = int(np.clip(a + kerr, 0, len(na) - 2))
    b = int(np.clip(b + kerr, a + 1, len(na) - 1))
    return float(np.max(na[a:b]))


CANDS = [("knee at contact  [current]", at_pct("knee", 0), "point", "knee"),
         ("ankle 40-50% window", win_pct("ankle", 40, 50), "window", "ankle"),
         ("ankle at 45%", at_pct("ankle", 45), "point", "ankle"),
         ("ankle at 85%  [scan winner]", at_pct("ankle", 85), "point", "ankle"),
         ("ankle peak in swing", swing_peak, "peak", "ankle")]

print("loading ...")
CELLS = {}
for f in CTRL + HY + WK:
    v = [d for d in (load(f, s) for s in range(101, 107)) if d]
    CELLS[f] = v
    print("   %-12s n=%d" % (f, len(v)))


def cellval(cell, fn, fs, sigma, yaw, kmax, rng):
    vals = []
    for cy in cell["cycles"]:
        n_new = max(8, int(round(cy["dur"] * fs)))
        g = np.linspace(0, 1, n_new)
        src = np.linspace(0, 1, len(cy["knee"]))
        nk = np.interp(g, src, cy["knee"]) * math.cos(math.radians(yaw))
        na = np.interp(g, src, cy["ankle"]) * math.cos(math.radians(yaw))
        if sigma > 0:
            nk = nk + rng.normal(0, sigma, nk.shape)
            na = na + rng.normal(0, sigma, na.shape)
        sw = None
        if cy["swing"]:
            sc = len(cy["knee"]) - 1.0
            sw = (int(cy["swing"][0] / sc * (n_new - 1)), int(cy["swing"][1] / sc * (n_new - 1)))
        kerr = int(rng.integers(-kmax, kmax + 1)) if kmax else 0
        vals.append(fn({"swing": sw, "dur": cy["dur"]}, nk, na, kerr))
    v = [x for x in vals if not math.isnan(x)]
    return float(np.mean(v)) if v else float("nan")


def loo(hv, wv):
    lab = [("H", v) for v in hv] + [("W", v) for v in wv]
    sgn = 1 if np.mean(hv) < np.mean(wv) else -1
    ok = 0
    for i in range(len(lab)):
        r = lab[:i] + lab[i + 1:]
        th = 0.5 * (np.mean([v for c, v in r if c == "H"]) + np.mean([v for c, v in r if c == "W"]))
        ok += (("H" if sgn * lab[i][1] < sgn * th else "W") == lab[i][0])
    return ok / len(lab)


OUT = {}
print("\n%-28s %-7s %-6s %-9s %-9s %-9s %s"
      % ("readout", "kind", "sigma", "disjoint%", "LOO acc", "2-sided%", "median gap"))
for name, fn, kind, joint in CANDS:
    rng = np.random.default_rng(SEED)
    rows = {}
    for fs in FS_LIST:
        for yaw in YAWS:
            for kmax in KFRAMES:
                for sg in SIGMAS:
                    reps = 1 if sg == 0 else N_REP
                    dis = two = 0
                    accs, gaps = [], []
                    for _ in range(reps):
                        cv = [cellval(c, fn, fs, sg, yaw, kmax, rng) for f in CTRL for c in CELLS[f]]
                        hv = [cellval(c, fn, fs, sg, yaw, kmax, rng) for f in HY for c in CELLS[f]]
                        wv = [cellval(c, fn, fs, sg, yaw, kmax, rng) for f in WK for c in CELLS[f]]
                        cv = [x for x in cv if not math.isnan(x)]
                        hv = [x for x in hv if not math.isnan(x)]
                        wv = [x for x in wv if not math.isnan(x)]
                        if not (cv and hv and wv):
                            continue
                        g = max(min(wv) - max(hv), min(hv) - max(wv))
                        gaps.append(g)
                        dis += (g > 0)
                        c0 = np.mean(cv)
                        two += ((np.mean(hv) - c0) * (np.mean(wv) - c0) < 0)
                        accs.append(loo(hv, wv))
                    if gaps:
                        rows["fs%d_yaw%d_k%d_s%g" % (fs, yaw, kmax, sg)] = {
                            "fs": fs, "yaw": yaw, "kmax": kmax, "sigma": sg,
                            "disjoint_frac": dis / len(gaps), "two_sided_frac": two / len(gaps),
                            "acc": float(np.mean(accs)), "gap_median": float(np.median(gaps))}
    OUT[name] = rows
    for sg in SIGMAS:
        sub = [v for v in rows.values() if v["sigma"] == sg]
        if sub:
            print("%-28s %-7s %-6g %-9.3f %-9.3f %-9.3f %+.3f"
                  % (name if sg == 0 else "", kind if sg == 0 else "", sg,
                     np.mean([v["disjoint_frac"] for v in sub]),
                     np.mean([v["acc"] for v in sub]),
                     np.mean([v["two_sided_frac"] for v in sub]),
                     np.median([v["gap_median"] for v in sub])))

print("\nunder realistic laboratory conditions (100 Hz, yaw <= 10 deg, event error <= 1 frame, "
      "jitter <= 3 deg):")
print("   %-28s %-11s %-11s %s" % ("readout", "disjoint", "LOO acc", "keeps sign reversal"))
summ = {}
for name, rows in OUT.items():
    real = [v for v in rows.values() if v["fs"] == 100 and v["yaw"] <= 10 and v["kmax"] <= 1
            and v["sigma"] <= 3]
    if real:
        summ[name] = {"disjoint": float(np.mean([v["disjoint_frac"] for v in real])),
                      "acc": float(np.mean([v["acc"] for v in real])),
                      "two_sided": float(np.mean([v["two_sided_frac"] for v in real]))}
        print("   %-28s %-11.3f %-11.3f %.3f"
              % (name, summ[name]["disjoint"], summ[name]["acc"], summ[name]["two_sided"]))

io.open(os.path.join(P, "MOCAP_r535.json"), "w", encoding="utf-8", newline="").write(
    json.dumps({"id": "MOCAP_r535",
                "why": ("The claim is clinical, so separation has to survive being measured. "
                        "VIDEOKNEE_r422's protocol, applied to every candidate at once so that "
                        "point, window and peak readouts can be compared under the same noise."),
                "protocol_from": "VIDEOKNEE_r422",
                "n_rep": N_REP, "rng_seed": SEED,
                "grid": OUT, "realistic_laboratory": summ}, indent=1, ensure_ascii=False))
print("\n-> MOCAP_r535.json")
