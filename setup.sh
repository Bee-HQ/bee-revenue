#!/usr/bin/env bash
#
# OpenClaw Revenue — Setup Script
# Sets up all bee-content tools on a fresh machine.
#
# Usage:
#   ./setup.sh           # install everything
#   ./setup.sh research  # install only bee-research
#   ./setup.sh auto      # install only bee-auto
#   ./setup.sh video     # install only bee-video
#   ./setup.sh test      # run all tests
#
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")" && pwd)"
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

info()  { echo -e "${BLUE}[info]${NC} $1"; }
ok()    { echo -e "${GREEN}[ok]${NC} $1"; }
warn()  { echo -e "${YELLOW}[warn]${NC} $1"; }
fail()  { echo -e "${RED}[fail]${NC} $1"; exit 1; }

# ── Prerequisites ─────────────────────────────────────────────

install_hint() {
    # Returns platform-appropriate install command
    local pkg="$1"
    if [[ "$(uname)" == "Darwin" ]]; then
        echo "brew install $pkg"
    elif command -v apt-get &>/dev/null; then
        echo "sudo apt-get install $pkg"
    elif command -v dnf &>/dev/null; then
        echo "sudo dnf install $pkg"
    elif command -v pacman &>/dev/null; then
        echo "sudo pacman -S $pkg"
    else
        echo "(install $pkg via your package manager)"
    fi
}

check_prereqs() {
    info "Checking prerequisites..."
    info "Platform: $(uname -s) $(uname -m)"

    # Python 3.11+
    if command -v python3 &>/dev/null; then
        PY_VER=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
        PY_MAJOR=$(echo "$PY_VER" | cut -d. -f1)
        PY_MINOR=$(echo "$PY_VER" | cut -d. -f2)
        if [ "$PY_MAJOR" -ge 3 ] && [ "$PY_MINOR" -ge 11 ]; then
            ok "Python $PY_VER"
        else
            fail "Python 3.11+ required (found $PY_VER). Install via: $(install_hint python3)"
        fi
    else
        fail "Python not found. Install via: $(install_hint python3)"
    fi

    # uv
    if command -v uv &>/dev/null; then
        ok "uv $(uv --version 2>/dev/null | head -1)"
    else
        warn "uv not found. Installing..."
        curl -LsSf https://astral.sh/uv/install.sh | sh
        export PATH="$HOME/.local/bin:$PATH"
        ok "uv installed"
    fi

    # git
    if command -v git &>/dev/null; then
        ok "git $(git --version | awk '{print $3}')"
    else
        fail "git not found. Install via: $(install_hint git)"
    fi

    # ffmpeg (optional, for video-editor)
    if command -v ffmpeg &>/dev/null; then
        ok "ffmpeg $(ffmpeg -version 2>&1 | head -1 | awk '{print $3}')"
    else
        warn "ffmpeg not found (needed for bee-video). Install via: $(install_hint ffmpeg)"
    fi

    # node/npm (optional, for video-editor web UI)
    if command -v node &>/dev/null; then
        ok "node $(node --version)"
    else
        warn "node not found (needed for bee-video web UI). Install via: $(install_hint nodejs)"
    fi
}

# ── Project Installers ────────────────────────────────────────

install_research() {
    local dir="$REPO_ROOT/bee-content/research"
    if [ ! -f "$dir/pyproject.toml" ]; then
        warn "bee-content/research not found, skipping"
        return
    fi
    info "Installing bee-research (YouTube competitor analysis)..."
    cd "$dir"
    uv sync --all-extras 2>/dev/null
    ok "bee-research installed"
    echo "  CLI: uv run bee-research --help"
    echo "  MCP: uv run bee-research-mcp"
}

install_automation() {
    local dir="$REPO_ROOT/bee-content/automation"
    if [ ! -f "$dir/pyproject.toml" ]; then
        warn "bee-content/automation not found, skipping"
        return
    fi
    info "Installing bee-auto (content pipeline)..."
    cd "$dir"
    uv sync --all-extras 2>/dev/null
    ok "bee-auto installed"
    echo "  CLI: uv run bee-auto --help"
}

