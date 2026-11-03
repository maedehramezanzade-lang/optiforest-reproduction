"""Standardise every feature column (zero mean, unit variance) of a dataset in the common format (features..., label; no header).
Usage: python src/standardise.py --in data/shop_logs.csv --out data/shop_scaled.csv"""
import argparse, numpy as np, pandas as pd
ap = argparse.ArgumentParser(); ap.add_argument('--in', dest='inp', required=True); ap.add_argument('--out', required=True)
a = ap.parse_args()
d = pd.read_csv(a.inp, header=None).values
X, y = d[:, :-1], d[:, -1]
s = X.std(0); s[s == 0] = 1
pd.DataFrame(np.c_[(X - X.mean(0)) / s, y]).to_csv(a.out, header=False, index=False)
