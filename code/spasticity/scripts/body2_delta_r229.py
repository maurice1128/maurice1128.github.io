# -*- coding: utf-8 -*-
"""Round 229 rev 6 -- WHAT EQUIVALENCE MARGIN CAN THIS DESIGN ACTUALLY EXCLUDE?

Decides whether the outcome set shrinks. Rev 5's rung 9 offered a body-specificity claim
("the 3D finding is a property of that body") gated on the Hodges-Lehmann CI upper bound
lying below the 3D shift. That is not what accepting a null requires. Accepting a null
requires excluding effects near ZERO; rev 5 excluded the 3D POINT ESTIMATE instead, which a
substantially attenuated but entirely real effect also satisfies. Three revisions have now
adjusted the interval when the instrument was wrong.

So: compute, BEFORE any data, the smallest equivalence margin delta a TOST on the HL shift
could exclude at the real arm size, with a variance prior from the 3D deposit. If no useful
delta is reachable, the body-specificity claim is DELETED from the outcome set rather than
listed and failed -- a design that cannot support a conclusion must not offer it, which is
how "we failed to detect" becomes "it is not there".

TOST at alpha = 0.05 concludes equivalence within +/-delta when the 90 percent CI lies
entirely inside (-delta, +delta). Reported under a TRUE ZERO effect: the most favourable
case for the claim.

Deposits paper/BODY2_DELTA_r229.json.
"""
import io
import os
import sys
import json
import hashlib

sys.path.insert(0, r"C:\Users\maurice\Desktop\spasticity_paper\scone")
import numpy as np

PAPER = r"C:\Users\maurice\Desktop\spasticity_paper\paper"
LADDER = os.path.join(PAPER, "LADDER36_r228.json")

N_PER_ARM = 16
N_SIM = 500
B_BOOT = 800
SEED = 229229
DELTA_3D = 2.5854


def sha256_of(p):
    return hashlib.sha256(io.open(p, "rb").read()).hexdigest()


def hl_boot_ci(sv, wv, rng, b=B_BOOT, lo=5.0, hi=95.0):
    """Vectorised percentile bootstrap CI for the Hodges-Lehmann shift."""
    n = len(sv)
    si = rng.integers(0, n, size=(b, n))
    wi = rng.integers(0, n, size=(b, n))
    sb = np.asarray(sv)[si]                      # (b, n)
    wb = np.asarray(wv)[wi]                      # (b, n)
    d = wb[:, None, :] - sb[:, :, None]          # (b, n, n)
    stat = np.median(d.reshape(b, -1), axis=1)
    return np.percentile(stat, lo), np.percentile(stat, hi)


def variance_prior():
    d = json.load(io.open(LADDER, encoding="utf-8"))
    ps = d["per_seed_hip_flexion_LmR"]
    sds = {k: float(np.std(v, ddof=1)) for k, v in ps.items()}
    arms = [k for k in ps if k != "C"]
    pooled = float(np.sqrt(np.mean([np.var(ps[k], ddof=1) for k in arms])))
    # THE CENTRAL CASE IS NOT THE POOLED SD. The real contrast is the SPASTIC arm against a
    # WEAK arm, and the spastic arm is much the more variable (S 0.587 vs weak 0.17-0.39).
    # Rev 6 gave BOTH simulated arms the pooled sigma, understating the effective spread.
    eff = float(np.mean([np.sqrt((np.var(ps["S"], ddof=1) + np.var(ps[k], ddof=1)) / 2.0)
                         for k in ("W870", "W892", "W915")]))
    return sds, pooled, eff


def run(sigma, shift, rng, n=N_PER_ARM, nsim=N_SIM):
    los = np.empty(nsim)
    his = np.empty(nsim)
    for i in range(nsim):
        sv = rng.normal(0.0, sigma, n)
        wv = rng.normal(shift, sigma, n)
        los[i], his[i] = hl_boot_ci(sv, wv, rng)
    return los, his


