#!/usr/bin/env bash
set -e
export PYTHONPATH="${PYTHONPATH:-.}"
echo "Python: $(python --version)"
echo "PORT=${PORT:-unset}"
echo "PWD=$(pwd)"
echo "Listing root:"
ls -la
echo "Trying import app.main..."
python -c "from app.main import app; print('import OK:', app.title)" || {
  echo "IMPORT FAILED"
  python -c "import traceback; traceback.print_exc()" 2>&1 || true
  exit 1
}
echo "Starting uvicorn..."
exec python -m uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"
