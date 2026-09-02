# -*- coding: utf-8 -*-
"""F3 -- settle the stance account by measurement. Implements PREREG_stance_test_r231.md.

The stance mechanism was declared refuted by comparing an IMPULSE fraction to a DURATION
fraction, which is not a test of it. What rev 1 predicted is RESISTANCE TO DORSIFLEXION, so
that is what is measured: the added plantarflexor force the reflex would produce, against the
baseline force in the same phase, per normalised-cycle bin.

Control cells only -- un-re-optimised, so this is where the lesion WOULD act, not where the
optimiser moved it. Corrected x1.0 velocity scale (V = fiber_velocity_norm, F5).

READ ONLY.
"""
import io
import os
import re
import sys
import glob
import json
import hashlib

sys.path.insert(0, r"C:\Users\maurice\Desktop\spasticity_paper\scone")
import numpy as np
import sto_utils as S

RES = r"C:\Users\maurice\Documents\SCONE\results"
PAPER = r"C:\Users\maurice\Desktop\spasticity_paper\paper"
PREREG = os.path.join(PAPER, "PREREG_stance_test_r231.md")

SETTLE, T1 = 1.0, 9.73
SEEDS = [101, 102, 103, 104, 105, 106]
KV = 0.050
FMAX = {"soleus_l": 3549.0, "gastroc_l": 2241.0}
NBIN = 20
LR_HI = 0.15            # loading response: 0-15 percent of cycle
ES_WIN = 0.15           # early swing: first 15 percent after toe-off
EPS_U = 0.01


def sha(p):
    return hashlib.sha256(io.open(p, "rb").read()).hexdigest()


def ankle_convention():
    g = glob.glob(os.path.join(RES, "R151C_s101.*", "H1922v7b3.hfd"))
    if not g:
        return {"error": "hfd not found"}
    t = io.open(g[0], encoding="utf-8", errors="replace").read()
    d = dict(re.findall(r"dof\s*\{\s*name\s*=\s*(ankle_angle_[lr])\s+source\s*=\s*(\S+)", t))
    return {"dofs": d, "note": "positive ankle_angle direction read from the model, not assumed"}


def per_seed(seed):
    ds = [x for x in glob.glob(os.path.join(RES, "R151C_s%d.*" % seed)) if os.path.isdir(x)]
    d = sorted(ds)[0]
    sto = sorted(glob.glob(os.path.join(d, "*.par.sto")))[-1]
    cols, dat = S.load_sto(sto)
    t = np.asarray(S.col(cols, dat, "time"), float)
    grf, thr = S.grf_vertical(cols, dat, "l")
    grf = np.asarray(grf, float)
    idx = S.heel_strikes(t, grf, thresh=thr)
    cyc = [(idx[k], idx[k + 1]) for k in range(len(idx) - 1)
           if t[idx[k]] >= SETTLE and t[idx[k + 1]] <= T1]
    cyc = cyc[:-1] if len(cyc) >= 2 else cyc
    if len(cyc) < 2:
        return None

    ank = np.asarray(S.col(cols, dat, "ankle_angle_l"), float) * 180.0 / np.pi
    chan = {}
    for m in FMAX:
        chan[m] = {"v": np.asarray(S.col(cols, dat, m + ".fiber_velocity_norm"), float),
                   "u": np.asarray(S.col(cols, dat, m + ".excitation"), float),
                   "f": np.asarray(S.col(cols, dat, m + ".mtu_force_norm"), float)}

    bins_add = np.zeros(NBIN); bins_base = np.zeros(NBIN)
    bins_du = np.zeros(NBIN); bins_u = np.zeros(NBIN)
    bins_dank = np.zeros(NBIN); bins_n = np.zeros(NBIN)
    lr = {"add": 0.0, "base": 0.0, "dank": 0.0, "n": 0}
    es = {"add": 0.0, "base": 0.0, "dank": 0.0, "n": 0}

    for (a, b) in cyc:
        n = b - a
        ph = (np.arange(n)) / float(n)
        st = grf[a:b] > 0.05
        to = np.argmax(~st) / float(n) if (~st).any() else 1.0   # toe-off phase
        dank = np.gradient(ank[a:b])
        f_add = np.zeros(n); f_base = np.zeros(n)
        du_t = np.zeros(n); u_t = np.zeros(n)
        for m, F in FMAX.items():
            v = chan[m]["v"][a:b]; u = chan[m]["u"][a:b]; f = chan[m]["f"][a:b]
            du = np.minimum(KV * np.maximum(0.0, v), np.maximum(0.0, 1.0 - u))
            gain = f / np.maximum(u, EPS_U)
            f_add += du * F * gain
            f_base += f * F
            du_t += du; u_t += u
        b_idx = np.minimum((ph * NBIN).astype(int), NBIN - 1)
        for i in range(n):
            k = b_idx[i]
            bins_add[k] += f_add[i]; bins_base[k] += f_base[i]
            bins_du[k] += du_t[i]; bins_u[k] += u_t[i]
            bins_dank[k] += dank[i]; bins_n[k] += 1
        for i in range(n):
            if ph[i] < LR_HI:
                lr["add"] += f_add[i]; lr["base"] += f_base[i]
                lr["dank"] += dank[i]; lr["n"] += 1
            elif to <= ph[i] < to + ES_WIN:
                es["add"] += f_add[i]; es["base"] += f_base[i]
                es["dank"] += dank[i]; es["n"] += 1

    nz = np.maximum(bins_n, 1)
    return {"seed": seed, "n_cycles": len(cyc), "sto": os.path.basename(sto),
            "bins": {"add_N": (bins_add / nz).tolist(), "base_N": (bins_base / nz).tolist(),
                     "du": (bins_du / nz).tolist(), "u": (bins_u / nz).tolist(),
                     "d_ankle": (bins_dank / nz).tolist()},
            "LR": {k: (lr[k] / max(lr["n"], 1) if k != "n" else lr["n"]) for k in lr},
            "ES": {k: (es[k] / max(es["n"], 1) if k != "n" else es["n"]) for k in es},
            "peak_add_N": float(max(bins_add / nz))}


