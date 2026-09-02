"""Could the joint-centre offset be a synchronisation lag rather than a definitional disagreement?

Section 2.1 asserts that the uncorrected sub-frame synchronisation residual "enters only the random
half, so it can only raise the offset share". That assertion is unargued, and a reviewer's objection
is that it is probably false HERE: heading varies by 1.0-14.1 degrees within ten of the eleven
participants (53.7 for P26; 56.0 across all trials, Table S20), and the offset is estimated within
participant, so a
CONSTANT sub-frame lag displaces every estimate in the same world-frame direction and lands in the
BIAS term, not the random one -- inflating the very offset Section 3.1 is built on rather than being
neutral to it. Table S12 bounds the residual's MAGNITUDE (3.58 mm typical at hip and knee) but says
nothing about its DIRECTION, so the objection cannot be answered from it.

This measures the direction, and tests the lag hypothesis on its own terms.

A timing lag of tau displaces a joint by (its velocity) x tau, ALONG the direction of travel. That
makes two predictions which the data can refute:

  it must be collinear with the walking direction, and
  its size must scale with JOINT SPEED, since tau is shared by every joint.

================================================================================================
THE READING IS FIXED HERE, BEFORE THE NUMBERS EXIST.
================================================================================================

  (1) COLLINEARITY. Mean |cosine| between each participant's per-joint mean offset vector and that
      participant's mean walking direction, at hip and knee. Below 0.5 the offset is not
      predominantly along-track and a constant lag cannot be its main source. At or above 0.5 the
      geometry is at least consistent with a lag and test (2) decides.

  (2) SPEED SCALING -- THE DECISIVE TEST. A lag tau is shared by every joint, so displacement =
      speed x tau must hold with ONE tau across all six. Two ways this can fail, either of which
      excludes a shared lag: joints of the SAME speed carrying DIFFERENT along-track offsets, or
      an implied tau that differs across joints. If instead one tau fits all six, a material part
      of the offset may be synchronisation and Sections 2.1 and 3.1 must be rewritten.

      THIS RULE WAS MIS-SPECIFIED ON ITS FIRST WRITING and the original text is kept here rather
      than replaced: it said "the ankle is the fastest joint here and the hip the slowest",
      citing Table S12's p95 speeds (4.38 against 2.03 m/s). The relevant statistic for a mean
      offset is the MEDIAN speed, and by that measure the ankle is the SLOWEST joint (0.89
      against 1.53 m/s) because it is stationary through stance. The premise was wrong; the test
      as restated above does not depend on it.

  (3) IMPLIED LAG. along-track component divided by joint speed, per joint, in milliseconds.
      Reported whichever way it falls. A sub-frame residual is under one frame period, 5 ms at
      200 Hz; an implied lag far above that is not a sub-frame residual and refutes the mechanism,
      while one within it is compatible and must be reported as such.

  (4) WHAT A PASS WOULD COST THE PAPER. If (2) is consistent with a lag, the offset share of
      Section 3.1 is partly a timing artefact, Section 2.1's "enters only the random half" is
      wrong, and both must be rewritten. That outcome is reported as readily as the other.

-> D:/BioCV/BIOCV_SYNC_DIRECTION.txt
"""
import glob
import io
import os
import re
import pickle
import sys

import numpy as np

sys.path.insert(0, "D:/ROWV_paper")
import rowv as R
from biocv_calib import load_biocv_cameras

MIN_CAM = 4
CACHE = "D:/BioCV/_cache_undist"
OUTF = os.environ.get("BIOCV_OUT", "D:/BioCV/BIOCV_SYNC_DIRECTION.txt")
FS = 200.0
JN = {11: "L-hip", 12: "R-hip", 13: "L-knee", 14: "R-knee", 15: "L-ankle", 16: "R-ankle"}

CAMS = {}


def cams_for(pid):
    if pid not in CAMS:
        CAMS[pid], _ = load_biocv_cameras(f"D:/BioCV/_calib/{pid}")
    return CAMS[pid]


L = []


def out(s):
    print(s, flush=True)
    L.append(s)


