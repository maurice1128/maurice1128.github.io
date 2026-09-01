"""Is the tolerance curve driven by biomechanics, or by how deeply each body's optimiser ran?

Analysed optimisation depth differs sharply by body — base has a median analysed generation of 272
(range 17-1469) and s4 at 247 (90-325), while s1/s2/s3 sit at 79-80 — and body is the
leave-one-body-out grouping factor. NOTE: two bodies are deeply optimised, not one.
So "which body is held out" is partly "how long the optimiser ran", a confound the design never
intended. This decides whether that confound drives the result.

Three tests, cheapest first:

  A  Does analysed convergence depth predict the label at all? If a classifier given ONLY the
     generation and objective can identify the weak muscle group, depth carries label information
     and the confound is live.
  B  Does the tolerance curve survive removing the deeply optimised bodies (base, and base+s4)?
     a narrow range. If the shape holds on those four alone, depth is not driving it.
  C  Is depth correlated with the features that carry the signal? A high correlation between
     generation and the A:: asymmetry summaries would mean the signal itself is contaminated.

Run:  python confound_test.py
"""
import warnings; warnings.filterwarnings('ignore')
import os, re, glob, numpy as np, pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.multioutput import MultiOutputClassifier
from scipy.stats import spearmanr

import voi_analysis as V

HERE = os.path.dirname(os.path.abspath(__file__))
import os as _os
_FROZEN = r'C:\Users\maurice\Desktop\stroke_scone\results_frozen'
RES = _FROZEN if _os.path.isdir(_FROZEN) else r'C:\Users\maurice\Documents\SCONE\results'
LEVELS = [0.0, 2.0, 5.0, 8.0, 12.0]


def analysed_depth():
    """generation and objective of the solution that was ACTUALLY evaluated into qc.sto."""
    acc = set(open(os.path.join(HERE, 'qc_accepted.txt')).read().split())
    out = {}
    for d in glob.glob(os.path.join(RES, '*.I')):
        tag = os.path.basename(d).split('.')[0]
        if tag not in acc:
            continue
        sto = os.path.join(d, 'qc.sto.sto')
        if not os.path.exists(sto):
            continue
        tsto = os.path.getmtime(sto)
        P = []
        for p in glob.glob(os.path.join(d, '*.par')):
            m = re.match(r'^(\d+)_([\d.]+)_([\d.]+)\.par$', os.path.basename(p))
            if m and os.path.getmtime(p) <= tsto:
                P.append((float(m.group(3)), int(m.group(1))))
        if P:
            obj, gen = min(P)
            out[tag] = (gen, obj)
    return out


def loso(df, cols, bodies=None, seeds=4):
    d = df if bodies is None else df[df.subj.isin(bodies)]
    subs = sorted(d.subj.unique())
    t1s = []
    for sd in range(seeds):
        c = n = 0
        for ho in subs:
            tr, te = d[d.subj != ho], d[d.subj == ho]
            if not len(tr) or not len(te):
                continue
            Y = tr[[f'is_{m}' for m in V.M]].to_numpy(int)
            mdl = Pipeline([('imp', SimpleImputer(strategy='median')),
                            ('clf', MultiOutputClassifier(ExtraTreesClassifier(
                                100, random_state=sd, n_jobs=1, class_weight='balanced')))])
            mdl.fit(tr[cols].to_numpy(float), Y)
            for tag in te.tag.unique():
                t = te[te.tag == tag]
                P = np.array([p[:, 1] if p.shape[1] == 2 else np.zeros(len(t))
                              for p in mdl.predict_proba(t[cols].to_numpy(float))]).T.mean(0)
                n += 1
                c += int(np.argsort(-P)[0] == V.M.index(t.mech.iloc[0]))
        if n:
            t1s.append(c / n)
    return (float(np.mean(t1s)), float(np.std(t1s))) if t1s else (float('nan'), float('nan'))


