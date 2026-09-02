"""slap_disentangle_r297.py -- round 297. Does slap_LmR track SEVERITY or OUTCOME?

EXPLORATORY, UNREGISTERED, POST-HOC. Read-only, no simulation, nothing re-measured:
every value is read from SLAP_LMR_r296.json.

The problem it addresses. Across arms, severity and outcome are perfectly entangled --
KV 0.050 spastic all fall, KV 0.0125 spastic all complete -- so the sign flip between them
cannot be attributed. The WPF arm is the only one in the corpus containing BOTH fallers and
completers at the SAME dose, which makes two contrasts available that no cross-arm
comparison can supply:

  OUTCOME  at fixed severity : f = 0.05 completers vs f = 0.05 fallers
  SEVERITY at fixed outcome  : f = 0.05 fallers vs f = 0.10 vs f = 0.20 fallers

Also applies the baseline correction r296 lacked: the control arm's slap_LmR is not zero,
so every corrected figure is reported as raw minus the control mean.
"""
import io
import json
import os

PAPER = r"C:\Users\maurice\Desktop\spasticity_paper\paper"
# WPF cell index -> dose, from run_weakpf_r276.py: 3 doses x 6 seeds, in order
DOSE = {}
for i in range(18):
    DOSE["c%02d" % i] = [0.05, 0.10, 0.20][i // 6]


def mean(v):
    return sum(v) / len(v) if v else None


def main():
    d = json.load(io.open(os.path.join(PAPER, "SLAP_LMR_r296.json"), encoding="utf-8"))
    per = d["per_cell"]

    ctrl = [c["slap_LmR_raw"] for c in per["C"].values() if c.get("slap_LmR_raw") is not None]
    base = mean(ctrl)

    rows = []
    for cid, c in sorted(per["WPF"].items()):
        v = c.get("slap_LmR_raw")
        if v is None:
            continue
        rows.append({"cell": cid, "f": DOSE.get(cid), "t_end_s": c.get("t_end_s"),
                     "completes": bool(c.get("completes")),
                     "slap_LmR_raw": v, "slap_LmR_corrected": v - base,
                     "slap_l_raw": c.get("slap_l_raw"), "slap_r_raw": c.get("slap_r_raw")})

    # ---- contrast 1: OUTCOME at fixed severity
    out = {}
    for f in (0.05, 0.10, 0.20):
        sub = [r for r in rows if r["f"] == f]
        co = [r for r in sub if r["completes"]]
        fa = [r for r in sub if not r["completes"]]
        out["f=%.2f" % f] = {
            "n_completers": len(co), "n_fallers": len(fa),
            "completers_corrected": [r["slap_LmR_corrected"] for r in co],
            "fallers_corrected": [r["slap_LmR_corrected"] for r in fa],
            "completers_mean": mean([r["slap_LmR_corrected"] for r in co]),
            "fallers_mean": mean([r["slap_LmR_corrected"] for r in fa]),
            "both_present": bool(co and fa),
            "difference_of_means": (mean([r["slap_LmR_corrected"] for r in co])
                                    - mean([r["slap_LmR_corrected"] for r in fa]))
            if (co and fa) else None,
            "signs_differ": (bool(co and fa) and
                             (mean([r["slap_LmR_corrected"] for r in co]) > 0)
                             != (mean([r["slap_LmR_corrected"] for r in fa]) > 0)),
        }

    # ---- contrast 2: SEVERITY at fixed outcome (fallers only)
    sev = {}
    for f in (0.05, 0.10, 0.20):
        fa = [r for r in rows if r["f"] == f and not r["completes"]]
        sev["f=%.2f" % f] = {"n": len(fa),
                             "corrected": [r["slap_LmR_corrected"] for r in fa],
                             "mean": mean([r["slap_LmR_corrected"] for r in fa]),
                             "t_end": [r["t_end_s"] for r in fa]}
    sm = [sev["f=%.2f" % f]["mean"] for f in (0.05, 0.10, 0.20)
          if sev["f=%.2f" % f]["mean"] is not None]
    sev["_monotone_in_dose"] = (all(sm[i] > sm[i + 1] for i in range(len(sm) - 1))
                                or all(sm[i] < sm[i + 1] for i in range(len(sm) - 1))
                                ) if len(sm) > 2 else None
    sev["_range_across_doses"] = (max(sm) - min(sm)) if sm else None
    sev["_all_same_sign"] = (all(x > 0 for x in sm) or all(x < 0 for x in sm)) if sm else None

    # ---- the cross-arm sign flip, restated with the baseline correction applied
    arms = {}
    for a in ("C", "S", "S289", "W870", "W950"):
        if a not in per:
            continue
        v = [c["slap_LmR_raw"] for c in per[a].values()
             if c.get("slap_LmR_raw") is not None]
        arms[a] = {"n": len(v), "raw_mean": mean(v),
                   "corrected_mean": mean(v) - base if v else None,
                   "raw_range": [min(v), max(v)] if v else None}

    res = {"round": 297,
           "status": "EXPLORATORY, UNREGISTERED, POST-HOC. Read-only; every value read from "
                     "SLAP_LMR_r296.json. Generates a hypothesis; settles nothing.",
           "baseline_correction": {
               "control_slap_LmR_raw_mean": base,
               "control_range": [min(ctrl), max(ctrl)],
               "note": ("the model has a baseline left-right asymmetry. r296's LmR figures are "
                        "uncorrected. Every 'corrected' value here is raw minus this mean, and "
                        "the correction is stated rather than left implicit.")},
           "why_WPF": ("WPF is the only arm holding both fallers and completers at the same "
                       "dose, so it is the only place severity and outcome can be varied one "
                       "at a time without a new simulation."),
           "per_cell": rows,
           "contrast_1_OUTCOME_at_fixed_severity": out,
           "contrast_2_SEVERITY_at_fixed_outcome": sev,
           "arms_with_baseline_correction": arms}

    p = os.path.join(PAPER, "SLAP_DISENTANGLE_r297.json")
    io.open(p, "w", encoding="utf-8", newline="\n").write(json.dumps(res, indent=1) + "\n")

    print("baseline: control slap_LmR mean %+.4f deg/s (range %+.2f .. %+.2f)"
          % (base, min(ctrl), max(ctrl)))
    print("\nWPF cells (corrected = raw - baseline):")
    print("%-6s %5s %8s %10s %12s" % ("cell", "f", "t_end", "completes", "corrected"))
    for r in rows:
        print("%-6s %5.2f %8.2f %10s %+12.4f"
              % (r["cell"], r["f"], r["t_end_s"], r["completes"], r["slap_LmR_corrected"]))
    print("\nCONTRAST 1 -- OUTCOME at fixed severity")
    for k, v in out.items():
        if v["both_present"]:
            print("  %s  completers n=%d mean %+8.4f | fallers n=%d mean %+8.4f | diff %+8.4f | signs differ %s"
                  % (k, v["n_completers"], v["completers_mean"], v["n_fallers"],
                     v["fallers_mean"], v["difference_of_means"], v["signs_differ"]))
        else:
            print("  %s  n_completers=%d n_fallers=%d -- contrast not available"
                  % (k, v["n_completers"], v["n_fallers"]))
    print("\nCONTRAST 2 -- SEVERITY at fixed outcome (fallers only)")
    for f in (0.05, 0.10, 0.20):
        v = sev["f=%.2f" % f]
        print("  f=%.2f n=%d mean %s" % (f, v["n"],
              ("%+8.4f" % v["mean"]) if v["mean"] is not None else "-"))
    print("  monotone in dose: %s | range across doses: %s | all same sign: %s"
          % (sev["_monotone_in_dose"],
             ("%.4f" % sev["_range_across_doses"]) if sev["_range_across_doses"] else "-",
             sev["_all_same_sign"]))
    print("\nARMS, baseline-corrected:")
    for a, v in arms.items():
        print("  %-5s n=%2d raw %+8.4f -> corrected %+8.4f" % (a, v["n"], v["raw_mean"],
                                                               v["corrected_mean"]))


if __name__ == "__main__":
    main()
