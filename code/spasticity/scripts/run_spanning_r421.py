# -*- coding: utf-8 -*-
"""r421: the single-muscle spanning test, warm-start chained.

Registered by paper/PREREG_spanning_r421.md, sha256 323568b2d8da15cf... hashed before any cell
in section 4 existed.

WHY THIS EXISTS. The mechanism line has been blocked all project because single-muscle spastic
cells do not survive. r407 injected KV 0.050 DIRECTLY and got gastroc-only 0/6 at every rung.
r410 froze the controller and every lesioned arm fell in 3-5 s. r420 pushed the frozen dose down
to 0.005 and still could not get both arms to 4/6. The one combination never tried is
SINGLE MUSCLE + LOW DOSE + WARM-START CHAINING, and chaining is what turned KV 0.070 from 0/6
into 6/6 in CHAIN_RESULT_r393.json.

Chain: the seed's unlesioned R151C optimum -> KV 0.0125 -> 0.025 -> 0.050, three arms.
The spastic MuscleReflex carries a LITERAL KV, so it adds no free parameter and a control .par
warm-starts a spastic config without a dimension mismatch -- this is how R151S was made from
R151C originally.

Safety: reuses run_chain_r393's proven machinery unchanged -- wpath() refuses any write outside
spasticity_paper, competing() yields to foreign sconecmd, and the PROTECTED pattern guards the
112 runs. Nothing here writes to the SCONE results directory except SCONE itself creating our
own R421* result directories.
"""
import argparse
import glob
import io
import json
import os
import re
import shutil
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import run_chain_r393 as C  # noqa: E402  -- imported for its verified helpers

ROOT = C.ROOT
STAGE = os.path.join(ROOT, "chain_r421")
PAPER = C.PAPER
SRC_S = C.SRC_S                      # spastic template: BOTH reflexes, KV 0.050
GENS = C.GENS
SEEDS = C.SEEDS

RUNGS = [("0125", 0.0125), ("0250", 0.025), ("0500", 0.050)]
ARMS = {"GASONLY": ("gastroc",), "SOLONLY": ("soleus",), "BOTH": ("soleus", "gastroc")}
CTRL_ROOT = "R151C"

# one MuscleReflex block inside the SpasticL controller
BLOCK = (r"\s*MuscleReflex\s*\{\s*target\s*=\s*%s\s+delay\s*=\s*0\.020\s+"
         r"KV\s*=\s*[0-9.]+\s+allow_neg_V\s*=\s*0\s*\}")


def cells():
    out = []
    for arm in ("GASONLY", "SOLONLY", "BOTH"):
        for k, (tag, kv) in enumerate(RUNGS):
            for s in SEEDS:
                out.append({
                    "arm": arm, "rung": tag, "rung_index": k, "value": kv, "seed": s,
                    "prefix": "R421%s%s_s%d" % (arm, tag, s),
                    "parent_prefix": ("%s_s%d" % (CTRL_ROOT, s) if k == 0
                                      else "R421%s%s_s%d" % (arm, RUNGS[k - 1][0], s)),
                    "parent_is_root": k == 0})
    return out


def cell_index(prefix):
    for i, c in enumerate(cells()):
        if c["prefix"] == prefix:
            return i
    return None


def make_dirs(c):
    """SRC_S keeps the .hfd and .zml FLAT, but config.scone refers to models/ and data/.
    The staged cell therefore has to re-nest them, the same shape chain_r393 cells have."""
    d = os.path.join(STAGE, c["prefix"])
    for sub in ("par", "models", "data"):
        os.makedirs(C.wpath(os.path.join(d, sub)), exist_ok=True)
    for src, sub in ((os.path.join(SRC_S, "H1922v7b3.hfd"), "models"),
                     (os.path.join(SRC_S, "InitStateH0918Gait10ActA.zml"), "data")):
        assert os.path.exists(src), "template file missing: " + src
        dst = os.path.join(d, sub, os.path.basename(src))
        if not os.path.exists(dst) or C.sha(dst) != C.sha(src):
            shutil.copyfile(src, C.wpath(dst))
    return d


