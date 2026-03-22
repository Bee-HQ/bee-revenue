#!/bin/bash
set -e
cd "$(dirname "$0")"

PORT=${PORT:-8420}

# Clean Vite cache
rm -rf node_modules/.vite

# Build frontend (always rebuild to avoid stale assets)
echo "Building frontend..."
npm run build

echo "Starting Bee Video Editor on :$PORT..."
STATIC_DIR=dist PORT=$PORT npx tsx server/index.ts
