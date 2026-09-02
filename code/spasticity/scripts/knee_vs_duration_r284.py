# -*- coding: utf-8 -*-
"""Is the knee separation type, or duration again?

MATCHED_FALLERS_r282.json found 6 of 16 channels separate spastic from plantarflexor weakness
among fallers, best knee_angle_LmR at +2.9481 deg, familywise 1 of 210. But the two arms are
NOT matched on how long they stayed up: spastic fell at 13.58-17.85 s, WEAK-PF at 10.79-16.21 s.
Duration already ate one discriminator in this project (CONFOUND_DURATION_r277, SEPARATION_r280).
This asks whether it eats this one too.

For each channel that separated, over the ten fallers pooled:
  rho(channel, t_end)         does the channel simply track how long the cell lasted?
  within-arm rho              does it track duration INSIDE an arm, where type is constant?
  overlap-band listing        the cells of both arms inside the duration range they share

A channel that separates type but does NOT track duration within either arm is doing something
the hip channel was not. A channel whose values line up with t_end regardless of arm is the
same artefact wearing a different name.

Reads MATCHED_FALLERS_r282.json only. Computes nothing new. UNREGISTERED, POST-HOC.
"""
import io, os, json

PAPER = r"C:\Users\maurice\Desktop\spasticity_paper\paper"
d = json.load(open(os.path.join(PAPER, "MATCHED_FALLERS_r282.json")))
b = d["blocks"][0]
CH = b["disjoint_channels"]
A_ids, B_ids = b["A_ids"], b["B_ids"]
A_te, B_te = b["A_t_end"], b["B_t_end"]


def rank(xs):
    o = sorted(range(len(xs)), key=lambda i: xs[i]); r = [0.0] * len(xs); i = 0
    while i < len(o):
        j = i
        while j + 1 < len(o) and xs[o[j + 1]] == xs[o[i]]:
            j += 1
        for k in range(i, j + 1):
            r[o[k]] = (i + j) / 2.0 + 1.0
        i = j + 1
    return r


def spearman(x, y):
    if len(x) < 3 or len(set(x)) < 2 or len(set(y)) < 2:
        return None
    rx, ry = rank(x), rank(y); n = len(rx)
    mx, my = sum(rx) / n, sum(ry) / n
    num = sum((p - mx) * (q - my) for p, q in zip(rx, ry))
    dx = sum((p - mx) ** 2 for p in rx) ** 0.5
    dy = sum((q - my) ** 2 for q in ry) ** 0.5
    return num / (dx * dy) if dx and dy else None


rows = {}
print("%-20s %10s %10s %10s   %s" % ("channel", "rho pooled", "rho in S", "rho in WPF", "reading"))
for ch in CH:
    a = b["channels"][ch]["A_seeds"]
    w = b["channels"][ch]["B_seeds"]
    rp = spearman(A_te + B_te, a + w)
    ra = spearman(A_te, a)
    rw = spearman(B_te, w)
    # A duration artefact shows up as a strong pooled association that is ALSO present inside
    # at least one arm, where lesion type cannot vary.
    strong_within = max([abs(x) for x in (ra, rw) if x is not None] or [0.0])
    reading = ("tracks duration within an arm" if strong_within >= 0.8 else
               "no strong within-arm duration association")
    rows[ch] = {"rho_pooled_vs_tend": rp, "rho_within_spastic": ra, "rho_within_weakpf": rw,
                "max_abs_within_arm_rho": strong_within, "reading": reading,
                "spastic_seeds": a, "weakpf_seeds": w}
    print("%-20s %10s %10s %10s   %s" % (
        ch,
        "n/a" if rp is None else "%+.4f" % rp,
        "n/a" if ra is None else "%+.4f" % ra,
        "n/a" if rw is None else "%+.4f" % rw,
        reading))

lo = max(min(A_te), min(B_te))
hi = min(max(A_te), max(B_te))
inA = [(i, A_ids[i], A_te[i]) for i in range(len(A_te)) if lo <= A_te[i] <= hi]
inB = [(i, B_ids[i], B_te[i]) for i in range(len(B_te)) if lo <= B_te[i] <= hi]

print()
print("duration-overlap band [%.2f, %.2f] s : spastic %d cells, WEAK-PF %d cells"
      % (lo, hi, len(inA), len(inB)))
print("  the band is one-sided because the WEAK-PF fallers skew shorter; more f=0.20 cells")
print("  will not help, they fall below the %s s window and are excluded by the guard."
      % d["window"][1])

print()
print("all ten fallers, ordered by how long they stayed up:")
print("  %-10s %-8s %8s %12s %12s" % ("cell", "arm", "t_end", "knee_LmR", "hip_LmR"))
kn = b["channels"]["knee_angle_LmR"]
hp = b["channels"]["hip_flexion_LmR"]
allr = ([(A_ids[i], "SPASTIC", A_te[i], kn["A_seeds"][i], hp["A_seeds"][i]) for i in range(len(A_te))]
        + [(B_ids[i], "WEAK_PF", B_te[i], kn["B_seeds"][i], hp["B_seeds"][i]) for i in range(len(B_te))])
for cid, arm, te, k, h in sorted(allr, key=lambda x: x[2]):
    print("  %-10s %-8s %8.3f %+12.4f %+12.4f" % (cid, arm, te, k, h))

out = {
    "question": "is the knee separation lesion type, or duration again",
    "status": "UNREGISTERED, POST-HOC; reads MATCHED_FALLERS_r282.json only",
    "n_fallers": {"spastic": len(A_te), "weak_pf": len(B_te)},
    "t_end": {"spastic": A_te, "weak_pf": B_te},
    "per_channel": rows,
    "duration_overlap_band": {
        "band_s": [lo, hi],
        "spastic_cells_in_band": [x[1] for x in inA],
        "weakpf_cells_in_band": [x[1] for x in inB],
        "evaluable": bool(len(inA) >= 2 and len(inB) >= 2),
        "why_not_fixable_by_more_cells": (
            "the remaining f=0.20 cells fall below the 9.73 s window and are excluded by the "
            "measurement guard, so they cannot extend the band downward for the spastic arm"),
    },
    "limits": [
        "n = 6 spastic vs 4 weak-PF; a within-arm rho on four points is not an estimate",
        "the exhaustive familywise proportion 1/210 is the FLOOR of this design, not a small "
        "p-value in the usual sense -- no arrangement of ten cells can do better",
        "16 channels tested, post-hoc, on a comparison chosen after seeing the hip result fail",
    ],
}
p = os.path.join(PAPER, "KNEE_VS_DURATION_r284.json")
json.dump(out, io.open(p, "w", encoding="utf-8"), indent=1)
print("\nwrote %s (%d bytes)" % (p, os.path.getsize(p)))
