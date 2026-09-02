# -*- coding: utf-8 -*-
"""r425: render a sagittal stick-figure animation straight from the .sto files.

NO SCONE AND NO HYFYDY LICENCE ARE INVOLVED. The .sto carries world positions for torso, pelvis,
femur_l/r, tibia_l/r and calcn_l/r, so the figure is drawn from data that is already on disk and
will still be renderable after the trial expires on 2026-08-27.

Usage:
  python render_gait_r425.py                  # the headline pair, spastic vs weak
  python render_gait_r425.py --left PREFIX --right PREFIX --out NAME
"""
import argparse
import glob
import os
import re
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt          # noqa: E402
import imageio.v2 as imageio             # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sto_utils as S                    # noqa: E402

RES = r"C:\Users\maurice\Documents\SCONE\results"
OUTDIR = r"C:\Users\maurice\Desktop\spasticity_paper\figures"
SETTLE, T1 = 1.0, 9.73

# drawn as chains of body origins; the affected side is the LEFT leg throughout this project
CHAINS = [("torso", "pelvis"), ("pelvis", "femur_r"), ("femur_r", "tibia_r"),
          ("tibia_r", "calcn_r"), ("pelvis", "femur_l"), ("femur_l", "tibia_l"),
          ("tibia_l", "calcn_l")]
LEFT_LINKS = {("pelvis", "femur_l"), ("femur_l", "tibia_l"), ("tibia_l", "calcn_l")}


def load(prefix):
    g = [d for d in glob.glob(os.path.join(RES, prefix + ".*")) if os.path.isdir(d)]
    if not g:
        raise SystemExit("no result dir for " + prefix)
    if len(g) > 1:
        g = [max(g, key=lambda d: len(glob.glob(os.path.join(d, "[0-9]*.par"))))]
    st = sorted(glob.glob(os.path.join(g[0], "*.par.sto")))
    if not st:
        raise SystemExit("no .par.sto in " + g[0])
    cols, dat = S.load_sto(st[-1])
    t = dat[:, 0]
    pos = {}
    for c in cols:
        m = re.match(r"(.+)\.pos\.([xyz])$", c)
        if m and m.group(1) not in ("world", "ground"):
            pos.setdefault(m.group(1), {})[m.group(2)] = S.col(cols, dat, c)
    grf, thr = S.grf_vertical(cols, dat, "l")
    hs = S.heel_strikes(t, grf, thresh=thr)
    allc = [(hs[k], hs[k + 1]) for k in range(len(hs) - 1) if t[hs[k]] >= SETTLE]
    win = [c for c in allc if t[c[1]] <= T1]
    win = win[:-1] if len(win) >= 2 else win
    knee = np.degrees(S.col(cols, dat, "knee_angle_l"))
    return {"t": t, "pos": pos, "knee": knee, "hs": [a for a, _ in win],
            "knee_hs": float(np.mean([knee[a] for a, _ in win])) if win else float("nan"),
            "n_cycles": len(win), "t_end": float(t[-1])}


def draw(ax, D, k, title, colour):
    ax.clear()
    p = D["pos"]
    px = p["pelvis"]["x"][k]
    for a, b in CHAINS:
        if a not in p or b not in p:
            continue
        lw, col = (4.0, colour) if (a, b) in LEFT_LINKS else (2.0, "#b9c0cc")
        ax.plot([p[a]["x"][k] - px, p[b]["x"][k] - px],
                [p[a]["y"][k], p[b]["y"][k]], "-", lw=lw, color=col,
                solid_capstyle="round", zorder=3 if (a, b) in LEFT_LINKS else 2)
    for b in ("torso", "pelvis", "femur_l", "tibia_l", "calcn_l"):
        if b in p:
            ax.plot(p[b]["x"][k] - px, p[b]["y"][k], "o", ms=5, color=colour, zorder=4)
    ax.axhline(0, color="#8a8f99", lw=1.2, zorder=1)
    ax.set_xlim(-0.95, 0.95)
    ax.set_ylim(-0.06, 1.85)
    ax.set_aspect("equal")
    ax.axis("off")
    on_hs = k in D["hs"]
    ax.set_title("%s\n膝角 %+.1f°%s" % (title, D["knee"][k], "   ← 腳跟著地" if on_hs else ""),
                 fontsize=11, color=colour if on_hs else "#2b2f36",
                 fontweight="bold" if on_hs else "normal")
    if on_hs:
        ax.add_patch(plt.Circle((p["calcn_l"]["x"][k] - px, p["calcn_l"]["y"][k]), 0.06,
                                fill=False, lw=2.5, color=colour, zorder=5))


