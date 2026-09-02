# -*- coding: utf-8 -*-
"""Round 234 -- measure the 2D between-seed SD. Implements PREREG_2Dsd_r234.md.

CONTROL CELLS ONLY: SG0_DR2K000, six cells, KV = 0.000, no lesion. No lesion arm is touched,
so this cannot contaminate the spastic-vs-weak comparison the main registration exists to
make.

REPLAY ONLY: sconecmd -e writes .sto and never .par. #205 discipline -- a replay may be
re-run only after a NON-RESULT; every attempt including failures goes to the ledger.
"""
import io
import os
import re
import sys
import glob
import json
import time
import math
import hashlib
import subprocess

sys.path.insert(0, r"C:\Users\maurice\Desktop\spasticity_paper\scone")
import numpy as np
import sto_utils as S

RESULTS = r"C:\Users\maurice\Documents\SCONE\results"
PAPER = r"C:\Users\maurice\Desktop\spasticity_paper\paper"
SCONECMD = r"C:\Program Files\SCONE\bin\sconecmd.exe"
PREREG = os.path.join(PAPER, "PREREG_2Dsd_r234.md")
LEDGER = os.path.join(PAPER, "BODY2_SD_LEDGER_r234.json")

FAMILY = "SG0_DR2K000"
SETTLE, T1 = 1.0, 8.00
MIN_CYCLES = 2
GRF_THRESH = 0.05
RAD2DEG = 180.0 / math.pi
PAR_RE = re.compile(r"^(\d+)_([\d.]+)_([\d.]+)\.par$")
SD_3D_POOLED, SD_3D_CENTRAL = 0.3644, 0.4729
DELTA_3D = 2.5854
DELTA_REG = 0.65
DELTA_CAP = 0.25 * DELTA_3D

PATH = "/jointset/%s_%s/%s_%s/value"


def _sha(p):
    return hashlib.sha256(io.open(p, "rb").read()).hexdigest()


def machine_sconecmd():
    try:
        out = subprocess.run(["tasklist", "/FI", "IMAGENAME eq sconecmd.exe", "/NH"],
                             capture_output=True, text=True, timeout=60).stdout
    except Exception:
        return 999
    return sum(1 for ln in out.splitlines() if "sconecmd" in ln.lower())


def cells():
    out = []
    for d in sorted(glob.glob(os.path.join(RESULTS, FAMILY + "_s*.H0914M.*"))):
        if not os.path.isdir(d):
            continue
        m = re.search(r"_s(\d+)\.", os.path.basename(d))
        if m:
            out.append((int(m.group(1)), d))
    return sorted(out)


def select_par(d):
    rows = []
    for f in os.listdir(d):
        m = PAR_RE.match(f)
        if m:
            rows.append((float(m.group(3)), int(m.group(1)), f))
    if not rows:
        return None, None
    best = min(r[0] for r in rows)
    tied = sorted([r for r in rows if r[0] == best], key=lambda r: -r[1])
    return os.path.join(d, tied[0][2]), {"field3": best, "n_tied": len(tied)}


def endpoint(sto):
    cols, dat = S.load_sto(sto)
    t = np.asarray(S.col(cols, dat, "time"), float)
    if t[-1] < T1:
        return None, "gate B: t_end %.2f < %.2f" % (t[-1], T1)
    grf, thr = S.grf_vertical(cols, dat, "l")
    idx = S.heel_strikes(t, grf, thresh=thr)
    cyc = [(idx[k], idx[k + 1]) for k in range(len(idx) - 1)
           if t[idx[k]] >= SETTLE and t[idx[k + 1]] <= T1]
    cyc = cyc[:-1] if len(cyc) >= 2 else cyc
    if len(cyc) < MIN_CYCLES:
        return None, "gate B: %d usable cycles" % len(cyc)
    a, b = cyc[0][0], cyc[-1][1]
    v = {}
    for side in ("l", "r"):
        w = PATH % ("hip", side, "hip_flexion", side)
        if w not in cols:
            return None, "missing column %s" % w
        v[side] = np.asarray(dat[:, cols.index(w)], float)[a:b]
    return {"value": float(np.mean(v["l"] - v["r"]) * RAD2DEG),
            "n_cycles": len(cyc), "t_end": float(t[-1])}, None


