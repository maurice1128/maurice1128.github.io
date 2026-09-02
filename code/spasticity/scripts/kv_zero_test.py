"""Does the CONTROLLER own the equinus, or does the REFLEX own it? One replay settles it.

THE OPEN QUESTION.
I claimed the equinus in the spastic arm is produced by the re-optimization responding to the
reflex's COST, not by the reflex acting mechanically -- on the grounds that the reflex contributes
< 6 % of plantarflexor excitation at peak stretch. Round 11 refuted the reasoning three ways:

 1. amplitude ratio is not a stability criterion in a delayed-feedback limit cycle;
 2. the < 6 % is measured on the ALREADY-ADAPTED gait, and the optimizer's entire job was to make
    the reflex harmless -- so finding it harmless afterwards is circular;
 3. this project's own `scone_naive_ladder.json` shows the frozen healthy controller FALLS at
    KV 0.01, one tenth of the gain in question. A perturbation that prevents walking is not
    mechanically negligible.

THE TEST, which needs no new machinery.
Take the converged spastic run's OWN best controller -- every optimized parameter unchanged -- and
simply switch the injected reflex off (KV = 0). Re-simulate. Nothing else differs.

    equinus PERSISTS  -> the adapted controller itself produces the plantarflexed gait. The reflex
                         shaped the optimization but is not holding the posture. My cost-route
                         claim survives in weakened form.
    equinus COLLAPSES -> the reflex is actively holding the ankle down every stride. It is acting
                         mechanically, and the cost-route claim is dead.

Either way the answer is a fact about the model rather than an inference from an amplitude ratio.

Also reported, because round 11 found it and it undercuts the < 6 % figure independently: the
excitation level of soleus at the instant the reflex peaks. If soleus is already SATURATED there,
the injected increment is clipped and contributes nothing -- meaning the ratio was measured at the
one moment it structurally cannot act.
"""
import glob
import os
import re
import shutil
import subprocess
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from sto_utils import col, grf_vertical, heel_strikes, load_sto, muscle_signal  # noqa: E402

RES = r"C:\Users\maurice\Documents\SCONE\results"
SCONECMD = r"C:\Program Files\SCONE\bin\sconecmd.exe"
WORK = os.path.join(HERE, "kv_zero")
PAIRS = [("SPAS01_s2", 0.10), ("SPAS01_s3", 0.10), ("SPAS005_s3", 0.05), ("SPAS005_s4", 0.05)]


def run_dir(tag):
    ds = [d for d in glob.glob(os.path.join(RES, tag + ".*")) if os.path.isdir(d)]
    return max(ds, key=os.path.getmtime) if ds else None


def best_par(d):
    bp, bf = None, 1e9
    for p in sorted(glob.glob(os.path.join(d, "0*.par"))):
        m = re.match(r"^(\d+)_.*?_([0-9.]+)$", os.path.basename(p)[:-4])
        if m and float(m.group(2)) < bf:
            bp, bf = p, float(m.group(2))
    return bp, bf


def ankle_stats(sto, side="l"):
    cols, d = load_sto(sto)
    if d.size == 0:
        return None
    t = d[:, 0]
    a = np.degrees(col(cols, d, "ankle_angle_%s" % side))
    grf, thr = grf_vertical(cols, d, side)
    hs = [i for i in heel_strikes(t, grf, thresh=thr) if t[i] >= 1.0]
    if len(hs) < 3:
        return {"fell": True, "t_end": float(t[-1]), "n_cycles": len(hs)}
    a0, b0 = hs[0], hs[-1]
    return {"fell": False, "mean": float(np.mean(a[a0:b0])), "min": float(np.min(a[a0:b0])),
            "hs": float(np.mean([a[i] for i in hs])), "n_cycles": len(hs) - 1,
            "t_end": float(t[-1])}


