# Stock Footage API + AI Video Generation Infra

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add stock footage sourcing via Pexels API and build pluggable video generation infrastructure (provider interface + stub) so real AI providers can be wired in later.

**Architecture:** Both features are new processors following the existing pattern. Stock footage is a self-contained processor (`stock.py`) with a service orchestrator. Video generation uses the same dispatch-by-engine pattern as TTS (`tts.py`): a top-level function routes to provider-specific implementations, with a `stub` provider for testing and real providers as optional extras. Both get CLI commands and API endpoints.

**Tech Stack:** Python 3.11+, httpx (Pexels API), typer (CLI), FastAPI (API endpoints)

---

## File Map

```
src/bee_video_editor/
├── processors/
│   ├── stock.py               (NEW — Pexels API search + download)
│   └── videogen.py            (NEW — video generation provider interface + stub)
├── services/
│   └── production.py          (MODIFY — add fetch_stock_for_project)
├── api/
│   ├── routes/
│   │   ├── media.py           (MODIFY — add /stock/search, /stock/download, /generate-clip)
│   │   └── production.py      (no changes)
│   └── schemas.py             (MODIFY — add request/response schemas)
├── adapters/
│   └── cli.py                 (MODIFY — add fetch-stock, generate-clip commands)

pyproject.toml                 (MODIFY — add httpx dep, video-gen extras)

tests/
├── test_stock.py              (NEW — Pexels search + download, mocked)
├── test_videogen.py           (NEW — provider dispatch, stub, interface)
└── test_api.py                (MODIFY — add stock + generation API tests)
```

---

## Task 1: Stock Footage Processor (Pexels API)

### 1.1: Pexels search + download

**Files:**
- Create: `src/bee_video_editor/processors/stock.py`
- Create: `tests/test_stock.py`
- Modify: `pyproject.toml` (add `httpx` to core dependencies)

- [ ] **Step 1: Add httpx dependency**

In `pyproject.toml`, add `"httpx>=0.27.0"` to `dependencies`:
```toml
dependencies = [
    "typer>=0.9.0",
    "rich>=13.0.0",
    "pillow>=10.0.0",
    "edge-tts>=6.1.0",
    "pysubs2>=1.7.0",
    "httpx>=0.27.0",
]
```

Run: `uv sync --extra dev`

- [ ] **Step 2: Write failing tests**

