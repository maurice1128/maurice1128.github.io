# -*- coding: utf-8 -*-
"""r426: rescue the x0.60 weakness root by inserting an x0.70 intermediate.

WHY. PREREG_mixed_r424.md names R393WK060 as the x0.60 row root. A Gate-G audit run AFTER that
registration was hashed found it passes only 3/6, below this corpus's own 4-cell bar, which makes
the r424 x0.60 row -- and therefore registered prediction P3 -- unjudgeable.

That 3/6 is not necessarily the lesion's fault. r393 built the weakness ladder by stepping x0.80
-> x0.60 in ONE jump. Warm-start chaining works by small steps: CHAIN_RESULT_r393.json turned KV
0.070 from 0/6 into 6/6 by exactly this means. This round inserts x0.70 between them.

THIS IS A ROOT REPAIR, NOT AN AMENDMENT TO r424. No r424 endpoint, threshold or prediction is
changed, and no r424 value has been read. If the repair succeeds the x0.60 row is re-run from the
repaired root; if it fails, r424's P3 is reported UNINFORMATIVE with this attempt on the record.

Reuses run_chain_r393's verified machinery unchanged.
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
import run_chain_r393 as C  # noqa: E402

STAGE = os.path.join(C.ROOT, "rescue_r426")
GENS = C.GENS
SEEDS = C.SEEDS
# (tag, tib_ant scale, parent prefix template)
LADDER = [("070", 0.70, "R151W_s%d"), ("060", 0.60, "R426WK070_s%d")]


def cells():
    return [{"tag": t, "scale": sc, "seed": s,
             "prefix": "R426WK%s_s%d" % (t, s), "parent_prefix": par % s}
            for t, sc, par in LADDER for s in SEEDS]


def prepare(c):
    d = os.path.join(STAGE, c["prefix"])
    for sub in ("par", "models", "data"):
        os.makedirs(C.wpath(os.path.join(d, sub)), exist_ok=True)
    shutil.copyfile(os.path.join(C.SRC_W, "InitStateH0918Gait10ActA.zml"),
                    C.wpath(os.path.join(d, "data", "InitStateH0918Gait10ActA.zml")))
    # write_hfd scales from FMAX_BASE (1759), NOT from the source file's current value, so the
    # scale is passed absolute even though SRC_W already carries x0.80.
    C.write_hfd(os.path.join(C.SRC_W, "H1922v7b3.hfd"),
                C.wpath(os.path.join(d, "models", "H1922v7b3.hfd")), c["scale"])

    rec = {k: c[k] for k in ("prefix", "tag", "scale", "seed", "parent_prefix")}
    pev = C.evaluate(c["parent_prefix"])
    if pev.get("status") != "OK":
        rec.update(status="PARENT_NOT_RUN", parent_status=pev.get("status"))
        return rec
    rec.update(parent_gate_G=pev["gate_G"], parent_t_end_s=pev["t_end_s"])
    if not pev["gate_G"]:
        rec.update(status="BROKEN_PARENT_FAILED_GATE")
        return rec

    psrc = os.path.join(C.RES, pev["result_dir"], pev["resolved_par"])
    warm = "WARM_%s_g%04d.par" % (c["parent_prefix"], pev["resolved_par_generation"])
    for old in glob.glob(os.path.join(d, "par", "WARM_*.par")):
        if os.path.basename(old) != warm:
            os.remove(C.wpath(old))
    shutil.copyfile(psrc, C.wpath(os.path.join(d, "par", warm)))
    assert C.sha(os.path.join(d, "par", warm)) == pev["resolved_par_sha256"]
    rec.update(parent_par=pev["resolved_par"], staged_warm_as=warm,
               parent_par_generation=pev["resolved_par_generation"])

    cfg = io.open(os.path.join(C.SRC_W, "config.scone"), encoding="utf-8").read()
    assert not re.search(r"KV\s*=\s*0\.0[0-9]+\s*$", cfg, re.M), "weakness template carries a KV"
    for pat, rep in ((r"max_generations\s*=\s*\d+", "max_generations = %d" % GENS),
                     (r'init\s*\{\s*file\s*=\s*"[^"]*"\s*\}', 'init { file = "par/%s" }' % warm),
                     (r"random_seed\s*=\s*\d+", "random_seed = %d" % c["seed"]),
                     (r"signature_prefix\s*=\s*\S+", "signature_prefix = %s" % c["prefix"])):
        cfg, n = re.subn(pat, rep, cfg, count=1)
        assert n == 1, "substitution failed: %s" % pat
    C.wopen(os.path.join(d, "config.scone")).write(cfg)

    back = io.open(os.path.join(d, "config.scone"), encoding="utf-8").read()
    assert re.search(r"signature_prefix\s*=\s*%s\b" % c["prefix"], back)
    assert re.search(r"random_seed\s*=\s*%d\b" % c["seed"], back)
    assert re.search(r"min_velocity\s*=\s*1\.0\b", back)
    chk = io.open(os.path.join(d, "models", "H1922v7b3.hfd"), encoding="utf-8").read()
    fm = {mm: float(re.search(r"name\s*=\s*" + mm + r"\b.*?max_isometric_force\s*=\s*([0-9.]+)",
                              chk, re.S).group(1)) for mm in C.FMAX_BASE}
    assert abs(fm["soleus_l"] - 3549.0) < 1e-6 and abs(fm["gastroc_l"] - 2241.0) < 1e-6, fm
    assert abs(fm["tib_ant_l"] - 1759.0 * c["scale"]) < 1e-6, fm
    rec.update(fmax_readback=fm, status="PREPARED")
    return rec


def run_cell(i):
    c = cells()[i]
    fleet = int(os.environ.get("R426_FLEET", "3"))
    while True:
        n = C.competing()
        if n < 0 or n <= fleet:
            break
        time.sleep(60)
    rec = prepare(c)
    if rec["status"] != "PREPARED":
        return rec
    d = os.path.join(STAGE, c["prefix"])
    t0 = time.time()
    C.subprocess.run([C.SCONE, "-o", "config.scone", "--quiet"], cwd=d,
                     capture_output=True, text=True, timeout=7200)
    rec["seconds"] = round(time.time() - t0, 1)
    ev = C.evaluate(c["prefix"])
    for k in ("result_dir", "gate_G", "t_end_s", "n_cycles_in_window", "knee_hs_deg"):
        rec[k] = ev.get(k)
    rec["status"] = "RUN_OK" if ev.get("status") == "OK" else ("RUN_%s" % ev.get("status"))
    C.wopen(os.path.join(C.PAPER, "RUN_RESCUE_r426_%s.json" % c["prefix"])).write(
        json.dumps(rec, indent=1, ensure_ascii=False))
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--range", type=str, default="0:12")
    a = ap.parse_args()
    i, j = (int(x) for x in a.range.split(":"))
    cs = cells()
    for k in range(i, min(j, len(cs))):
        r = run_cell(k)
        print("%3d  %-18s x%.2f  %-26s gate_G=%s t_end=%s"
              % (k, cs[k]["prefix"], cs[k]["scale"], r.get("status"), r.get("gate_G"),
                 r.get("t_end_s")))
        sys.stdout.flush()


if __name__ == "__main__":
    main()
