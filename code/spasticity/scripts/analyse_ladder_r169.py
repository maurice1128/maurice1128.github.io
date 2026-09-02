# -*- coding: utf-8 -*-
"""Analyse the re-optimised 3D DOSE LADDER.

GOVERNED BY  paper/PREREG_3d_ladder_r169.md
             sha256 e3ec76aa98759c821ef410889d3fc5d2840297bfc93482e00efc85e244e6d703
Where this script and that registration disagree, THE REGISTRATION DECIDES.

ORDER IS FIXED:
   0  directory selection      (the killed-cell hazard)
   1  calibration gate         (reused cells must reproduce r151's numbers, not just its bytes)
   2  Gate G                   (from the .sto, before any endpoint)
   3  common window            (across ADMITTED rungs)
   4  endpoints
   5  overlap-mass gate k = 6  (section 3)
   6  co-primary 4a sign conservation, 4b double dissociation  -- PATTERN criteria, NO p-value
   7  REACHED-BUT-EMPTY / secondary

DIRECTORY SELECTION -- section 8 and the round-170 hazard.
  Two cells were killed in flight and left well-formed but SHORT history.txt files (81 and 71
  lines, final record complete, CRLF intact). Re-running does not resume: SCONE creates a
  sibling "<tag>... (1)" directory. r151's find_run took sorted(ds)[0], which is the ORIGINAL
  TRUNCATED directory -- a plausible wrong number rather than an error, the LAUNCH_STATUS.json
  class exactly. This script selects ONLY directories whose history.txt has >= 91 lines and
  ASSERTS that exactly one qualifies per tag. Nothing is deleted; the debris stays on disk as
  evidence and is excluded by measurement, not by name order.

REPLAY: r169 cells carry .par but no .sto. Producing kinematics requires sconecmd -e on the best
par -- an EVALUATION of an already-optimised parameter vector, which is what analyse_reopt_r151.py
did for r151. It is not an optimisation, not --run, not --launch. Nothing is re-optimised here.
"""
import io
import os
import sys
import glob
import json
import math
import itertools
import subprocess


def _js(o):
    """numpy scalars are not JSON-serialisable. Coerce them; raise on anything else
       rather than writing a placeholder that would read as a real value."""
    if hasattr(o, "item"):
        return o.item()
    raise TypeError("refusing to serialise %r" % type(o))

sys.path.insert(0, r"C:\Users\maurice\Desktop\spasticity_paper\scone")
import sto_utils as S

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

RESULTS = r"C:\Users\maurice\Documents\SCONE\results"
PAPER = r"C:\Users\maurice\Desktop\spasticity_paper\paper"
OUT = os.path.join(PAPER, "LADDER_RESULT_r169.json")
SCONE = r"C:\Program Files\SCONE\bin\sconecmd.exe"
PREREG = "e3ec76aa98759c821ef410889d3fc5d2840297bfc93482e00efc85e244e6d703"

SEEDS = [101, 102, 103, 104, 105, 106]
MIN_DUR, MIN_CYC, MIN_SEEDS, SETTLE = 9.73, 5, 4, 1.0
K_MASS = 6                                   # section 3, fixed before data
R151_WINDOW_T1 = 13.58                       # for the calibration gate only
TOL = 1e-9

# registration section 0, control bands FIXED before any new cell existed
BANDS = {"ankle_angle_LmR": (-0.5153, 0.0581),
         "hip_flexion_LmR": (-0.3671, 0.2900)}
CHANNELS = ["ankle_angle_LmR", "hip_flexion_LmR"]

RUNGS = [("C",    "control", "R151C",    0.0,  1.00),
         ("S050", "spastic", "R151S",    0.050, 1.00),
         ("S150", "spastic", "R169S150", 0.150, 1.00),
         ("S400", "spastic", "R169S400", 0.400, 1.00),
         ("W080", "weak",    "R151W",    0.0,  0.80),
         ("W090", "weak",    "R169W090", 0.0,  0.90),
         ("W095", "weak",    "R169W095", 0.0,  0.95)]