def saturation_check(sto, kv):
    """At the frame where the injected term peaks, is soleus already at excitation 1.0?"""
    cols, d = load_sto(sto)
    out = []
    for m in ("soleus", "gastroc"):
        rv = None
        for cand in ("%s_l.RV" % m, "/forceset/%s_l/RV" % m):
            if cand in cols:
                rv = d[:, cols.index(cand)]
                break
        exc = muscle_signal(cols, d, m, "l", "excitation")
        if rv is None or exc is None:
            continue
        add = kv * np.maximum(rv, 0.0)
        i = int(np.argmax(add))
        out.append((m, float(add[i]), float(exc[i])))
    return out


def main():
    os.makedirs(WORK, exist_ok=True)
    print("Switching KV to 0 in the spastic run's OWN converged controller.\n")
    print("%-12s %-4s %-26s %-26s" % ("run", "KV", "WITH reflex", "reflex OFF"))
    print("-" * 74)
    for tag, kv in PAIRS:
        d = run_dir(tag)
        if d is None:
            print("%-12s no run dir" % tag)
            continue
        par, fit = best_par(d)
        if par is None:
            print("%-12s no .par" % tag)
            continue

        # --- baseline: the run as optimized -------------------------------------------------
        w0 = os.path.join(WORK, tag + "_on")
        os.makedirs(w0, exist_ok=True)
        for f in glob.glob(os.path.join(d, "*")):
            if os.path.isfile(f) and not f.endswith(".sto"):
                shutil.copy(f, w0)
        subprocess.run([SCONECMD, "-e", os.path.join(w0, os.path.basename(par))],
                       cwd=w0, capture_output=True, timeout=900)
        s0 = [x for x in glob.glob(os.path.join(w0, "*.sto")) if os.path.getsize(x) > 1000]
        on = ankle_stats(s0[0]) if s0 else None

        # --- same controller, reflex switched off -------------------------------------------
        w1 = os.path.join(WORK, tag + "_off")
        os.makedirs(w1, exist_ok=True)
        for f in glob.glob(os.path.join(d, "*")):
            if os.path.isfile(f) and not f.endswith(".sto"):
                shutil.copy(f, w1)
        cfg = os.path.join(w1, "config.scone")
        txt = open(cfg, encoding="utf-8", errors="ignore").read()
        new = re.sub(r"KV = 0\.[0-9]+", "KV = 0.0000", txt)
        n_changed = len(re.findall(r"KV = 0\.0000", new)) - len(re.findall(r"KV = 0\.0000", txt))
        if n_changed < 2:
            print("%-12s could not zero both reflex gains (changed %d)" % (tag, n_changed))
            continue
        open(cfg, "w", encoding="utf-8").write(new)
        subprocess.run([SCONECMD, "-e", os.path.join(w1, os.path.basename(par))],
                       cwd=w1, capture_output=True, timeout=900)
        s1 = [x for x in glob.glob(os.path.join(w1, "*.sto")) if os.path.getsize(x) > 1000]
        off = ankle_stats(s1[0]) if s1 else None

        def fmt(x):
            if x is None:
                return "replay failed"
            if x["fell"]:
                return "FELL (t=%.1fs, %d hs)" % (x["t_end"], x["n_cycles"])
            return "mean %6.2f  min %6.2f  n=%d" % (x["mean"], x["min"], x["n_cycles"])

        print("%-12s %.2f %-26s %-26s" % (tag, kv, fmt(on), fmt(off)))
        if on and off and not on["fell"] and not off["fell"]:
            print("             -> equinus change when reflex removed: %+.2f deg"
                  % (off["mean"] - on["mean"]))
        if s0:
            for m, add, exc in saturation_check(s0[0], kv):
                flag = "  <- SATURATED, increment clipped" if exc >= 0.999 else ""
                print("             %-8s peak injected %.4f  at excitation %.4f%s"
                      % (m, add, exc, flag))
    print("\nEquinus persists with the reflex off -> the adapted controller holds the posture.")
    print("Equinus collapses               -> the reflex is acting mechanically every stride.")


if __name__ == "__main__":
    main()
