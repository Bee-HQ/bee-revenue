#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

echo "=== Installing Python dependencies ==="
uv sync --extra dev --extra web

echo ""
echo "=== Installing frontend dependencies ==="
cd web
npm install

echo ""
echo "=== Building frontend ==="
npm run build

echo ""
echo "Done. Run with: uv run bee-video serve"
