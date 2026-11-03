#!/bin/bash
# Rebuild processed data, notebooks, and executed notebooks, in order.
set -e
cd "$(dirname "$0")/.."
python scripts/download_data.py
python scripts/build_processed.py
python scripts/build_notebooks.py
python -m nbconvert --to notebook --execute --inplace notebooks/*.ipynb
cp charts/*.png docs/charts/
echo "rebuild complete: 6 notebooks, 16 charts"
