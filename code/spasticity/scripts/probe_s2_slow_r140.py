"""S2 -- the slow feasibility probe registered in PREREG_speed_AMEND1_r137.md section 4. ONE cell.

WHAT IT IS. The amendment registers a slow arm at `min_velocity = 0.6` and gates it behind S2:
**DR2K000 at v = 0.6, seed 101, run FIRST AND ALONE**, with four clauses. If S2 fails the slow arm
is not launched, the design reverts to the parent's {1.0, 1.4, 1.8}, and the reversion is reported
as SLOW ARM NOT ATTAINABLE rather than as a design choice.

WHY A COMPANION AND NOT AN EDIT. `gen_speed_r89.py` section 8 of the amendment states the generator
change is REQUIRED and NOT MADE, and the generator is left byte-identical. It does not need editing:
`gen_speed_r89.build(speeds)` already takes the speed list as an argument, so `build([0.6])` produces
the 0.6 scenarios using the registered helpers unmodified -- the same relation `gen_slope_tier2_r87`
has to `gen_slope_r60`. Nothing registered is rewritten by this file.

WHY IT HAS ITS OWN LAUNCH CALL. `gen_slope_r60._popen` hard-codes `OPTDIR = opt_slope_r60`; the speed
scenarios live in `opt_speed_r89`. The subprocess call here is byte-for-byte the same shape --
`sconecmd -o <scenario> -l 2`, `CREATE_NO_WINDOW | BELOW_NORMAL_PRIORITY_CLASS`, cwd at the scenario
directory -- so our cell still yields to the user's own work on contention.

THE FOUR CLAUSES, verbatim from the amendment section 4:
  1  >= 2 complete GRF-delimited gait cycles under `cycle_features`            PASS/FAIL
  2  achieved forward pelvis velocity within [0.55, 0.75] m/s, settle 1.0      PASS/FAIL -- A BAND
  3  terminal best fitness within one order of magnitude of the v = 1.0 cell   PASS/FAIL
  4  peak `fiber_velocity_norm` against the v = 1.0 DR2K000 mean of 2.1121     REPORTED, not PASS/FAIL

Clause 2 is a band and not a `>=` because a floor of 0.6 is satisfied by walking at 1.0: a one-sided
test would pass an arm that never went slow, which is the failure this gate exists for.

MODES. --build writes scenarios and launches nothing. --launch starts the single probe.
--evaluate scores the four clauses. Default prints this docstring and does nothing.
"""
import glob
import json
import os
import subprocess
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import gen_speed_r89 as GS   # noqa: E402  -- imported, never modified
import gen_slope_r60 as G60  # noqa: E402
import sto_utils            # noqa: E402

SLOW = 0.6
PROBE_COND = "DR2K000"
PROBE_SEED = 101
TAG = "%s_s%d" % (GS.tag_of(SLOW, PROBE_COND), PROBE_SEED)     # SPD06_DR2K000_s101
BAND = (0.55, 0.75)
FVN_REF_V10 = 2.1121                    # amendment section 2(c), DR2K000 at v = 1.0
RESULTS = r"C:\Users\maurice\Documents\SCONE\results"
OUT_JSON = os.path.abspath(os.path.join(HERE, "..", "paper", "S2_PROBE_r140.json"))


def live_sconecmd():
    """tasklist, never `ps aux`. Fails CLOSED: an unknown count must not permit a launch."""
    try:
        p = subprocess.run(["tasklist", "/FI", "IMAGENAME eq sconecmd.exe", "/NH"],
                           capture_output=True, timeout=60)
        return sum(1 for ln in p.stdout.decode("utf8", "replace").splitlines()
                   if "sconecmd" in ln.lower())
    except Exception as e:
        print("tasklist failed (%s) -- refusing to launch blind" % e)
        return 10 ** 6


def result_dir(tag):
    hits = [d for d in glob.glob(os.path.join(RESULTS, tag + ".*")) if os.path.isdir(d)]
    return sorted(hits)[-1] if hits else None


def do_build():
    made = GS.build([SLOW])
    print("built %d scenarios at v = %.1f (all 5 conditions x 6 seeds; ONLY %s is probed)"
          % (len(made), SLOW, TAG))
    path = os.path.join(GS.OUT, TAG + ".scone")
    if not os.path.isfile(path):
        raise RuntimeError("probe scenario not written: %s" % path)
    s = open(path, encoding="utf-8", errors="ignore").read()
    import re
    checks = [("min_velocity = 0.6", re.search(r"min_velocity\s*=\s*0\.6\b", s)),
              ("min_progress = 0", re.search(r"min_progress\s*=\s*0\b", s)),
              ("max_generations = 90", re.search(r"max_generations\s*=\s*90\b", s)),
              ("init_file ResultH0914Gait10.par", "ResultH0914Gait10.par" in s),
              ("no _resume.par", "_resume.par" not in s),
              ("signature_prefix = " + TAG, ("signature_prefix = %s" % TAG) in s)]
    for k, ok in checks:
        print("   %-38s %s" % (k, "OK" if ok else "*** FAILED ***"))
    if not all(ok for _, ok in checks):
        raise RuntimeError("probe scenario failed its own budget read-back")
    if result_dir(TAG):
        raise RuntimeError("a result directory for %s already exists -- refusing (G5)" % TAG)
    print("   collision check                        OK (no existing result dir)")
    return path


