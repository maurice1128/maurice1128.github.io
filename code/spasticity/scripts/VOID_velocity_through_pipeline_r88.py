#!/usr/bin/env python3
"""VOID -- BUILT, NEVER EXECUTED, CANCELLED BEFORE IT PRODUCED A NUMBER. DO NOT RUN.

WHAT THIS WAS. A companion to `video_degradation.py` that would have pushed `ank_vel_max` through
the registered pipeline to test whether the velocity separation survives the 6 Hz low-pass. It
imported the registered stages rather than reimplementing them, which was the right construction
for the wrong question.

WHY IT IS VOID. The premise was refuted by a result already in the manuscript, at
`RESULTS_discrimination.md`:429-435, marked *"This result is not retracted"*:

    ank_vel_max (registered, filtered)              AUC 0.0000  p 0.0079365  overlap 0/5
    residual after ROM + cadence + equinus          AUC 0.3600  p 0.5476     overlap 4/5
    R^2 = 0.8030

ROM, cadence and presenting equinus account for 80.3 % of condition-level peak ankle velocity, and
what remains does not separate the arms. **The velocity separation is not an independent channel --
it is largely ROM restated.** A velocity feature that survived the pipeline would therefore be ROM
surviving under another name, and the pre-processing question does not arise. The second premise was
also wrong: the registered primary IS the filtered variant, and filtered and unfiltered reach the
same verdict (R^2 0.8030 against 0.9809).

RETAINED RATHER THAN DELETED, for the reason this project retains void artifacts: a script sitting
unrun in `scone/` is a trap, and a script that explains why it must not be run is a record. It never
wrote an output file and no figure anywhere derives from it.

*** IF YOU ARE ABOUT TO RUN THIS TO SEE WHAT HAPPENS: the number it produces would be a fourth
variant of a feature that already has three (see COUNCIL_round88.md). That is the hazard this
project has paid for twice. ***
"""
import sys

print(__doc__)
print("VOID. This script is disabled by disposition, not by defect. Exiting without computing.")
sys.exit(2)