def spastic_config(keep, kv):
    """SRC_S config with the unwanted MuscleReflex removed and KV set on those that remain."""
    cfg = io.open(os.path.join(SRC_S, "config.scone"), encoding="utf-8").read()
    i = cfg.index("name = SpasticL")
    head, blk = cfg[:i], cfg[i:]
    for muscle in ("soleus", "gastroc"):
        if muscle in keep:
            continue
        blk, n = re.subn(BLOCK % muscle, "", blk, count=1)
        assert n == 1, "could not remove the %s MuscleReflex" % muscle
    for muscle in keep:
        blk, n = re.subn(r"(target\s*=\s*%s\s+delay\s*=\s*0\.020\s+KV\s*=\s*)[0-9.]+" % muscle,
                         r"\g<1>%.4f" % kv, blk, count=1)
        assert n == 1, "could not set KV on %s" % muscle
    return head + blk


def prepare(c):
    d = make_dirs(c)
    rec = {k: c[k] for k in ("prefix", "arm", "rung", "value", "seed", "parent_prefix",
                             "parent_is_root")}
    pev = C.evaluate(c["parent_prefix"])
    if pev.get("status") != "OK":
        rec.update(status="PARENT_NOT_RUN", parent_status=pev.get("status"))
        return rec
    rec.update(parent_result_dir=pev["result_dir"], parent_gate_G=pev["gate_G"],
               parent_t_end_s=pev["t_end_s"], parent_n_cycles=pev["n_cycles_in_window"])
    if not pev["gate_G"]:
        rec.update(status="BROKEN_PARENT_FAILED_GATE",
                   broken_reason="parent %s failed Gate G; no substitute parent is used and this "
                                 "seed's chain on this arm is BROKEN" % c["parent_prefix"])
        return rec

    psrc = os.path.join(C.RES, pev["result_dir"], pev["resolved_par"])
    warm = "WARM_%s_g%04d.par" % (c["parent_prefix"], pev["resolved_par_generation"])
    for old in glob.glob(os.path.join(d, "par", "WARM_*.par")):
        if os.path.basename(old) != warm:
            os.remove(C.wpath(old))
    shutil.copyfile(psrc, C.wpath(os.path.join(d, "par", warm)))
    assert C.sha(os.path.join(d, "par", warm)) == pev["resolved_par_sha256"], "warm copy differs"
    rec.update(parent_par=pev["resolved_par"], parent_par_sha256=pev["resolved_par_sha256"],
               parent_par_generation=pev["resolved_par_generation"], staged_warm_as=warm)

    keep = ARMS[c["arm"]]
    cfg = spastic_config(keep, c["value"])
    for pat, rep, n_want in (
            (r"max_generations\s*=\s*\d+", "max_generations = %d" % GENS, 1),
            (r'init\s*\{\s*file\s*=\s*"[^"]*"\s*\}', 'init { file = "par/%s" }' % warm, 1),
            (r"random_seed\s*=\s*\d+", "random_seed = %d" % c["seed"], 1),
            (r"signature_prefix\s*=\s*\S+", "signature_prefix = %s" % c["prefix"], 1)):
        cfg, n = re.subn(pat, rep, cfg, count=1)
        assert n == n_want, "substitution failed: %s" % pat
    C.wopen(os.path.join(d, "config.scone")).write(cfg)

    # ---- read back off disk and assert every intended field -------------------------------
    back = io.open(os.path.join(d, "config.scone"), encoding="utf-8").read()
    i = back.index("name = SpasticL")
    blk = back[i:i + 900]
    for muscle in ("soleus", "gastroc"):
        present = bool(re.search(r"target\s*=\s*%s\s+delay\s*=\s*0\.020" % muscle, blk))
        assert present == (muscle in keep), \
            "%s: %s reflex present=%s but keep=%s" % (c["prefix"], muscle, present, keep)
    got = re.findall(r"KV\s*=\s*([0-9.]+)\s+allow_neg_V", blk)
    assert len(got) == len(keep) and all(abs(float(g) - c["value"]) < 1e-9 for g in got), \
        "%s: spastic KV readback %s, wanted %d x %.4f" % (c["prefix"], got, len(keep), c["value"])
    assert re.search(r"max_generations\s*=\s*%d\b" % GENS, back)
    assert re.search(r"random_seed\s*=\s*%d\b" % c["seed"], back)
    assert re.search(r"signature_prefix\s*=\s*%s\b" % c["prefix"], back)
    assert re.search(r"min_velocity\s*=\s*1\.0\b", back), "min_velocity 1.0 missing"
    m = re.search(r'init\s*\{\s*file\s*=\s*"([^"]*)"\s*\}', back)
    assert m and m.group(1) == "par/" + warm
    assert os.path.exists(os.path.join(d, "par", warm))

    # no weakness anywhere: all three max_isometric_force at base
    chk = io.open(os.path.join(d, "models", "H1922v7b3.hfd"), encoding="utf-8").read()
    fm = {mm: float(re.search(r"name\s*=\s*" + mm + r"\b.*?max_isometric_force\s*=\s*([0-9.]+)",
                              chk, re.S).group(1)) for mm in C.FMAX_BASE}
    assert all(abs(fm[k] - v) < 1e-6 for k, v in C.FMAX_BASE.items()), fm
    rec.update(fmax_readback=fm, spastic_targets=list(keep),
               config_sha256=C.sha(os.path.join(d, "config.scone")),
               init_line_readback=m.group(0), status="PREPARED")
    return rec