def trace(ax, D, k, colour, label):
    ax.clear()
    t, kn = D["t"], D["knee"]
    ax.plot(t, kn, "-", lw=1.2, color="#c8ccd4")
    ax.plot(t[:k + 1], kn[:k + 1], "-", lw=1.8, color=colour)
    hs = [h for h in D["hs"] if h <= k]
    if hs:
        ax.plot(t[hs], kn[hs], "o", ms=5, color=colour)
    ax.axhline(D["knee_hs"], ls="--", lw=1.0, color=colour, alpha=0.7)
    ax.set_xlim(SETTLE, T1)
    ax.set_ylim(min(kn) - 4, max(kn) + 4)
    ax.set_xlabel("時間 (s)", fontsize=9)
    ax.set_ylabel("左膝角 (°)", fontsize=9)
    ax.set_title("%s   著地平均 %+.2f°" % (label, D["knee_hs"]), fontsize=9, color=colour)
    ax.grid(alpha=0.25)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--left", default="R396SPg110_s101")
    ap.add_argument("--right", default="R151W_s101")
    ap.add_argument("--left-label", default="痙攣 (KV 0.110)")
    ap.add_argument("--right-label", default="無力 (脛前肌 x0.80)")
    ap.add_argument("--out", default="gait_spastic_vs_weak")
    ap.add_argument("--fps", type=int, default=25)
    ap.add_argument("--stride", type=int, default=2)
    a = ap.parse_args()

    for f in ("Microsoft JhengHei", "Microsoft YaHei", "SimHei", "DejaVu Sans"):
        try:
            matplotlib.rcParams["font.sans-serif"] = [f]
            matplotlib.rcParams["axes.unicode_minus"] = False
            break
        except Exception:
            continue

    L, R = load(a.left), load(a.right)
    print("%-22s %d cycles, t_end %.2f, knee@HS %+.4f" % (a.left, L["n_cycles"], L["t_end"],
                                                          L["knee_hs"]))
    print("%-22s %d cycles, t_end %.2f, knee@HS %+.4f" % (a.right, R["n_cycles"], R["t_end"],
                                                          R["knee_hs"]))
    print("edge difference of the two means: %+.4f deg" % (R["knee_hs"] - L["knee_hs"]))

    n = min(len(L["t"]), len(R["t"]))
    ks = [k for k in range(0, n, a.stride) if SETTLE <= L["t"][k] <= T1]
    os.makedirs(OUTDIR, exist_ok=True)

    fig = plt.figure(figsize=(11, 6.2), dpi=110)
    gs = fig.add_gridspec(2, 2, height_ratios=[2.4, 1.0], hspace=0.32, wspace=0.18)
    axL, axR = fig.add_subplot(gs[0, 0]), fig.add_subplot(gs[0, 1])
    tL, tR = fig.add_subplot(gs[1, 0]), fig.add_subplot(gs[1, 1])
    CL, CR = "#c0392b", "#1f6fb4"

    frames = []
    for i, k in enumerate(ks):
        draw(axL, L, k, a.left_label, CL)
        draw(axR, R, k, a.right_label, CR)
        trace(tL, L, k, CL, a.left_label)
        trace(tR, R, k, CR, a.right_label)
        fig.suptitle("腳跟著地瞬間的左膝角:痙攣 vs 無力   (資料來自已存檔的 .sto,無需授權)",
                     fontsize=12, y=0.975)
        fig.canvas.draw()
        buf = np.asarray(fig.canvas.buffer_rgba())[:, :, :3]
        frames.append(buf.copy())
        if i % 25 == 0:
            print("  frame %d/%d" % (i, len(ks)))
            sys.stdout.flush()
    plt.close(fig)

    gif = os.path.join(OUTDIR, a.out + ".gif")
    imageio.mimsave(gif, frames, fps=a.fps, loop=0)
    print("wrote %s (%.1f MB, %d frames)" % (gif, os.path.getsize(gif) / 1e6, len(frames)))
    try:
        mp4 = os.path.join(OUTDIR, a.out + ".mp4")
        imageio.mimsave(mp4, frames, fps=a.fps, quality=8)
        print("wrote %s (%.1f MB)" % (mp4, os.path.getsize(mp4) / 1e6))
    except Exception as e:
        print("mp4 unavailable (%s); the gif is the deliverable" % type(e).__name__)


if __name__ == "__main__":
    main()
