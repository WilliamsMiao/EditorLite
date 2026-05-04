import typer
from typing import List
from src.api.video_agent import (
    ClipTask, ConcatTask, BGMTask, SubtitleTask, GenerateSrtTask,
    process_clip, process_concat, process_bgm, process_subtitle, process_generate_srt
)

app = typer.Typer(help="Video Processing CLI & Agent Component")

@app.command("clip")
def clip_video(
    input_video: str = typer.Argument(..., help="Path to input video"),
    output_video: str = typer.Argument(..., help="Path to save output"),
    start: str = typer.Option("00:00:00", help="Start time (e.g., 00:00:10)"),
    end: str = typer.Option(..., help="End time (e.g., 00:00:20)")
):
    """Cut a specific clip from a video."""
    task = ClipTask(input_path=input_video, output_path=output_video, start_time=start, end_time=end)
    result = process_clip(task)
    typer.echo(f"Success! Clipped video saved to: {result}")

@app.command("concat")
def concat_videos(
    inputs: List[str] = typer.Argument(..., help="List of videos to concatenate"),
    output: str = typer.Option(..., "--output", "-o", help="Path to save concatenated video")
):
    """Concatenate multiple videos sequentially."""
    task = ConcatTask(input_paths=inputs, output_path=output)
    result = process_concat(task)
    typer.echo(f"Success! Concatenated video saved to: {result}")

@app.command("bgm")
def apply_bgm(
    video: str = typer.Argument(..., help="Path to source video"),
    audio: str = typer.Argument(..., help="Path to background audio"),
    output: str = typer.Argument(..., help="Path to save output"),
    volume: float = typer.Option(1.0, help="BGM volume multiplier")
):
    """Mix background music into a video."""
    task = BGMTask(video_path=video, audio_path=audio, output_path=output, volume=volume)
    result = process_bgm(task)
    typer.echo(f"Success! Video with BGM saved to: {result}")

@app.command("subtitle")
def apply_subtitle(
    video: str = typer.Argument(..., help="Path to source video"),
    srt_file: str = typer.Argument(..., help="Path to SRT subtitle file"),
    output: str = typer.Argument(..., help="Path to save output")
):
    """Burn SRT subtitles into the video frames."""
    task = SubtitleTask(video_path=video, srt_path=srt_file, output_path=output)
    result = process_subtitle(task)
    typer.echo(f"Success! Video with subtitles saved to: {result}")

@app.command("auto-subtitle")
def auto_subtitle(
    video: str = typer.Argument(..., help="Path to source video"),
    output_srt: str = typer.Argument(..., help="Path to save generated SRT file"),
    text_script: str = typer.Option(None, help="Path to plain text script to guide vocabulary and alignment"),
    model: str = typer.Option("base", help="Whisper model size (tiny, base, small, medium)")
):
    """Auto-generate SRT subtitles from video audio using AI (Whisper)."""
    task = GenerateSrtTask(video_path=video, srt_path=output_srt, text_prompt_path=text_script, model_size=model)
    result = process_generate_srt(task)
    typer.echo(f"Success! Auto-generated SRT saved to: {result}")

if __name__ == "__main__":
    app()