def main():
    out = open(os.path.join(HERE, 'confound_test.txt'), 'w')

    def say(m):
        print(m, flush=True); out.write(m + '\n'); out.flush()

    depth = analysed_depth()
    say('=== IS THE RESULT DRIVEN BY OPTIMISATION DEPTH RATHER THAN BIOMECHANICS? ===')
    say(f'conditions with a recoverable analysed solution: {len(depth)}')
    by = {}
    for tag, (g, o) in depth.items():
        b = re.match(r'^(s\d)?', tag).group(1) or 'base'
        by.setdefault(b, []).append(g)
    for b in sorted(by):
        v = sorted(by[b])
        say(f'  {b:5} n={len(v):3}  median gen {int(np.median(v)):6}  range {min(v)}-{max(v)}')
    say('')

    df = V.build(n_rep=4, noise=2.0, seed=0)
    for m in V.M:
        df[f'is_{m}'] = (df.mech == m).astype(int)
    df['gen'] = df.tag.map(lambda t: depth.get(t, (np.nan, np.nan))[0])
    df['obj'] = df.tag.map(lambda t: depth.get(t, (np.nan, np.nan))[1])

    # ---- TEST A: can depth alone identify the weak group? -----------------------------------
    say('=== TEST A: classifier given ONLY convergence metadata (gen, obj) ===')
    a1, asd = loso(df.dropna(subset=['gen', 'obj']), ['gen', 'obj'])
    say(f'  top-1 = {a1:.3f} +- {asd:.3f}   (chance 0.200, majority class ~0.227)')
    say('  ' + ('*** ABOVE CHANCE: depth carries label information, the confound is LIVE ***'
                if a1 > 0.30 else 'at or near chance -> depth alone does not identify the group'))
    say('')

    # ---- TEST C: is depth correlated with the signal-carrying features? ----------------------
    say('=== TEST C: correlation between analysed generation and the asymmetry features ===')
    sub = df.dropna(subset=['gen']).groupby('tag').first().reset_index()
    acols = [c for c in df.columns if c.startswith('A::')]
    rows = []
    for c in acols:
        r, p = spearmanr(sub['gen'], sub[c])
        rows.append((abs(r), r, p, c))
    rows.sort(reverse=True)
    for ar, r, p, c in rows[:6]:
        say(f'  {c:28} rho vs analysed gen = {r:+.3f}  (p={p:.3f})')
    say(f'  largest |rho| among asymmetry features: {rows[0][0]:.3f}')
    say('  ' + ('*** a feature is strongly tied to depth ***' if rows[0][0] > 0.5
                else 'no asymmetry feature is strongly tied to depth'))
    say('')

    # ---- TEST B: does the curve survive dropping the deeply optimised bodies? ----------------
    say('=== TEST B: tolerance curve WITHOUT base (base and s4 are the deeply optimised ones) ===')
    say(f'{"error":>7}{"all 5 bodies":>16}{"without base":>16}{"difference":>13}')
    K1 = 'L1  camera (sagittal + timing)'
    for nz in LEVELS:
        d = V.build(n_rep=4, noise=nz, seed=0)
        for m in V.M:
            d[f'is_{m}'] = (d.mech == m).astype(int)
        cols = V.levels(d)[K1]
        full, fsd = loso(d, cols)
        nb, nbsd = loso(d, cols, bodies=['s1', 's2', 's3', 's4'])
        say(f'{nz:7.1f}{full:10.3f}+-{fsd:.3f}{nb:10.3f}+-{nbsd:.3f}{nb-full:+13.3f}')
    say('')
    say('READING: if the "without base" column shows the same downward shape, the tolerance result')
    say('is not an artefact of the deeply optimised bodies (base, s4) driving it. If it goes')
    say('flat, part of the curve was convergence depth and the claim must be withdrawn.')
    out.close()


if __name__ == '__main__':
    main()
