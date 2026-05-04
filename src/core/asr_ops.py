import os
import ffmpeg
from pathlib import Path
from src.core.utils import logger, with_retry
from src.core.ffmpeg_ops import _ensure_output_dir

def format_timestamp(seconds: float) -> str:
    """Convert seconds to SRT timestamp format HH:MM:SS,mmm"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    milliseconds = int((seconds - int(seconds)) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{milliseconds:03d}"

@with_retry(max_retries=2, delay=2.0)
def generate_srt_from_video(video_path: str, srt_path: str, text_prompt_path: str = None, model_size: str = "base") -> str:
    """
    Extract audio from video, run local ASR (faster-whisper), and align to text prompt if provided.
    Outputs an SRT file.
    """
    from faster_whisper import WhisperModel
    
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video not found: {video_path}")
        
    _ensure_output_dir(srt_path)
    audio_path = "temp_asr_audio.wav"
    
    try:
        logger.info(f"Extracting audio track from '{video_path}' for ASR processing...")
        (
            ffmpeg
            .input(video_path)
            .output(audio_path, acodec='pcm_s16le', ac=1, ar='16k')
            .overwrite_output()
            .run(quiet=True)
        )
        
        prompt = None
        if text_prompt_path and os.path.exists(text_prompt_path):
            logger.info(f"Reading plain text script from '{text_prompt_path}' as initial prompt guidelines...")
            with open(text_prompt_path, 'r', encoding='utf-8') as f:
                prompt = f.read().strip()

        logger.info(f"Loading Whisper model ({model_size}) on CPU...")
        # compute_type='int8' forces fast integer quantization, which performs great on CPUs (like Apple Silicon)
        model = WhisperModel(model_size, device="cpu", compute_type="int8")
        
        logger.info("Transcribing and aligning audio... This may take a moment.")
        # Generates segments. Passing 'initial_prompt' helps Whisper align to the exact vocabulary of the script.
        segments, info = model.transcribe(audio_path, initial_prompt=prompt, condition_on_previous_text=False)
        
        with open(srt_path, "w", encoding="utf-8") as f:
            for i, segment in enumerate(segments, start=1):
                start = format_timestamp(segment.start)
                end = format_timestamp(segment.end)
                f.write(f"{i}\n{start} --> {end}\n{segment.text.strip()}\n\n")

        logger.info(f"Successfully generated SRT file safely saved to: {srt_path}")
        
    except Exception as e:
        logger.error(f"ASR process failed: {str(e)}")
        raise
    finally:
        if os.path.exists(audio_path):
            os.remove(audio_path)
            
    return srt_path
