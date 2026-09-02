# -*- coding: utf-8 -*-
"""PROVENANCE TEST v2 -- using analyse_ladder_r169's OWN reduction, not a reimplementation.

v1 computed mean(hip_flexion_l - hip_flexion_r), a difference of LEVELS, and reproduced nothing.
analyse_ladder_r169.py:163 computes rom(L) - rom(R), a difference of per-cycle ROMs in degrees.
That was the whole disagreement.

The module runs its analysis at import, so its DEFINITIONS are exec'd up to the first top-level
section marker. The functions used here are therefore byte-identical to the originals, not copies.
"""
import os, sys, glob, json, shutil, subprocess
SRC = r"C:\Users\maurice\Desktop\spasticity_paper\scone\analyse_ladder_r169.py"
src = open(SRC, encoding="utf-8").read()
cut = src.index("# ================================================== 0. selection + replay")
ns = {"__name__": "_defs_only"}
exec(compile(src[:cut], SRC, "exec"), ns)          # definitions only, no analysis run
rom, cycles_in, S = ns["rom"], ns["cycles_in"], ns["S"]
print("imported from analyse_ladder_r169.py: rom(), cycles_in()  [definitions exec'd, analysis not run]")

RES = r"C:\Users\maurice\Documents\SCONE\results"
SCR = r"C:\Users\maurice\Desktop\spasticity_paper\scone\probe3d_r141\_prov2"
SCONE = r"C:\Program Files\SCONE\bin\sconecmd.exe"
SETTLE, T1 = 1.00, 13.58
arch = json.load(open(r"C:\Users\maurice\Desktop\spasticity_paper\paper\LADDER_RESULT_r169.json"))["per_cell"]

print("=" * 96)
print("PROVENANCE TEST v2 -- replay of the ORIGINAL r169 S050 .par files, ORIGINAL reduction")
print("=" * 96)
print("%-6s %13s %13s %12s %6s %8s %8s" %
      ("seed", "archived", "replay", "abs diff", "ncyc", "t_end", "match"))
rows, ok = {}, 0
for s in range(101, 107):
    d0 = [d for d in glob.glob(os.path.join(RES, "R151S_s%d.*" % s)) if os.path.isdir(d)][0]
    w = os.path.join(SCR, "s%d" % s)
    if os.path.isdir(w):
        shutil.rmtree(w)
    os.makedirs(w)
    for f in os.listdir(d0):
        if not f.endswith(".sto"):
            p = os.path.join(d0, f)
            (shutil.copytree if os.path.isdir(p) else shutil.copy2)(p, os.path.join(w, f))
    par = sorted(glob.glob(os.path.join(w, "[0-9]*.par")))[-1]
    subprocess.run([SCONE, "-e", os.path.basename(par)], cwd=w, capture_output=True, timeout=900)
    st = glob.glob(os.path.join(w, "*.sto"))
    if not st:
        print("%-6d REPLAY PRODUCED NO .sto" % s)
        continue
    cols, dat = S.load_sto(st[0])
    t = list(S.col(cols, dat, "time"))
    cyc, _ = cycles_in(cols, dat, t, SETTLE, T1)
    val = rom(cols, dat, "hip_flexion_l", cyc) - rom(cols, dat, "hip_flexion_r", cyc)
    a = arch["S050_%d" % s]["hip_flexion_LmR"]
    diff = abs(val - a)
    m = diff < 1e-3
    ok += m
    rows["s%d" % s] = {"archived": a, "replay": val, "abs_diff": diff,
                       "ncyc": len(cyc), "t_end": t[-1], "match": bool(m)}
    print("%-6d %13.6f %13.6f %12.2e %6d %8.2f %8s" %
          (s, a, val, diff, len(cyc), t[-1], "YES" if m else "NO"))
print("\nreproduced %d of 6 to 1e-3" % ok)
json.dump(rows, open(r"C:\Users\maurice\Desktop\spasticity_paper\paper\PROVENANCE2_r209.json", "w"), indent=1)
shutil.rmtree(SCR, ignore_errors=True)
print("deposited paper/PROVENANCE2_r209.json  (scratch removed)")
