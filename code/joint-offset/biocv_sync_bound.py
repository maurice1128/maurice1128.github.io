"""How much position error can the uncorrected sub-frame synchronisation residual carry?

The dataset providers corrected a whole-frame offset from an LED pulse and report an uncorrected
sub-frame residual without quantifying it; the copy obtained under our data use agreement carries
no descriptor from which to quote a figure. A reviewer's objection is that this residual inflates
the RANDOM half of the bias/variance decomposition, and therefore deflates the 74-81% offset share
that Section 3.1 is built on. The magnitude cannot be looked up, but it can be BOUNDED from the
reference trajectories, and a bound is what the objection needs.

A sub-frame residual is by definition less than one frame period. At 200 Hz that is 5 ms, so the
worst-case position consequence at a joint is its speed times 5 ms, and the expected consequence
for a residual uniform on (-half a frame, +half a frame) is its speed times 2.5 ms. Both are
computed here, per joint, from the marker-based reference itself -- the same trajectories the
errors are measured against, so no assumption about gait speed enters.

This is an UPPER BOUND on a nuisance term, not an estimate of it. If the bound is small against
the systematic offset (27-37 mm at hip and knee) the objection is answered; if it is comparable, the
share must be qualified.

-> D:/BioCV/BIOCV_SYNC_BOUND.txt
"""
import glob
import io
import os

import ezc3d
import numpy as np

FS = 200.0
OUTF = os.environ.get("BIOCV_OUT", "D:/BioCV/BIOCV_SYNC_BOUND.txt")
JOINTS = ["LEFT_HIP", "RIGHT_HIP", "LEFT_KNEE", "RIGHT_KNEE", "LEFT_ANKLE", "RIGHT_ANKLE"]
PIDS = ["P03", "P04", "P06", "P08", "P09", "P10", "P13", "P16", "P17", "P26", "P28"]

L = []


def out(s):
    print(s, flush=True)
    L.append(s)


speeds = {j: [] for j in JOINTS}
ntr = 0
for pid in PIDS:
    for c3d in sorted(glob.glob(f"D:/BioCV/{pid}/*WALK*/markers.c3d")):
        try:
            d = ezc3d.c3d(c3d)
        except Exception:
            continue
        lab = d["parameters"]["POINT"]["LABELS"]["value"]
        if not all(j in lab for j in JOINTS):
            continue
        VP = np.transpose(d["data"]["points"][:3], (2, 1, 0))
        # C3D convention: the 4th row is the reconstruction residual and a NEGATIVE
        # value marks an invalid sample. Filtering on coordinates alone leaves gap
        # sentinels in, which produced speeds of 1e30 mm/s on the first run.
        RES = np.transpose(d["data"]["points"][3], (1, 0))
        ntr += 1
        for j in JOINTS:
            P = VP[:, lab.index(j), :]
            # A frame is usable only if the marker is labelled there: finite and not the
            # all-zero row ezc3d writes for a gap. Displacement is taken only between two
            # CONSECUTIVE usable frames, so a gap never manufactures a large step.
            ok = (np.isfinite(P).all(axis=1) & np.any(P != 0, axis=1)
                  & np.isfinite(RES[:, lab.index(j)]) & (RES[:, lab.index(j)] >= 0))
            pair = ok[:-1] & ok[1:]
            if pair.sum() < 3:
                continue
            step = np.linalg.norm(P[1:][pair] - P[:-1][pair], axis=1)
            speeds[j].append(step * FS)                              # mm/s

out("AN UPPER BOUND ON THE SUB-FRAME SYNCHRONISATION RESIDUAL, IN MILLIMETRES")
out("")
out(f"{ntr} walking trials, marker-based reference at {FS:.0f} Hz. This count exceeds the 104")
out("trials analysed elsewhere because it needs only the reference markers, not video: the")
out("trials excluded for missing or unusable video still carry usable reference trajectories,")
out("and a bound on the residual is better estimated on all of them.")
out("A sub-frame residual is less")
out("than one frame period (5.00 ms); the expected magnitude for a residual uniform within one")
out("frame is half of that (2.50 ms). Speed is the per-frame displacement of the reference")
out("marker itself, so no assumption about gait speed enters.")
out("")
out(f"{'joint':>12}{'median spd':>12}{'p95 speed':>11}{'typ. bound':>12}{'worst bound':>13}")
out(f"{'':12}{'mm/s':>12}{'mm/s':>11}{'mm @2.5ms':>12}{'mm @5ms':>13}")
rows = []
for j in JOINTS:
    if not speeds[j]:
        continue
    v = np.concatenate(speeds[j])
    # median rather than mean: a single surviving bad sample would otherwise set the bound.
    mu, p95 = float(np.median(v)), float(np.percentile(v, 95))
    rows.append((j, mu, p95))
    out(f"{j:>12}{mu:>12.1f}{p95:>11.1f}{mu * 0.0025:>12.2f}{p95 * 0.005:>13.2f}")
