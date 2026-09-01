"""Does the kinetics result survive a bootstrap that respects the study's cluster structure?

The 66 conditions are not 66 independent units. They come from five simulated bodies, and the body
is also the cross-validation fold, so conditions within a body share a model, a controller and a
held-out fold. Resampling conditions independently - which is what the reported intervals do -
assumes an independence the design does not have, and produces intervals that are too narrow. A
reviewer pointed out that the interval at 5 deg has a lower bound of +0.008, close enough to zero
that the correction could remove it.

This repeats the paired bootstrap resampling BODIES with replacement rather than conditions, which
is the unit that would be redrawn if the study were repeated. Both are reported side by side, so the
cost of the assumption is visible rather than argued about.

Run:  python clustered_ci.py [n_seeds] [n_boot]
"""
import warnings; warnings.filterwarnings('ignore')
import os, sys, numpy as np
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.multioutput import MultiOutputClassifier

import voi_analysis as V

HERE = os.path.dirname(os.path.abspath(__file__))
NSEED = int(sys.argv[1]) if len(sys.argv) > 1 else 8
NBOOT = int(sys.argv[2]) if len(sys.argv) > 2 else 4000
LEVELS = [0.0, 2.0, 5.0, 8.0, 12.0]
K1 = 'L1  camera (sagittal + timing)'
K2 = 'L2  camera + FORCE PLATE'


def per_condition(df, cols, seeds):
    acc = {}
    subs = sorted(df.subj.unique())
    for sd in range(seeds):
        for ho in subs:
            tr, te = df[df.subj != ho], df[df.subj == ho]
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
                a = acc.setdefault(tag, [0, 0, t.subj.iloc[0]])
                a[0] += int(np.argsort(-P)[0] == V.M.index(t.mech.iloc[0])); a[1] += 1
    return {k: (v[0] / v[1], v[2]) for k, v in acc.items()}


def main():
    out = open(os.path.join(HERE, 'clustered_ci.txt'), 'w')

    def say(m):
        print(m, flush=True); out.write(m + '\n'); out.flush()

    say('=== MARGINAL VALUE OF THE FORCE PLATE: CONDITION-LEVEL vs BODY-LEVEL BOOTSTRAP ===')
    say('The body is the unit that would be redrawn if the study were repeated, and it is also the')
    say('cross-validation fold. Resampling conditions treats them as independent; resampling bodies')
    say('does not. The second is the honest interval.')
    say('')
    say(f'{"error":>6}{"gain":>9}{"per-condition 95% CI":>26}{"per-BODY 95% CI":>24}{"survives":>10}')

    rng = np.random.default_rng(0)
    rows = []
    for nz in LEVELS:
        df = V.build(n_rep=4, noise=nz, seed=0)
        for m in V.M:
            df[f'is_{m}'] = (df.mech == m).astype(int)
        lv = V.levels(df)
        h1 = per_condition(df, lv[K1], NSEED)
        h2 = per_condition(df, lv[K2], NSEED)
        tags = sorted(set(h1) & set(h2))
        d = np.array([h2[t][0] - h1[t][0] for t in tags])
        body = np.array([h1[t][1] for t in tags])
        n = len(tags)

        b1 = np.array([d[rng.integers(0, n, n)].mean() for _ in range(NBOOT)])
        lo1, hi1 = np.percentile(b1, [2.5, 97.5])

        # cluster bootstrap: resample BODIES with replacement, take all their conditions
        bodies = sorted(set(body))
        idx = {b: np.where(body == b)[0] for b in bodies}
        b2 = []
        for _ in range(NBOOT):
            pick = rng.integers(0, len(bodies), len(bodies))
            sel = np.concatenate([idx[bodies[k]] for k in pick])
            b2.append(d[sel].mean())
        b2 = np.array(b2)
        lo2, hi2 = np.percentile(b2, [2.5, 97.5])

        ok = 'yes' if lo2 > 0 else ('no' if hi2 > 0 else 'negative')
        rows.append((nz, d.mean(), lo1, hi1, lo2, hi2, lo2 > 0))
        say(f'{nz:6.1f}{d.mean():+9.3f}   [{lo1:+.3f}, {hi1:+.3f}]        [{lo2:+.3f}, {hi2:+.3f}]{ok:>10}')

    say('')
    surv = [r[0] for r in rows if r[6]]
    say('=== WHAT MAY BE CLAIMED AFTER THE CORRECTION ===')
    if surv:
        say(f'  the force plate still adds information at: ' + ', '.join(f'{x:.0f} deg' for x in surv))
    else:
        say('  NO error level survives a body-level bootstrap. The kinetics result must be reported as')
        say('  a consistent positive trend whose interval includes zero once the cluster structure of')
        say('  the design is respected, and NOT as a demonstrated effect at any level.')
    say('')
    say(f'  n = {len(sorted(set(body)))} bodies is a very small number of clusters; a body-level')
    say('  bootstrap is itself unstable at this sample size, and the honest reading of both intervals')
    say('  together is that the direction is consistent and the magnitude is not well determined.')
    out.close()


if __name__ == '__main__':
    main()
