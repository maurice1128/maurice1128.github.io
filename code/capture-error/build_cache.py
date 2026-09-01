"""Parse every accepted condition ONCE and cache its features to disk.

Parsing the SCONE .sto files (420 columns x ~1000 rows, pure-Python float parsing) dominates the
runtime of every analysis and has been re-done from scratch on each run. This script does it once
and writes features.csv, so downstream analyses load in seconds.

Writes progress to stdout AND to build_cache.log so it is observable while running.
"""
import warnings; warnings.filterwarnings('ignore')
import glob, os, re, sys, time
import numpy as np, pandas as pd
import scone_ident as si
import deployment_levels as dl

import os as _os
_FROZEN = r'C:\Users\maurice\Desktop\stroke_scone\results_frozen'
RES = _FROZEN if _os.path.isdir(_FROZEN) else r'C:\Users\maurice\Documents\SCONE\results'
HERE = os.path.dirname(os.path.abspath(__file__))
LOG = open(os.path.join(HERE, 'build_cache.log'), 'w')


def say(m):
    print(m, flush=True)
    LOG.write(m + '\n'); LOG.flush()


def main():
    qa = os.path.join(HERE, 'qc_accepted.txt')
    accepted = set(open(qa).read().split()) if os.path.exists(qa) else None
    say(f'QC-accepted conditions: {len(accepted) if accepted else "ALL (no gate file)"}')

    rows = []
    folders = sorted(glob.glob(os.path.join(RES, '*.I')))
    t0 = time.time()
    for k, folder in enumerate(folders):
        tag = os.path.basename(folder).split('.')[0]
        m = re.match(r'^(s\d)?(PF|DF|KE|KF|HF)(\d+)L$', tag)
        if not m:
            continue
        if accepted is not None and tag not in accepted:
            continue
        stos = glob.glob(os.path.join(folder, 'qc.sto*'))
        if not stos:
            say(f'  {tag}: no qc.sto, skipped'); continue
        try:
            cols, d = si.load_sto(stos[0])
        except Exception as e:
            say(f'  {tag}: parse failed ({e})'); continue
        s = int(len(d) * 0.4)
        base = dict(tag=tag, subj=m.group(1) or 'base', mech=m.group(2), sev=int(m.group(3)))
        # deterministic (noise-free) parts: spatiotemporal + force plate
        st = dl.spatiotemporal(cols, d, s)
        gr = dl.grf_features(cols, d, s)
        # store the raw steady-state joint signals so noise can be re-applied cheaply later
        raw = {}
        for j in si.JOINTS:
            for side in ('l', 'r'):
                v = si.ang(cols, d, j, side)
                if v is not None:
                    raw[f'{j}_{side}'] = v[s:]
        rec = dict(base); rec.update(st); rec.update(gr)
        rows.append((rec, raw))
        say(f'  [{k+1}/{len(folders)}] {tag}: {len(st)} timing + {len(gr)} GRF features  ({time.time()-t0:.0f}s)')

    say(f'parsed {len(rows)} conditions in {time.time()-t0:.0f}s')

    # save deterministic feature table
    det = pd.DataFrame([r for r, _ in rows])
    det.to_csv(os.path.join(HERE, 'features_det.csv'), index=False)
    say(f'wrote features_det.csv  shape={det.shape}')

    # save the raw steady-state signals (resampled to a fixed length) for noise re-application
    NP = 200
    raw_rows = []
    for rec, raw in rows:
        rr = {'tag': rec['tag']}
        for k2, v in raw.items():
            x = np.interp(np.linspace(0, 1, NP), np.linspace(0, 1, len(v)), v)
            for i, val in enumerate(x):
                rr[f'{k2}_{i:03d}'] = float(val)
        raw_rows.append(rr)
    pd.DataFrame(raw_rows).to_csv(os.path.join(HERE, 'signals_raw.csv'), index=False)
    say(f'wrote signals_raw.csv  ({len(raw_rows)} conditions x {NP} samples/joint)')
    say('DONE')


if __name__ == '__main__':
    main()
