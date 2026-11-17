"""Read-only check: what does a nominal degree mean under each error model, and does the
white-versus-structured comparison survive when total RMS error is matched?"""
import os, sys, warnings
warnings.filterwarnings('ignore')
PROJ = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJ)
sys.argv = ['x']
import numpy as np, pandas as pd
from joblib import Parallel, delayed
import tolerance as T
V = T.V
MIX = T.MIX
K = float(np.sqrt(MIX['offset']**2 + MIX['drift']**2 + MIX['white']**2))


def err(kind, s, n, rng):
    if kind == 'white':
        return rng.normal(0, s, n)
    if kind == 'offset':
        return np.full(n, rng.normal(0, s))
    sc = s / K if kind == 'structured_matched' else s
    ph = rng.uniform(0, 2 * np.pi)
    return (rng.normal(0, sc * MIX['offset'])
            + sc * MIX['drift'] * np.sqrt(2) * np.sin(np.linspace(0, np.pi, n) + ph)
            + rng.normal(0, sc * MIX['white'], n))


def signals(tag, rng, kind, s):
    row = V.sig.loc[tag]
    out = {}
    for j in V.JOINTS:
        for side in ('l', 'r'):
            cols = [c for c in V.sig.columns if c.startswith(f'{j}_{side}_')]
            if cols:
                x = row[cols].to_numpy(float)
                out[(j, side)] = x + (err(kind, s, len(x), rng) if s > 0 else 0)
    return out


def feats(w):
    f = {}
    for j in V.JOINTS:
        if (j, 'l') not in w or (j, 'r') not in w:
            continue
        l, r = w[(j, 'l')], w[(j, 'r')]
        f[f'S::{j}_ROM_l'] = float(np.ptp(l)); f[f'S::{j}_min_l'] = float(l.min()); f[f'S::{j}_max_l'] = float(l.max())
        f[f'S::{j}_ROM_r'] = float(np.ptp(r)); f[f'S::{j}_min_r'] = float(r.min()); f[f'S::{j}_max_r'] = float(r.max())
        f[f'A::{j}_ROMd'] = float(np.ptp(l) - np.ptp(r))
        f[f'A::{j}_mind'] = float(l.min() - r.min())
        f[f'A::{j}_maxd'] = float(l.max() - r.max())
    return f


def build(kind, s, seed, n_rep=4):
    rng = np.random.default_rng(seed)
    rows = []
    for _, d in V.det.iterrows():
        tag = d['tag']
        if tag not in V.sig.index:
            continue
        fixed = {k: d[k] for k in V.det.columns if k.startswith(('C::', 'G::'))}
        for _ in range(n_rep):
            f = feats(signals(tag, rng, kind, s))
            rel = 0.015 * (s / 2.0) if s > 0 else 0.0
            f.update({k: float(v) * (1.0 + rng.normal(0, rel)) if rel else float(v) for k, v in fixed.items()})
            f['tag'] = tag; f['subj'] = d['subj']; f['mech'] = d['mech']; f['sev'] = int(d['sev'])
            rows.append(f)
    df = pd.DataFrame(rows)
    for m in V.M:
        df[f'is_{m}'] = (df.mech == m).astype(int)
    return df


def metrics(kind, s, nrep=40):
    rng = np.random.default_rng(7)
    tags = [t for t in V.det.tag if t in V.sig.index]
    wave, sd, bias, rmse = [], [], [], []
    for tag in tags:
        clean = signals(tag, rng, kind, 0)
        fc = feats(clean)
        keys = [k for k in fc if k.startswith('S::')]
        R = []
        for _ in range(nrep):
            w = signals(tag, rng, kind, s)
            wave.append(np.mean([np.mean((w[k] - clean[k])**2) for k in w]))
            f = feats(w)
            R.append([f[k] - fc[k] for k in keys])
        R = np.array(R)
        ext = np.array(['ROM' not in k for k in keys])
        sd.append((R[:, ext].std(0).mean(), R[:, ~ext].std(0).mean()))
        bias.append((np.abs(R[:, ext].mean(0)).mean(), np.abs(R[:, ~ext].mean(0)).mean()))
        rmse.append((np.sqrt((R[:, ext]**2).mean()), np.sqrt((R[:, ~ext]**2).mean())))
    a = lambda x: np.mean(x, axis=0)
    return (kind, s, float(np.sqrt(np.mean(wave))), *a(sd), *a(bias), *a(rmse))


def cell(kind, s, seed):
    df = build(kind, s, seed)
    lv = V.levels(df)
    a = T.evaluate(df, lv['L1  camera (sagittal + timing)'], seeds=2)[0]
    b = T.evaluate(df, lv['L2  camera + FORCE PLATE'], seeds=2)[0]
    return kind, s, seed, a, b


if __name__ == '__main__':
    print('K (structured RMS per nominal unit) = %.3f' % K, flush=True)
    print('kind, nominal, waveform RMS, SD extremum, SD ROM, |bias| extremum, |bias| ROM, RMSE extremum, RMSE ROM', flush=True)
    for kind in ('white', 'structured', 'structured_matched', 'offset'):
        for s in (2.0, 5.0, 8.0, 12.0):
            r = metrics(kind, s)
            print('%-19s %4.0f  ' % r[:2] + '  '.join('%6.2f' % x for x in r[2:]), flush=True)
    cells = [(k, s, sd) for k in ('white', 'structured', 'structured_matched', 'offset')
             for s in (2.0, 5.0, 8.0, 12.0) for sd in (0, 1, 2)]
    res = Parallel(n_jobs=4)(delayed(cell)(*c) for c in cells)
    d = pd.DataFrame(res, columns=['kind', 's', 'seed', 'cam', 'plate'])
    g = d.groupby(['kind', 's'])[['cam', 'plate']].agg(['mean', 'std']).round(3)
    print(g.to_string(), flush=True)
