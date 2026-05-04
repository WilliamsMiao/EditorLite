import ffmpeg
import os
import shutil
from pathlib import Path
from src.core.utils import logger, with_retry

def _ensure_ffmpeg_installed():
    """Ensure ffmpeg is available in the system PATH."""
    if not shutil.which("ffmpeg"):
        raise EnvironmentError(
            "FFmpeg not found in system PATH. Please install FFmpeg (e.g., `brew install ffmpeg` or `apt-get install ffmpeg`)."
        )

# Run check on module load
_ensure_ffmpeg_installed()

def _ensure_output_dir(output_path: str):
    """Ensure the target output directory exists."""
    out_dir = Path(output_path).parent
    out_dir.mkdir(parents=True, exist_ok=True)

@with_retry(max_retries=3, delay=1.5)
def cut_video(input_path: str, output_path: str, start: str, end: str) -> str:
    """
    Cut a video from start to end time.
    """
    logger.info(f"Starting cut_video: slicing '{input_path}' from {start} to {end}")
    
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input video not found: {input_path}")
    
    _ensure_output_dir(output_path)
    
    try:
        (
            ffmpeg
            .input(input_path, ss=start, to=end)
            .output(output_path, c="copy")
            .overwrite_output()
            .run(capture_stdout=True, capture_stderr=True)
        )
        logger.info(f"Successfully created cropped video at: {output_path}")
        return output_path
    except ffmpeg.Error as e:
        err_msg = e.stderr.decode('utf-8') if e.stderr else str(e)
        logger.error(f"FFmpeg Error in cut_video: {err_msg}")
        raise RuntimeError(f"FFmpeg Error: {err_msg}")

@with_retry(max_retries=3, delay=2.0)
def concat_videos(input_paths: list[str], output_path: str) -> str:
    """
    Concatenate multiple videos into a single video file.
    Uses concat filter instead of demuxer to handle varying encodings better,
    re-encoding the streams to ensure they merge properly.
    """
    logger.info(f"Starting concat_videos: uniting {len(input_paths)} clips into '{output_path}'")
    
    if not input_paths:
        raise ValueError("No input paths provided")
        
    for path in input_paths:
        if not os.path.exists(path):
            raise FileNotFoundError(f"Input video not found: {path}")

    _ensure_output_dir(output_path)

    # Use filter_complex to concatenate streams for greater robustness
    # This prevents failures caused by slightly different codecs across inputs.
    try:
        inputs = [ffmpeg.input(p) for p in input_paths]
        # Flatten streams: [v0, a0, v1, a1, ...]
        streams = []
        for i in inputs:
            streams.extend([i.video, i.audio])
            
        merged = ffmpeg.concat(*streams, v=1, a=1)
        (
            ffmpeg
            .output(merged[0], merged[1], output_path)
            .overwrite_output()
            .run(capture_stdout=True, capture_stderr=True)
        )
        logger.info(f"Successfully concatenated video at: {output_path}")
        return output_path
    except ffmpeg.Error as e:
        err_msg = e.stderr.decode('utf-8') if e.stderr else str(e)
        logger.error(f"FFmpeg Error in concat_videos: {err_msg}")
        raise RuntimeError(f"FFmpeg Error during Concat: {err_msg}")

@with_retry(max_retries=3, delay=2.0)
def add_bgm(video_path: str, audio_path: str, output_path: str, volume: float = 1.0) -> str:
    """
    Add background music to a video. Replaces original audio or mixes depending on needs.
    Here we mix original audio and new audio.
    """
    logger.info(f"Starting add_bgm: mixing '{audio_path}' (vol:{volume}) into '{video_path}'")
    
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video not found: {video_path}")
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio not found: {audio_path}")
        
    _ensure_output_dir(output_path)
    
    video = ffmpeg.input(video_path)
    audio = ffmpeg.input(audio_path).filter('volume', volume)
    
    try:
        # mix the audio from video and bgm, map the video output
        merged_audio = ffmpeg.filter([video.audio, audio], 'amix', duration='first')
        (
            ffmpeg
            .output(video.video, merged_audio, output_path, vcodec='copy', acodec='aac', shortest=None)
            .overwrite_output()
            .run(capture_stdout=True, capture_stderr=True)
        )
        logger.info(f"Successfully mixed BGM into video at: {output_path}")
        return output_path
    except ffmpeg.Error as e:
        err_msg = e.stderr.decode('utf-8') if e.stderr else str(e)
        logger.error(f"FFmpeg Error in add_bgm: {err_msg}")
        raise RuntimeError(f"FFmpeg Error: {err_msg}")

@with_retry(max_retries=3, delay=2.0)
def add_subtitles(video_path: str, srt_path: str, output_path: str) -> str:
    """
    Burn subtitles (.srt) into a video using the subtitles filter.
    """
    logger.info(f"Starting add_subtitles: burning '{srt_path}' into '{video_path}'")
    
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video not found: {video_path}")
    if not os.path.exists(srt_path):
        raise FileNotFoundError(f"Subtitles not found: {srt_path}")
        
    _ensure_output_dir(output_path)
    
    try:
        (
            ffmpeg
            .input(video_path)
            .output(output_path, vf=f"subtitles='{srt_path}'")
            .overwrite_output()
            .run(capture_stdout=True, capture_stderr=True)
        )
        logger.info(f"Successfully burned subtitles into video at: {output_path}")
        return output_path
    except ffmpeg.Error as e:
        err_msg = e.stderr.decode('utf-8') if e.stderr else str(e)
        logger.error(f"FFmpeg Error in add_subtitles: {err_msg}")
        raise RuntimeError(f"FFmpeg Error: {err_msg}")
