"""POST-HOC EXTENSION of the registered video-degradation sweep. NOT PRE-REGISTERED.

DISCLOSURE, WRITTEN FIRST. The registered study (scone/video_degradation.py, sha256
6b8b68b9d44afb784f243e3be0bc2452f3013f378a619e802828cf0e0ba2a3f4) swept angular noise sd from 0
to 8 deg and PREDICTED that mild-rung classification would reach chance somewhere between 3 and 6
deg. That prediction was FALSIFIED: mild leave-one-seed-out accuracy was still 0.684 at sd = 8 deg
(the top of the registered range) with perfect camera alignment. The deliverable "report the noise
amplitude at which mild-rung classification falls to chance" therefore has no answer inside the
registered range.

This script extends the sd sweep upward ONLY, to locate that crossing. It changes nothing else:
it imports and calls the registered functions unmodified, uses the same RNG seed, the same
repetitions, the same splits, the same leave-one-seed-out rule with the direction still fixed
a priori. The extended sd values (10-40 deg, i.e. 11-45 px at 1080p) are FAR BEYOND any plausible
pose-estimator error and are reported as a location exercise for the collapse point, NOT as a
realistic operating regime. Nothing here may be used to revise the registered predictions; the
falsification of PR3 stands.

Output: paper/VIDEO_DEGRADATION_POSTHOC.json  (the registered paper/VIDEO_DEGRADATION.json is
not touched).
"""
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import video_degradation as V  # noqa: E402
from scipy import signal  # noqa: E402

SIGMA_EXT = [0.0, 2.0, 4.0, 6.0, 8.0, 10.0, 12.0, 16.0, 20.0, 26.0, 32.0, 40.0]
YAWS = [("fixed", 0.0), ("random", 30.0)]
FS = 30.0
OUT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "paper",
                                   "VIDEO_DEGRADATION_POSTHOC.json"))


def main():
    rng = np.random.default_rng(V.SEED)
    runs = V.load_runs()
    ridx = {"_REF_": np.array([i for i, r in enumerate(runs) if r["cond"] in V.REFERENCE])}
    b, a = signal.butter(V.BUTTER_ORDER, V.FC / (FS / 2.0), btype="low")
    pr = [V.prepare(r, FS) for r in runs]
    dpp = V.deg_per_px(V.PX_PER_M_1080)

    cells = []
    for ymode, ymax in YAWS:
        print("\n=== POST-HOC extended sweep, fs=30 Hz, yaw %s %g deg ===" % (ymode, ymax))
        print("%7s %7s | %-24s | %-24s" % ("sd_deg", "sd_px", "MILD loso[p05] ref refcal",
                                           "SEVERE loso[p05] ref refcal"))
        for sd in SIGMA_EXT:
            nrep = 1 if (sd == 0.0 and ymode == "fixed") else V.N_REP
            rom = np.empty((nrep, len(runs)))
            for k, (grid, qs, qf, wins) in enumerate(pr):
                if ymode == "fixed":
                    ang = V.project(qs, qf, np.cos(np.radians(ymax)))[None, :]
                    ang = np.repeat(ang, nrep, axis=0) if nrep > 1 else ang
                else:
                    th = rng.uniform(0.0, ymax, size=nrep)
                    ang = V.project(qs[None, :], qf[None, :], np.cos(np.radians(th))[:, None])
                if sd > 0:
                    ang = ang + rng.normal(0.0, sd, size=ang.shape)
                rom[:, k] = V.rom_matrix(ang, wins, b, a)
            res = V.evaluate(rom, runs, ridx)
            m, s = res["MILD"], res["SEVERE"]
            cells.append({"fs": FS, "yaw_mode": ymode, "yaw_deg": ymax, "sigma_deg": sd,
                          "sigma_px_1080p": sd / dpp, "n_rep": nrep, "splits": res})
            print("%7.1f %7.2f | %.3f [%.3f] %.3f %.3f | %.3f [%.3f] %.3f %.3f"
                  % (sd, sd / dpp, m["loso_mean"], m["loso_p05"], m["ref_mean"], m["refcal_mean"],
                     s["loso_mean"], s["loso_p05"], s["ref_mean"], s["refcal_mean"]))

    def cross(ymode, ymax, split, key, rule):
        for c in sorted([c for c in cells if c["yaw_mode"] == ymode and c["yaw_deg"] == ymax],
                        key=lambda c: c["sigma_deg"]):
            if rule(c["splits"][split][key]):
                return c["sigma_deg"]
        return None

    summary = {}
    for ymode, ymax in YAWS:
        t = "%s_%g" % (ymode, ymax)
        summary[t] = {
            "mild_p05_reaches_chance_sigma_deg":
                cross(ymode, ymax, "MILD", "loso_p05", lambda x: x <= 0.5),
            "mild_mean_below_060_sigma_deg":
                cross(ymode, ymax, "MILD", "loso_mean", lambda x: x < 0.60),
            "mild_mean_below_055_sigma_deg":
                cross(ymode, ymax, "MILD", "loso_mean", lambda x: x < 0.55),
            "severe_mean_below_060_sigma_deg":
                cross(ymode, ymax, "SEVERE", "loso_mean", lambda x: x < 0.60),
        }
    print("\n=== POST-HOC crossings (sd in deg; 1 deg = %.2f px at 1080p) ===" % (1.0 / dpp))
    for k, v in summary.items():
        print("  %-12s %s" % (k, v))

    json.dump({"POSTHOC": True, "not_preregistered": True,
               "registered_script_sha256":
                   "6b8b68b9d44afb784f243e3be0bc2452f3013f378a619e802828cf0e0ba2a3f4",
               "why": "registered sd range 0-8 deg did not contain the mild chance-crossing",
               "deg_per_px_1080p": dpp, "sigma_deg": SIGMA_EXT,
               "cells": cells, "summary": summary}, open(OUT, "w"), indent=1)
    print("\nwrote %s (%d bytes)" % (OUT, os.path.getsize(OUT)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