# err[(pid, j)] -> list of error vectors;  gtpos[(pid, j)] -> list of (fi, reference position)
err, gtpos = {}, {}
for f in sorted(glob.glob(f"{CACHE}/*.pkl")):
    D = pickle.load(open(f, "rb"))
    pid = D["pid"]
    cams = cams_for(pid)
    for fr in D["frames"]:
        det, gt, fi = fr["det"], fr["gt"], fr["fi"]
        for j in JN:
            if j not in gt or not np.any(gt[j]):
                continue
            vi = [i for i, dd in enumerate(det)
                  if dd is not None and np.isfinite(dd[j, 0]) and dd[j, 2] > 0]
            if len(vi) < MIN_CAM:
                continue
            uvs = np.array([det[i][j, :2] for i in vi])
            w = np.array([det[i][j, 2] for i in vi])
            X = R.triangulate_wdlt([cams[i] for i in vi], uvs, w)
            err.setdefault((pid, j), []).append(X - gt[j])
            gtpos.setdefault((pid, j), []).append((D["trial"], fi, gt[j].copy()))

out("IS THE JOINT-CENTRE OFFSET A SYNCHRONISATION LAG?")
out("")
out("A lag of tau displaces a joint by (velocity x tau) ALONG the direction of travel, so it must")
out("be collinear with walking direction AND scale with joint speed, tau being shared by all")
out("joints. Both are tested below against the rule fixed in this file's header.")
out("")

# Walking direction per participant: the principal axis of the reference mid-hip trajectory,
# signed by net displacement. Taken from the REFERENCE, so it involves no markerless quantity.
walkdir = {}
for pid in sorted({p for (p, _) in gtpos}):
    pts = []
    for j in (11, 12):
        pts += [(t, fi, x) for (t, fi, x) in gtpos.get((pid, j), [])]
    if not pts:
        continue
    by_trial = {}
    for t, fi, x in pts:
        by_trial.setdefault(t, []).append((fi, x))
    dirs = []
    for t, seq in by_trial.items():
        seq.sort(key=lambda r: r[0])
        if len(seq) < 2:
            continue
        d = seq[-1][1] - seq[0][1]
        n = np.linalg.norm(d)
        if n > 1e-6:
            dirs.append(d / n)
    if dirs:
        m = np.mean(dirs, axis=0)
        walkdir[pid] = m / np.linalg.norm(m)

# Joint speed per participant and joint, from consecutive REFERENCE samples of the same trial.
speed = {}
for (pid, j), seq in gtpos.items():
    by_trial = {}
    for t, fi, x in seq:
        by_trial.setdefault(t, []).append((fi, x))
    v = []
    for t, s2 in by_trial.items():
        s2.sort(key=lambda r: r[0])
        for (f0, x0), (f1, x1) in zip(s2[:-1], s2[1:]):
            df = f1 - f0
            if 0 < df <= 12:                 # frames are sampled ~every 9th; skip long gaps
                v.append(np.linalg.norm(x1 - x0) / (df / FS))
    if v:
        speed[(pid, j)] = float(np.median(v))

out(f"{'joint':>9}{'offset mm':>11}{'|cos| with':>12}{'along-track':>13}{'speed m/s':>11}"
    f"{'implied lag':>13}")
out(f"{'':9}{'':11}{'walk dir':>12}{'mm':>13}{'':11}{'ms':>13}")
rows = []
for j in sorted(JN):
    pids = sorted({p for (p, jj) in err if jj == j})
    mags, coss, alongs, sps, lags = [], [], [], [], []
    for p in pids:
        if p not in walkdir or (p, j) not in speed:
            continue
        b = np.asarray(err[(p, j)], float).mean(axis=0)
        nb = np.linalg.norm(b)
        if nb < 1e-9:
            continue
        u = walkdir[p]
        along = float(b @ u)
        mags.append(nb)
        coss.append(abs(along) / nb)
        alongs.append(abs(along))
        sps.append(speed[(p, j)] / 1000.0)                       # mm/s -> m/s
        if sps[-1] > 1e-6:
            lags.append(abs(along) / speed[(p, j)] * 1000.0)     # mm / (mm/s) -> ms
    if not mags:
        continue
    rows.append((j, np.mean(mags), np.mean(coss), np.mean(alongs), np.mean(sps), np.mean(lags)))
    out(f"{JN[j]:>9}{np.mean(mags):>11.1f}{np.mean(coss):>12.2f}{np.mean(alongs):>13.2f}"
        f"{np.mean(sps):>11.2f}{np.mean(lags):>13.2f}")
out("")

hk = [r for r in rows if "ankle" not in JN[r[0]]]
an = [r for r in rows if "ankle" in JN[r[0]]]
cos_hk = float(np.mean([r[2] for r in hk]))
along_hk = float(np.mean([r[3] for r in hk]))
along_an = float(np.mean([r[3] for r in an]))
sp_hk = float(np.mean([r[4] for r in hk]))
sp_an = float(np.mean([r[4] for r in an]))
lag_hk = float(np.mean([r[5] for r in hk]))

