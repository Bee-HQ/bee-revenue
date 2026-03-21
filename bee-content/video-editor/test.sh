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
echo "=== Frontend unit tests ==="
if (cd web && npm test); then
    echo "✓ Frontend unit tests passed"
else
    echo "✗ Frontend unit tests failed"
    FAILED=1
fi

# E2E tests (optional — pass --e2e flag to include)
if [[ "${1:-}" == "--e2e" ]]; then
    echo ""
    echo "=== Frontend E2E tests ==="
    if (cd web && npm run test:e2e); then
        echo "✓ E2E tests passed"
    else
        echo "✗ E2E tests failed"
        FAILED=1
    fi
fi

echo ""
if [ $FAILED -eq 0 ]; then
    echo "All checks passed."
else
    echo "Some checks failed."
    exit 1
fi
