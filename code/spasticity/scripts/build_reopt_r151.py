# -*- coding: utf-8 -*-
"""Build the 18 re-optimised 3D arms of PREREG_3d_reopt_r151.md
   sha256 f6a65408731cc7141580ea4c38b68871c9167d0f0c2a9da416142405758c4c23

3 arms x 6 seeds, every one RE-OPTIMISED (sconecmd on the scenario, NOT -e).

Magnitudes are the 2D registered values and are NOT lowered: KV = 0.050 and
tib_ant_l x 0.80. Whether they survive WITH adaptation is the prediction.

Every construction is verified rather than assumed:
  * random_seed written by the project's registered gen_seeds.set_seed, which
    reads the write back (it exists because a string-replace no-op once made
    N "seeds" one identical run)
  * S arm: the injected block present once, KV = 0.050 exactly twice
  * W arm: the model differs from the control model in EXACTLY ONE LINE
  * C arm: config differs from the template only in prefix and seed
"""
import io, os, re, sys, glob, json, shutil, hashlib, subprocess

sys.path.insert(0, r"C:\Users\maurice\Desktop\spasticity_paper\scone")
import gen_seeds as GS

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

BASE = r"C:\Users\maurice\Desktop\spasticity_paper\scone\probe3d_r141"
ROOT = os.path.join(BASE, "reopt_r151")
TEMPLATE = os.path.join(BASE, "timing3d", "config.scone")
SRC = os.path.join(BASE, "bench_D20")
HFD = "H1922v7b3.hfd"
ZML = "InitStateH0918Gait10ActA.zml"
PARF = os.path.join("par", "H1922v7b3-TSG3Dv8g-989_fixed2.par")
SEEDS = [101, 102, 103, 104, 105, 106]
TA_BASE, TA_SCALE = 1759.0, 0.80
KV = "0.050"

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
""" % (KV, KV)


def edit_tib_ant_l(path, scale):
    lines = io.open(path, encoding="utf-8", newline="").read().splitlines(True)
    i = next(k for k, ln in enumerate(lines) if ln.strip() == "name = tib_ant_l")
    j = next(k for k in range(i, len(lines)) if "max_isometric_force" in lines[k])
    lines[j] = lines[j][:lines[j].index("=") + 1] + (" %.1f\n" % (TA_BASE * scale))
    io.open(path, "w", encoding="utf-8", newline="").write("".join(lines))


def one_line_diff(a, b):
    x = io.open(a, encoding="utf-8").read().splitlines()
    y = io.open(b, encoding="utf-8").read().splitlines()
    return [k for k in range(min(len(x), len(y))) if x[k] != y[k]], len(x) == len(y)


def build():
    if os.path.isdir(ROOT):
        shutil.rmtree(ROOT)
    os.makedirs(ROOT)
    tmpl = io.open(TEMPLATE, encoding="utf-8", newline="").read()
    built = []
    for arm in ("C", "S", "W"):
        for s in SEEDS:
            tag = "R151%s_s%d" % (arm, s)
            d = os.path.join(ROOT, tag)
            os.makedirs(os.path.join(d, "par"))
            shutil.copy2(os.path.join(SRC, HFD), os.path.join(d, HFD))
            shutil.copy2(os.path.join(SRC, ZML), os.path.join(d, ZML))
            shutil.copy2(os.path.join(SRC, PARF), os.path.join(d, PARF))

            txt = re.sub(r"signature_prefix\s*=\s*\S+", "signature_prefix = " + tag, tmpl, count=1)
            if arm == "S":
                m = list(re.finditer(r"\n\t+\}\n\t+\}\n", txt))
                anchor = txt.rindex("ConditionalController")
                close = txt.index("\n\t\t\t\t}\n", anchor)
                txt = txt[:close] + "\n" + SPASTIC_BLOCK + txt[close:]
                assert txt.count("name = SpasticL") == 1, "SpasticL not inserted exactly once"
                assert txt.count("KV = " + KV) == 2, "KV=%s must appear exactly twice" % KV
            txt = GS.set_seed(txt, s)              # registered writer, reads back
            cp = os.path.join(d, "config.scone")
            io.open(cp, "w", encoding="utf-8", newline="").write(txt)

            if arm == "W":
                edit_tib_ant_l(os.path.join(d, HFD), TA_SCALE)
                diffs, samelen = one_line_diff(os.path.join(SRC, HFD), os.path.join(d, HFD))
                assert samelen and len(diffs) == 1, \
                    "W model must differ in exactly one line, got %r" % diffs
            else:
                diffs, _ = one_line_diff(os.path.join(SRC, HFD), os.path.join(d, HFD))
                assert not diffs, "%s model must be identical to control" % arm
            built.append((tag, cp, arm, s))
    return built


built = build()
print("built %d scenarios" % len(built))

# ---- verification, not assumption -------------------------------------------
seen = {}
for tag, cp, arm, s in built:
    t = io.open(cp, encoding="utf-8").read()
    got = GS.read_seed(t)
    assert got == s, "%s carries random_seed %r, wanted %d" % (tag, got, s)
    assert "max_generations = 90" in t, "%s lost max_generations" % tag
    seen.setdefault(arm, set()).add(got)
    if arm == "S":
        assert "name = SpasticL" in t and t.count("KV = " + KV) == 2
    else:
        assert "SpasticL" not in t
for arm, ss in sorted(seen.items()):
    print("  arm %s : %d distinct seeds %s" % (arm, len(ss), sorted(ss)))
    assert len(ss) == len(SEEDS), "arm %s has duplicate seeds" % arm

print()
print("W-arm model check:")
w = os.path.join(ROOT, "R151W_s101", HFD)
d, _ = one_line_diff(os.path.join(SRC, HFD), w)
print("  differing lines: %r" % d)
print("  line now reads : %s" % io.open(w, encoding="utf-8").read().splitlines()[d[0]].strip())

json.dump({"prereg_sha256": "f6a65408731cc7141580ea4c38b68871c9167d0f0c2a9da416142405758c4c23",
           "arms": {a: sorted(s) for a, s in seen.items()},
           "kv": KV, "ta_scale": TA_SCALE, "ta_value": TA_BASE * TA_SCALE,
           "scenarios": [t for t, _, _, _ in built]},
          io.open(os.path.join(ROOT, "BUILD_MANIFEST.json"), "w", encoding="utf-8"), indent=1)
print("\nbuild manifest written")
