# 🎬 Avatar 视频处理引擎

一个强大、健壮且强类型的基于 FFmpeg 的视频处理引擎。专为您可以通过**命令行界面 (CLI)**，或通过**AI 智能体 (LLMs)** 及业务后端代码原生调用而设计。

---

## 🌟 核心功能

### 🎞️ 视频操作 (FFmpeg 后端)
- **剪辑 (Clipping)**: 使用经过正则校验的时间码精确提取视频片段。
- **拼接 (Concat)**: 将多段视频无缝拼接在一起。使用成熟的 Filter Graph 重新编码机制，可完美合并具有不同编码和分辨率的视频流。
- **背景音混音 (BGM Mixing)**: 将背景音乐轨道叠加到视频上，并支持精确的音量控制。
- **字幕烧录 (Subtitle Burning)**: 将 `.srt` 字幕硬编码（烧录）直接压制到视频流中，以确保各播放器上的绝对兼容性。

### 🛡️ 企业级健壮性 & 智能体接入就绪
- **严格的接口类型推导**: 所有 API 端点均使用 `Pydantic` 设计的数据约束模型（Schema），提供自动的合法性校验（例如时间码格式、音量边界），这使得该组件极为天然地顺滑对接各种智能体（Agent）的 JSON Schema 函数调用（Function Calling）。
- **自愈与指数退避重试**: 底层网络 I/O 的瞬时故障或 FFmpeg 的偶发崩溃将被自定义的 `@with_retry` 装饰器捕获。引擎会利用指数退避策略对失败的 FFmpeg 任务进行自动重试操作，防止工作流断裂。
- **双通道日志系统**: 最详尽的 `DEBUG` 级别回溯信息与 FFmpeg 报错 stderr 会持久化保存至 `logs/system.log` 内，而纯净的业务 `INFO` 阶段提示则会打印到控制台以供查阅。
- **自动化路径保障**: 输出路径的目标目录会被自动递归式创建，根绝了因文件夹不存在而导致的导出失败错误。

---

## 🚀 安装与配置

请确保您的系统级环境中已经安装了底层的 **FFmpeg** 库（这是 `ffmpeg-python` 的必须依赖）:

```bash
# macOS 环境
brew install ffmpeg

# Ubuntu / Debian 环境
sudo apt-get update && sudo apt-get install -y ffmpeg
```

安装 Python 处理引擎及其所需依赖:

```bash
# 创建独立的虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装相关依赖包 (typer, pydantic, ffmpeg-python)
pip install -r requirements.txt
```

---

## 💻 命令行终端使用 (CLI)

整个系统对外暴露了一套极为丰富且带自动生成文档说明的 CLI。
*(请确保此时处于激活的虚拟环境中)*

### 1. 剪辑提取视频
```bash
python -m src.cli.main clip original.mp4 snippet.mp4 --start 00:00:10 --end 00:00:20
```

### 2. 拼接多段视频
您可以合并任意数量的视频片段。引擎底层的过滤器会安全地为您进行重编码适配。
```bash
python -m src.cli.main concat part1.mp4 part2.mp4 part3.mp4 --output merged_final.mp4
```

### 3. 应用背景音乐
叠加双轨音频（保留原视频声音+新增 BGM）。使用 `--volume` 控制音乐响度 (`1.0` = 100%, `0.5` = 50%)。
```bash
python -m src.cli.main bgm source.mp4 music.mp3 final.mp4 --volume 0.5
```

### 4. 烧录字幕
将 SRT 字幕文件视觉化地压制融合到视频图像中。
```bash
python -m src.cli.main subtitle source.mp4 captions.srt ready_to_publish.mp4
```

---

## 🤖 AI 智能体 (Agent) & 开发者 API

所有位于 `src/api/video_agent.py` 的函数都被 **Pydantic** 提供严格类型约束保护。
针对诸如 LangChain、AutoGen 或者原生的 OpenAI Function-Calling 应用框架，您可以近乎零成本地将它们导出直接作为 Tools。

### 示例: 在外部业务代码 / Agent 规划树中调用
```python
from src.api.video_agent import (
    ClipTask, BGMTask, process_clip, process_bgm
)

# 1. AI 决策引擎（或者业务逻辑）产生经过严格校验的任务参数
# Pydantic 模型会自动核验 `start_time` 及 `end_time` 是否符合视频标准时间格式
clip_task = ClipTask(
    input_path="assets/raw.mp4",
    output_path="exports/short.mp4",
    start_time="10.5",  # 兼容秒数写法, 浮点数写法, 或标准 HH:MM:SS 写法
    end_time="00:00:25"
)

# 2. 传入处理引擎执行 (该动作受到日志系统与自愈机制的包裹保护)
clipped_file = process_clip(clip_task)

# 3. 链式调用到下一个处理环节中
bgm_task = BGMTask(
    video_path=clipped_file,
    audio_path="assets/lofi.mp3",
    output_path="exports/final_vlog.mp4",
    volume=0.3
)
final_file = process_bgm(bgm_task)
```

---

## 🗂️ 项目工程结构

```text
Avatar-beta/
├── README.md               # 英文说明文档
├── README_zh.md            # 中文说明文档
├── requirements.txt        # Python 依赖配置文件
├── logs/
│   └── system.log          # 极详尽的执行追踪记录及报错日志回溯
└── src/
    ├── core/
    │   ├── utils.py        # 日志组建与底层 @with_retry 指数重试与自愈核心
    │   └── ffmpeg_ops.py   # 安全封装的 ffmpeg-python 子进程操控层
    ├── api/
    │   └── video_agent.py  # 强类型 Pydantic Schema 及对外封装暴露的 Agent API 管道
    └── cli/
        └── main.py         # 基于 Typer 构建的优美终端应用
```