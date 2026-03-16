#!/usr/bin/env bash
# Start video editor in dev mode (backend + frontend with hot reload)
# Kills any previous instances, finds open ports if defaults are taken.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

BACKEND_PORT=${BACKEND_PORT:-8420}
FRONTEND_PORT=${FRONTEND_PORT:-5173}

# --- helpers ---

find_open_port() {
    local port=$1
    while lsof -iTCP:"$port" -sTCP:LISTEN &>/dev/null 2>&1 || ss -tlnp 2>/dev/null | grep -q ":$port "; do
        echo "Port $port in use, trying $((port + 1))..." >&2
        port=$((port + 1))
    done
    echo "$port"
}

kill_previous() {
    # Kill previous bee-video serve instances
    pkill -f "bee-video serve" 2>/dev/null || true
    pkill -f "uvicorn.*bee_video" 2>/dev/null || true
    # Kill previous vite dev servers in this project
    pkill -f "vite.*--port" 2>/dev/null || true
    pkill -f "node.*vite" 2>/dev/null || true
    sleep 0.5
}

cleanup() {
    echo ""
    echo "Shutting down..."
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    wait 2>/dev/null
}

# --- main ---

echo "Killing previous instances..."
kill_previous

BACKEND_PORT=$(find_open_port "$BACKEND_PORT")
FRONTEND_PORT=$(find_open_port "$FRONTEND_PORT")

trap cleanup EXIT INT TERM

# Start backend
echo "Starting backend on :$BACKEND_PORT"
uv run bee-video serve --dev --port "$BACKEND_PORT" &
BACKEND_PID=$!

# Start frontend with matching proxy
echo "Starting frontend on :$FRONTEND_PORT (proxying API to :$BACKEND_PORT)"
cd web
VITE_API_PORT=$BACKEND_PORT npx vite --port "$FRONTEND_PORT" --strictPort false &
FRONTEND_PID=$!
cd ..

echo ""
echo "Editor:  http://localhost:$FRONTEND_PORT"
echo "API:     http://localhost:$BACKEND_PORT"
echo "Press Ctrl+C to stop"
echo ""

wait