def do_launch():
    path = os.path.join(GS.OUT, TAG + ".scone")
    if not os.path.isfile(path):
        raise RuntimeError("run --build first")
    if result_dir(TAG):
        raise RuntimeError("result dir already exists -- refusing")
    n = live_sconecmd()
    if n != 0:
        raise RuntimeError("S2 runs FIRST AND ALONE; %d sconecmd already live" % n)
    lg = open(os.path.join(G60.LOGDIR, "log_%s.txt" % TAG), "w")
    flags = (getattr(subprocess, "CREATE_NO_WINDOW", 0)
             | getattr(subprocess, "BELOW_NORMAL_PRIORITY_CLASS", 0))
    pr = subprocess.Popen([G60.SCONECMD, "-o", path, "-l", "2"], cwd=GS.OUT,
                          stdout=lg, stderr=subprocess.STDOUT, creationflags=flags)
    print("launched %s  pid=%d  (alone, BELOW_NORMAL)" % (TAG, pr.pid))
    return pr.pid


def _best_fitness(d):
    h = os.path.join(d, "history.txt")
    if not os.path.isfile(h):
        return None, 0
    rows = [ln.split() for ln in open(h, encoding="utf-8", errors="ignore").read().splitlines()[1:]]
    vals = []
    for r in rows:
        try:
            vals.append(float(r[1]))
        except (IndexError, ValueError):
            pass
    return (min(vals) if vals else None), len(rows)


