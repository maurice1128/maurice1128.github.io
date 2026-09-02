# -*- coding: utf-8 -*-
"""Recompute the r294 endpoint. The deposited one resolved the WARM START, not the result.

Defect found. Both `RUN_FASTSTART_r294_cell*.json` record `resolved_par` equal to `warm_start`:
  s101  resolved_par = 0060_19.456_0.988.par   = the warm-start file, copied into the result dir
  s102  resolved_par = 0003_26.221_0.983.par   = likewise
and the only `.par.sto` present in each directory is that file's.

Why the resolver picked it. The launcher takes the minimum objective encoded in the filename.
The warm start was optimised under `min_velocity = 1.0`, where it scored 0.988. Under
`min_velocity = 1.5` the speed penalty puts every genuine result near 21-23. So 0.988 is the
smallest number in the directory and the tie-break selected the starting point.

Consequence: `achieved_speed_mps` 1.0239 and 1.0222 are the speeds of the WARM START, measured
before the arm did anything. They are not the arm's result and the rung cannot be read from them.

This script resolves instead by GENERATION -- the highest-numbered par actually produced by the
run -- evaluates it, and computes achieved speed the way `speed_gate_r203.py` does. It also
reads the registered failure criterion off `history.txt`: the best-fitness gain over the final
100 generations.

Read-only apart from `sconecmd -e`, which writes only `.sto`.
"""
import io, os, re, sys, glob, json, subprocess
sys.path.insert(0, r"C:\Users\maurice\Desktop\spasticity_paper\scone")
import numpy as np, sto_utils as S

RES = r"C:\Users\maurice\Documents\SCONE\results"
PAPER = r"C:\Users\maurice\Desktop\spasticity_paper\paper"
SCONECMD = r"C:\Program Files\SCONE\bin\sconecmd.exe"
SETTLE, T1 = 1.00, 13.58          # speed_gate_r203.py's window
SUCCESS, FAIL_GAIN = 1.30, 0.02   # PREREG_faststart_r294.md

out = {"what": "recomputation of the r294 endpoint after the deposited one was found to "
                "resolve the warm start instead of the result",
       "window": [SETTLE, T1], "success_threshold_mps": SUCCESS,
       "failure_final100_gain_mps": FAIL_GAIN, "cells": []}

for p in sorted(glob.glob(os.path.join(PAPER, "RUN_FASTSTART_r294_cell*.json"))):
    dep = json.load(open(p))
    d = os.path.join(RES, dep["result_dir"])
    warm = dep["warm_start"]

    pars = []
    for f in os.listdir(d):
        m = re.match(r"^(\d{4})_[\d.]+_[\d.]+\.par$", f)
        if m and f != warm:
            pars.append((int(m.group(1)), f))
    pars.sort()
    if not pars:
        out["cells"].append({"cell": dep["cell"], "error": "no non-warm-start par"}); continue
    gen, best = pars[-1]

    sto = os.path.join(d, best + ".sto")
    if not os.path.exists(sto):
        subprocess.run([SCONECMD, "-e", best], cwd=d, capture_output=True, timeout=1800)
    if not os.path.exists(sto):
        out["cells"].append({"cell": dep["cell"], "error": "evaluation produced no sto"}); continue

    cols, dat = S.load_sto(sto)
    t = np.asarray(S.col(cols, dat, "time"), dtype=float)
    grf, thr = S.grf_vertical(cols, dat, "l")
    idx = S.heel_strikes(t, grf, thresh=thr)
    cyc = [(a, b) for a, b in zip(idx[:-1], idx[1:]) if t[a] >= SETTLE and t[b] <= T1]
    cyc = cyc[:-1] if len(cyc) >= 2 else cyc
    px = np.asarray(S.col(cols, dat, "pelvis_tx"), dtype=float)
    if cyc:
        a, b = cyc[0][0], cyc[-1][1]
        speed = float((px[b - 1] - px[a]) / (t[b - 1] - t[a]))
    else:
        speed = None

    hist = [l.split("\t") for l in
            io.open(os.path.join(d, "history.txt"), errors="replace").read().splitlines() if l.strip()]
    bf = [float(r[1]) for r in hist[1:] if len(r) > 1]
    gain100 = (bf[-101] - bf[-1]) if len(bf) > 101 else None

    rec = {"cell": dep["cell"], "seed": dep["seed"], "result_dir": dep["result_dir"],
           "deposited_resolved_par": dep["resolved_par"],
           "deposited_speed_mps": dep["achieved_speed_mps"],
           "warm_start_par": warm,
           "deposit_resolved_the_warm_start": dep["resolved_par"] == warm,
           "true_final_par": best, "true_final_generation": gen,
           "n_generations_in_history": len(bf),
           "best_fitness_first": bf[0], "best_fitness_last": bf[-1],
           "final_100_gen_fitness_gain": gain100,
           "t_end_s": float(t[-1]), "n_cycles_in_window": len(cyc),
           "achieved_speed_mps": speed}
    out["cells"].append(rec)
    print("cell %d seed %d" % (rec["cell"], rec["seed"]))
    print("   deposited par   %-28s speed %.4f  <- WARM START" %
          (rec["deposited_resolved_par"], rec["deposited_speed_mps"]))
    print("   true final par  %-28s gen %d" % (best, gen))
    print("   t_end %.3f s, %d cycles in window" % (rec["t_end_s"], rec["n_cycles_in_window"]))
    print("   ACHIEVED SPEED  %s m/s" % ("undefined" if speed is None else "%.4f" % speed))
    print("   best_fitness %.4f -> %.4f, final-100-gen gain %s"
          % (bf[0], bf[-1], "n/a" if gain100 is None else "%.4f" % gain100))

sp = [c["achieved_speed_mps"] for c in out["cells"] if c.get("achieved_speed_mps") is not None]
if sp:
    mx = max(sp)
    if mx > SUCCESS:
        rung, verdict = "SUCCESS", "a warm start above 1.30 m/s exists; the velocity axis is deliverable"
    else:
        rung, verdict = "FAILURE", ("<= 1.30 m/s at 600 generations; the velocity axis is closed "
                                    "for this MODEL from its own warm start, not merely for the tool")
    out["max_achieved_speed_mps"] = mx
    out["RUNG"] = rung
    out["VERDICT"] = verdict
    print("\nmax achieved %.4f m/s against a success threshold of %.2f  ->  %s" % (mx, SUCCESS, rung))
    print(verdict)

out["defect"] = ("both deposits set resolved_par = warm_start because the launcher takes the "
                 "minimum objective encoded in the filename, and the warm start scored 0.988 "
                 "under min_velocity=1.0 while every result under 1.5 scores ~21-23")
q = os.path.join(PAPER, "VERIFY_R294.json")
json.dump(out, io.open(q, "w", encoding="utf-8"), indent=1)
print("\nwrote %s (%d bytes)" % (q, os.path.getsize(q)))
