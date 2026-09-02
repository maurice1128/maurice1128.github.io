"""margins_r248.py -- round 248.

Answers two questions put by the council, from deposits already on disk.
Read-only: opens LADDER36_r228.json, ANKLE_LADDER_r235.json, VERIFY_F5_r231.json.
Recomputes nothing from .sto.

Q1. Per severity, how far does each arm's MEAN lie beyond the control band edge,
    on hip_flexion_LmR and on ankle_angle_LmR?  The band is the control seed
    range [min(C), max(C)] -- the definition CHANNELS_G2_r219.json uses.

Q2. Is the spastic lesion an order of magnitude larger than the weakness ladder?
"""
import io, json, os

PAPER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "paper")
SEV = ["W800", "W870", "W892", "W900", "W915", "W950"]
SCALE = {"W800": 0.800, "W870": 0.870, "W892": 0.892,
         "W900": 0.900, "W915": 0.915, "W950": 0.950}


def load(n):
    return json.load(io.open(os.path.join(PAPER, n), encoding="utf-8"))


def margin(mean, lo, hi):
    """Signed distance beyond the nearest band edge. Negative = inside the band."""
    if mean > hi:
        return mean - hi, "above"
    if mean < lo:
        return lo - mean, "below"
    return -min(hi - mean, mean - lo), "INSIDE"


def channel_block(per_seed, name):
    C = per_seed["C"]
    lo, hi = min(C), max(C)
    out = {"band": [lo, hi],
           "band_definition": "[min, max] over the 6 control seeds",
           "control_mean": sum(C) / len(C),
           "arms": {}}
    for arm in ["S"] + SEV:
        v = per_seed[arm]
        m = sum(v) / len(v)
        mg, side = margin(m, lo, hi)
        out["arms"][arm] = {"mean": m, "margin": mg, "side": side,
                            "clears_band": side != "INSIDE"}
    # Does the channel's margin track the weakness lesion's magnitude at all?
    # Severity scale ASCENDS 0.800..0.950 = lesion WEAKENS. A channel driven by the
    # weakness lesion must therefore have margin DESCENDING: Spearman rho = -1.
    mg = [out["arms"][k]["margin"] for k in SEV]
    n = len(SEV)
    rk = [sorted(mg).index(v) + 1 for v in mg]          # no ties in this data
    xk = list(range(1, n + 1))                           # scale is already sorted
    dbar = sum((a - b) ** 2 for a, b in zip(rk, xk))
    out["dose_response"] = {
        "severity_scale_ascending": [SCALE[k] for k in SEV],
        "margins_in_that_order": mg,
        "spearman_rho_margin_vs_scale": 1 - 6.0 * dbar / (n * (n * n - 1)),
        "expected_if_driven_by_the_weakness_lesion": -1.0,
        "strictly_monotone_decreasing": all(mg[i] > mg[i + 1] for i in range(n - 1)),
    }

    s = out["arms"]["S"]["margin"]
    wk = {k: out["arms"][k]["margin"] for k in SEV}
    cleared = {k: v for k, v in wk.items() if out["arms"][k]["clears_band"]}
    out["asymmetry"] = {
        "spastic_margin": s,
        "weak_margins": wk,
        "weak_arms_inside_band": [k for k in SEV if not out["arms"][k]["clears_band"]],
        "spastic_over_largest_weak": s / max(wk.values()),
        "spastic_over_smallest_cleared_weak": (s / min(cleared.values())) if cleared else None,
        "largest_weak_over_spastic": max(wk.values()) / s,
        "dominant_arm": "spastic" if s > max(wk.values()) else "weakness",
    }
    out["channel"] = name
    return out