```python
# tests/test_stock.py
"""Tests for stock footage search and download via Pexels API."""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from bee_video_editor.processors.stock import (
    PexelsResult,
    download_stock_clip,
    search_pexels,
)


class TestSearchPexels:
    def test_parses_video_results(self):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "videos": [
                {
                    "id": 123,
                    "url": "https://pexels.com/video/123",
                    "duration": 15,
                    "width": 1920,
                    "height": 1080,
                    "video_files": [
                        {"id": 1, "quality": "hd", "width": 1920, "height": 1080,
                         "link": "https://cdn.pexels.com/123-hd.mp4", "file_type": "video/mp4"},
                        {"id": 2, "quality": "sd", "width": 640, "height": 360,
                         "link": "https://cdn.pexels.com/123-sd.mp4", "file_type": "video/mp4"},
                    ],
                },
            ],
            "total_results": 1,
        }

        with patch("bee_video_editor.processors.stock.httpx") as mock_httpx:
            mock_httpx.get.return_value = mock_response
            results = search_pexels("farm aerial", api_key="test-key")

        assert len(results) == 1
        assert results[0].id == 123
        assert results[0].duration == 15
        assert results[0].hd_url == "https://cdn.pexels.com/123-hd.mp4"

    def test_filters_by_min_duration(self):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "videos": [
                {"id": 1, "url": "", "duration": 3, "width": 1920, "height": 1080,
                 "video_files": [{"id": 1, "quality": "hd", "width": 1920, "height": 1080,
                                  "link": "https://cdn/1.mp4", "file_type": "video/mp4"}]},
                {"id": 2, "url": "", "duration": 10, "width": 1920, "height": 1080,
                 "video_files": [{"id": 2, "quality": "hd", "width": 1920, "height": 1080,
                                  "link": "https://cdn/2.mp4", "file_type": "video/mp4"}]},
            ],
            "total_results": 2,
        }

        with patch("bee_video_editor.processors.stock.httpx") as mock_httpx:
            mock_httpx.get.return_value = mock_response
            results = search_pexels("test", api_key="key", min_duration=5)

        assert len(results) == 1
        assert results[0].id == 2

    def test_missing_api_key_raises(self):
        with pytest.raises(ValueError, match="PEXELS_API_KEY"):
            search_pexels("test", api_key=None)

    def test_api_error_raises(self):
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"

        with patch("bee_video_editor.processors.stock.httpx") as mock_httpx:
            mock_httpx.get.return_value = mock_response
            with pytest.raises(RuntimeError, match="Pexels API error"):
                search_pexels("test", api_key="bad-key")

    def test_empty_results(self):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"videos": [], "total_results": 0}

        with patch("bee_video_editor.processors.stock.httpx") as mock_httpx:
            mock_httpx.get.return_value = mock_response
            results = search_pexels("nonexistent", api_key="key")

        assert results == []


class TestDownloadStockClip:
    def _mock_stream(self, mock_httpx, status_code=200, chunks=None):
        """Set up mock for httpx.stream context manager."""
        if chunks is None:
            chunks = [b"\x00" * 100]
        mock_response = MagicMock()
        mock_response.status_code = status_code
        mock_response.iter_bytes.return_value = iter(chunks)
        mock_httpx.stream.return_value.__enter__ = MagicMock(return_value=mock_response)
        mock_httpx.stream.return_value.__exit__ = MagicMock(return_value=False)
        return mock_response

    def test_downloads_to_path(self):
        with tempfile.TemporaryDirectory() as d:
            output = Path(d) / "stock" / "clip.mp4"

            with patch("bee_video_editor.processors.stock.httpx") as mock_httpx:
                self._mock_stream(mock_httpx, chunks=[b"\x00" * 100])
                result = download_stock_clip("https://cdn/clip.mp4", output)

            assert result == output
            assert output.exists()
            assert output.read_bytes() == b"\x00" * 100

    def test_creates_parent_dirs(self):
        with tempfile.TemporaryDirectory() as d:
            output = Path(d) / "deep" / "nested" / "clip.mp4"

            with patch("bee_video_editor.processors.stock.httpx") as mock_httpx:
                self._mock_stream(mock_httpx, chunks=[b"\x00"])
                download_stock_clip("https://cdn/clip.mp4", output)

            assert output.exists()

    def test_skips_existing_file(self):
        with tempfile.TemporaryDirectory() as d:
            output = Path(d) / "clip.mp4"
            output.write_bytes(b"existing")

            with patch("bee_video_editor.processors.stock.httpx") as mock_httpx:
                result = download_stock_clip("https://cdn/clip.mp4", output)

            mock_httpx.stream.assert_not_called()
            assert result == output

    def test_download_error_raises(self):
        with tempfile.TemporaryDirectory() as d:
            output = Path(d) / "clip.mp4"

            with patch("bee_video_editor.processors.stock.httpx") as mock_httpx:
                self._mock_stream(mock_httpx, status_code=404)
                with pytest.raises(RuntimeError, match="Download failed"):
                    download_stock_clip("https://cdn/clip.mp4", output)
```

- [ ] **Step 3: Run tests to verify they fail**

Run: `uv run --extra dev pytest tests/test_stock.py -v`
Expected: FAIL with `ModuleNotFoundError`

- [ ] **Step 4: Implement stock processor**

