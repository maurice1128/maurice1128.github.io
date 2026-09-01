"""Is the reported curve the accuracy of one capture, or of four averaged together?

voi_analysis.loso ranks a held-out condition from the MEAN predicted probability over that
condition's four noise realisations (`...predict_proba(...)]).T.mean(0)`). That is test-time
averaging: the decision pools four independent captures, which a clinic taking one capture does not
get. Two consequences have to be measured rather than argued:

  1. every non-zero level is an ensemble of four, so the level claims are optimistic by an unknown
     amount;
  2. at 0 deg the four replicates are byte-identical (build() takes the `else` branch and adds no
     noise), so 0 deg is a genuine one-capture number while every other level is not - the degree
     axis is not like-for-like at its own anchor, and the 0-2 deg segment of the loss rate compares
     one capture against four.

This scores each realisation separately and averages the hits, which is the one-capture decision,
and prints it beside the pooled curve. Both tiers, all five levels.

Run:  python single_capture.py [n_seeds]
"""
import warnings; warnings.filterwarnings('ignore')
import os, sys
import numpy as np
import voi_analysis as V
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.multioutput import MultiOutputClassifier

HERE = os.path.dirname(os.path.abspath(__file__))
NSEED = int(sys.argv[1]) if len(sys.argv) > 1 else 8
LEVELS = [0.0, 2.0, 5.0, 8.0, 12.0]
TIERS = ['L1  camera (sagittal + timing)', 'L2  camera + FORCE PLATE']


def both_curves(nz, tier):
    df = V.build(n_rep=4, noise=nz, seed=0)
    for m in V.M:
        df[f'is_{m}'] = (df.mech == m).astype(int)
    cols = V.levels(df)[tier]
    pooled, single = [], []
    for sd in range(NSEED):
        cp = cs = np_ = ns = 0
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
                ti = V.M.index(t.mech.iloc[0])
                P = np.array([p[:, 1] if p.shape[1] == 2 else np.zeros(len(t))
                              for p in mdl.predict_proba(t[cols].to_numpy(float))]).T
                cp += int(np.argsort(-P.mean(0))[0] == ti); np_ += 1          # four captures pooled
                for row in P:                                                 # one capture at a time
                    cs += int(np.argsort(-row)[0] == ti); ns += 1
        if np_:
            pooled.append(cp / np_); single.append(cs / ns)
    return float(np.mean(pooled)), float(np.mean(single))


def main():
    out = open(os.path.join(HERE, 'single_capture.txt'), 'w', encoding='utf-8')

    def say(m):
        print(m, flush=True); out.write(m + '\n'); out.flush()

    say('=== ONE CAPTURE OR FOUR? ===')
    say(f'seeds {NSEED}; the pooled column must reproduce the reported curve exactly.')
    say('')
    curves = {}
    for tier in TIERS:
        say(tier)
        say(f'{"error":>7}{"pooled (reported)":>20}{"one capture":>14}{"difference":>13}')
        c = {}
        for nz in LEVELS:
            p, s = both_curves(nz, tier)
            c[nz] = (p, s)
            say(f'{nz:6.0f} {p:19.3f}{s:14.3f}{s - p:+13.3f}')
        curves[tier] = c
        say('')

    say('--- per-degree loss rate on each curve ---')
    say('The rate claim ("steepest inside 2-5 deg") is the reason this matters most: at 0 deg the')
    say('four replicates are identical, so the 0-2 deg segment alone compares one capture with four.')
    c = curves[TIERS[0]]
    say(f'{"band":>10}{"pooled":>12}{"one capture":>14}')
    for a, b in ((0, 2), (2, 5), (5, 8), (8, 12)):
        rp = (c[b][0] - c[a][0]) / (b - a)
        rs = (c[b][1] - c[a][1]) / (b - a)
        say(f'{a:4.0f}-{b:<5.0f}{rp:12.4f}{rs:14.4f}')
    say('')
    bp = min(((0, 2), (2, 5), (5, 8), (8, 12)), key=lambda k: (c[k[1]][0] - c[k[0]][0]) / (k[1] - k[0]))
    bs = min(((0, 2), (2, 5), (5, 8), (8, 12)), key=lambda k: (c[k[1]][1] - c[k[0]][1]) / (k[1] - k[0]))
    say(f'steepest band: pooled {bp[0]:.0f}-{bp[1]:.0f} deg, one capture {bs[0]:.0f}-{bs[1]:.0f} deg')
    say('')
    say('READING: if the one-capture curve keeps every level at least twice the 0.227 baseline the')
    say('tolerance claim survives and only the numbers change. If the steepest band moves, the rate')
    say('claim was an artefact of unequal averaging and has to be withdrawn.')
    out.close()


if __name__ == '__main__':
    main()
