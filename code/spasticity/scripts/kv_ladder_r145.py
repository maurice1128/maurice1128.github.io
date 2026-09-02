# -*- coding: utf-8 -*-
"""P3D-2 KV titration ladder, per PREREG_3d_injection_r145.md (sha256 d7ce407e...).

Thresholds are NOT in this script's gift -- they are read from the registration and
restated here only as constants. Changing them here would not change them.

  SURVIVES   <=> duration >= 9.73 s (80% of baseline 12.16 s) AND >= 5 GRF cycles
                 after settle = 1.0 s
  UNILATERAL <=> for BOTH soleus mean activation and ankle ROM,
                 |dL| = |m_L(inj) - m_L(base)|, |dR| = |m_R(inj) - m_R(base)|,
                 dR/dL <= 0.33, measured over a COMMON window
                 [1.0 s, min(duration_inj, duration_base)]

Only the two `KV = 0.050` values inside the SpasticL block change per rung.
Every clause is THREE-STATE: PASS / FAIL / UNEVALUABLE. A quantity that cannot be
measured never reaches a verdict (round 140's defect, repaired).
"""
import io, os, re, shutil, subprocess, sys, json, math

SCONE = r"C:\Program Files\SCONE\bin\sconecmd.exe"
BASE = r"C:\Users\maurice\Desktop\spasticity_paper\scone\probe3d_r141"
SRC = os.path.join(BASE, "bench_D20_spasL")
REF = os.path.join(BASE, "bench_D20")
PAR = "230119.H1922v7b3.D20.par"
OUT = r"C:\Users\maurice\Desktop\spasticity_paper\paper\P3D2_LADDER_r145.json"

LADDER = ["0.025", "0.0125", "0.00625", "0.003125"]
MIN_DUR = 9.73
MIN_CYC = 5
RATIO = 0.33
SETTLE = 1.0

PASS, FAIL, UNEVAL = "PASS", "FAIL", "UNEVALUABLE"


def clause(measured, test):
    if measured is None:
        return UNEVAL
    return PASS if test(measured) else FAIL


def load_sto(p):
    cols, rows = None, []
    with io.open(p, encoding="utf-8", errors="replace") as f:
        hdr = True
        for ln in f:
            if hdr:
                if ln.strip().lower() == "endheader":
                    hdr = False
                continue
            if cols is None:
                cols = ln.split()
                continue
            s = ln.split()
            if s:
                rows.append([float(x) for x in s])
    return cols, rows


def col(cols, rows, name):
    if name not in cols:
        return None
    i = cols.index(name)
    return [r[i] for r in rows]


def find_col(cols, *frags):
    for c in cols:
        lc = c.lower()
        if all(f in lc for f in frags):
            return c
    return None


def cycles(cols, rows, t0, t1):
    """GRF-delimited heel strikes on the left, within [t0, t1]."""
    t = col(cols, rows, "time")
    gname = find_col(cols, "grf", "_y") or find_col(cols, "leg0", "grf") or find_col(cols, "grf")
    if gname is None or t is None:
        return None
    g = col(cols, rows, gname)
    hs, prev = [], 0.0
    for i in range(len(t)):
        if t[i] < t0 or t[i] > t1:
            prev = g[i]
            continue
        if prev <= 0.05 < g[i]:
            hs.append(t[i])
        prev = g[i]
    return max(0, len(hs) - 1)


def metrics(path, t0, t1):
    cols, rows = load_sto(path)
    t = col(cols, rows, "time")
    if t is None:
        return None
    idx = [i for i in range(len(t)) if t0 <= t[i] <= t1]
    if not idx:
        return None
    out = {}
    for side in ("l", "r"):
        a = find_col(cols, "soleus_" + side, "activation")
        out["sol_" + side] = (sum(col(cols, rows, a)[i] for i in idx) / len(idx)) if a else None
        # SCONE .sto stores joint angles in RADIANS. Converted here; an earlier
        # revision of this script labelled the raw value "deg" and understated
        # every ankle delta by 57x.
        k = "ankle_angle_" + side
        if k in cols:
            v = [col(cols, rows, k)[i] for i in idx]
            out["rom_" + side] = math.degrees(max(v) - min(v))
        else:
            out["rom_" + side] = None
    out["dur"] = t[-1]
    out["cols"] = cols
    out["rows"] = rows
    return out