def die(msg, code=2):
    print("\n" + "=" * 92)
    print("STOP -- %s" % msg)
    print("Nothing reported.")
    print("=" * 92)
    sys.exit(code)


def hist_lines(d):
    h = os.path.join(d, "history.txt")
    return sum(1 for _ in io.open(h, errors="replace")) if os.path.exists(h) else 0


def find_run(tag):
    """Section 8: complete iff history.txt >= 91 lines. Exactly one candidate must qualify."""
    cands = [d for d in glob.glob(os.path.join(RESULTS, tag + ".*")) if os.path.isdir(d)]
    good = [d for d in cands if hist_lines(d) >= 91]
    short = [(os.path.basename(d), hist_lines(d)) for d in cands if hist_lines(d) < 91]
    if len(good) != 1:
        die("tag %s has %d complete directories (need exactly 1); short: %r" % (tag, len(good), short))
    return good[0], short


def best_par(d):
    ps = [p for p in glob.glob(os.path.join(d, "*.par")) if os.path.basename(p)[0].isdigit()]
    return sorted(ps)[-1] if ps else None


def sto_for(d):
    s = glob.glob(os.path.join(d, "*.par.sto"))
    return sorted(s)[-1] if s else None


def cycles_in(cols, dat, t, t0, t1):
    grf, thr = S.grf_vertical(cols, dat, "l")
    if grf is None:
        return None, None
    idx = S.heel_strikes(t, grf, thresh=thr)
    c = [(idx[k], idx[k + 1]) for k in range(len(idx) - 1)
         if t[idx[k]] >= t0 and t[idx[k + 1]] <= t1]
    return (c[:-1] if len(c) >= 2 else c), (grf, thr)


def rom(cols, dat, chan, cyc):
    v = S.col(cols, dat, chan)
    if v is None or not cyc:
        return None
    return sum(math.degrees(max(v[a:b + 1]) - min(v[a:b + 1])) for a, b in cyc) / len(cyc)


def hs_angle(cols, dat, chan, cyc):
    v = S.col(cols, dat, chan)
    if v is None or not cyc:
        return None
    return sum(math.degrees(v[a]) for a, _ in cyc) / len(cyc)


def mwu_two_sided(a, b):
    n, m = len(a), len(b)
    obs = sum(1 for x in a for y in b if x > y) + 0.5 * sum(1 for x in a for y in b if x == y)
    allv = list(a) + list(b)
    cnt = tot = 0
    for c in itertools.combinations(range(n + m), n):
        A = [allv[i] for i in c]
        B = [allv[i] for i in range(n + m) if i not in c]
        u = sum(1 for x in A for y in B if x > y) + 0.5 * sum(1 for x in A for y in B if x == y)
        tot += 1
        if abs(u - n * m / 2.0) >= abs(obs - n * m / 2.0) - 1e-9:
            cnt += 1
    return obs / (n * m), cnt / float(tot)


def measure(sto, t1):
    cols, dat = S.load_sto(sto)
    t = list(S.col(cols, dat, "time"))
    cyc, _ = cycles_in(cols, dat, t, SETTLE, t1)
    if not cyc:
        return None
    out = {"n_cycles": len(cyc), "t_end": t[-1]}
    for ch, (L, R) in (("ankle_angle_LmR", ("ankle_angle_l", "ankle_angle_r")),
                       ("hip_flexion_LmR", ("hip_flexion_l", "hip_flexion_r"))):
        out[ch] = rom(cols, dat, L, cyc) - rom(cols, dat, R, cyc)
    out["ank_hs_LmR"] = (hs_angle(cols, dat, "ankle_angle_l", cyc)
                         - hs_angle(cols, dat, "ankle_angle_r", cyc))
    return out


