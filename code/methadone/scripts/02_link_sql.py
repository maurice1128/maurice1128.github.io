# -*- coding: utf-8 -*-
"""
Step 02: Link urine tests to dose windows using DuckDB SQL (fast range join).
Reads the parquet caches produced by step 01. Writes analysis_index.parquet.
"""
import os as _os
ROOT = _os.environ.get('MMT_DATA_ROOT', '')  # local folder holding raw data/, code/, analysis/
if not ROOT: raise SystemExit('Set MMT_DATA_ROOT before running; patient data is not distributed.')

import os, hashlib
import duckdb

OUT = _os.path.join(ROOT, r'analysis')
con = duckdb.connect()
con.execute(f"CREATE VIEW dose  AS SELECT * FROM read_parquet('{OUT}\\dose_cache.parquet')")
con.execute(f"CREATE VIEW urine AS SELECT * FROM read_parquet('{OUT}\\urine_morphine.parquet')")

def q(sql): return con.execute(sql).fetchall()

print('=== RAW COUNTS ===')
print('dose rows      :', q("SELECT count(*), count(DISTINCT pid) FROM dose")[0])
print('urine morphine :', q("SELECT count(*), count(DISTINCT pid) FROM urine")[0])
print('  pos/neg      :', q("SELECT sum(positive), sum(1-positive) FROM urine")[0])

# range join: dose days within +/-28d of each test (covers +/-7 too)
con.execute("""
CREATE TABLE idx AS
SELECT u.pid, u.date, u.positive,
       count(*) FILTER (WHERE d.date BETWEEN u.date - INTERVAL 7  DAY AND u.date + INTERVAL 7  DAY) AS n7,
       count(*) FILTER (WHERE d.date BETWEEN u.date - INTERVAL 28 DAY AND u.date + INTERVAL 28 DAY) AS n28,
       max(d.dose_mg) FILTER (WHERE d.date = u.date - INTERVAL 7 DAY) AS dose_m7
FROM urine u
JOIN dose d
  ON u.pid = d.pid
 AND d.date BETWEEN u.date - INTERVAL 28 DAY AND u.date + INTERVAL 28 DAY
GROUP BY u.pid, u.date, u.positive
""")

print('\n=== ANALYSIS-READY (tests that have ANY dose within +/-28d) ===')
print('tests / patients :', q("SELECT count(*), count(DISTINCT pid) FROM idx")[0])
print('  pos / neg      :', q("SELECT sum(positive), sum(1-positive) FROM idx")[0])
print('>=8 dose days in +/-7d  :',
      q("SELECT count(*), sum(positive), sum(1-positive) FROM idx WHERE n7 >= 8")[0])
print('>=20 dose days in +/-28d:',
      q("SELECT count(*), sum(positive), sum(1-positive) FROM idx WHERE n28 >= 20")[0])
print('tests/patient distribution (how many tests per patient):')
for row in q("""SELECT n_tests, count(*) AS n_patients FROM
                (SELECT pid, count(*) n_tests FROM idx GROUP BY pid)
                GROUP BY n_tests ORDER BY n_tests LIMIT 15"""):
    print('   tests/patient=%2d : %d patients' % row)

# de-identified export
con.execute("""
CREATE TABLE idx_out AS
SELECT printf('%x', hash(pid || 'methadone')) AS pid_hash,
       pid, date, positive, n7, n28, dose_m7 FROM idx
""")
con.execute(f"COPY idx_out TO '{OUT}\\analysis_index.parquet' (FORMAT parquet)")
print('\nsaved analysis_index.parquet')
con.close()
