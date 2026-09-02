# -*- coding: utf-8 -*-
"""Step 43 - participant-flow diagnostics demanded by the round-2 review.

Three questions the funnel in 3.1 did not answer:
  (a) why do 1,704 of the 3,213 tested patients have NO daily methadone record?
      -> characterise the dose extract's own patient coverage and date span
  (b) 599 patients were supplied on the >=2-year retention list but only 553
      appear at step 3 -- where did the other 46 go?
  (c) the 4,516 tests lost at the dosing-linkage step: do they differ in
      positivity from the linked ones? (selection mechanism, not a technicality)
  (d) the 677 duplicate patient-day urine records the pipeline retained: are
      they concordant (same result) or discordant (two different results)?

Prints only; nothing downstream depends on it.
"""
import os as _os
ROOT = _os.environ.get('MMT_DATA_ROOT', '')  # local folder holding raw data/, code/, analysis/
if not ROOT: raise SystemExit('Set MMT_DATA_ROOT before running; patient data is not distributed.')

import pandas as pd, numpy as np, os, openpyxl

AN = _os.path.join(ROOT, r'analysis')
RAW = _os.path.join(ROOT, r'raw data')

def roc2date(v):
    try: v = int(v)
    except (TypeError, ValueError): return None
    y, m, d = v // 10000, (v // 100) % 100, v % 100
    if not (1 <= m <= 12 and 1 <= d <= 31): return None
    try: return pd.Timestamp(year=y + 1911, month=m, day=d)
    except ValueError: return None

# ---------- urine records ----------
wb = openpyxl.load_workbook(os.path.join(RAW, '2018-2022驗尿結果.xlsx'), read_only=True, data_only=True)
ws = wb['驗尿結果']; it = ws.iter_rows(values_only=True); next(it)
recs = []
for r in it:
    if r[2] == 1 and r[3] in (0, 1):
        d = roc2date(r[1])
        if d is not None: recs.append((int(r[0]), d, int(r[3])))
wb.close()
u = pd.DataFrame(recs, columns=['pid', 'date', 'positive'])

dose = pd.read_parquet(os.path.join(AN, 'dose_cache.parquet'))
dpat = set(dose.pid.unique())

# ---------- (a) coverage of the dose extract ----------
print('=== (a) dose extract coverage ===')
print(f'  patients with >=1 urine record      : {u.pid.nunique()}')
print(f'  patients in the daily-dose extract  : {len(dpat)}')
print(f'  intersection                        : {len(set(u.pid) & dpat)}')
print(f'  dose-extract patients with NO urine : {len(dpat - set(u.pid))}')
print(f'  tested patients with NO dose record : {len(set(u.pid) - dpat)}')
print(f'  dose extract date span              : {dose.date.min().date()} .. {dose.date.max().date()}')
print(f'  urine record date span              : {u.date.min().date()} .. {u.date.max().date()}')

# per-patient number of dosing days for linked patients (is the extract a subset by volume?)
npd = dose.groupby('pid').size()
print(f'  dosing days per extract patient     : median {npd.median():.0f} (IQR {npd.quantile(.25):.0f}-{npd.quantile(.75):.0f}), min {npd.min()}')

# ---------- (b) 599 vs 553 ----------
wb = openpyxl.load_workbook(os.path.join(RAW, '2年以上維持治療者_599人.xlsx'), read_only=True, data_only=True)
ws = wb.active; it = ws.iter_rows(values_only=True); next(it)
keep = set()
for r in it:
    if r[0] is not None:
        try: keep.add(int(r[0]))
        except (TypeError, ValueError): pass
wb.close()
print('\n=== (b) reconciliation of the 599-patient retention list ===')
print(f'  distinct patient IDs on the supplied list : {len(keep)}')
have_urine = keep & set(u.pid)
have_dose = keep & dpat
print(f'  ... with >=1 morphine urine record        : {len(have_urine)}')
print(f'  ... with >=1 daily-dose record            : {len(have_dose)}')
print(f'  ... with BOTH (= step-3 patient count)    : {len(have_urine & have_dose)}')
print(f'  no urine record at all                    : {len(keep - set(u.pid))}')
print(f'  urine record but no dose record           : {len(have_urine - dpat)}')

# ---------- (c) do the unlinked tests differ? ----------
print('\n=== (c) tests lost at the dosing-linkage step (1 -> 2) ===')
lk = u[u.pid.isin(dpat)]; un = u[~u.pid.isin(dpat)]
for nm, g in [('linked', lk), ('UNLINKED', un)]:
    tpp = g.groupby('pid').size()
    print(f'  {nm:9s} tests={len(g):6d} patients={g.pid.nunique():5d} '
          f'positive rate={g.positive.mean():.3f}  median tests/patient={tpp.median():.0f}')
from scipy.stats import chi2_contingency
ct = np.array([[int((lk.positive == 1).sum()), int((lk.positive == 0).sum())],
               [int((un.positive == 1).sum()), int((un.positive == 0).sum())]])
c2, p, _, _ = chi2_contingency(ct)
print(f'  chi2 = {c2:.1f}, p = {p:.3g}  (positivity linked vs unlinked)')
print(f'  absolute difference in positive rate: {lk.positive.mean() - un.positive.mean():+.3f}')

# ---------- (d) duplicate patient-days ----------
print('\n=== (d) duplicate patient-day urine records ===')
g = u.groupby(['pid', 'date'])
sz = g.size()
dupkeys = sz[sz > 1]
print(f'  patient-days with >1 record : {len(dupkeys)}  (excess records = {int((sz-1).sum())})')
nun = g.positive.nunique()
disc = nun[nun > 1]
print(f'  ... of which DISCORDANT (both a positive and a negative on the same day): {len(disc)}')
print(f'  ... concordant (identical result repeated)                              : {len(dupkeys)-len(disc)}')
print(f'  max records on one patient-day: {int(sz.max())}')
# how many of the excess records survive into the analysable window? approximate by the
# >=2y + dose-linked restriction
s3 = u[u.pid.isin(dpat) & u.pid.isin(keep)]
g3 = s3.groupby(['pid', 'date']); sz3 = g3.size()
n3 = g3.positive.nunique()
print(f'  within the step-3 sample ({len(s3)} tests): {int((sz3-1).sum())} excess records, '
      f'{int((n3>1).sum())} discordant patient-days')
print(f'  step-3 positive rate WITH duplicates    : {s3.positive.mean():.4f}')
ded3 = s3.sort_values("positive").drop_duplicates(['pid', 'date'], keep='last')
print(f'  step-3 positive rate DE-DUPLICATED      : {ded3.positive.mean():.4f}  (n={len(ded3)})')