# ================================================== 0. selection + replay
print("=" * 92)
print("0. DIRECTORY SELECTION -- complete iff history.txt >= 91 lines; debris excluded by")
print("   MEASUREMENT, not by name order. Nothing is deleted.")
print("=" * 92)
runs, debris = {}, []
for rid, kind, prefix, kv, scale in RUNGS:
    for s in SEEDS:
        tag = "%s_s%d" % (prefix, s)
        d, short = find_run(tag)
        runs[(rid, s)] = d
        for nm, n in short:
            debris.append({"tag": tag, "dir": nm, "history_lines": n})
            print("  EXCLUDED debris  %-58s %d lines" % (nm, n))
print("  %d tags, exactly one complete directory each. %d debris directories excluded and left"
      " in place." % (len(runs), len(debris)))

need = [(k, d) for k, d in runs.items() if sto_for(d) is None]
if need:
    print("\n  replaying %d cells (sconecmd -e on the best par; an EVALUATION, not an optimisation)"
          % len(need))
    for k, d in need:
        bp = best_par(d)
        if bp is None:
            die("no par in %s" % d)
        subprocess.run([SCONE, "-e", bp], capture_output=True, timeout=900, cwd=d)
    still = [k for k, d in runs.items() if sto_for(d) is None]
    if still:
        die("replay produced no .sto for %r" % still)
    print("  all %d cells now carry a .sto" % len(runs))

# ================================================== 1. calibration gate
print("\n" + "=" * 92)
print("1. CALIBRATION GATE -- the 18 REUSED cells must reproduce r151's ENDPOINTS, not merely")
print("   its bytes. Window pinned to r151's [1.00, %.2f] for this check only." % R151_WINDOW_T1)
print("=" * 92)
dep = json.load(io.open(os.path.join(PAPER, "REOPT3D_RESULT_r151.json"), encoding="utf-8"))
known = dep["registered_asymmetry_endpoints"]["endpoints"]
recal = {}
for rid, arm in (("C", "C"), ("S050", "S"), ("W080", "W")):
    for s in SEEDS:
        m = measure(sto_for(runs[(rid, s)]), R151_WINDOW_T1)
        if m is None:
            die("calibration: no cycles for %s s%d" % (rid, s))
        recal[(rid, s)] = m
fails = 0
print("%-20s %16s %16s %16s %16s" % ("channel", "S recomputed", "S r151", "W recomputed", "W r151"))
for ch in CHANNELS:
    sm = sum(recal[("S050", s)][ch] for s in SEEDS) / 6.0
    wm = sum(recal[("W080", s)][ch] for s in SEEDS) / 6.0
    ds, dw = known[ch]["S_mean"], known[ch]["W_mean"]
    ok = abs(sm - ds) <= TOL and abs(wm - dw) <= TOL
    fails += (not ok)
    print("%-20s %16.10f %16.10f %16.10f %16.10f  %s"
          % (ch, sm, ds, wm, dw, "OK" if ok else "*** MISMATCH ***"))
if fails:
    die("%d channels failed to reproduce r151 to %g -- the ladder is NOT reported" % (fails, TOL))
print("\n  Reused cells reproduce r151's endpoints exactly. Byte-identity at build time was")
print("  necessary and is now shown to be sufficient. Gate PASSED.")

# ================================================== 2. Gate G
print("\n" + "=" * 92)
print("2. GATE G -- a rung is ADMITTED iff >= %d of 6 seeds each reach >= %.2f s AND >= %d cycles."
      % (MIN_SEEDS, MIN_DUR, MIN_CYC))
