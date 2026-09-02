# -*- coding: utf-8 -*-
"""Is the shipped discriminator a lesion-type signal or a fall signature?

The shipped 3D result separates 6 spastic cells from 36 dorsiflexor-weakness cells on
`hip_flexion_LmR`, seed-level disjoint, gap +1.0128 deg (LADDER36_r228.json). This script
asks whether SIMULATED DURATION explains that separation just as well as lesion type does,
using only numbers already on disk. Nothing is re-run and nothing is re-simulated.

Sources, both read-only:
  SPEED_LADDER_r217.json   per-cell dur_s and cycles for the spastic arm and six weakness doses
  LADDER36_r228.json       per-cell hip_flexion_LmR for control, spastic and six weakness doses

Three things are measured:
  1. the duration distribution of each arm, and whether the two arms overlap at all
  2. Spearman rho of hip_flexion_LmR against dur_s WITHIN the spastic arm, where duration varies
  3. the same within the weakness arm, where it may not

If the arms do not overlap in duration, then "spastic" and "fell early" are the same partition
of the corpus, and no test computed on this corpus can prefer one explanation over the other.
That is a property of the design, not a result, and it holds however small the permutation
proportion is.

UNREGISTERED, POST-HOC. Added after WEAK-PF cell 0 was measured at 16.21 s -- the first
weakness cell in the project that falls -- which is what made the question answerable at all.
No registration is amended; this deposits alongside.
"""
import os, json

PAPER = r"C:\Users\maurice\Desktop\spasticity_paper\paper"
r217 = json.load(open(os.path.join(PAPER, "SPEED_LADDER_r217.json")))
r228 = json.load(open(os.path.join(PAPER, "LADDER36_r228.json")))

# r217 arm key -> r228 arm key. r217 has no control arm; that gap is recorded, not filled.
ARMMAP = {
    "spastic KV 0.050": "S",
    "weak x0.800": "W800",
    "weak x0.870": "W870",
    "weak x0.892": "W892",
    "weak x0.900": "W900",
    "weak x0.915": "W915",
    "weak x0.950": "W950",
}


def rank(xs):
    order = sorted(range(len(xs)), key=lambda i: xs[i])
    r = [0.0] * len(xs)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and xs[order[j + 1]] == xs[order[i]]:
            j += 1
        avg = (i + j) / 2.0 + 1.0
        for k in range(i, j + 1):
            r[order[k]] = avg
        i = j + 1
    return r


def spearman(x, y):
    """Pearson correlation of the ranks; ties get average ranks. Returns None if either
    variable has no variance, because a correlation is undefined there rather than zero."""
    if len(set(x)) < 2 or len(set(y)) < 2:
        return None
    rx, ry = rank(x), rank(y)
    n = len(rx)
    mx, my = sum(rx) / n, sum(ry) / n
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    dx = sum((a - mx) ** 2 for a in rx) ** 0.5
    dy = sum((b - my) ** 2 for b in ry) ** 0.5
    return num / (dx * dy) if dx and dy else None


arms, spastic_dur, weak_dur = {}, [], []
for k217, k228 in ARMMAP.items():
    per = r217["arms"][k217]["per_seed"]
    seeds = [p["seed"] for p in per]
    dur = [float(p["dur_s"]) for p in per]
    cyc = [int(p["cycles"]) for p in per]
    lmr = [float(v) for v in r228["per_seed_hip_flexion_LmR"][k228]]
    assert len(dur) == len(lmr) == 6, k228
    rho = spearman(dur, lmr)
    arms[k228] = {
        "source_arm_key_r217": k217,
        "seeds": seeds,
        "dur_s": dur,
        "cycles": cyc,
        "hip_flexion_LmR": lmr,
        "dur_min": min(dur), "dur_max": max(dur),
        "dur_constant": len(set(dur)) == 1,
        "spearman_LmR_vs_dur": rho,
        "spearman_undefined_reason": (None if rho is not None else
                                      "duration has no variance within this arm"),
    }
    (spastic_dur if k228 == "S" else weak_dur).extend(dur)

