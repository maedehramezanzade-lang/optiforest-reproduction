"""scikit-learn Isolation Forest baseline on a dataset in the common format (features..., label; no header).
Repeated with several seeds so a mean and standard deviation can be reported.
Usage: python src/run_baseline_iforest.py --data data/shop_logs.csv --runs 15 --name shop"""
import argparse, json, os, time
import numpy as np, pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.metrics import roc_auc_score, average_precision_score
ap = argparse.ArgumentParser()
ap.add_argument('--data', required=True); ap.add_argument('--runs', type=int, default=15); ap.add_argument('--name', required=True)
ap.add_argument('--results-dir', default='results')
a = ap.parse_args()
d = pd.read_csv(a.data, header=None).values
X, y = d[:, :-1], d[:, -1]
aucs, prs = [], []
for seed in range(a.runs):
    t0 = time.time()
    s = -IsolationForest(n_estimators=100, random_state=seed).fit(X).decision_function(X)
    aucs.append(roc_auc_score(y, s)); prs.append(average_precision_score(y, s))
    print(f"run {seed+1}/{a.runs}: AUC-ROC={aucs[-1]:.4f}  AUC-PR={prs[-1]:.4f}  ({time.time()-t0:.1f}s)", flush=True)
res = dict(dataset=a.name, method='IsolationForest (scikit-learn)', rows=int(len(y)), features=int(X.shape[1]), anomaly_ratio=float(y.mean()),
           runs=a.runs, auc_roc=aucs, auc_pr=prs, auc_roc_mean=float(np.mean(aucs)), auc_roc_std=float(np.std(aucs)),
           auc_pr_mean=float(np.mean(prs)), auc_pr_std=float(np.std(prs)))
print(f"\nIsolation Forest on {a.name}: AUC-ROC={res['auc_roc_mean']:.4f} +/- {res['auc_roc_std']:.4f}   AUC-PR={res['auc_pr_mean']:.4f} +/- {res['auc_pr_std']:.4f}")
os.makedirs(a.results_dir, exist_ok=True)
json.dump(res, open(os.path.join(a.results_dir, f'{a.name}_iforest.json'), 'w'), indent=2)
