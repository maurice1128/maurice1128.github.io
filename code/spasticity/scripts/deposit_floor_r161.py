# -*- coding: utf-8 -*-
"""Deposit the LEAD's own numbers into SCREEN_r153.json.

Round 160 found that every quantity in the leading claim -- the observed maximum
|AUC - 0.5| of 0.22 and the 5v5 resolution floor of 0.42 -- exists only in prose,
while every quantity in the deposit belongs to the superseded body. A lead whose
numbers have no container is the class this project's register was built to catch,
and it was sitting in our own headline.

Both are COMPUTED here, not transcribed.
"""
import io, os, json, itertools

P = r"C:\Users\maurice\Desktop\spasticity_paper\paper"
F = os.path.join(P, "SCREEN_r153.json")

d = json.load(io.open(F, encoding="utf-8"))

# (a) the observed maximum |AUC - 0.5| over every residual in the screen
obs = max(abs(r["res_auc"] - 0.5) for r in d["screen"])
worst = [r["name"] for r in d["screen"] if abs(r["res_auc"] - 0.5) == obs]

# (b) the 5v5 resolution floor: enumerate all C(10,5) splits, find the smallest
#     |AUC - 0.5| whose exact two-sided p is < 0.05
counts = {}
for comb in itertools.combinations(range(10), 5):
    a = set(comb)
    U = sum(1 for x in a for y in range(10) if y not in a and x > y)
    counts[U] = counts.get(U, 0) + 1
tot = sum(counts.values())
floor = None
for U in sorted(counts):
    p = sum(c for u, c in counts.items() if abs(u - 12.5) >= abs(U - 12.5) - 1e-9) / float(tot)
    if p < 0.05:
        # the floor is the SMALLEST resolvable effect, not the largest.
        # An earlier revision of this script used max() and returned 0.500
        # (perfect separation) instead of 0.420 -- caught only because the
        # expected value was known.
        v = abs(U / 25.0 - 0.5)
        floor = v if floor is None else min(floor, v)
best_p = min(sum(c for u, c in counts.items() if abs(u - 12.5) >= abs(U - 12.5) - 1e-9) / float(tot)
             for U in counts)

d["lead_numbers"] = {
    "what": ("the two quantities the leading claim turns on; both computed by "
             "scone/deposit_floor_r161.py, neither transcribed"),
    "observed_max_abs_auc_minus_half": obs,
    "observed_max_at": worst,
    "resolution_floor_5v5_abs_auc_minus_half": floor,
    "resolution_floor_note": ("smallest |AUC-0.5| whose exact two-sided Mann-Whitney p is < 0.05 "
                              "at 5 v 5, enumerated over all %d splits" % tot),
    "min_attainable_two_sided_p_5v5": best_p,
    "observed_over_floor": obs / floor,
}
json.dump(d, io.open(F, "w", encoding="utf-8"), indent=1, sort_keys=True)

print("observed max |AUC-0.5| : %.3f   at %r" % (obs, worst))
print("resolution floor 5v5   : %.3f   (AUC %.3f or %.3f)" % (floor, 0.5 - floor, 0.5 + floor))
print("min attainable p       : %.6f" % best_p)
print("observed / floor       : %.3f" % (obs / floor))
print("wrote", F, "->", os.path.getsize(F), "bytes")
