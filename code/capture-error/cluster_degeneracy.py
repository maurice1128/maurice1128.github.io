"""Is "excludes zero under the body-level bootstrap" an uncertainty result, or just five same signs?

clustered_ci.py answers the reviewer objection about cluster structure with a pairs-cluster
PERCENTILE bootstrap over the five bodies. That estimator has a defect at this number of clusters
which is not a matter of degree: a resample mean is a convex combination of the five body means, so
its support is confined to [min body mean, max body mean]. If all five body means share a sign, the
interval cannot include zero no matter what the true uncertainty is, and "excludes zero" reduces to
"five numbers agreed in sign". Five same signs is a two-sided sign test at p = 2 x 0.5^5 = 0.0625,
which is not a 95 % result.

This prints the five per-body values behind each reported interval, and a t interval on 4 degrees of
freedom over those five numbers - the standard small-cluster alternative, which can cross zero and
therefore actually tests something. Where the two disagree, the t interval is the honest one.

Run:  python cluster_degeneracy.py [n_seeds]
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
LEVELS = [0.0, 2.0, 5.0, 8.0, 12.0]
K1 = 'L1  camera (sagittal + timing)'
K2 = 'L2  camera + FORCE PLATE'


def per_body_gain(nz):
    """{body: mean(plate hit) - mean(camera hit)} at one capture-error level."""
    df = V.build(n_rep=4, noise=nz, seed=0)
    for m in V.M:
        df[f'is_{m}'] = (df.mech == m).astype(int)
    lv = V.levels(df)
    hit = {K1: {}, K2: {}}
    for key in (K1, K2):
        cols = lv[key]
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
                    a = hit[key].setdefault(str(t.subj.iloc[0]), [0, 0])
                    a[0] += int(np.argsort(-P)[0] == V.M.index(t.mech.iloc[0]))
                    a[1] += 1
    return {b: hit[K2][b][0] / hit[K2][b][1] - hit[K1][b][0] / hit[K1][b][1] for b in hit[K1]}


def t_interval(x):
    """Two-sided 95 % t interval on the mean of a handful of cluster values."""
    x = np.asarray(x, float)
    n = len(x)
    if n < 2:
        return np.nan, np.nan
    se = x.std(ddof=1) / np.sqrt(n)
    # t(0.975, n-1) for the small n this study has, so scipy is not required
    # keyed by n, not by degrees of freedom: n = 5 bodies -> t(0.975, df = 4) = 2.776
    T = {2: 12.706, 3: 4.303, 4: 3.182, 5: 2.776, 6: 2.571, 7: 2.447}.get(n, 1.96)
    return x.mean() - T * se, x.mean() + T * se


def main():
    out = open(os.path.join(HERE, 'cluster_degeneracy.txt'), 'w', encoding='utf-8')

    def say(m):
        print(m, flush=True); out.write(m + '\n'); out.flush()

    say('=== THE FIVE NUMBERS BEHIND EACH BODY-LEVEL INTERVAL ===')
    say(f'seeds {NSEED}')
    say('')
    say('--- marginal value of the force plate, per body ---')
    say(f'{"error":>7}   ' + ''.join(f'{b:>9}' for b in
        sorted(per_body_gain(0.0))) + f'{"mean":>10}{"t(4) 95 % CI":>22}  verdict')

    G = {}
    for nz in LEVELS:
        g = per_body_gain(nz)
        G[nz] = g
        bodies = sorted(g)
        v = [g[b] for b in bodies]
        lo, hi = t_interval(v)
        sign = 'all +' if all(x > 0 for x in v) else ('all -' if all(x < 0 for x in v) else 'mixed')
        say(f'{nz:6.0f}   ' + ''.join(f'{g[b]:+9.3f}' for b in bodies)
            + f'{np.mean(v):+10.3f}   [{lo:+.3f}, {hi:+.3f}]  '
            + ('excludes zero' if lo > 0 or hi < 0 else 'INCLUDES ZERO') + f'  ({sign})')
    json.dump({str(k): v for k, v in G.items()},
              open(os.path.join(HERE, 'per_body_gain.json'), 'w'), indent=1)
    say('')

    say('--- what the percentile bootstrap could and could not have returned ---')
    say('Support of a pairs-cluster resample mean is [min body value, max body value], so:')
    say(f'{"error":>7}{"min body":>11}{"max body":>11}   could the percentile interval have crossed zero?')
    for nz in LEVELS:
        v = list(G[nz].values())
        say(f'{nz:6.0f}{min(v):+11.3f}{max(v):+11.3f}   '
            + ('yes - the body values straddle zero' if min(v) < 0 < max(v)
               else 'NO - guaranteed to exclude zero by sign agreement alone'))
    say('')
    say('READING: at any level marked NO, the reported "excludes zero" carries no information beyond')
    say('the five signs agreeing, and five agreeing signs is p = 0.0625 two-sided - not a 95 % result.')
    say('The t interval on the same five numbers is the one that can fail, so it is the one to quote.')
    out.close()


if __name__ == '__main__':
    main()
