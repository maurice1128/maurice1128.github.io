"""yaw_recover_r309.py -- recover net pelvis yaw per cycle for the four arms whose
registrations required it and whose deposits omitted it: r287, r289, r291, r294.

METHOD: taken verbatim from gain_ladder_r264.py measure(), which is the existing deposited
method (GAIN_LADDER_r264.json carries yaw_per_cycle / yaw_per_cycle_sd / yaw_total).
  pelvis_rotation in degrees; cycles wholly inside [SETTLE, T1]; drop the last;
  per-cycle net change v[b] - v[a]; mean, sd (ddof=1), total.
No method is invented here. Read-only with respect to results/.
"""
import glob, io, json, os, sys, datetime
import numpy as np

sys.path.insert(0, r"C:\Users\maurice\Desktop\spasticity_paper\scone")
import sto_utils as S

RES = r"C:\Users\maurice\Documents\SCONE\results"
PAPER = r"C:\Users\maurice\Desktop\spasticity_paper\paper"
SETTLE, T1 = 1.0, 9.73


def rd(tag, min_lines):
    g = [d for d in glob.glob(os.path.join(RES, tag + ".*")) if os.path.isdir(d)
         and os.path.exists(os.path.join(d, "history.txt"))
         and sum(1 for _ in io.open(os.path.join(d, "history.txt"), errors="replace")) >= min_lines]
    if len(g) != 1:
        return None, "%s -> %d dirs at >=%d history lines" % (tag, len(g), min_lines)
    return g[0], None


def measure(sto):
    cols, dat = S.load_sto(sto)
    t = list(S.col(cols, dat, "time"))
    grf, thr = S.grf_vertical(cols, dat, "l")
    idx = S.heel_strikes(t, grf, thresh=thr)
    v = np.degrees(np.asarray(S.col(cols, dat, "pelvis_rotation"), dtype=float))
    t_end = float(t[-1])
    all_cyc = [(idx[k], idx[k + 1]) for k in range(len(idx) - 1) if t[idx[k]] >= SETTLE]
    c = [(idx[k], idx[k + 1]) for k in range(len(idx) - 1)
         if t[idx[k]] >= SETTLE and t[idx[k + 1]] <= T1]
    c = c[:-1] if len(c) >= 2 else c
    if len(c) < 2:
        return {"t_end_s": t_end, "n_cycles_total": len(all_cyc), "n_cycles_in_window": len(c),
                "yaw_per_cycle": None, "yaw_per_cycle_sd": None, "yaw_total": None,
                "not_measured_because": "fewer than 2 whole cycles inside the window"}
    per = [float(v[b] - v[a]) for a, b in c]
    return {"t_end_s": t_end, "n_cycles_total": len(all_cyc), "n_cycles_in_window": len(c),
            "yaw_per_cycle": float(np.mean(per)),
            "yaw_per_cycle_sd": float(np.std(per, ddof=1)) if len(per) > 1 else None,
            "yaw_total": float(np.sum(per)),
            "per_cycle_values": per}


ARMS = {"r287": ("RUN_BANDFILL_r287_cell*.json", 91),
        "r289": ("RUN_MATCHED20_r289_cell*.json", 91),
        "r291": ("RUN_BANDFILL_r291_cell*.json", 91),
        "r294": ("RUN_FASTSTART_r294_cell*.json", 601)}

out = {"round": 309,
       "what": ("Net pelvis yaw per gait cycle, recovered for the four arms whose registrations "
                "required it (PREREG_matched20_r289.md sec9, PREREG_bandfill_r291.md sec8) and "
                "whose per-cell deposits omitted it."),
       "method_source": ("gain_ladder_r264.py measure(), verbatim. GAIN_LADDER_r264.json is the "
                         "existing deposit using this method. No method invented for this "
                         "recovery."),
       "method": ("pelvis_rotation in degrees; gait cycles wholly inside [%.2f, %.2f] s; drop "
                  "the last; per-cycle net change v[end]-v[start]; mean, sd (ddof=1), total."
                  % (SETTLE, T1)),
       "guard": "the >=91-line history guard (>=601 for r294's 600-generation arm)",
       "arms": {}}

for arm, (pat, minl) in ARMS.items():
    cells, errs = {}, []
    files = sorted(glob.glob(os.path.join(PAPER, pat)))
    for f in files:
        d = json.load(io.open(f, encoding="utf-8"))
        tag = d.get("prefix")
        if not tag:
            errs.append("%s: no prefix field" % os.path.basename(f))
            continue
        dirp, err = rd(tag, minl)
        if err:
            errs.append(err)
            continue
        stos = sorted(glob.glob(os.path.join(dirp, "*.par.sto")))
        if not stos:
            errs.append("%s: no .par.sto" % tag)
            continue
        try:
            cells[tag] = measure(stos[-1])
        except Exception as e:
            errs.append("%s: %s" % (tag, str(e)[:80]))
    ys = [c["yaw_per_cycle"] for c in cells.values() if c.get("yaw_per_cycle") is not None]
    out["arms"][arm] = {
        "n_cell_deposits": len(files), "n_measured": len(cells),
        "n_with_usable_cycles": len(ys),
        "yaw_mean_deg_per_cycle": float(np.mean(ys)) if ys else None,
        "yaw_sd_across_cells": float(np.std(ys, ddof=1)) if len(ys) > 1 else None,
        "unmeasurable_note": ("Cells with fewer than 2 whole cycles inside the window carry "
                              "yaw_per_cycle null. These are cells that collapsed early; the "
                              "omission is the r281 guard operating, not a measurement failure."),
        "errors": errs, "per_cell": cells}
    print("%-6s deposits=%3d measured=%3d usable=%3d mean=%s"
          % (arm, len(files), len(cells), len(ys),
             ("%+.4f" % np.mean(ys)) if ys else "n/a"), flush=True)

out["written_at"] = datetime.datetime.now().isoformat(timespec="seconds")
p = os.path.join(PAPER, "YAW_RECOVERED_r309.json")
io.open(p, "w", encoding="utf-8", newline="\n").write(json.dumps(out, indent=1) + "\n")
print("wrote %s  %d B" % (p, os.path.getsize(p)))
