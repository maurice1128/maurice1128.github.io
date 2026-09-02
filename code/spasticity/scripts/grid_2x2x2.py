"""Which structural variable controls delivery? 2x2x2, one generation each, measured not argued.

THE QUESTION, AND WHY IT NEEDED A GRID.
The injected reflex is delivered at 2.000x nominal in every working spastic run, and at exactly
0.000x in SPASpf / SPASpf (1) / SPASpf2. Three things differ between those two groups:

    CompositeController wrapper   present in every 2x run, absent in every 0x run
    symmetric on the block        absent  in every 2x run, = 0    in every 0x run
    explicit source = target      absent  in every 2x run, present in every 0x run

n = 2 zero cases against n = 3 doubled cases, with three variables moving together. **Nothing is
identified.** I blamed `symmetric = 0` and wrote it into the generator as a prohibition -- inside a
comment warning against over-attribution. The watchdog then blamed the same variable one round
later, in the document retracting my version of it. Both of us reasoned from confounded
observational evidence and both of us were wrong to.

This is the experiment that settles it, and it is cheap: 8 cells, one generation each, replay only.

WHY IT CAN RUN NOW AND COULD NOT BEFORE.
Holding the generator at a known-broken 2x was correct only while no instrument could measure
delivery -- swapping a measured 2x for an unmeasured change would have been trading a known defect
for an unknown one. `delivered_gain.py` now measures rho = K_hat / K_declared against gain-free
plant state, calibrated at rho = 2.03 (n = 60) on the known 2x and rho = 0.0000 on both known 0x.
So the justification for holding has expired: run the grid, adopt whichever cell reads rho ~ 1.0.

WHAT COUNTS AS AN ANSWER.
Each cell is scored by delivered_gain.py, not by the `.R<n>` directory token (whose semantics this
project could never establish) and not by any channel count (which varies with which gains happen
to be non-zero -- `kv_dose\SPAS005_s3_kf000\` has 422 columns because an optimised gain went to 0).

    rho ~ 1.0  -> correct delivery. Adopt this cell in gen_conditions.spastic_block().
    rho ~ 2.0  -> duplicated.
    rho ~ 0.0  -> never instantiated.

If more than one cell reads 1.0, prefer the one differing least from the current generator, and
record the others. If none does, the mechanism is outside these three variables and this grid has
falsified the whole line of attribution -- which is also a result.
"""
import glob
import itertools
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "opt2")
GRID = os.path.join(HERE, "opt_grid222")
SCONECMD = r"C:\Program Files\SCONE\bin\sconecmd.exe"
KV = 0.10


def build(wrapper, symmetric, source):
    """Return scenario text with the three structural variables set independently."""
    txt = open(os.path.join(SRC, "SPAS01.scone"), encoding="utf-8", errors="ignore").read()

    m = re.search(r"([ \t]*)ReflexController\s*\{[^{}]*?name\s*=\s*SpasticL.*?\n\1\}\n",
                  txt, re.S)
    if not m:
        return None
    indent = m.group(1)
    blk = [indent + "ReflexController {", indent + "\tname = SpasticL"]
    if symmetric:
        blk.append(indent + "\tsymmetric = 0")
    for mus in ("soleus_l", "gastroc_l"):
        blk += [indent + "\tMuscleReflex {", indent + "\t\ttarget = %s" % mus]
        if source:
            blk.append(indent + "\t\tsource = %s" % mus)
        blk += [indent + "\t\tdelay = 0.020",
                indent + "\t\tKV = %.3f" % KV,
                indent + "\t\tallow_neg_V = 0",
                indent + "\t}"]
    blk.append(indent + "}")
    txt = txt[:m.start()] + "\n".join(blk) + "\n" + txt[m.end():]

    if not wrapper:
        # unwrap: CompositeController { GaitStateController {...} ReflexController {...} }
        # becomes GaitStateController {...} and ReflexController {...} as siblings.
        c = re.search(r"([ \t]*)CompositeController\s*\{\n", txt)
        if not c:
            return None
        # drop the opening line and its matching close (the line with the same indent + '}')
        txt = txt[:c.start()] + txt[c.end():]
        ind = c.group(1)
        close = re.search(r"\n%s\}\n(?=%s?CompositeMeasure|\s*CompositeMeasure)" % (ind, ind), txt)
        if not close:
            close = re.search(r"\n%s\}\n" % ind, txt[c.start():])
            if not close:
                return None
            s = c.start() + close.start()
            txt = txt[:s] + txt[s + len(close.group(0)) - 1:]
        else:
            txt = txt[:close.start()] + txt[close.end() - 1:]
    return txt


def main():
    os.makedirs(GRID, exist_ok=True)
    for f in (glob.glob(os.path.join(SRC, "*.osim")) + glob.glob(os.path.join(SRC, "*.zml"))
              + glob.glob(os.path.join(SRC, "*.par"))):
        d = os.path.join(GRID, os.path.basename(f))
        if not os.path.exists(d):
            shutil.copy(f, d)

    launched = []
    for wrapper, symmetric, source in itertools.product((1, 0), repeat=3):
        tag = "G%d%d%d" % (wrapper, symmetric, source)
        txt = build(wrapper, symmetric, source)
        if txt is None:
            print("  %-6s BUILD FAILED -- not launched" % tag)
            continue
        txt = re.sub(r"signature_prefix\s*=\s*\S+", "signature_prefix = " + tag, txt, count=1)
        txt = re.sub(r"min_progress\s*=\s*\S+", "min_progress = 1e-7\n\tmax_generations = 1",
                     txt, count=1)

        checks = {
            "wrapper as intended": (("CompositeController" in txt) == bool(wrapper)),
            "symmetric as intended": (("symmetric = 0" in txt) == bool(symmetric)),
            "source as intended": (("source = soleus_l" in txt) == bool(source)),
            "KV on both muscles": txt.count("KV = %.3f" % KV) == 2,
        }
        bad = [k for k, v in checks.items() if not v]
        if bad:
            print("  %-6s NOT LAUNCHED -- %s" % (tag, ", ".join(bad)))
            continue

        p = os.path.join(GRID, tag + ".scone")
        # BOM-free: PowerShell's Set-Content -Encoding utf8 writes a BOM that SCONE cannot parse
        # ("Error parsing line 1: Invalid label CmaOptimizer"). Learned the hard way.
        with open(p, "w", encoding="utf-8", newline="") as fh:
            fh.write(txt)
        with open(os.path.join(GRID, "log_%s.txt" % tag), "w") as lg:
            subprocess.Popen([SCONECMD, "-o", p, "-l", "2"], cwd=GRID,
                             stdout=lg, stderr=subprocess.STDOUT)
        launched.append((tag, wrapper, symmetric, source))
        print("  launched %-6s wrapper=%d symmetric0=%d source=%d" % (tag, wrapper, symmetric,
                                                                     source))

    print("\nlaunched %d/8 cells (1 generation each).")
    print("When they finish, score EVERY cell with:")
    print("    python delivered_gain.py <result_dir>")
    print("and adopt the cell reading rho ~ 1.0. Do NOT score by the .R<n> token or column count.")
    for tag, w, s, so in launched:
        print("    %-6s wrapper=%d symmetric=0:%d explicit source:%d" % (tag, w, s, so))


if __name__ == "__main__":
    sys.exit(main())
