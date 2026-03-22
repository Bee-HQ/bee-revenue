#!/bin/bash
set -e
cd "$(dirname "$0")"

PORT=${PORT:-8420}

# Build frontend if needed
if [[ "$BUILD" == "1" ]] || [[ ! -d dist ]]; then
  echo "Building frontend..."
  npm run build
fi

echo "Starting Bee Video Editor on :$PORT..."
STATIC_DIR=dist PORT=$PORT npx tsx server/index.ts
