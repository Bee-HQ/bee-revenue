#!/usr/bin/env bash
# Start video editor in production mode (single server, built frontend)
# Kills any previous instances, finds open port if default is taken.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

PORT=${PORT:-8420}

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
    pkill -f "bee-video serve" 2>/dev/null || true
    pkill -f "uvicorn.*bee_video" 2>/dev/null || true
    sleep 0.5
}

# --- main ---

echo "Killing previous instances..."
kill_previous

# Build frontend if needed
if [ ! -d "web/dist" ] || [ "${BUILD:-0}" = "1" ]; then
    echo "Building frontend..."
    cd web
    npm install --include=dev
    npm run build
    cd ..
fi

PORT=$(find_open_port "$PORT")

echo "Starting Bee Video Editor on :$PORT"
echo "http://localhost:$PORT"
echo ""

exec uv run bee-video serve --port "$PORT"
