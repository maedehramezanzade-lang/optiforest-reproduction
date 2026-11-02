"""Preprocessing for the web-shop dataset: parse access.log, compute 16 features per session (one session = one client),
attach the simulator's labels, save the dataset.   Usage: python src/build_shop_features.py --in-dir sim_out --out data/shop_logs.csv"""
import argparse, os
ap = argparse.ArgumentParser()
ap.add_argument('--in-dir', default='sim_out')
ap.add_argument('--out', default='data/shop_logs.csv')
args = ap.parse_args()
import re, numpy as np, pandas as pd
from datetime import datetime

line_re = re.compile(r'^(\S+) - - \[(.+?)\] "(\S+) (\S+) HTTP/1.1" (\d{3}) (\d+) ([\d.]+)$')
rows = []
for line in open(os.path.join(args.in_dir,'access.log')):
    m = line_re.match(line.strip())
    if m:
        client, ts, method, path, status, nbytes, ms = m.groups()
        rows.append((client, datetime.strptime(ts, '%d/%b/%Y:%H:%M:%S.%f').timestamp(), method, path, int(status), int(nbytes), float(ms)))
log = pd.DataFrame(rows, columns=['client', 'time', 'method', 'path', 'status', 'bytes', 'ms']).sort_values(['client', 'time'])
log['template'] = log['path'].str.replace(r'\?.*', '', regex=True).str.replace(r'\d+', '<n>', regex=True)
log['gap'] = log.groupby('client')['time'].diff()          # seconds since the same visitor's previous request
print("Parsed requests:", len(log), "| sessions (clients):", log['client'].nunique())

def entropy(s):
    p = s.value_counts(normalize=True).values
    return float(-(p * np.log2(p)).sum())

g = log.groupby('client')
feat = pd.DataFrame({
    'n_requests':     g.size(),
    'duration_s':     g['time'].max() - g['time'].min(),
    'n_paths':        g['path'].nunique(),
    'n_templates':    g['template'].nunique(),
    'path_entropy':   g['template'].apply(entropy),
    'frac_post':      g['method'].apply(lambda s: (s == 'POST').mean()),
    'n_401':          g['status'].apply(lambda s: (s == 401).sum()),
    'n_404':          g['status'].apply(lambda s: (s == 404).sum()),
    'frac_error':     g['status'].apply(lambda s: (s >= 400).mean()),
    'mean_gap_s':     g['gap'].mean(),
    'std_gap_s':      g['gap'].std(),
    'min_gap_s':      g['gap'].min(),
    'mean_ms':        g['ms'].mean(),
    'max_ms':         g['ms'].max(),
    'mean_kbytes':    g['bytes'].mean() / 1000,
})
feat['requests_per_s'] = feat['n_requests'] / feat['duration_s'].clip(lower=0.05)
feat = feat.fillna(0)

labels = pd.read_csv(os.path.join(args.in_dir,'labels.csv')).set_index('client')
data = feat.join(labels, how='inner')
y = data['is_attack'].values
X = data.drop(columns=['behaviour', 'is_attack']).values.astype(float)
print("Dataset shape:", X.shape, "(rows = sessions, columns = features)")
print("Attacks:", int(y.sum()), "| Normal:", int((y == 0).sum()), f"| attack ratio: {y.mean():.2%}")
print("Distinct feature patterns:", pd.DataFrame(X).drop_duplicates().shape[0], "out of", len(X))
os.makedirs(os.path.dirname(args.out) or '.', exist_ok=True)
pd.DataFrame(np.hstack([X, y.reshape(-1, 1)])).to_csv(args.out, header=False, index=False)   # format expected by the runners: features..., label (1 = attack)
named = data.reset_index().rename(columns={'client': 'client_ip'})
named.to_csv(args.out.replace('.csv', '_named.csv'), index=False)                          # same data with column names, for inspection and report snippets
print('Saved', args.out, 'and', args.out.replace('.csv', '_named.csv'), '; features:', list(data.columns[:-2]))
