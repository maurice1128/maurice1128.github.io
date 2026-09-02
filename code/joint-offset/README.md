# Joint-centre offset and per-joint triangulation verdicts — analysis code

Analysis code for the study behind
[projects/joint-offset.html](../../projects/joint-offset.html):
what 3D position error measures at the hip and knee, and what follows for comparing
markerless triangulation variants.

## What is here, and what is not

Every script that produces a number in the manuscript or its supplementary material is
included. **No data is included.** The study is a secondary analysis of the BioCV dataset,
which is All Rights Reserved and released by the University of Bath on request under a data
use agreement; it may not be redistributed, so neither the recordings, the marker
trajectories, the camera calibrations, nor the cached pose detections derived from them
appear here. Requests go to the Bath Research Data Archive
(https://doi.org/10.15125/BATH-01258).

No participant is identifiable from anything in this directory. Participant labels such as
`P03` and `P26` are the archive's own trial identifiers and are used in the paper.

The result files the scripts write are reproduced verbatim in the supplementary material, so
the numbers can be checked without the data.

## Layout

- `rowv.py`, `biocv_calib.py` — triangulation and camera geometry.
- `biocv_detect*.py`, `biocv_make_undist_cache.py` — pose detection and the undistorted cache
  the analyses run from.
- `biocv_permutation_v2.py`, `biocv_*_fdr.py`, `by_sensitivity.py`,
  `pooled_family_sensitivity.py` — the exact sign-flip test, the declared families, and the
  two multiplicity sensitivities.
- `biocv_offset_confound.py` — the offset-removal experiment, Parts A to G, including the
  reversal test the paper's central claim rests on.
- `biocv_camera_subsets.py`, `biocv_subset_control.py`, `biocv_loo_exclusion.py`,
  `biocv_mad_sweep.py` — the pre-declared controls, including the ones that returned against
  the paper.
- `biocv_figures.py` — the four figures.
- `build_*.py` — the manuscript, supplement and cover letter documents.
- `check_*.py`, `measure_checkers.py`, `provenance.py` — the consistency checks run over the
  written text against the result files.

## Reading rules fixed before the numbers

Most analysis scripts carry, in their module docstring, the reading that was fixed before the
script was run — including the branch under which the result would count against the paper.
Where such a branch fired, the file says so and the paper reports it. Those docstrings are
part of the record, not commentary added afterwards.

## Running

Python 3.11 with `numpy`, `scipy`, `matplotlib`, `ezc3d`, `python-docx`, `PyMuPDF`. Pose
detection additionally needs `mmpose`/`mmdet` and a CUDA device. Paths to the dataset and to
the result directory are set at the top of each script.
