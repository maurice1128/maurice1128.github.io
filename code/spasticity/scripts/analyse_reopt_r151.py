# -*- coding: utf-8 -*-
"""Analyse the 18 re-optimised arms, per PREREG_3d_reopt_r151.md
   sha256 f6a65408731cc7141580ea4c38b68871c9167d0f0c2a9da416142405758c4c23

Gate G first (it can void the study), then the endpoint.

METRIC: mean per-cycle ROM. Global range is FORBIDDEN by section 4 -- it inflated a
0.405 deg difference into 1.934 deg at r145.

WINDOW: one common interval across all admitted arms.

CYCLE COUNT: r150 found two of this project's scripts counting cycles differently.
This script defines it once, here, and uses the SAME definition for the gate and the
endpoint: GRF-delimited heel strikes on the left, cycles wholly inside the window,
last cycle dropped.
"""
import io, os, sys, math, glob, json, itertools

sys.path.insert(0, r"C:\Users\maurice\Desktop\spasticity_paper\scone")
import sto_utils as S

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

RESULTS = r"C:\Users\maurice\Documents\SCONE\results"
OUT = r"C:\Users\maurice\Desktop\spasticity_paper\paper\REOPT3D_RESULT_r151.json"
SEEDS = [101, 102, 103, 104, 105, 106]
MIN_DUR, MIN_CYC, MIN_SEEDS, SETTLE = 9.73, 5, 4, 1.0
POOL = 13                      # registered and fixed; see the note printed below

PAIRED = ["ankle_angle", "knee_angle", "hip_flexion", "hip_adduction"]
UNPAIRED = ["pelvis_list", "pelvis_rotation", "lumbar_bending"]


def best_par(d):
    ps = [p for p in glob.glob(os.path.join(d, "*.par")) if os.path.basename(p)[0].isdigit()]
    return sorted(ps)[-1] if ps else None


def find_run(tag):
    ds = [d for d in glob.glob(os.path.join(RESULTS, tag + ".*")) if os.path.isdir(d)]
    ds = [d for d in ds if os.path.exists(os.path.join(d, "history.txt"))]
    return sorted(ds)[0] if ds else None


def sto_for(d):
    s = glob.glob(os.path.join(d, "*.par.sto"))
    return sorted(s)[-1] if s else None


def cycles_in(cols, dat, t, t0, t1):
    grf, thr = S.grf_vertical(cols, dat, "l")
    if grf is None:
        return None
    idx = S.heel_strikes(t, grf, thresh=thr)
    c = [(idx[k], idx[k + 1]) for k in range(len(idx) - 1)
         if t[idx[k]] >= t0 and t[idx[k + 1]] <= t1]
    return c[:-1] if len(c) >= 2 else c


def rom(cols, dat, t, chan, cyc):
    v = S.col(cols, dat, chan)
    if v is None or not cyc:
        return None
    out = [math.degrees(max(v[a:b + 1]) - min(v[a:b + 1])) for a, b in cyc]
    return sum(out) / len(out)


def mwu_two_sided(a, b):
    """Exact two-sided Mann-Whitney by enumeration; 6v6 is 924 splits."""
    n, m = len(a), len(b)
    obs = sum(1 for x in a for y in b if x > y) + 0.5 * sum(1 for x in a for y in b if x == y)
    allv = list(a) + list(b)
    cnt = tot = 0
    for comb in itertools.combinations(range(n + m), n):
        A = [allv[i] for i in comb]
        B = [allv[i] for i in range(n + m) if i not in comb]
        u = sum(1 for x in A for y in B if x > y) + 0.5 * sum(1 for x in A for y in B if x == y)
        tot += 1
        if abs(u - n * m / 2.0) >= abs(obs - n * m / 2.0) - 1e-9:
            cnt += 1
    return obs / (n * m), cnt / float(tot)


# ---------------- collect ----------------------------------------------------
runs = {}
for arm in ("C", "S", "W"):
    for s in SEEDS:
        tag = "R151%s_s%d" % (arm, s)
        d = find_run(tag)
        sto = sto_for(d) if d else None
        if d and not sto:                       # replay the best par to get kinematics
            bp = best_par(d)
            if bp:
                import subprocess
                subprocess.run([r"C:\Program Files\SCONE\bin\sconecmd.exe", "-e", bp],
                               capture_output=True, timeout=600)
                sto = sto_for(d)
        runs[(arm, s)] = {"dir": d, "sto": sto}

print("=" * 78)
print("GATE G -- admitted iff >= %d of 6 seeds reach >= %.2f s AND >= %d cycles"
      % (MIN_SEEDS, MIN_DUR, MIN_CYC))
