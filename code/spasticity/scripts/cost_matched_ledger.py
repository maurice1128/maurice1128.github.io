"""Cost-matched contrast on the CROSSED corpus, computed from the replay ledger.

WRITTEN AND RUN 2026-08-03 (round 61), BY THE ROUND-61 AUDITOR, AFTER THE DATA EXISTED.
This is NOT a pre-registered analysis and must never be cited as one. It exists because the
round-61 audit found that the "cost-matched pairs, 4/4 negative, mean -17 deg" sentence in
`paper/RESULTS_discrimination.md` Sec.3 had been RELAYED from a referee report with no artifact
anywhere in this repository. `scone/cost_matched.py` is a LAUNCHER -- it writes SCONE scenarios and
starts optimizations; it computes no contrast, and its `opt_costmatch` corpus tags collide with the
crossed corpus, so its outputs cannot be separated from the crossed runs by name. The choice was
therefore: cut the claim, or earn it. This script earns it.

WHAT "COST" MEANS HERE, AND WHAT IT DOES NOT MEAN.
"Cost" is the achieved CMA-ES OBJECTIVE VALUE of the run whose parameters were replayed -- the
`fitness` field of `replay_crossed/ledger.json`, which `crossed_endpoint.py` already loads (as
`p["fitness"]`, stored into `runs[tag]["fit"]`) and then never uses. It is NOT a separately measured
metabolic rate. The objective is a weighted composite of gait, effort and penalty terms. This
matters in BOTH directions and neither is suppressed:

  - It is the project's own operationalisation of cost. `cost_matched.py`'s header defines the
    problem in exactly these terms: "the CMA-ES objective value ALONE separates the classes
    perfectly (non-spastic 0.601-0.684, spastic 0.731-1.138, no overlap)", and matching on it is
    what that script was built to do. Using `fitness` is continuous with the design, not a
    substitution invented here.
  - It is nonetheless a composite, so a matched pair is matched on ACHIEVED OBJECTIVE VALUE, not on
    metabolic energy. Any sentence in the manuscript that says "matched on metabolic cost" is
    overstating what this computes and has been corrected to say what it is.

THE MATCHING BAND WAS CHOSEN AFTER SEEING THE FITNESS VALUES. There is no MDC for an objective
value, so the equinus analysis's trick (match within a threshold fixed by an earlier round) is not
available. The band used is one POOLED WITHIN-CONDITION SD of fitness over the ten lesioned
conditions -- a data-defined scale rather than a round number -- and because that choice is a
researcher degree of freedom exercised after the fact, the script sweeps the band from 0.5 to 3.0
pooled SD and prints every result. The sweep is the disclosure. Read it, not the headline.

SIGN PATTERN ONLY. As with the equinus pairs, the pairs share conditions (three of the four at
1 SD involve CMW70), so they are not independent and a Wilcoxon over them has no defensible null.
No p-value is computed here and none may be added later.

Corpus: `scone/replay_crossed` (48 runs, 12 conditions x 4 seeds, ledger status "ok" for all 48).
Feature: `ank_rom` from `sto_utils.cycle_features`, the same repaired GRF-windowed library the
registered `rom_reanalysis.py` uses. Writes `paper/COST_MATCHED_LEDGER.json`.
"""
import glob
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import sto_utils as S  # noqa: E402

REPLAY = os.path.join(HERE, "replay_crossed")
SPASTIC = ["DR2K050", "DR2K075", "DR2K100", "DR2K150", "DR2K200"]
WEAK = ["PAR20", "PAR40", "PAR60", "CMW70", "CMW80"]
REFERENCE = ["HEALTHY", "DR2K000"]
SEEDS = 4
BANDS = (0.5, 1.0, 1.5, 2.0, 3.0)
HEADLINE_BAND = 1.0


