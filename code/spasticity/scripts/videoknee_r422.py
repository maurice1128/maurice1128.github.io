# -*- coding: utf-8 -*-
"""r422: does the +6.3919 deg knee separation survive 2D markerless video noise?

Registered by paper/PREREG_videoknee_r422.md, sha256 4618ecfad328d19c... hashed before any noise
was injected. NO SIMULATION IS RUN -- this injects noise into .sto files that already exist, so it
consumes no Hyfydy licence.

The published literature supplies sigma. It cannot supply the answer, because whether 6.3919 deg
survives depends on (a) averaging over 5-6 cycles, which divides per-frame noise by sqrt(n_cyc),
(b) each arm's own spread, since the endpoint is an EDGE gap not a mean difference, and (c) how
the heel-strike event is found. All three are properties of this design.
"""
import glob
import io
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sto_utils as S

RES = r"C:\Users\maurice\Documents\SCONE\results"
OUT = r"C:\Users\maurice\Desktop\spasticity_paper\paper\VIDEOKNEE_r422.json"
SETTLE, T1 = 1.0, 9.73
SEED = 20260826
N_REP = 200
SIGMAS = [0, 1, 2, 3, 4, 5, 6, 8, 10]
FS_LIST = [30, 60]
YAWS = [0, 10, 20, 30]
KFRAMES = [0, 1, 2]

SPAS = ["R396SPg110_s%d" % s for s in (101, 102, 105, 106)]
WEAK = ["R151W_s%d" % s for s in range(101, 107)]
LADDER = {"KV0.070": ["R393SPg070_s%d" % s for s in range(101, 107)],
          "KV0.100": ["R393SPg100_s%d" % s for s in range(101, 107)],
          "KV0.120": ["R396SPg120_s%d" % s for s in range(101, 107)]}


def load(prefix):
    """-> (resampled time grid per fs, knee angle deg, heel-strike sample indices per fs)."""
    g = [d for d in glob.glob(os.path.join(RES, prefix + ".*")) if os.path.isdir(d)]
    if not g:
        return None
    if len(g) > 1:
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
    hs_t = np.array([t[a] for a, _ in win])            # heel-strike TIMES, resolution-free

    out = {}
    for fs in FS_LIST:
        tg = np.arange(t[0], t[-1], 1.0 / fs)
        kg = np.interp(tg, t, kn)
        idx = np.searchsorted(tg, hs_t)                # nearest frame of each heel strike
        idx = np.clip(idx, 0, len(tg) - 1)
        out[fs] = {"t": tg, "knee": kg, "hs_idx": idx}
    return out


def readout(cell, fs, sigma, yaw, kmax, rng):
    """One noisy realisation of the cell's endpoint, in degrees."""
    d = cell[fs]
    k = d["knee"] * np.cos(np.radians(yaw))            # out-of-plane projection
    if sigma > 0:
        k = k + rng.normal(0.0, sigma, size=k.shape)   # per-frame keypoint jitter
    idx = d["hs_idx"]
    if kmax > 0:
        idx = np.clip(idx + rng.integers(-kmax, kmax + 1, size=idx.shape), 0, len(k) - 1)
    return float(np.mean(k[idx]))                      # per-cycle mean, corpus convention


def edge_gap(spas_vals, weak_vals):
    return min(weak_vals) - max(spas_vals)


def loo_accuracy(spas_vals, weak_vals):
    """Leave-one-out midpoint-threshold classification over the 10 cells."""
    lab = [("S", v) for v in spas_vals] + [("W", v) for v in weak_vals]
    ok = 0
    for i in range(len(lab)):
        rest = lab[:i] + lab[i + 1:]
        s = [v for c, v in rest if c == "S"]
        w = [v for c, v in rest if c == "W"]
        thr = 0.5 * (np.mean(s) + np.mean(w))
        pred = "S" if lab[i][1] < thr else "W"         # spastic knee is MORE flexed = more negative
        ok += (pred == lab[i][0])
    return ok / len(lab)


