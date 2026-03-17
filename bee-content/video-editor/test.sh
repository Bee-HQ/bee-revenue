#!/usr/bin/env bash
# Run all tests: backend (pytest) + frontend (tsc type check)
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

FAILED=0

echo "=== Backend tests ==="
if uv run --extra dev pytest tests/ -v "$@"; then
    echo "✓ Backend tests passed"
else
    echo "✗ Backend tests failed"
    FAILED=1
fi

echo ""
echo "=== Frontend type check ==="
if (cd web && npx tsc --noEmit); then
    echo "✓ Frontend types OK"
else
    echo "✗ Frontend type check failed"
    FAILED=1
fi

echo ""
if [ $FAILED -eq 0 ]; then
    echo "All checks passed."
else
    echo "Some checks failed."
    exit 1
fi
