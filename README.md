# 🎬 Avatar Video Processing Engine

A powerful, robust, and highly-typed FFmpeg-backed video processing engine. Designed explicitly to be operated via **Command Line Interface (CLI)** or natively invoked by **AI Agents (LLMs)** and business backend code.

---

## 🌟 Core Features

### 🎞️ Video Manipulation (FFmpeg Backend)
- **Clipping**: Precisely slice segments from videos with regex-validated timecodes.
- **Concat**: Splice multiple videos together. Uses advanced filter-graph re-encoding to flawlessly merge videos with different codecs and resolutions.
- **BGM Mixing**: Overlay background audio tracks onto videos with precise volume control.
- **Subtitle Burning**: Hard-burn `.srt` subtitles directly into the video stream for universal compatibility.
- **Auto-Subtitle (ASR)**: Automatically transcript spoken words in videos to highly accurate `.srt` files using AI (`faster-whisper`), with support for text alignment.

### 🛡️ Enterprise Robustness & Agent-Readiness
- **Strict Interface Typing**: All API endpoints use `Pydantic` schemas, offering automatic validation (e.g., timecode formatting, volume constraints) and seamless exporting to JSON Schema for Agent tool configurations.
- **Self-Healing & Exponential Backoff**: Transient system or I/O errors are caught by a custom `@with_retry` decorator, retrying failed FFmpeg runs intelligently to prevent workflow drops.
- **Dual-Channel Logging**: Detailed `DEBUG` traces and FFmpeg internal error messages are persistently logged to `logs/system.log`, while clean `INFO` feedback is streamed to the console.
- **Automatic Path Management**: Output directories are recursively generated to prevent file-not-found errors during export.

---

## 🚀 Installation

Ensure you have the system-level dependency **FFmpeg** installed (required by `ffmpeg-python`):

```bash
# macOS
brew install ffmpeg

# Ubuntu / Debian
sudo apt-get update && sudo apt-get install -y ffmpeg
```

Install the Python engine and its dependencies:

```bash
# Create a virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies (typer, pydantic, ffmpeg-python)
pip install -r requirements.txt
```

---

## 💻 Command Line Interface (CLI)

The system exposes a rich, auto-documented CLI using `typer`.
*(Make sure your virtual environment is activated)*

### 1. Clip a Video Segment
```bash
python -m src.cli.main clip original.mp4 snippet.mp4 --start 00:00:10 --end 00:00:20
```

### 2. Concatenate Multiple Videos
Merge any number of video fragments. The engine will safely re-encode them.
```bash
python -m src.cli.main concat part1.mp4 part2.mp4 part3.mp4 --output merged_final.mp4
```

### 3. Apply Background Music
Overlay dual audio tracks (original + BGM). Use `--volume` to balance the music (`1.0` = 100%, `0.5` = 50%).
```bash
python -m src.cli.main bgm source.mp4 music.mp3 final.mp4 --volume 0.5
```

### 4. Burn Subtitles
Embed an SRT file visually onto the video frame.
```bash
python -m src.cli.main subtitle source.mp4 captions.srt ready_to_publish.mp4
```

### 5. Auto-Generate Subtitles (ASR)
Extract audio and transcribe it to an SRT file using Whisper. Optional `--text-script` parameter forces the AI to align with your plain text script for perfect accuracy.
```bash
python -m src.cli.main auto-subtitle source.mp4 output.srt --text-script transcript.txt --model base
```

---

## 🤖 AI Agent & Developer API

The functions located in `src/api/video_agent.py` are strictly typed using **Pydantic**. 
You can use these components as standalone programmatic functions or expose them directly to your AI Agents.

### Example: Programmatic Pipeline Invocation
```python
from src.api.video_agent import (
    ClipTask, GenerateSrtTask, 
    process_clip, process_generate_srt
)

# 1. Clip the video
clip_task = ClipTask(
    input_path="assets/raw.mp4",
    output_path="exports/short.mp4",
    start_time="10.5",  
    end_time="00:00:25"
)
clipped_file = process_clip(clip_task)

# 2. Generate SRT from the clipped video 
srt_task = GenerateSrtTask(
    video_path=clipped_file,
    srt_path="exports/subs.srt",
    text_prompt_path="script_draft.txt",
    model_size="base"
)
srt_file = process_generate_srt(srt_task)
```

---

## 🧠 Using this Project as an AI Agent Tool

This project is structured specifically to serve as **"Action Tools" (Function Calling)** for Autonomous AI Agents (like LangChain, AutoGen, or raw OpenAI API). 

Since every tool parameter is encapsulated in a Pydantic model, you can instantly export them to JSON Schemas that the LLM understands natively.

**How to feed this to your LLM:**

```python
import json
from src.api.video_agent import ClipTask, SubtitleTask

# 1. Generate the exact JSON Schema expected by OpenAI / LLMs
clip_tool_schema = {
    "type": "function",
    "function": {
        "name": "process_clip",
        "description": "Cuts a specific segment out of a larger video file.",
        "parameters": ClipTask.model_json_schema() # <-- The magic happens here
    }
}

# Print it out to see the LLM-ready format!
print(json.dumps(clip_tool_schema, indent=2))
```

**What the LLM sees:**
Because of the Pydantic field descriptions in `video_agent.py`, the AI knows exactly what to do. It reads:
* *"input_path: Absolute or relative path to the input video file."*
* *"start_time: Start time for the clip, e.g., '00:00:10'."*

**Agent Loop Integration Check:**
1. Pass the generated Schemas to your Agent's `tools` array.
2. The Agent decides to "cut a video", and outputs a JSON: `{"input_path": "a.mp4", "start_time": "10", ...}`.
3. Pass that JSON directly into our pipeline: `process_clip(ClipTask(**agent_json_args))`.

---

## 🗂️ Project Structure

```text
Avatar-beta/
├── README.md               # Documentation
├── README_zh.md            # Chinese Documentation
├── requirements.txt        # Python package dependencies
├── logs/
│   └── system.log          # Detailed execution & error backtrace
└── src/
    ├── core/
    │   ├── utils.py        # Loggers & @with_retry self-healing
    │   ├── asr_ops.py      # Whisper AI audio processing
    │   └── ffmpeg_ops.py   # Secure ffmpeg-python subprocess wrapper
    ├── api/
    │   └── video_agent.py  # Pydantic Schemas & Agent exposure pipeline
    └── cli/
        └── main.py         # Typer-powered terminal interface
```