```python
# src/bee_video_editor/processors/stock.py
"""Stock footage search and download via Pexels API."""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from pathlib import Path

import httpx

PEXELS_API_URL = "https://api.pexels.com/videos/search"


@dataclass
class PexelsResult:
    """A single video result from Pexels."""
    id: int
    url: str
    duration: int
    width: int
    height: int
    hd_url: str
    sd_url: str | None = None


def search_pexels(
    query: str,
    api_key: str | None = None,
    per_page: int = 10,
    min_duration: int = 0,
    orientation: str | None = None,
) -> list[PexelsResult]:
    """Search Pexels for stock video clips.

    Args:
        query: Search terms (e.g. "aerial farm dusk").
        api_key: Pexels API key. Falls back to PEXELS_API_KEY env var.
        per_page: Results per page (max 80).
        min_duration: Minimum clip duration in seconds (0 = no filter).
        orientation: "landscape", "portrait", or "square" (None = any).

    Returns:
        List of PexelsResult with download URLs.
    """
    api_key = api_key or os.environ.get("PEXELS_API_KEY")
    if not api_key:
        raise ValueError(
            "No API key provided. Set PEXELS_API_KEY env var or pass api_key parameter."
        )

    params = {"query": query, "per_page": per_page}
    if orientation:
        params["orientation"] = orientation

    response = httpx.get(
        PEXELS_API_URL,
        headers={"Authorization": api_key},
        params=params,
        timeout=30,
    )

    if response.status_code != 200:
        raise RuntimeError(f"Pexels API error {response.status_code}: {response.text[:200]}")

    data = response.json()
    results = []

    for video in data.get("videos", []):
        if min_duration and video.get("duration", 0) < min_duration:
            continue

        # Find best quality download URL
        hd_url = None
        sd_url = None
        for vf in video.get("video_files", []):
            if vf.get("quality") == "hd" and vf.get("file_type") == "video/mp4":
                hd_url = vf["link"]
            elif vf.get("quality") == "sd" and vf.get("file_type") == "video/mp4":
                sd_url = vf["link"]

        if not hd_url and not sd_url:
            continue

        results.append(PexelsResult(
            id=video["id"],
            url=video.get("url", ""),
            duration=video.get("duration", 0),
            width=video.get("width", 0),
            height=video.get("height", 0),
            hd_url=hd_url or sd_url,
            sd_url=sd_url,
        ))

    return results


def download_stock_clip(
    url: str,
    output_path: Path,
    timeout: int = 120,
) -> Path:
    """Download a stock video clip to the given path.

    Skips download if the file already exists (idempotent).
    """
    output_path = Path(output_path)
    if output_path.exists():
        return output_path

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with httpx.stream("GET", url, timeout=timeout, follow_redirects=True) as response:
        if response.status_code != 200:
            raise RuntimeError(f"Download failed ({response.status_code})")
        with open(output_path, "wb") as f:
            for chunk in response.iter_bytes(chunk_size=65536):
                f.write(chunk)

    return output_path


def slugify_query(query: str) -> str:
    """Convert search query to a filename-safe slug."""
    slug = re.sub(r'[^\w\s-]', '', query.lower())
    slug = re.sub(r'[\s_]+', '-', slug)
    return slug.strip('-')[:40]
```

- [ ] **Step 5: Run tests**

Run: `uv run --extra dev pytest tests/test_stock.py -v`
Expected: all 9 pass

- [ ] **Step 6: Commit**

```bash
git add pyproject.toml src/bee_video_editor/processors/stock.py tests/test_stock.py
git commit -m "feat(video-editor): Pexels stock footage search + download processor"
```

---

## Task 2: Video Generation Provider Interface

### 2.1: Provider protocol + stub

