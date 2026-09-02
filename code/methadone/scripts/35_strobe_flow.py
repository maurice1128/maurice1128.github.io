# -*- coding: utf-8 -*-
"""STROBE participant flow: morphine urine tests -> analysable tests.

Reconstructs the funnel from the raw urine + daily-dose spreadsheets, following
the SAME rules the collaborator's MATLAB pipeline applied when it built
aim2.mat (the file every downstream analysis reads).  Every step is asserted
against the actual aim2.mat row counts; the script fails loudly if it drifts.

  step 1  morphine urine test RECORDS, 2018-2022 (the pipeline did not
          de-duplicate same-day repeat records; the de-duplicated count is
          reported alongside)
  step 2  records from patients present in the daily-dose extract
  step 3  RETENTION RESTRICTION: retrieve_raw_data.m line 468 runs the whole
          pipeline only on an externally supplied list of patients retained in
          MMT for >= 2 years (raw data/2年以上維持治療者_599人.xlsx)
  step 4  DATA SUFFICIENCY: retrieve_raw_data.m builds a fixed 57-day window
          (day -28 .. +28) per test, coding non-attended days -1; Index_ver2.m
          linearly interpolates those days and drops any test whose window is
          still all -1 afterwards, i.e. no observed dose day anywhere in it.

Also reports an included-vs-excluded comparison at the retention restriction.
"""
import os as _os
ROOT = _os.environ.get('MMT_DATA_ROOT', '')  # local folder holding raw data/, code/, analysis/
if not ROOT: raise SystemExit('Set MMT_DATA_ROOT before running; patient data is not distributed.')

import pandas as pd, numpy as np, os, openpyxl, h5py

AN = _os.path.join(ROOT, r'analysis')
RAW = _os.path.join(ROOT, r'raw data')
MAT = _os.path.join(ROOT, r'code\including_False_N_splitdata_testingvalidating\aim2.mat')

def roc2date(v):
    try: v = int(v)
    except (TypeError, ValueError): return None
    y, m, d = v // 10000, (v // 100) % 100, v % 100
    if not (1 <= m <= 12 and 1 <= d <= 31): return None
    try: return pd.Timestamp(year=y + 1911, month=m, day=d)
    except ValueError: return None

# ---- step 1: raw morphine records, as the MATLAB read them (no de-duplication) ----
wb = openpyxl.load_workbook(os.path.join(RAW, '2018-2022驗尿結果.xlsx'), read_only=True, data_only=True)
ws = wb['驗尿結果']; it = ws.iter_rows(values_only=True); next(it)
recs = []
for r in it:
    if r[2] == 1 and r[3] in (0, 1):
        d = roc2date(r[1])
        if d is not None: recs.append((int(r[0]), d, int(r[3])))
wb.close()
u = pd.DataFrame(recs, columns=['pid', 'date', 'positive'])
ded = u.drop_duplicates(['pid', 'date'])

print('=== STROBE participant flow (morphine urine tests) ===')
print(f'1. Morphine urine test records, 2018-2022: {len(u)}  ({u.pid.nunique()} patients)')
print(f'   positive={int((u.positive==1).sum())}, negative={int((u.positive==0).sum())}')
print(f'   [{len(u)-len(ded)} of these are repeat records for the same patient-day; the pipeline')
print(f'    retained them, so the de-duplicated test count is {len(ded)}]')

dose = pd.read_parquet(os.path.join(AN, 'dose_cache.parquet'))
dpat = set(dose.pid.unique())
s2 = u[u.pid.isin(dpat)]
print(f'2. From patients present in the daily methadone extract: {len(s2)}  ({s2.pid.nunique()} patients)')
print(f'   excluded 1->2 (no dosing record for that patient): {len(u)-len(s2)}')

# ---- step 3: >= 2-year retention list actually used by retrieve_raw_data.m ----
wb = openpyxl.load_workbook(os.path.join(RAW, '2年以上維持治療者_599人.xlsx'), read_only=True, data_only=True)
ws = wb.active; it = ws.iter_rows(values_only=True); next(it)
keep = set()
for r in it:
    if r[0] is not None:
        try: keep.add(int(r[0]))
        except (TypeError, ValueError): pass
