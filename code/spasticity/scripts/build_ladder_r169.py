# -*- coding: utf-8 -*-
"""Build the re-optimised 3D DOSE LADDER of PREREG_3d_ladder_r169.md
   sha256 e3ec76aa98759c821ef410889d3fc5d2840297bfc93482e00efc85e244e6d703
   hashed BEFORE this file was written and before any scenario file existed.

Where this script and that registration disagree, THE REGISTRATION DECIDES.

LADDER (section 2, levels FIXED, none may be added):
   spastic  KV        in {0.050, 0.150, 0.400}   soleus+gastroc, legs=left, allow_neg_V=0
   weak     tib_ant_l in {0.80, 0.90, 0.95} x 1759.0
   control  KV 0, x1.00
   seeds 101-106 at every rung, max_generations = 90, same warm start.

REUSE BY CONSTRUCTION IDENTITY (section 2): the r151 control, KV 0.050 and x0.80 arms ARE
this ladder's control, spastic rung 1 and weak rung 1. This script REGENERATES each of those
configs from the same template and compares them BYTE-WISE to the r151 files on disk, together
with the .hfd. It does not assume they are the same. If any comparison fails the rung is
marked REBUILD and this script exits non-zero rather than reusing it.

Nothing here runs sconecmd. No --run. No --launch. Writes stay under Desktop\\spasticity_paper.
"""
import io
import os
import re
import sys
import json
import shutil
import filecmp

sys.path.insert(0, r"C:\Users\maurice\Desktop\spasticity_paper\scone")
import gen_seeds as GS

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

BASE = r"C:\Users\maurice\Desktop\spasticity_paper\scone\probe3d_r141"
R151 = os.path.join(BASE, "reopt_r151")
ROOT = os.path.join(BASE, "ladder_r169")
TEMPLATE = os.path.join(BASE, "timing3d", "config.scone")
SRC = os.path.join(BASE, "bench_D20")
HFD = "H1922v7b3.hfd"
ZML = "InitStateH0918Gait10ActA.zml"
PARF = os.path.join("par", "H1922v7b3-TSG3Dv8g-989_fixed2.par")
SEEDS = [101, 102, 103, 104, 105, 106]
TA_BASE = 1759.0
PREREG = "e3ec76aa98759c821ef410889d3fc5d2840297bfc93482e00efc85e244e6d703"

# rung id -> (kind, kv string or None, tib_ant scale, tag prefix, reuse-from-r151 prefix or None)
RUNGS = [
    ("C",     "control", None,    1.00, "R151C",    "R151C"),
    ("S050",  "spastic", "0.050", 1.00, "R151S",    "R151S"),
    ("S150",  "spastic", "0.150", 1.00, "R169S150", None),
    ("S400",  "spastic", "0.400", 1.00, "R169S400", None),
    ("W080",  "weak",    None,    0.80, "R151W",    "R151W"),
    ("W090",  "weak",    None,    0.90, "R169W090", None),
    ("W095",  "weak",    None,    0.95, "R169W095", None),
]

SPASTIC_BLOCK = """
					ConditionalController {
						states = "EarlyStance LateStance Liftoff Swing Landing"
						legs = left
						ReflexController {
							name = SpasticL
							MuscleReflex {
								target = soleus
								delay = 0.020
								KV = %s
								allow_neg_V = 0
							}
							MuscleReflex {
								target = gastroc
								delay = 0.020
								KV = %s
								allow_neg_V = 0
							}
						}
					}
"""


def edit_tib_ant_l(path, scale):
    lines = io.open(path, encoding="utf-8", newline="").read().splitlines(True)
    i = next(k for k, ln in enumerate(lines) if ln.strip() == "name = tib_ant_l")
    j = next(k for k in range(i, len(lines)) if "max_isometric_force" in lines[k])
    lines[j] = lines[j][:lines[j].index("=") + 1] + (" %.1f\n" % (TA_BASE * scale))
    io.open(path, "w", encoding="utf-8", newline="").write("".join(lines))
    return lines[j].strip()


def line_diff(a, b):
    x = io.open(a, encoding="utf-8").read().splitlines()
    y = io.open(b, encoding="utf-8").read().splitlines()
    return [k for k in range(min(len(x), len(y))) if x[k] != y[k]], len(x) == len(y)


def make_config(tmpl, tag, kind, kv, seed):
    txt = re.sub(r"signature_prefix\s*=\s*\S+", "signature_prefix = " + tag, tmpl, count=1)
    if kind == "spastic":
        anchor = txt.rindex("ConditionalController")
        close = txt.index("\n\t\t\t\t}\n", anchor)
        txt = txt[:close] + "\n" + (SPASTIC_BLOCK % (kv, kv)) + txt[close:]
        assert txt.count("name = SpasticL") == 1, "%s: SpasticL not inserted exactly once" % tag
        assert txt.count("KV = " + kv) == 2, "%s: KV = %s must appear exactly twice" % (tag, kv)
    else:
        assert "SpasticL" not in txt, "%s: unexpected SpasticL" % tag
    txt = GS.set_seed(txt, seed)                 # registered writer; it reads the write back
    return txt