**Files:**
- Create: `src/bee_video_editor/processors/videogen.py`
- Create: `tests/test_videogen.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_videogen.py
"""Tests for video generation provider interface and stub."""

import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from bee_video_editor.processors.videogen import (
    GenerationRequest,
    GenerationResult,
    generate_clip,
    list_providers,
)


class TestGenerationRequest:
    def test_basic_request(self):
        req = GenerationRequest(prompt="aerial shot of farm at dusk", duration=5.0)
        assert req.prompt == "aerial shot of farm at dusk"
        assert req.duration == 5.0
        assert req.reference_images == []
        assert req.reference_videos == []
        assert req.width == 1280
        assert req.height == 720

    def test_request_with_references(self):
        req = GenerationRequest(
            prompt="match this style",
            duration=3.0,
            reference_images=[Path("/img/ref.jpg")],
            reference_videos=[Path("/vid/ref.mp4")],
        )
        assert len(req.reference_images) == 1
        assert len(req.reference_videos) == 1


class TestListProviders:
    def test_stub_always_available(self):
        providers = list_providers()
        assert "stub" in providers

    def test_returns_dict_with_descriptions(self):
        providers = list_providers()
        assert isinstance(providers, dict)
        assert isinstance(providers["stub"], str)


class TestGenerateClip:
    def test_stub_creates_placeholder(self):
        req = GenerationRequest(prompt="test prompt", duration=3.0)
        with tempfile.TemporaryDirectory() as d:
            output = Path(d) / "generated.mp4"
            result = generate_clip(req, output, provider="stub")

        assert result.provider == "stub"
        assert result.output_path == output
        assert result.success is True
        assert output.exists()

    def test_stub_output_has_content(self):
        req = GenerationRequest(prompt="test", duration=2.0)
        with tempfile.TemporaryDirectory() as d:
            output = Path(d) / "out.mp4"
            generate_clip(req, output, provider="stub")

        assert output.stat().st_size > 0

    def test_unknown_provider_raises(self):
        req = GenerationRequest(prompt="test", duration=1.0)
        with tempfile.TemporaryDirectory() as d:
            output = Path(d) / "out.mp4"
            with pytest.raises(ValueError, match="Unknown video generation provider"):
                generate_clip(req, output, provider="nonexistent")

    def test_creates_parent_dirs(self):
        req = GenerationRequest(prompt="test", duration=1.0)
        with tempfile.TemporaryDirectory() as d:
            output = Path(d) / "deep" / "nested" / "out.mp4"
            result = generate_clip(req, output, provider="stub")

        assert result.success
        assert output.exists()

    def test_result_includes_metadata(self):
        req = GenerationRequest(prompt="a beautiful sunset", duration=5.0)
        with tempfile.TemporaryDirectory() as d:
            output = Path(d) / "out.mp4"
            result = generate_clip(req, output, provider="stub")

        assert result.prompt == "a beautiful sunset"
        assert result.duration == 5.0
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run --extra dev pytest tests/test_videogen.py -v`
Expected: FAIL with `ModuleNotFoundError`

- [ ] **Step 3: Implement provider interface + stub**

```python
# src/bee_video_editor/processors/videogen.py
"""Video generation — pluggable provider interface.

Providers generate video clips from text prompts and optional reference media.
Ships with a 'stub' provider for testing. Real providers (Runway, Kling, Luma, etc.)
are optional extras.

Usage:
    from bee_video_editor.processors.videogen import generate_clip, GenerationRequest

    req = GenerationRequest(prompt="aerial shot of farm", duration=5.0)
    result = generate_clip(req, Path("output.mp4"), provider="stub")
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class GenerationRequest:
    """Input for video generation."""
    prompt: str
    duration: float = 5.0
    width: int = 1280
    height: int = 720
    reference_images: list[Path] = field(default_factory=list)
    reference_videos: list[Path] = field(default_factory=list)
    style: str | None = None       # provider-specific style hint
    negative_prompt: str | None = None


@dataclass
class GenerationResult:
    """Output from video generation."""
    success: bool
    output_path: Path
    provider: str
    prompt: str
    duration: float
    error: str | None = None
    metadata: dict = field(default_factory=dict)


# ─── Provider registry ───────────────────────────────────────────────────────

_PROVIDERS: dict[str, tuple[str, object]] = {}


def _register(name: str, description: str, fn):
    _PROVIDERS[name] = (description, fn)


def list_providers() -> dict[str, str]:
    """Return {name: description} for all available providers."""
    _ensure_providers_loaded()
    return {name: desc for name, (desc, _) in _PROVIDERS.items()}


def generate_clip(
    request: GenerationRequest,
    output_path: Path,
    provider: str = "stub",
) -> GenerationResult:
    """Generate a video clip using the specified provider.

    Args:
        request: What to generate (prompt, duration, references).
        output_path: Where to save the generated clip.
        provider: Provider name ("stub", "runway", "kling", etc.).

    Returns:
        GenerationResult with success status and metadata.
    """
    _ensure_providers_loaded()
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if provider not in _PROVIDERS:
        available = ", ".join(sorted(_PROVIDERS.keys()))
        raise ValueError(
            f"Unknown video generation provider '{provider}'. "
            f"Available: {available}"
        )

    _, fn = _PROVIDERS[provider]
    return fn(request, output_path)


# ─── Stub provider (always available, for testing) ───────────────────────────

def _generate_stub(request: GenerationRequest, output_path: Path) -> GenerationResult:
    """Generate a placeholder clip — writes metadata JSON instead of real video.

    For testing and development. Real providers replace this with actual
    AI-generated video.
    """
    placeholder = {
        "type": "stub_generated_clip",
        "prompt": request.prompt,
        "duration": request.duration,
        "width": request.width,
        "height": request.height,
        "reference_images": [str(p) for p in request.reference_images],
        "reference_videos": [str(p) for p in request.reference_videos],
        "style": request.style,
    }
    output_path.write_text(json.dumps(placeholder, indent=2))

    return GenerationResult(
        success=True,
        output_path=output_path,
        provider="stub",
        prompt=request.prompt,
        duration=request.duration,
        metadata=placeholder,
    )


def _ensure_providers_loaded():
    """Register built-in and optional providers."""
    if _PROVIDERS:
        return

    _register("stub", "Placeholder — writes metadata JSON (for testing)", _generate_stub)

    # Optional providers — registered only if their dependencies are installed
    try:
        from bee_video_editor.processors._videogen_runway import generate_runway
        _register("runway", "Runway Gen-4 — text/image to video", generate_runway)
    except ImportError:
        pass

    try:
        from bee_video_editor.processors._videogen_kling import generate_kling
        _register("kling", "Kling — text/image to video", generate_kling)
    except ImportError:
        pass

    try:
        from bee_video_editor.processors._videogen_luma import generate_luma
        _register("luma", "Luma Dream Machine — text/image to video", generate_luma)
    except ImportError:
        pass
```

