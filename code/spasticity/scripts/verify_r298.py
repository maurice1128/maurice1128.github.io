# -*- coding: utf-8 -*-
"""Independent recomputation of the r289/r292 matched-at-completion endpoints.

Does not read MATCHED20_ENDPOINT_r298.json. Resolves every cell by its deposit's result_dir,
re-measures knee_angle_LmR and hip_flexion_LmR from .sto with hipgap_r220.py's convention, and
re-evaluates the two readings from scratch:

  reading C  CLINICAL PAIR      r289 spastic completers vs the 36 dorsiflexor-weakness cells
  reading P  ANATOMY-MATCHED    r289 spastic completers vs plantarflexor-weakness COMPLETERS
                                pooled across r276, r285 and r287

Admission: t_end == 20.000 s exactly for the spastic side, and for the plantarflexor side.
The 36 dorsiflexor cells all complete by construction (SPEED_LADDER_r217.json).

Self-check: the six R151S spastic cells must reproduce LADDER36_r228.json's hip values to
< 1e-9 deg, or the script refuses to run.
"""
import io, os, sys, glob, json, math, itertools
sys.path.insert(0, r"C:\Users\maurice\Desktop\spasticity_paper\scone")
import numpy as np, sto_utils as S

RES = r"C:\Users\maurice\Documents\SCONE\results"
PAPER = r"C:\Users\maurice\Desktop\spasticity_paper\paper"
SETTLE, T1 = 1.0, 9.73
SEEDS = list(range(101, 107))
DF_ARMS = [("W800", "R151W"), ("W870", "R174W870"), ("W892", "R174W892"),
           ("W900", "R169W090"), ("W915", "R174W915"), ("W950", "R169W095")]


def measure(d):
    cols, dat = S.load_sto(sorted(glob.glob(os.path.join(d, "*.par.sto")))[-1])
    t = list(S.col(cols, dat, "time"))
    t_end = float(t[-1])
    grf, thr = S.grf_vertical(cols, dat, "l")
    idx = S.heel_strikes(t, grf, thresh=thr)
    c = [(a, b) for a, b in zip(idx[:-1], idx[1:]) if t[a] >= SETTLE and t[b] <= T1]
    c = c[:-1] if len(c) >= 2 else c
    if not c or t_end < T1:
        return None

    def rom(ch):
        v = S.col(cols, dat, ch)
        return sum(math.degrees(max(v[a:b + 1]) - min(v[a:b + 1])) for a, b in c) / len(c)

    return {"t_end_s": t_end,
            "knee_angle_LmR": rom("knee_angle_l") - rom("knee_angle_r"),
            "hip_flexion_LmR": rom("hip_flexion_l") - rom("hip_flexion_r")}


def by_tag(tag):
    ds = [x for x in glob.glob(os.path.join(RES, tag + ".*")) if os.path.isdir(x)
          and os.path.exists(os.path.join(x, "history.txt"))
          and sum(1 for _ in io.open(os.path.join(x, "history.txt"), errors="replace")) >= 91
          and glob.glob(os.path.join(x, "*.par.sto"))]
    assert len(ds) == 1, "%s -> %d dirs" % (tag, len(ds))
    return ds[0]


# self-check
spas_ship = [measure(by_tag("R151S_s%d" % s)) for s in SEEDS]
ref = json.load(open(os.path.join(PAPER, "LADDER36_r228.json")))["per_seed_hip_flexion_LmR"]["S"]
bad = [(SEEDS[i], a["hip_flexion_LmR"], b) for i, (a, b) in enumerate(zip(spas_ship, ref))
       if abs(a["hip_flexion_LmR"] - b) > 1e-9]
assert not bad, "SELF-CHECK FAILED %s" % bad
print("self-check: R151S hip reproduces LADDER36_r228.json to < 1e-9 deg\n")


def from_deposits(pattern, want_complete):
    out = []
    for p in sorted(glob.glob(os.path.join(PAPER, pattern))):
        dep = json.load(open(p))
        d = os.path.join(RES, dep["result_dir"])
        if not os.path.isdir(d) or not glob.glob(os.path.join(d, "*.par.sto")):
            continue
        r = measure(d)
        if not r:
            continue
        r["id"] = os.path.basename(p).replace(".json", "").split("_")[-1]
        r["tag"] = dep["result_dir"].split(".")[0]
        r["completes"] = abs(r["t_end_s"] - 20.0) < 1e-9
        if want_complete and not r["completes"]:
            continue
        out.append(r)
    return out


