# Analysis code — capture-error tolerance study

Code and derived data for **"How much joint-angle error can the identification of a weak muscle
group tolerate? A predictive-simulation study"** (Wang & Shih, under review at *Journal of
Biomechanics*).

Every number in the paper is produced by one of the scripts here, run on the frozen dataset in
`data/`. Nothing is copied by hand between the analysis and the manuscript.

## Layout

```
*.py         the scripts named in Supplementary S13, plus the three modules they import
data/        the frozen inputs
outputs/     what each script printed, one file per script
```

## Data

| file | what it is |
|---|---|
| `data/features_det.csv` | the per-condition feature table, 66 accepted conditions |
| `data/signals_raw.csv` | the raw sagittal joint-angle waveforms the noise is added to |
| `data/qc_accepted.txt` | the quality-control record: which of the 75 design cells passed and why |

The full SCONE simulation output is 0.33 GB and is not in this repository. These three files are
what every analysis actually reads, so the results reproduce without it.

## Running

```
pip install numpy pandas scikit-learn matplotlib
python voi_analysis.py          # the tolerance curve and the tier comparison
python severity_clustered.py    # the severity interaction, both resampling units
python cluster_degeneracy.py    # why a five-cluster percentile interval cannot fail
python make_figure1.py          # rebuilds Figure 1 from the outputs
```

Each script writes its own `.txt` beside itself. The copies in `outputs/` are the runs the
manuscript quotes, so a fresh run can be diffed against them.

`voi_analysis.py` is the core: it builds the feature table at a given capture-error level, applies
zero-mean Gaussian error to the raw signals before any feature is computed, and evaluates
leave-one-variant-out. The others import it.

## Two things worth knowing before reading the numbers

**The reported decision pools four noise realisations.** `voi_analysis.loso` ranks a held-out
condition from the mean predicted probability across its four independent realisations, which is
four captures rather than the one a clinic takes. `single_capture.py` measures both; the level
claims hold either way.

**Interval estimators are not interchangeable here.** With five model variants, a pairs-cluster
percentile bootstrap is confined to the convex hull of the five variant means, so when they agree in
sign it cannot cross zero regardless of the true uncertainty. `cluster_degeneracy.py` demonstrates
this and computes the *t* interval the paper reports instead. The severity interaction survives the
percentile bootstrap and fails the *t* interval, which is why the paper reports it as an observation
rather than a demonstrated effect.

## Licence and status

The manuscript is under review. The code is provided so the reported numbers can be checked; please
do not redistribute the manuscript text itself. Correspondence: Hui-Ting Shih.