- [ ] **Step 4: Run tests**

Run: `uv run --extra dev pytest tests/test_videogen.py -v`
Expected: all 9 pass

- [ ] **Step 5: Commit**

```bash
git add src/bee_video_editor/processors/videogen.py tests/test_videogen.py
git commit -m "feat(video-editor): video generation provider interface with stub"
```

---

## Task 3: CLI Commands

### 3.1: fetch-stock + generate-clip CLI

**Files:**
- Modify: `src/bee_video_editor/adapters/cli.py`

- [ ] **Step 1: Add fetch-stock command**

Add before `_load_project()` in `cli.py`:

```python
@app.command()
def fetch_stock(
    query: str = typer.Argument(..., help="Search query (e.g. 'aerial farm dusk')"),
    project_dir: str = typer.Option(".", "--project-dir", "-p"),
    count: int = typer.Option(3, "--count", "-n", help="Number of clips to download"),
    min_duration: int = typer.Option(5, "--duration", "-d", help="Minimum clip duration (seconds)"),
    orientation: str | None = typer.Option(None, "--orientation", "-o", help="landscape/portrait/square"),
    api_key: str | None = typer.Option(None, "--api-key", envvar="PEXELS_API_KEY"),
):
    """Search and download stock footage from Pexels."""
    from bee_video_editor.processors.stock import (
        download_stock_clip,
        search_pexels,
        slugify_query,
    )

    try:
        results = search_pexels(
            query, api_key=api_key, per_page=count,
            min_duration=min_duration, orientation=orientation,
        )
    except ValueError as e:
        console.print(f"[red]{e}[/red]")
        raise typer.Exit(1)
    except RuntimeError as e:
        console.print(f"[red]{e}[/red]")
        raise typer.Exit(1)

    if not results:
        console.print("[yellow]No results found.[/yellow]")
        return

    console.print(f"[bold]Found {len(results)} clips. Downloading...[/bold]")
    stock_dir = Path(project_dir) / "stock"
    slug = slugify_query(query)

    for i, clip in enumerate(results[:count]):
        filename = f"{slug}-{i:02d}-pexels-{clip.id}.mp4"
        out_path = stock_dir / filename

        try:
            download_stock_clip(clip.hd_url, out_path)
            console.print(f"  [green]{filename}[/green] ({clip.duration}s, {clip.width}x{clip.height})")
        except RuntimeError as e:
            console.print(f"  [red]{filename}: {e}[/red]")

    console.print(f"[bold green]Done — {stock_dir}[/bold green]")


@app.command()
def generate_clip(
    prompt: str = typer.Argument(..., help="Text prompt describing the clip to generate"),
    project_dir: str = typer.Option(".", "--project-dir", "-p"),
    provider: str = typer.Option("stub", "--provider", help="Generation provider (stub/runway/kling/luma)"),
    duration: float = typer.Option(5.0, "--duration", "-d", help="Clip duration (seconds)"),
    reference: list[str] | None = typer.Option(None, "--reference", "-r", help="Reference image/video path (repeatable)"),
    width: int = typer.Option(1280, "--width", "-w"),
    height: int = typer.Option(720, "--height"),
    style: str | None = typer.Option(None, "--style", "-s", help="Provider-specific style hint"),
):
    """Generate a video clip from a text prompt using AI."""
    from bee_video_editor.processors.videogen import (
        GenerationRequest,
        generate_clip as gen_clip,
        list_providers,
    )

    available = list_providers()
    if provider not in available:
        console.print(f"[red]Unknown provider '{provider}'. Available: {', '.join(sorted(available))}[/red]")
        raise typer.Exit(1)

    # Classify references as images or videos
    ref_images = []
    ref_videos = []
    for ref in (reference or []):
        p = Path(ref)
        if p.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp", ".bmp"}:
            ref_images.append(p)
        else:
            ref_videos.append(p)

    import re
    slug = re.sub(r'[^\w\s-]', '', prompt.lower())
    slug = re.sub(r'[\s_]+', '-', slug).strip('-')[:30]

    output_dir = Path(project_dir) / "generated"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{slug}-{provider}.mp4"

    req = GenerationRequest(
        prompt=prompt,
        duration=duration,
        width=width,
        height=height,
        reference_images=ref_images,
        reference_videos=ref_videos,
        style=style,
    )

    console.print(f"[bold]Generating clip ({provider})...[/bold]")
    console.print(f"  Prompt: {prompt}")
    if ref_images or ref_videos:
        console.print(f"  References: {len(ref_images)} images, {len(ref_videos)} videos")

    try:
        result = gen_clip(req, output_path, provider=provider)
        if result.success:
            console.print(f"[bold green]Generated: {result.output_path}[/bold green]")
        else:
            console.print(f"[red]Generation failed: {result.error}[/red]")
    except Exception as e:
        console.print(f"[red]{e}[/red]")
        raise typer.Exit(1)
```

