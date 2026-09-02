# -*- coding: utf-8 -*-
"""THE MATCHED-OUTCOME TEST: among cells that FELL, does any channel separate type?

This is the project's question asked in the one design that can answer it.

Why it is the right design. SEPARATION_r280.json showed hip_flexion_LmR separates cells that
fall from cells that do not, and that the shipped spastic-vs-weakness disjointness collapses
into a 0.9049 deg overlap once a single falling weakness cell is added. The shipped corpus
could not tell "spasticity" from "fell over" because it contained no weakness cell that fell.

The WEAK-PF arm supplies them. So restrict to fallers and the outcome is matched. What is
left differing between the arms is:

  SPASTIC   a velocity-dependent stretch reflex on soleus and gastrocnemius, left leg
  WEAK-PF   reduced max isometric force on soleus and gastrocnemius, left leg

Same muscles, same side, same body, same controller family, same optimiser, same horizon,
and now the same outcome. Only the LESION TYPE differs. If no channel separates them here,
then the honest claim is that gait kinematics in this model do not identify type once
stability is controlled -- and the shipped separation was reading stability.

Reported for all 16 channels, exhaustively, with no selection:
  per-arm seed values, arm means, seed-level disjointness and its gap
  an exhaustive permutation null over every label assignment, familywise across channels
  the same restricted to a duration-overlap band, since the two arms' fall times differ

SELF-CHECK. Before anything is reported the script recomputes hip_flexion_LmR for the six
spastic cells and requires an exact match against LADDER36_r228.json. If the measurement path
has drifted from the shipped one the script refuses to run rather than reporting a number that
looks like the shipped one but is not.

UNREGISTERED, POST-HOC. Read-only; nothing re-simulated. Run at FINAL n.
"""
import io, os, sys, glob, json, math, itertools
sys.path.insert(0, r"C:\Users\maurice\Desktop\spasticity_paper\scone")
import numpy as np, sto_utils as S

RES = r"C:\Users\maurice\Documents\SCONE\results"
PAPER = r"C:\Users\maurice\Desktop\spasticity_paper\paper"
SETTLE, T1 = 1.0, 9.73
SEEDS = list(range(101, 107))
PAIR = ["ankle_angle", "knee_angle", "hip_flexion", "hip_adduction"]
UNP = ["pelvis_list", "pelvis_rotation", "lumbar_bending"]
CH = ([p + s for p in PAIR for s in ("_l", "_r")] + UNP + ["cycle_time"]
      + [p + "_LmR" for p in PAIR])          # 16 channels, channels_g2_r219.py's list


def meas(sto):
    """channels_g2_r219.py's meas(), unchanged: per-cycle mean ROM in degrees over the
    registered window, plus cycle_time and the four LmR differences."""
    cols, dat = S.load_sto(sto)
    t = list(S.col(cols, dat, "time"))
    grf, thr = S.grf_vertical(cols, dat, "l")
    idx = S.heel_strikes(t, grf, thresh=thr)
    c = [(idx[k], idx[k + 1]) for k in range(len(idx) - 1)
         if t[idx[k]] >= SETTLE and t[idx[k + 1]] <= T1]
    c = c[:-1] if len(c) >= 2 else c
    if not c:
        return None, float(t[-1])
    o = {}
    for ch in [p + s for p in PAIR for s in ("_l", "_r")] + UNP:
        v = S.col(cols, dat, ch)
        o[ch] = sum(math.degrees(max(v[a:b + 1]) - min(v[a:b + 1])) for a, b in c) / len(c)
    o["cycle_time"] = (t[c[-1][1]] - t[c[0][0]]) / len(c)
    for p in PAIR:
        o[p + "_LmR"] = o[p + "_l"] - o[p + "_r"]
    return o, float(t[-1])


def sto_of(d):
    g = sorted(glob.glob(os.path.join(d, "*.par.sto")))
    return g[-1] if g else None


def find_dir(tag):
    ds = [x for x in glob.glob(os.path.join(RES, tag + ".*")) if os.path.isdir(x)
          and os.path.exists(os.path.join(x, "history.txt"))
          and sum(1 for _ in io.open(os.path.join(x, "history.txt"), errors="replace")) >= 91
          and glob.glob(os.path.join(x, "*.par.sto"))]
    return ds[0] if ds else None


# ---------------------------------------------------------------- spastic arm + self-check
spastic = []
for s in SEEDS:
    d = find_dir("R151S_s%d" % s)
    assert d, "missing spastic seed %d" % s
    o, te = meas(sto_of(d))
    assert o is not None, "spastic seed %d has no cycle in the window" % s
    spastic.append({"id": "S_s%d" % s, "arm": "SPASTIC", "t_end_s": te, "ch": o})