install_video() {
    local dir="$REPO_ROOT/bee-content/video-editor"
    if [ ! -f "$dir/pyproject.toml" ]; then
        warn "bee-content/video-editor not found, skipping"
        return
    fi
    info "Installing bee-video (video production)..."
    cd "$dir"
    uv sync --all-extras 2>/dev/null
    ok "bee-video Python deps installed"

    # Frontend (Node/npm)
    if [ -d "$dir/web" ]; then
        if command -v node &>/dev/null && command -v npm &>/dev/null; then
            info "Installing bee-video web frontend..."
            cd "$dir/web"
            npm install --include=dev
            npm run build
            ok "bee-video web UI built"
        else
            warn "node/npm not found — skipping web UI build"
            echo "  Install Node.js 18+ to enable the web editor"
        fi
    fi

    echo "  CLI: uv run bee-video --help"
    echo "  Web: uv run bee-video serve"
}

# ── Environment Setup ─────────────────────────────────────────

setup_env() {
    info "Checking environment variables..."

    if [ -n "${ANTHROPIC_API_KEY:-}" ]; then
        ok "ANTHROPIC_API_KEY is set"
    else
        warn "ANTHROPIC_API_KEY not set — needed for:"
        echo "  - bee-research review (script review agent)"
        echo "  - bee-auto script generation"
        echo "  Set it: export ANTHROPIC_API_KEY=sk-ant-..."
    fi

    # Create data directory for bee-research
    mkdir -p "$HOME/.bee-content-research"
    ok "Data directory: ~/.bee-content-research/"
}

# ── Test Runner ───────────────────────────────────────────────

run_tests() {
    local failed=0

    for project in research automation video-editor; do
        local dir="$REPO_ROOT/bee-content/$project"
        if [ ! -f "$dir/pyproject.toml" ]; then
            continue
        fi
        info "Testing bee-content/$project..."
        cd "$dir"
        if uv run pytest tests/ -v --tb=short 2>&1; then
            ok "bee-content/$project — all tests passed"
        else
            warn "bee-content/$project — some tests failed"
            failed=1
        fi
    done

    if [ "$failed" -eq 0 ]; then
        ok "All tests passed!"
    else
        warn "Some tests failed — check output above"
    fi
}

# ── CLI Verification ──────────────────────────────────────────

verify() {
    info "Verifying CLI tools..."
    local all_ok=1

    cd "$REPO_ROOT/bee-content/research" 2>/dev/null && \
        uv run bee-research --help &>/dev/null && ok "bee-research" || { warn "bee-research not working"; all_ok=0; }

    cd "$REPO_ROOT/bee-content/automation" 2>/dev/null && \
        uv run bee-auto --help &>/dev/null && ok "bee-auto" || { warn "bee-auto not working"; all_ok=0; }

    cd "$REPO_ROOT/bee-content/video-editor" 2>/dev/null && \
        uv run bee-video --help &>/dev/null && ok "bee-video" || { warn "bee-video not working"; all_ok=0; }

    if [ "$all_ok" -eq 1 ]; then
        ok "All tools verified!"
    fi
}

# ── Main ──────────────────────────────────────────────────────

print_summary() {
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  OpenClaw Revenue — Setup Complete"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "  Tools installed:"
    echo "    bee-research  — YouTube competitor analysis"
    echo "    bee-auto      — Anime content pipeline"
    echo "    bee-video     — Video production"
    echo ""
    echo "  Usage (run from each project dir):"
    echo "    cd bee-content/research   && uv run bee-research --help"
    echo "    cd bee-content/automation && uv run bee-auto --help"
    echo "    cd bee-content/video-editor && uv run bee-video --help"
    echo "    cd bee-content/video-editor && uv run bee-video serve"
    echo ""
    echo "  Run tests:"
    echo "    ./setup.sh test"
    echo ""
    echo "  Docs:"
    echo "    bee-content/discovery/    — research by genre"
    echo "    bee-content/research/CLAUDE.md — full CLI reference"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
}

main() {
    local target="${1:-all}"

    echo ""
    echo "  OpenClaw Revenue — Setup"
    echo ""

    case "$target" in
        research)
            check_prereqs
            setup_env
            install_research
            ;;
        auto|automation)
            check_prereqs
            setup_env
            install_automation
            ;;
        video|video-editor)
            check_prereqs
            setup_env
            install_video
            ;;
        test|tests)
            run_tests
            ;;
        verify)
            verify
            ;;
        all)
            check_prereqs
            setup_env
            install_research
            install_automation
            install_video
            verify
            print_summary
            ;;
        *)
            echo "Usage: ./setup.sh [research|auto|video|test|verify|all]"
            exit 1
            ;;
    esac
}

main "$@"