def main():
    hip = load("LADDER36_r228.json")["per_seed_hip_flexion_LmR"]
    ank = load("ANKLE_LADDER_r235.json")["per_seed"]
    f5 = load("VERIFY_F5_r231.json")

    res = {
        "round": 248,
        "question": "band-edge margins per severity, and lesion-magnitude confound",
        "inputs": ["LADDER36_r228.json", "ANKLE_LADDER_r235.json", "VERIFY_F5_r231.json"],
        "recomputed_from_sto": False,
        "corpus_shape": {
            "weakness_severities": len(SEV),
            "spastic_conditions": 1,
            "spastic_kv": f5["kv"],
            "note": ("The weakness arm has a six-point severity ladder. The spastic arm is ONE "
                     "condition at KV=0.05, reused unchanged in every severity comparison; "
                     "LADDER36_r228.json carries a single constant spastic_max for all six."),
        },
        "hip_flexion_LmR": channel_block(hip, "hip_flexion_LmR"),
        "ankle_angle_LmR": channel_block(ank, "ankle_angle_LmR"),
    }

    # ---- Q2: lesion magnitude
    tib = f5["tib_ant_mean_force_N"]
    corr = f5["spastic_dose_corrected_V_N"]
    reg = f5["spastic_dose_as_registered_N"]
    lad = {}
    for k in SEV:
        removed = (1.0 - SCALE[k]) * tib
        lad[k] = {"scale": SCALE[k], "force_removed": removed,
                  "spastic_over_this_corrected": corr / removed,
                  "spastic_over_this_as_registered": reg / removed}
    res["lesion_magnitude"] = {
        "tib_ant_mean_force_N": tib,
        "spastic_dose_corrected": corr,
        "spastic_dose_as_registered": reg,
        "weakness_ladder": lad,
        "corrected_ratio_range": [min(v["spastic_over_this_corrected"] for v in lad.values()),
                                  max(v["spastic_over_this_corrected"] for v in lad.values())],
        "as_registered_ratio_range": [min(v["spastic_over_this_as_registered"] for v in lad.values()),
                                      max(v["spastic_over_this_as_registered"] for v in lad.values())],
        "units_caveat": (
            "Both quantities are dimensionally newtons, so the ratio is not a unit error. But they "
            "are not the same KIND of newton: the numerator is a NOMINAL COMMANDED force increment "
            "(a dimensionless excitation increment KV*V multiplied by Fmax), while the denominator "
            "is an ACHIEVED mean muscle force read from .sto. RESULTS_3d_r214.md section 9 withdraws "
            "the newton unit from ce_vel_norm-derived figures and forbids comparing them to force "
            "quantities outside that section; the corrected 136.266 is on the V scale, not the "
            "ce_vel_norm scale, so section 9's stated REASON does not reach it, but section 9's "
            "blanket prohibition textually does. The scope conflict is unresolved."),
        "what_survives": (
            "'No arm is dose-matched' survives: it needs only that the ratio corrected/tib_ant "
            "exceeds 1, which makes the required matching scale negative. The ORDER-OF-MAGNITUDE "
            "claim depends entirely on the measured factor 10 between V and ce_vel_norm: on the "
            "as-registered scale the spastic arm is 0.54x-2.17x the ladder, i.e. comparable."),
    }

    p = os.path.join(PAPER, "MARGINS_r248.json")
    with io.open(p, "w", encoding="utf-8", newline="\n") as f:
        json.dump(res, f, indent=1)
        f.write("\n")

    for ch in ["hip_flexion_LmR", "ankle_angle_LmR"]:
        b = res[ch]
        print("=== %s   band [%.6f, %.6f]" % (ch, b["band"][0], b["band"][1]))
        for arm in ["S"] + SEV:
            a = b["arms"][arm]
            print("   %-5s mean %+.6f   margin %+.6f  %s" % (arm, a["mean"], a["margin"], a["side"]))
        x = b["asymmetry"]
        print("   dominant=%s  S/maxW=%.2f  maxW/S=%.2f  inside_band=%s"
              % (x["dominant_arm"], x["spastic_over_largest_weak"],
                 x["largest_weak_over_spastic"], x["weak_arms_inside_band"]))
    m = res["lesion_magnitude"]
    print("=== lesion magnitude (corrected): %.2fx - %.2fx the ladder"
          % tuple(m["corrected_ratio_range"]))
    print("=== lesion magnitude (as registered): %.2fx - %.2fx"
          % tuple(m["as_registered_ratio_range"]))


if __name__ == "__main__":
    main()