def do_evaluate():
    d = result_dir(TAG)
    if d is None:
        print("no result directory for %s yet" % TAG)
        return 1
    sto = [s for s in glob.glob(os.path.join(d, "*.sto")) if os.path.getsize(s) > 1000]
    rec = {"tag": TAG, "result_dir": d, "band": list(BAND), "fvn_ref_v10": FVN_REF_V10}

    # ------------------------------------------------------------------ r142 REPAIR (defect D1)
    # The first version of this file wrote every clause as `x is not None and <test>`, which
    # collapses "I could not measure this" into FAIL. It did exactly that on 2026-08-08: no `.sto`
    # existed, clauses 1 and 2 reported FAIL, and the verdict SLOW ARM NOT ATTAINABLE would have
    # closed the last live route on a gap in this script rather than on a property of the arm.
    # Supplying the `.sto` made the question measurable and left the reporting defect intact --
    # a workaround, not a repair, which is what the watchdog found three days later.
    #
    # A clause is now THREE-STATE. UNEVALUABLE is not FAIL and it never contributes to a verdict.
    PASS, FAIL, UNEVAL = "PASS", "FAIL", "UNEVALUABLE"

    def clause(measured, test):
        """UNEVALUABLE if the quantity is missing; otherwise the test decides."""
        if measured is None:
            return UNEVAL
        return PASS if test(measured) else FAIL

    if not sto:
        rec["verdict"] = "UNEVALUABLE -- no .sto in the result dir; replay the best .par first"
        print("UNEVALUABLE: %s has no .sto. `sconecmd -e <NNNN_*.par>` in that directory first.\n"
              "This is NOT a failure of the slow arm and must not be reported as one." % d)
        json.dump(rec, open(OUT_JSON, "w"), indent=1)
        return 2

    # clause 1
    cf = sto_utils.cycle_features(sto[0], side="l", settle=1.0)
    n_cyc = cf.get("n_cycles") if cf else None
    s1 = clause(n_cyc, lambda n: n >= 2)
    c1 = s1 == PASS
    rec["clause1_cycles"] = {"state": s1, "n_cycles": n_cyc}

    # clause 2 -- achieved forward pelvis velocity, settle 1.0, THE BAND
    v_ach = None
    if sto:
        cols, dat = sto_utils.load_sto(sto[0])
        t = dat[:, 0]
        px = sto_utils.col(cols, dat, "pelvis_tx")
        if px is not None:
            m = t >= 1.0
            if m.sum() > 1:
                v_ach = float((px[m][-1] - px[m][0]) / (t[m][-1] - t[m][0]))
    s2 = clause(v_ach, lambda v: BAND[0] <= v <= BAND[1])
    c2 = s2 == PASS
    rec["clause2_velocity"] = {"state": s2, "achieved_m_s": v_ach}

    # clause 3 -- terminal best fitness within one order of magnitude of the v = 1.0 cell
    f_slow, ngen = _best_fitness(d)
    ref_dir = result_dir("SG0_%s_s%d" % (PROBE_COND, PROBE_SEED))
    f_ref, _ = _best_fitness(ref_dir) if ref_dir else (None, 0)
    ratio = (f_slow / f_ref) if (f_slow and f_ref) else None
    s3 = clause(ratio, lambda r: 0.1 <= r <= 10.0)
    c3 = s3 == PASS
    rec["clause3_fitness"] = {"state": s3, "slow": f_slow, "v10_ref": f_ref,
                              "ratio": ratio, "ref_dir": ref_dir, "generations": ngen}

    # clause 4 -- REPORTED, not pass/fail
    fvn = None
    if sto:
        cols, dat = sto_utils.load_sto(sto[0])
        names = [c for c in cols if "fiber_velocity" in c.lower() and c.lower().endswith("_l")]
        if names:
            vals = [np.max(np.abs(sto_utils.col(cols, dat, n))) for n in names]
            fvn = float(np.max(vals))
    # r142 REPAIR (defect D3). Clause 4 is REPORTED, not PASS/FAIL -- the registration is explicit
    # and that is not changed here. But r137 calls it "the quantity a future amendment needs", so a
    # null is not a cosmetic gap: it is the mechanism quantity the slow arm exists to supply. The
    # first version printed `n/a` and issued a verdict anyway. That was benign ONLY because clause 2
    # failed independently; had clause 2 passed, the arm would have been declared ATTAINABLE with
    # the registered mechanism quantity silently absent. A missing clause 4 can no longer be quoted
    # as a clean PASS -- it does not gate, but it MUST appear in the verdict string.
    s4 = "REPORTED" if fvn is not None else UNEVAL
    rec["clause4_fvn_reported"] = {"state": s4, "peak": fvn,
                                   "ratio_vs_v10": (fvn / FVN_REF_V10) if fvn else None}

    gated = [s1, s2, s3]
    if UNEVAL in gated:
        which = [n for n, s in zip((1, 2, 3), gated) if s == UNEVAL]
        verdict = ("UNEVALUABLE -- clause(s) %s could not be measured. NOT a failure of the slow "
                   "arm and must not be reported as one." % which)
    elif all(s == PASS for s in gated):
        verdict = "PASS"
        if s4 == UNEVAL:
            verdict += (" -- BUT clause 4 (peak fiber_velocity_norm) IS UNMEASURED. The registered "
                        "mechanism quantity is absent; this PASS may not be quoted without it.")
    else:
        verdict = "FAIL -> SLOW ARM NOT ATTAINABLE"
    rec["verdict"] = verdict
    rec["clause_states"] = {"1": s1, "2": s2, "3": s3, "4": s4}

    print("=" * 84)
    print("S2 SLOW FEASIBILITY PROBE -- PREREG_speed_AMEND1_r137.md section 4")
    print("=" * 84)
    print("  cell        : %s   (%s at min_velocity = %.1f, seed %d)"
          % (TAG, PROBE_COND, SLOW, PROBE_SEED))
    print("  1 cycles>=2 : %-11s  n_cycles = %s" % (s1, rec["clause1_cycles"]["n_cycles"]))
    print("  2 band      : %-11s  achieved = %s m/s   band [%.2f, %.2f]"
          % (s2, ("%.4f" % v_ach) if v_ach is not None else "n/a", *BAND))
    print("  3 fitness   : %-11s  slow = %s  v1.0 = %s  ratio = %s"
          % (s3, f_slow, f_ref, ("%.3f" % ratio) if ratio else "n/a"))
    print("  4 fvn       : %-11s  peak = %s  vs v1.0 mean %.4f -> ratio %s"
          % (s4, ("%.4f" % fvn) if fvn else "n/a", FVN_REF_V10,
             ("%.3f" % rec["clause4_fvn_reported"]["ratio_vs_v10"])
             if rec["clause4_fvn_reported"]["ratio_vs_v10"] else "n/a"))
    print("\n  VERDICT: %s" % verdict)
    json.dump(rec, open(OUT_JSON, "w"), indent=1)
    print("  wrote %s" % OUT_JSON)
    return 0


def main():
    if "--build" in sys.argv:
        do_build()
        if "--launch" in sys.argv:
            do_launch()
        return 0
    if "--launch" in sys.argv:
        do_launch()
        return 0
    if "--evaluate" in sys.argv:
        return do_evaluate()
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())
