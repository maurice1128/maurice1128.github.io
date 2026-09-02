"""Does the simulated spasticity actually produce EQUINUS? Independent check of round 10's claim.

Round 10's fresh-eyes reviewer made a claim that, if true, invalidates the entire project:

    "The spastic model at KV = 0.05 is MORE DORSIFLEXED than healthy. It does not produce equinus
     at all. So the contrast is near-normal gait (spastic arm) vs gross drop-foot at 70-80 % TA
     loss (weak arm). A classifier will read 'does this foot drop', not 'which mechanism'."

The whole clinical premise is that BOTH mechanisms produce equinus and the question is which one.
If the spastic arm does not produce equinus, there is nothing to discriminate and every result on
this project is about something else.

This script re-derives the number from raw `.sto` rather than accepting the review, and reports:
  * mean / min ankle angle over the gait cycle, affected and intact
  * ankle angle at heel strike (round 9 used this and reached the OPPOSITE sign for the paretic
    arm, so the two metrics must be shown together or one of them will be cherry-picked later)
  * the size of the injected reflex's excitation against the muscle's actual operating activation,
    which is what decides whether the injected "spasticity" is physiologically present at all
  * the column-count leak: spastic `.sto` reportedly carry 4 extra columns naming the controller

Sign convention: ankle_angle negative = PLANTARFLEXION = equinus.
"""
import glob
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from replay_cache import replay  # noqa: E402
from sto_utils import col, grf_vertical, heel_strikes, load_sto, muscle_signal  # noqa: E402

CONDS = [
    ("HEALTHY", "DHEALTHY_s1", None),
    ("TA -20%", "DPAR20_s1", None),
    ("TA -40%", "DPAR40_s1", None),
    ("TA -60%", "DPAR60_s1", None),
    ("TA -70%", "CMW70_s1", None),
    ("TA -80%", "CMW80_s1", None),
    ("KV 0.02", "CMS020_s1", 0.02),
    ("KV 0.03", "CMS030_s1", 0.03),
    ("KV 0.05", "SPAS005_s2", 0.05),
    ("KV 0.10", "SPAS01_s2", 0.10),
]


def main():
    print("EQUINUS CHECK -- ankle_angle, negative = plantarflexion = equinus\n")
    print("%-9s %-13s %6s %7s %7s %7s %7s  %s"
          % ("cond", "run", "gen", "mean_L", "min_L", "HS_L", "mean_R", "cols"))
    print("-" * 86)
    rows = []
    for name, tag, kv in CONDS:
        r = replay(tag, gen_cap=None)          # deepest available; equinus is not a depth claim
        if "error" in r:
            print("%-9s %-13s  %s" % (name, tag, r["error"]))
            continue
        cols, d = load_sto(r["sto"])
        t = d[:, 0]
        aL = np.degrees(col(cols, d, "ankle_angle_l"))
        aR = np.degrees(col(cols, d, "ankle_angle_r"))
        grf, thr = grf_vertical(cols, d, "l")
        hs = [i for i in heel_strikes(t, grf, thresh=thr) if t[i] >= 1.0]
        if len(hs) < 3:
            print("%-9s %-13s  no cycles" % (name, tag))
            continue
        a0, b0 = hs[0], hs[-1]
        rec = dict(name=name, tag=tag, gen=r["gen"], kv=kv,
                   mean_l=float(np.mean(aL[a0:b0])), min_l=float(np.min(aL[a0:b0])),
                   hs_l=float(np.mean([aL[i] for i in hs])),
                   mean_r=float(np.mean(aR[a0:b0])), ncol=len(cols))
        rows.append(rec)
        print("%-9s %-13s %6d %7.2f %7.2f %7.2f %7.2f  %d"
              % (name, tag, r["gen"], rec["mean_l"], rec["min_l"], rec["hs_l"],
                 rec["mean_r"], rec["ncol"]))

        # --- how big is the injected reflex against the muscle's real operating excitation? ---
        if kv is not None:
            for m in ("soleus", "gastroc"):
                act = muscle_signal(cols, d, m, "l", "activation")
                rv = None
                for cand in ("%s_l.RV" % m, "/forceset/%s_l/RV" % m):
                    if cand in cols:
                        rv = d[:, cols.index(cand)]
                        break
                if act is not None and rv is not None:
                    add = kv * np.maximum(rv, 0)
                    print("            %-8s injected excitation mean=%.5f p95=%.5f | "
                          "activation mean=%.4f  -> reflex is %.2f%% of drive"
                          % (m, np.mean(add), np.percentile(add, 95), np.mean(act[a0:b0]),
                             100 * np.mean(add) / max(np.mean(act[a0:b0]), 1e-9)))

    if not rows:
        return
    hea = [r for r in rows if r["name"] == "HEALTHY"]
    if not hea:
        return
    h = hea[0]
    print("\n" + "=" * 86)
    print("Relative to HEALTHY (mean_L = %.2f deg):" % h["mean_l"])
    print("%-9s %10s %10s   %s" % ("cond", "d_mean", "d_HS", "produces equinus?"))
    for r in rows:
        if r["name"] == "HEALTHY":
            continue
        dm, dh = r["mean_l"] - h["mean_l"], r["hs_l"] - h["hs_l"]
        verdict = ("YES (both metrics)" if dm < 0 and dh < 0 else
                   "NO -- more dorsiflexed" if dm > 0 and dh > 0 else
                   "AMBIGUOUS -- metrics disagree")
        print("%-9s %+10.2f %+10.2f   %s" % (r["name"], dm, dh, verdict))

    print("\n" + "=" * 86)
    ncols = {r["name"]: r["ncol"] for r in rows}
    uniq = sorted(set(ncols.values()))
    print("COLUMN-COUNT LEAK: distinct .sto widths = %s" % uniq)
    if len(uniq) > 1:
        print("  -> LEAK CONFIRMED. Column count alone identifies the class:")
        for n in uniq:
            print("     %d cols: %s" % (n, ", ".join(k for k, v in ncols.items() if v == n)))
        print("  Any pipeline reading all columns is a perfect classifier of the label.")
        print("  waveform_classify.py reads NAMED channels only, so it is not affected -- but")
        print("  this must never be relaxed to 'use all columns'.")


if __name__ == "__main__":
    main()
