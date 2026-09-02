"""Gate: does the injected mechanism reach the model at the amount claimed? Run BEFORE any result.

WHY THIS EXISTS.
For the entire life of this project the injected spastic reflex was delivered at exactly 2x its
nominal gain, on every spastic run, on both muscles. Fourteen rounds of adversarial review missed
it, and could not have found it: two identical `MuscleReflex` instances compute identical outputs
and call StoreData with the SAME channel label, so `soleus_l.RV` reports ONE copy while
`soleus_l.input` contains TWO. Kinematics, GRF, activation, fitness and ankle angle are all exactly
what a correctly-injected gain of twice the size would produce -- a perfectly legal value inside the
declared range. The output file is otherwise indistinguishable.

The lesson is structural: **review of the analysis path cannot detect a defect on the injection
path.** No amount of further analysis-side scrutiny would have found this. The check has to sit
where the mechanism enters the model.

Two gates, both cheap, both fail loudly.

GATE 1 -- declared vs instantiated, free, no simulation.
SCONE encodes the INSTANTIATED reflex count in the results directory name as an `R<n>` token.
Every spastic scenario declares 2 MuscleReflex children; every spastic results directory reads
`...GH2010.R4.S10W...`. 2 declared, 4 built. That fingerprint has been in every path string in
this project since the first run. Absence of the token when reflexes are declared is the opposite
signature -- a total no-op, which is what happened to the historical SPASpf arm (KV = 8.0,
zero effect).

GATE 2 -- residual identity, free, works retroactively on archived .sto.
For a muscle whose reflex set contains no C0 term, `input` must equal the sum of its stored reflex
channels. In a healthy run this closes exactly (max residual 0.0). In a spastic run:

    (soleus_l.input - soleus_l.RF) / soleus_l.RV  ==  2.000000

k = 1 -> correct. k = 2 -> doubled. k = 0 or no channel -> silent no-op. Non-integer -> something
else is writing to the muscle.

NOTE the identity only closes for muscles with no pure-C0 reflex (soleus, gastroc, tib_ant here);
for vasti/iliopsoas/glut_max/hamstrings SCONE stores no channel for a C0 term, so the residual is
non-zero even when correct and the test is uninformative there. Those are skipped rather than
reported as failures.
"""
import glob
import os
import re
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from sto_utils import load_sto, muscle_signal  # noqa: E402

RES = r"C:\Users\maurice\Documents\SCONE\results"
# `tib_ant` was REMOVED. SCONE keys a cross-muscle reflex's channel on the SOURCE, so the
# GH2010 `target = tib_ant, source = soleus` term is stored under `soleus_l.RF`, not under
# tib_ant at all. Enumerating tib_ant's own channels therefore never closes -- residual
# 7.9e-03 (l) / 1.1e-02 (r) even in a HEALTHY run with no injection whatsoever. Including it
# made this script print FAILED on correct data, and made me report a bookkeeping artifact as
# a defect. Only soleus and gastroc satisfy: no foreign-source reflex, no pure-C0 term.
TESTABLE = ("soleus", "gastroc")


def gate1(tags):
    """Declared reflex count (from the scenario) vs instantiated (from the R<n> directory token)."""
    print("=" * 78)
    print("GATE 1 -- declared vs instantiated reflexes (from the results directory name)")
    print("=" * 78)
    bad = 0
    for tag in tags:
        ds = [d for d in glob.glob(os.path.join(RES, tag + ".*")) if os.path.isdir(d)]
        if not ds:
            continue
        d = max(ds, key=os.path.getmtime)
        cfg = os.path.join(d, "config.scone")
        if not os.path.exists(cfg):
            continue
        txt = open(cfg, encoding="utf-8", errors="ignore").read()
        # count MuscleReflex children of any controller that is NOT the GaitStateController
        m = re.search(r"ReflexController\s*\{[^{}]*name\s*=\s*\w+.*?(?=\n\s*\}\s*\n\s*\})",
                      txt, re.S)
        decl = len(re.findall(r"MuscleReflex", m.group(0))) if m else 0
        tok = re.search(r"\.R(\d+)\.", os.path.basename(d))
        inst = int(tok.group(1)) if tok else 0
        ok = (inst == decl)
        if decl == 0 and inst == 0:
            verdict = "no injection declared or built"
        elif decl > 0 and inst == 0:
            verdict = "*** SILENT NO-OP: declared but nothing built ***"
            bad += 1
        elif not ok:
            verdict = "*** MISMATCH: built %d for %d declared (x%.1f) ***" % (inst, decl,
                                                                             inst / decl)
            bad += 1
        else:
            verdict = "ok"
        print("  %-14s declared=%d instantiated=%d   %s" % (tag, decl, inst, verdict))
    return bad


