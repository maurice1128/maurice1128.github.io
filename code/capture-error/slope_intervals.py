"""Does an interval separate the 2-5 deg loss rate from its neighbours?

Section 3.2 says the steepest per-degree loss falls inside the convention's own 2-5 deg band and
concludes the convention "locates correctly where accuracy is most sensitive". The four rates are
finite differences of five point estimates carrying no intervals, over unequal spans (2/3/3/4 deg)
whose edges are the convention's own boundaries. Three things therefore have to be measured:

  1. does a bootstrap interval on the CONTRAST between adjacent rates exclude zero, under both the
     condition unit and the body unit the paper argues for elsewhere;
  2. is the ordering stable at the study's own 1/n resolution floor;
  3. does it survive scoring one capture rather than the four the pipeline averages
     (single_capture.py).

Run:  python slope_intervals.py [n_seeds] [n_boot]
"""
import warnings; warnings.filterwarnings('ignore')
import os, sys, json
import numpy as np
import voi_analysis as V
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.multioutput import MultiOutputClassifier

HERE = os.path.dirname(os.path.abspath(__file__))
NSEED = int(sys.argv[1]) if len(sys.argv) > 1 else 8
NBOOT = int(sys.argv[2]) if len(sys.argv) > 2 else 4000
RNG = np.random.default_rng(0)
LEVELS = [0.0, 2.0, 5.0, 8.0, 12.0]
BANDS = [(0.0, 2.0), (2.0, 5.0), (5.0, 8.0), (8.0, 12.0)]


def per_condition(nz):
    df = V.build(n_rep=4, noise=nz, seed=0)
    for m in V.M:
        df[f'is_{m}'] = (df.mech == m).astype(int)
    cols = V.levels(df)['L1  camera (sagittal + timing)']
    acc = {}
    for sd in range(NSEED):
        for ho in sorted(df.subj.unique()):
            tr, te = df[df.subj != ho], df[df.subj == ho]
            if not len(tr) or not len(te):
                continue
            mdl = Pipeline([('imp', SimpleImputer(strategy='median')),
                            ('clf', MultiOutputClassifier(ExtraTreesClassifier(
                                100, random_state=sd, n_jobs=1, class_weight='balanced')))])
            mdl.fit(tr[cols].to_numpy(float), tr[[f'is_{x}' for x in V.M]].to_numpy(int))
            for tag in te.tag.unique():
                t = te[te.tag == tag]
                P = np.array([p[:, 1] if p.shape[1] == 2 else np.zeros(len(t))
                              for p in mdl.predict_proba(t[cols].to_numpy(float))]).T.mean(0)
                a = acc.setdefault(tag, [0, 0, str(t.subj.iloc[0])])
                a[0] += int(np.argsort(-P)[0] == V.M.index(t.mech.iloc[0]))
                a[1] += 1
    return {k: (v[0] / v[1], v[2]) for k, v in acc.items()}


def main():
    out = open(os.path.join(HERE, 'slope_intervals.txt'), 'w', encoding='utf-8')

    def say(m):
        print(m, flush=True); out.write(m + '\n'); out.flush()

    say('=== IS THE 2-5 DEG BAND SEPARABLY THE STEEPEST? ===')
    say(f'seeds {NSEED}, bootstrap draws {NBOOT}')
    say('')

    A = {nz: per_condition(nz) for nz in LEVELS}
    shared = sorted(set.intersection(*[set(A[nz]) for nz in LEVELS]))
    body = {t: A[0.0][t][1] for t in shared}
    bodies = sorted(set(body.values()))
    json.dump({t: [body[t]] + [A[nz][t][0] for nz in LEVELS] for t in shared},
              open(os.path.join(HERE, 'slope_percondition.json'), 'w'), indent=1)

    say(f'{"error":>7}{"accuracy":>11}   (must reproduce the reported curve)')
    lvl = {nz: np.mean([A[nz][t][0] for t in shared]) for nz in LEVELS}
    for nz in LEVELS:
        say(f'{nz:6.0f} {lvl[nz]:10.3f}')
    say('')

    rate = {b: (lvl[b[1]] - lvl[b[0]]) / (b[1] - b[0]) for b in BANDS}
    say(f'{"band":>10}{"loss per degree":>18}')
    for b in BANDS:
        say(f'{b[0]:4.0f}-{b[1]:<5.0f}{rate[b]:18.4f}')
    say('')

    def rates_from(tags):
        m = {nz: np.mean([A[nz][t][0] for t in tags]) for nz in LEVELS}
        return {b: (m[b[1]] - m[b[0]]) / (b[1] - b[0]) for b in BANDS}

    say('--- contrasts against the 2-5 deg band (negative = 2-5 deg is steeper) ---')
    say(f'{"contrast":22}{"observed":>10}{"95 % over conditions":>26}{"95 % over bodies":>24}')
    tgt = (2.0, 5.0)
    for b in [(0.0, 2.0), (5.0, 8.0), (8.0, 12.0)]:
        obs = rate[tgt] - rate[b]
        bc = []
        for _ in range(NBOOT):
            r = rates_from([shared[i] for i in RNG.integers(0, len(shared), len(shared))])
            bc.append(r[tgt] - r[b])
        cl, ch = np.percentile(bc, [2.5, 97.5])
        bb = []
        for _ in range(NBOOT):
            pick = [bodies[i] for i in RNG.integers(0, len(bodies), len(bodies))]
            tags = [t for p in pick for t in shared if body[t] == p]
            r = rates_from(tags)
            bb.append(r[tgt] - r[b])
        bl, bh = np.percentile(bb, [2.5, 97.5])
        say(f'  2-5 vs {b[0]:.0f}-{b[1]:<5.0f}{"":4}{obs:+10.4f}   [{cl:+.4f}, {ch:+.4f}] {"YES" if cl > 0 or ch < 0 else "no ":>4}'
            f'   [{bl:+.4f}, {bh:+.4f}] {"YES" if bl > 0 or bh < 0 else "no "}')
    say('')
    say('READING: the sentence "the steepest degradation falls inside the 2-5 deg band" is a')
    say('statement about point estimates and is true as such. The sentence that follows it - that')
    say('the convention therefore LOCATES CORRECTLY where accuracy is most sensitive - is a claim')
    say('that the 2-5 deg rate differs from its neighbours, and it needs these intervals. Where')
    say('they include zero, that step is not licensed and the observation must stand alone.')
    out.close()


if __name__ == '__main__':
    main()