ref = json.load(open(os.path.join(PAPER, "LADDER36_r228.json")))["per_seed_hip_flexion_LmR"]["S"]
got = [c["ch"]["hip_flexion_LmR"] for c in spastic]
bad = [(i, a, b) for i, (a, b) in enumerate(zip(got, ref)) if abs(a - b) > 1e-9]
if bad:
    print("SELF-CHECK FAILED -- measurement path has drifted from the shipped one:")
    for i, a, b in bad:
        print("  seed %d: recomputed %+.12f vs shipped %+.12f  (delta %.3e)" % (SEEDS[i], a, b, a - b))
    sys.exit(1)
print("self-check: hip_flexion_LmR reproduces LADDER36_r228.json for all 6 spastic cells "
      "to < 1e-9 deg -- measurement path is the shipped one\n")

# ---------------------------------------------------------------- WEAK-PF arm
wpf, wpf_short = [], []
for p in sorted(glob.glob(os.path.join(PAPER, "RUN_WEAKPF_r276_cell*.json"))):
    dep = json.load(open(p))
    d = os.path.join(RES, dep["result_dir"])
    sto = sto_of(d) if os.path.isdir(d) else None
    if not sto:
        continue
    o, te = meas(sto)
    rec = {"id": "WPF_c%02d" % dep["cell"], "arm": "WEAK_PF", "t_end_s": te,
           "f": dep["f"], "seed": dep["seed"], "ch": o}
    # Same guard as r278/r281: a window truncated by the cell's own collapse is not measured.
    if o is None or te < T1:
        rec["excluded"] = ("t_end %.3f s short of the %.2f s window" % (te, T1) if te < T1
                           else "no complete cycle in the window")
        wpf_short.append(rec)
    else:
        wpf.append(rec)

print("spastic cells      : %d  (t_end %.2f - %.2f s)"
      % (len(spastic), min(c["t_end_s"] for c in spastic), max(c["t_end_s"] for c in spastic)))
print("WEAK-PF measured   : %d" % len(wpf))
for r in wpf:
    print("   %-10s f=%.2f s%d  t_end %6.3f s%s"
          % (r["id"], r["f"], r["seed"], r["t_end_s"], "  FELL" if r["t_end_s"] < 20.0 else "  full"))
print("WEAK-PF excluded   : %d" % len(wpf_short))
for r in wpf_short:
    print("   %-10s f=%.2f s%d  t_end %6.3f s  -- %s" % (r["id"], r["f"], r["seed"], r["t_end_s"], r["excluded"]))


def analyse(A, B, label, note):
    """A vs B on all 16 channels: seed-level disjointness plus an exhaustive permutation null."""
    n, k = len(A) + len(B), len(A)
    if len(A) < 2 or len(B) < 2:
        return {"label": label, "note": note, "n_A": len(A), "n_B": len(B),
                "not_evaluable": "each arm needs at least two cells"}
    allc = A + B
    res, best_obs = {}, {}
    for ch in CH:
        a = [c["ch"][ch] for c in A]
        b = [c["ch"][ch] for c in B]
        gap = max(min(b) - max(a), min(a) - max(b))     # positive only when disjoint
        res[ch] = {"A_seeds": a, "B_seeds": b,
                   "A_mean": float(np.mean(a)), "B_mean": float(np.mean(b)),
                   "A_range": [min(a), max(a)], "B_range": [min(b), max(b)],
                   "seed_gap_deg": gap, "disjoint": bool(gap > 0)}
        best_obs[ch] = gap

    idxs = list(range(n))
    perms = list(itertools.combinations(idxs, k))
    fam_hit, per_ch_hit = 0, {ch: 0 for ch in CH}
    obs_best = max(best_obs.values())
    for sel in perms:
        ssel = set(sel)
        pa = [allc[i] for i in sel]
        pb = [allc[i] for i in idxs if i not in ssel]
        hit_any = False
        for ch in CH:
            x = [c["ch"][ch] for c in pa]
            y = [c["ch"][ch] for c in pb]
            g = max(min(y) - max(x), min(x) - max(y))
            if g >= best_obs[ch] - 1e-12:
                per_ch_hit[ch] += 1
            if g >= obs_best - 1e-12:
                hit_any = True
        fam_hit += hit_any
    disj = sorted([ch for ch in CH if res[ch]["disjoint"]],
                  key=lambda c: -res[c]["seed_gap_deg"])
    return {
        "label": label, "note": note, "n_A": len(A), "n_B": len(B),
        "A_ids": [c["id"] for c in A], "B_ids": [c["id"] for c in B],
        "A_t_end": [c["t_end_s"] for c in A], "B_t_end": [c["t_end_s"] for c in B],
        "channels": res,
        "disjoint_channels": disj,
        "n_disjoint_of_16": len(disj),
        "permutation": {
            "method": "exhaustive over C(%d,%d)" % (n, k),
            "assignments": len(perms),
            "familywise_count_ge_best_observed": fam_hit,
            "familywise_proportion": fam_hit / len(perms),
            "best_observed_gap_deg": obs_best,
            "per_channel_count_ge_observed": per_ch_hit,
        },
    }