print("   A failing rung is DROPPED. It is never replaced and never re-titrated.")
print("=" * 92)
gate, per_seed = {}, {}
print("%-6s %-8s %-7s %-6s %s" % ("rung", "kind", "KV", "scale", "seeds (dur s / cycles)"))
for rid, kind, prefix, kv, scale in RUNGS:
    ok, cells = 0, []
    for s in SEEDS:
        try:
            cols, dat = S.load_sto(sto_for(runs[(rid, s)]))
            t = list(S.col(cols, dat, "time"))
            cyc, _ = cycles_in(cols, dat, t, SETTLE, t[-1])
            n = len(cyc) if cyc else 0
        except Exception:
            # a cell that fell so early the .sto carries no usable trace is a Gate G FAILURE,
            # not an error to be smoothed over. It is recorded as such, with dur 0.
            t, n = [0.0], 0
        good = (t[-1] >= MIN_DUR and n >= MIN_CYC)
        ok += good
        per_seed["%s_%d" % (rid, s)] = {"dur": t[-1], "cycles": n, "pass": bool(good)}
        cells.append("%.2f/%d%s" % (t[-1], n, "" if good else "X"))
    gate[rid] = {"n_pass": ok, "admitted": ok >= MIN_SEEDS, "kind": kind, "kv": kv, "scale": scale}
    print("%-6s %-8s %-7s %-6.2f %s  -> %d/6  %s"
          % (rid, kind, ("%.3f" % kv) if kv else "-", scale, "  ".join(cells), ok,
             "ADMITTED" if ok >= MIN_SEEDS else "*** DROPPED ***"))

admitted = [r for r, g in gate.items() if g["admitted"]]
if "C" not in admitted:
    die("FC FIRES -- control fails Gate G; nothing is interpretable")
spast = [r for r in admitted if gate[r]["kind"] == "spastic"]
weak = [r for r in admitted if gate[r]["kind"] == "weak"]
print("\n  admitted: %r   spastic rungs %r   weak rungs %r" % (admitted, spast, weak))

res = {"prereg_sha256": PREREG, "debris_excluded": debris, "gate": gate, "per_seed": per_seed,
       "admitted": admitted, "spastic_rungs": spast, "weak_rungs": weak,
       "calibration": "PASSED -- reused cells reproduce r151 endpoints to 1e-9"}

ANSWERABLE_4A = len(spast) >= 2 and len(weak) >= 2
res["answerable_4a"] = bool(ANSWERABLE_4A)
if not ANSWERABLE_4A:
    res["verdict_4a"] = "NOT ANSWERABLE"
    res["reason_4a"] = ("a mechanism has fewer than 2 admitted rungs, so conservation ACROSS "
                        "severity cannot be tested on it: a one-rung ladder is the r151 design "
                        "again. The rungs that failed Gate G are named above and are NOT "
                        "replaced and NOT re-titrated.")
    print("\n  ⛔ 4a NOT ANSWERABLE -- %s" % res["reason_4a"])
    print("  Everything that IS answerable is still computed below and labelled as such.")

# ================================================== 3. common window
durs = [per_seed["%s_%d" % (r, s)]["dur"] for r in admitted for s in SEEDS
        if per_seed["%s_%d" % (r, s)]["pass"]]
T1 = min(durs)
print("\n3. COMMON WINDOW across ADMITTED rungs: [%.2f, %.4f]" % (SETTLE, T1))
res["window"] = [SETTLE, T1]

# ================================================== 4. endpoints
vals = {}
for r in admitted:
    for s in SEEDS:
        if per_seed["%s_%d" % (r, s)]["pass"]:
            m = measure(sto_for(runs[(r, s)]), T1)
            if m:
                vals[(r, s)] = m
res["per_cell"] = {"%s_%d" % k: v for k, v in vals.items()}


def rung_vals(r, ch):
    return [vals[(r, s)][ch] for s in SEEDS if (r, s) in vals]


print("\n" + "=" * 92)
print("4. ENDPOINTS -- per-cycle mean ROM difference (L-R), degrees, common window")
print("=" * 92)
print("%-6s %-8s %8s %26s %26s %22s"
      % ("rung", "kind", "n", "ankle_angle_LmR", "hip_flexion_LmR", "ank_hs_LmR"))
