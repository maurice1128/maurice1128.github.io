# -*- coding: utf-8 -*-
"""STROBE baseline / descriptive table for the ANALYSABLE cohort.

The R4 editor reviewer flagged the absence of any descriptive table as the single
most likely desk-reject trigger. A raw-data probe showed AGE and SEX are absent
from every source workbook, so they cannot be derived here and must be requested
from the programme. Everything else below IS derivable and is computed from
source records, restricted to the patients who actually contributed the 9,900
analysable tests (patient ids taken from aim2.mat headers)."""
import os as _os
ROOT = _os.environ.get('MMT_DATA_ROOT', '')  # local folder holding raw data/, code/, analysis/
if not ROOT: raise SystemExit('Set MMT_DATA_ROOT before running; patient data is not distributed.')

import pandas as pd, numpy as np, os, io, sys, h5py, openpyxl
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
AN = _os.path.join(ROOT, r'analysis')
RAW = _os.path.join(ROOT, r'raw data')
MAT = _os.path.join(ROOT, r'code\including_False_N_splitdata_testingvalidating\aim2.mat')

f = h5py.File(MAT, 'r')
cells = lambda n: [np.array(f[r]) for r in np.array(f[n]).ravel()]
hdr = cells('All_fill_header')
pidp = np.array(hdr[0]).ravel().astype(int); pidn = np.array(hdr[2]).ravel().astype(int)
POS_P = set(pidp.tolist()); NEG_P = set(pidn.tolist()); ALLP = POS_P | NEG_P
print('=== analysable cohort ===')
print(f'  tests: {len(pidp)} positive + {len(pidn)} negative = {len(pidp)+len(pidn)}')
print(f'  patients: any={len(ALLP)}  contributed a positive={len(POS_P)}  '
      f'contributed a negative={len(NEG_P)}  both={len(POS_P & NEG_P)}')

def roc2date(v):
    try: v = int(v)
    except (TypeError, ValueError): return None
    y, m, d = v // 10000, (v // 100) % 100, v % 100
    if not (1 <= m <= 12 and 1 <= d <= 31): return None
    try: return pd.Timestamp(year=y + 1911, month=m, day=d)
    except ValueError: return None

# ---- weight + site from the urine workbook ----
wb = openpyxl.load_workbook(os.path.join(RAW, '2018-2022驗尿結果.xlsx'), read_only=True, data_only=True)
ws = wb['驗尿結果']; it = ws.iter_rows(values_only=True); next(it)
wt = {}; site = {}
for r in it:
    try: p = int(r[0])
    except (TypeError, ValueError): continue
    if p not in ALLP: continue
    if isinstance(r[6], (int, float)) and 25 < float(r[6]) < 200: wt.setdefault(p, []).append(float(r[6]))
    if r[5] not in (None, ''): site[p] = str(r[5])
wb.close()

# ---- dose records ----
dose = pd.read_parquet(os.path.join(AN, 'dose_cache.parquet'))
dose = dose[dose.pid.isin(ALLP)]
g = dose.groupby('pid')
span = ((g.date.max() - g.date.min()).dt.days / 30.44)
mg = g.dose_mg.median(); cc = g.dose_cc.median(); ndays = g.size()

def desc(s, name, unit='', dec=1):
    s = pd.Series(s).dropna()
    if len(s) == 0:
        print(f'  {name:38s} (no data)'); return
    q1, q2, q3 = np.percentile(s, [25, 50, 75])
    print(f'  {name:38s} n={len(s):5d}  median {q2:.{dec}f} (IQR {q1:.{dec}f}-{q3:.{dec}f}) {unit}')

print('\n=== Table 1. Baseline characteristics of the analysable cohort ===')
print('  (age and sex are NOT present in any source file -- must be supplied by the programme)')
desc([np.median(v) for v in wt.values()], 'Body weight, kg')
desc(span.values, 'Methadone record span, months')
desc(ndays.values, 'Attended dosing days per patient', dec=0)
desc(mg.values, 'Prescribed dose, mg/day (patient median)')
desc(cc.values, 'Consumed dose, cc/day (patient median)')

# tests per patient + positivity, from the analysable sample itself
tp = pd.Series(np.r_[pidp, pidn]).value_counts()
desc(tp.values, 'Analysable urine tests per patient', dec=0)
pos_frac = pd.Series(pidp).value_counts().reindex(sorted(ALLP)).fillna(0) / tp.reindex(sorted(ALLP))
desc(pos_frac.values * 100, 'Morphine-positive tests per patient, %')

print('\n=== dispensing site (column "轉入院所") ===')
if site:
    vc = pd.Series(list(site.values())).value_counts()
    print(f'  distinct values: {len(vc)} across {len(site)} patients')
    for k, n in vc.head(8).items():
        print(f'    {str(k)[:40]:42s} {n:5d} ({n/len(site)*100:.1f}%)')
    if len(vc) > 1:
        print('  NOTE: more than one site value appears -- verify the "single-programme" wording in Methods.')
else:
    print('  no site values recorded for analysable patients')

print('\n=== what still must come from the institution ===')
print('  - age at first methadone record   (MISSING from all source files)')
print('  - sex                             (MISSING from all source files)')
print('  - comorbidity / psychiatric history, if the journal expects it')