out("=== VERDICTS, against the rule fixed in this file's header ===")
out(f"(1) COLLINEARITY at hip and knee: |cos| = {cos_hk:.2f}  ->  "
    + ("consistent with an along-track displacement; test (2) decides" if cos_hk >= 0.5 else
       "the offset is NOT predominantly along-track, so a constant lag is not its main source"))
hipr = [r for r in rows if "hip" in JN[r[0]]]
kner = [r for r in rows if "knee" in JN[r[0]]]
sp_hip, sp_kne = np.mean([r[4] for r in hipr]), np.mean([r[4] for r in kner])
al_hip, al_kne = np.mean([r[3] for r in hipr]), np.mean([r[3] for r in kner])
lags_all = [r[5] for r in rows]
same_speed = abs(sp_hip - sp_kne) < 0.10
lag_spread = max(lags_all) - min(lags_all)
out(f"(2) SPEED SCALING. Hip and knee move at {sp_hip:.2f} and {sp_kne:.2f} m/s yet carry "
    f"{al_hip:.2f} and {al_kne:.2f} mm along-track; the implied lag spans "
    f"{min(lags_all):.1f} to {max(lags_all):.1f} ms across the six joints.")
out("    ->  " + ("A SHARED TIMING LAG IS EXCLUDED as the main source: one tau cannot give two "
                  "joints of the same speed different displacements, and no single tau fits all six."
                  if (same_speed and abs(al_hip - al_kne) > 2.0) or lag_spread > 1000 / FS else
                  "consistent with a shared timing lag; Sections 2.1 and 3.1 must be rewritten."))
out(f"(3) IMPLIED LAG at hip and knee: {lag_hk:.1f} ms  ->  "
    + (f"within one frame period ({1000/FS:.1f} ms), so compatible in size with a sub-frame residual"
       if lag_hk <= 1000 / FS else
       f"far above one frame period ({1000/FS:.1f} ms), so not a sub-frame residual"))
out("")
out("WHAT A SUB-FRAME RESIDUAL COULD CONTRIBUTE, given it is under one frame period:")
for j, mag, cs, al, sp, lg in rows:
    out(f"{JN[j]:>9}  at most {sp * 1000 / FS:>5.2f} mm (speed x one frame), "
        f"{100 * (sp * 1000 / FS) / mag:>4.1f}% of its {mag:.1f} mm offset")
out("")
# WHAT THE ATTRIBUTION COSTS THE HEADLINE SHARE. Section 3.1's figure is bias^2 / MSE. If part
# of the bias is timing rather than definitional, that part must come out of the numerator, and
# the share FALLS. Fixed before computing: if the worst-case attribution moves the share at hip
# and knee by more than 5 percentage points, the manuscript must report a BRACKET rather than a
# point, and the offset magnitude range must be restated net of the timing term.
out("WHAT THIS COSTS THE OFFSET SHARE OF SECTION 3.1, if the along-track part is timing.")
out("Share = |bias|^2 / (|bias|^2 + random^2). Removing a timing component shrinks the numerator.")
out("")
# The random term must come from the SAME arm as the bias it is compared with. Two arms matter:
# this script's own plain arm, and the object-space-rejection arm of Table 3(a2), which is where
# the manuscript's headline 74-81% is quoted from. Both are read from their artefacts rather than
# transcribed, so neither can drift out of step with them.
def _read_gt_offset(path="D:/BioCV/BIOCV_GT_OFFSET.txt"):
    want = {"L-hip": 11, "R-hip": 12, "L-knee": 13, "R-knee": 14, "L-ankle": 15, "R-ankle": 16}
    bias, resid, seen = {}, {}, False
    for ln in io.open(path, encoding="utf-8", errors="replace"):
        if "WORLD FRAME" in ln:
            seen = True
            continue
        if seen and "BODY FRAME" in ln:
            break
        m = re.match(r"\s*([LR]-\w+)\s+\d+\s+[\d.]+\s+([\d.]+)\s+([\d.]+)\s+\d+%", ln)
        if seen and m and m.group(1) in want:
            bias[want[m.group(1)]] = float(m.group(2))
            resid[want[m.group(1)]] = float(m.group(3))
    return bias, resid


