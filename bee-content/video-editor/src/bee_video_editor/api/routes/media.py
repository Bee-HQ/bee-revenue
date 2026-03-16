"""Media routes — browse project media files, upload."""

from __future__ import annotations

import shutil
from pathlib import Path

from fastapi import APIRouter, HTTPException, UploadFile
from fastapi.responses import FileResponse

from bee_video_editor.api.schemas import MediaFileSchema, MediaListResponse

router = APIRouter()

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

    return FileResponse(p)
