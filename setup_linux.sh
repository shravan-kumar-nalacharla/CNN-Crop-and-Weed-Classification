#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
command -v python3.11 >/dev/null || { echo 'Install Python 3.11 and its venv package first.'; exit 1; }
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements-local.txt
python -m ipykernel install --user --name crop-weed-vgg16 --display-name 'Crop Weed VGG16'
python scripts/verify_environment.py
