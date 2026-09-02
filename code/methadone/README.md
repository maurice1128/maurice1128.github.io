# Methadone dose-trajectory analysis — code

Analysis code for a retrospective study of consumed methadone dose patterns around
randomly scheduled urine testing in a methadone maintenance programme (2018–2022).

**No patient data is included in this repository, and none will be.** See
*What is not here* below.

## Layout

```
scripts/     57 Python scripts, numbered in the order they were run
matlab/      35 MATLAB sources — the upstream pipeline that builds the
             57-day windows, the >=2-year cohort selection and the
             interpolation of non-attended days
results/     aggregate outputs only: cluster-level tables and summary JSON
figures/     the manuscript figures
```

Key entry points:

| file | what it does |
|---|---|
| `matlab/retrieve_raw_data.m` | selects the >=2-year retention cohort |
| `matlab/Index_ver2.m` | builds the daily series; linearly interpolates non-attended days |
| `scripts/36_final_combined.py` | canonical generator of the primary nine-cluster solution |
| `scripts/42_correct_imputation_free.py` | the genuinely interpolation-free subsets, from the `-1` markers |
| `scripts/46_audit_bootstrap_and_ci.py` | Jaccard-matched bootstrap (label switching must be handled first) |
| `scripts/49_confound_same_exposure.py` | prescribed-dose confounding, computed with the same algorithm as the exposure |
| `scripts/50_lrt_and_cluster_shape.py` | does cluster membership add over a single continuous slope? |

## Running

The scripts read a local data root. Nothing runs without it:

```bash
export MMT_DATA_ROOT=/path/to/your/data      # Windows: set MMT_DATA_ROOT=...
python scripts/36_final_combined.py
```

`MMT_DATA_ROOT` must contain `raw data/`, `code/` and `analysis/` in the original
layout. Those files stay on the study site.

## What is not here, and why

Excluded deliberately:

- **the raw clinical extracts** — daily dosing and urine results, one file of which
  carries patient names;
- **every `.mat` and `.parquet`** — these hold 57-day dose trajectories keyed to
  individual patients. In a single-site cohort of 552 people, a 57-day trajectory is
  close to a fingerprint, so releasing them is not de-identification;
- **`id_map.csv`** — the identifier crosswalk;
- a trained classifier checkpoint, which was fitted on those records.

Local absolute paths and one data-provider's name have been replaced with
`<LOCAL_DATA_PATH>`. `.gitignore` blocks the excluded file types so they cannot be
committed by accident.

Aggregate outputs in `results/` are cluster-level counts and summary statistics; the
smallest cell they report is a cluster, not a person.

## Provenance

Every table and figure in the manuscript names the script that generated it. Analyses
were run in Python 3.12; the upstream windows and interpolation were written by the
authors in MATLAB.

`scripts/36_final_combined.py` carries one repair relative to the working copy: a
newline escape inside a `print()` had been mangled into a literal line break, which
made the file fail to parse. Only that escape was restored; no logic was changed.
