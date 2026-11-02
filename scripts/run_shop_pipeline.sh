#!/usr/bin/env bash
# Build the web-shop dataset from scratch and run both detectors. Usage: scripts/run_shop_pipeline.sh [SEED] [RUNS] [THRESHOLD]
set -euo pipefail
cd "$(dirname "$0")/.."
SEED=${1:-42}; RUNS=${2:-15}; THR=${3:-200}
python src/shop_sim.py --seed "$SEED" --out-dir sim_out            # collection  (~2 min)
python src/build_shop_features.py --in-dir sim_out --out data/shop_logs.csv   # preprocessing + annotation (labels come from the simulator)
python src/run_baseline_iforest.py --data data/shop_logs.csv --runs "$RUNS" --name shop
python src/run_optiforest.py --data data/shop_logs.csv --name shop --runs "$RUNS" --threshold "$THR"   # slow: about 1 minute per run
