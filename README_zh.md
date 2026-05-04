# 🎬 Avatar 视频处理引擎

一个强大、健壮且强类型的基于 FFmpeg 的视频处理引擎。专为您可以通过**命令行界面 (CLI)**，或通过**AI 智能体 (LLMs)** 及业务后端代码原生调用而设计。

---

## 🌟 核心功能

### 🎞️ 视频操作 (FFmpeg 后端)
- **剪辑 (Clipping)**: 使用经过正则校验的时间码精确提取视频片段。
- **拼接 (Concat)**: 将多段视频无缝拼接在一起。使用成熟的 Filter Graph 重新编码机制，可完美合并具有不同编码和分辨率的视频流。
- **背景音混音 (BGM Mixing)**: 将背景音乐轨道叠加到视频上，并支持精确的音量控制。
- **字幕烧录 (Subtitle Burning)**: 将 `.srt` 字幕硬编码（烧录）直接压制到视频流中，以确保各播放器上的绝对兼容性。
- **AI 字幕生成 (ASR)**: 使用底层大模型（`faster-whisper`）提取视频音频并直接翻译/识别出高精度 `.srt` 挂载文件，允许文本剧本强制对准纠错。

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

### 5. 自动生成字幕文件 (AI 音频识别)
抽取音频并交由 Whisper 生成时间戳。可通过 `--text-script` 传入纯文本手稿来强行引导 AI 的词汇精准度。
```bash
python -m src.cli.main auto-subtitle source.mp4 output.srt --text-script transcript.txt --model base
```

---

## 🤖 AI 智能体 (Agent) & 开发者 API

所有位于 `src/api/video_agent.py` 的函数都被 **Pydantic** 提供严格类型约束保护。
您可以近乎零成本地将它们作为普通的 Python 工具代码使用，或者作为 Tools 对接到智能体中。

### 示例: 业务流中的 API 链式调用
```python
from src.api.video_agent import (
    ClipTask, GenerateSrtTask, 
    process_clip, process_generate_srt
)

# 1. 剪切出一个片段
clip_task = ClipTask(
    input_path="assets/raw.mp4",
    output_path="exports/short.mp4",
    start_time="10.5",  
    end_time="00:00:25"
)
clipped_file = process_clip(clip_task)

# 2. 对刚剪好的视频自动生成配套字幕
srt_task = GenerateSrtTask(
    video_path=clipped_file,
    srt_path="exports/subs.srt",
    text_prompt_path="script_draft.txt", # 可选：参考原稿
    model_size="base"
)
srt_file = process_generate_srt(srt_task)
```

---

## 🧠 直接向 AI Agent 提供该系统库 (函数调用指南)

这个项目是完全根据 Autonomous AI Agent（比如 LangChain, AutoGen 或直接调用 OpenAI Function Calling）所需的**动作接口（Action Tools）**而架构的。

由于所有参数都包裹在了 `Pydantic` 模型下，您只需要一行代码就可以动态生成能够直接发给大语言模型（LLM）去解读的 JSON Schema。

**如何将其喂给大语言模型:**

```python
import json
from src.api.video_agent import ClipTask, SubtitleTask

# 1. 自动生成可以直接怼进 OpenAI 'functions' 参数内的配置
clip_tool_schema = {
    "type": "function",
    "function": {
        "name": "process_clip",
        "description": "从较长的视频文件中裁切出一段特定长短的切片视频。",
        "parameters": ClipTask.model_json_schema() # <-- 核心在这里！
    }
}

# 打印看看，已经是完美的 JSON 格式了
print(json.dumps(clip_tool_schema, indent=2, ensure_ascii=False))
```

**大模型（LLM）看到的是什么？**
得益于 `video_agent.py` 中写死的丰富的字段 `description` 注释，只要被 Schema 生成后，大模型天然就懂得每个参数该怎么填。比如：
* *"input_path: 绝对或相对的源视频文件路径"*
* *"start_time: 视频阶段的起始位置, 例如 '00:00:10'."*

**与 Agent 对接的工作流校验:**
1. 将刚才生成的 Tools Schema 发进 Agent 管线。
2. Agent 一旦察觉用户的诉求（“帮我截取视频的前十秒”），会输出如下推理动作字典：`{"input_path": "a.mp4", "start_time": "00:00:00", "end_time": "00:00:10"}`。
3. 业务代码接到 JSON，直接原封不动透传进该引擎：`process_clip(ClipTask(**agent_json_args))`，工作流完成并自愈兜底！

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
    │   ├── asr_ops.py      # Whisper AI 音频识别处理器
    │   └── ffmpeg_ops.py   # 安全封装的 ffmpeg-python 子进程操控层
    ├── api/
    │   └── video_agent.py  # 强类型 Pydantic Schema 及对外封装暴露的 Agent API 管道
    └── cli/
        └── main.py         # 基于 Typer 构建的优美终端应用
```