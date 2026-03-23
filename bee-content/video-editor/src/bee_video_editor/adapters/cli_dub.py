# src/bee_video_editor/adapters/cli_dub.py
from __future__ import annotations
from pathlib import Path
import typer
from rich.console import Console

dub_app = typer.Typer(name="dub", help="AI dubbing pipeline.", no_args_is_help=True)
console = Console()


@dub_app.command()
def run(
    source: str = typer.Argument(..., help="YouTube URL or local file path"),
    lang: str = typer.Option("es", "--lang", "-l", help="Target language code"),
    voices: str = typer.Option("clone", "--voices", help="Voice mode: clone or mapped"),
    project_dir: str = typer.Option(".", "--project-dir", "-p", help="Project directory"),
):
    """Run the full dubbing pipeline."""
    from bee_video_editor.services.dub.pipeline import run_pipeline
    project = Path(project_dir)
    project.mkdir(parents=True, exist_ok=True)
    url = source if source.startswith("http") else None
    run_pipeline(project, url=url, lang=lang)


@dub_app.command()
def download(
    url: str = typer.Argument(..., help="YouTube URL"),
    project_dir: str = typer.Option(".", "-p", help="Project directory"),
):
    """Download source video."""
    from bee_video_editor.services.dub.download import download_video
    out = Path(project_dir) / "source.mp4"
    download_video(url, out)
    console.print(f"Downloaded to {out}")


@dub_app.command()
def transcribe(
    project_dir: str = typer.Option(".", "-p", help="Project directory"),
):
    """Transcribe source audio."""
    from bee_video_editor.services.dub.transcribe import transcribe_audio
    p = Path(project_dir)
    transcribe_audio(p / "source.mp4", p / "transcript.json")
    console.print("Transcription complete.")


@dub_app.command()
def diarize(
    project_dir: str = typer.Option(".", "-p", help="Project directory"),
):
    """Identify speakers in transcript."""
    from bee_video_editor.services.dub.diarize import diarize_segments
    p = Path(project_dir)
    diarize_segments(p / "source.mp4", p / "transcript.json", p / "diarization.json", p / "voices")
    console.print("Diarization complete.")


@dub_app.command()
def separate(
    project_dir: str = typer.Option(".", "-p", help="Project directory"),
):
    """Separate vocals from background audio."""
    from bee_video_editor.services.dub.separate import separate_vocals
    p = Path(project_dir)
    separate_vocals(p / "source.mp4", p / "separated")
    console.print("Vocal separation complete.")


@dub_app.command()
def translate(
    lang: str = typer.Option("es", "--lang", "-l", help="Target language"),
    engine: str = typer.Option("claude", "--engine", help="Translation engine"),
    project_dir: str = typer.Option(".", "-p", help="Project directory"),
):
    """Translate segments to target language."""
    from bee_video_editor.services.dub.translate import translate_segments
    p = Path(project_dir)
    translate_segments(p / "diarization.json", p / "translations" / f"{lang}.json", lang=lang, engine=engine)
    console.print(f"Translation to {lang} complete.")


@dub_app.command(name="voices")
def voices_cmd(
    mode: str = typer.Option("clone", "--mode", help="clone or mapped"),
    project_dir: str = typer.Option(".", "-p", help="Project directory"),
):
    """Set up voices (clone or map)."""
    import json
    from bee_video_editor.services.dub.voices import setup_voices
    p = Path(project_dir)
    diarization = json.loads((p / "diarization.json").read_text())
    setup_voices(p / "voices", p / "voices" / "manifest.json", diarization["speakers"], mode=mode)
    console.print("Voices configured.")


@dub_app.command()
def tts(
    lang: str = typer.Option("es", "--lang", "-l", help="Target language"),
    retry_failed: bool = typer.Option(False, "--retry-failed", help="Retry failed segments"),
    project_dir: str = typer.Option(".", "-p", help="Project directory"),
):
    """Generate dubbed TTS audio."""
    from bee_video_editor.services.dub.tts import generate_dubbed_audio
    from bee_video_editor.services.dub.status import StatusTracker
    p = Path(project_dir)
    status = StatusTracker(p / "status.json")
    if retry_failed:
        status.retry_failed("tts")
    generate_dubbed_audio(p / "translations" / f"{lang}.json", p / "voices" / "manifest.json", p / "tts" / lang, status)
    console.print(f"TTS generation for {lang} complete.")


@dub_app.command()
def compose(
    lang: str = typer.Option("es", "--lang", "-l", help="Target language"),
    project_dir: str = typer.Option(".", "-p", help="Project directory"),
):
    """Compose final dubbed video."""
    from bee_video_editor.services.dub.compose import compose_dubbed_video
    p = Path(project_dir)
    accompaniment = p / "separated" / "accompaniment.wav"
    compose_dubbed_video(
        p / "source.mp4", p / "translations" / f"{lang}.json",
        p / "tts" / lang, p / "output" / f"{lang}.mp4",
        accompaniment_path=accompaniment if accompaniment.exists() else None,
    )
    console.print(f"Composed {lang} video.")


@dub_app.command()
def status(
    project_dir: str = typer.Option(".", "-p", help="Project directory"),
):
    """Show pipeline status."""
    import json
    from rich.table import Table
    p = Path(project_dir)
    status_file = p / "status.json"
    if not status_file.exists():
        console.print("No status file found.")
        return
    data = json.loads(status_file.read_text())
    table = Table(title="Dub Pipeline Status")
    table.add_column("Segment")
    table.add_column("Step")
    table.add_column("State")
    table.add_column("Error")
    for key, entry in sorted(data.items()):
        seg, step = key.rsplit(":", 1)
        table.add_row(seg, step, entry["state"], entry.get("error", ""))
    console.print(table)
