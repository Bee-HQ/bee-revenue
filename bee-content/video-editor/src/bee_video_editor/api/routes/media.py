"""Media routes — browse project media files, upload, download."""

from __future__ import annotations

import asyncio
import hashlib
import logging
import shutil
import subprocess
from pathlib import Path

from fastapi import APIRouter, HTTPException, UploadFile
from fastapi.responses import FileResponse

from bee_video_editor.api.schemas import (
    DownloadRequest,
    DownloadScriptInfo,
    DownloadStatusResponse,
    MediaFileSchema,
    MediaListResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter()

# Track running downloads
_download_tasks: dict[str, dict] = {}

# Media categories and their expected subdirectories
MEDIA_CATEGORIES = {
    "footage": ["footage"],
    "stock": ["stock", "stock-footage"],
    "photos": ["photos", "images"],
    "graphics": ["graphics", "output/graphics"],
    "narration": ["narration", "output/narration"],
    "maps": ["maps"],
    "music": ["music", "audio"],
    "segments": ["output/segments", "segments"],
}

MEDIA_EXTENSIONS = {
    "video": {".mp4", ".mkv", ".webm", ".mov", ".avi"},
    "audio": {".mp3", ".wav", ".m4a", ".aac", ".ogg"},
    "image": {".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp"},
}

ALL_MEDIA_EXTENSIONS = set()
for exts in MEDIA_EXTENSIONS.values():
    ALL_MEDIA_EXTENSIONS.update(exts)


def _get_project_dir() -> Path:
    from bee_video_editor.api.routes.projects import _current_project_dir
    if _current_project_dir is None:
        raise HTTPException(404, "No project loaded")
    return _current_project_dir


def _scan_media_dir(base_dir: Path, category: str, subdirs: list[str]) -> list[MediaFileSchema]:
    """Scan directories for media files."""
    files = []
    for subdir in subdirs:
        d = base_dir / subdir
        if not d.exists():
            continue
        for f in sorted(d.rglob("*")):
            if not f.is_file():
                continue
            if f.suffix.lower() not in ALL_MEDIA_EXTENSIONS:
                continue
            try:
                rel = f.relative_to(base_dir)
            except ValueError:
                rel = f.name
            files.append(MediaFileSchema(
                name=f.name,
                path=str(f),
                relative_path=str(rel),
                size_bytes=f.stat().st_size,
                category=category,
                extension=f.suffix.lower(),
            ))
    return files


@router.get("", response_model=MediaListResponse)
def list_media():
    """List all media files in the project directory."""
    project_dir = _get_project_dir()

    all_files: list[MediaFileSchema] = []
    categories: dict[str, int] = {}

    for category, subdirs in MEDIA_CATEGORIES.items():
        cat_files = _scan_media_dir(project_dir, category, subdirs)
        all_files.extend(cat_files)
        if cat_files:
            categories[category] = len(cat_files)

    return MediaListResponse(files=all_files, categories=categories)


@router.post("/upload")
async def upload_media(file: UploadFile, category: str = "footage"):
    """Upload a media file to the project."""
    project_dir = _get_project_dir()

    # Determine target directory
    target_dirs = MEDIA_CATEGORIES.get(category, [category])
    target_dir = project_dir / target_dirs[0]
    target_dir.mkdir(parents=True, exist_ok=True)

    target_path = target_dir / file.filename
    with open(target_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    return {
        "status": "ok",
        "path": str(target_path),
        "name": file.filename,
        "category": category,
    }


def _probe_container(path: Path) -> str | None:
    """Return the container format name via ffprobe, or None on failure."""
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=format_name",
             "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
            capture_output=True, text=True, timeout=10,
        )
        return result.stdout.strip() if result.returncode == 0 else None
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None


# Containers that browsers can't play natively
_NON_BROWSER_CONTAINERS = {"mpegts", "matroska", "avi", "asf"}


def _ensure_browser_playable(p: Path) -> Path:
    """If a video file isn't in a browser-playable container, remux to cached MP4."""
    if p.suffix.lower() not in {".mp4", ".mkv", ".avi", ".ts", ".mts"}:
        return p

    fmt = _probe_container(p)
    if not fmt or not any(bad in fmt for bad in _NON_BROWSER_CONTAINERS):
        return p

    # Remux to cache dir
    project_dir = _get_project_dir()
    cache_dir = project_dir / ".bee-video" / "remux-cache"
    cache_dir.mkdir(parents=True, exist_ok=True)

    path_hash = hashlib.md5(str(p).encode()).hexdigest()[:12]
    cached = cache_dir / f"{p.stem}-{path_hash}.mp4"

    if cached.exists() and cached.stat().st_mtime >= p.stat().st_mtime:
        return cached

    logger.info("Remuxing %s → %s (container: %s)", p.name, cached.name, fmt)
    try:
        result = subprocess.run(
            ["ffmpeg", "-y", "-i", str(p), "-c", "copy", "-movflags", "+faststart",
             str(cached)],
            capture_output=True, timeout=120,
        )
        if result.returncode != 0:
            logger.warning("Remux failed for %s: %s", p.name,
                           result.stderr[:500] if result.stderr else "unknown error")
            cached.unlink(missing_ok=True)
            return p
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return p  # ffmpeg not available or timed out, serve original

    return cached if cached.exists() else p


@router.get("/file")
def serve_media_file(path: str):
    """Serve a media file for preview."""
    p = Path(path)
    if not p.exists():
        raise HTTPException(404, f"File not found: {path}")

    # Basic security: ensure the file is within the project dir
    project_dir = _get_project_dir()
    try:
        p.resolve().relative_to(project_dir.resolve())
    except ValueError:
        raise HTTPException(403, "Access denied: file outside project directory")

    p = _ensure_browser_playable(p)
    logger.debug("Serving media file: %s", p.name)
    return FileResponse(p)


def _find_download_scripts(project_dir: Path) -> list[DownloadScriptInfo]:
    """Find download scripts in or near the project directory."""
    scripts = []
    # Check project dir and parent dirs (up to 3 levels)
    search_dirs = [project_dir]
    p = project_dir
    for _ in range(3):
        p = p.parent
        search_dirs.append(p)

    seen = set()
    for d in search_dirs:
        for pattern in ["download*.sh", "*download*.sh", "fetch*.sh"]:
            for script in d.glob(pattern):
                if script.resolve() not in seen and script.is_file():
                    seen.add(script.resolve())
                    scripts.append(DownloadScriptInfo(
                        name=script.name,
                        path=str(script.resolve()),
                        relative_to_project=str(
                            script.resolve().relative_to(project_dir.resolve())
                        ) if str(script.resolve()).startswith(str(project_dir.resolve())) else str(script.resolve()),
                    ))
    return scripts


def _check_tool(name: str) -> bool:
    """Check if a CLI tool is available."""
    return shutil.which(name) is not None


@router.get("/download/scripts", response_model=list[DownloadScriptInfo])
def list_download_scripts():
    """List available download scripts for this project."""
    project_dir = _get_project_dir()
    return _find_download_scripts(project_dir)


@router.get("/download/tools")
def check_download_tools():
    """Check which download tools are available."""
    return {
        "yt_dlp": _check_tool("yt-dlp"),
        "curl": _check_tool("curl"),
        "wget": _check_tool("wget"),
        "ffmpeg": _check_tool("ffmpeg"),
    }


@router.post("/download/run-script")
async def run_download_script(req: DownloadRequest):
    """Run a download script in the project directory."""
    project_dir = _get_project_dir()

    script_path = Path(req.script_path)
    if not script_path.exists():
        raise HTTPException(404, f"Script not found: {req.script_path}")
    if not script_path.suffix == ".sh":
        raise HTTPException(400, "Only .sh scripts are supported")

    task_id = f"script-{script_path.stem}"
    if task_id in _download_tasks and _download_tasks[task_id].get("running"):
        raise HTTPException(409, "This script is already running")

    _download_tasks[task_id] = {
        "running": True,
        "script": script_path.name,
        "output_lines": [],
        "return_code": None,
    }

    async def _run():
        try:
            proc = await asyncio.create_subprocess_exec(
                "bash", str(script_path),
                cwd=str(project_dir),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
            )
            while True:
                line = await proc.stdout.readline()
                if not line:
                    break
                decoded = line.decode("utf-8", errors="replace").rstrip()
                _download_tasks[task_id]["output_lines"].append(decoded)
                # Keep last 200 lines
                if len(_download_tasks[task_id]["output_lines"]) > 200:
                    _download_tasks[task_id]["output_lines"] = \
                        _download_tasks[task_id]["output_lines"][-200:]
            await proc.wait()
            _download_tasks[task_id]["return_code"] = proc.returncode
            if proc.returncode == 0:
                logger.info("Download completed: %s", task_id)
            else:
                logger.error("Download failed: %s (exit=%d) last output: %s",
                            task_id, proc.returncode,
                            "\n".join(_download_tasks[task_id]["output_lines"][-10:]))
        except Exception as e:
            _download_tasks[task_id]["output_lines"].append(f"ERROR: {e}")
            _download_tasks[task_id]["return_code"] = -1
        finally:
            _download_tasks[task_id]["running"] = False

    asyncio.create_task(_run())
    return {"status": "started", "task_id": task_id}


@router.post("/download/yt-dlp")
async def download_with_ytdlp(url: str, category: str = "footage", filename: str | None = None):
    """Download a video using yt-dlp."""
    if not _check_tool("yt-dlp"):
        raise HTTPException(400, "yt-dlp is not installed. Install with: pip install yt-dlp")

    project_dir = _get_project_dir()
    target_dir = project_dir / category
    target_dir.mkdir(parents=True, exist_ok=True)

    output_template = str(target_dir / (filename or "%(title)s.%(ext)s"))

    task_id = f"ytdlp-{hash(url) % 10000}"
    _download_tasks[task_id] = {
        "running": True,
        "url": url,
        "output_lines": [],
        "return_code": None,
    }

    async def _run():
        try:
            proc = await asyncio.create_subprocess_exec(
                "yt-dlp",
                "-f", "bestvideo[height<=720]+bestaudio/best[height<=720]",
                "--remux-video", "mp4",
                "--no-playlist",
                "-o", output_template,
                url,
                cwd=str(project_dir),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
            )
            while True:
                line = await proc.stdout.readline()
                if not line:
                    break
                decoded = line.decode("utf-8", errors="replace").rstrip()
                _download_tasks[task_id]["output_lines"].append(decoded)
                if len(_download_tasks[task_id]["output_lines"]) > 200:
                    _download_tasks[task_id]["output_lines"] = \
                        _download_tasks[task_id]["output_lines"][-200:]
            await proc.wait()
            _download_tasks[task_id]["return_code"] = proc.returncode
            if proc.returncode == 0:
                logger.info("Download completed: %s", task_id)
            else:
                logger.error("Download failed: %s (exit=%d) last output: %s",
                            task_id, proc.returncode,
                            "\n".join(_download_tasks[task_id]["output_lines"][-10:]))
        except Exception as e:
            _download_tasks[task_id]["output_lines"].append(f"ERROR: {e}")
            _download_tasks[task_id]["return_code"] = -1
        finally:
            _download_tasks[task_id]["running"] = False

    asyncio.create_task(_run())
    return {"status": "started", "task_id": task_id}


@router.get("/download/status", response_model=list[DownloadStatusResponse])
def download_status():
    """Get status of all download tasks."""
    result = []
    for task_id, info in _download_tasks.items():
        result.append(DownloadStatusResponse(
            task_id=task_id,
            running=info["running"],
            output_lines=info["output_lines"][-20:],
            return_code=info.get("return_code"),
        ))
    return result


@router.post("/download/create-dirs")
def create_media_dirs():
    """Create all standard media directories in the project."""
    project_dir = _get_project_dir()
    created = []
    for category, subdirs in MEDIA_CATEGORIES.items():
        d = project_dir / subdirs[0]
        if not d.exists():
            d.mkdir(parents=True, exist_ok=True)
            created.append(str(subdirs[0]))
    return {"status": "ok", "created": created}