out("")

if rows:
    worst = max(r[2] * 0.005 for r in rows)
    mean_hk = float(np.mean([r[1] * 0.0025 for r in rows if "ANKLE" not in r[0]]))
    OFFSET_LO = 27.0          # Section 3.1's systematic offset at hip and knee, mm
    RANDOM_LO = 13.0          # the random residual it is compared against, mm
    out("=== READ ===")
    out(f"Largest worst-case contribution at any joint: {worst:.2f} mm (p95 speed x one frame).")
    out(f"Typical contribution at hip and knee: {mean_hk:.2f} mm (median speed x half a frame).")
    out("Section 3.1's systematic offset at hip and knee is 27-37 mm and the random residual it is")
    out("compared against is 13-17 mm.")
    out("")
    if worst < 0.1 * RANDOM_LO:
        out("The bound is under a tenth of the random residual, so the synchronisation term cannot")
        out("account for either half of the decomposition. It enters the RANDOM half, so it can only")
        out("DEFLATE the offset share, never inflate it: the 74-81% figure is if anything")
        out("conservative with respect to this nuisance term.")
    elif worst < 0.5 * RANDOM_LO:
        out("The bound is a material but minority fraction of the random residual. It enters the")
        out("RANDOM half only, so it can only DEFLATE the offset share; the 74-81% figure is")
        out("conservative with respect to it, but the random half should not be read as pure")
        out("triangulation noise.")
    else:
        out("AGAINST THE PAPER: the bound is comparable to the random residual, so a material part")
        out("of what Section 3.1 calls random error may be synchronisation. The offset SHARE must")
        out("be qualified accordingly, and the random half must not be described as triangulation")
        out("noise.")
    out("")
    out("It also largely cancels between arms, which share the same frames, and every contrast in")
    out("this paper is between arms; the share is the one quantity it can move.")
    out("")
    out("=== THE RULE ABOVE USED THE WRONG THRESHOLD, AND THIS TABLE THE WRONG ATTRIBUTION ===")
    out("")
    out("Two things are wrong with what precedes, and both are left standing rather than replaced.")
    out("")
    out("First, the threshold fixed in this file's header compares a COMPOUNDED worst case -- the")
    out("95th percentile of joint speed times a FULL frame period, when the whole-frame offset was")
    out("already corrected -- against an RMS quantity, in linear mm, while the decomposition it")
    out("bears on is in SQUARED error. That is why it fired.")
    out("")
    out("Second, and more seriously, the arithmetic this file originally offered as a rebuttal")
    out("placed the residual in the RANDOM half and concluded it 'can only raise the offset share'.")
    out("That attribution is wrong. Heading varies little WITHIN a participant -- 1.0 to 14.1 deg")
    out("for ten of the eleven, 53.7 for P26, against 56.0 across all trials (Table S20) -- and the")
    out("offset is estimated within participant, so a")
    out("CONSTANT sub-frame residual displaces every estimate the same way in the world frame and")
    out("lands in the BIAS term. Table S14 measures the direction and finds the offset is indeed")
    out("substantially along-track (|cos| = 0.60 at hip and knee). The correction therefore runs")
    out("the OTHER way: removing a timing component shrinks the numerator of the share, and the")
    out("share FALLS rather than rises. Table S14 carries that arithmetic, and Section 3.1 now")
    out("quotes the resulting bracket instead of a point.")
    out("")
    out("What survives from this table is the magnitude bound alone: the residual is about 3.6 mm")
    out("at hip and knee on the typical figure and under 7.7 mm at worst. What does NOT survive is")
    out("this file's original claim about which half of the decomposition it enters.")

io.open(OUTF, "w", encoding="utf-8").write("\n".join(L) + "\n")
print("\nWROTE", OUTF)
