"""How large is the perturbation that a nominal capture error actually induces in each feature?

A cold reader raised the strongest objection this study has received: joint-angle error is applied
independently to each of the 200 samples of each waveform, so a feature that averages over the
waveform would see only sigma/sqrt(200) - 0.85 degrees at a nominal 12 - and the comparison against
a 5-degree convention that refers to session-level offsets would be meaningless.

The objection has a factual premise that can be checked. It is false for the kinematic features: all
eighteen are minima, maxima or ranges, and an extremum of 200 noisy samples does not average out - it
is displaced outward by roughly sigma*sqrt(2*ln(n)). But the quantitative form of the objection still
has to be answered, so this measures directly, for every feature:

  induced SD   the spread the noise itself produces, over independent error realisations of one
               fixed condition
  signal SD    the spread across conditions with no noise, i.e. the variation the classifier has to
               exploit
  ratio        induced / signal. Above 1 the noise dominates that feature; well below 1 it does not.

Run:  python noise_magnitude.py
"""
import warnings
warnings.filterwarnings('ignore')
import os
import numpy as np
import voi_analysis as V

HERE = os.path.dirname(os.path.abspath(__file__))
LEVELS = (2.0, 5.0, 12.0)
NREP = 12


def main():
    out = open(os.path.join(HERE, 'noise_magnitude.txt'), 'w', encoding='utf-8')

    def say(m):
        print(m, flush=True)
        out.write(m + '\n')
        out.flush()

    say('=== HOW BIG IS THE PERTURBATION A NOMINAL CAPTURE ERROR ACTUALLY INDUCES? ===')
    say('induced SD : spread produced by the error model alone, over independent realisations')
    say('signal SD  : spread across the 66 conditions with no error added')
    say('ratio      : induced / signal. Above 1 the error dominates that feature.')
    say('')

    clean = V.build(n_rep=1, noise=0.0, seed=0)
    feats = [c for c in clean.columns if '::' in c]
    signal = {c: float(np.nanstd(clean[c].to_numpy(float))) for c in feats}

    say('  all eighteen S:: features are minima, maxima or ranges - none is a mean over the')
    say('  waveform - so per-sample noise is not averaged away in the kinematic tier.')
    say('')

    for nz in LEVELS:
        reps = [V.build(n_rep=1, noise=nz, seed=100 + k) for k in range(NREP)]
        say(f'--- nominal capture error {nz:.0f} deg, {NREP} independent error realisations ---')
        say(f'  {"feature":26}{"induced SD":>12}{"signal SD":>11}{"ratio":>8}')
        rows = []
        for c in feats:
            if c not in reps[0].columns:
                continue
            per_tag = []
            for tag in reps[0].tag.unique():
                v = [float(r.loc[r.tag == tag, c].iloc[0]) for r in reps
                     if (r.tag == tag).any()]
                if len(v) > 2:
                    per_tag.append(np.nanstd(v))
            if not per_tag:
                continue
            ind = float(np.nanmean(per_tag))
            sig = signal.get(c, np.nan)
            rows.append((ind / sig if sig else np.nan, ind, sig, c))
        rows.sort(reverse=True)
        for r, ind, sig, c in rows[:8]:
            say(f'  {c:26}{ind:12.3f}{sig:11.3f}{r:8.2f}')
        say('  ...')
        for r, ind, sig, c in rows[-4:]:
            say(f'  {c:26}{ind:12.3f}{sig:11.3f}{r:8.2f}')
        rr = np.array([r for r, _, _, _ in rows if np.isfinite(r)])
        say(f'  median ratio {np.median(rr):.2f}   max {rr.max():.2f}   '
            f'features with ratio > 1: {int((rr > 1).sum())} of {len(rr)}')
        say('')

    say('READING: the ratio is what decides whether the degree axis is a strong or a weak')
    say('perturbation. A nominal degree value that produces an induced SD far below the')
    say('between-condition SD is not a severe test, whatever the nominal number says.')
    out.close()


if __name__ == '__main__':
    main()