- [ ] **Step 2: Run full test suite to verify no regressions**

Run: `uv run --extra dev pytest tests/ -q`
Expected: all pass

- [ ] **Step 3: Commit**

```bash
git add src/bee_video_editor/adapters/cli.py
git commit -m "feat(video-editor): bee-video fetch-stock + generate-clip CLI commands"
```

---

## Task 4: API Endpoints

### 4.1: Schemas + routes

**Files:**
- Modify: `src/bee_video_editor/api/schemas.py`
- Modify: `src/bee_video_editor/api/routes/media.py`
- Modify: `tests/test_api.py`

- [ ] **Step 1: Add schemas**

Append to `schemas.py`:

```python
class StockSearchRequest(BaseModel):
    query: str
    count: int = 3
    min_duration: int = 5
    orientation: str | None = None


class StockDownloadRequest(BaseModel):
    url: str
    filename: str


class GenerateClipRequest(BaseModel):
    prompt: str
    provider: str = "stub"
    duration: float = 5.0
    width: int = 1280
    height: int = 720
    reference_images: list[str] = []
    reference_videos: list[str] = []
    style: str | None = None
```

- [ ] **Step 2: Add routes to media.py**

Add to `media.py` (after the `create_media_dirs` route):

```python
@router.post("/stock/search")
def search_stock(req: StockSearchRequest, session: SessionStore = Depends(get_session)):
    """Search Pexels for stock footage."""
    from bee_video_editor.processors.stock import search_pexels

    try:
        results = search_pexels(
            req.query, per_page=req.count,
            min_duration=req.min_duration, orientation=req.orientation,
        )
    except ValueError as e:
        raise HTTPException(400, str(e))
    except RuntimeError as e:
        raise HTTPException(502, str(e))

    return {
        "results": [
            {
                "id": r.id,
                "url": r.url,
                "duration": r.duration,
                "width": r.width,
                "height": r.height,
                "hd_url": r.hd_url,
                "sd_url": r.sd_url,
            }
            for r in results
        ],
        "count": len(results),
    }


@router.post("/stock/download")
def download_stock(req: StockDownloadRequest, session: SessionStore = Depends(get_session)):
    """Download a stock footage clip to the project."""
    from urllib.parse import urlparse

    from bee_video_editor.processors.stock import download_stock_clip

    _, project_dir = session.require_project()

    # Validate URL (SSRF prevention)
    parsed = urlparse(req.url)
    if parsed.scheme != "https" or not parsed.hostname:
        raise HTTPException(400, "Only HTTPS URLs are allowed")

    # Validate filename
    safe_name = Path(req.filename).name
    if not safe_name or safe_name.startswith(".") or safe_name != req.filename:
        raise HTTPException(400, "Invalid filename")

    stock_dir = project_dir / "stock"
    try:
        result = download_stock_clip(req.url, stock_dir / safe_name)
        return {"status": "ok", "path": str(result), "name": safe_name}
    except RuntimeError as e:
        raise HTTPException(502, str(e))


@router.post("/generate-clip")
def generate_video_clip(req: GenerateClipRequest, session: SessionStore = Depends(get_session)):
    """Generate a video clip from a text prompt."""
    from bee_video_editor.processors.videogen import (
        GenerationRequest,
        generate_clip,
        list_providers,
    )

    available = list_providers()
    if req.provider not in available:
        raise HTTPException(400, f"Unknown provider '{req.provider}'. Available: {', '.join(sorted(available))}")

    _, project_dir = session.require_project()
    output_dir = project_dir / "generated"
    output_dir.mkdir(parents=True, exist_ok=True)

    import re
    slug = re.sub(r'[^\w\s-]', '', req.prompt.lower())
    slug = re.sub(r'[\s_]+', '-', slug).strip('-')[:30]
    output_path = output_dir / f"{slug}-{req.provider}.mp4"

    gen_req = GenerationRequest(
        prompt=req.prompt,
        duration=req.duration,
        width=req.width,
        height=req.height,
        reference_images=[Path(p) for p in req.reference_images],
        reference_videos=[Path(p) for p in req.reference_videos],
        style=req.style,
    )

    try:
        result = generate_clip(gen_req, output_path, provider=req.provider)
        return {
            "status": "ok" if result.success else "error",
            "output": str(result.output_path),
            "provider": result.provider,
            "error": result.error,
        }
    except Exception as e:
        raise HTTPException(500, str(e))
```

