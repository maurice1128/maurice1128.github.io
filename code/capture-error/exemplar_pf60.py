"""The plantarflexor exemplar quoted in section 3.1.

A cold reader could not trace the two degree values in that sentence, because they had been computed
interactively and never written to a file. They are real, but an unwritten number is indistinguishable
from an invented one, so this exists to write them.

Run:  python exemplar_pf60.py
"""
import warnings
warnings.filterwarnings('ignore')
import os
import glob
import face_validity_phase as F

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    out = open(os.path.join(HERE, 'exemplar_pf60.txt'), 'w', encoding='utf-8')

    def say(m):
        print(m, flush=True)
        out.write(m + '\n')

    say('=== THE PLANTARFLEXOR EXEMPLAR QUOTED IN SECTION 3.1 ===')
    say('Terminal-stance peak plantarflexion, base body, 60 % plantarflexor force loss.')
    say('Terminal stance is the last 40 % of each stance, averaged over strides, as defined in')
    say('face_validity_phase.py. Negative is plantarflexion.')
    say('')

    ds = [d for d in glob.glob(os.path.join(F.RES, 'PF60L.*')) if d.endswith('.I')]
    if not ds:
        say('  PF60L not found')
        out.close()
        return
    A = F.phase_stats(os.path.join(ds[0], 'qc.sto.sto'))
    H = F.healthy_for('base')
    say(f'  paretic (left)                {A[("ankle", "l", "late")][0]:7.1f} deg')
    say(f'  sound (right)                 {A[("ankle", "r", "late")][0]:7.1f} deg')
    say(f'  same body, unimpaired left    {H[("ankle", "l", "late")][0]:7.1f} deg')
    say('')
    say('The sound side and the unimpaired left limb both round to -10.0 deg. That is a coincidence of')
    say('rounding between two different measurements, not one measurement used twice.')
    say('')
    say('Whole-cycle minima for the same condition are in face_validity.txt and differ, because that')
    say('is a different window. Quantities from the two windows must not be mixed in one sentence.')
    out.close()


if __name__ == '__main__':
    main()
