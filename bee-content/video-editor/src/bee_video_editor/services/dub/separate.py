from __future__ import annotations
import shutil
import subprocess
from pathlib import Path


def separate_vocals(
    audio_path: Path, output_dir: Path, model: str = "htdemucs",
) -> tuple[Path, Path]:
    """Separate vocals from accompaniment using demucs."""
    vocals_path = output_dir / "vocals.wav"
    accompaniment_path = output_dir / "accompaniment.wav"
    if vocals_path.exists() and accompaniment_path.exists():
        return vocals_path, accompaniment_path
    output_dir.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(
        ["python", "-m", "demucs", "-n", model, "--two-stems", "vocals",
         "-o", str(output_dir), str(audio_path)],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"demucs failed: {result.stderr}")
    stem_name = audio_path.stem
    demucs_dir = output_dir / model / stem_name
    shutil.move(str(demucs_dir / "vocals.wav"), str(vocals_path))
    shutil.move(str(demucs_dir / "no_vocals.wav"), str(accompaniment_path))
    shutil.rmtree(output_dir / model, ignore_errors=True)
    return vocals_path, accompaniment_path