summ = {}
for r in admitted:
    row = {}
    for ch in CHANNELS + ["ank_hs_LmR"]:
        v = rung_vals(r, ch)
        row[ch] = {"mean": sum(v) / len(v), "min": min(v), "max": max(v), "n": len(v),
                   "vals": v}
    summ[r] = row
    print("%-6s %-8s %8d %+9.4f [%+7.3f,%+7.3f] %+9.4f [%+7.3f,%+7.3f] %+8.3f [%+6.2f,%+6.2f]"
          % (r, gate[r]["kind"], row[CHANNELS[0]]["n"],
             row[CHANNELS[0]]["mean"], row[CHANNELS[0]]["min"], row[CHANNELS[0]]["max"],
             row[CHANNELS[1]]["mean"], row[CHANNELS[1]]["min"], row[CHANNELS[1]]["max"],
             row["ank_hs_LmR"]["mean"], row["ank_hs_LmR"]["min"], row["ank_hs_LmR"]["max"]))
res["rung_summary"] = {r: {c: {k: v for k, v in d.items() if k != "vals"}
                           for c, d in summ[r].items()} for r in admitted}

# ================================================== 5. overlap-mass gate, k = 6
print("\n" + "=" * 92)
print("5. OVERLAP-MASS GATE on ank_hs_LmR, k = %d from EACH mechanism (section 3, fixed before data)"
      % K_MASS)
print("=" * 92)
sv = [v for r in spast for v in rung_vals(r, "ank_hs_LmR")]
wv = [v for r in weak for v in rung_vals(r, "ank_hs_LmR")]
lo, hi = max(min(sv), min(wv)), min(max(sv), max(wv))
ns = sum(1 for x in sv if lo <= x <= hi)
nw = sum(1 for x in wv if lo <= x <= hi)
passed = (lo <= hi) and ns >= K_MASS and nw >= K_MASS
print("  spastic pooled n=%d  range [%+.3f, %+.3f]" % (len(sv), min(sv), max(sv)))
print("  weak    pooled n=%d  range [%+.3f, %+.3f]" % (len(wv), min(wv), max(wv)))
if lo <= hi:
    print("  matched region [%+.3f, %+.3f] width %.3f deg -> %d spastic, %d weak inside"
          % (lo, hi, hi - lo, ns, nw))
else:
    print("  ⛔ DISJOINT -- no matched region exists (gap %.3f deg)" % (lo - hi))
print("  -> %s" % ("PASSED" if passed else "INSUFFICIENT MASS"))
res["overlap_mass"] = {"k": K_MASS, "spastic_range": [min(sv), max(sv)],
                       "weak_range": [min(wv), max(wv)],
                       "matched_region": [lo, hi] if lo <= hi else None,
                       "n_spastic_inside": ns, "n_weak_inside": nw, "passed": bool(passed)}

# ================================================== 6. co-primaries
print("\n" + "=" * 92)
print("6. CO-PRIMARIES -- PATTERN criteria. NO p-VALUE ATTACHES TO EITHER AND NONE IS QUOTED.")
print("=" * 92)
sign = {}
for ch in CHANNELS:
    ss = [(r, summ[r][ch]["mean"]) for r in spast]
    ws = [(r, summ[r][ch]["mean"]) for r in weak]
    s_signs = set(1 if m > 0 else -1 for _, m in ss)
    w_signs = set(1 if m > 0 else -1 for _, m in ws)
    cons = len(s_signs) == 1 and len(w_signs) == 1 and s_signs != w_signs
    sign[ch] = {"spastic": {r: m for r, m in ss}, "weak": {r: m for r, m in ws},
                "conserved": bool(cons)}
    print("  4a %-18s spastic %s | weak %s -> %s"
          % (ch, " ".join("%s%+.3f" % (r, m) for r, m in ss),
             " ".join("%s%+.3f" % (r, m) for r, m in ws),
             "CONSERVED" if cons else "FLIPS or CROSSES"))
res["sign_conservation"] = sign
if ANSWERABLE_4A:
    res["verdict_4a"] = ("CONSERVED" if all(v["conserved"] for v in sign.values())
                         else "NOT CONSERVED")
