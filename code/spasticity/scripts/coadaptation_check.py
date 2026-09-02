"""Did the controller CO-ADAPT to the reflex? Read it straight out of the .par files. No simulation.

THE QUESTION KV=0 COULD NOT ANSWER.
Switching the injected reflex off makes three of four converged spastic runs fall
(`kv_zero_test.py`). That establishes NECESSITY, not mechanism. Three hypotheses survive:

  H1 mechanical work  -- the reflex actively does plantarflexor work each stride; removing it
                         removes real force.
  H2 co-adaptation    -- the optimizer LEANED on the reflex, reducing the controller's own
                         intrinsic soleus drive to compensate. Removing it then leaves a deficit
                         the controller can no longer cover.
  H3 generic fragility-- the controller is brittle to any perturbation of this size and the reflex
                         is incidental.

The naive direction already argues against the reflex being an independent driver: a healthy
controller with the reflex ADDED falls at KV >= 0.01 (`scone_naive_ladder.json`), and an adapted
controller with it REMOVED falls too. A term that can be neither added nor removed is one half of a
matched pair, which is H2.

THE DIRECT TEST, and it costs nothing.
H2 makes a sharp, checkable prediction about the optimized parameters themselves: if the optimizer
delegated plantarflexor work to the injected reflex, the spastic controllers should carry
systematically LOWER intrinsic soleus drive than the non-spastic ones.

SCONE writes the optimized parameters by name into every `.par`. `S00111.soleus.KF` is the soleus
force-feedback gain during stance -- the controller's own plantarflexor drive. Compare it across
arms. No replay, no simulation, no analysis choices.

  spastic soleus.KF systematically LOWER  -> H2 confirmed directly
  no difference                           -> H2 is not the mechanism; H1/H3 remain open

Confound to respect: the injected gain is a fixed literal and adds no free parameter, and both arms
optimize the identical 36-parameter vector (verified). So any systematic shift in a named parameter
is a genuine difference in what the optimizer chose, not a difference in what it was allowed to
choose. Optimization depth is reported alongside, because a deep run and a shallow one are not
comparable and this project has made that mistake three times.
"""
import glob
import os
import re

import numpy as np

RES = r"C:\Users\maurice\Documents\SCONE\results"

# --- PRE-REGISTRATION, fixed before this depth-matched version was run -------------------------
# The first version of this script ran the spastic arm at its natural depth (mean generation 246)
# against a non-spastic arm at 68 -- a 3.6x mismatch, the fourth occurrence of that error class on
# this project. It returned soleus.KF -5.7% (p = 0.137) and gastroc.KF -7.0% (p = 0.121). Because
# that shape is already known, direction and alpha are fixed here BEFORE re-running at matched
# depth, so the re-run cannot become a search for a threshold that clears.
#
#   PRIMARY      S00111.soleus.KF, spastic LOWER than non-spastic. One-sided. alpha = 0.05.
#   SECONDARY    S00111.gastroc.KF, same direction, reported uncorrected and labelled secondary.
#   SPECIFICITY  S11111.tib_ant.KL and S11111.tib_ant-soleus.KF are antagonist-side parameters and
#                must show NO effect. If they move with the plantarflexor gains, the result is a
#                global shift in the optimizer's operating point, not delegation of plantarflexor
#                work, and H2 is NOT supported however small the primary p-value is.
#   DEPTH        Both arms read at GEN_CAP. If mean depth differs by more than 15%, no claim.
#
# BINDING INTERPRETATION LIMIT: the controller is `symmetric = 1`, so left and right gains are tied.
# Any shift measured here is therefore a BILATERAL retuning of the controller, NOT the lateralized
# compensation a hemiparetic patient makes. This must be stated wherever the result is reported.
GEN_CAP = 90

# the controller's own plantarflexor drive, plus neighbours for context
KEYS = ["S00111.soleus.KF", "S00111.gastroc.KF", "S11111.tib_ant.KL",
        "S11111.tib_ant-soleus.KF"]

ARMS = {
    "non-spastic": {
        "HEALTHY": ["DHEALTHY_s1", "DHEALTHY_s2", "DHEALTHY_s3"],
        "TA -20%": ["DPAR20_s1", "DPAR20_s2", "DPAR20_s3"],
        "TA -40%": ["DPAR40_s1", "DPAR40_s2", "DPAR40_s3"],
        "TA -60%": ["DPAR60_s1", "DPAR60_s2", "DPAR60_s3"],
    },
    "spastic": {
        "KV 0.05": ["SPAS005", "SPAS005_s2", "SPAS005_s3", "SPAS005_s4"],
        "KV 0.10": ["SPAS01", "SPAS01_s2", "SPAS01_s3", "SPAS01_s4"],
    },
}


