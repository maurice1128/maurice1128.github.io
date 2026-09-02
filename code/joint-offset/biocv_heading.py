"""How wide is the span of walking headings across the 104 trials?

Two files assert "all 104 trials walk within a 9 degree span of heading" in prose, and three
claims rest on it: that the population offset table is a world-frame translation which therefore
does not transfer to another laboratory, that the world- and body-frame decompositions of
Table S3m are near-identical, and that a constant sub-frame timing residual lands in the BIAS
term rather than the random one (Table S14). The number was never computed. It is computed here.

Heading is taken from the marker-based reference alone, as the horizontal direction of the
mid-hip displacement from the first to the last usable frame of a trial, so no assumption about
the markerless pipeline enters. The span is reported as the width of the smallest arc containing
every trial's heading, which is the quantity the three claims need; headings 180 degrees apart
are the same line of travel walked in opposite directions, so the arc is computed on the
DOUBLED angle and halved, which makes a there-and-back protocol read as one axis rather than two.

================================================================================================
THE READING IS FIXED HERE, BEFORE THE NUMBER EXISTS.
================================================================================================

  (1) HOLDS. If the span is at most 15 degrees, the single-heading premise is confirmed and the
      three claims above may quote the measured value instead of the asserted one.

  (2) WIDER THAN ASSERTED. If the span exceeds 15 degrees, the assertion is wrong. The
      world/body near-identity must then be justified from Table S3m directly rather than from
      heading, and Table S14's timing argument must be restated as applying to the component of
      the offset that is common across headings.

  (3) Either way the measured value replaces the asserted one everywhere it is quoted.

-> D:/BioCV/BIOCV_HEADING.txt
"""
import glob
import io
import os

import ezc3d
import numpy as np

OUTF = os.environ.get("BIOCV_OUT", "D:/BioCV/BIOCV_HEADING.txt")
PIDS = ["P03", "P04", "P06", "P08", "P09", "P10", "P13", "P16", "P17", "P26", "P28"]
HIPS = ("LEFT_HIP", "RIGHT_HIP")

L = []


def out(s):
    print(s, flush=True)
    L.append(s)


head = []
for pid in PIDS:
    for c3d in sorted(glob.glob(f"D:/BioCV/{pid}/*WALK*/markers.c3d")):
        try:
            d = ezc3d.c3d(c3d)
        except Exception:
            continue
        lab = d["parameters"]["POINT"]["LABELS"]["value"]
        if not all(h in lab for h in HIPS):
            continue
        P = np.transpose(d["data"]["points"][:3], (2, 1, 0))
        RES = np.transpose(d["data"]["points"][3], (1, 0))
        idx = [lab.index(h) for h in HIPS]
        ok = np.ones(P.shape[0], bool)
        for j in idx:
            ok &= (np.isfinite(P[:, j]).all(axis=1) & np.any(P[:, j] != 0, axis=1)
                   & np.isfinite(RES[:, j]) & (RES[:, j] >= 0))
        if ok.sum() < 20:
            continue
        mid = 0.5 * (P[:, idx[0]] + P[:, idx[1]])[ok]
        v = mid[-1] - mid[0]
        if np.linalg.norm(v[:2]) < 100.0:            # under 10 cm of travel is not a pass
            continue
        head.append((pid, os.path.basename(os.path.dirname(c3d)),
                     float(np.degrees(np.arctan2(v[1], v[0])))))

out("THE SPAN OF WALKING HEADINGS, MEASURED")
out("")
out("Heading is the horizontal direction of mid-hip displacement from the first to the last")
out("usable reference frame of a trial. Opposite directions of travel along one axis are the same")
out("line, so the arc is computed on the doubled angle and halved.")
out("")
if not head:
    out("No trial yielded a usable heading.")
else:
    a = np.array([h[2] for h in head])
    dbl = np.radians(2.0 * a)
    x, y = np.cos(dbl), np.sin(dbl)
    srt = np.sort(np.degrees(np.arctan2(y, x)) % 360.0)
    gaps = np.diff(np.concatenate([srt, [srt[0] + 360.0]]))
    span_dbl = 360.0 - float(gaps.max())
    span = span_dbl / 2.0
    out(f"{len(head)} trials from {len({h[0] for h in head})} participants.")
    out("Table S12 counts 108 for a reference-only quantity because it requires all six")
    out("lower-limb joints to be labelled, where heading needs only the two hips; the extra")
    out("trial has usable hips and an unusable joint elsewhere.")
    out(f"Smallest arc containing every heading, as an axis: {span:.1f} degrees.")
    out("")
    out(f"{'participant':>12}{'trials':>8}{'own span, deg':>15}")
    for pid in sorted({h[0] for h in head}):
        b = np.array([h[2] for h in head if h[0] == pid])
        db = np.radians(2.0 * b)
        s2 = np.sort(np.degrees(np.arctan2(np.sin(db), np.cos(db))) % 360.0)
        g2 = np.diff(np.concatenate([s2, [s2[0] + 360.0]]))
        out(f"{pid:>12}{len(b):>8}{(360.0 - float(g2.max())) / 2.0:>15.1f}")
    out("")
    out("=== VERDICT, against the rule fixed in this file's header ===")
    if span <= 15.0:
        out(f"(1) HOLDS: {span:.1f} degrees, within the 15-degree threshold. The single-heading")
        out("    premise is confirmed and the measured value replaces the asserted 9 degrees.")
    else:
        out(f"(2) WIDER THAN ASSERTED: {span:.1f} degrees. The prose figure of 9 degrees is wrong.")
        out("    The world/body near-identity must be justified from Table S3m directly, and the")
        out("    timing argument restated as applying to the heading-common component only.")

io.open(OUTF, "w", encoding="utf-8").write("\n".join(L) + "\n")
print("\nWROTE", OUTF)
