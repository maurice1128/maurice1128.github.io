# -*- coding: utf-8 -*-
"""r213 STEP 1 -- is a FORCE-feedback magnitude anchor a step or a line?

Read-only. No simulation. Reads the six CONTROL cells (R151C_s101..106) only, exactly as
speed_dose_r200.py does, and reuses the REGISTERED dose formula from dose_r174.py unmodified
except for which normalised signal drives it:

    KV arm (registered, unchanged):  du = KV * max(0, ce_vel_norm)
    KF arm (this script):            du = KF * max(0, mtu_force_norm - F0)
    both:                            du = min(du, max(0, 1 - excitation))     <-- THE CLAMP
                                     dose_N = mean over window of sum_m du * Fmax[m]

⛔ WHAT THIS DOES AND DOES NOT SETTLE.
   It settles MAGNITUDE: which KF delivers the same newtons as the registered KV = 0.050.
   That is the SAME matching principle dose_r174.py used to set the weakness match at x0.892,
   so it is a registered precedent, not a new invention.
   ⛔ It does NOT settle TIMING. A velocity term is active only while the fibre lengthens; a force
   term is active whenever the muscle bears load. DEFECT #48's duty-cycle objection applies and is
   NOT addressed by dose-matching -- so this script MEASURES the duty cycle of each term and prints
   it beside the dose, rather than letting a matched mean imply matched provocation.
"""
import os, sys, glob, json
sys.path.insert(0, r"C:\Users\maurice\Desktop\spasticity_paper\scone")
import numpy as np
import sto_utils as S

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

RESULTS = r"C:\Users\maurice\Documents\SCONE\results"
DST = r"C:\Users\maurice\Desktop\spasticity_paper\paper\FORCE_DOSE_r213.json"
SEEDS = [101, 102, 103, 104, 105, 106]
SETTLE, T1 = 1.0, 13.58
FMAX = {"soleus_l": 3549.0, "gastroc_l": 2241.0}
KV_REG = 0.050
F0 = 0.0          # SCONE MuscleReflex force threshold; 0 unless declared. STATED, not assumed away.


def ctrl_dir(s):
    g = [d for d in glob.glob(os.path.join(RESULTS, "R151C_s%d.*" % s)) if os.path.isdir(d)]
    return sorted([d for d in g if os.path.exists(os.path.join(d, "history.txt"))])[0]


def cycles(cols, dat, t):
    grf, thr = S.grf_vertical(cols, dat, "l")
    idx = S.heel_strikes(t, grf, thresh=thr)
    c = [(idx[k], idx[k + 1]) for k in range(len(idx) - 1)
         if t[idx[k]] >= SETTLE and t[idx[k + 1]] <= T1]
    return c[:-1] if len(c) >= 2 else c


def load(s):
    d = ctrl_dir(s)
    sto = sorted(glob.glob(os.path.join(d, "*.par.sto")))[-1]
    cols, dat = S.load_sto(sto)
    t = np.asarray(S.col(cols, dat, "time"), dtype=float)
    cyc = cycles(cols, dat, t)
    a, b = cyc[0][0], cyc[-1][1]
    o = {"seed": s, "n_cycles": len(cyc), "sto": os.path.basename(sto), "sig": {}}
    for m in FMAX:
        o["sig"][m] = {
            "v": np.asarray(S.col(cols, dat, m + ".ce_vel_norm"), dtype=float)[a:b],
            "f": np.asarray(S.col(cols, dat, m + ".mtu_force_norm"), dtype=float)[a:b],
            "u": np.asarray(S.col(cols, dat, m + ".excitation"), dtype=float)[a:b]}
    return o


def dose(r, gain, mode):
    add = None
    for m in FMAX:
        sig = r["sig"][m]
        drive = np.maximum(0.0, sig["v"]) if mode == "V" else np.maximum(0.0, sig["f"] - F0)
        du = np.minimum(gain * drive, np.maximum(0.0, 1.0 - sig["u"]))
        term = du * FMAX[m]
        add = term if add is None else add + term
    return float(np.mean(add))


def duty(r, mode):
    """fraction of samples on which the term is ACTIVE at all, pooled over the two muscles"""
    on = tot = 0
    for m in FMAX:
        sig = r["sig"][m]
        drive = np.maximum(0.0, sig["v"]) if mode == "V" else np.maximum(0.0, sig["f"] - F0)
        on += int(np.count_nonzero(drive > 0)); tot += drive.size
    return on / float(tot)


rows = [load(s) for s in SEEDS]
print("=" * 92)
print("r213 STEP 1 -- FORCE-feedback magnitude anchor.  READ-ONLY, NO SIMULATION.")
print("=" * 92)
print("containers: 6 control cells R151C_s101..106, newest *.par.sto, window [%.2f, %.2f]"
      % (SETTLE, T1))
