"""Is the reflex CAUSALLY holding the equinus, or is the controller just brittle? Dose-response.

THE WEAKNESS IN THE ON/OFF TEST.
`kv_zero_test.py` took each converged spastic controller, set KV = 0, and found that three of four
runs fall and the fourth loses its entire equinus (-12.72 -> +0.45 deg). I read that as "the
reflex is mechanically load-bearing".

That reading is not safe on its own. Every parameter in that controller was optimized *in the
presence* of KV = 0.10. Removing it is a large perturbation to a solution tuned around it, so a
fall is also consistent with a much weaker claim: **the controller is brittle to any change of
this size**, and the reflex is incidental. On/off cannot separate the two.

THE DISCRIMINATOR.
Sweep the gain down in steps on the SAME converged controller and watch the shape of the response:

  MONOTONE RECESSION  (equinus shrinks smoothly as KV falls, e.g. -12.7 -> -9 -> -5 -> -1 -> +0.5)
      -> the reflex is holding the posture, and its contribution is graded with its gain. The
         load-bearing claim survives.
  CLIFF               (unchanged at 0.09, 0.08 ... then abrupt failure)
      -> the controller sits on a knife edge and the outcome is about fragility, not about the
         reflex doing mechanical work. The load-bearing claim dies.

A dose-response curve is the standard way to tell a causal agent from a brittle equilibrium, and
here it costs only replays -- no optimization.

CONTROL ARM, for the same reason.
Perturbing ONE parameter and seeing a fall proves nothing unless perturbing a comparable parameter
by a comparable amount does NOT cause a fall. So the same sweep is applied to a control gain the
lesion never touched: the native `KF` on soleus, scaled by the same fractional steps. If scaling an
arbitrary native gain by 0.75/0.50/0.25/0 also destroys the gait, then the model is simply fragile
and nothing about the injected reflex is special.

Sign convention: ankle angle negative = plantarflexion = equinus.
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
from sto_utils import col, grf_vertical, heel_strikes, load_sto  # noqa: E402

RES = r"C:\Users\maurice\Documents\SCONE\results"
SCONECMD = r"C:\Program Files\SCONE\bin\sconecmd.exe"
WORK = os.path.join(HERE, "kv_dose")
FRACS = [1.0, 0.75, 0.50, 0.25, 0.10, 0.0]
RUNS = [("SPAS01_s2", 0.10), ("SPAS005_s3", 0.05)]


def run_dir(tag):
    ds = [d for d in glob.glob(os.path.join(RES, tag + ".*")) if os.path.isdir(d)]
    return max(ds, key=os.path.getmtime) if ds else None


def best_par(d):
    bp, bf = None, 1e9
    for p in sorted(glob.glob(os.path.join(d, "0*.par"))):
        m = re.match(r"^(\d+)_.*?_([0-9.]+)$", os.path.basename(p)[:-4])
        if m and float(m.group(2)) < bf:
            bp, bf = p, float(m.group(2))
    return bp


def ankle(sto, side="l"):
    cols, d = load_sto(sto)
    if d.size == 0:
        return None
    t = d[:, 0]
    a = np.degrees(col(cols, d, "ankle_angle_%s" % side))
    grf, thr = grf_vertical(cols, d, side)
    hs = [i for i in heel_strikes(t, grf, thresh=thr) if t[i] >= 1.0]
    if len(hs) < 3:
        return {"fell": True, "t_end": float(t[-1])}
    return {"fell": False, "mean": float(np.mean(a[hs[0]:hs[-1]])),
            "min": float(np.min(a[hs[0]:hs[-1]])), "n": len(hs) - 1}


def simulate(src_dir, par, tag, mutate, target="config"):
    """target='config' for the injected KV (a fixed literal in the scenario);
    target='par'   for a NATIVE gain (a free parameter, whose replayed value lives in the .par).

    This distinction matters and got the control wrong the first time: free parameters appear in
    config.scone only as search ranges (`KF = "~1.6<-10,10>"`), and `sconecmd -e` takes their actual
    values from the .par. Editing the config would have changed nothing on replay.
    """
    w = os.path.join(WORK, tag)
    if os.path.isdir(w):
        shutil.rmtree(w, ignore_errors=True)
    os.makedirs(w, exist_ok=True)
    for f in glob.glob(os.path.join(src_dir, "*")):
        if os.path.isfile(f) and not f.endswith(".sto"):
            shutil.copy(f, w)
    path = os.path.join(w, "config.scone" if target == "config" else os.path.basename(par))
    txt = open(path, encoding="utf-8", errors="ignore").read()
    new = mutate(txt)
    if new is None:
        return None, "mutation failed"
    open(path, "w", encoding="utf-8").write(new)
    p = subprocess.run([SCONECMD, "-e", os.path.join(w, os.path.basename(par))],
                       cwd=w, capture_output=True, timeout=900)
    if p.returncode != 0:
        return None, "sconecmd exit %d" % p.returncode
    s = [x for x in glob.glob(os.path.join(w, "*.sto")) if os.path.getsize(x) > 1000]
    if len(s) != 1:
        return None, "%d sto" % len(s)
    return ankle(s[0]), None


def set_injected_kv(txt, kv):
    """Only the SpasticL block's KV -- the native controller's own KV gains must not move."""
    m = re.search(r"(ReflexController\s*\{[^{}]*name\s*=\s*SpasticL.*?)(?=\n\s*\}\s*\n\s*\})",
                  txt, re.S)
    if not m:
        return None
    block = m.group(1)
    nb = re.sub(r"KV\s*=\s*[0-9.]+", "KV = %.4f" % kv, block)
    if nb.count("KV = %.4f" % kv) != 2:
        return None
    return txt[:m.start(1)] + nb + txt[m.end(1):]


def scale_native_kf(par_txt, frac):
    """Control: scale the NATIVE soleus KF in the .par -- a gain the lesion never touched.

    Matched in absolute effect to the injected sweep: the same fractional steps are applied, so if
    the model simply cannot survive a perturbation of this size to ANY plantarflexor gain, the
    control falls too and the injected sweep proves nothing about the reflex specifically.
    """
    out, hit = [], False
    for line in par_txt.splitlines(True):
        p = line.split()
        if len(p) >= 2 and p[0] == "S00111.soleus.KF":
            try:
                v = float(p[1]) * frac
            except ValueError:
                out.append(line)
                continue
            out.append(line.replace(p[1], "%.8g" % v, 1))
            hit = True
        else:
            out.append(line)
    return "".join(out) if hit else None


def main():
    os.makedirs(WORK, exist_ok=True)
    for tag, kv0 in RUNS:
        d = run_dir(tag)
        par = best_par(d) if d else None
        if par is None:
            print("%s: no run" % tag)
            continue
        print("\n=== %s  (injected KV = %.2f as optimized) ===" % (tag, kv0))
        print("%-22s %-34s" % ("condition", "outcome"))
        print("-" * 58)
        for fr in FRACS:
            kv = kv0 * fr
            r, err = simulate(d, par, "%s_kv%03d" % (tag, round(fr * 100)),
                              lambda t, k=kv: set_injected_kv(t, k))
            if err:
                print("  injected KV %.4f    %s" % (kv, err))
            elif r["fell"]:
                print("  injected KV %.4f    FELL (t=%.1fs)" % (kv, r["t_end"]))
            else:
                print("  injected KV %.4f    mean %7.2f  min %7.2f  n=%d"
                      % (kv, r["mean"], r["min"], r["n"]))

        print("  --- control: scale a NATIVE gain the lesion never touched ---")
        for fr in FRACS:
            r, err = simulate(d, par, "%s_kf%03d" % (tag, round(fr * 100)),
                              lambda t, f=fr: scale_native_kf(t, f), target="par")
            if err:
                print("  native soleus KF x%.2f  %s" % (fr, err))
            elif r["fell"]:
                print("  native soleus KF x%.2f  FELL (t=%.1fs)" % (fr, r["t_end"]))
            else:
                print("  native soleus KF x%.2f  mean %7.2f  min %7.2f  n=%d"
                      % (fr, r["mean"], r["min"], r["n"]))

    print("\nMonotone recession of equinus with injected KV, while the native-gain control")
    print("survives comparable scaling -> the reflex is causally holding the posture.")
    print("A cliff in both -> the controller is brittle and the on/off result meant nothing.")


if __name__ == "__main__":
    main()
