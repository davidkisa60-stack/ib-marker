#!/usr/bin/env bash
# IB Marker launcher for Mac and Linux. Run:  ./run.sh
set -e
cd "$(dirname "$0")"

if command -v python3 >/dev/null 2>&1; then PY=python3
elif command -v python >/dev/null 2>&1; then PY=python
else
  echo "Python 3 was not found."
  echo "Install it from https://www.python.org/downloads/ (on a Mac: brew install python) and run this script again."
  exit 1
fi
echo "Found $($PY --version 2>&1)"

if ! $PY -c 'import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)'; then
  echo "This Python is older than 3.10. Please install a newer version and run this script again."
  exit 1
fi

if [ ! -x ".venv/bin/python" ]; then
  echo "Creating a private Python environment in .venv ..."
  if ! $PY -m venv .venv; then
    echo "Could not create a virtual environment."
    echo "On Debian/Ubuntu run:  sudo apt install python3-venv   and try again."
    exit 1
  fi
fi
VPY=".venv/bin/python"

echo "Installing required packages (takes a minute the first time)..."
"$VPY" -m pip install --quiet --disable-pip-version-check -r requirements.txt

echo
echo "Starting IB Marker. Keep this terminal open while you use the app."
echo "It will open in your browser at http://localhost:8000"
echo "Press Ctrl+C to stop."
echo
( sleep 4; open http://localhost:8000 2>/dev/null || xdg-open http://localhost:8000 2>/dev/null || true ) &
exec "$VPY" -m uvicorn app.main:app --host 0.0.0.0 --port 8000