def run_rung(kv):
    tag = "kv" + kv.replace(".", "p")
    d = os.path.join(BASE, "bench_D20_" + tag)
    if os.path.isdir(d):
        shutil.rmtree(d)
    shutil.copytree(SRC, d)
    for f in os.listdir(d):
        if f.endswith(".sto"):
            os.remove(os.path.join(d, f))
    cp = os.path.join(d, "config.scone")
    t = io.open(cp, encoding="utf-8", newline="").read()
    n = t.count("KV = 0.050")
    if n != 2:
        raise SystemExit("ABORT: expected 2 occurrences of 'KV = 0.050', found %d" % n)
    io.open(cp, "w", encoding="utf-8", newline="").write(t.replace("KV = 0.050", "KV = " + kv))
    print("  rung KV=%-9s dir=%s" % (kv, os.path.basename(d)))
    r = subprocess.run([SCONE, "-e", os.path.join(d, PAR)],
                       capture_output=True, text=True, timeout=900)
    sto = os.path.join(d, PAR + ".sto")
    return d, (sto if os.path.exists(sto) else None), r.returncode


def main():
    base = metrics(os.path.join(REF, PAR + ".sto"), SETTLE, 1e9)
    print("baseline duration %.4f s" % base["dur"])

    results = []
    landed = None
    for kv in LADDER:
        d, sto, rc = run_rung(kv)
        if sto is None:
            results.append({"kv": kv, "verdict": UNEVAL, "why": "no .sto produced", "rc": rc})
            print("    -> UNEVALUABLE (no .sto, rc=%d)" % rc)
            continue
        inj = metrics(sto, SETTLE, 1e9)
        dur = inj["dur"] if inj else None
        t1 = min(dur, base["dur"]) if dur else None
        ncyc = cycles(inj["cols"], inj["rows"], SETTLE, t1) if inj else None

        c1 = clause(dur, lambda v: v >= MIN_DUR)
        c2 = clause(ncyc, lambda v: v >= MIN_CYC)
        survives = (c1 == PASS and c2 == PASS)

        # unilaterality on the COMMON window
        uni, det = None, {}
        if survives:
            bw = metrics(os.path.join(REF, PAR + ".sto"), SETTLE, t1)
            iw = metrics(sto, SETTLE, t1)
            ok = True
            for m in ("sol", "rom"):
                bl, br = bw.get(m + "_l"), bw.get(m + "_r")
                il, ir = iw.get(m + "_l"), iw.get(m + "_r")
                if None in (bl, br, il, ir):
                    det[m] = {"state": UNEVAL}
                    ok = None
                    continue
                dl, dr = abs(il - bl), abs(ir - br)
                ratio = (dr / dl) if dl else None
                det[m] = {"dL": dl, "dR": dr, "ratio": ratio,
                          "state": clause(ratio, lambda v: v <= RATIO)}
                if det[m]["state"] != PASS:
                    ok = False if ok is not None else None
            uni = ok
        rec = {"kv": kv, "duration_s": dur, "cycles": ncyc,
               "clause1_duration": c1, "clause2_cycles": c2,
               "survives": survives, "unilateral": uni, "detail": det, "rc": rc}
        results.append(rec)
        print("    dur=%s cyc=%s  c1=%s c2=%s  SURVIVES=%s  UNILATERAL=%s"
              % (("%.3f" % dur) if dur else "n/a", ncyc, c1, c2, survives, uni))
        if survives and uni is True:
            landed = kv
            break

    json.dump({"what": "P3D-2 KV ladder, PREREG_3d_injection_r145.md",
               "thresholds": {"min_duration_s": MIN_DUR, "min_cycles": MIN_CYC,
                              "ratio_max": RATIO, "settle": SETTLE},
               "baseline_duration_s": base["dur"],
               "kv_0.050_prior": {"duration_s": 3.87, "note": "contaminated by fall, not re-run"},
               "rungs": results, "landed_kv": landed},
              io.open(OUT, "w", encoding="utf-8"), indent=1)
    print("\nwrote", OUT)
    print("LANDED:", landed if landed else "NO RUNG both survived and was unilateral")


if __name__ == "__main__":
    main()
