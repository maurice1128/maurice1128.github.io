# -*- coding: utf-8 -*-
"""r418: build the soleus-KV ladder at FIXED gastroc KV = 0.050, frozen controller.

Registered by paper/PREREG_slack_r418.md (a908b4b7...). Template is the r410 BOTH staging cell,
which carries a soleus MuscleReflex followed by a gastroc MuscleReflex, both KV 0.050. Only the
SOLEUS KV is edited; the gastroc line is asserted unchanged afterwards. Replay writes FROZEN.par.sto
beside the .par inside our own staging tree -- nothing is written to the SCONE results directory,
so the 112 protected runs are untouchable by construction here.
"""
import io
import os
import re
import shutil
import subprocess
import sys

BASE = r"C:\Users\maurice\Desktop\spasticity_paper\scone\probe3d_r141"
SRC = os.path.join(BASE, "frozen2_r410")
DST = os.path.join(BASE, "slack_r418")
SCONE = r"C:\Program Files\SCONE\bin\sconecmd.exe"
RUNGS = ["0.000", "0.0125", "0.025", "0.050", "0.075", "0.100"]
SEEDS = [101, 102, 103, 104, 105, 106]

# ANCHORED to the SpasticL block. The GH2010 controller above it contains many other
# `target = soleus` / `target = gastroc` lines, and an unanchored search edits one of those --
# caught by the gastroc guard on the first build attempt, before anything was replayed.
SOL_RE = re.compile(r"(target\s*=\s*soleus\s+delay\s*=\s*0\.020\s+KV\s*=\s*)([0-9.]+)")
GAS_RE = re.compile(r"target\s*=\s*gastroc\s+delay\s*=\s*0\.020\s+KV\s*=\s*([0-9.]+)")


def tag(kv):
    return "sk" + kv.replace(".", "")


def build(kv, seed):
    src = os.path.join(SRC, "R410BOTH_s%d" % seed)
    name = "R418%s_s%d" % (tag(kv), seed)
    dst = os.path.join(DST, name)
    if os.path.isdir(dst):
        shutil.rmtree(dst)
    shutil.copytree(src, dst)
    stale = os.path.join(dst, "FROZEN.par.sto")
    if os.path.exists(stale):
        os.remove(stale)

    cfg = os.path.join(dst, "config.scone")
    s = io.open(cfg, encoding="utf-8").read()
    i = s.index("name = SpasticL")
    head, blk = s[:i], s[i:]

    m = SOL_RE.search(blk)
    assert m, "%s: soleus KV not found inside SpasticL" % name
    blk = blk[:m.start(2)] + kv + blk[m.end(2):]

    g = GAS_RE.search(blk)
    assert g and g.group(1) == "0.050", "%s: gastroc KV is %s" % (name, g and g.group(1))
    got = SOL_RE.search(blk)          # group(1) is the prefix; the NUMBER is group(2)
    assert got.group(2) == kv, "%s: soleus KV is %s not %s" % (name, got.group(2), kv)

    # signature_prefix sits ABOVE the SpasticL block, so it lives in `head`, not `blk`.
    s2 = (head + blk).replace("signature_prefix = R410BOTH_s%d" % seed,
                              "signature_prefix = %s" % name)
    assert "R410BOTH" not in s2, "%s: stale signature_prefix" % name
    io.open(cfg, "w", encoding="utf-8", newline="").write(s2)
    return dst, name


if __name__ == "__main__":
    os.makedirs(DST, exist_ok=True)
    built = [build(kv, s) for kv in RUNGS for s in SEEDS]
    print("built %d cells under %s" % (len(built), DST))
    sys.stdout.flush()

    ok = fail = 0
    for i, (d, name) in enumerate(built, 1):
        try:
            r = subprocess.run([SCONE, "-e", "FROZEN.par"], cwd=d, capture_output=True,
                               text=True, timeout=900)
            last = ((r.stdout or "") + (r.stderr or "")).strip().splitlines()[-1:]
        except Exception as e:
            last = [repr(e)]
        sto = os.path.join(d, "FROZEN.par.sto")
        if os.path.exists(sto) and os.path.getsize(sto) > 0:
            ok += 1
        else:
            fail += 1
            print("  FAIL %s :: %s" % (name, last))
        if i % 6 == 0:
            print("  %d/%d  ok %d  fail %d" % (i, len(built), ok, fail))
            sys.stdout.flush()
    print("DONE built %d  sto %d  fail %d" % (len(built), ok, fail))
