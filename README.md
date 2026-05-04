# 🎬 Avatar Video Processing Engine

A powerful, robust, and highly-typed FFmpeg-backed video processing engine. Designed explicitly to be operated via **Command Line Interface (CLI)** or natively invoked by **AI Agents (LLMs)** and business backend code.

---

## 🌟 Core Features

### 🎞️ Video Manipulation (FFmpeg Backend)
- **Clipping**: Precisely slice segments from videos with regex-validated timecodes.
- **Concat**: Splice multiple videos together. Uses advanced filter-graph re-encoding to flawlessly merge videos with different codecs and resolutions.
- **BGM Mixing**: Overlay background audio tracks onto videos with precise volume control.
- **Subtitle Burning**: Hard-burn `.srt` subtitles directly into the video stream for universal compatibility.

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

---

## 🤖 AI Agent & Developer API

The functions located in `src/api/video_agent.py` are strictly typed using **Pydantic**. 
For LangChain, AutoGen, or OpenAI function-calling implementations, you can export these schemas directly as tools.

### Example: Programmatic Invocation
```python
from src.api.video_agent import (
    ClipTask, BGMTask, process_clip, process_bgm
)

# 1. AI or User generates the strongly-typed task
# The Pydantic model automatically validates the `start_time` and `end_time` formats.
clip_task = ClipTask(
    input_path="assets/raw.mp4",
    output_path="exports/short.mp4",
    start_time="10.5",  # Supports seconds, floats, or HH:MM:SS
    end_time="00:00:25"
)

# 2. Process via the Engine (Equipped with logging & self-healing)
clipped_file = process_clip(clip_task)

# 3. Chain immediately to another task
bgm_task = BGMTask(
    video_path=clipped_file,
    audio_path="assets/lofi.mp3",
    output_path="exports/final_vlog.mp4",
    volume=0.3
)
final_file = process_bgm(bgm_task)
```

---

## 🗂️ Project Structure

```text
Avatar-beta/
├── README.md               # Documentation
├── requirements.txt        # Python package dependencies
├── logs/
│   └── system.log          # Detailed execution & error backtrace
└── src/
    ├── core/
    │   ├── utils.py        # Loggers & @with_retry self-healing
    │   └── ffmpeg_ops.py   # Secure ffmpeg-python subprocess wrapper
    ├── api/
    │   └── video_agent.py  # Pydantic Schemas & Agent exposure pipeline
    └── cli/
        └── main.py         # Typer-powered terminal interface
```
