# -*- coding: utf-8 -*-
"""Round 229 rev 5 -- WHICH normalised velocity does SCONE's MuscleReflex KV multiply?

This settles the question that revisions 1-3 hedged. It ships as a script because the three
figures previously quoted in the registration were computed ad hoc, were gastroc_l only, and
carried an unregistered denominator mask. A number that decides a design must come from a
hashed script.

METHOD. Spastic .sto files already contain the velocity reflex's own output, <m>.RV, beside
<m>.fiber_velocity_norm, in cells whose config.scone declares a fixed KV. With
allow_neg_V = 0 the reflex computes

    RV(t) = KV * max(0, V(t - delay))

for whichever normalised velocity V SCONE uses. So

    ratio = RV / (KV * max(0, fiber_velocity_norm))

is 1.0 if SCONE multiplies fiber_velocity_norm, and 0.1 if it multiplies a channel that is
0.1 x fiber_velocity_norm (which is what ce_vel_norm is: measured on the 3D corpus, where
both names coexist, ce_vel_norm = 0.1000 * fiber_velocity_norm, corr 1.000000).

THE ANSWER IS REPORTED AS A SPREAD ACROSS DEFENSIBLE VARIANTS, not as a point estimate,
because the ratio depends on three analyst choices -- muscle, delay lag, and how much of the
low-amplitude tail is masked out -- and none of those was registered in advance. The
discrimination does not depend on resolving them: every variant is far from both 0.1 and 10.

Deposits paper/BODY2_CONVENTION_r229.json and records its own sha256 there.
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

RESULTS = r"C:\Users\maurice\Documents\SCONE\results"
PAPER = r"C:\Users\maurice\Desktop\spasticity_paper\paper"

# Cells with a declared, fixed KV in a SpasticL block. None is an SG* cell; none enters the
# replication study.
CELLS = [("BSPAS005_s1.H0914M.GH2010.R4.S10W.D10.I.R1", 0.050),
         ("BSPAS01_s1.H0914M.GH2010.R4.S10W.D10.I.R1", 0.100),
         ("CMS020_s1.H0914M.GH2010.R4.S10W.D10.I.R1", 0.020),
         ("CMS030_s1.H0914M.GH2010.R4.S10W.D10.I.R1", 0.030),
         ("SPAS005.H0914M.GH2010.R4.S10W.D10.I", 0.050)]
MUSCLES = ["soleus_l", "gastroc_l"]
LAGS = [1, 2, 3]                 # 0.010 / 0.020 / 0.030 s at dt = 0.010
MASKS = [0.0, 0.05, 0.20, 0.50]  # fraction of peak predicted signal below which we ignore


def sha256_of(path):
    return hashlib.sha256(io.open(path, "rb").read()).hexdigest()


def declared_kv(d):
    p = os.path.join(RESULTS, d, "config.scone")
    if not os.path.exists(p):
        return None
    t = io.open(p, encoding="utf-8", errors="replace").read()
    i = t.find("SpasticL")
    if i < 0:
        return None
    v = [float(x) for x in re.findall(r"KV\s*=\s*([\d.]+)", t[i:i + 900])]
    return v[0] if v and len(set(v)) == 1 else None


def variants():
    rows = []
    for d, kv_expect in CELLS:
        kv = declared_kv(d)
        if kv is None:
            rows.append({"cell": d.split(".")[0], "error": "no fixed KV in SpasticL"})
            continue
        if abs(kv - kv_expect) > 1e-9:
            raise SystemExit("%s: config KV %r != expected %r" % (d, kv, kv_expect))
        stos = sorted(glob.glob(os.path.join(RESULTS, d, "*.sto")))
        if not stos:
            rows.append({"cell": d.split(".")[0], "error": "no .sto"})
            continue
        cols, dat = S.load_sto(stos[-1])
        for m in MUSCLES:
            if (m + ".RV") not in cols or (m + ".fiber_velocity_norm") not in cols:
                continue
            rv_all = np.asarray(dat[:, cols.index(m + ".RV")], dtype=float)
            v_all = np.asarray(dat[:, cols.index(m + ".fiber_velocity_norm")], dtype=float)
            for lag in LAGS:
                rv = rv_all[lag:]
                pred = kv * np.maximum(0.0, v_all[:len(v_all) - lag])
                if pred.max() <= 0:
                    continue
                for mask in MASKS:
                    k = (pred > mask * pred.max()) & (pred > 1e-12) & (rv > 0)
                    if k.sum() < 30:
                        continue
                    r = rv[k] / pred[k]
                    rows.append({"cell": d.split(".")[0], "kv": kv, "muscle": m,
                                 "lag_samples": lag, "mask_frac_of_peak": mask,
                                 "n_samples": int(k.sum()),
                                 "median_ratio": float(np.median(r)),
                                 "q1": float(np.percentile(r, 25)),
                                 "q3": float(np.percentile(r, 75))})
    return rows


def main():
    rows = variants()
    good = [r for r in rows if "median_ratio" in r]
    if not good:
        raise SystemExit("no usable variants")
    med = [r["median_ratio"] for r in good]

    # Two DIFFERENT quantities, which rev 5 conflated under one mislabelled field.
    #
    #   min_separation(h) = the WEAKEST evidence any variant gives against h. Meaningful for
    #                       a hypothesis OUTSIDE the observed range: for h = 0.1 every
    #                       variant sits above it, so the minimum is the closest approach.
    #   worst_fit(h)      = how badly the WORST-FITTING variant agrees with h. This is the
    #                       right quantity for a hypothesis INSIDE the range, such as 1.0.
    #
    # Rev 5 used min() for both and reported "worst-case discrimination vs 1.0 = 1.00x",
    # which is the BEST-fitting variant, not the worst. The honest contrast is
    # worst_fit(1.0) = 2.08x against min_separation(0.1) = 4.80x -- a factor of about 2.3,
    # not the near-infinite preference the mislabelled field implied.
    def min_separation(h):
        return min(max(x / h, h / x) for x in med)

    def worst_fit(h):
        return max(max(x / h, h / x) for x in med)

    res = {"rev": 5,
           "question": "which normalised velocity does SCONE MuscleReflex KV multiply",
           "estimator": "median over samples of RV / (KV * max(0, fiber_velocity_norm))",
           "hypotheses": {"fiber_velocity_norm": 1.0, "ce_vel_norm (0.1x)": 0.1,
                          "ten_times": 10.0},
           "analyst_choices_not_preregistered": ["muscle", "delay lag", "amplitude mask"],
           "n_variants": len(good),
           "median_ratio_min": float(min(med)), "median_ratio_max": float(max(med)),
           "median_ratio_median": float(np.median(med)),
           "worst_fit_vs_1.0": worst_fit(1.0),
           "min_separation_vs_0.1": min_separation(0.1),
           "min_separation_vs_10": min_separation(10.0),
           "field_note": ("worst_fit is the worst-FITTING variant's distance from a "
                          "hypothesis inside the observed range; min_separation is the "
                          "weakest evidence any variant gives against a hypothesis outside "
                          "it. Rev 5 reported min() for both and mislabelled it worst-case."),
           "empty_mask_levels": sorted(set(MASKS) - set(r.get("mask_frac_of_peak")
                                                        for r in good)),
           "variants": rows,
           "script": os.path.basename(__file__),
           "script_sha256": sha256_of(os.path.abspath(__file__))}
    out = os.path.join(PAPER, "BODY2_CONVENTION_r229.json")
    json.dump(res, io.open(out, "w", encoding="utf-8"), indent=1)

    print("variants computed: %d" % len(good))
    print("median ratio across variants: min %.4f  median %.4f  max %.4f"
          % (min(med), np.median(med), max(med)))
    print("worst-FITTING variant vs 1.0      : %.2fx  (how badly the worst variant fits)"
          % worst_fit(1.0))
    print("min separation vs 0.1             : %.2fx  (weakest evidence against 0.1)"
          % min_separation(0.1))
    print("min separation vs 10              : %.2fx" % min_separation(10.0))
    empty = sorted(set(MASKS) - set(r.get("mask_frac_of_peak") for r in good))
    if empty:
        print("mask levels that produced NO usable variant: %r" % empty)
    by_m = {}
    for r in good:
        by_m.setdefault(r["muscle"], []).append(r["median_ratio"])
    for m, v in sorted(by_m.items()):
        print("   %-10s n=%2d  [%.3f, %.3f]" % (m, len(v), min(v), max(v)))
    print("wrote %s" % out)


if __name__ == "__main__":
    main()
