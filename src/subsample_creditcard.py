"""Stratified random subsample of a dataset in the common format (features..., label; no header).
Keeps the anomaly ratio of the full data. Used because OptIForest (authors' code) did not finish one run on all
284,807 credit card rows within about 9 hours of CPU time.
Usage: python src/subsample_creditcard.py --in data/creditcard.csv --out data/creditcard_30k.csv --n 30000 --seed 42"""
import argparse, os
import numpy as np, pandas as pd
ap = argparse.ArgumentParser()
ap.add_argument('--in', dest='inp', default='data/creditcard.csv'); ap.add_argument('--out', default='data/creditcard_30k.csv')
ap.add_argument('--n', type=int, default=30000); ap.add_argument('--seed', type=int, default=42)
a = ap.parse_args()
d = pd.read_csv(a.inp, header=None)
y = d.iloc[:, -1]
n_anom = int(round(a.n * y.mean()))
rng = np.random.RandomState(a.seed)
idx = np.concatenate([rng.choice(d.index[y == 1], n_anom, replace=False),
                      rng.choice(d.index[y == 0], a.n - n_anom, replace=False)])
rng.shuffle(idx)
os.makedirs(os.path.dirname(a.out) or '.', exist_ok=True)
d.loc[idx].to_csv(a.out, header=False, index=False)
print(f'Full: {len(d)} rows, {int(y.sum())} anomalies ({y.mean():.5f}). Subsample: {len(idx)} rows, {n_anom} anomalies. Saved {a.out}')