def gate2(tags):
    """input must equal the sum of stored reflex channels, for muscles with no C0 term."""
    print("\n" + "=" * 78)
    print("GATE 2 -- residual identity  (input - RF) / RV   [1.0 = correct, 2.0 = doubled]")
    print("=" * 78)
    bad = 0
    for tag in tags:
        ds = [d for d in glob.glob(os.path.join(RES, tag + ".*")) if os.path.isdir(d)]
        if not ds:
            continue
        stos = [s for d in ds for s in glob.glob(os.path.join(d, "*.sto"))
                if os.path.getsize(s) > 1000]
        if not stos:
            continue
        cols, dat = load_sto(max(stos, key=os.path.getmtime))
        for m in TESTABLE:
            for side in ("l", "r"):
                inp = muscle_signal(cols, dat, m, side, "input")
                if inp is None:
                    continue
                comp = np.zeros_like(inp)
                chans = []
                for suf in ("RF", "RL", "RV"):
                    k = "%s_%s.%s" % (m, side, suf)
                    if k in cols:
                        comp = comp + dat[:, cols.index(k)]
                        chans.append(suf)
                rvk = "%s_%s.RV" % (m, side)
                if rvk not in cols:
                    resid = float(np.max(np.abs(inp - comp)))
                    if resid > 1e-6:
                        print("  %-13s %-8s %-2s no RV channel, residual %.3e  <- unexplained"
                              % (tag, m, side, resid))
                        bad += 1
                    continue
                rv = dat[:, cols.index(rvk)]
                base = comp - rv
                act = rv > 1e-9
                if not act.any():
                    continue
                k = np.median((inp[act] - base[act]) / rv[act])
                flag = ("" if abs(k - 1.0) < 1e-3 else
                        "  *** DOUBLED ***" if abs(k - 2.0) < 1e-3 else
                        "  *** k=%.4f, unexplained ***" % k)
                if flag:
                    bad += 1
                print("  %-13s %-8s %-2s k = %.6f  (channels %s)%s"
                      % (tag, m, side, k, "+".join(chans), flag))
    return bad


def gate0(tags):
    """A KV reflex on soleus_l MUST produce a soleus_l.RV channel. Absence proves non-instantiation.

    This catches the 0x family, which neither other gate can see. `SPASpf2` declares
    `symmetric = 0, target = soleus_l, source = soleus_l, KV = 8.0` and its .sto has NO
    soleus_l.RV channel, 420 columns, and max|input - RF| = 0.0 at every sample: a declared gain
    of 8.0 delivered exactly nothing, while the run optimized to generation 584 and produced a
    normal-looking gait. Free, retrospective, needs only the .sto header and the archived config.

    Note the irony worth recording: the 424-vs-420 channel difference that LEAKS the class label
    into every classifier is the same signal that VERIFIES instantiation. A defect for analysis is
    an asset for verification.
    """
    print("=" * 78)
    print("GATE 0 -- declared KV reflex must produce its .RV channel (catches silent 0x)")
    print("=" * 78)
    bad = 0
    for tag in tags:
        ds = [d for d in glob.glob(os.path.join(RES, tag + ".*")) if os.path.isdir(d)]
        if not ds:
            print("  %-14s NO RESULT DIRECTORY -- cannot verify (fail closed)" % tag)
            bad += 1
            continue
        d = max(ds, key=os.path.getmtime)
        cfg = os.path.join(d, "config.scone")
        if not os.path.exists(cfg):
            print("  %-14s no archived config.scone (fail closed)" % tag)
            bad += 1
            continue
        txt = open(cfg, encoding="utf-8", errors="ignore").read()
        want = set()
        for mm in re.finditer(r"target\s*=\s*(\w+_[lr])(?=[^{}]*?KV\s*=\s*([0-9.]+))", txt, re.S):
            if float(mm.group(2)) > 0:
                want.add("%s.RV" % mm.group(1))
        stos = [s for s in glob.glob(os.path.join(d, "*.sto")) if os.path.getsize(s) > 1000]
        if not stos:
            print("  %-14s declares %d KV reflex(es), no .sto to check yet" % (tag, len(want)))
            continue
        cols, _ = load_sto(max(stos, key=os.path.getmtime))
        missing = sorted(w for w in want if w not in cols)
        if not want:
            print("  %-14s no KV reflex declared" % tag)
        elif missing:
            print("  %-14s declares %s but .sto LACKS %s   *** SILENT NO-OP ***"
                  % (tag, sorted(want), missing))
            bad += 1
        else:
            print("  %-14s declares %s -- all present  ok" % (tag, sorted(want)))
    return bad


def main():
    tags = sys.argv[1:] or ["DHEALTHY_s1", "DPAR60_s1", "SPAS005", "SPAS01", "SPAS01_s2",
                            "CMS020_s1", "CMS030_s1", "MMIX20S01_s1", "SPASpf2"]
    b = gate0(tags) + gate1(tags) + gate2(tags)
    print("\n" + "=" * 78)
    if b:
        print("FAILED: %d gate violations. Do not read any result from these runs." % b)
    else:
        print("PASSED: every injected mechanism reaches the model at the amount declared.")
    print("=" * 78)
    return 1 if b else 0


if __name__ == "__main__":
    sys.exit(main())
