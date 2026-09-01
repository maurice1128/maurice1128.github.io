"""Confidence intervals on the force plate's marginal value, at every capture-error level.

This is the last statistical analysis. Everything reported so far has been a point estimate at four
classifier seeds, and the study has a hard resolution limit that makes that inadequate: with 61
conditions, one condition changing its answer moves the estimate by 1/61 = 0.016. A quoted difference
of +0.025 is therefore "about one and a half conditions", which no reader can evaluate without an
interval.

Design, so the interval means what it says:
  * both tiers see the SAME conditions, the SAME folds and the SAME noise realisations, so the
    difference is paired within condition rather than a difference of two independent means;
  * classifier randomness is averaged over many seeds rather than four;
  * the interval is bootstrapped over CONDITIONS, because a repeat of this study would draw new
    conditions, not new random seeds;
  * the full bootstrap distribution is summarised, not just an endpoint, since a percentile bootstrap
    that lands exactly on zero is a degenerate endpoint rather than a coverage statement.

Run:  python crossover_ci.py [n_seeds] [n_boot]
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
    """Mean top-1 and top-3 correctness for each condition, averaged over classifier seeds."""
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
                o = np.argsort(-P); ti = V.M.index(t.mech.iloc[0])
                a = acc.setdefault(tag, [0, 0, 0])
                a[0] += int(o[0] == ti); a[1] += int(ti in o[:3]); a[2] += 1
    return {k: (v[0] / v[2], v[1] / v[2]) for k, v in acc.items()}


def main():
    out = open(os.path.join(HERE, 'crossover_ci.txt'), 'w')

    def say(m):
        print(m, flush=True); out.write(m + '\n'); out.flush()

    say('=== MARGINAL VALUE OF THE FORCE PLATE, WITH INTERVALS ===')
    say(f'classifier seeds {NSEED} | {NBOOT} paired bootstrap resamples over conditions')
    say(f'resolution limit: one condition changing its answer = 1/n of the estimate')
    say('')
    say(f'{"error":>6}{"camera":>9}{"+plate":>9}{"value":>9}{"95% CI":>18}{"P(value>0)":>12}{"~cond":>7}')

    rows = []
    for nz in LEVELS:
        df = V.build(n_rep=4, noise=nz, seed=0)
        for m in V.M:
            df[f'is_{m}'] = (df.mech == m).astype(int)
        lv = V.levels(df)
        h1 = per_condition(df, lv[K1], NSEED)
        h2 = per_condition(df, lv[K2], NSEED)
        tags = sorted(set(h1) & set(h2))
        a = np.array([h1[t][0] for t in tags])
        b = np.array([h2[t][0] for t in tags])
        d = b - a
        n = len(tags)
        rng = np.random.default_rng(0)
        boot = np.array([d[rng.integers(0, n, n)].mean() for _ in range(NBOOT)])
        lo, hi = np.percentile(boot, [2.5, 97.5])
        pgt = float((boot > 0).mean())
        rows.append((nz, a.mean(), b.mean(), d.mean(), lo, hi, pgt, n))
        say(f'{nz:6.1f}{a.mean():9.3f}{b.mean():9.3f}{d.mean():+9.3f}'
            f'   [{lo:+.3f}, {hi:+.3f}]{pgt:12.3f}{d.mean()*n:7.1f}')

    say('')
    say(f'  n = {rows[0][7]} conditions -> resolution {1/rows[0][7]:.4f} per condition changed')
    say('  "~cond" is the difference expressed as the number of conditions whose answer changed.')
    say('')
    say('=== WHAT MAY BE CLAIMED ===')
    sig = [r for r in rows if r[4] > 0]
    if sig:
        say('  Levels where the force plate helps with the interval excluding zero:')
        for r in sig:
            say(f'    {r[0]:.0f} deg : {r[3]:+.3f}  95% CI [{r[4]:+.3f}, {r[5]:+.3f}]')
        say(f'  -> the plate can be claimed to help at or above {min(r[0] for r in sig):.0f} deg.')
    else:
        say('  NO level has an interval excluding zero. The crossover may be described as a trend')
        say('  supported by robustness checks, but NOT as a demonstrated effect at any single level.')
    neg = [r for r in rows if r[5] < 0]
    if neg:
        say('  Levels where the plate measurably HURTS (interval entirely below zero):')
        for r in neg:
            say(f'    {r[0]:.0f} deg : {r[3]:+.3f}  95% CI [{r[4]:+.3f}, {r[5]:+.3f}]')
    say('')
    say('  Trend test across levels (Spearman of value vs capture error):')
    from scipy.stats import spearmanr
    rho, p = spearmanr([r[0] for r in rows], [r[3] for r in rows])
    say(f'    rho = {rho:+.3f}, p = {p:.3f}  (n = {len(rows)} levels — a weak test by construction)')
    out.close()


if __name__ == '__main__':
    main()