print("=" * 78)
gate, meta = {}, {}
for arm in ("C", "S", "W"):
    ok = 0
    for s in SEEDS:
        r = runs[(arm, s)]
        if not r["sto"]:
            meta[(arm, s)] = {"state": "UNEVALUABLE"}
            print("  %s s%d  UNEVALUABLE (no .sto)" % (arm, s))
            continue
        cols, dat = S.load_sto(r["sto"])
        t = list(S.col(cols, dat, "time"))
        cyc = cycles_in(cols, dat, t, SETTLE, t[-1])
        n = len(cyc) if cyc else 0
        good = t[-1] >= MIN_DUR and n >= MIN_CYC
        ok += good
        meta[(arm, s)] = {"state": "PASS" if good else "FAIL", "dur": t[-1], "cycles": n}
        print("  %s s%-4d dur %7.3f s  cycles %2d  -> %s" % (arm, s, t[-1], n, meta[(arm, s)]["state"]))
    gate[arm] = ok
    print("  ARM %s: %d/6 viable -> %s\n" % (arm, ok, "ADMITTED" if ok >= MIN_SEEDS else "NOT ADMITTED"))

admitted = [a for a in ("C", "S", "W") if gate[a] >= MIN_SEEDS]
res = {"gate": gate, "admitted": admitted,
       "per_seed": {"%s_%d" % k: v for k, v in meta.items()}}

if not ("S" in admitted and "W" in admitted):
    print("=" * 78)
    print("FG FIRES -- S or W not admitted. Per section 3 the design is VOID, not negative.")
    print("Do NOT titrate; that would be a new registration.")
    print("=" * 78)
    json.dump(res, io.open(OUT, "w", encoding="utf-8"), indent=1)
    sys.exit(0)

# ---------------- common window ---------------------------------------------
durs = [meta[(a, s)]["dur"] for a in admitted for s in SEEDS
        if meta[(a, s)].get("state") == "PASS"]
T1 = min(durs)
print("COMMON WINDOW across all admitted arms: [%.2f, %.4f]\n" % (SETTLE, T1))

chans = [c + "_" + sd for c in PAIRED for sd in ("l", "r")] + UNPAIRED + ["cycle_time"]
print("ENUMERATED ENDPOINTS: %d   REGISTERED POOL: %d" % (len(chans), POOL))
print("  (the registration enumerates %d quantities but fixes the pool at %d;" % (len(chans), POOL))
print("   the LARGER correction is applied, which is conservative and cannot inflate)\n")

vals = {}
for a in admitted:
    for s in SEEDS:
        if meta[(a, s)].get("state") != "PASS":
            continue
        cols, dat = S.load_sto(runs[(a, s)]["sto"])
        t = list(S.col(cols, dat, "time"))
        cyc = cycles_in(cols, dat, t, SETTLE, T1)
        row = {}
        for ch in chans[:-1]:
            row[ch] = rom(cols, dat, t, ch, cyc)
        row["cycle_time"] = ((t[cyc[-1][1]] - t[cyc[0][0]]) / len(cyc)) if cyc else None
        vals[(a, s)] = row

print("=" * 78)
print("PRIMARY -- S vs W, exact two-sided Mann-Whitney, Bonferroni x%d" % POOL)
print("=" * 78)
print("%-18s %9s %9s %7s %10s %10s" % ("endpoint", "S mean", "W mean", "AUC", "p_raw", "p_adj"))
prim = {}
for ch in chans:
    a = [vals[("S", s)][ch] for s in SEEDS if ("S", s) in vals and vals[("S", s)][ch] is not None]
    b = [vals[("W", s)][ch] for s in SEEDS if ("W", s) in vals and vals[("W", s)][ch] is not None]
    if len(a) < 2 or len(b) < 2:
        print("%-18s UNEVALUABLE" % ch)
        prim[ch] = {"state": "UNEVALUABLE"}
        continue
    auc, p = mwu_two_sided(a, b)
    padj = min(1.0, p * POOL)
    prim[ch] = {"S_mean": sum(a) / len(a), "W_mean": sum(b) / len(b), "auc": auc,
                "p_raw": p, "p_adj": padj, "separates": padj < 0.05,
                "nS": len(a), "nW": len(b)}
    print("%-18s %9.3f %9.3f %7.3f %10.5f %10.5f %s"
          % (ch, prim[ch]["S_mean"], prim[ch]["W_mean"], auc, p, padj,
             "  *** SEPARATES ***" if padj < 0.05 else ""))

res.update({"window": [SETTLE, T1], "endpoints": {"%s_%d" % k: v for k, v in vals.items()},
            "primary": prim, "pool": POOL,
            "min_attainable_p_6v6": 2.0 / 924, "min_attainable_p_adj": 13 * 2.0 / 924})
json.dump(res, io.open(OUT, "w", encoding="utf-8"), indent=1)
print("\nwrote", OUT)
sep = [c for c, v in prim.items() if v.get("separates")]
print("SEPARATING ENDPOINTS: %r" % sep)
print("FS %s" % ("does NOT fire" if sep else "FIRES -- no endpoint separates"))
