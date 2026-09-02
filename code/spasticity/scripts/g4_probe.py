"""GATE G4 -- the -5 degree convergence probe, run on ONE control cell.

PREREG_slope.md section 7.1 G4:
    "-5 deg convergence probe: does the control cell at D = 5 yield >= 2 complete gait cycles
     under `cycle_features`?  if no, the -5 deg tier is reported NOT ATTAINABLE at S10W from a
     cold start and the design reduces to {0, 2}."

Nothing here is a fresh judgement: the `.par` is chosen by the registered
`sto_utils.select_registered_par` (minimum fitness asserted to be maximum generation), replayed
by the registered `replay_all.replay_registered` into an ISOLATED directory using the run's OWN
archived `config.scone`, and the feature is the registered
`sto_utils.cycle_features(path, side="l", settle=1.0)`.

Usage:  python g4_probe.py <run_dir>
"""
import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import replay_all                      # noqa: E402
import sto_utils                       # noqa: E402

RES = r"C:\Users\maurice\Documents\SCONE\results"


def stopping_readback(run_dir):
    """Section 7.3 item 5 -- from the run's OWN artifacts, never from the launcher's copy."""
    out = {}
    cfg = os.path.join(run_dir, "config.scone")
    txt = open(cfg, encoding="utf-8", errors="ignore").read()
    for key in ("min_progress", "max_generations", "random_seed", "min_velocity",
                "init_file", "signature_prefix", "model_file"):
        m = re.findall(r"^[ \t]*%s[ \t]*=[ \t]*(\S+)[ \t]*$" % key, txt, re.M)
        out[key] = m[0] if len(m) == 1 else m
    hist = os.path.join(run_dir, "history.txt")
    rows = [ln for ln in open(hist, encoding="utf-8", errors="ignore").read().splitlines()
            if ln.strip()]
    body = rows[1:]
    out["history_rows"] = len(body)
    out["terminal_generation_index"] = int(body[-1].split("\t")[0]) if body else None
    out["best_fitness_overall"] = min(float(r.split("\t")[1]) for r in body) if body else None
    out["final_row"] = body[-1] if body else None
    # gravity of the model the run itself archived
    mf = out.get("model_file")
    gp = os.path.join(run_dir, mf) if isinstance(mf, str) else None
    if gp and os.path.exists(gp):
        g = re.findall(r"<gravity>([^<]*)</gravity>",
                       open(gp, encoding="utf-8", errors="ignore").read())
        out["archived_model_gravity"] = g[0] if len(g) == 1 else g
    return out


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    if not args:
        cand = sorted(glob.glob(os.path.join(RES, "SG5_DR2K000_s101*")))
        if len(cand) != 1:
            print("expected exactly 1 SG5_DR2K000_s101* dir, found %d: %s" % (len(cand), cand))
            return 2
        run_dir = cand[0]
    else:
        run_dir = args[0]

    print("=" * 92)
    print("GATE G4 -- -5 DEGREE FEASIBILITY PROBE (control cell, cold start, S10W)")
    print("=" * 92)
    print("run_dir : %s" % run_dir)

    rb = stopping_readback(run_dir)
    print("\n-- stopping-rule readback from the run's OWN archived artifacts (section 7.3.5) --")
    for k in ("signature_prefix", "random_seed", "init_file", "min_progress", "max_generations",
              "min_velocity", "model_file", "archived_model_gravity"):
        print("   %-26s %s" % (k, rb.get(k)))
    print("   %-26s %s" % ("history rows", rb["history_rows"]))
    print("   %-26s %s   (registered terminal index = 89)"
          % ("terminal generation index", rb["terminal_generation_index"]))
    print("   %-26s %.4f" % ("best fitness over run", rb["best_fitness_overall"]))

    print("\n-- registered .par selection (section 1.2 / 7.3.7) --")
    try:
        sel = sto_utils.select_registered_par(run_dir)
        print("   par      : %s" % os.path.basename(sel["par"]))
        print("   gen      : %s   max_gen: %s   n_par: %s"
              % (sel["gen"], sel["max_gen"], sel["n_par"]))
        print("   fitness  : %s" % sel["fitness"])
        print("   assertion: minimum-fitness .par == maximum-generation .par  -> HELD")
    except Exception as e:                                        # noqa: BLE001
        print("   *** RegisteredSelectionError -> exclusion E5: %r" % e)
        json.dump({"gate": "G4", "status": "E5_SELECTION", "error": repr(e), "readback": rb},
                  open(os.path.join(HERE, "G4_PROBE.json"), "w"), indent=1, default=str)
        return 1

    print("\n-- registered replay into an isolated directory (section 1.2) --")
    rec = replay_all.replay_registered(run_dir)
    print("   status   : %s" % rec["status"])
    print("   work     : %s" % rec.get("work"))
    print("   cmd      : %s" % rec.get("cmd"))
    print("   cfg sha  : %s" % rec.get("config_sha256"))
    if rec["status"] != "ok":
        print("   *** replay did not yield exactly one .sto -> exclusion E5 ***")
        print("   detail: %s" % rec.get("error") or rec.get("sto_candidates"))
        json.dump({"gate": "G4", "status": rec["status"], "replay": rec, "readback": rb},
                  open(os.path.join(HERE, "G4_PROBE.json"), "w"), indent=1, default=str)
        return 1
    print("   sto      : %s" % os.path.basename(rec["sto"]))
    print("   sto sha  : %s" % rec.get("sto_sha256"))

    print("\n-- registered feature extraction: cycle_features(side='l', settle=1.0) --")
    feat = sto_utils.cycle_features(rec["sto"], side="l", settle=1.0)
    if feat is None:
        print("   cycle_features returned None -> FEWER THAN 2 COMPLETE CYCLES")
        verdict = "FAIL"
    else:
        for k in sorted(feat):
            v = feat[k]
            print("   %-20s %s" % (k, ("%.4f" % v) if isinstance(v, float) else v))
        nc = feat.get("n_cycles")
        verdict = "PASS" if (nc is not None and nc >= 2) else "FAIL"

    print("\n" + "=" * 92)
    print("G4 VERDICT: %s" % verdict)
    if verdict == "PASS":
        print("  The -5 degree control cell converges from a cold start at S10W and yields")
        print("  >= 2 complete GRF-delimited gait cycles. The -5 degree tier IS ATTAINABLE.")
    else:
        print("  The -5 degree tier is NOT ATTAINABLE at S10W from a cold start.")
        print("  Registered consequence (section 7.1 G4 fallback): the design reduces to {0, 2}")
        print("  and the required interaction rises from 0.4450 to 1.1124 deg/deg.")
        print("  NO SUBSTITUTE GRADE IS INTRODUCED.")
    print("=" * 92)

    json.dump({"gate": "G4", "verdict": verdict, "run_dir": run_dir, "readback": rb,
               "selection": sel, "replay": rec, "features": feat},
              open(os.path.join(HERE, "G4_PROBE.json"), "w"), indent=1, default=str)
    print("\nwrote %s" % os.path.join(HERE, "G4_PROBE.json"))
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
