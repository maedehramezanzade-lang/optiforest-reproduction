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

To be filled in from `results/*.json` after the final runs (15 runs each; OptIForest threshold tuned on the shop logs with a stated protocol). Not final yet.

| Dataset | OptIForest AUC-ROC | OptIForest AUC-PR | Isolation Forest AUC-ROC | Isolation Forest AUC-PR |
|---|---|---|---|---|
| AD (paper) | 0.7763 | 0.4590 | - | - |
| Web shop (simulated) | tbd | tbd | tbd | tbd |
| Credit card | tbd | tbd | tbd | tbd |
| HDFS | tbd | tbd | tbd | tbd |

## Known limitations

* OptIForest's cut threshold is a free parameter; the paper tunes it per dataset. Until tuned, comparisons with Isolation Forest are preliminary.
* Everything is unsupervised and evaluated on the same data it is fitted on (as in the authors' demo).