print("method    : dose_r174.py's formula, including the excitation clamp; F0 = %.3f\n" % F0)

dv = [dose(r, KV_REG, "V") for r in rows]
print("REGISTERED KV = %.3f delivered dose, per seed (N): %s" % (KV_REG, ", ".join("%.3f" % x for x in dv)))
print("  mean %.4f N\n" % np.mean(dv))

# solve for the KF that matches the mean delivered dose -- bisection, because the clamp is nonlinear
lo, hi = 0.0, 10.0
for _ in range(200):
    mid = 0.5 * (lo + hi)
    if np.mean([dose(r, mid, "F") for r in rows]) < np.mean(dv):
        lo = mid
    else:
        hi = mid
KF_STAR = 0.5 * (lo + hi)
df = [dose(r, KF_STAR, "F") for r in rows]
print("DOSE-MATCHED KF* = %.6f" % KF_STAR)
print("  delivered dose, per seed (N): %s" % ", ".join("%.3f" % x for x in df))
print("  mean %.4f N   (target %.4f N, residual %.2e)\n" % (np.mean(df), np.mean(dv),
                                                            np.mean(df) - np.mean(dv)))

print("⛔ DUTY CYCLE -- defect #48, and dose-matching does NOT address it:")
duty_v = float(np.mean([duty(r, "V") for r in rows]))
duty_f = float(np.mean([duty(r, "F") for r in rows]))
print("  velocity term active on %.1f %% of samples" % (100 * duty_v))
print("  force    term active on %.1f %% of samples" % (100 * duty_f))
print("  ratio %.2fx -- matched MEAN dose is delivered over %s temporal support\n"
      % (duty_f / duty_v if duty_v else float("nan"),
         "very different" if abs(duty_f - duty_v) > 0.1 else "similar"))

# ---------------------------------------------------------------------------------------------
# F0 is the ONE design lever that touches the duty cycle. SCONE ships MuscleReflex with F0 both
# absent (=0) and optimised (e.g. F0 = "~0.15<0,0.5>"). This measures how much of defect #48 a
# threshold can buy, so the choice is made against numbers instead of taste. NO ARM IS PROPOSED.
print("⚠ F0 SWEEP -- how much of the duty-cycle gap a force THRESHOLD can close (read-only):")
print("  %6s %10s %14s %12s" % ("F0", "duty %", "dose-matched KF*", "peak du ratio"))
sweep = []
for f0 in (0.0, 0.05, 0.10, 0.15, 0.20, 0.30, 0.40):
    globals()["F0"] = f0
    on = tot = 0
    for r in rows:
        for m in FMAX:
            drv = np.maximum(0.0, r["sig"][m]["f"] - f0)
            on += int(np.count_nonzero(drv > 0)); tot += drv.size
    dcy = on / float(tot)
    lo2, hi2 = 0.0, 1e4
    for _ in range(300):
        mid2 = 0.5 * (lo2 + hi2)
        if np.mean([dose(r, mid2, "F") for r in rows]) < np.mean(dv):
            lo2 = mid2
        else:
            hi2 = mid2
    k2 = 0.5 * (lo2 + hi2)
    pk = max(float(np.max(np.minimum(k2 * np.maximum(0.0, r["sig"][m]["f"] - f0),
                                     np.maximum(0.0, 1.0 - r["sig"][m]["u"]))))
             for r in rows for m in FMAX)
    sweep.append({"F0": f0, "duty": dcy, "KF_star": k2, "peak_du": pk})
    print("  %6.2f %9.1f %16.6f %12.4f" % (f0, 100 * dcy, k2, pk))
globals()["F0"] = 0.0
print("  velocity term, for comparison: duty %.1f %%\n" % (100 * duty_v))

json.dump({"label": "r213 step 1 -- magnitude anchor for a force-feedback arm. Read-only.",
           "F0_sweep": sweep,
           "method": "dose_r174.py formula with the registered excitation clamp",
           "F0": F0, "KV_registered": KV_REG, "KV_dose_N_per_seed": dv,
           "KV_dose_N_mean": float(np.mean(dv)), "KF_star": KF_STAR,
           "KF_dose_N_per_seed": df, "KF_dose_N_mean": float(np.mean(df)),
           "duty_velocity": duty_v, "duty_force": duty_f,
           "caveat": "dose-matching equalises MAGNITUDE only; defect #48's duty-cycle objection is "
                     "NOT addressed and the duty cycles are printed to show by how much"},
          open(DST, "w", encoding="utf-8", newline="\n"), indent=1)
print("deposited paper/FORCE_DOSE_r213.json")
