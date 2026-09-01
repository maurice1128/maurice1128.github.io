"""Operating envelope: at what capture error does the sagittal camera stop being sufficient?

The single-point claim "adding a force plate is worth +0.000" is weak, because it is measured at one
assumed noise level and at a top-3 accuracy of 1.000 — a ceiling, where nothing *could* add value.
The defensible version of the claim is a boundary:

    up to X degrees of capture error, a sagittal camera suffices; beyond it, kinetics are required.

This sweeps capture error and reports every tier at each level, so the point at which the tiers
separate (if they separate at all) is measured rather than assumed. It also doubles as a robustness
check on the headline: if the ordering of tiers flips between 2 and 3 degrees, the headline was
never safe to report.

Run:  python noise_envelope.py            (default sweep)
      python noise_envelope.py 0 2 4 8    (explicit levels, degrees)
"""
import warnings; warnings.filterwarnings('ignore')
import os, sys
import voi_analysis as V

HERE = os.path.dirname(os.path.abspath(__file__))
LEVELS = [float(x) for x in sys.argv[1:]] or [0.0, 1.0, 2.0, 3.0, 5.0, 8.0, 12.0]


def main():
    out = open(os.path.join(HERE, 'noise_envelope.txt'), 'w')

    def say(m):
        print(m, flush=True); out.write(m + '\n'); out.flush()

    say('=== OPERATING ENVELOPE: capture error vs tier sufficiency ===')
    say('Each row is an independent evaluation (features rebuilt from the raw signals with that')
    say('level of error applied, then leave-one-body-out). "value" is camera+plate minus camera.')
    say('')
    say(f'{"noise":>7}  {"camera t1":>10}{"camera t3":>10}   {"+plate t1":>10}{"+plate t3":>10}'
        f'   {"value t1":>9}{"value t3":>9}   {"plate alone t1":>15}')

    K1 = 'L1  camera (sagittal + timing)'
    K2 = 'L2  camera + FORCE PLATE'
    K4 = '    - force plate alone'
    rows = []
    for nz in LEVELS:
        df = V.build(n_rep=4, noise=nz, seed=0)
        for m in V.M:
            df[f'is_{m}'] = (df.mech == m).astype(int)
        lv = V.levels(df)
        r = {}
        for k in (K1, K2, K4):
            t1, sd, t3, _ = V.loso(df, lv[k])
            r[k] = (t1, t3)
        v1 = r[K2][0] - r[K1][0]
        v3 = r[K2][1] - r[K1][1]
        rows.append((nz, r[K1], r[K2], r[K4], v1, v3))
        say(f'{nz:7.1f}  {r[K1][0]:10.3f}{r[K1][1]:10.3f}   {r[K2][0]:10.3f}{r[K2][1]:10.3f}'
            f'   {v1:+9.3f}{v3:+9.3f}   {r[K4][0]:15.3f}')

    say('')
    say('=== where does the boundary sit? ===')
    cross = [nz for nz, _, _, _, v1, _ in rows if v1 > 0.02]
    if cross:
        say(f'  camera+plate exceeds camera by >0.02 top-1 from {min(cross):.1f} deg upward')
        say(f'  -> claim: below {min(cross):.1f} deg a sagittal camera is sufficient; above it kinetics add information')
    else:
        say('  the force plate never adds >0.02 top-1 anywhere in the swept range.')
        say('  -> the claim is NOT an envelope but a saturation result, and must be reported as such:')
        say('     within the range tested, kinetics are redundant for this task at every error level.')
    deg = [(nz, c[0]) for nz, c, _, _, _, _ in rows]
    say('')
    say('=== does the camera itself degrade? (is the task actually being stressed?) ===')
    say('  ' + '  '.join(f'{nz:.0f}deg:{t1:.3f}' for nz, t1 in deg))
    best, worst = max(t for _, t in deg), min(t for _, t in deg)
    say(f'  camera top-1 range over the sweep: {worst:.3f} to {best:.3f}  (spread {best-worst:.3f})')
    if best - worst < 0.05:
        say('  WARNING: the task is insensitive to capture error across the whole range. Either the')
        say('  features are extremely robust, or the task is too easy for this comparison to be')
        say('  informative. Report this rather than the null force-plate result alone.')
    out.close()


if __name__ == '__main__':
    main()
