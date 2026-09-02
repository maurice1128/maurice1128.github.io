#!/usr/bin/env python3
"""gen_speed_r89.py -- build and gate the registered walking-speed study. NO LAUNCH PATH.

*** THIS SCRIPT CANNOT LAUNCH ANYTHING. There is no --launch flag and no call to any launcher. ***
Launch is a separate decision after Tier 2 completes, and a build script that could start 60 runs by
a one-character typo is a hazard this project does not need.

REGISTERED BY: paper/PREREG_speed_r89.md. Where that document and this script disagree, THE
DOCUMENT DECIDES -- the same relation slope_analysis_r62.py has to PREREG_slope.md.

WHY A COMPANION. `gen_slope_r60.py` produced Tier 1 and `gen_slope_tier2_r87.py` produced Tier 2;
both are part of their corpora's provenance and neither is edited. This imports the first and reuses
its registered helpers unmodified.

WHAT IT CHECKS BEFORE IT WOULD BE SAFE TO LAUNCH:
  * REUSE (section 3): a generated v = 1.0 scenario must be byte-identical to the corresponding
    SG0_* scenario apart from signature_prefix. If anything else differs, the 1.0 arm is NOT
    reusable and the study is 90 runs, not 60 -- registered in advance so the larger number cannot
    be presented later as scope creep.
  * BUDGET: the six registered properties, read back from every generated file.
  * G5: tag collision against a results root that already holds 43 directories with ' (1)'.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import gen_slope_r60 as G60                                       # noqa: E402

SPEEDS = [1.0, 1.4, 1.8]                     # section 3; 1.8 subject to the section 5 gate
NEW_SPEEDS = [1.4, 1.8]                      # the 1.0 arm is reused if section 3 verifies
CONDS = [c for c in G60.CONDS
         if c[0] in ("DR2K000", "DR2K050", "DR2K075", "PAR20", "PAR40")]
SEEDS = list(range(101, 107))
OUT = os.path.join(HERE, "opt_speed_r89")


def tag_of(v, cond):
    """SPD14_DR2K050 style. The speed is in the tag so no cell can be mistaken for a slope cell."""
    return "SPD%02d_%s" % (round(v * 10), cond)


def set_min_velocity(txt, v):
    out, n = re.subn(r"min_velocity\s*=\s*[0-9.]+", "min_velocity = %.1f" % v, txt)
    if n != 1:
        raise RuntimeError("expected exactly one min_velocity line, found %d" % n)
    return out


def build(speeds):
    os.makedirs(OUT, exist_ok=True)
    made = []
    for v in speeds:
        for cond, _w, _kv, _n, _role in CONDS:
            base = os.path.join(G60.OPTDIR, "SG0_%s.scone" % cond)
            if not os.path.isfile(base):
                raise RuntimeError("missing level base scenario %s" % base)
            txt = set_min_velocity(open(base, encoding="utf-8", errors="ignore").read(), v)
            for seed in SEEDS:
                t2 = "%s_s%d" % (tag_of(v, cond), seed)
                s = re.sub(r"signature_prefix\s*=\s*\S+",
                           "signature_prefix = %s" % t2, txt, count=1)
                s = G60.GS.set_seed(s, seed)
                sp = os.path.join(OUT, t2 + ".scone")
                open(sp, "w", encoding="utf-8").write(s)
                made.append((t2, sp, v, cond, seed))
    return made


def verify_reuse(made):
    """Section 3, BY CONTENT. Is a generated v = 1.0 cell the SG0 cell apart from the prefix?"""
    print("\n" + "=" * 92)
    print("REUSE VERIFICATION (section 3) -- can the slope study's D = 0 cells serve as the v = 1.0 arm?")
    print("=" * 92)
    diffs, checked = [], 0
    for t2, sp, v, cond, seed in made:
        if v != 1.0:
            continue
        checked += 1
        sg0 = os.path.join(G60.OPTDIR, "SG0_%s_s%d.scone" % (cond, seed))
        if not os.path.isfile(sg0):
            diffs.append((t2, "no SG0 counterpart on disk"))
            continue
        a = open(sg0, encoding="utf-8", errors="ignore").read().split("\n")
        b = open(sp, encoding="utf-8", errors="ignore").read().split("\n")
        if len(a) != len(b):
            diffs.append((t2, "line count %d vs %d" % (len(a), len(b))))
            continue
        for i, (x, y) in enumerate(zip(a, b), 1):
            if x != y and "signature_prefix" not in x:
                diffs.append((t2, "line %d: %r vs %r" % (i, x.strip()[:48], y.strip()[:48])))
    print("  v = 1.0 cells compared against their SG0 counterparts : %d" % checked)
    if diffs:
        print("  *** DIFFERENCES BEYOND signature_prefix ***")
        for t2, d in diffs[:12]:
            print("    %-24s %s" % (t2, d))
        print("\n  REUSE VERDICT: NOT REUSABLE -- the study is 90 runs, not 60 (section 3).")
        return False
    print("  differences beyond signature_prefix                   : 0")
    print("  REUSE VERDICT: REUSABLE -- the 1.0 arm is the existing SG0 D = 0 cells;")
    print("                 the study is 60 new runs (5 conditions x 2 new speeds x 6 seeds).")
    return True


def assert_budget(made):
    print("\n" + "=" * 92)
    print("BUDGET ASSERTION -- the six registered properties, read back from every generated file")
    print("=" * 92)
    bad = []
    for t2, sp, v, cond, seed in made:
        s = open(sp, encoding="utf-8", errors="ignore").read()
        for k, ok in (("min_progress = 0", re.search(r"min_progress\s*=\s*0\b", s)),
                      ("max_generations = 90", re.search(r"max_generations\s*=\s*90\b", s)),
                      ("init_file", "ResultH0914Gait10.par" in s),
                      # The model is the level parent OF THAT CONDITION'S FAMILY, not BASE for
                      # all: PAR20/PAR40 carry weakened tib_ant and have their own level parents,
                      # already built by the slope study. This assertion was written as BASE-for-all
                      # and the gate caught it before the registration was hashed.
                      ("model %s" % G60.model_name(G60.family_of(cond), 0),
                       G60.model_name(G60.family_of(cond), 0) in s),
                      ("min_velocity = %.1f" % v,
                       re.search(r"min_velocity\s*=\s*%.1f\b" % v, s)),
                      ("no _resume.par", "_resume.par" not in s)):
            if not ok:
                bad.append((t2, k))
    print("  files checked : %d      assertions per file : 6" % len(made))
    if bad:
        for t2, k in bad[:20]:
            print("    *** %-26s FAILED %s" % (t2, k))
        raise RuntimeError("BUDGET ASSERTION FAILED on %d checks" % len(bad))
    print("  failures      : 0        budget verdict: PASS")


def main():
    if "--build" not in sys.argv:
        print(__doc__)
        return 2
    made = build(SPEEDS)
    print("built %d scenarios: %d conditions x %d speeds x %d seeds"
          % (len(made), len(CONDS), len(SPEEDS), len(SEEDS)))
    reusable = verify_reuse(made)
    assert_budget(made)
    launch_set = [(t, p) for t, p, v, _c, _s in made if v in NEW_SPEEDS] if reusable \
        else [(t, p) for t, p, _v, _c, _s in made]
    print("\n  runs this study would add: %d  (%s)"
          % (len(launch_set), "1.0 arm reused" if reusable else "1.0 arm NOT reusable"))
    G60.gate_collision(launch_set)
    print("\n" + "=" * 92)
    print("BUILT AND GATED. NOT LAUNCHED, AND THIS SCRIPT CANNOT LAUNCH.")
    print("  Tier 2 holds the cores. Launch is a separate decision, per PREREG_speed_r89.md section 8.")
    print("=" * 92)
    return 0


if __name__ == "__main__":
    sys.exit(main())
