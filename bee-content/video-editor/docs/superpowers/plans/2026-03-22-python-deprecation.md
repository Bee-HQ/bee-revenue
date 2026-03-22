# Python Web Server Deprecation — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Remove all Python web server code — the Node.js Express server is the sole backend for the web editor.

**Architecture:** Delete the FastAPI API directory, remove the `serve` CLI command, drop `web` optional deps, update all docs and scripts. Python CLI (`bee-video`) keeps working for everything except `serve`.

**Tech Stack:** Shell scripts, markdown docs, pyproject.toml

**Spec:** `docs/superpowers/specs/2026-03-22-python-deprecation-design.md`

---

## File Map

| File | Action | Responsibility |
|------|--------|----------------|
| `src/bee_video_editor/api/` | Delete | Entire FastAPI backend (9 files) |
| `src/bee_video_editor/adapters/cli.py` | Modify | Remove `serve()` command (lines 566-602) |
| `tests/test_api.py` | Delete | Tests for deleted FastAPI routes |
| `pyproject.toml` | Modify | Remove `web` extras (line 33) |
| `dev.sh` (parent) | Modify | Replace Python server with Node.js |
| `.github/workflows/ci.yml` | Modify | Remove `--extra web` (lines 50, 63) |
| `setup.sh` | Modify | Update echo lines (lines 170, 256) |
| `README.md` | Modify | Update web editor section |
| `CLAUDE.md` (video-editor) | Modify | Remove `bee-video serve` references |
| `.claude/commands/true-crime/generate-storyboard.md` | Modify | Update line 181 |
| `.claude/commands/true-crime/review-storyboard.md` | Modify | Update line 136 |
| `bee-content/discovery/true-crime/research/screenplay-storyboard-formula.md` | Modify | Update line 911 |

---

### Task 1: Delete Python API directory and tests

**Files:**
- Delete: `src/bee_video_editor/api/` (entire directory)
- Delete: `tests/test_api.py`

- [ ] **Step 1: Delete the API directory**

```bash
rm -rf src/bee_video_editor/api/
```

- [ ] **Step 2: Delete the API test file**

```bash
rm tests/test_api.py
```

- [ ] **Step 3: Check for imports from the deleted module**

```bash
cd bee-content/video-editor
grep -r "from bee_video_editor.api" src/ tests/ --include="*.py" | grep -v __pycache__
```

Expected: only `adapters/cli.py` references (the `serve` command, removed in Task 2).

- [ ] **Step 4: Commit**

```bash
git add -A src/bee_video_editor/api/ tests/test_api.py
git commit -m "chore: remove Python FastAPI backend and API tests"
```

---

### Task 2: Remove `serve` command from CLI

**Files:**
- Modify: `src/bee_video_editor/adapters/cli.py` (remove lines 566-602)

- [ ] **Step 1: Remove the `serve()` function**

Delete the entire `@app.command() def serve(...)` block (lines 566-602) and any serve-only imports at the top of the file.

- [ ] **Step 2: Verify CLI still works**

```bash
uv run bee-video --help
```

Expected: all commands listed except `serve`.

- [ ] **Step 3: Run Python tests**

```bash
uv run --extra dev pytest tests/ -v --timeout=30
```

Expected: all remaining tests pass (test_api.py already deleted).

- [ ] **Step 4: Commit**

```bash
git add src/bee_video_editor/adapters/cli.py
git commit -m "chore: remove serve command from CLI"
```

---

### Task 3: Drop `web` optional dependencies

**Files:**
- Modify: `pyproject.toml` (remove line 33)
- Modify: `.github/workflows/ci.yml` (remove `--extra web` from lines 50, 63)

- [ ] **Step 1: Remove `web` extras from pyproject.toml**

Delete the line:
```toml
web = ["fastapi>=0.115.0", "uvicorn[standard]>=0.34.0", "python-multipart>=0.0.9"]
```

- [ ] **Step 2: Remove `--extra web` from CI**

In `.github/workflows/ci.yml`, change both occurrences (lines 50 and 63):
```yaml
# Before:
uv sync --extra dev --extra web --extra animation --extra maps
# After:
uv sync --extra dev --extra animation --extra maps
```

- [ ] **Step 3: Verify uv sync works without web extras**

```bash
uv sync --extra dev
```

Expected: no errors, no fastapi/uvicorn installed.

- [ ] **Step 4: Commit**

```bash
git add pyproject.toml .github/workflows/ci.yml
git commit -m "chore: drop web optional dependencies (fastapi, uvicorn)"
```

