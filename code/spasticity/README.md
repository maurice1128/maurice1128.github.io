# Analysis code and containers — hyperreflexia versus weakness

Supporting material for *Distinguishing graded plantarflexor hyperreflexia from graded dorsiflexor
weakness in simulated post-stroke gait: a search over 81 sagittal kinematic variables*
(manuscript in preparation).

Project page: https://maurice1128.github.io/projects/spasticity.html

## What is here

| Directory | Contents |
|---|---|
| `scripts/` | 396 Python analysis scripts. Every statistic in the manuscript and supplement is produced by one of these. |
| `containers/` | 818 JSON result containers. Each holds the numbers one script produced, the inputs it read, and a statement of why it was run. |
| `preregistrations/` | 147 preregistrations, written before the analysis they govern was run. |
| `hashes/` | 117 SHA-256 sidecars over the preregistrations. |
| `records/` | The defect register, the formally abandoned arms, and the first council audit. |

The containers are the reproducible layer. A reader who wants to check a number in the paper should
look for it in `containers/`, not re-run anything: `scripts/bindcheck_r572.py` is the script that
binds three-or-more-decimal values in the text to a container holding that value whose path shares a
term with the claim, and the manuscript reports its outcome, including the 23 values it could not
bind.

## What is not here, and why

**The raw simulation outputs are not in this repository.** They are roughly 1129 run directories of
SCONE output, far past what belongs in a web repository, and they are not redistributed here. The
manuscript's availability statement commits them to an archival deposit; that deposit is not yet
made, and this repository does not stand in for it. Sixteen of those run directories lack a replayed
output and contribute to no analysis in the paper.

**Nothing here can be re-simulated.** The Hyfydy licence under which these simulations were run
expired on 27 August 2026. The scripts that read simulation output will not reproduce that output.
Analyses that consume the containers do not need a simulator licence and do run.

**Paths are absolute and local.** The scripts were written against one machine and read from
hard-coded Windows paths. They are published as the record of what was actually run, not as a
portable package, and they are not expected to execute unchanged elsewhere.

**The scripts include the corrections, not only the analyses.** Files named `fix_rNNN.py` are the
edits that repaired defects found in adversarial review. They are part of the record deliberately:
the defect register in `records/` names the defects, and these scripts are what was done about them.

## Licence

Analysis code and containers: CC0. The normative reference dataset used elsewhere in this project
(van Criekinge et al., *Sci Data* 2023) is CC0 and is not redistributed here; it is available from
its own record at doi:10.6084/m9.figshare.24192489.
