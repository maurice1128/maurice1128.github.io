"""Is it the VELOCITY DEPENDENCE, or just the extra drive? The test that should have come first.

WHAT EVERYTHING SO FAR ESTABLISHED, AND WHAT IT DID NOT.
Removing the injected reflex from a converged spastic controller makes 3 of 4 runs fall
(`kv_zero_test.py`). Reducing its gain grades the equinus among survivors, with a stability hole at
KV 0.075 (`kv_dose_response.py`). But scaling a NATIVE plantarflexor gain the lesion never touched
produces the same shape -- scattered falls plus graded equinus -- so none of that is specific to
the injected reflex. And the co-adaptation explanation is refuted outright at matched depth
(`RESULT_coadaptation_refuted.md`).

So the reflex is necessary. Nothing yet shows that its VELOCITY DEPENDENCE is what matters -- and
velocity dependence is the entire clinical premise. It is what makes the modelled lesion
"spasticity" (Lance) rather than contracture or a tonic co-contraction, and the whole diagnostic
question presupposes it.

THE TEST.
Replace the velocity-gated term with a CONSTANT offset delivering the same mean drive to the same
muscles, in the same converged controller, changing nothing else:

    reflex ON              KV as optimized                       (baseline)
    reflex OFF             KV = 0                                (falls, or loses equinus)
    reflex OFF + tonic     KV = 0, C0 = matched mean drive       <- the discriminator

  tonic RESTORES equinus and stability -> the reflex acts as a DC bias. Velocity dependence is NOT
                                          the load-bearing part, and the clinical premise fails
                                          inside the model.
  tonic does NOT restore                -> the velocity gating is doing the work; the premise holds
                                          and this is the first positive evidence for it.

SIZING -- the error this must not repeat.
The previous control scaled `soleus.KF`, removing a term of steady mean 0.2388 against the injected
0.0017: a ~140x mismatch, so its failure said nothing about comparable perturbations. Here the
tonic level is measured from the run's own trace as the mean of the injected contribution
`KV * max(RV, 0)` over complete gait cycles, per muscle. Same mean drive, same muscles, same
controller. The ONLY thing removed is the gating on stretch velocity.

Three sizings are run because "matched drive" is ambiguous and choosing one after seeing the result
would be a researcher degree of freedom:
    mean    -- matches the cycle-mean contribution (equal total drive)
    rms     -- matches the RMS contribution (equal energetic weight, larger than the mean)
    window  -- matches the mean over only the frames where the reflex is ACTIVE (largest)
All are reported. A conclusion is drawn only if they agree.

★ BINDING LIMITATION -- DUTY CYCLE IS A SECOND UNCONTROLLED VARIABLE.
`KV * max(RV, 0)` with `allow_neg_V = 0` is silent whenever the muscle shortens: measured duty
cycle is 43-54%. A constant offset is on 100% of the cycle. So at matched MEAN the two differ in
BOTH the velocity gating and the temporal distribution of the drive, and the claim "only velocity
dependence changed" is FALSE as stated.

What this test can and cannot conclude, fixed in advance:
  tonic FAILS to restore  -> WEAK result. It shows only that this offset, at this sizing, on this
                             signal path, does not substitute. It does NOT establish that velocity
                             dependence is what matters, because duty cycle also differs.
  tonic DOES restore      -> STRONG result. A drive that is neither velocity-gated nor
                             phase-restricted reproduces the effect, so the velocity dependence is
                             not doing the work -- and the clinical premise fails inside the model.

The asymmetry is pre-committed here so it cannot be reinterpreted after the numbers arrive.

The missing third arm, stated so its absence is not mistaken for a result: a PHASE-MATCHED offset
-- constant within the reflex's active window and zero outside -- would isolate velocity gating
from duty cycle. It is not expressible as a `MuscleReflex` property in SCONE 2.4.4 as far as this
project has verified, so the `window` sizing below is an amplitude bracket, NOT the phase-matched
control. Any conclusion here is limited accordingly.
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
WORK = os.path.join(HERE, "tonic_swap")
RUNS = [("SPAS01_s2", 0.10), ("SPAS01_s3", 0.10), ("SPAS005_s3", 0.05), ("SPAS005_s4", 0.05)]


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
    return {"fell": False, "mean": float(np.mean(a[hs[0]:hs[-1]])), "n": len(hs) - 1}


def injected_levels(sto, kv):
    """Mean and RMS of the injected contribution, per muscle, over complete cycles."""
    cols, d = load_sto(sto)
    t = d[:, 0]
    grf, thr = grf_vertical(cols, d, "l")
    hs = [i for i in heel_strikes(t, grf, thresh=thr) if t[i] >= 1.0]
    if len(hs) < 3:
        return None
    a0, b0 = hs[0], hs[-1]
    out = {}
    for m in ("soleus", "gastroc"):
        rv = None
        for cand in ("%s_l.RV" % m, "/forceset/%s_l/RV" % m):
            if cand in cols:
                rv = d[:, cols.index(cand)]
                break
        if rv is None:
            return None
        add = kv * np.maximum(rv[a0:b0], 0.0)
        act = add > 0                       # frames where the reflex is actually contributing
        out[m] = {"mean": float(np.mean(add)),
                  "rms": float(np.sqrt(np.mean(add ** 2))),
                  "window": float(np.mean(add[act])) if act.any() else 0.0,
                  "duty": float(np.mean(act))}
    return out


def mutate_cfg(txt, kv, c0=None):
    """Rewrite ONLY the SpasticL block: set its KV, optionally add a constant offset C0."""
    m = re.search(r"(ReflexController\s*\{[^{}]*name\s*=\s*SpasticL.*?)(?=\n\s*\}\s*\n\s*\})",
                  txt, re.S)
    if not m:
        return None
    b = re.sub(r"KV\s*=\s*[0-9.]+", "KV = %.6f" % kv, m.group(1))
    if b.count("KV = %.6f" % kv) != 2:
        return None
    if c0 is not None:
        out, seen = [], 0
        for line in b.splitlines(True):
            out.append(line)
            mm = re.match(r"(\s*)target\s*=\s*(soleus_l|gastroc_l)", line)
            if mm:
                out.append("%sC0 = %.6f\n" % (mm.group(1), c0[mm.group(2).split("_")[0]]))
                seen += 1
        if seen != 2:
            return None
        b = "".join(out)
    return txt[:m.start(1)] + b + txt[m.end(1):]


def simulate(src, par, tag, kv, c0=None):
    w = os.path.join(WORK, tag)
    shutil.rmtree(w, ignore_errors=True)
    os.makedirs(w, exist_ok=True)
    for f in glob.glob(os.path.join(src, "*")):
        if os.path.isfile(f) and not f.endswith(".sto"):
            shutil.copy(f, w)
    cfg = os.path.join(w, "config.scone")
    new = mutate_cfg(open(cfg, encoding="utf-8", errors="ignore").read(), kv, c0)
    if new is None:
        return None, "mutation failed"
    open(cfg, "w", encoding="utf-8").write(new)
    p = subprocess.run([SCONECMD, "-e", os.path.join(w, os.path.basename(par))],
                       cwd=w, capture_output=True, timeout=900)
    if p.returncode != 0:
        return None, "sconecmd exit %d" % p.returncode
    s = [x for x in glob.glob(os.path.join(w, "*.sto")) if os.path.getsize(x) > 1000]
    if len(s) != 1:
        return None, "%d sto" % len(s)
    return ankle(s[0]), None


def fmt(r, err):
    if err:
        return err
    return "FELL (t=%.1fs)" % r["t_end"] if r["fell"] else "mean %7.2f  n=%d" % (r["mean"], r["n"])


def main():
    os.makedirs(WORK, exist_ok=True)
    print("Replacing velocity gating with a matched CONSTANT offset. Same controller throughout.\n")
    for tag, kv in RUNS:
        d = run_dir(tag)
        par = best_par(d) if d else None
        if par is None:
            print("%-12s no run" % tag)
            continue
        base, err = simulate(d, par, tag + "_on", kv)
        if err:
            print("%-12s baseline failed: %s" % (tag, err))
            continue
        sto = glob.glob(os.path.join(WORK, tag + "_on", "*.sto"))[0]
        lv = injected_levels(sto, kv)
        if lv is None:
            print("%-12s could not measure injected level" % tag)
            continue

        print("=== %s  (KV = %.2f) ===" % (tag, kv))
        for m in ("soleus", "gastroc"):
            print("   %-8s injected mean %.5f  rms %.5f  in-window %.5f  duty %.0f%%"
                  % (m, lv[m]["mean"], lv[m]["rms"], lv[m]["window"], 100 * lv[m]["duty"]))
        print("   -> the constant offset runs at 100%% duty against the reflex's %.0f%%;"
              % (100 * lv["soleus"]["duty"]))
        print("      duty cycle is therefore NOT controlled. See the header for what this limits.")
        print("   %-34s %s" % ("reflex ON (as optimized)", fmt(base, None)))
        off, e1 = simulate(d, par, tag + "_off", 0.0)
        print("   %-34s %s" % ("reflex OFF (KV = 0)", fmt(off, e1)))
        for kind in ("mean", "rms", "window"):
            c0 = {m: lv[m][kind] for m in ("soleus", "gastroc")}
            r, e = simulate(d, par, "%s_tonic_%s" % (tag, kind), 0.0, c0)
            print("   %-34s %s"
                  % ("OFF + tonic (%s-matched)" % kind, fmt(r, e)))
        print()

    print("Tonic restores equinus AND stability -> the reflex is a DC bias; velocity dependence")
    print("is not the load-bearing part, and the clinical premise fails inside this model.")
    print("Tonic does NOT restore -> the velocity gating is doing the work.")
    print("Conclude only if the mean-matched and rms-matched variants agree.")


if __name__ == "__main__":
    main()
