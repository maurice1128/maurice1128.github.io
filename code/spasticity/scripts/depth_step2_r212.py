# -*- coding: utf-8 -*-
"""ZERO-COST RECONNAISSANCE r212, STEP 2 -- PER-CELL CURVES. Variant (c).

⛔ NOT A REGISTERED STUDY. Nothing computed here may be cited as evidence for or against a
hypothesis. This is a look, to decide whether a registered study is worth running.

⛔ THE SPASTIC ARM IS THE SHAPE-BEARING CURVE. THE WEAK ARM IS A CONVERGED REFERENCE POINT,
   NOT A CURVE: it holds 3-5 saved points and shows no Gate-G transition, so "flat" is
   UNOBSERVABLE there, not observed. No line is drawn through three points.

⛔ INDEXED BY GENERATION, with the caveat attached: EQUAL GENERATION IS NOT EQUAL CONVERGENCE.
   Last-improvement generation ranges 33-86 (spastic) and 38-87 (weak). Fitness is not a common
   scale because the objective differs with the lesion. PER-CELL ONLY: no cross-seed grid, no
   interpolation, no arm mean at a nominal generation -- the census found the only generation
   common to all six seeds, in either arm, is zero.

Endpoints use analyse_ladder_r169.py's OWN rom() and cycles_in(), exec'd definitions-only.
VALIDATE BEFORE TRUST: the converged depth must reproduce PRIMARYB_RESULT_r179.json's published
arm means before any shallow value is reported.

⛔ SAFETY: never deletes a .sto; asserts sorted(glob("*.par.sto"))[-1] -- how pb_r179.py selects
   the solution behind a PUBLISHED number -- is unchanged in every directory touched.
"""
import io, os, glob, json, math, time, subprocess

SRC = r"C:\Users\maurice\Desktop\spasticity_paper\scone\analyse_ladder_r169.py"
src = io.open(SRC, encoding="utf-8").read()
ns = {"__name__": "_defs_only"}
exec(compile(src[:src.index("# ================================================== 0. selection + replay")],
             SRC, "exec"), ns)
rom, cycles_in, S = ns["rom"], ns["cycles_in"], ns["S"]

RES = r"C:\Users\maurice\Documents\SCONE\results"
SCONECMD = r"C:\Program Files\SCONE\bin\sconecmd.exe"
P = r"C:\Users\maurice\Desktop\spasticity_paper\paper"
SETTLE, T1, MIN_DUR, MIN_CYC = 1.00, 13.58, 9.73, 4
PAIR = ["ankle_angle", "knee_angle", "hip_flexion", "hip_adduction"]
UNP = ["pelvis_list", "pelvis_rotation", "lumbar_bending"]

cen = json.load(io.open(os.path.join(P, "DEPTH_CENSUS_r212.json"), encoding="utf-8"))
pub = json.load(io.open(os.path.join(P, "PRIMARYB_RESULT_r179.json"), encoding="utf-8"))


def measure(sto):
    cols, dat = S.load_sto(sto)
    t = list(S.col(cols, dat, "time"))
    cyc, _ = cycles_in(cols, dat, t, SETTLE, T1)
    g2, g3 = bool(t[-1] >= MIN_DUR), bool(cyc is not None and len(cyc) >= MIN_CYC)
    if not (g2 and g3):
        return {"t_end": float(t[-1]), "ncyc": 0 if not cyc else len(cyc),
                "G2": g2, "G3": g3, "pass": False}
    o = {}
    for ch in [p + s for p in PAIR for s in ("_l", "_r")] + UNP:
        o[ch] = rom(cols, dat, ch, cyc)
    o["cycle_time"] = (t[cyc[-1][1]] - t[cyc[0][0]]) / len(cyc)
    for p in PAIR:
        o[p + "_LmR"] = o[p + "_l"] - o[p + "_r"]
    return {"t_end": float(t[-1]), "ncyc": len(cyc), "G2": g2, "G3": g3,
            "pass": True, "ch": o}


# ------------------------------------------------------------------- 1. replay what is missing
targets = []
before = {}
for arm in ("S", "W892"):
    for tag in sorted(cen["arms"][arm]):
        rec = cen["arms"][arm][tag]
        d = os.path.join(RES, rec["dir"])
        stos = sorted(glob.glob(os.path.join(d, "*.par.sto")))
        before[d] = stos[-1] if stos else None
        for r in rec["rows"]:
            targets.append((arm, tag, d, r["gen"], r["file"]))

t0 = time.time(); made = skipped = 0
for arm, tag, d, gen, parf in targets:
    if os.path.exists(os.path.join(d, parf + ".sto")):
        skipped += 1; continue
    subprocess.run([SCONECMD, "-e", parf], cwd=d, capture_output=True, timeout=900)
    made += os.path.exists(os.path.join(d, parf + ".sto"))
print("replayed %d, already present %d, %.1f s" % (made, skipped, time.time() - t0))

