"""Does the simulated weak gait look like real weak gait?

A cold reviewer's decisive objection: the study never shows that its simulated plantarflexor-weak
gait resembles a real plantarflexor-weak gait, so the ground truth is internally consistent but
externally unmoored. No reviewer at a clinical or biomechanics journal will accept an identification
study built on gaits that were never checked against a patient.

This extracts the kinematic signature of each imposed weakness in the form the clinical literature
reports it, so it can be laid beside published values. It makes no comparison itself - the published
numbers are fetched separately and the comparison is written by hand, deliberately, so that a
mismatch cannot be quietly absorbed.

Reported per mechanism, at 60 % force loss (the clearest case) and on the STEADY-STATE window:

  ankle   peak plantarflexion (push-off), peak dorsiflexion (swing), total ROM
  knee    peak flexion (swing), peak extension (stance), total ROM
  hip     peak flexion, peak extension, total ROM

each for the paretic and non-paretic limb, and for the healthy reference, since the clinically
meaningful statement is the DIRECTION and SIZE of the change from healthy, not the absolute value of
a scaled model.

Run:  python face_validity.py
"""
import warnings; warnings.filterwarnings('ignore')
import os, re, glob, numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
JOINTS = ['hip_flexion', 'knee_angle', 'ankle_angle']
FULL = {'PF': 'plantarflexor', 'DF': 'dorsiflexor', 'KE': 'knee extensor',
        'KF': 'knee flexor', 'HF': 'hip flexor'}


def signature(row, cols_all):
    """Peak angles per joint per side, from the cached steady-state waveforms."""
    s = {}
    for j in JOINTS:
        for side in ('l', 'r'):
            c = [x for x in cols_all if x.startswith(f'{j}_{side}_')]
            if not c:
                continue
            v = row[c].to_numpy(float)
            s[(j, side)] = (float(v.min()), float(v.max()), float(np.ptp(v)))
    return s


