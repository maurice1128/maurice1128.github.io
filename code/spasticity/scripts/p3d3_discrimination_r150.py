# -*- coding: utf-8 -*-
"""P3D-3, per PREREG_3d_discrimination_r150.md
   sha256 52459560d75e1be97ee40f82dbb64e8e382b12201c03522170c983fd2de21845

Builds the two weakness arms (MODEL edit: tib_ant_l max_isometric_force only),
runs them, and measures all four arms on the registered endpoint set over ONE
common window, using MEAN PER-CYCLE ROM.

Thresholds are the registration's and are restated here only as constants.
Every clause is three-state; a quantity that cannot be measured never reaches a
verdict.
"""
import io, os, sys, math, json, shutil, subprocess

sys.path.insert(0, r"C:\Users\maurice\Desktop\spasticity_paper\scone")
import sto_utils as S

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

SCONE = r"C:\Program Files\SCONE\bin\sconecmd.exe"
BASE = r"C:\Users\maurice\Desktop\spasticity_paper\scone\probe3d_r141"
PAR = "230119.H1922v7b3.D20.par"
HFD = "H1922v7b3.hfd"
OUT = r"C:\Users\maurice\Desktop\spasticity_paper\paper\P3D3_RESULT_r150.json"

MIN_DUR, MIN_CYC, SETTLE = 9.73, 5, 1.0
UNI_RATIO = 0.33
TA_BASE = 1759.0

ARMS = [("A0_baseline", "bench_D20", None),
        ("A1_spastic_kv0.0125", "bench_D20_kv0p0125", None),
        ("A2_weak_par20", "bench_D20_par20", 0.80),
        ("A3_weak_par40", "bench_D20_par40", 0.60)]

PAIRED = ["ankle_angle", "hip_adduction", "hip_rotation"]
UNPAIRED = ["pelvis_list", "pelvis_rotation"]
EXTRA = ["knee_angle", "hip_flexion"]


def edit_tib_ant_l(path, scale):
    """Replace max_isometric_force ONLY inside the tib_ant_l block."""
    lines = io.open(path, encoding="utf-8", newline="").read().splitlines(True)
    i = next(k for k, ln in enumerate(lines) if ln.strip() == "name = tib_ant_l")
    j = next(k for k in range(i, len(lines)) if "max_isometric_force" in lines[k])
    old = lines[j]
    new_val = TA_BASE * scale
    lines[j] = old[:old.index("=") + 1] + (" %.1f\n" % new_val)
    io.open(path, "w", encoding="utf-8", newline="").write("".join(lines))
    return old.strip(), lines[j].strip(), new_val


def build(tag, scale):
    d = os.path.join(BASE, tag)
    if os.path.isdir(d):
        shutil.rmtree(d)
    shutil.copytree(os.path.join(BASE, "bench_D20"), d)
    for f in os.listdir(d):
        if f.endswith(".sto"):
            os.remove(os.path.join(d, f))
    o, n, v = edit_tib_ant_l(os.path.join(d, HFD), scale)
    print("  %s : %r -> %r" % (tag, o, n))
    # nothing else may have changed
    a = io.open(os.path.join(BASE, "bench_D20", HFD), encoding="utf-8").read().splitlines()
    b = io.open(os.path.join(d, HFD), encoding="utf-8").read().splitlines()
    diffs = [k for k in range(min(len(a), len(b))) if a[k] != b[k]]
    print("     model lines differing from baseline: %d %s" % (len(diffs), diffs))
    assert len(diffs) == 1, "more than the intended line changed"
    r = subprocess.run([SCONE, "-e", os.path.join(d, PAR)],
                       capture_output=True, text=True, timeout=1200)
    sto = os.path.join(d, PAR + ".sto")
    return d, (sto if os.path.exists(sto) else None), r.returncode


def rom(cols, dat, t, chan, t0, t1):
    v = S.col(cols, dat, chan)
    if v is None:
        return None, 0
    grf_side = chan[-1] if chan[-1] in ("l", "r") else "l"
    grf, thr = S.grf_vertical(cols, dat, grf_side)
    if grf is None:
        return None, 0
    idx = S.heel_strikes(t, grf, thresh=thr)
    cyc = []
    for k in range(len(idx) - 1):
        i0, i1 = idx[k], idx[k + 1]
        if t[i0] < t0 or t[i1] > t1:
            continue
        seg = v[i0:i1 + 1]
        if len(seg):
            cyc.append(math.degrees(max(seg) - min(seg)))
    if len(cyc) >= 2:
        cyc = cyc[:-1]
    return (sum(cyc) / len(cyc) if cyc else None), len(cyc)


def load(sto):
    cols, dat = S.load_sto(sto)
    return cols, dat, list(S.col(cols, dat, "time"))


print("=" * 78)
print("P3D-3  building the weakness arms (MODEL edit, tib_ant_l only)")
print("=" * 78)
runs = {}
for name, tag, scale in ARMS:
    if scale is None:
        d = os.path.join(BASE, tag)
        runs[name] = os.path.join(d, PAR + ".sto")
        print("  %s : existing" % name)
        continue
    d, sto, rc = build(tag, scale)
    runs[name] = sto
    print("     rc=%d sto=%s" % (rc, bool(sto)))

