#!/bin/bash
set -e
cd "$(dirname "$0")"

BACKEND_PORT=${BACKEND_PORT:-8420}
FRONTEND_PORT=${FRONTEND_PORT:-5173}

# Kill previous instances
lsof -ti:$BACKEND_PORT | xargs kill -9 2>/dev/null || true
lsof -ti:$FRONTEND_PORT | xargs kill -9 2>/dev/null || true

echo "Starting Express backend on :$BACKEND_PORT..."
PORT=$BACKEND_PORT npx tsx watch server/index.ts &

echo "Starting Vite frontend on :$FRONTEND_PORT..."
VITE_API_PORT=$BACKEND_PORT npm run dev