def chi2_sd_ci(sd, n, lo=0.025, hi=0.975):
    """chi-square CI for a normal SD. n = 6 -> df = 5."""
    from math import sqrt
    # df=5 chi-square quantiles at 0.025 / 0.975
    q_lo, q_hi = 0.8312, 12.8325
    df = n - 1
    return sd * sqrt(df / q_hi), sd * sqrt(df / q_lo)


def equiv_power(sigma, delta, n=16, nsim=400, b=600, seed=234234):
    """P(90% HL bootstrap CI inside +/-delta) under a true zero effect."""
    rng = np.random.default_rng(seed)
    ok = 0
    for _ in range(nsim):
        sv = rng.normal(0.0, sigma, n)
        wv = rng.normal(0.0, sigma, n)
        si = rng.integers(0, n, size=(b, n))
        wi = rng.integers(0, n, size=(b, n))
        d = wv[wi][:, None, :] - sv[si][:, :, None]
        stat = np.median(d.reshape(b, -1), axis=1)
        lo, hi = np.percentile(stat, 5), np.percentile(stat, 95)
        ok += (lo > -delta and hi < delta)
    return ok / float(nsim)


def main():
    n0 = machine_sconecmd()
    if n0:
        raise SystemExit("machine sconecmd = %d; our cells give way." % n0)

    ledger = []
    if os.path.exists(LEDGER):
        ledger = json.load(io.open(LEDGER, encoding="utf-8")).get("attempts", [])
    done = {(a["seed"], a["par"]) for a in ledger if a["outcome"] == "ok"}

    queue = []
    for seed, d in cells():
        par, meta = select_par(d)
        if par is None:
            ledger.append({"seed": seed, "par": None, "outcome": "no_conforming_par",
                           "ts": time.strftime("%Y-%m-%dT%H:%M:%S")})
            continue
        sto = par + ".sto"
        if os.path.exists(sto) and os.path.getsize(sto) > 0:
            continue                       # #205: never re-run a replay that produced a .sto
        queue.append((seed, d, par, meta))

    print("control cells: %d   to replay: %d" % (len(cells()), len(queue)))
    live = []
    for (seed, d, par, meta) in queue:
        while len([p for p in live if p.poll() is None]) >= 3 or machine_sconecmd() >= 4:
            time.sleep(0.2)
        live.append(subprocess.Popen([SCONECMD, "-e", os.path.basename(par)], cwd=d,
                                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL))
    for p in live:
        p.wait()

    rows, excluded = [], []
    for seed, d in cells():
        par, meta = select_par(d)
        sto = (par + ".sto") if par else None
        good = bool(sto and os.path.exists(sto) and os.path.getsize(sto) > 0)
        ledger.append({"seed": seed, "par": os.path.basename(par) if par else None,
                       "outcome": "ok" if good else "E5_STO_0",
                       "sto_bytes": os.path.getsize(sto) if good else 0,
                       "ts": time.strftime("%Y-%m-%dT%H:%M:%S")})
        if not good:
            excluded.append({"seed": seed, "why": "E5_STO_0"})
            continue
        r, why = endpoint(sto)
        if r is None:
            excluded.append({"seed": seed, "why": why})
        else:
            r["seed"] = seed
            r["field3"] = meta["field3"]
            rows.append(r)

    json.dump({"note": "#205: every attempt including failures", "attempts": ledger},
              io.open(LEDGER, "w", encoding="utf-8"), indent=1)

    res = {"round": 234, "scope": "CONTROL CELLS ONLY (%s); no lesion arm touched" % FAMILY,
           "window": [SETTLE, T1], "statistic": "cycle-averaged hip_flexion_LmR, degrees",
           "provenance": {"script": os.path.basename(__file__),
                          "script_sha256": _sha(os.path.abspath(__file__)),
                          "prereg_sha256": _sha(PREREG)},
           "per_cell": rows, "excluded": excluded,
           "n_cells": len(cells()), "n_admitted": len(rows), "n_excluded": len(excluded)}
    # CONSERVATION: a partition that does not sum is machinery announcing it did not fire.
    assert res["n_cells"] == res["n_admitted"] + res["n_excluded"], \
        "CONSERVATION VIOLATED: %d != %d + %d" % (res["n_cells"], res["n_admitted"],
                                                  res["n_excluded"])
    res["conservation_ok"] = True

    if len(rows) < 3:
        res["OUTCOME"] = "INSUFFICIENT"
        res["reason"] = "only %d admitted control cells" % len(rows)
    else:
        v = [r["value"] for r in rows]
        sd = float(np.std(v, ddof=1))
        lo, hi = chi2_sd_ci(sd, len(v))
        res["sigma_2D"] = sd
        res["sigma_2D_ci95"] = [lo, hi]
        res["ratio_to_3D_pooled"] = sd / SD_3D_POOLED
        res["ratio_to_3D_central"] = sd / SD_3D_CENTRAL
        res["values"] = v
        # recalibrate using the CI UPPER bound (registration section 3)
        tab = {}
        for lab, s in (("point", sd), ("ci_upper", hi)):
            tab[lab] = {"sigma": s,
                        "power_at_0.65": equiv_power(s, DELTA_REG),
                        "power_at_cap": equiv_power(s, DELTA_CAP)}
        res["recalibrated"] = tab
        res["delta_cap"] = DELTA_CAP
        p65 = tab["ci_upper"]["power_at_0.65"]
        pcap = tab["ci_upper"]["power_at_cap"]
        if p65 >= 0.80:
            res["OUTCOME"] = "POWER ADEQUATE"
            res["reason"] = "EQUIV power at delta=0.65 is %.3f using the CI upper bound" % p65
        elif pcap >= 0.80:
            need = None
            for dd in np.linspace(DELTA_REG, DELTA_CAP, 25):
                if equiv_power(hi, float(dd)) >= 0.80:
                    need = float(dd)
                    break
            res["OUTCOME"] = "DELTA RAISED"
            res["delta_new"] = need
            res["reason"] = ("power at 0.65 is %.3f; raised to delta = %.3f (<= 0.25 x "
                             "Delta_3D = %.3f)" % (p65, need or DELTA_CAP, DELTA_CAP))
        else:
            res["OUTCOME"] = "EQUIVALENCE UNREACHABLE"
            res["reason"] = ("power at 0.65 is %.3f and at the cap %.3f is %.3f; no delta "
                             "<= 0.25 x Delta_3D reaches 0.80. The EQUIV rung must be "
                             "DELETED." % (p65, DELTA_CAP, pcap))

    json.dump(res, io.open(os.path.join(PAPER, "BODY2_SD_r234.json"), "w",
                           encoding="utf-8"), indent=1)

    print("admitted %d / %d   excluded %s" % (len(rows), len(cells()), excluded))
    for r in rows:
        print("   s%-4d  hip_flexion_LmR %+8.4f deg   cycles %d" % (r["seed"], r["value"],
                                                                    r["n_cycles"]))
    if "sigma_2D" in res:
        print("\n  sigma_2D = %.4f deg   chi2 95%% CI [%.4f, %.4f]"
              % (res["sigma_2D"], *res["sigma_2D_ci95"]))
        print("  ratio to 3D pooled %.3f   to 3D central %.3f"
              % (res["ratio_to_3D_pooled"], res["ratio_to_3D_central"]))
        for lab, d in res["recalibrated"].items():
            print("  %-9s sigma %.4f  power@0.65 %.3f  power@cap(%.3f) %.3f"
                  % (lab, d["sigma"], d["power_at_0.65"], DELTA_CAP, d["power_at_cap"]))
    print("\nOUTCOME = %s\n  %s" % (res["OUTCOME"], res["reason"]))


if __name__ == "__main__":
    main()
