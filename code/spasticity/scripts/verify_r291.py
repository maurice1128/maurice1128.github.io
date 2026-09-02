# -*- coding: utf-8 -*-
"""Independent recomputation of the r291 reading-A endpoint.

Does not read BANDFILL_ENDPOINT_r291.json. Enumerates every plantarflexor-weakness cell across
r276, r285, r287 and r291 by its deposit's result_dir, measures t_end and knee_angle_LmR from
.sto with hipgap_r220.py's convention, keeps those whose t_end lands in [13.58, 17.85], and
compares against the six R151S KV 0.050 cells. Re-derives the ladder and the exhaustive
permutation floor from scratch.

Self-check: the six spastic cells must reproduce LADDER36_r228.json's hip values to < 1e-9 deg.
"""
import io, os, sys, glob, json, math, itertools
sys.path.insert(0, r"C:\Users\maurice\Desktop\spasticity_paper\scone")
import sto_utils as S

RES = r"C:\Users\maurice\Documents\SCONE\results"
PAPER = r"C:\Users\maurice\Desktop\spasticity_paper\paper"
SETTLE, T1 = 1.0, 9.73
BAND = (13.58, 17.85)
SEEDS = list(range(101, 107))
PATTERNS = ["RUN_WEAKPF_r276_cell*.json", "RUN_BANDFILL_r285_cell*.json",
            "RUN_BANDFILL_r287_cell*.json", "RUN_BANDFILL_r291_cell*.json"]


def measure(d):
    g = sorted(glob.glob(os.path.join(d, "*.par.sto")))
    if not g:
        return None
    cols, dat = S.load_sto(g[-1])
    t = list(S.col(cols, dat, "time"))
    t_end = float(t[-1])
    grf, thr = S.grf_vertical(cols, dat, "l")
    idx = S.heel_strikes(t, grf, thresh=thr)
    c = [(a, b) for a, b in zip(idx[:-1], idx[1:]) if t[a] >= SETTLE and t[b] <= T1]
    c = c[:-1] if len(c) >= 2 else c
    if not c or t_end < T1:
        return {"t_end_s": t_end, "knee_angle_LmR": None, "hip_flexion_LmR": None}

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


spastic = []
for s in SEEDS:
    r = measure(by_tag("R151S_s%d" % s))
    r["tag"] = "R151S_s%d" % s
    spastic.append(r)
ref = json.load(open(os.path.join(PAPER, "LADDER36_r228.json")))["per_seed_hip_flexion_LmR"]["S"]
bad = [(SEEDS[i], a["hip_flexion_LmR"], b) for i, (a, b) in enumerate(zip(spastic, ref))
       if abs(a["hip_flexion_LmR"] - b) > 1e-9]
assert not bad, "SELF-CHECK FAILED %s" % bad
print("self-check: R151S hip reproduces LADDER36_r228.json to < 1e-9 deg\n")

weak, seen = [], set()
for pat in PATTERNS:
    for p in sorted(glob.glob(os.path.join(PAPER, pat))):
        dep = json.load(open(p))
        rd = dep.get("result_dir")
        if not rd or rd in seen:
            continue
        # r291's deposits carry BOTH arms: spastic cells have `kv`, weakness cells have `f`.
        # Omitting this filter puts the in-band KV 0.035 cell into the weakness group and
        # flips the verdict to OVERLAP. Found by recomputation disagreeing with the deposit.
        if dep.get("kind") == "spastic" or dep.get("kv") is not None:
            continue
        seen.add(rd)
        d = os.path.join(RES, rd)
        if not os.path.isdir(d):
            continue
        r = measure(d)
        if not r or r["knee_angle_LmR"] is None:
            continue
        r["tag"] = rd.split(".")[0]
        r["in_band"] = BAND[0] <= r["t_end_s"] <= BAND[1]
        weak.append(r)

inband = sorted([r for r in weak if r["in_band"]], key=lambda x: -x["t_end_s"])
print("weakness cells measured: %d   in band [%.2f, %.2f]: %d"
      % (len(weak), BAND[0], BAND[1], len(inband)))
print("%-20s %9s %12s" % ("cell", "t_end", "knee_LmR"))
for r in inband:
    print("%-20s %9.3f %+12.4f" % (r["tag"], r["t_end_s"], r["knee_angle_LmR"]))
print()
for r in spastic:
    print("%-20s %9.3f %+12.4f" % (r["tag"], r["t_end_s"], r["knee_angle_LmR"]))

x = [r["knee_angle_LmR"] for r in spastic]
y = [r["knee_angle_LmR"] for r in inband]
disj = (max(x) < min(y)) or (max(y) < min(x))
gap = max(min(y) - max(x), min(x) - max(y))
pred = disj and all(v > 0 for v in y) and all(v < 0 for v in x)
rung = 2 if pred else 3 if disj else 4
verdict = {2: "DISJOINT-AS-PREDICTED", 3: "DISJOINT-OPPOSITE", 4: "OVERLAP"}[rung]

perm = None
if disj:
    allv = x + y
    n, k = len(allv), len(x)
    tot = cnt = 0
    for sel in itertools.combinations(range(n), k):
        ss = set(sel)
        a = [allv[i] for i in sel]
        b = [allv[i] for i in range(n) if i not in ss]
        g = max(min(b) - max(a), min(a) - max(b))
        tot += 1
        cnt += g >= gap - 1e-12
    perm = {"assignments": tot, "count_ge": cnt, "floor": cnt / tot}

out = {"what": "independent recomputation of r291 reading A; the agent's deposit was not read",
       "self_check": "R151S hip reproduces LADDER36_r228.json to < 1e-9 deg",
       "band": list(BAND), "n_weak_measured": len(weak), "n_weak_in_band": len(inband),
       "weak_in_band": [{"tag": r["tag"], "t_end_s": r["t_end_s"],
                         "knee_angle_LmR": r["knee_angle_LmR"]} for r in inband],
       "spastic": [{"tag": r["tag"], "t_end_s": r["t_end_s"],
                    "knee_angle_LmR": r["knee_angle_LmR"]} for r in spastic],
       "spastic_range": [min(x), max(x)], "weak_range": [min(y), max(y)],
       "disjoint": bool(disj), "gap_deg": gap, "RUNG": rung, "VERDICT": verdict,
       "permutation": perm}
q = os.path.join(PAPER, "VERIFY_R291.json")
json.dump(out, io.open(q, "w", encoding="utf-8"), indent=1)

print()
print("=" * 80)
print("READING A -- knee_angle_LmR, in-band weakness vs R151S KV 0.050")
print("  spastic  n=%-3d %+.4f .. %+.4f" % (len(x), min(x), max(x)))
print("  weakness n=%-3d %+.4f .. %+.4f" % (len(y), min(y), max(y)))
print("  RUNG %d -- %s   gap %+.4f deg" % (rung, verdict, gap))
if perm:
    print("  exhaustive C(%d,%d)=%d: %d reach the gap -> floor 1/%d"
          % (len(x) + len(y), len(x), perm["assignments"], perm["count_ge"],
             int(round(1 / perm["floor"])) if perm["floor"] else 0))
print("\nwrote %s (%d bytes)" % (q, os.path.getsize(q)))