Don't forget to import the new schemas at the top of `media.py`:
```python
from bee_video_editor.api.schemas import (
    ...,
    GenerateClipRequest,
    StockDownloadRequest,
    StockSearchRequest,
)
```

- [ ] **Step 3: Write API tests**

Append to `tests/test_api.py`:

```python
class TestStockSearch:
    def test_search_returns_results(self, loaded_project):
        client, _, _ = loaded_project
        from unittest.mock import MagicMock
        mock_result = MagicMock()
        mock_result.id = 123
        mock_result.url = "https://pexels.com/123"
        mock_result.duration = 10
        mock_result.width = 1920
        mock_result.height = 1080
        mock_result.hd_url = "https://cdn/123.mp4"
        mock_result.sd_url = None

        with patch("bee_video_editor.processors.stock.search_pexels", return_value=[mock_result]):
            r = client.post("/api/media/stock/search", json={
                "query": "aerial farm",
                "count": 3,
            })

        assert r.status_code == 200
        assert r.json()["count"] == 1
        assert r.json()["results"][0]["id"] == 123

    def test_search_no_api_key_400(self, loaded_project):
        client, _, _ = loaded_project
        with patch("bee_video_editor.processors.stock.search_pexels",
                    side_effect=ValueError("No API key")):
            r = client.post("/api/media/stock/search", json={"query": "test"})

        assert r.status_code == 400


class TestStockDownload:
    def test_download_clip(self, loaded_project):
        client, _, proj_dir = loaded_project
        with patch("bee_video_editor.processors.stock.download_stock_clip") as mock_dl:
            mock_dl.return_value = proj_dir / "stock" / "clip.mp4"
            r = client.post("/api/media/stock/download", json={
                "url": "https://cdn/clip.mp4",
                "filename": "clip.mp4",
            })

        assert r.status_code == 200
        assert r.json()["name"] == "clip.mp4"

    def test_download_traversal_filename_400(self, loaded_project):
        client, _, _ = loaded_project
        r = client.post("/api/media/stock/download", json={
            "url": "https://cdn/clip.mp4",
            "filename": "../../evil.mp4",
        })
        assert r.status_code == 400


class TestGenerateClip:
    def test_generate_with_stub(self, loaded_project):
        client, _, proj_dir = loaded_project
        r = client.post("/api/media/generate-clip", json={
            "prompt": "aerial shot of farm",
            "provider": "stub",
            "duration": 3.0,
        })

        assert r.status_code == 200
        assert r.json()["status"] == "ok"
        assert r.json()["provider"] == "stub"

    def test_generate_unknown_provider_400(self, loaded_project):
        client, _, _ = loaded_project
        r = client.post("/api/media/generate-clip", json={
            "prompt": "test",
            "provider": "nonexistent",
        })
        assert r.status_code == 400
```

