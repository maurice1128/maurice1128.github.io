# -*- coding: utf-8 -*-
"""r210 bookkeeping: restrict the PUBLISHED r179 parallel fractions to the three channel
families PREREG_3d_mirror_r210.md defines. No simulation, no new measurement -- this only
re-reads paper/PRIMARYB_RESULT_r179.json, which was deposited in r179.

Purpose: the r210 headline is PAIRED-ONLY, but 0.89 / 0.88 / 0.86 are POOLED over all
sixteen channels. This computes the like-for-like comparator the registration needs.
"""
import io, json

SRC = r"C:\Users\maurice\Desktop\spasticity_paper\paper\PRIMARYB_RESULT_r179.json"
DST = r"C:\Users\maurice\Desktop\spasticity_paper\paper\PARENT_BYFAMILY_r210.json"

PAIR = ["ankle_angle", "knee_angle", "hip_flexion", "hip_adduction"]
FAM = {
    "paired":   [p + s for p in PAIR for s in ("_l", "_r")],
    "unpaired": ["pelvis_list", "pelvis_rotation", "lumbar_bending", "cycle_time"],
    "LmR":      [p + "_LmR" for p in PAIR],
}
DOSES = ("W870", "W892", "W915")

d = json.load(io.open(SRC, encoding="utf-8"))
out = {"source": "PRIMARYB_RESULT_r179.json", "label": "BOOKKEEPING: re-read of a deposited "
       "result, not a new measurement", "families": {}, "pooled_check": {}}

for fam, chs in FAM.items():
    out["families"][fam] = {}
    for r in DOSES:
        b = p = 0; opp = []
        for ch in chs:
            row = d["channels"][ch]
            if row["S_displaced"] and row[r]["displaced"]:
                b += 1
                if row[r]["opposed"]: opp.append(ch)
                else: p += 1
        out["families"][fam][r] = {"both_displaced": b, "parallel": p, "opposed": opp,
                                   "fraction": (p / b) if b else None}
        print("%-9s %-5s both=%d parallel=%d frac=%s opposed=%s"
              % (fam, r, b, p, ("%.4f" % (p / b)) if b else "n/a", opp))
    print()

# the published pooled numbers must be reproduced by summing the three families
for r in DOSES:
    b = sum(out["families"][f][r]["both_displaced"] for f in FAM)
    p = sum(out["families"][f][r]["parallel"] for f in FAM)
    pub = d["primary_B"][r]
    ok = (b == pub["both_displaced"] and p == pub["parallel"])
    out["pooled_check"][r] = {"summed_both": b, "summed_parallel": p,
                              "published_both": pub["both_displaced"],
                              "published_parallel": pub["parallel"],
                              "fraction": p / b, "reproduces": bool(ok)}
    print("POOLED %-5s summed %d/%d vs published %d/%d  frac %.4f  reproduces=%s"
          % (r, p, b, pub["parallel"], pub["both_displaced"], p / b, ok))
    assert ok, r

json.dump(out, io.open(DST, "w", encoding="utf-8", newline="\n"), indent=1)
print("\nwrote PARENT_BYFAMILY_r210.json")
