"""The three items a reviewer asked for that are detail rather than correctness.

  A  Is the unimpaired simulated gait human? Speed, cadence, stride length and peak joint angles
     against published normative bands. Every downstream claim assumes the baseline walks like a
     person, and nothing in the submission lets a reader check it.
  B  How many features, and what were the classifier settings? Never stated anywhere, so overfitting
     cannot be assessed.
  C  Confidence intervals on the severity table, which carries the paper's clinical claim and was
     the only headline reported bare.

Run:  python remaining_checks.py
"""
import warnings; warnings.filterwarnings('ignore')
import os, re, glob, numpy as np, pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.multioutput import MultiOutputClassifier

import voi_analysis as V

HERE = os.path.dirname(os.path.abspath(__file__))
import os as _os
_FROZEN = r'C:\Users\maurice\Desktop\stroke_scone\results_frozen'
RES = _FROZEN if _os.path.isdir(_FROZEN) else r'C:\Users\maurice\Documents\SCONE\results'
NSEED, NBOOT = 8, 4000

# Published normative bands for healthy adult walking at self-selected speed. Sources are given in
# the supplement; ranges rather than point values because they genuinely differ between cohorts.
NORM = {
    'speed (m/s)':            (1.20, 1.45, 'self-selected, healthy adults'),
    'cadence (steps/min)':    (100,  125,  'healthy adults'),
    'stride length (m)':      (1.30, 1.60, 'healthy adults'),
    'hip ROM (deg)':          (40,   50,   'Kwon 2015; Jiang 2025; Bak 2025'),
    'knee peak flexion (deg)': (54,  64,   'Kwon 2015; Patathong 2023 (n=98) 63.7 +- 4.5'),
    'ankle ROM (deg)':        (22,   29,   'Jiang 2025; Bak 2025'),
}


def read_sto(path):
    with open(path, encoding='utf-8', errors='replace') as f:
        for line in f:
            if line.strip().lower() == 'endheader':
                break
        cols = f.readline().split()
        data = np.array([[float(x) for x in ln.split()] for ln in f if ln.strip()])
    return cols, data


def col(cols, d, name):
    return d[:, cols.index(name)] if name in cols else None