pooled_weak_lmr, pooled_weak_dur = [], []
for k in ("W800", "W870", "W892", "W900", "W915", "W950"):
    pooled_weak_lmr.extend(arms[k]["hip_flexion_LmR"])
    pooled_weak_dur.extend(arms[k]["dur_s"])
s_lmr, s_dur = arms["S"]["hip_flexion_LmR"], arms["S"]["dur_s"]

overlap = not (max(spastic_dur) < min(weak_dur) or max(weak_dur) < min(spastic_dur))

out = {
    "question": "does simulated duration explain the shipped hip_flexion_LmR separation as well as lesion type does",
    "status": "UNREGISTERED, POST-HOC; added after WEAK-PF cell 0 measured 16.21 s",
    "inputs_read_only": ["SPEED_LADDER_r217.json", "LADDER36_r228.json"],
    "nothing_resimulated": True,
    "per_arm": arms,
    "duration_separation": {
        "spastic_dur_range": [min(spastic_dur), max(spastic_dur)],
        "weakness_dur_range": [min(weak_dur), max(weak_dur)],
        "arms_overlap_in_duration": overlap,
        "n_spastic": len(spastic_dur), "n_weakness": len(weak_dur),
        "weakness_duration_is_constant": len(set(weak_dur)) == 1,
        "consequence": (
            "spastic and fell-early are the SAME partition of this corpus"
            if not overlap else
            "the arms overlap in duration, so duration and lesion type are separable here"),
    },
    "within_arm": {
        "spastic": {
            "n": len(s_dur),
            "spearman_LmR_vs_dur": spearman(s_dur, s_lmr),
            "note": "duration varies within this arm, so the correlation is defined",
        },
        "weakness_pooled": {
            "n": len(pooled_weak_dur),
            "spearman_LmR_vs_dur": spearman(pooled_weak_dur, pooled_weak_lmr),
            "note": "if duration is constant across all 36, the correlation is undefined, not null",
        },
    },
    "gaps_recorded_not_filled": [
        "SPEED_LADDER_r217.json contains no control arm, so control durations are absent here.",
        "n = 6 within the spastic arm; a rho on six points is reported as a magnitude and a "
        "direction only, with no p-value and no inference attached.",
    ],
}

p = os.path.join(PAPER, "CONFOUND_DURATION_r277.json")
with open(p, "w") as f:
    json.dump(out, f, indent=1)

print("=" * 78)
print("DURATION AS A RIVAL EXPLANATION FOR THE SHIPPED hip_flexion_LmR SEPARATION")
print("=" * 78)
print("%-8s %-6s %-18s %-8s %s" % ("arm", "n", "dur_s range", "const?", "rho(LmR, dur)"))
for k in ("S", "W800", "W870", "W892", "W900", "W915", "W950"):
    a = arms[k]
    rho = a["spearman_LmR_vs_dur"]
    print("%-8s %-6d %-18s %-8s %s" % (
        k, len(a["dur_s"]), "%.2f - %.2f" % (a["dur_min"], a["dur_max"]),
        "yes" if a["dur_constant"] else "no",
        "undefined" if rho is None else "%+.4f" % rho))
print()
print("spastic  duration %.2f - %.2f s   (n=%d)" % (min(spastic_dur), max(spastic_dur), len(spastic_dur)))
print("weakness duration %.2f - %.2f s   (n=%d)" % (min(weak_dur), max(weak_dur), len(weak_dur)))
print("arms overlap in duration : %s" % overlap)
print()
rs = out["within_arm"]["spastic"]["spearman_LmR_vs_dur"]
rw = out["within_arm"]["weakness_pooled"]["spearman_LmR_vs_dur"]
print("within spastic  (n=6)  rho(LmR, dur) = %s" % ("undefined" if rs is None else "%+.4f" % rs))
print("within weakness (n=36) rho(LmR, dur) = %s" % ("undefined" if rw is None else "%+.4f" % rw))
print()
print("wrote %s (%d bytes)" % (p, os.path.getsize(p)))