def best_par(tag):
    ds = [d for d in glob.glob(os.path.join(RES, tag + ".*")) if os.path.isdir(d)]
    if not ds:
        return None, None, None
    d = max(ds, key=os.path.getmtime)
    cfg = os.path.join(d, "config.scone")
    cap = None
    if os.path.exists(cfg):
        m = re.search(r"max_generations\s*=\s*(\d+)",
                      open(cfg, encoding="utf-8", errors="ignore").read())
        cap = int(m.group(1)) if m else None
    setup = os.path.getmtime(cfg) if os.path.exists(cfg) else None
    bp, bf, bg = None, 1e9, None
    for p in sorted(glob.glob(os.path.join(d, "0*.par"))):
        m = re.match(r"^(\d+)_.*?_([0-9.]+)$", os.path.basename(p)[:-4])
        if not m:
            continue
        g, f = int(m.group(1)), float(m.group(2))
        if cap is not None and g > cap:            # foreign warm-start copy
            continue
        if g > GEN_CAP:                            # shared depth ceiling across BOTH arms
            continue
        if setup is not None and os.path.getmtime(p) <= setup:
            continue
        if f < bf:
            bp, bf, bg = p, f, g
    return bp, bf, bg


def read_params(path):
    out = {}
    for line in open(path, encoding="utf-8", errors="ignore"):
        parts = line.split()
        if len(parts) >= 2:
            try:
                out[parts[0]] = float(parts[1])
            except ValueError:
                pass
    return out


def main():
    rows = []
    for arm, conds in ARMS.items():
        for cname, tags in conds.items():
            for t in tags:
                p, f, g = best_par(t)
                if p is None:
                    continue
                v = read_params(p)
                if KEYS[0] not in v:
                    continue
                rows.append(dict(arm=arm, cond=cname, tag=t, fit=f, gen=g,
                                 **{k: v.get(k, float("nan")) for k in KEYS}))

    if not rows:
        print("no data")
        return

    print("%-12s %-9s %-13s %5s %7s  %s"
          % ("arm", "condition", "run", "gen", "fitness",
             "  ".join("%-10s" % k.split(".", 1)[1] for k in KEYS)))
    print("-" * 108)
    for r in sorted(rows, key=lambda r: (r["arm"], r["cond"], r["tag"])):
        print("%-12s %-9s %-13s %5d %7.4f  %s"
              % (r["arm"], r["cond"], r["tag"], r["gen"], r["fit"],
                 "  ".join("%-10.4f" % r[k] for k in KEYS)))

    print("\n" + "=" * 108)
    print("H2 prediction: the SPASTIC arm delegates plantarflexor work to the injected reflex,")
    print("so its own soleus.KF should be systematically LOWER.\n")
    for k in KEYS:
        a = np.array([r[k] for r in rows if r["arm"] == "non-spastic"])
        b = np.array([r[k] for r in rows if r["arm"] == "spastic"])
        a, b = a[~np.isnan(a)], b[~np.isnan(b)]
        if len(a) < 2 or len(b) < 2:
            continue
        # exact rank-sum over all label assignments: no distributional assumption, tiny n
        allv = np.concatenate([a, b])
        import itertools
        obs = b.mean() - a.mean()
        cnt = tot = 0
        for idx in itertools.combinations(range(len(allv)), len(b)):
            m = np.zeros(len(allv), bool)
            m[list(idx)] = True
            if allv[m].mean() - allv[~m].mean() <= obs:
                cnt += 1
            tot += 1
        print("  %-26s non-spastic %.4f +-%.4f (n=%d) | spastic %.4f +-%.4f (n=%d)"
              % (k, a.mean(), a.std(), len(a), b.mean(), b.std(), len(b)))
        # The annotation must respect the pre-registered roles. An earlier version keyed only on
        # "significantly lower" and printed "<- LOWER, as H2 predicts" for tib_ant.KL -- the
        # ANTAGONIST, about which H2 predicts nothing and whose movement DISCONFIRMS H2. Marking a
        # bug in prose does not stop it re-firing; the rule itself has to know the roles.
        PRIMARY = ("S00111.soleus.KF", "S00111.gastroc.KF")
        sig = cnt / tot < 0.05
        if k in PRIMARY:
            note = "   <- LOWER, as H2 predicts" if (obs < 0 and sig) else ""
        else:
            note = ("   <- ANTAGONIST MOVED -- H2 DISCONFIRMED (pre-registered specificity clause)"
                    if sig else "   (specificity control: no effect, as required)")
        print("  %-26s difference %+.4f (%+.1f%%)   exact one-sided p = %.4f (floor %.4f)%s"
              % ("", obs, 100 * obs / a.mean(), cnt / tot, 1.0 / tot, note))
        print()

    ga = [r["gen"] for r in rows if r["arm"] == "non-spastic"]
    gb = [r["gen"] for r in rows if r["arm"] == "spastic"]
    print("  DEPTH: non-spastic gen %d-%d (mean %.0f) | spastic gen %d-%d (mean %.0f)"
          % (min(ga), max(ga), np.mean(ga), min(gb), max(gb), np.mean(gb)))
    print("  If these differ greatly the comparison inherits the depth confound -- state it.")


if __name__ == "__main__":
    main()
