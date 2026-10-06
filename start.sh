#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

if [ ! -d "backend/.venv" ]; then
  echo "Creating backend virtual environment..."
  python3 -m venv backend/.venv
fi

source backend/.venv/bin/activate
python -m pip install --upgrade pip
pip install -r backend/requirements.txt
cd backend
python main.py
