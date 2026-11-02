#!/usr/bin/env bash
# Get the authors' original OptIForest code and apply the one compatibility fix it needs on NumPy 2.
set -euo pipefail
cd "$(dirname "$0")/.."
[ -d OptIForest ] || git clone https://github.com/xiagll/OptIForest.git
# np.mat was removed in NumPy 2.0; np.asmatrix is the identical replacement.
sed -i 's/np\.mat(/np.asmatrix(/g' OptIForest/detectors/opt_forest.py OptIForest/detectors/opt_tree.py
grep -n "asmatrix" OptIForest/detectors/*.py
echo "Authors' code ready in ./OptIForest"
