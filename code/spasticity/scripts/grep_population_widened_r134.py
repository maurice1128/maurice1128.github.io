# -*- coding: utf-8 -*-
"""Round 134, part 3. THE WIDENED-POPULATION TEST -- a measurement, not a fix.

Authorised by the coordinator as a test and only as a test. The manuscript's
definition is NOT modified; this script runs the SAME grep with ONE thing
changed -- the population is taken at ALL depths instead of the top two.

Held identical to the deposited baseline (grep_population_test_r134.py /
grep_population_scope_r134.py):
  * matching rule  -- case-SENSITIVE, word-boundary both sides, so a longer
                      registered name is its own outcome (METHODS:618-621)
  * file scope     -- reported for BOTH scopes, exactly as the baseline was
  * positive control -- ank_rom, per METHODS:625
  * flag criterion -- a population name is FLAGGED when it appears zero times
                      in BOTH manuscripts (that is what "absent from both
                      manuscripts" means at METHODS:637)

Comparison points quoted from the manuscript:
  METHODS:611-613  discarded first instrument: "1,053 flagged of 1,158 -- 91 %"
  METHODS:637      tightened run:              "flags **191 of 254**"
"""
import io, json, re, os, glob

PAPER = r"C:\Users\maurice\Desktop\spasticity_paper\paper"
MSS = {"METHODS": os.path.join(PAPER, "METHODS_contribution.md"),
       "RESULTS": os.path.join(PAPER, "RESULTS_discrimination.md")}
TXT = dict((k, io.open(v, encoding="utf-8").read()) for k, v in MSS.items())

FILES = sorted(glob.glob(os.path.join(PAPER, "*.json")))
MAIN = os.path.join(PAPER, "VIDEO_DEGRADATION.json")


def keys_upto(obj, depth, maxd, out):
    """Collect dict keys. maxd=None -> all depths. Arrays transparent, matching
    the deposited baseline's convention (the coordinator confirmed the answer is
    invariant under the other convention)."""
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


def flagged(pop):
    """A name is flagged when absent from BOTH manuscripts."""
    out = set()
    for n in pop:
        if wb(n, TXT["METHODS"]) == 0 and wb(n, TXT["RESULTS"]) == 0:
            out.add(n)
    return out


def report(label, files):
    print("=" * 74)
    print(label)
    print("=" * 74)
    rows = []
    for name, maxd in (("top two levels (as defined)", 2), ("ALL depths (widened)", None)):
        pop = population(files, maxd)
        fl = flagged(pop)
        pct = (100.0 * len(fl) / len(pop)) if pop else 0.0
        rows.append((name, pop, fl))
        print("  %-28s population=%-5d flagged=%-5d (%.1f %%)" % (name, len(pop), len(fl), pct))
    (_, p2, f2), (_, pa, fa) = rows
    print()
    print("  REFCAL under each:")
    for probe in ("refcal_mean", "refcal_sd"):
        print("    %-12s in top2-pop: %-5s flagged: %-5s | in all-pop: %-5s flagged: %-5s"
              % (probe, probe in p2, probe in f2, probe in pa, probe in fa))
    new = fa - f2
    print()
    print("  NEWLY FLAGGED by widening: %d names" % len(new))
    print("  population growth: %d -> %d (+%d)" % (len(p2), len(pa), len(pa) - len(p2)))
    samp = sorted(new)
    print("  sample of newly flagged (first 30):")
    for n in samp[:30]:
        print("     ", n)
    return p2, f2, pa, fa, new


print()
p2a, f2a, paa, faa, newa = report("SCOPE A: VIDEO_DEGRADATION.json alone", [MAIN])
print()
p2b, f2b, pab, fab, newb = report("SCOPE B: union over all %d paper/*.json" % len(FILES), FILES)

print()
print("=" * 74)
print("POSITIVE CONTROL, per METHODS:625 -- identical to baseline")
print("=" * 74)
for probe in ("ank_rom", "refcal_mean", "margin_gap"):
    print("  %-12s METHODS=%-3d RESULTS=%-3d  in widened pop(B): %s"
          % (probe, wb(probe, TXT["METHODS"]), wb(probe, TXT["RESULTS"]), probe in pab))
print("  ^ ank_rom fires, so a zero is an absence and not a dead pattern.")

print()
print("=" * 74)
print("VERDICT -- which of the coordinator's three outcomes")
print("=" * 74)
hit = ("refcal_mean" in fab) or ("refcal_sd" in fab)
print("  widening FLAGS refcal?  %s" % ("YES" if hit else "NO"))
print("  flood size (scope B)  :  %d newly flagged, total flagged %d of %d"
      % (len(newb), len(fab), len(pab)))
print()
print("  manuscript comparison points:")
print("    discarded first instrument (METHODS:611-613): 1053 of 1158 = 91.0 %")
print("    tightened run as reported  (METHODS:637)    :  191 of 254  = 75.2 %")
print("    measured here, top two, scope B             :  %d of %d = %.1f %%"
      % (len(f2b), len(p2b), 100.0 * len(f2b) / len(p2b)))
print("    measured here, widened, scope B             :  %d of %d = %.1f %%"
      % (len(fab), len(pab), 100.0 * len(fab) / len(pab)))