def main():
    out = open(os.path.join(HERE, 'remaining_checks.txt'), 'w')

    def say(m):
        print(m, flush=True); out.write(m + '\n'); out.flush()

    # ================= A. is the baseline gait human? =========================================
    say('=== A. IS THE UNIMPAIRED SIMULATED GAIT HUMAN? ===')
    say('Measured on the UNIMPAIRED base model - the healthy solution every weakened condition was')
    say('warm-started from - over the steady-state window. An earlier version measured the mildest')
    say('weakened condition instead, which is not the same object and gave a slower speed.')
    say('')
    cand = [d for d in glob.glob(os.path.join(RES, 'HEALTHY.H0914M*.I'))
            if os.path.exists(os.path.join(d, 'hq.sto.sto'))]
    if not cand:
        say('  no baseline trajectory available')
    else:
        cols, d = read_sto(os.path.join(cand[0], 'hq.sto.sto'))
        t = d[:, 0]
        s = int(len(t) * 0.4)                       # steady-state window
        px = col(cols, d, '/jointset/ground_pelvis/pelvis_tx/value')
        meas = {}
        if px is not None:
            meas['speed (m/s)'] = (px[-1] - px[s]) / (t[-1] - t[s])
        # foot contacts from vertical GRF give cadence and stride length
        gy = col(cols, d, 'leg0_l.grf_norm_y')
        if gy is None:
            gy = col(cols, d, 'leg0_l.grf_y')
        if gy is not None:
            contact = gy[s:] > 0.05
            on = np.where(np.diff(contact.astype(int)) == 1)[0]
            if len(on) > 1:
                stride = np.median(np.diff(t[s:][on]))
                meas['cadence (steps/min)'] = 2 * 60.0 / stride
                if 'speed (m/s)' in meas:
                    meas['stride length (m)'] = meas['speed (m/s)'] * stride
        for nm, key in (('hip ROM (deg)', '/jointset/hip_l/hip_flexion_l/value'),
                        ('ankle ROM (deg)', '/jointset/ankle_l/ankle_angle_l/value')):
            v = col(cols, d, key)
            if v is not None:
                meas[nm] = float(np.ptp(np.degrees(v[s:]))) if abs(v[s:]).max() < 7 else float(np.ptp(v[s:]))
        kv = col(cols, d, '/jointset/knee_l/knee_angle_l/value')
        if kv is not None:
            kk = np.degrees(kv[s:]) if abs(kv[s:]).max() < 7 else kv[s:]
            meas['knee peak flexion (deg)'] = float(abs(kk.min()))

        say(f'{"measure":>26}{"simulated":>12}{"normative":>16}   verdict')
        for k, (lo, hi, src) in NORM.items():
            if k not in meas:
                say(f'{k:>26}{"n/a":>12}{f"{lo}-{hi}":>16}   not extractable')
                continue
            v = meas[k]
            ok = 'within band' if lo <= v <= hi else ('BELOW' if v < lo else 'ABOVE')
            say(f'{k:>26}{v:12.2f}{f"{lo}-{hi}":>16}   {ok}')
        say('')
        say('  Sources for the bands are listed in the supplement. A value outside a band is not')
        say('  automatically a defect - a planar reflex walker is not a person - but it must be')
        say('  reported, because every downstream claim assumes this gait is a reasonable stand-in.')

    # ================= B. features and classifier settings ====================================
    say('')
    say('=== B. FEATURE COUNT AND CLASSIFIER SETTINGS ===')
    df = V.build(n_rep=4, noise=2.0, seed=0)
    for m in V.M:
        df[f'is_{m}'] = (df.mech == m).astype(int)
    lv = V.levels(df)
    for name, cols_ in lv.items():
        say(f'  {name:38} {len(cols_):3} features')
    S = [c for c in df.columns if c.startswith('S::')]
    A = [c for c in df.columns if c.startswith('A::')]
    C = [c for c in df.columns if c.startswith('C::')]
    G = [c for c in df.columns if c.startswith('G::')]
    say('')
    say(f'  before the objective-term exclusion: S {len(S)}, A {len(A)}, C {len(C)}, G {len(G)}'
        f'  (total {len(S)+len(A)+len(C)+len(G)})')
    say(f'  excluded by rule: {len([c for c in S+A+C+G if c not in V._clean(S+A+C+G)])}')
    say('')
    say('  classifier: ExtraTreesClassifier, 100 trees, class_weight="balanced", all other')
    say('              scikit-learn defaults (no max_depth, no min_samples_leaf tuning)')
    say('  wrapper   : MultiOutputClassifier, one binary tree ensemble per muscle group, ranked by')
    say('              predicted probability')
    say('  imputation: median, fitted on training folds only')
    say('  NO hyperparameter tuning was performed, so there is no inner selection loop and no')
    say('  opportunity for selection bias through tuning; the cost is that the settings are not')
    say('  optimal for any tier and the comparison between tiers is like-for-like.')
    say(f'  training set size per fold: {df.tag.nunique()} conditions x 4 noise replicates,')
    say(f'  minus one held-out body.')

    # ================= C. confidence intervals on the severity table ==========================
    say('')
    say('=== C. CONFIDENCE INTERVALS ON THE SEVERITY RESULT ===')
    say('Bootstrap over conditions within each severity, 4000 resamples, 8 classifier seeds.')
    say('')
    say(f'{"error":>6}{"severity":>10}{"top-1":>9}{"95% CI":>20}{"n":>5}')
    rng = np.random.default_rng(0)
    for nz in (2.0, 8.0):
        d2 = V.build(n_rep=4, noise=nz, seed=0)
        for m in V.M:
            d2[f'is_{m}'] = (d2.mech == m).astype(int)
        cols_ = V.levels(d2)['L1  camera (sagittal + timing)']
        acc = {}
        subs = sorted(d2.subj.unique())
        for sd in range(NSEED):
            for ho in subs:
                tr, te = d2[d2.subj != ho], d2[d2.subj == ho]
                if not len(tr) or not len(te):
                    continue
                Y = tr[[f'is_{m}' for m in V.M]].to_numpy(int)
                mdl = Pipeline([('imp', SimpleImputer(strategy='median')),
                                ('clf', MultiOutputClassifier(ExtraTreesClassifier(
                                    100, random_state=sd, n_jobs=1, class_weight='balanced')))])
                mdl.fit(tr[cols_].to_numpy(float), Y)
                for tag in te.tag.unique():
                    tt = te[te.tag == tag]
                    P = np.array([p[:, 1] if p.shape[1] == 2 else np.zeros(len(tt))
                                  for p in mdl.predict_proba(tt[cols_].to_numpy(float))]).T.mean(0)
                    a = acc.setdefault(tag, [0, 0, int(tt.sev.iloc[0])])
                    a[0] += int(np.argsort(-P)[0] == V.M.index(tt.mech.iloc[0])); a[1] += 1
        for sev in (20, 40, 60):
            v = np.array([x[0] / x[1] for x in acc.values() if x[2] == sev])
            if not len(v):
                continue
            boot = np.array([v[rng.integers(0, len(v), len(v))].mean() for _ in range(NBOOT)])
            lo, hi = np.percentile(boot, [2.5, 97.5])
            say(f'{nz:6.0f}{sev:9} %{v.mean():9.3f}   [{lo:.3f}, {hi:.3f}]{len(v):5}')
    say('')
    say('  These intervals describe sampling of conditions only. They do not include the')
    say('  across-rebuild variation reported in S4, which for mild weakness at 2 deg spans')
    say('  0.61 to 0.80 and is the larger source of uncertainty.')
    out.close()


if __name__ == '__main__':
    main()