def main():
    cells = {}
    for p in SPAS + WEAK + [x for v in LADDER.values() for x in v]:
        c = load(p)
        if c:
            cells[p] = c
    sp = [p for p in SPAS if p in cells]
    wk = [p for p in WEAK if p in cells]
    print("loaded  SPAS %d/%d   WEAK %d/%d" % (len(sp), len(SPAS), len(wk), len(WEAK)))

    clean_s = [readout(cells[p], 60, 0, 0, 0, np.random.default_rng(0)) for p in sp]
    clean_w = [readout(cells[p], 60, 0, 0, 0, np.random.default_rng(0)) for p in wk]
    clean_gap = edge_gap(clean_s, clean_w)
    print("clean edge gap at fs60 yaw0 k0: %+.4f deg   (corpus value +6.3919)" % clean_gap)

    res = {"round": "VIDEOKNEE_r422", "registration": "PREREG_videoknee_r422.md",
           "registration_sha256":
               "4618ecfad328d19c99c562d95455f6508c598a54312cac51d058e3a9cd2a7e7b",
           "no_simulation_run": True, "n_rep": N_REP, "rng_seed": SEED,
           "clean": {"spas": clean_s, "weak": clean_w, "edge_gap_deg": clean_gap,
                     "corpus_edge_gap_deg": 6.391931677410274,
                     "resampling_shift_deg": clean_gap - 6.391931677410274},
           "grid": {}}

    print()
    print("%-4s %-4s %-3s %-6s  %-9s %-9s %s" %
          ("fs", "yaw", "k", "sigma", "disjoint%", "acc", "median gap"))
    for fs in FS_LIST:
        for yaw in YAWS:
            for kmax in KFRAMES:
                for sigma in SIGMAS:
                    rng = np.random.default_rng(SEED + fs * 1000 + yaw * 100 + kmax * 10 + sigma)
                    gaps, dis, accs = [], 0, []
                    for _ in range(N_REP):
                        s = [readout(cells[p], fs, sigma, yaw, kmax, rng) for p in sp]
                        w = [readout(cells[p], fs, sigma, yaw, kmax, rng) for p in wk]
                        g = edge_gap(s, w)
                        gaps.append(g)
                        dis += (g > 0)
                        accs.append(loo_accuracy(s, w))
                    key = "fs%d_yaw%d_k%d_s%g" % (fs, yaw, kmax, sigma)
                    res["grid"][key] = {
                        "fs": fs, "yaw_deg": yaw, "k_frames": kmax, "sigma_deg": sigma,
                        "disjoint_rate": dis / N_REP,
                        "accuracy_mean": float(np.mean(accs)),
                        "gap_median_deg": float(np.median(gaps)),
                        "gap_p05_deg": float(np.percentile(gaps, 5)),
                        "gap_p95_deg": float(np.percentile(gaps, 95))}
                    if yaw in (0, 20) and kmax in (0, 1):
                        print("%-4d %-4d %-3d %-6g  %-9.3f %-9.3f %+.4f"
                              % (fs, yaw, kmax, sigma, dis / N_REP, np.mean(accs),
                                 np.median(gaps)))
                sys.stdout.flush()

    def first_below(fs, yaw, kmax, field, thresh):
        for sigma in SIGMAS:
            if res["grid"]["fs%d_yaw%d_k%d_s%g" % (fs, yaw, kmax, sigma)][field] < thresh:
                return sigma
        return None

    res["sigma_break_disjoint95"] = {"fs60_yaw0_k0": first_below(60, 0, 0, "disjoint_rate", 0.95),
                                     "fs30_yaw20_k1": first_below(30, 20, 1, "disjoint_rate", 0.95)}
    res["sigma_chance_acc70"] = {"fs60_yaw0_k0": first_below(60, 0, 0, "accuracy_mean", 0.70),
                                 "fs30_yaw20_k1": first_below(30, 20, 1, "accuracy_mean", 0.70)}

    P = {}
    sb = res["sigma_break_disjoint95"]["fs60_yaw0_k0"]
    P["P1_sigma_break_at_least_3"] = {
        "sigma_break": sb,
        "VERDICT": "HOLDS" if (sb is None or sb >= 3.0) else "FAILS"}
    a = res["grid"]["fs30_yaw20_k1_s2"]["accuracy_mean"]
    P["P2_phone_condition_acc_at_least_0.80_at_sigma2"] = {
        "accuracy": a, "VERDICT": "HOLDS" if a >= 0.80 else "FAILS"}
    d_yaw = (res["grid"]["fs60_yaw0_k0_s0"]["accuracy_mean"]
             - res["grid"]["fs60_yaw30_k0_s0"]["accuracy_mean"])
    d_sig = (res["grid"]["fs60_yaw0_k0_s0"]["accuracy_mean"]
             - res["grid"]["fs60_yaw0_k0_s5"]["accuracy_mean"])
    P["P3_yaw_matters_less_than_jitter"] = {
        "accuracy_drop_from_yaw_0_to_30": d_yaw, "accuracy_drop_from_sigma_0_to_5": d_sig,
        "VERDICT": "HOLDS" if d_yaw < d_sig else "FAILS"}
    res["predictions"] = P
    res["VERDICT"] = "; ".join("%s %s" % (k, v["VERDICT"]) for k, v in P.items())

    io.open(OUT, "w", encoding="utf-8").write(json.dumps(res, indent=2, ensure_ascii=False))
    print()
    for k, v in P.items():
        print("  %-46s %s" % (k, v["VERDICT"]))
    print()
    print("sigma_break (disjoint<95%%): %s" % res["sigma_break_disjoint95"])
    print("sigma_chance (acc<70%%)    : %s" % res["sigma_chance_acc70"])
    print("wrote %s (%d B)" % (OUT, os.path.getsize(OUT)))


if __name__ == "__main__":
    main()