fall_S = [c for c in spastic if c["t_end_s"] < 20.0]
fall_W = [c for c in wpf if c["t_end_s"] < 20.0]

blocks = [analyse(fall_S, fall_W, "MATCHED ON OUTCOME: fallers only, spastic vs WEAK-PF",
                  "both arms lesion the same two muscles on the same side; only type differs")]

# Duration-overlap band: keep only cells inside the range both arms occupy.
if fall_S and fall_W:
    lo = max(min(c["t_end_s"] for c in fall_S), min(c["t_end_s"] for c in fall_W))
    hi = min(max(c["t_end_s"] for c in fall_S), max(c["t_end_s"] for c in fall_W))
    bS = [c for c in fall_S if lo <= c["t_end_s"] <= hi]
    bW = [c for c in fall_W if lo <= c["t_end_s"] <= hi]
    blocks.append(analyse(bS, bW,
                          "DURATION-OVERLAP BAND [%.2f, %.2f] s" % (lo, hi),
                          "the two arms' fall times differ; this keeps only the band both occupy"))

out = {
    "question": "among cells that FELL, does any of 16 channels separate spastic from plantarflexor weakness",
    "status": "UNREGISTERED, POST-HOC; read-only; nothing re-simulated",
    "self_check": "hip_flexion_LmR reproduces LADDER36_r228.json for all 6 spastic cells to < 1e-9 deg",
    "window": [SETTLE, T1], "channels_tested": CH,
    "guard": "a cell whose t_end is short of the window end is not measured (r278/r281 rule)",
    "weak_pf_excluded": [{"id": r["id"], "f": r["f"], "seed": r["seed"],
                          "t_end_s": r["t_end_s"], "reason": r["excluded"]} for r in wpf_short],
    "blocks": blocks,
    "incomplete_warning": ("run at FINAL n; if the WEAK-PF batch was still running this is a "
                           "partial read and the permutation null is over fewer assignments"),
}
p = os.path.join(PAPER, "MATCHED_FALLERS_r282.json")
json.dump(out, io.open(p, "w", encoding="utf-8"), indent=1)

for b in blocks:
    print("\n" + "=" * 92)
    print(b["label"])
    print("=" * 92)
    if b.get("not_evaluable"):
        print("  NOT EVALUABLE: %s  (n = %d vs %d)" % (b["not_evaluable"], b["n_A"], b["n_B"]))
        continue
    print("  spastic n=%d  t_end %s" % (b["n_A"], ", ".join("%.2f" % x for x in b["A_t_end"])))
    print("  WEAK-PF n=%d  t_end %s" % (b["n_B"], ", ".join("%.2f" % x for x in b["B_t_end"])))
    print()
    print("  %-20s %10s %10s %12s  %s" % ("channel", "S mean", "WPF mean", "seed gap", "disjoint"))
    for ch in CH:
        r = b["channels"][ch]
        print("  %-20s %+10.4f %+10.4f %+12.4f  %s"
              % (ch, r["A_mean"], r["B_mean"], r["seed_gap_deg"], "YES" if r["disjoint"] else ""))
    pm = b["permutation"]
    print()
    print("  channels disjoint at seed level : %d of 16%s"
          % (b["n_disjoint_of_16"], ("  -> " + ", ".join(b["disjoint_channels"])) if b["disjoint_channels"] else ""))
    print("  permutation, %s over %d assignments" % (pm["method"], pm["assignments"]))
    print("  familywise: %d of %d reach the best observed gap (%.4f deg) -> p = %.4f"
          % (pm["familywise_count_ge_best_observed"], pm["assignments"],
             pm["best_observed_gap_deg"], pm["familywise_proportion"]))

print("\nwrote %s (%d bytes)" % (p, os.path.getsize(p)))