def main():
    out = open(os.path.join(HERE, 'face_validity.txt'), 'w')

    def say(m):
        print(m, flush=True); out.write(m + '\n'); out.flush()

    sig = pd.read_csv(os.path.join(HERE, 'signals_raw.csv')).set_index('tag')
    det = pd.read_csv(os.path.join(HERE, 'features_det.csv'))
    cols_all = list(sig.columns)

    say('=== FACE VALIDITY: kinematic signature of each imposed weakness ===')
    say('Sign convention follows the model output. Angles in degrees, steady-state window.')
    say('L = paretic (weakened) limb, R = non-paretic.')
    say('')

    # healthy reference, if a healthy run is cached
    healthy = [t for t in sig.index if str(t).upper().startswith('HEALTH')]
    if healthy:
        h = signature(sig.loc[healthy[0]], cols_all)
        say(f'--- HEALTHY REFERENCE ({healthy[0]}) ---')
        for j in JOINTS:
            if (j, 'l') in h:
                mn, mx, rom = h[(j, 'l')]
                say(f'  {j:14} min {mn:+7.1f}   max {mx:+7.1f}   ROM {rom:6.1f}')
        say('')
    else:
        h = None
        say('--- no cached healthy run found; changes below are paretic-vs-non-paretic only ---')
        say('')

    say('--- BY MECHANISM, 60 % force loss (base body where available) ---')
    say(f'{"mechanism":>16}{"joint":>14}{"L min":>9}{"L max":>9}{"L ROM":>8}'
        f'{"R min":>9}{"R max":>9}{"R ROM":>8}{"L-R ROM":>9}')
    rows = {}
    for mech in ['PF', 'DF', 'KE', 'KF', 'HF']:
        cand = [t for t in det[det.mech == mech].tag
                if str(t) in sig.index and str(t).endswith('60L')]
        base = [t for t in cand if not re.match(r'^s\d', str(t))]
        tag = (base or cand or [None])[0]
        if tag is None:
            continue
        s = signature(sig.loc[tag], cols_all)
        rows[mech] = s
        for j in JOINTS:
            if (j, 'l') not in s or (j, 'r') not in s:
                continue
            lm, lx, lr = s[(j, 'l')]
            rm, rx, rr = s[(j, 'r')]
            lbl = FULL[mech] if j == JOINTS[0] else ''
            say(f'{lbl:>16}{j:>14}{lm:9.1f}{lx:9.1f}{lr:8.1f}{rm:9.1f}{rx:9.1f}{rr:8.1f}{lr-rr:+9.1f}')
        say('')

    # ---- the specific clinical expectations, stated so they can be checked ------------------
    say('=== WHAT THE CLINICAL LITERATURE EXPECTS, AND WHAT WE SEE ===')
    say('Each row states the textbook consequence of the weakness, then the value measured here.')
    say('A row that does not match is a face-validity failure and must be reported as one.')
    say('')

    checks = []
    if 'PF' in rows and ('ankle_angle', 'l') in rows['PF']:
        lm, lx, lr = rows['PF'][('ankle_angle', 'l')]
        rm, rx, rr = rows['PF'][('ankle_angle', 'r')]
        checks.append(('plantarflexor weakness',
                       'reduced push-off plantarflexion; ankle ROM on the paretic side falls',
                       f'paretic ankle ROM {lr:.1f} vs non-paretic {rr:.1f} (difference {lr-rr:+.1f})',
                       lr < rr))
    if 'DF' in rows and ('ankle_angle', 'l') in rows['DF']:
        lm, lx, lr = rows['DF'][('ankle_angle', 'l')]
        rm, rx, rr = rows['DF'][('ankle_angle', 'r')]
        checks.append(('dorsiflexor weakness',
                       'reduced swing-phase dorsiflexion (foot drop): paretic peak dorsiflexion lower',
                       f'paretic ankle max {lx:+.1f} vs non-paretic {rx:+.1f} (difference {lx-rx:+.1f})',
                       lx < rx))
    if 'KE' in rows and ('knee_angle', 'l') in rows['KE']:
        lm, lx, lr = rows['KE'][('knee_angle', 'l')]
        rm, rx, rr = rows['KE'][('knee_angle', 'r')]
        # negative = flexion: knee extensor weakness should leave the knee LESS able to resist
        # flexion under load, i.e. a more negative stance/overall minimum on the paretic side.
        checks.append(('knee extensor (vasti) weakness',
                       'the knee cannot be held extended against load, so it flexes further',
                       f'paretic peak flexion {lm:+.1f} vs non-paretic {rm:+.1f} '
                       f'(difference {lm-rm:+.1f})',
                       lm < rm - 2.0))
    if 'KF' in rows and ('knee_angle', 'l') in rows['KF']:
        lm, lx, lr = rows['KF'][('knee_angle', 'l')]
        rm, rx, rr = rows['KF'][('knee_angle', 'r')]
        # knee_angle is NEGATIVE for flexion in this model (verified against the .osim), so peak
        # swing flexion is the MINIMUM and terminal-stance hyperextension is the MAXIMUM. The
        # hamstrings decelerate terminal knee extension, so their weakness is expected to show as
        # HYPEREXTENSION (genu recurvatum) rather than as reduced swing flexion - stiff-knee gait
        # after stroke is usually attributed to rectus femoris overactivity, not hamstring weakness.
        checks.append(('knee flexor (hamstring) weakness',
                       'knee hyperextension in terminal stance (genu recurvatum), the hamstrings no '
                       'longer decelerating extension',
                       f'paretic knee peak extension {lx:+.1f} vs non-paretic {rx:+.1f} '
                       f'(difference {lx-rx:+.1f})',
                       lx > rx + 2.0))
        checks.append(('knee flexor (hamstring) weakness - secondary',
                       'peak SWING flexion should be little changed (stiff-knee is not the expected '
                       'consequence of hamstring weakness)',
                       f'paretic peak flexion {lm:+.1f} vs non-paretic {rm:+.1f} '
                       f'(difference {lm-rm:+.1f})',
                       abs(lm - rm) < 5.0))
    if 'HF' in rows and ('hip_flexion', 'l') in rows['HF']:
        lm, lx, lr = rows['HF'][('hip_flexion', 'l')]
        rm, rx, rr = rows['HF'][('hip_flexion', 'r')]
        checks.append(('hip flexor weakness',
                       'reduced peak hip flexion in swing; shorter step on the paretic side',
                       f'paretic hip max {lx:+.1f} vs non-paretic {rx:+.1f} (difference {lx-rx:+.1f})',
                       lx < rx))

    for name, expect, got, ok in checks:
        mark = '  ' if ok is None else ('OK' if ok else '**MISMATCH**')
        say(f'  {name}')
        say(f'      expected : {expect}')
        say(f'      measured : {got}   {mark}')
        say('')

    say('NOTE ON SIGN CONVENTIONS. Whether a row is a match depends on the model\'s sign convention')
    say('for each joint, which must be confirmed against the model file before any of these is')
    say('written up. A previous version of this project reported an asymmetry direction that')
    say('reversed once it was measured on the window the analysis actually uses.')
    out.close()


if __name__ == '__main__':
    main()