else:
    print("  (4a stays NOT ANSWERABLE: the signs above are DESCRIPTIVE only. A mechanism")
    print("   with one admitted rung contributes no test of conservation across severity.)")

print()
diss = {}
for ch in CHANNELS:
    band = BANDS[ch]
    out_s = {r: not (band[0] <= summ[r][ch]["mean"] <= band[1]) for r in spast}
    out_w = {r: not (band[0] <= summ[r][ch]["mean"] <= band[1]) for r in weak}
    diss[ch] = {"band": list(band), "outside_at_spastic_rungs": out_s, "outside_at_weak_rungs": out_w}
    print("  4b %-18s band [%+.4f,%+.4f]" % (ch, band[0], band[1]))
    print("       spastic rungs outside band: %s" % {r: out_s[r] for r in spast})
    print("       weak    rungs outside band: %s" % {r: out_w[r] for r in weak})
ank, hip = CHANNELS
held = (all(diss[hip]["outside_at_spastic_rungs"].values())
        and not any(diss[hip]["outside_at_weak_rungs"].values())
        and all(diss[ank]["outside_at_weak_rungs"].values())
        and not any(diss[ank]["outside_at_spastic_rungs"].values()))
res["double_dissociation"] = diss
res["verdict_4b"] = "HELD" if held else "BROKEN"
print("\n  4b VERDICT: %s   (HELD = each channel leaves its band for one mechanism only)"
      % res["verdict_4b"])
print("  4a VERDICT: %s" % res["verdict_4a"])

# ================================================== 7. reached-but-empty / secondary
print("\n" + "=" * 92)
print("7. SECONDARY / REACHED-BUT-EMPTY (section 5)")
print("=" * 92)
if not passed:
    res["verdict_secondary"] = "NO CROSSING"
    res["secondary_note"] = ("section 3 returned INSUFFICIENT MASS. No matched-equinus contrast is "
                             "computed and no number from one is reported. At survivable magnitudes "
                             "these two lesions do not produce a common equinus presentation in this "
                             "model.")
    print("  ⛔ NO CROSSING -- no matched-equinus contrast computed, none reported.")
else:
    inside = [r for r in weak
              if all(BANDS[c][0] <= summ[r][c]["mean"] <= BANDS[c][1] for c in CHANNELS)
              and any(lo <= v <= hi for v in rung_vals(r, "ank_hs_LmR"))]
    if inside and len(inside) == len([r for r in weak
                                      if any(lo <= v <= hi for v in rung_vals(r, "ank_hs_LmR"))]):
        res["verdict_secondary"] = "REACHED-BUT-EMPTY"
        res["secondary_note"] = ("every weak rung inside the matched region has BOTH channel means "
                                 "within the section 0 control bands: the overlap was bought by "
                                 "abolishing the contrast. NOT reported as a null.")
        print("  ⛔ REACHED-BUT-EMPTY -- overlap bought by abolishing the contrast; not a null.")
    else:
        sec = {}
        for ch in CHANNELS:
            a = [v for r in spast for i, v in enumerate(rung_vals(r, ch))
                 if lo <= rung_vals(r, "ank_hs_LmR")[i] <= hi]
            b = [v for r in weak for i, v in enumerate(rung_vals(r, ch))
                 if lo <= rung_vals(r, "ank_hs_LmR")[i] <= hi]
            auc, p = mwu_two_sided(a, b)
            sec[ch] = {"n_spastic": len(a), "n_weak": len(b), "auc": auc, "p_raw": p,
                       "p_adj_x2": min(1.0, 2 * p), "abs_auc_minus_half": abs(auc - 0.5)}
            print("  %-18s n %d v %d  AUC %.4f  p %.6f  p_adj(x2) %.6f"
                  % (ch, len(a), len(b), auc, p, min(1.0, 2 * p)))
        res["secondary"] = sec
        res["verdict_secondary"] = "COMPUTED"

json.dump(res, io.open(OUT, "w", encoding="utf-8"), indent=1, default=_js)
print("\nwrote %s" % OUT)
