#!/usr/bin/env python3
"""gen_slope_tier2_r87.py -- the registered Tier 2 escalation, as a COMPANION.

WHY THIS IS A SEPARATE FILE AND NOT AN EDIT.
`gen_slope_r60.py` produced the 114-run Tier-1 corpus. Its behaviour is part of that corpus's
provenance, and a corpus whose generator changed after the fact cannot be audited against the
generator that made it. This file therefore IMPORTS that module and reuses its registered
functions unmodified; it overrides only the seed range and the cell list, which is exactly what
the registration escalates.

WHAT THE REGISTRATION SAYS THIS IS (PREREG_slope.md section 6.2c and 5.77-5.78):
  * the 12 PRIMARY cells only -- DR2K050, DR2K075 (spastic) and PAR20, PAR40 (weak), at D = 0, 2, 5;
  * random_seed 107..116, ten per cell, 120 runs;
  * control and manipulation-check cells stay exactly as they are and are NOT extended.

WHAT IT REUSES RATHER THAN REBUILDS. The BASE scenario for each cell is read from the file the
Tier-1 runs were generated from, not regenerated. Regenerating it would produce a byte-identical
file in the ordinary case and a silently different corpus in the case that matters, and the whole
point of Tier 2 is that it is the same design at larger n.

THE BUDGET IS ASSERTED, NOT ASSUMED. min_progress = 0, max_generations = 90,
init_file = ResultH0914Gait10.par, and no _resume.par anywhere -- checked against every one of the
120 generated files before a single process starts.

GATE G5 RUNS BEFORE LAUNCH. SCONE appends ` (1)` rather than overwriting, and 114 Tier-1
directories now sit in the results root, so a tag collision here would silently produce a
directory the analysis cannot resolve. This is the round where G5 stops being a formality.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import gen_slope_r60 as G60                                       # noqa: E402

#: Registered Tier-2 seeds. Tier 1 used 101..106; 107..116 were reserved for this escalation.
TIER2_SEEDS = list(range(107, 117))

#: The 12 primary cells: 4 primary conditions x 3 grades. CONTROL and MANIP_CHECK are excluded
#: by the registration, not by preference.
TIER2_CONDS = [c for c in G60.CONDS if c[4] in ("PRIMARY_SPASTIC", "PRIMARY_WEAK")]


def build_tier2():
    """Write the 120 seeded scenarios from the EXISTING Tier-1 base scenario of each cell."""
    made = []
    for grade in G60.GRADES:
        for cond, _weak, _kv, _n, role in TIER2_CONDS:
            tag = G60.tag_of(grade, cond)
            base = os.path.join(G60.OPTDIR, tag + ".scone")
            if not os.path.isfile(base):
                raise RuntimeError("missing Tier-1 base scenario %s; refusing to regenerate it, "
                                   "because a regenerated base is a different corpus" % base)
            txt = open(base, encoding="utf-8", errors="ignore").read()
            for seed in TIER2_SEEDS:
                t2 = "%s_s%d" % (tag, seed)
                s = re.sub(r"signature_prefix\s*=\s*\S+",
                           "signature_prefix = %s" % t2, txt, count=1)
                s = G60.GS.set_seed(s, seed)
                sp = os.path.join(G60.OPTDIR, t2 + ".scone")
                open(sp, "w", encoding="utf-8").write(s)
                made.append((t2, sp))
    return made


def assert_budget(made):
    """The registered stopping rule, checked in every generated file. Asserted, not assumed."""
    print("\n" + "=" * 92)
    print("BUDGET ASSERTION -- the registered stopping rule, read back from every generated file")
    print("=" * 92)
    bad = []
    for t2, sp in made:
        s = open(sp, encoding="utf-8", errors="ignore").read()
        checks = {
            "min_progress = 0": re.search(r"min_progress\s*=\s*0\b", s),
            "max_generations = 90": re.search(r"max_generations\s*=\s*90\b", s),
            "init_file ResultH0914Gait10.par": "ResultH0914Gait10.par" in s,
            "random_seed correct": re.search(r"random_seed\s*=\s*%s\b" % t2.rsplit("_s", 1)[1], s),
            "signature_prefix correct": re.search(r"signature_prefix\s*=\s*%s\b" % re.escape(t2), s),
            "no _resume.par": "_resume.par" not in s,
        }
        for k, v in checks.items():
            if not v:
                bad.append((t2, k))
    print("  files checked                       : %d" % len(made))
    print("  distinct assertions per file        : 6")
    if bad:
        for t2, k in bad[:20]:
            print("    *** %-28s FAILED %s" % (t2, k))
        raise RuntimeError("BUDGET ASSERTION FAILED on %d checks" % len(bad))
    print("  failures                            : 0")
    print("  budget verdict: PASS")
    return "PASS"


def main():
    if "--build" not in sys.argv and "--launch" not in sys.argv:
        print(__doc__)
        return 2
    made = build_tier2()
    print("built %d Tier-2 seed scenarios over %d cells (seeds %d..%d)"
          % (len(made), len(made) // len(TIER2_SEEDS), TIER2_SEEDS[0], TIER2_SEEDS[-1]))
    assert_budget(made)
    G60.gate_collision(made)                       # GATE G5, before launch
    if "--launch" in sys.argv:
        G60.launch([t for t, _ in made], "TIER2")
    else:
        print("\nbuild + gates only. Re-run with --launch to start the 120 runs.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
