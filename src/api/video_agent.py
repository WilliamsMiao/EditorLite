import os
import re
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator
import src.core.ffmpeg_ops as ops

def validate_time_format(v: str) -> str:
    """Ensure time follows formats like '10', '00:10', '10.5', '00:00:10.500'."""
    pattern = r'^(\d{1,2}:)?(\d{1,2}:)?\d+(\.\d{1,3})?$'
    if not re.match(pattern, str(v)):
        raise ValueError(f"Invalid time format: {v}. Use seconds (e.g., '10') or HH:MM:SS (e.g., '00:00:10').")
    return str(v)

class ClipTask(BaseModel):
    """Configuration for cutting a segment out of a video."""
    input_path: str = Field(..., description="Absolute or relative path to the input video file.")
    output_path: str = Field(..., description="Path where the clipped video will be saved.")
    start_time: str = Field(..., description="Start time for the clip, e.g., '00:00:10' or '10'.")
    end_time: str = Field(..., description="End time for the clip, e.g., '00:00:20' or '20'.")

    @field_validator("start_time", "end_time")
    @classmethod
    def check_time_params(cls, v):
        return validate_time_format(v)

class ConcatTask(BaseModel):
    """Configuration for concatenating multiple video segments."""
    input_paths: List[str] = Field(..., description="Ordered list of paths of video files to concatenate.")
    output_path: str = Field(..., description="Path where the final concatenated video will be saved.")

class BGMTask(BaseModel):
    """Configuration for adding background music to a video."""
    video_path: str = Field(..., description="Path to the source video file.")
    audio_path: str = Field(..., description="Path to the background audio file (mp3, wav).")
    output_path: str = Field(..., description="Path for the output video with BGM.")
    volume: float = Field(1.0, description="Volume multiplier for the BGM (1.0 is original, 0.5 is half).", ge=0.0, le=10.0)

class SubtitleTask(BaseModel):
    """Configuration for burning subtitles into a video."""
    video_path: str = Field(..., description="Path to the source video file.")
    srt_path: str = Field(..., description="Path to the subtitle file (.srt).")
    output_path: str = Field(..., description="Path for the output video with subtitles.")

class GenerateSrtTask(BaseModel):
    """Configuration for auto-generating SRT from video using ASR."""
    video_path: str = Field(..., description="Path to the source video file.")
    srt_path: str = Field(..., description="Path where the generated SRT file will be saved.")
    text_prompt_path: Optional[str] = Field(None, description="Optional path to a plain text file containing the exact transcript, used as a prompt to guide the ASR aligner.")
    model_size: str = Field("base", description="Whisper model size: tiny, base, small, medium, large-v3.")

def process_clip(task: ClipTask) -> str:
    """
    Cuts a specific segment out of a larger video file.
    Ideal for Agents needing to isolate key moments.
    """
    return ops.cut_video(task.input_path, task.output_path, task.start_time, task.end_time)

def process_concat(task: ConcatTask) -> str:
    """
    Merges an ordered list of video files into one continuous video.
    Note: Requires all input clips to share codec and resolution.
    """
    return ops.concat_videos(task.input_paths, task.output_path)

def process_bgm(task: BGMTask) -> str:
    """
    Overlays a background music track onto an existing video.
    Mixes the original video audio with the new background audio channel.
    """
    return ops.add_bgm(task.video_path, task.audio_path, task.output_path, task.volume)

def process_subtitle(task: SubtitleTask) -> str:
    """
    Burns an SRT subtitle file directly into the video frames.
    Requires FFmpeg to re-encode the video stream.
    """
    return ops.add_subtitles(task.video_path, task.srt_path, task.output_path)

def process_generate_srt(task: GenerateSrtTask) -> str:
    """
    Auto-generates an SRT file from a video by extracting its audio and running local Whisper ASR.
    Optionally takes a plain text prompt to force-align the output slightly more to the script.
    """
    from src.core.asr_ops import generate_srt_from_video
    return generate_srt_from_video(task.video_path, task.srt_path, task.text_prompt_path, task.model_size)
