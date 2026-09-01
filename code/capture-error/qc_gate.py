"""Real quality-control gate for SCONE conditions.

Council finding: the stated QC ("all conditions walk 13-24 steps") had no implementation, rejected
nothing, and step count is not a valid criterion (a dorsiflexor gait can double its ground contacts
by shuffling). This script implements explicit, reproducible acceptance criteria and WRITES the
qc.sto used downstream, so the single input to the whole analysis has a traceable provenance.

Acceptance criteria (all must pass):
  1. Optimisation actually adapted the controller   : best solution not at generation 0
  2. Gait quality                                   : best CMA objective <= OBJ_MAX
  3. No fall                                        : pelvis height never drops below FALL_FRAC of its
                                                      own steady-state median
  4. Sustained locomotion                           : forward progression >= MIN_DISTANCE m
  5. Steady-state exists                            : trial length >= MIN_DURATION s
Rejected conditions are reported and excluded from analysis (not silently kept).
"""
import glob, os, re, subprocess, sys
import numpy as np

import os as _os
_FROZEN = r'C:\Users\maurice\Desktop\stroke_scone\results_frozen'
RES = _FROZEN if _os.path.isdir(_FROZEN) else r'C:\Users\maurice\Documents\SCONE\results'
SCONE = r'C:\Program Files\SCONE\bin\sconecmd.exe'
OBJ_MAX = 5.0        # CMA objective; > 5 indicates a poor / unstable gait
FALL_FRAC = 0.70     # pelvis must stay above 70% of its steady-state median height
MIN_DISTANCE = 3.0   # metres of forward progression in the trial
MIN_DURATION = 8.0   # seconds

TAG_RE = re.compile(r'^(s\d)?(PF|DF|KE|KF|HF)(\d+)L$')


def best_par(folder):
    pars = glob.glob(os.path.join(folder, '[0-9]*.par'))
    best, binfo = None, None
    for p in pars:
        m = re.match(r'(\d+)_([\d.]+)_([\d.]+)\.par', os.path.basename(p))
        if not m:
            continue
        gen, obj = int(m.group(1)), float(m.group(3))
        if binfo is None or obj < binfo[1]:
            best, binfo = p, (gen, obj)
    return best, binfo


def read_sto(path):
    lines = open(path).read().splitlines()
    hi = [i for i, l in enumerate(lines) if l.lower().startswith('time')][0]
    cols = lines[hi].split('\t')
    data = np.array([[float(x) for x in l.split('\t')] for l in lines[hi + 1:] if l.strip()])
    return cols, data


def col(cols, data, name):
    m = [i for i, c in enumerate(cols) if c == name]
    return data[:, m[0]] if m else None


def qc_condition(folder, regenerate=False):
    tag = os.path.basename(folder).split('.')[0]
    par, info = best_par(folder)
    if par is None:
        return tag, False, 'no optimisation result'
    gen, obj = info
    if gen == 0:
        return tag, False, f'controller never adapted (best at generation 0, obj={obj:.2f})'
    if obj > OBJ_MAX:
        return tag, False, f'poor gait quality (objective {obj:.2f} > {OBJ_MAX})'

    # The .sto must come from the par whose generation and objective we go on to report. The previous
    # rule regenerated only when the file was ABSENT, so whenever an optimisation kept running after
    # its first QC pass, the analysed kinematics silently came from an older, worse solution than the
    # one reported: 40 of 61 accepted conditions drifted this way, by a median of +0.041 objective and
    # up to +0.197 (DF40L was analysed at generation 3 while being reported as generation 23).
    # Stamping the evaluated par makes the drift impossible: if the best par changes, we re-evaluate.
    sto = os.path.join(folder, 'qc.sto.sto')
    stamp = os.path.join(folder, 'qc.par.txt')
    cur = os.path.basename(par)
    prev = open(stamp).read().strip() if os.path.exists(stamp) else None
    if regenerate or not os.path.exists(sto) or prev != cur:
        subprocess.run([SCONE, '-e', par, '-q', '-r', os.path.join(folder, 'qc.sto')],
                       capture_output=True)
        if os.path.exists(sto):
            open(stamp, 'w').write(cur)
    if not os.path.exists(sto):
        return tag, False, 'evaluation produced no output'

    cols, d = read_sto(sto)
    t = d[:, 0]
    if t[-1] - t[0] < MIN_DURATION:
        return tag, False, f'trial too short ({t[-1]-t[0]:.1f}s)'
    py = col(cols, d, '/jointset/ground_pelvis/pelvis_ty/value')
    px = col(cols, d, '/jointset/ground_pelvis/pelvis_tx/value')
    if py is not None:
        s = int(len(py) * 0.4)
        med = np.median(py[s:])
        if py.min() < FALL_FRAC * med:
            return tag, False, f'fall detected (pelvis {py.min():.2f} < {FALL_FRAC:.0%} of {med:.2f})'
    if px is not None:
        dist = px.max() - px.min()
        if dist < MIN_DISTANCE:
            return tag, False, f'insufficient progression ({dist:.1f} m)'
    return tag, True, f'OK (gen={gen}, obj={obj:.2f})'


def main():
    regen = '--regenerate' in sys.argv
    accepted, rejected = [], []
    for folder in sorted(glob.glob(os.path.join(RES, '*.I'))):
        tag = os.path.basename(folder).split('.')[0]
        if not TAG_RE.match(tag):
            continue
        tag, ok, why = qc_condition(folder, regen)
        (accepted if ok else rejected).append((tag, why))
    print(f'=== QC GATE ===  accepted {len(accepted)}, rejected {len(rejected)}')
    print('\nREJECTED:')
    for tag, why in rejected:
        print(f'  {tag:12} {why}')
    print('\nACCEPTED:')
    for tag, why in accepted:
        print(f'  {tag:12} {why}')
    # write the accepted list for the analysis to consume
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'qc_accepted.txt')
    open(out, 'w').write('\n'.join(t for t, _ in accepted))
    print(f'\nwrote {out} ({len(accepted)} conditions)')


if __name__ == '__main__':
    main()