- [ ] **Step 4: Run all tests**

Run: `uv run --extra dev pytest tests/test_stock.py tests/test_videogen.py tests/test_api.py -v`
Expected: all pass

- [ ] **Step 5: Commit**

```bash
git add src/bee_video_editor/api/schemas.py src/bee_video_editor/api/routes/media.py tests/test_api.py
git commit -m "feat(video-editor): stock search/download + generate-clip API endpoints"
```

---

## Task 5: Add "generated" to media categories + update MEDIA_CATEGORIES

**Files:**
- Modify: `src/bee_video_editor/api/routes/media.py`

- [ ] **Step 1: Add "generated" category**

In `media.py`, add `"generated": ["generated"]` to the existing `MEDIA_CATEGORIES` dict (after `"segments"`). The `"stock"` category already exists — no changes needed for it. This makes AI-generated clips appear in the media library automatically.

- [ ] **Step 2: Run full test suite**

Run: `./test.sh`
Expected: all pass

- [ ] **Step 3: Commit**

```bash
git add src/bee_video_editor/api/routes/media.py
git commit -m "feat(video-editor): add 'generated' media category for AI-generated clips"
```

---

## Task 6: Update Docs + Release

**Files:**
- Modify: `ROADMAP.md`
- Modify: `CLAUDE.md`
- Modify: `CHANGELOG.md`
- Modify: `README.md`

- [ ] **Step 1: Mark roadmap items done**

In `ROADMAP.md`, mark `Stock footage API` as `[x]`, and add a new item for video generation.

- [ ] **Step 2: Update CLAUDE.md**

Add to CLI commands section:
```
uv run bee-video fetch-stock "aerial farm dusk" -n 3 -p ./proj   # Download stock from Pexels
uv run bee-video generate-clip "sunset over ocean" -p ./proj     # Generate clip (AI)
```

- [ ] **Step 3: Add CHANGELOG entry**

Add to the `[Unreleased]` or new version section in `CHANGELOG.md`.

- [ ] **Step 4: Update README.md**

Add Stock Footage and Video Generation sections.

- [ ] **Step 5: Run full test suite**

Run: `./test.sh`
Expected: all pass

- [ ] **Step 6: Commit**

```bash
# Run from repo root
git add bee-content/video-editor/ROADMAP.md bee-content/video-editor/CLAUDE.md \
        bee-content/video-editor/CHANGELOG.md bee-content/video-editor/README.md
git commit -m "docs(video-editor): stock footage API + video generation infra"
```