def main():
    rows = [r for r in (per_seed(s) for s in SEEDS) if r is not None]
    res = {"round": 231, "window": [SETTLE, T1], "kv": KV, "n_bins": NBIN,
           "scale": "corrected x1.0 (V = fiber_velocity_norm)",
           "ankle_convention": ankle_convention(),
           "moment_arm_assumption": ("forces reported, not moments; added/baseline MOMENT "
                                     "ratios equal FORCE ratios only under a constant moment "
                                     "arm within a phase"),
           "provenance": {"script": os.path.basename(__file__),
                          "script_sha256": sha(os.path.abspath(__file__)),
                          "prereg_sha256": sha(PREREG)},
           "per_seed": rows}
    if len(rows) < 4:
        res["OUTCOME"] = "S4"; res["reason"] = "only %d usable seeds" % len(rows)
    else:
        lr_add = float(np.mean([r["LR"]["add"] for r in rows]))
        lr_base = float(np.mean([r["LR"]["base"] for r in rows]))
        es_add = float(np.mean([r["ES"]["add"] for r in rows]))
        es_base = float(np.mean([r["ES"]["base"] for r in rows]))
        peak = float(np.mean([r["peak_add_N"] for r in rows]))
        lr_dank = float(np.mean([r["LR"]["dank"] for r in rows]))
        es_dank = float(np.mean([r["ES"]["dank"] for r in rows]))
        res["summary"] = {"LR_add_N": lr_add, "LR_base_N": lr_base,
                          "LR_ratio": lr_add / lr_base if lr_base else None,
                          "ES_add_N": es_add, "ES_base_N": es_base,
                          "ES_ratio": es_add / es_base if es_base else None,
                          "peak_add_N": peak,
                          "LR_add_as_frac_of_peak": lr_add / peak if peak else None,
                          "ES_add_as_frac_of_peak": es_add / peak if peak else None,
                          "LR_mean_d_ankle": lr_dank, "ES_mean_d_ankle": es_dank}
        s = res["summary"]
        if s["LR_add_as_frac_of_peak"] is not None and es_add > 0 and \
                min(lr_add, es_add) >= 0.5 * max(lr_add, es_add):
            res["OUTCOME"] = "S3"
            res["reason"] = ("LR %.2f N and ES %.2f N are comparable: the reflex is not "
                             "phase-localised" % (lr_add, es_add))
        elif s["LR_ratio"] is not None and s["LR_ratio"] >= 0.20 and s["LR_add_as_frac_of_peak"] >= 0.05:
            res["OUTCOME"] = "S1"
            res["reason"] = ("LR added force is %.1f%% of baseline there and %.1f%% of peak"
                             % (100 * s["LR_ratio"], 100 * s["LR_add_as_frac_of_peak"]))
        elif s["LR_add_as_frac_of_peak"] < 0.05:
            res["OUTCOME"] = "S2"
            res["reason"] = ("LR added force is %.2f N, only %.1f%% of the cycle peak %.2f N: "
                             "negligible in absolute terms"
                             % (lr_add, 100 * s["LR_add_as_frac_of_peak"], peak))
        else:
            res["OUTCOME"] = "S2"
            res["reason"] = "LR ratio %.3f below 0.20" % s["LR_ratio"]

    json.dump(res, io.open(os.path.join(PAPER, "STANCE_TEST_r231.json"), "w",
                           encoding="utf-8"), indent=1)

    print("ankle convention: %r" % res["ankle_convention"].get("dofs"))
    print("usable control seeds: %d\n" % len(rows))
    if "summary" in res:
        s = res["summary"]
        print("  window            added N    baseline N     ratio    frac of cycle peak   mean d(ankle)")
        print("  LR  0-15%%       %9.3f  %11.2f  %8.3f  %14.3f  %+14.5f"
              % (s["LR_add_N"], s["LR_base_N"], s["LR_ratio"], s["LR_add_as_frac_of_peak"],
                 s["LR_mean_d_ankle"]))
        print("  ES  toe-off+15%% %9.3f  %11.2f  %8.3f  %14.3f  %+14.5f"
              % (s["ES_add_N"], s["ES_base_N"], s["ES_ratio"], s["ES_add_as_frac_of_peak"],
                 s["ES_mean_d_ankle"]))
        print("  cycle peak added force: %.3f N" % s["peak_add_N"])
        print("\n  per-bin added force (N), 20 bins of 5%% of cycle:")
        mb = np.mean([r["bins"]["add_N"] for r in rows], axis=0)
        mu = np.mean([r["bins"]["u"] for r in rows], axis=0)
        md = np.mean([r["bins"]["d_ankle"] for r in rows], axis=0)
        for k in range(NBIN):
            print("    %3d-%3d%%  add %8.3f   u %.4f   d(ankle) %+8.5f"
                  % (k * 5, (k + 1) * 5, mb[k], mu[k], md[k]))
    print("\nOUTCOME = %s" % res["OUTCOME"])
    print("  %s" % res["reason"])
    print("wrote STANCE_TEST_r231.json")


if __name__ == "__main__":
    main()
