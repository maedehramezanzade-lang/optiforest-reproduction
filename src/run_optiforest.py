"""OptIForest (the authors' code, in ./OptIForest after scripts/setup_authors_code.sh) on a dataset in the common format
(features..., label; no header). Same call style as the authors' demo.py: OptIForest('L2OPT', n_trees, threshold, branch).
Usage: python src/run_optiforest.py --data data/shop_logs.csv --name shop --runs 15 --threshold 200"""
import argparse, json, os, sys, time, warnings
import numpy as np, pandas as pd
from sklearn.metrics import roc_auc_score, average_precision_score
ap = argparse.ArgumentParser()
ap.add_argument('--data', required=True); ap.add_argument('--name', required=True)
ap.add_argument('--runs', type=int, default=15); ap.add_argument('--threshold', type=int, default=200)
ap.add_argument('--trees', type=int, default=100); ap.add_argument('--branch', type=int, default=0, help='0 = optimal branching factor (about e), as in the paper')
ap.add_argument('--authors-dir', default='OptIForest'); ap.add_argument('--results-dir', default='results')
a = ap.parse_args()
sys.path.insert(0, a.authors_dir)
warnings.filterwarnings("ignore")   # harmless divide-by-zero warning inside opt_tree.py (equal-sized sibling clusters)
from detectors import OptIForest
d = pd.read_csv(a.data, header=None).values
X, y = d[:, :-1], d[:, -1]
aucs, prs, tt = [], [], []
for j in range(a.runs):
    t0 = time.time()
    det = OptIForest('L2OPT', a.trees, a.threshold, a.branch)
    det.fit(X)
    s = -det.decision_function(X)
    aucs.append(roc_auc_score(y, s)); prs.append(average_precision_score(y, s)); tt.append(time.time() - t0)
    print(f"run {j+1}/{a.runs}: AUC-ROC={aucs[-1]:.4f}  AUC-PR={prs[-1]:.4f}  ({tt[-1]:.0f}s)", flush=True)
res = dict(dataset=a.name, method='OptIForest (authors code)', trees=a.trees, threshold=a.threshold, branch=a.branch,
           rows=int(len(y)), features=int(X.shape[1]), anomaly_ratio=float(y.mean()), runs=a.runs, auc_roc=aucs, auc_pr=prs, seconds_per_run=tt,
           auc_roc_mean=float(np.mean(aucs)), auc_roc_std=float(np.std(aucs)), auc_pr_mean=float(np.mean(prs)), auc_pr_std=float(np.std(prs)))
print(f"\nOptIForest on {a.name} (threshold {a.threshold}): AUC-ROC={res['auc_roc_mean']:.4f} +/- {res['auc_roc_std']:.4f}   AUC-PR={res['auc_pr_mean']:.4f} +/- {res['auc_pr_std']:.4f}")
os.makedirs(a.results_dir, exist_ok=True)
json.dump(res, open(os.path.join(a.results_dir, f'{a.name}_optiforest_thr{a.threshold}.json'), 'w'), indent=2)