wb.close()
print(f'   [>= 2-year retention list supplied by the programme: {len(keep)} patients]')
s3 = s2[s2.pid.isin(keep)]
print(f'3. Restricted to patients retained in MMT >= 2 years: {len(s3)}  ({s3.pid.nunique()} patients)')
print(f'   positive={int((s3.positive==1).sum())}, negative={int((s3.positive==0).sum())}')
print(f'   excluded 2->3 (not on the >=2-year retention list): {len(s2)-len(s3)}')

# ---- step 4: the +-28-day window must contain at least one observed dose day ----
dby = {p: np.sort(g.date.values) for p, g in dose.groupby('pid')}
def has_any(pid, d):
    a = dby.get(pid)
    if a is None: return False
    d = np.datetime64(d)
    return int(((a >= d - np.timedelta64(28, 'D')) & (a <= d + np.timedelta64(28, 'D'))).sum()) > 0
mask = np.array([has_any(r.pid, r.date) for r in s3.itertuples()])
s4 = s3[mask]
print(f'4. With >= 1 attended (dosed) day inside the +-28-day window: {len(s4)}  ({s4.pid.nunique()} patients)')
print(f'   positive={int((s4.positive==1).sum())}, negative={int((s4.positive==0).sum())}')
print(f'   excluded 3->4 (no observed dose day in the window): {len(s3)-len(s4)}')

# ---- assert against the actual aim2.mat contents ----
f = h5py.File(MAT, 'r')
cells = lambda n: [np.array(f[r]) for r in np.array(f[n]).ravel()]
pre = cells('All'); post = cells('All_fill')
n_pre_pos, n_pre_neg = pre[0].shape[1], pre[2].shape[1]
n_pos, n_neg = post[0].shape[1], post[2].shape[1]
hdr = cells('All_fill_header')
pidp = np.array(hdr[0]).ravel().astype(int); pidn = np.array(hdr[2]).ravel().astype(int)
print('\n=== cross-check against aim2.mat (the file every analysis reads) ===')
print(f'   windows built by retrieve_raw_data.m  : {n_pre_pos} pos + {n_pre_neg} neg = {n_pre_pos+n_pre_neg}')
print(f'   dropped by Index_ver2.m (window all -1): {n_pre_pos-n_pos} pos + {n_pre_neg-n_neg} neg = {(n_pre_pos-n_pos)+(n_pre_neg-n_neg)}')
print(f'   ANALYSABLE SAMPLE                     : {n_pos} pos + {n_neg} neg = {n_pos+n_neg}')
print(f'   unique patients: positives {len(set(pidp))}, negatives {len(set(pidn))}, '
      f'contributing both {len(set(pidp)&set(pidn))}, ANY {len(set(pidp)|set(pidn))}')

assert (n_pos, n_neg) == (3401, 6499), f'aim2 sample changed: {n_pos}/{n_neg}'
assert len(s3) == n_pre_pos + n_pre_neg, f'step3 {len(s3)} != MATLAB windows {n_pre_pos+n_pre_neg}'
assert (int((s3.positive == 1).sum()), int((s3.positive == 0).sum())) == (n_pre_pos, n_pre_neg)
assert len(s4) == n_pos + n_neg, f'step4 {len(s4)} != analysable {n_pos+n_neg}'
assert (int((s4.positive == 1).sum()), int((s4.positive == 0).sum())) == (n_pos, n_neg)
assert s4.pid.nunique() == len(set(pidp) | set(pidn))
print('   ALL ASSERTIONS PASSED: this funnel reproduces the analysable sample exactly.')

# ---- included vs excluded at the retention restriction (step 2 -> 3) ----
print('\n=== included vs excluded at the >= 2-year retention restriction ===')
inc = s3; exc = s2[~s2.pid.isin(keep)]
for grp, nm in [(inc, 'included (>=2 y)'), (exc, 'excluded (<2 y)')]:
    tpp = grp.groupby('pid').size()
    a = []
    for r in grp.itertuples():
        arr = dby.get(r.pid)
        if arr is None: continue
        d = np.datetime64(r.date)
        a.append(int(((arr >= d - np.timedelta64(7, 'D')) & (arr < d)).sum()) / 7.0)
    a = np.array(a)
    print(f'  {nm:18s} tests={len(grp):6d} patients={grp.pid.nunique():5d} '
          f'positive rate={float((grp.positive==1).mean()):.3f}  '
          f'median tests/patient={tpp.median():.0f}  mean pre-test attendance={a.mean():.3f}')
print('  -> reported so readers can judge the direction of the selection; no reweighting was applied.')