def main():
    if os.path.isdir(ROOT):
        shutil.rmtree(ROOT)
    os.makedirs(ROOT)
    tmpl = io.open(TEMPLATE, encoding="utf-8", newline="").read()

    built, reused, failures, manifest = [], [], [], []
    print("=" * 90)
    print("BUILD -- PREREG_3d_ladder_r169.md  sha256 %s..." % PREREG[:16])
    print("=" * 90)

    for rid, kind, kv, scale, prefix, reuse in RUNGS:
        for s in SEEDS:
            tag = "%s_s%d" % (prefix, s)
            d = os.path.join(ROOT, tag)
            os.makedirs(os.path.join(d, "par"))
            shutil.copy2(os.path.join(SRC, HFD), os.path.join(d, HFD))
            shutil.copy2(os.path.join(SRC, ZML), os.path.join(d, ZML))
            shutil.copy2(os.path.join(SRC, PARF), os.path.join(d, PARF))

            txt = make_config(tmpl, tag, kind, kv, s)
            cp = os.path.join(d, "config.scone")
            io.open(cp, "w", encoding="utf-8", newline="").write(txt)

            taline = None
            if kind == "weak":
                taline = edit_tib_ant_l(os.path.join(d, HFD), scale)
                diffs, samelen = line_diff(os.path.join(SRC, HFD), os.path.join(d, HFD))
                assert samelen and len(diffs) == 1, \
                    "%s: weak model must differ in exactly one line, got %r" % (tag, diffs)
            else:
                diffs, _ = line_diff(os.path.join(SRC, HFD), os.path.join(d, HFD))
                assert not diffs, "%s: model must be identical to control" % tag

            # ---- verification, not assumption -------------------------------
            t2 = io.open(cp, encoding="utf-8").read()
            assert GS.read_seed(t2) == s, "%s: random_seed readback failed" % tag
            assert "max_generations = 90" in t2, "%s: lost max_generations" % tag

            rec = {"rung": rid, "tag": tag, "kind": kind, "kv": kv, "ta_scale": scale,
                   "ta_line": taline, "seed": s, "reused": False}

            # ---- section 2: byte-wise reuse verification --------------------
            if reuse:
                oc = os.path.join(R151, tag, "config.scone")
                oh = os.path.join(R151, tag, HFD)
                if not (os.path.exists(oc) and os.path.exists(oh)):
                    failures.append((tag, "r151 artefact missing"))
                    rec["reuse_check"] = "MISSING"
                else:
                    same_c = io.open(oc, "rb").read() == io.open(cp, "rb").read()
                    same_h = filecmp.cmp(oh, os.path.join(d, HFD), shallow=False)
                    rec["reuse_check"] = "IDENTICAL" if (same_c and same_h) else "DIFFERS"
                    if same_c and same_h:
                        rec["reused"] = True
                        reused.append(tag)
                    else:
                        failures.append((tag, "config_same=%s hfd_same=%s" % (same_c, same_h)))
            else:
                built.append(tag)
            manifest.append(rec)

    print("\n%-10s %-9s %-7s %-6s %-8s %s" % ("rung", "kind", "KV", "scale", "cells", "status"))
    for rid, kind, kv, scale, prefix, reuse in RUNGS:
        rs = [m for m in manifest if m["rung"] == rid]
        st = ("REUSE %s" % rs[0].get("reuse_check")) if reuse else "NEW -> to run"
        print("%-10s %-9s %-7s %-6.2f %-8d %s" % (rid, kind, kv or "-", scale, len(rs), st))

    print("\nnew cells to run : %d  %s" % (len(built), sorted(set(t.rsplit('_', 1)[0] for t in built))))
    print("reused cells     : %d  %s" % (len(reused), sorted(set(t.rsplit('_', 1)[0] for t in reused))))

    if failures:
        print("\n" + "=" * 90)
        print("REUSE VERIFICATION FAILED -- section 2 says the rung is REBUILT AND RE-RUN, not excused")
        for t, why in failures:
            print("  %-16s %s" % (t, why))
        print("=" * 90)
        return 3

    seen = {}
    for m in manifest:
        seen.setdefault(m["rung"], set()).add(m["seed"])
    for rid, ss in seen.items():
        assert len(ss) == 6, "rung %s has duplicate seeds: %r" % (rid, sorted(ss))
    print("\nall 7 rungs carry 6 distinct seeds")

    json.dump({"prereg": "PREREG_3d_ladder_r169.md", "prereg_sha256": PREREG,
               "ta_base": TA_BASE, "seeds": SEEDS,
               "cells": manifest,
               "new_tags": sorted(built), "reused_tags": sorted(reused)},
              io.open(os.path.join(ROOT, "BUILD_MANIFEST.json"), "w", encoding="utf-8"), indent=1)
    print("build manifest written to %s" % os.path.join(ROOT, "BUILD_MANIFEST.json"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