# ---- survival gate + common window -----------------------------------------
print()
print("=" * 78)
print("SURVIVAL GATE  (duration >= %.2f s AND >= %d cycles)" % (MIN_DUR, MIN_CYC))
print("=" * 78)
meta, admitted = {}, []
for name, _, _ in ARMS:
    sto = runs[name]
    if not sto:
        print("  %-22s UNEVALUABLE (no .sto)" % name)
        meta[name] = {"state": "UNEVALUABLE"}
        continue
    cols, dat, t = load(sto)
    dur = t[-1]
    grf, thr = S.grf_vertical(cols, dat, "l")
    ncyc = max(0, len(S.heel_strikes(t, grf, thresh=thr)) - 1)
    ok = dur >= MIN_DUR and ncyc >= MIN_CYC
    meta[name] = {"state": "PASS" if ok else "FAIL", "duration_s": dur, "cycles": ncyc}
    print("  %-22s dur %7.3f s  cycles %2d  -> %s" % (name, dur, ncyc, meta[name]["state"]))
    if ok:
        admitted.append(name)

T1 = min(meta[n]["duration_s"] for n in admitted)
print()
print("COMMON WINDOW across all admitted arms: [%.2f, %.4f]" % (SETTLE, T1))

# ---- the endpoint set -------------------------------------------------------
res = {}
for name in admitted:
    cols, dat, t = load(runs[name])
    row = {}
    for ch in PAIRED + EXTRA:
        for side in ("l", "r"):
            v, n = rom(cols, dat, t, ch + "_" + side, SETTLE, T1)
            row[ch + "_" + side] = v
    for ch in UNPAIRED:
        v, n = rom(cols, dat, t, ch, SETTLE, T1)
        row[ch] = v
    res[name] = row

print()
print("=" * 78)
print("ENDPOINT SET -- mean per-cycle ROM (deg), common window")
print("=" * 78)
chans = [c + "_" + s for c in PAIRED for s in ("l", "r")] + UNPAIRED
hdr = "%-22s" % "channel"
for name in admitted:
    hdr += "%16s" % name.split("_")[0]
print(hdr)
for ch in chans:
    line = "%-22s" % ch
    for name in admitted:
        v = res[name].get(ch)
        line += "%16s" % (("%.3f" % v) if v is not None else "n/a")
    print(line)

# ---- PREDICTION P: laterality ----------------------------------------------
print()
print("=" * 78)
print("PREDICTION P -- is each injection unilateral?  |dR|/|dL| <= %.2f on ankle ROM" % UNI_RATIO)
print("=" * 78)
b = res["A0_baseline"]
lat = {}
for name in admitted:
    if name == "A0_baseline":
        continue
    dl = res[name]["ankle_angle_l"] - b["ankle_angle_l"]
    dr = res[name]["ankle_angle_r"] - b["ankle_angle_r"]
    ratio = abs(dr) / abs(dl) if dl else None
    state = "UNEVALUABLE" if ratio is None else ("UNILATERAL" if ratio <= UNI_RATIO else "BILATERAL")
    lat[name] = {"dL": dl, "dR": dr, "ratio": ratio, "state": state}
    print("  %-22s dL %+7.3f  dR %+7.3f  |dR|/|dL| %s  -> %s"
          % (name, dl, dr, ("%.2f" % ratio) if ratio else "n/a", state))

# ---- SEPARATION criterion ---------------------------------------------------
print()
print("=" * 78)
print("SEPARATION -- |A1 - A2/A3| must exceed the BASELINE's own |L-R| on that channel")
print("=" * 78)
sep = {}
for ch in PAIRED:
    floor = abs(b[ch + "_l"] - b[ch + "_r"])
    for other in [n for n in admitted if n.startswith(("A2", "A3"))]:
        for side in ("l", "r"):
            k = ch + "_" + side
            d = abs(res["A1_spastic_kv0.0125"][k] - res[other][k])
            hit = d > floor
            sep["%s|%s" % (k, other)] = {"diff": d, "floor": floor, "separates": hit}
            print("  %-18s %-16s diff %7.3f  floor %7.3f  -> %s"
                  % (k, other.split("_")[0], d, floor, "SEPARATES" if hit else "no"))
for ch in UNPAIRED:
    floor = abs(b["ankle_angle_l"] - b["ankle_angle_r"])
    for other in [n for n in admitted if n.startswith(("A2", "A3"))]:
        d = abs(res["A1_spastic_kv0.0125"][ch] - res[other][ch])
        hit = d > floor
        sep["%s|%s" % (ch, other)] = {"diff": d, "floor": floor, "separates": hit,
                                      "note": "unpaired; floor is the ankle L-R proxy"}
        print("  %-18s %-16s diff %7.3f  floor %7.3f  -> %s"
              % (ch, other.split("_")[0], d, floor, "SEPARATES" if hit else "no"))

json.dump({"prereg_sha256": "52459560d75e1be97ee40f82dbb64e8e382b12201c03522170c983fd2de21845",
           "window": [SETTLE, T1], "survival": meta, "endpoints": res,
           "prediction_P_laterality": lat, "separation": sep},
          io.open(OUT, "w", encoding="utf-8"), indent=1)
print()
print("wrote", OUT)
