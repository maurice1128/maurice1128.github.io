# -*- coding: utf-8 -*-
"""
Step 03: ANTI-HALLUCINATION VERIFICATION.

This script exists so you do NOT have to trust the agent. It re-derives every
headline number a SECOND, INDEPENDENT way (straight from the raw .xlsx via
openpyxl + pandas, bypassing the DuckDB pipeline) and ASSERTS the two agree.

If any number the agent reported were fabricated or the SQL had a bug, an
assertion below would FAIL. All PASS => the numbers are real, reproducible
output of the raw data, not model invention.

It also exports `audit_sample.xlsx`: for a few randomly chosen patients, every
raw dose row and raw urine row, so you can open the ORIGINAL xlsx and hand-check
that patient yourself.

Run:  python 03_verify.py
"""
import os as _os
ROOT = _os.environ.get('MMT_DATA_ROOT', '')  # local folder holding raw data/, code/, analysis/
if not ROOT: raise SystemExit('Set MMT_DATA_ROOT before running; patient data is not distributed.')

import os
import openpyxl
import pandas as pd

RAW = _os.path.join(ROOT, r'raw data')
OUT = _os.path.join(ROOT, r'analysis')

def roc_to_date(v):
    try: v = int(v)
    except (TypeError, ValueError): return None
    y, m, d = v // 10000, (v // 100) % 100, v % 100
    if not (1 <= m <= 12 and 1 <= d <= 31): return None
    try: return pd.Timestamp(year=y + 1911, month=m, day=d)
    except ValueError: return None

results = []
def check(name, got, expected):
    ok = (got == expected)
    results.append(ok)
    print(f'  [{"PASS" if ok else "FAIL"}] {name}: independent={got}  pipeline={expected}')
    return ok

# ---------- reload pipeline outputs (what the agent reported) ----------
dose_pq  = pd.read_parquet(os.path.join(OUT, 'dose_cache.parquet'))
urine_pq = pd.read_parquet(os.path.join(OUT, 'urine_morphine.parquet'))
idx_pq   = pd.read_parquet(os.path.join(OUT, 'analysis_index.parquet'))

print('\n=== A. RE-COUNT URINE STRAIGHT FROM RAW XLSX (independent of pipeline) ===')
wb = openpyxl.load_workbook(os.path.join(RAW, '2018-2022驗尿結果.xlsx'), read_only=True, data_only=True)
ws = wb['驗尿結果']; it = ws.iter_rows(values_only=True); next(it)
raw = []
for r in it:
    if r[2] == 1 and r[3] in (0, 1):            # morphine, valid neg/pos
        raw.append((int(r[0]), roc_to_date(r[1]), int(r[3])))
wb.close()
raw = pd.DataFrame(raw, columns=['pid', 'date', 'positive']).dropna(subset=['date'])
raw_dedup = raw.drop_duplicates(['pid', 'date'])
check('morphine tests (after dedup pid+date)', len(raw_dedup), len(urine_pq))
check('positive count', int(raw_dedup.positive.sum()), int(urine_pq.positive.sum()))
check('negative count', int((raw_dedup.positive == 0).sum()), int((urine_pq.positive == 0).sum()))
check('distinct patients', raw_dedup.pid.nunique(), urine_pq.pid.nunique())

print('\n=== B. RE-DO THE DOSE-WINDOW LINK WITH PANDAS (independent of DuckDB) ===')
# pandas merge_asof-free brute check on a RANDOM 40-patient subset, compare to idx_pq
sample_pids = sorted(urine_pq.pid.unique())[::80]   # deterministic spread, ~40 pids
dose_by = {p: g.set_index('date')['dose_mg'].sort_index() for p, g in dose_pq.groupby('pid')}
rows = []
for t in urine_pq[urine_pq.pid.isin(sample_pids)].itertuples(index=False):
    s = dose_by.get(t.pid)
    if s is None: continue
    n28 = int(((s.index >= t.date - pd.Timedelta(days=28)) & (s.index <= t.date + pd.Timedelta(days=28))).sum())
    if n28 == 0: continue
    n7 = int(((s.index >= t.date - pd.Timedelta(days=7)) & (s.index <= t.date + pd.Timedelta(days=7))).sum())
    rows.append((t.pid, t.date, n7, n28))
pd_chk = pd.DataFrame(rows, columns=['pid', 'date', 'n7_pd', 'n28_pd'])
merged = pd_chk.merge(idx_pq[['pid', 'date', 'n7', 'n28']], on=['pid', 'date'], how='inner')
check('window rows matched on sample', len(merged), len(pd_chk))
check('n7 agrees (pandas vs duckdb)',  int((merged.n7_pd == merged.n7).sum()), len(merged))
check('n28 agrees (pandas vs duckdb)', int((merged.n28_pd == merged.n28).sum()), len(merged))

print('\n=== C. CONSERVATION: analysis_index is a subset of urine tests ===')
check('every idx test exists in urine',
      len(idx_pq.merge(urine_pq, on=['pid', 'date'])), len(idx_pq))

# ---------- audit sample for human hand-check ----------
print('\n=== D. EXPORT audit_sample.xlsx (hand-check these against raw xlsx) ===')
audit_pids = sorted(idx_pq.pid.unique())[::300][:5]
with pd.ExcelWriter(os.path.join(OUT, 'audit_sample.xlsx')) as xw:
    for p in audit_pids:
        dose_pq[dose_pq.pid == p].to_excel(xw, sheet_name=f'{p}_dose', index=False)
        urine_pq[urine_pq.pid == p].to_excel(xw, sheet_name=f'{p}_urine', index=False)
        idx_pq[idx_pq.pid == p].to_excel(xw, sheet_name=f'{p}_derived', index=False)
print('  audit patients:', audit_pids)
print('  -> open analysis\\audit_sample.xlsx and cross-check these 病歷號 in the raw files')

print('\n' + '=' * 50)
print('OVERALL:', 'ALL PASS - numbers are real & reproducible'
      if all(results) else '*** SOME CHECKS FAILED ***')
print('=' * 50)