for d, was in before.items():
    now = sorted(glob.glob(os.path.join(d, "*.par.sto")))[-1]
    assert now == was, "SELECTION CHANGED in %s: %s -> %s" % (d, was, now)
print("⛔ selection guard: sorted(*.par.sto)[-1] unchanged in all %d directories\n" % len(before))

# ------------------------------------------------------------------------ 2. measure everything
V = {}
for arm, tag, d, gen, parf in targets:
    sto = os.path.join(d, parf + ".sto")
    V.setdefault(arm, {}).setdefault(tag, {})[gen] = (
        measure(sto) if os.path.exists(sto) else {"pass": False, "no_sto": True})

# ------------------------------------------- 3. VALIDATE BEFORE TRUST at the converged depth
print("=" * 96)
print("VALIDATION -- converged depth must reproduce PRIMARYB_RESULT_r179.json's arm means")
print("=" * 96)
worst = 0.0
for arm, key in (("S", "S_mean"), ("W892", "W892")):
    means = {}
    for tag, byg in V[arm].items():
        g = max(byg)
        means[tag] = byg[g]["ch"]
    for ch in pub["channels"]:
        mine = sum(means[t][ch] for t in means) / len(means)
        theirs = pub["channels"][ch][key] if key == "S_mean" else pub["channels"][ch][key]["mean"]
        worst = max(worst, abs(mine - theirs))
print("largest absolute difference across 16 channels x 2 arms: %.3e" % worst)
assert worst < 1e-9, "converged depth does NOT reproduce the published means -- ABORT"
print("⭐ reproduces to < 1e-9. The shallow values below are computed by the same code path.\n")

# ------------------------------------------------------------------------ 4. the curves
HEAD = ["hip_flexion_LmR", "ankle_angle_LmR", "cycle_time"]
print("=" * 96)
print("SPASTIC ARM (R151S) -- the shape-bearing curve.  PER CELL, INDEXED BY GENERATION.")
print("⚠ EQUAL GENERATION IS NOT EQUAL CONVERGENCE (last improvement: gen 33-86 across seeds).")
print("=" * 96)
for tag in sorted(V["S"]):
    byg = V["S"][tag]
    print("\n%s   (last improvement at gen %d)" % (tag, max(byg)))
    print("  %5s %7s %5s  %14s %15s %11s" % ("gen", "t_end", "ncyc", HEAD[0], HEAD[1], HEAD[2]))
    for g in sorted(byg):
        r = byg[g]
        if not r["pass"]:
            print("  %5d %7.2f %5d  ⛔ GATE FAIL (G2=%s G3=%s)"
                  % (g, r.get("t_end", 0), r.get("ncyc", 0), r.get("G2"), r.get("G3")))
        else:
            print("  %5d %7.2f %5d  %14.4f %15.4f %11.4f"
                  % (g, r["t_end"], r["ncyc"], r["ch"][HEAD[0]], r["ch"][HEAD[1]], r["ch"][HEAD[2]]))

print("\n" + "=" * 96)
print("WEAK ARM (R174W892) -- CONVERGED REFERENCE POINT, NOT A CURVE.")
print("⛔ 3-5 saved points and no Gate-G transition: FLAT IS UNOBSERVABLE HERE, NOT OBSERVED.")
print("=" * 96)
print("  %-16s %5s %7s %5s  %14s %15s %11s"
      % ("cell", "gen", "t_end", "ncyc", HEAD[0], HEAD[1], HEAD[2]))
for tag in sorted(V["W892"]):
    byg = V["W892"][tag]
    for g in sorted(byg):
        r = byg[g]
        mark = " <- converged" if g == max(byg) else ""
        if r["pass"]:
            print("  %-16s %5d %7.2f %5d  %14.4f %15.4f %11.4f%s"
                  % (tag, g, r["t_end"], r["ncyc"], r["ch"][HEAD[0]], r["ch"][HEAD[1]],
                     r["ch"][HEAD[2]], mark))
        else:
            print("  %-16s %5d  ⛔ GATE FAIL%s" % (tag, g, mark))

json.dump({"label": "RECONNAISSANCE STEP 2 -- per-cell curves, variant (c). NOT A STUDY.",
           "caveats": ["equal generation is not equal convergence",
                       "fitness is not a common scale across arms; the objective differs with the lesion",
                       "weak arm is a reference point, not a curve; flat is unobservable at 3-5 points",
                       "no cross-seed grid, no interpolation, no arm mean at a nominal generation"],
           "validation_max_abs_diff_vs_r179": worst,
           "cells": {a: {t: {str(g): V[a][t][g] for g in V[a][t]} for t in V[a]} for a in V}},
          io.open(os.path.join(P, "DEPTH_STEP2_r212.json"), "w", encoding="utf-8", newline="\n"),
          indent=1)
print("\ndeposited paper/DEPTH_STEP2_r212.json")
