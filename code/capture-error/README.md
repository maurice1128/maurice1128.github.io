# Analysis code: capture-error tolerance study

Code and derived data for **"How much joint-angle error can the identification of a weak muscle
group tolerate? A predictive-simulation study"** (Wang &amp; Shih). Status: manuscript prepared for
*Journal of Biomechanics* (not yet submitted). Version of 2026-11-17.

Every number in the paper is produced by one of the scripts here, run on the frozen dataset in this
folder. Nothing is copied by hand between the analysis and the manuscript.

## Layout

```
*.py                 the scripts named in Supplementary S13, plus the modules they import
features_det.csv     per-condition feature table, the 66 analysed conditions
signals_raw.csv      raw sagittal joint-angle waveforms (200 samples) that the capture error is added to
qc_accepted.txt      quality-control record: which design cells passed and were analysed
outputs/             what each script printed in the run the manuscript quotes, one file per script
```

The full SCONE simulation output is not included. The three data files above are what the
identification analyses read, so those results reproduce without it.

## Running

```
pip install numpy pandas scikit-learn matplotlib joblib
python voi_analysis.py 2           # identification at one capture-error level (here 2 degrees)
python crossover_ci.py             # tolerance curve and force-plate gain with intervals
python kinematics_only.py          # the 27 purely kinematic features
python clinical_breakdown.py       # accuracy by severity and by muscle group, confusion matrices
python single_capture.py           # one capture against the four the decision pools
python tolerance.py --white-only   # white-noise sweep (Supplementary S8)
python tolerance.py                # structured error at the same total RMS (Supplementary S8)
python error_structure.py          # white, structured and constant-offset error (S8.1, S8.2)
```

Each script writes its own `.txt` beside itself; compare it with the copy in `outputs/`.
`make_figure1.py` and `make_figure3.py` read those `.txt` files, so run the analyses first.

Scripts that need the full simulation output and will not run from this folder alone:
`qc_gate.py`, `build_cache.py`, `face_validity_all.py`, `face_validity_phase.py`,
`exemplar_pf60.py`, `confound_test.py`, `tier_boundary.py`, parts of `remaining_checks.py`, and
`make_figure2.py` (which draws rendered frames). Their outputs are in `outputs/`.

## Three things worth knowing before reading the numbers

**The reported decision pools four noise samples.** A held-out condition is ranked from the mean
predicted probability across four independent error samples. `single_capture.py` reports one
capture as well: 0.767 at 2 degrees and 0.504 at 12, against 0.824 and 0.549 pooled.

**Interval estimators are not interchangeable here.** With five model variants, a cluster
percentile bootstrap is confined to the range of the five variant means, so it cannot cross zero
when they agree in sign. `cluster_degeneracy.py` shows this and computes the *t* interval the paper
reports. This is also why the severity difference is reported as not statistically separable
(Supplementary S11).

**A degree here is waveform RMS error.** Error is added per sample to the joint-angle waveform. It is
not the between-session standard deviation of the reliability literature. In `tolerance.py` the
structured error (offset, drift, jitter) is scaled to the same total RMS as white noise.

## Licence and status

The manuscript is not yet published. The code is provided so the reported numbers can be checked;
please do not redistribute the manuscript text. Correspondence: Hui-Ting Shih.