def load():
    """Condition -> list of per-seed feature dicts, with ledger fitness attached."""
    led = json.load(open(os.path.join(REPLAY, "ledger.json"), encoding="utf-8"))
    bad = [e["tag"] for e in led if e.get("status") != "ok"]
    if bad:
        raise SystemExit("[BLOCKED] ledger entries not ok: %s" % bad)
    fit = {e["tag"]: float(e["fitness"]) for e in led}

    per = {}
    for d in sorted(glob.glob(os.path.join(REPLAY, "*"))):
        if not os.path.isdir(d):
            continue
        tag = os.path.basename(d)
        cond = tag.rsplit("_s", 1)[0]
        if cond not in SPASTIC + WEAK + REFERENCE:
            continue
        sto = [x for x in glob.glob(os.path.join(d, "*.sto")) if os.path.getsize(x) > 1000]
        if len(sto) != 1:
            continue
        f = S.cycle_features(sto[0], side="l", settle=1.0)
        if f is None:
            continue
        f["fit"] = fit[tag]
        per.setdefault(cond, []).append(f)

    # FAIL CLOSED, for the same reason crossed_endpoint.py does: a partial cell is how n<4
    # silently becomes a reported n=4.
    short = [(c, len(per.get(c, []))) for c in SPASTIC + WEAK + REFERENCE
             if len(per.get(c, [])) != SEEDS]
    if short:
        raise SystemExit("[BLOCKED] incomplete cells: %s" % short)
    return per


def main():
    per = load()
    les = SPASTIC + WEAK
    M = lambda c, k: float(np.mean([r[k] for r in per[c]]))  # noqa: E731

    sds = [float(np.std([r["fit"] for r in per[c]], ddof=1)) for c in les]
    pooled = float(np.sqrt(np.mean(np.square(sds))))

    print("=" * 78)
    print("COST-MATCHED CONTRAST -- computed 2026-08-03 (round 61), NOT pre-registered")
    print("  cost = achieved CMA-ES objective value (ledger `fitness`), NOT a metabolic rate")
    print("=" * 78)
    print("\n%-9s %10s %10s %10s" % ("cond", "fitness", "fit SD", "ank_rom"))
    for c in les + REFERENCE:
        sd = float(np.std([r["fit"] for r in per[c]], ddof=1))
        print("%-9s %10.4f %10.4f %10.3f" % (c, M(c, "fit"), sd, M(c, "ank_rom")))
    print("\n  pooled within-condition fitness SD over the 10 lesioned conditions = %.5f" % pooled)

    out = {"computed_utc_date": "2026-08-03", "computed_by": "round-61 audit",
           "preregistered": False,
           "cost_definition": "achieved CMA-ES objective value from replay_crossed/ledger.json",
           "pooled_within_condition_fitness_sd": pooled, "bands": {}}

    print("\n  BAND SWEEP (the band was chosen after seeing the data; this sweep is the disclosure)")
    for mult in BANDS:
        band = mult * pooled
        pairs = [(x, y) for x in SPASTIC for y in WEAK if abs(M(x, "fit") - M(y, "fit")) < band]
        d = [M(x, "ank_rom") - M(y, "ank_rom") for x, y in pairs]
        neg = sum(1 for v in d if v < 0)
        mean = float(np.mean(d)) if d else float("nan")
        print("    %.1f SD (%.4f) : %2d pairs, %2d negative, mean %+8.3f deg"
              % (mult, band, len(pairs), neg, mean))
        out["bands"]["%.1f" % mult] = {
            "band": band, "n_pairs": len(pairs), "n_negative": neg, "mean_d_ank_rom": mean,
            "pairs": [[x, y, float(M(x, "fit") - M(y, "fit")), float(v)]
                      for (x, y), v in zip(pairs, d)]}

    hb = out["bands"]["%.1f" % HEADLINE_BAND]
    print("\n  HEADLINE BAND = %.1f pooled SD" % HEADLINE_BAND)
    for x, y, df, dv in hb["pairs"]:
        print("    %-8s vs %-8s   d_fitness %+7.4f   d_ank_rom %+8.3f" % (x, y, df, dv))
    print("    -> %d of %d negative, mean %+.2f deg" % (hb["n_negative"], hb["n_pairs"],
                                                        hb["mean_d_ank_rom"]))
    print("\n  SIGN PATTERN ONLY. The pairs share conditions and are not independent;")
    print("  no p-value is computed here and none may be added later.")

    dst = os.path.abspath(os.path.join(HERE, "..", "paper", "COST_MATCHED_LEDGER.json"))
    json.dump(out, open(dst, "w"), indent=1)
    print("\n  wrote %s" % dst)
    return 0


if __name__ == "__main__":
    sys.exit(main())
