# -*- coding: utf-8 -*-
"""Round 134, part 4. THE COUNTERFACTUAL, RUN AGAINST THE PRE-REPAIR DRAFT.

Parts 1-3 scored the flag criterion -- "absent from BOTH manuscripts" -- against
TODAY's manuscripts. Today's manuscripts discuss REFCAL, because section 4.9 was
written after the referee found it: `refcal_mean` occurs once in RESULTS. So a
widened population cannot flag it today no matter how deep it reaches, and that
is an artifact of the repair, NOT evidence about depth.

The question the paper actually asks is a counterfactual: would this check have
caught REFCAL when REFCAL was live? That requires the draft as it stood then.
METHODS:532-533 names it: the false wording "the only decision rule available
without a labelled training set" is in `paper/.bak_r55_RESULTS_discrimination.md`.

Measured: .bak_r55_METHODS_contribution.md and .bak_r55_RESULTS_discrimination.md
contain ZERO occurrences of refcal in any case. That is the pre-repair state.

Everything else is held identical to the deposited baseline: same matching rule
(case-sensitive, word-boundary both sides), same two file scopes, same positive
control, same flag criterion. ONE thing varies -- the depth cap.
"""
import io, json, re, os, glob

PAPER = r"C:\Users\maurice\Desktop\spasticity_paper\paper"
FILES = sorted(glob.glob(os.path.join(PAPER, "*.json")))
MAIN = os.path.join(PAPER, "VIDEO_DEGRADATION.json")

DRAFTS = {
    "TODAY (post-repair)": ("METHODS_contribution.md", "RESULTS_discrimination.md"),
    "r55 (pre-repair, the founding case)": (".bak_r55_METHODS_contribution.md",
                                            ".bak_r55_RESULTS_discrimination.md"),
}


def keys_upto(obj, depth, maxd, out):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if maxd is None or depth <= maxd:
                out.add(k)
            keys_upto(v, depth + 1, maxd, out)
    elif isinstance(obj, list):
        for v in obj:
            keys_upto(v, depth, maxd, out)


def population(files, maxd):
    pop = set()
    for f in files:
        try:
            d = json.load(io.open(f, encoding="utf-8"))
        except Exception:
            continue
        keys_upto(d, 1, maxd, pop)
    return pop


def wb(name, txt):
    return len(re.findall(r"(?<![A-Za-z0-9_])" + re.escape(name) + r"(?![A-Za-z0-9_])", txt))


for dname, (mf, rf) in DRAFTS.items():
    M = io.open(os.path.join(PAPER, mf), encoding="utf-8").read()
    R = io.open(os.path.join(PAPER, rf), encoding="utf-8").read()
    print("=" * 76)
    print("DRAFT: %s" % dname)
    print("  %s (%d B) + %s (%d B)" % (mf, len(M.encode("utf-8")), rf, len(R.encode("utf-8"))))
    print("  refcal occurrences, case-insensitive: METHODS=%d RESULTS=%d"
          % (len(re.findall("refcal", M, re.I)), len(re.findall("refcal", R, re.I))))
    print("=" * 76)

    def flagged(pop):
        return set(n for n in pop if wb(n, M) == 0 and wb(n, R) == 0)

    for scope_name, files in (("VIDEO_DEGRADATION.json alone", [MAIN]),
                              ("union over all %d paper/*.json" % len(FILES), FILES)):
        print("  scope: %s" % scope_name)
        prev = None
        for pname, maxd in (("top two (as defined)", 2), ("ALL depths (widened)", None)):
            pop = population(files, maxd)
            fl = flagged(pop)
            hit = ("refcal_mean" in fl) or ("refcal_sd" in fl)
            inpop = ("refcal_mean" in pop)
            print("     %-22s pop=%-4d flagged=%-4d (%.1f %%)  refcal in pop: %-5s  FLAGGED: %s"
                  % (pname, len(pop), len(fl), 100.0 * len(fl) / len(pop), inpop,
                     "YES" if hit else "NO"))
            if prev is not None:
                print("        -> widening adds %d names to the population, %d to the flag list"
                      % (len(pop) - len(prev[0]), len(fl) - len(prev[1])))
            prev = (pop, fl)
        print()

    # positive control, per METHODS:625
    print("  positive control (METHODS:625): ank_rom -> METHODS=%d RESULTS=%d"
          % (wb("ank_rom", M), wb("ank_rom", R)))
    print()

print("=" * 76)
print("THE ONE SENTENCE THIS MEASURES")
print("=" * 76)
print("  Against the draft in which REFCAL was actually omitted, the population")
print("  as DEFINED (top two levels) does not contain refcal_mean, so the check")
print("  never tests it; the WIDENED population does contain it and flags it.")
print("  The cost of widening is the flood number printed above.")
