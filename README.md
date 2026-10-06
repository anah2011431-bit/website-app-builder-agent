#!/bin/bash

set -e

echo "Starting Website App Builder..."

if [ ! -d "backend/.venv" ]; then
  echo "Creating backend virtual environment..."
  cd backend
  python3 -m venv .venv
  . .venv/bin/activate
  pip install -r requirements.txt
  cd ..
fi

cd backend
. .venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000