def main():
    rng = np.random.default_rng(SEED)
    sds, pooled, eff = variance_prior()

    res = {"rev": 6, "n_per_arm": N_PER_ARM, "n_sim": N_SIM, "b_bootstrap": B_BOOT,
           "seed": SEED, "delta_3d_hl_deg": DELTA_3D,
           "variance_prior_source": "LADDER36_r228.json per-arm within-arm SD",
           "per_arm_sd_3d_deg": sds, "pooled_lesioned_arm_sd_3d_deg": pooled,
           "effective_spastic_vs_weak_sd_3d_deg": eff,
           "effective_over_pooled_ratio": eff / pooled,
           "registered_delta_equiv_deg": 0.65,
           "n_per_arm_caveat": ("n = 16 is the PRE-Gate-B count. No .par.sto exists yet, so "
                                "the post-gate arm size is unmeasured and may be smaller; "
                                "every power figure here assumes zero attrition."),
           "method": ("TOST at alpha=0.05 concludes equivalence within +/-delta when the 90 "
                      "percent bootstrap CI lies inside (-delta,+delta); delta reported at "
                      "80 percent power under a TRUE ZERO effect"),
           "scenarios": []}

    for label, sigma in [("pooled lesioned-arm SD (rev 6 case, understated)", pooled),
                         ("CENTRAL: spastic-vs-weak effective SD", eff),
                         ("1.5x pooled", 1.5 * pooled),
                         ("2x pooled", 2.0 * pooled)]:
        lo0, hi0 = run(sigma, 0.0, rng)
        halfw = (hi0 - lo0) / 2.0
        d80 = float(np.percentile(np.maximum(np.abs(lo0), np.abs(hi0)), 80))
        lo1, hi1 = run(sigma, 0.25 * DELTA_3D, rng)
        sc = {"scenario": label, "sigma_deg": float(sigma),
              "median_90pct_CI_halfwidth_deg": float(np.median(halfw)),
              "delta_for_80pct_power_deg": d80,
              "delta_as_fraction_of_delta3d": d80 / DELTA_3D,
              "rev5_rung9_fires_on_true_zero": float(np.mean(hi0 < DELTA_3D)),
              "rev5_rung9_fires_on_quarter_magnitude_real_effect":
                  float(np.mean(hi1 < DELTA_3D)),
              "equiv_power_at_delta_0.65": float(np.mean((lo0 > -0.65) & (hi0 < 0.65)))}
        res["scenarios"].append(sc)

    res["script_sha256"] = sha256_of(os.path.abspath(__file__))
    out = os.path.join(PAPER, "BODY2_DELTA_r229.json")
    json.dump(res, io.open(out, "w", encoding="utf-8"), indent=1)

    print("3D within-arm SD (deg): " + "  ".join("%s %.3f" % (k, sds[k])
                                                 for k in sorted(sds)))
    print("pooled lesioned-arm SD: %.4f deg" % pooled)
    print("Delta_3D = %.4f deg;  n = %d per arm; %d sims x %d bootstrap\n"
          % (DELTA_3D, N_PER_ARM, N_SIM, B_BOOT))
    for s in res["scenarios"]:
        print("%-26s sigma %.3f" % (s["scenario"], s["sigma_deg"]))
        print("   median 90%% CI half-width          : %.3f deg"
              % s["median_90pct_CI_halfwidth_deg"])
        print("   smallest delta @80%% power         : %.3f deg  = %.2f x Delta_3D"
              % (s["delta_for_80pct_power_deg"], s["delta_as_fraction_of_delta3d"]))
        print("   rev5 rung 9 on TRUE ZERO          : %.1f%%"
              % (100 * s["rev5_rung9_fires_on_true_zero"]))
        print("   rev5 rung 9 on REAL quarter effect: %.1f%%"
              % (100 * s["rev5_rung9_fires_on_quarter_magnitude_real_effect"]))
        print("   EQUIV power at delta = 0.65       : %.3f"
              % s["equiv_power_at_delta_0.65"])
        print()
    print("wrote %s" % out)


if __name__ == "__main__":
    main()
