"""HDFS log dataset from LogHub/loglizer: published raw logs (100k messages) and published block labels.
Our work: parse messages into event types (Drain3), group by block ID, build features, merge labels, check.
Usage: python src/build_hdfs.py --out data/hdfs_log.csv   (needs: pip install drain3)"""
import argparse, os, re, urllib.request
from collections import defaultdict
import numpy as np, pandas as pd
from drain3 import TemplateMiner
ap = argparse.ArgumentParser(); ap.add_argument('--out', default='data/hdfs_log.csv'); ap.add_argument('--raw-dir', default='hdfs_raw')
a = ap.parse_args()
os.makedirs(a.raw_dir, exist_ok=True)
base = 'https://raw.githubusercontent.com/logpai/loglizer/master/data/HDFS/'
for f in ('HDFS_100k.log_structured.csv', 'anomaly_label.csv'):
    p = os.path.join(a.raw_dir, f)
    if not os.path.exists(p):
        urllib.request.urlretrieve(base + f, p)
logs   = pd.read_csv(os.path.join(a.raw_dir, 'HDFS_100k.log_structured.csv'))
labels = pd.read_csv(os.path.join(a.raw_dir, 'anomaly_label.csv'))
print("Log messages:", len(logs))
n_anom = int((labels['Label'] == 'Anomaly').sum())
print(f"Published labels: {len(labels):,} blocks, {n_anom:,} anomalous ({n_anom/len(labels):.2%})")
label_map = dict(zip(labels['BlockId'], labels['Label']))

# time in seconds (date + time of each log line)
stamp = pd.to_datetime(logs['Date'].astype(str).str.zfill(6) + logs['Time'].astype(str).str.zfill(6), format='%y%m%d%H%M%S')
secs = (stamp - stamp.min()).dt.total_seconds().values

tm = TemplateMiner()
block_re = re.compile(r'blk_-?\d+')
ip_re    = re.compile(r'\d+\.\d+\.\d+\.\d+')
size_re  = re.compile(r'size (\d+)')
counts  = defaultdict(lambda: defaultdict(int)); ips = defaultdict(set); sizes = defaultdict(list); times = defaultdict(list); has_exc = defaultdict(int)
for content, t in zip(logs['Content'].astype(str), secs):
    cid = tm.add_log_message(content)['cluster_id']
    for b in block_re.findall(content):
        counts[b][cid] += 1
        ips[b].update(ip_re.findall(content))
        times[b].append(t)
        m = size_re.search(content)
        if m:
            sizes[b].append(int(m.group(1)))
        if 'xception' in content:
            has_exc[b] = 1
n_t = len(tm.drain.clusters)
print("Event types found by Drain3:", n_t, "| blocks:", len(counts))

rows, y = [], []
for b in counts:
    if b not in label_map:
        continue
    ev = [counts[b].get(i, 0) for i in range(1, n_t + 1)]
    span = (max(times[b]) - min(times[b])) if len(times[b]) > 1 else 0
    avg_size = np.mean(sizes[b]) if sizes[b] else 0
    rows.append(ev + [len(ips[b]), avg_size / 1e6, span / 100, has_exc[b], sum(ev)])
    y.append(1 if label_map[b] == 'Anomaly' else 0)
X = np.array(rows, dtype=float); y = np.array(y)
print("Dataset shape:", X.shape, "(rows = blocks, columns = features)")
print("Anomalies:", int(y.sum()), "| Normal:", int((y == 0).sum()), f"| anomaly ratio: {y.mean():.2%}")
os.makedirs(os.path.dirname(a.out) or '.', exist_ok=True)
pd.DataFrame(np.hstack([X, y.reshape(-1, 1)])).to_csv(a.out, header=False, index=False)
print("Saved", a.out)
