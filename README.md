# Reproducing OptIForest, and testing it on new data

COMP8240 (Macquarie University, Session 2 2026) project by Maedeh Ramezanzadeh.

**Paper:** Xiang et al. (2023). *OptIForest: Optimal Isolation Forest for Anomaly Detection.* IJCAI-23, pp. 2379-2387.
**Authors' code:** https://github.com/xiagll/OptIForest (not copied here; `scripts/setup_authors_code.sh` clones it).

## What is in this repository

| Path | What it does |
|---|---|
| `scripts/setup_authors_code.sh` | Clones the authors' code and applies the one fix it needs on NumPy 2: `np.mat` (removed in NumPy 2.0) becomes `np.asmatrix` (identical behaviour). |
| `src/run_optiforest.py` | Runs the authors' `OptIForest('L2OPT', trees, threshold, branch)` on a dataset, N runs, writes mean and std to `results/`. |
| `src/run_baseline_iforest.py` | scikit-learn Isolation Forest baseline, same metrics, N seeds. |
| `src/shop_sim.py` | **New dataset I construct:** a small web shop plus a traffic simulator. Writes `access.log` and `labels.csv`. |
| `src/build_shop_features.py` | Parses the access log into 16 features per session and attaches the labels. |
| `src/prepare_creditcard.py` | Existing dataset: Kaggle *Credit Card Fraud* converted to the common format. |
| `src/subsample_creditcard.py` | Stratified random subsample (same anomaly ratio), used because OptIForest is too slow on all 284,807 rows. |
| `src/build_hdfs.py` | Second log dataset from LogHub (HDFS): Drain3 parsing, per-block features, published labels. |
| `scripts/run_shop_pipeline.sh` | Runs the whole shop pipeline end to end. |
| `notebooks/OptIForest_Recording_video.ipynb` | The notebook used for the project-update video (first version of the simulator). |

Common data format for the runners: a CSV with no header, features first, label last (1 = anomaly).

## Environment

Python 3.13 (Google Colab), NumPy 2.x, pandas, scikit-learn, drain3. `pip install -r requirements.txt`.

## Reproduction on the paper's data (AD, Internet Advertisements)

```bash
scripts/setup_authors_code.sh
cd OptIForest && python demo.py --dataset=ad --threshold=403 --branch=0
```
My run (Colab, 15 runs, 100 ensemblers): AUC score 0.7763 (std 0.0054), PR score 0.4590 (std 0.0342).
Paper Table 1 for AD: 77.4 (+/-0.7) and 43.8 (+/-3.1). "AUC score" is the mean AUC-ROC and "PR score" the mean AUC-PR of the demo output.

## New data

1. **Credit Card Fraud** (existing): download from Kaggle (`mlg-ulb/creditcardfraud`), unzip, `python src/prepare_creditcard.py`.
2. **Web shop logs** (constructed): `scripts/run_shop_pipeline.sh 42 15 200`.
3. **HDFS** (existing logs and labels, my parsing and features): `python src/build_hdfs.py`.

### About the web-shop dataset (read this before using it)

* Traffic is **simulated**: nine visitor types (4 legitimate including look-alikes such as a search-engine crawler, 5 attack types). About half of each attack type is "mild" so it blends in with normal traffic.
* Labels are **not human annotations**: each session's label is the behaviour the simulator injected. There is therefore no inter-annotator agreement to report.
* **Reproducibility:** `--seed` fixes the visitor types and every visitor's own sequence of requests (tested: same seed gives the same per-visitor requests, paths, status codes and sizes; a different seed gives different traffic). Response *delays* are real timing and are not seeded, so the timing features (`*_gap_s`, `*_ms`, `requests_per_s`, `duration_s`) vary slightly between runs and machines.
* The video used the first version of the simulator (one global seed, threads interleaved the random draws), so its numbers are not exactly reproducible. Final-report numbers come from this version.

## Results

Mean +/- standard deviation over runs. All numbers come from `results/*.json` (OptIForest and Isolation Forest) and are explained in the report. OptIForest has no random seed in the authors' code, so its runs are not bit-for-bit repeatable; Isolation Forest uses seeds 0 to 14.

| Dataset | OptIForest AUC-ROC | OptIForest AUC-PR | Isolation Forest AUC-ROC | Isolation Forest AUC-PR |
|---|---|---|---|---|
| AD (paper data), threshold 403, 15 runs | 0.772 +/- 0.006 | 0.435 +/- 0.043 | 0.683 +/- 0.018 | 0.378 +/- 0.058 |
| Web shop (simulated), threshold 100, 15 runs | 0.889 +/- 0.004 | 0.387 +/- 0.024 | 0.959 +/- 0.003 | 0.790 +/- 0.019 |
| HDFS logs, threshold 200, 5 runs (IF: 15) | 0.762 +/- 0.007 | 0.167 +/- 0.020 | 0.792 +/- 0.005 | 0.540 +/- 0.005 |
| Credit card fraud, all 284,807 rows | did not finish (see below) | did not finish | 0.949 +/- 0.002 | 0.137 +/- 0.024 |
| Credit card fraud, 30,000-row subsample (52 frauds) | did not finish | did not finish | 0.971 +/- 0.002 | 0.218 +/- 0.056 |

Paper Table 1 for AD (OptIForest): 77.4 +/- 0.7 (AUC-ROC) and 43.8 +/- 3.1 (AUC-PR). The authors' `demo.py` gave 77.63 +/- 0.54 and 45.90 +/- 3.42 in my run.

Web-shop cut thresholds tried for OptIForest: 403, 200 and 100 (threshold 50 was started but did not finish); the results are in `results/shop_optiforest_thr*.json`. Threshold 100 was chosen after seeing these results on the same labels, so it is slightly optimistic.

**Credit card, full data:** one OptIForest run on all 284,807 rows (threshold 200) had used more than 9 hours of CPU on Colab when the runtime was reset, so no result exists. Runs on 30,000- and 10,000-row subsamples (raw features, threshold 200) had printed no finished run after about 2.5 and 1.5 hours of CPU when the Colab runtime was reset. I did not find the cause; unscaled `Time` and `Amount` are one untested possibility (see the scaling section below). The subsample is made with `src/subsample_creditcard.py --n 30000 --seed 42` (same anomaly ratio as the full data).

## Known limitations

* OptIForest's cut threshold is a free parameter; the paper tunes it per dataset. I tried only a few values, so comparisons with Isolation Forest are preliminary.
* Everything is unsupervised and evaluated on the same data it is fitted on (as in the authors' demo).

## Feature scaling experiment (added 3 Nov 2026)
OptIForest's hash uses Euclidean distance, so unscaled features with large ranges can dominate; Isolation Forest is scale-invariant.
`src/standardise.py` standardises every column; results are in `results/scaling/` (web shop regenerated with seed 42, 5 runs, threshold 100; HDFS, 5 runs, threshold 200).

| Data | Setting | AUC-ROC | AUC-PR |
|---|---|---|---|
| Web shop (regenerated) | OptIForest raw, 5 runs | 0.892 +/- 0.001 | 0.382 +/- 0.011 |
| Web shop (regenerated) | OptIForest standardised, 5 runs | 0.962 +/- 0.002 | 0.834 +/- 0.011 |
| Web shop (regenerated) | Isolation Forest, 15 runs | 0.959 +/- 0.003 | 0.796 +/- 0.016 |
| HDFS | OptIForest standardised, 5 runs | 0.745 +/- 0.009 | 0.186 +/- 0.014 |