---

### Task 4: Update dev.sh (parent)

**Files:**
- Modify: `bee-content/video-editor/dev.sh`

- [ ] **Step 1: Replace Python server launch with Node.js**

The `dev.sh` at the video-editor root should:
- Kill previous instances (both Python and Node.js)
- Start Express backend with `npx tsx watch server/index.ts`
- Start Vite frontend with `npm run dev`

Replace `uv run bee-video serve --dev --port "$BACKEND_PORT"` (line 53) with:
```bash
cd web && PORT=$BACKEND_PORT npx tsx watch server/index.ts &
```

Update the kill commands (lines 24-26) to also kill `tsx` processes:
```bash
pkill -f "tsx.*server/index" 2>/dev/null || true
```

- [ ] **Step 2: Test dev.sh starts correctly**

```bash
cd bee-content/video-editor && ./dev.sh &
sleep 3
curl -s http://localhost:8420/api/health
kill %1
```

Expected: `{"status":"ok"}`

- [ ] **Step 3: Commit**

```bash
git add dev.sh
git commit -m "chore: dev.sh uses Node.js Express instead of Python"
```

---

### Task 5: Update documentation

**Files:**
- Modify: `bee-content/video-editor/README.md`
- Modify: `bee-content/video-editor/CLAUDE.md`
- Modify: `setup.sh`
- Modify: `.claude/commands/true-crime/generate-storyboard.md`
- Modify: `.claude/commands/true-crime/review-storyboard.md`
- Modify: `bee-content/discovery/true-crime/research/screenplay-storyboard-formula.md`

- [ ] **Step 1: Update README.md**

Replace `uv run bee-video serve --dev` (line 38) with:
```bash
cd web && ./dev.sh     # Dev mode (Express + Vite hot reload)
```

- [ ] **Step 2: Update CLAUDE.md (video-editor)**

Remove any remaining `bee-video serve` references. Ensure the web editor section points to `web/dev.sh` and `web/start.sh` only.

- [ ] **Step 3: Update setup.sh**

Line 170: `echo "  Web: cd bee-content/video-editor && ./start.sh"`
Line 256: `echo "    cd bee-content/video-editor && ./start.sh"`

- [ ] **Step 4: Update true-crime skills**

`generate-storyboard.md` line 181:
```markdown
   - "Open in web editor (`./start.sh`) to assign media and review"
```

`review-storyboard.md` line 136:
```markdown
- "Assign remaining media in web editor (`./start.sh`)"
```

- [ ] **Step 5: Update screenplay-storyboard-formula.md**

Line 911: Change `./start.sh  # or: bee-video serve` to:
```bash
./start.sh  # Launches Node.js web editor on :8420
```

- [ ] **Step 6: Commit**

```bash
git add README.md CLAUDE.md setup.sh .claude/commands/true-crime/*.md bee-content/discovery/true-crime/research/screenplay-storyboard-formula.md
git commit -m "docs: remove all bee-video serve references, point to Node.js scripts"
```

---

### Task 6: Final verification

- [ ] **Step 1: Run Python CLI tests**

```bash
cd bee-content/video-editor && uv run --extra dev pytest tests/ -v --timeout=30
```

Expected: all tests pass, no import errors.

- [ ] **Step 2: Run Node.js tests**

```bash
cd bee-content/video-editor/web && npm test
```

Expected: 215 tests pass.

- [ ] **Step 3: Run E2E tests**

```bash
cd bee-content/video-editor/web && npx --package=@playwright/test playwright test
```

Expected: 11 tests pass.

- [ ] **Step 4: Verify CLI has no serve command**

```bash
uv run bee-video --help | grep -c serve
```

Expected: `0`

- [ ] **Step 5: Verify web editor starts**

```bash
cd bee-content/video-editor && ./start.sh &
sleep 3
curl -s http://localhost:8420/api/health
kill %1
```

Expected: `{"status":"ok"}`

- [ ] **Step 6: Search for any remaining `bee-video serve` references**

```bash
grep -r "bee-video serve" --include="*.md" --include="*.sh" --include="*.py" --include="*.yml" . | grep -v node_modules | grep -v __pycache__ | grep -v CHANGELOG
```

Expected: zero results (CHANGELOG historical entries excluded).

- [ ] **Step 7: Commit any fixes, then final commit**

```bash
git add -A
git commit -m "chore: verify Python web server fully deprecated"
```
