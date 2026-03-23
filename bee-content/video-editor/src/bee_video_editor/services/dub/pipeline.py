from __future__ import annotations
import json
from pathlib import Path
from rich.console import Console
from bee_video_editor.services.dub.models import DubConfig
from bee_video_editor.services.dub.status import StatusTracker
from bee_video_editor.services.dub.download import download_video
from bee_video_editor.services.dub.transcribe import transcribe_audio
from bee_video_editor.services.dub.diarize import diarize_segments
from bee_video_editor.services.dub.separate import separate_vocals
from bee_video_editor.services.dub.translate import translate_segments
from bee_video_editor.services.dub.voices import setup_voices
from bee_video_editor.services.dub.tts import generate_dubbed_audio
from bee_video_editor.services.dub.compose import compose_dubbed_video

console = Console()


def run_pipeline(project_dir: Path, url: str | None = None, lang: str | None = None) -> Path:
    """Run the full dubbing pipeline."""
    config_path = project_dir / "dub.json"
    config = DubConfig.load(config_path) if config_path.exists() else DubConfig()
    status = StatusTracker(project_dir / "status.json")
    source = project_dir / (config.source or "source.mp4")
    target_lang = lang or config.languages[0]

    if url:
        console.print("[bold]Step 0:[/] Downloading source...")
        download_video(url, source)

    console.print("[bold]Step 1:[/] Transcribing...")
    transcribe_audio(source, project_dir / "transcript.json", engine=config.transcription.engine)

    voices_dir = project_dir / "voices"
    console.print("[bold]Step 2:[/] Diarizing speakers...")
    diarize_segments(
        source, project_dir / "transcript.json", project_dir / "diarization.json", voices_dir,
        engine=config.diarization.engine, min_speakers=config.diarization.min_speakers,
        max_speakers=config.diarization.max_speakers,
    )

    console.print("[bold]Step 3:[/] Separating vocals...")
    vocals, accompaniment = separate_vocals(source, project_dir / "separated", model=config.separation.model)

    console.print(f"[bold]Step 4:[/] Translating to {target_lang}...")
    translations_path = project_dir / "translations" / f"{target_lang}.json"
    translate_segments(
        project_dir / "diarization.json", translations_path, lang=target_lang,
        engine=config.translation.engine, model=config.translation.model, style=config.translation.style,
    )

    console.print("[bold]Step 5:[/] Setting up voices...")
    diarization = json.loads((project_dir / "diarization.json").read_text())
    setup_voices(
        voices_dir, voices_dir / "manifest.json", speakers=diarization["speakers"],
        mode=config.voices.mode, overrides=config.voices.overrides,
    )

    console.print("[bold]Step 6:[/] Generating dubbed audio...")
    tts_dir = project_dir / "tts" / target_lang
    generate_dubbed_audio(
        translations_path, voices_dir / "manifest.json", tts_dir, status,
        model=config.tts.model, stability=config.tts.stability, similarity_boost=config.tts.similarity_boost,
    )

    output_path = project_dir / "output" / f"{target_lang}.mp4"
    console.print("[bold]Step 7:[/] Composing final video...")
    compose_dubbed_video(
        source, translations_path, tts_dir, output_path,
        accompaniment_path=accompaniment if config.compositor.keep_background_audio else None,
        background_volume=config.compositor.background_volume, subtitles=config.compositor.subtitles,
        subtitle_style=config.compositor.subtitle_style, target_lufs=config.compositor.target_lufs,
    )
    console.print(f"[bold green]Done![/] Output: {output_path}")
    return output_path