spas289 = from_deposits("RUN_MATCHED20_r289_cell*.json", True)
all289 = from_deposits("RUN_MATCHED20_r289_cell*.json", False)
wpf = (from_deposits("RUN_WEAKPF_r276_cell*.json", True)
       + from_deposits("RUN_BANDFILL_r285_cell*.json", True)
       + from_deposits("RUN_BANDFILL_r287_cell*.json", True))
df = []
for key, pref in DF_ARMS:
    for s in SEEDS:
        r = measure(by_tag("%s_s%d" % (pref, s)))
        if r:
            r["id"] = "%s_s%d" % (key, s); r["completes"] = abs(r["t_end_s"] - 20.0) < 1e-9
            df.append(r)

print("r289 cells measured   : %d   completing 20.000 s: %d" % (len(all289), len(spas289)))
print("dorsiflexor weakness  : %d   completing: %d" % (len(df), sum(c["completes"] for c in df)))
print("plantarflexor weakness completers pooled r276+r285+r287: %d" % len(wpf))
print("  " + ", ".join(sorted(c["tag"] for c in wpf)))


def ladder(a, b, ch, name):
    x = [c[ch] for c in a]
    y = [c[ch] for c in b]
    disj = (max(x) < min(y)) or (max(y) < min(x))
    gap = max(min(y) - max(x), min(x) - max(y))
    pred = disj and all(v > 0 for v in y) and all(v < 0 for v in x)
    rung = 2 if pred else 3 if disj else 4
    verdict = {2: "DISJOINT-AS-PREDICTED", 3: "DISJOINT-OPPOSITE", 4: "OVERLAP"}[rung]
    out = {"name": name, "channel": ch, "n_spastic": len(x), "n_weak": len(y),
           "spastic_range": [min(x), max(x)], "weak_range": [min(y), max(y)],
           "disjoint": bool(disj), "gap_deg": gap, "RUNG": rung, "VERDICT": verdict}
    if disj:
        allv = x + y
        n, k = len(allv), len(x)
        cnt = 0
        tot = 0
        for sel in itertools.combinations(range(n), k):
            ss = set(sel)
            p = [allv[i] for i in sel]
            q = [allv[i] for i in range(n) if i not in ss]
            g = max(min(q) - max(p), min(p) - max(q))
            tot += 1
            cnt += g >= gap - 1e-12
        out["permutation"] = {"assignments": tot, "count_ge": cnt, "floor": cnt / tot}
    return out


blocks = [ladder(spas289, df, "knee_angle_LmR", "reading C -- CLINICAL PAIR (spastic vs dorsiflexor weak)"),
          ladder(spas289, wpf, "knee_angle_LmR", "reading P -- ANATOMY-MATCHED (spastic vs plantarflexor weak)"),
          ladder(spas289, df, "hip_flexion_LmR", "SECONDARY hip, clinical pair -- the shipped headline"),
          ladder(spas289, wpf, "hip_flexion_LmR", "SECONDARY hip, anatomy-matched")]

for b in blocks:
    print()
    print("=" * 86)
    print("%s   [%s]" % (b["name"], b["channel"]))
    print("  spastic  n=%-3d %+.4f .. %+.4f" % (b["n_spastic"], *b["spastic_range"]))
    print("  weakness n=%-3d %+.4f .. %+.4f" % (b["n_weak"], *b["weak_range"]))
    print("  RUNG %d -- %s%s" % (b["RUNG"], b["VERDICT"],
                                 ("   gap %+.4f" % b["gap_deg"]) if b["disjoint"] else ""))
    if "permutation" in b:
        pm = b["permutation"]
        print("  exhaustive C(%d,%d)=%d: %d reach the gap -> floor %.3e"
              % (b["n_spastic"] + b["n_weak"], b["n_spastic"], pm["assignments"],
                 pm["count_ge"], pm["floor"]))

out = {"what": "independent recomputation of r289/r292; MATCHED20_ENDPOINT_r298.json not read",
       "self_check": "R151S hip reproduces LADDER36_r228.json to < 1e-9 deg",
       "n": {"r289_measured": len(all289), "r289_completing": len(spas289),
             "dorsiflexor": len(df), "plantarflexor_completers": len(wpf)},
       "r289_t_end": sorted(c["t_end_s"] for c in all289),
       "blocks": blocks}
p = os.path.join(PAPER, "VERIFY_R298.json")
json.dump(out, io.open(p, "w", encoding="utf-8"), indent=1)
print("\nwrote %s (%d bytes)" % (p, os.path.getsize(p)))
