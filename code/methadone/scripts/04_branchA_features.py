# -*- coding: utf-8 -*-
"""
Experiment 1 - Branch A feature reconstruction (7-day slope -> polar angle).

Per the method read off the PPTX (slides 2-4) + MATLAB workspace:
  1. normalize daily dose to % of dose on day -7 (7 days before the test)
  2. 3-day moving window (step 1 day) over the 7 days BEFORE and 7 days AFTER
     the test; take the MIN and MAX slope on each side
  3. polar angle:
        theta_min = atan2(post_min_slope, pre_min_slope)
        theta_max = atan2(post_max_slope, pre_max_slope)
  4. polarhistogram(theta,30) and 2D histogram of (theta_min, theta_max)

This script REPRODUCES the rose plots (slide 3/29) and the 2D histogram
(slide 4) so we can eyeball-match the original before assigning clusters.
Branch-A condition = dose CHANGES within +/-7d (else it's Branch B / PCA).

Dose signal used: 處方劑量(mg) [configurable: DOSE_COL].
"""
import os as _os
ROOT = _os.environ.get('MMT_DATA_ROOT', '')  # local folder holding raw data/, code/, analysis/
if not ROOT: raise SystemExit('Set MMT_DATA_ROOT before running; patient data is not distributed.')

import os
import numpy as np
import pandas as pd

OUT = _os.path.join(ROOT, r'analysis')
DOSE_COL = 'dose_mg'   # 處方劑量(mg)

dose  = pd.read_parquet(os.path.join(OUT, 'dose_cache.parquet'))
urine = pd.read_parquet(os.path.join(OUT, 'urine_morphine.parquet'))

dose_by = {p: g.set_index('date')[DOSE_COL].sort_index() for p, g in dose.groupby('pid')}

def day_offset_series(s, test_date, lo, hi):
    """Return dict {offset: normalized_dose} for offsets in [lo,hi] present in s,
       normalized to dose at offset -7. Returns None if ref day missing/zero."""
    idx = pd.date_range(test_date + pd.Timedelta(days=lo), test_date + pd.Timedelta(days=hi))
    present = {}
    for off in range(lo, hi + 1):
        d = test_date + pd.Timedelta(days=off)
        if d in s.index:
            present[off] = float(s.loc[d])
    ref = present.get(-7)
    if ref is None or ref == 0:
        return None
    return {o: v / ref * 100.0 for o, v in present.items()}

def window_slopes(norm, offs_lo, offs_hi):
    """min & max slope over 3-day moving windows within [offs_lo, offs_hi]."""
    slopes = []
    for start in range(offs_lo, offs_hi - 1):          # 3-day windows
        pts = [(o, norm[o]) for o in (start, start + 1, start + 2) if o in norm]
        if len(pts) >= 2:
            x = np.array([p[0] for p in pts], float)
            y = np.array([p[1] for p in pts], float)
            slopes.append(np.polyfit(x, y, 1)[0])
    if not slopes:
        return None, None
    return min(slopes), max(slopes)

rows = []
for t in urine.itertuples(index=False):
    s = dose_by.get(t.pid)
    if s is None:
        continue
    norm = day_offset_series(s, t.date, -7, 7)
    if norm is None or len(norm) < 6:
        continue
    # Branch A requires dose change within +/-7d (else Branch B)
    vals = list(norm.values())
    if max(vals) - min(vals) < 1e-9:
        continue
    pre_min, pre_max   = window_slopes(norm, -7, 0)
    post_min, post_max = window_slopes(norm, 0, 7)
    if None in (pre_min, pre_max, post_min, post_max):
        continue
    theta_min = np.arctan2(post_min, pre_min)
    theta_max = np.arctan2(post_max, pre_max)
    rows.append((t.pid, t.date, t.positive, pre_min, pre_max, post_min, post_max,
                 theta_min, theta_max))

feat = pd.DataFrame(rows, columns=['pid', 'date', 'positive', 'pre_min', 'pre_max',
                                   'post_min', 'post_max', 'theta_min', 'theta_max'])
feat.to_parquet(os.path.join(OUT, 'branchA_features.parquet'))

print('=== Branch A feature extraction ===')
print('tests entering Branch A :', len(feat))
print('  positive / negative   :', int(feat.positive.sum()), '/', int((feat.positive == 0).sum()))
print('theta_min range (rad)   :', round(feat.theta_min.min(), 3), '..', round(feat.theta_min.max(), 3))
print('theta_max range (rad)   :', round(feat.theta_max.min(), 3), '..', round(feat.theta_max.max(), 3))

# ---- figures to compare against PPTX ----
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

pos = feat[feat.positive == 1]

fig = plt.figure(figsize=(15, 5))
ax1 = fig.add_subplot(1, 3, 1, projection='polar')
ax1.hist(pos.theta_min, bins=30)
ax1.set_title('polarhistogram(theta_min,30)  [positive]')
ax2 = fig.add_subplot(1, 3, 2, projection='polar')
ax2.hist(pos.theta_max, bins=30)
ax2.set_title('polarhistogram(theta_max,30)  [positive]')
ax3 = fig.add_subplot(1, 3, 3)
H, xe, ye = np.histogram2d(pos.theta_min, pos.theta_max, bins=30,
                           range=[[-np.pi, np.pi], [-np.pi, np.pi]])
im = ax3.imshow(H.T, origin='lower', extent=[-np.pi, np.pi, -np.pi, np.pi], aspect='auto')
ax3.set_xlabel('theta_min'); ax3.set_ylabel('theta_max')
ax3.set_title('2D histogram (theta_min, theta_max)')
plt.colorbar(im, ax=ax3)
plt.tight_layout()
fig.savefig(os.path.join(OUT, 'fig_branchA_angles.png'), dpi=110)
print('\nsaved fig_branchA_angles.png')