def yield_to_foreign():
    """Our cells give way on resource conflict; the 112 protected runs never do.

    Three of OUR workers are alive by design, so a raw process count cannot identify a foreign
    run. R421_FLEET says how many are ours; anything above that is someone else's and we wait.
    """
    fleet = int(os.environ.get("R421_FLEET", "3"))
    waited = 0
    while True:
        n = C.competing()
        if n < 0 or n <= fleet:
            return waited
        time.sleep(60)
        waited += 60
        if waited % 600 == 0:
            print("   yielding to %d sconecmd (fleet %d), waited %ds" % (n, fleet, waited))
            sys.stdout.flush()


def run_cell(i):
    c = cells()[i]
    yield_to_foreign()
    rec = prepare(c)
    if rec["status"] != "PREPARED":
        return rec
    d = os.path.join(STAGE, c["prefix"])
    t0 = time.time()
    r = C.subprocess.run([C.SCONE, "-o", "config.scone", "--quiet"], cwd=d,
                         capture_output=True, text=True, timeout=7200)
    rec["seconds"] = round(time.time() - t0, 1)
    ev = C.evaluate(c["prefix"])
    rec.update({k: ev.get(k) for k in ("status", "result_dir", "gate_G", "t_end_s",
                                       "n_cycles_in_window", "knee_hs_deg", "resolved_par")})
    rec["run_status"] = rec.pop("status", None)
    rec["status"] = "RUN_OK" if ev.get("status") == "OK" else ("RUN_%s" % ev.get("status"))
    rec["scone_tail"] = ((r.stdout or "") + (r.stderr or "")).strip().splitlines()[-3:]
    C.wopen(os.path.join(PAPER, "RUN_SPANNING_r421_%s.json" % c["prefix"])).write(
        json.dumps(rec, indent=1, ensure_ascii=False))
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--cell", type=int)
    ap.add_argument("--range", type=str, help="i:j, run cells i..j-1 in this process")
    a = ap.parse_args()
    cs = cells()
    if a.list:
        for i, c in enumerate(cs):
            print("%3d  %-24s parent %-22s KV %.4f" %
                  (i, c["prefix"], c["parent_prefix"], c["value"]))
        print("total %d cells" % len(cs))
        return
    if a.cell is not None:
        print(json.dumps({k: v for k, v in run_cell(a.cell).items() if k != "scone_tail"},
                         indent=1, ensure_ascii=False))
        return
    if a.range:
        i, j = (int(x) for x in a.range.split(":"))
        for k in range(i, min(j, len(cs))):
            r = run_cell(k)
            print("%3d  %-24s %-28s gate_G=%s t_end=%s knee=%s" %
                  (k, cs[k]["prefix"], r.get("status"), r.get("gate_G"), r.get("t_end_s"),
                   ("%.4f" % r["knee_hs_deg"]) if r.get("knee_hs_deg") is not None else "-"))
            sys.stdout.flush()
        return
    ap.print_help()


if __name__ == "__main__":
    main()