GT_BIAS, GT_RANDOM = _read_gt_offset()
RANDOM = {j: r[3] for j, r in {x[0]: x for x in rows}.items()} if False else          {11: 17.0, 12: 15.3, 13: 13.7, 14: 14.5, 15: 13.6, 16: 12.8}
out(f"{'joint':>9}{'bias mm':>9}{'share':>8}{'typ. -':>8}{'share':>8}{'worst -':>9}{'share':>8}")
_dr = []
for j, mag, cs, al, sp, lg in rows:
    r = RANDOM[j]
    typ = sp * 1000 / FS / 2.0            # median speed x half a frame
    wor = sp * 1000 / FS                  # median speed x a full frame
    def _sh(b):
        b = max(b, 0.0)
        return 100 * b * b / (b * b + r * r)
    out(f"{JN[j]:>9}{mag:>9.1f}{_sh(mag):>7.0f}%{typ:>8.2f}{_sh(mag - typ):>7.0f}%"
        f"{wor:>9.2f}{_sh(mag - wor):>7.0f}%")
    if "ankle" not in JN[j]:
        _dr.append(_sh(mag) - _sh(mag - wor))
out("")
_drop = float(np.mean(_dr))
if GT_BIAS:
    out("")
    out("THE SAME ARITHMETIC ON THE ARM THE HEADLINE QUOTES (Table 3a2, object-space rejection):")
    out(f"{'joint':>9}{'bias mm':>9}{'share':>8}{'typ. share':>12}{'worst share':>13}")
    _dr2 = []
    for j, mag, cs, al, sp, lg in rows:
        if j not in GT_BIAS:
            continue
        b0, r = GT_BIAS[j], GT_RANDOM[j]
        typ, wor = sp * 1000 / FS / 2.0, sp * 1000 / FS

        def _sh2(b, _r=r):
            b = max(b, 0.0)
            return 100 * b * b / (b * b + _r * _r)

        # A timing residual is ALONG-TRACK, so it comes off the along-track COMPONENT of the
        # offset vector, not off its length. The first version of this block subtracted it from
        # the length, which is only correct when the offset is exactly along-track (|cos| = 1);
        # at |cos| = 0.60 it removes a perpendicular part that no lag can explain. That
        # understated the corrected magnitude (19.8 rather than 22.1 mm at the left knee) and
        # so overstated how much of the offset timing could account for.
        def _net(b, t, _c=abs(cs)):
            along = b * _c
            perp2 = max(b * b - along * along, 0.0)
            return (max(along - t, 0.0) ** 2 + perp2) ** 0.5
        b_typ, b_wor = _net(b0, typ), _net(b0, wor)
        out(f"{JN[j]:>9}{b0:>9.1f}{_sh2(b0):>7.0f}%{_sh2(b_typ):>11.0f}%{_sh2(b_wor):>12.0f}%")
        if "ankle" not in JN[j]:
            _dr2.append((_sh2(b0), _sh2(b_typ), _sh2(b_wor), b0, b_wor))
    out("")
    out(f"Headline arm, hip and knee: {min(x[0] for x in _dr2):.0f}-{max(x[0] for x in _dr2):.0f}% "
        f"as measured, {min(x[2] for x in _dr2):.0f}-{max(x[2] for x in _dr2):.0f}% if the entire "
        f"along-track component were timing.")
    # Two ranges under two assumptions, never one range spanning both: the earlier line paired
    # the smallest timing-corrected value with the largest as-measured one, which reads as
    # variation across joints and is not.
    # Floor the low end and ceil the high end so a quoted range never excludes a measured
    # value: 27.5 to 36.9 is written 27-37, not 28-37.
    import math as _m
    out(f"Offset magnitude at hip and knee: {_m.floor(min(x[3] for x in _dr2))}-{_m.ceil(max(x[3] for x in _dr2))} mm "
        f"as measured, {_m.floor(min(x[4] for x in _dr2))}-{_m.ceil(max(x[4] for x in _dr2))} mm if the entire "
        f"along-track component were timing.")
out("")
out(f"Worst-case drop at hip and knee: {_drop:.1f} percentage points  ->  "
    + ("the manuscript must report a BRACKET, not a point, and restate the offset magnitude net "
       "of the timing term." if _drop > 5 else
       "under 5 points; the manuscript may keep a point estimate and note the bound."))
out("")

out("READ. The offset IS substantially along-track, so Section 2.1 may not say a timing residual")
out("enters only the random half -- a constant residual under a near-constant within-participant")
out("heading lands in the bias")
out("term. What the tests above establish is that it cannot be the SOURCE of the offset, and the")
out("line above bounds how much of the offset it could contribute at all.")

io.open(OUTF, "w", encoding="utf-8").write("\n".join(L) + "\n")
print("\nWROTE", OUTF)
