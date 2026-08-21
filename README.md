<div align="center">

# NPU Motion Studio

**Endpoint-locked A→B motion, generated locally on an Intel NPU + Arc GPU.**

[![Windows](https://img.shields.io/badge/Windows-11-0078D4?logo=windows11)](https://www.microsoft.com/windows/)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![OpenVINO](https://img.shields.io/badge/OpenVINO-2025.4-5C2D91)](https://github.com/openvinotoolkit/openvino)
[![License](https://img.shields.io/badge/code-MIT-4ce3d9)](LICENSE)

[日本語](README.ja.md) · [Architecture](docs/architecture.md) · [Benchmarks](docs/benchmarks.md)

</div>

![A-to-B demo](examples/showcase/a-to-b.gif)

Choose image **A**, choose image **B**, and describe what happens between them. NPU Motion Studio keeps the
first and last frames exact, asks the NPU to draw the missing moments, then uses the Intel Arc GPU to connect
them into a smooth MP4. It runs locally: prompts and images do not leave the PC.

> This is not a full video-diffusion model. It is a deliberately fast hybrid: prompt-aware NPU keyframes,
> motion warping, GPU interpolation, and hardware video encoding.

## Why it feels different

- **A and B are sacred** — the decoded MP4 starts at A and ends at B, apart from normal H.264 compression.
- **The prompt actually drives time** — Japanese is translated locally; English goes directly into the motion
  classifier and every NPU keyframe prompt.
- **The whole Intel chip gets a job** — CPU for language, NPU for diffusion, Arc GPU for VAE + RIFE, and
  Quick Sync for H.264.
- **Aspect ratio is preserved** — A defines the output shape; B is contained without stretching.
- **Bilingual, beginner-friendly UI** — switch between English and Japanese with one click.
- **No hard 10-second limit** — quality modes can spend more time drawing better transitions.

## Two creation modes

### 1. Transform A → B (default)

<p align="center">
  <img src="examples/v3/A-robot.png" width="42%" alt="A input">
  <strong>&nbsp;→&nbsp;</strong>
  <img src="examples/v3/B-robot.png" width="42%" alt="B input">
</p>

The default experience. Pick two images and describe the process—not just the destination. The engine creates
4, 8, or 12 anchor moments, locks A/B at the ends, and interpolates the final sequence on the Arc GPU.

Example prompt:

```text
The same giant robot sprints through a rainy neon street, moving its body and legs dramatically as it changes
from pose A to pose B.
```

[Watch the 4-second MP4](examples/v3/A-to-B-robot.mp4) ·
[See eight sampled moments](examples/v3/A-to-B-contact-sheet.png)

### 2. Animate one image

![Single-image loop demo](examples/showcase/one-image-loop.gif)

Use a prompt, one image, or both. With seamless loop enabled, the final frame returns to A.

## Measured on a Core Ultra 7 258V

Windows 11 · Intel AI Boost NPU · Intel Arc 140V · OpenVINO 2025.4.1.

| Workflow | NPU work | Arc GPU work | Total |
|---|---:|---:|---:|
| A→B Dynamic, 8 anchors, 4 sec / 96 frames | 7.94 sec | 1.97 sec RIFE | **11.61 sec** |
| One image Fast, 4 anchors, 3 sec / 47 frames | 3.13 sec | 1.27 sec RIFE | **5.80 sec** |
| High quality build sequence, 12 anchors, 5 sec | 11.11 sec | 2.42 sec RIFE | **15.39 sec** |

These are warm-run measurements from one laptop, not universal guarantees. The first NPU compilation can take
minutes; cached launches took roughly 6–7 seconds on the test machine.

## Quick start on Windows

Requirements: Windows 11, Python 3.12, an Intel Core Ultra NPU, an Intel Arc GPU, and current Intel drivers.

1. Download or clone this repository.
2. Double-click **`setup_windows.bat`** once. It downloads the optional AI runtime, image model, translator, and
   RIFE binary. Models are not stored in Git.
3. Double-click **`run_windows.bat`** whenever you want to create.
4. Choose A and B, write the motion prompt, and press **Create the A-to-B video**.

Everything listens on `127.0.0.1` only. Generated videos are stored under `.runtime/outputs/`.

## How the pipeline works

```text
Japanese / English prompt
          │
          ▼
CPU: local translation + action timeline
          │
          ▼
NPU: 4 / 8 / 12 prompt-aware anchor images
          │
          ▼
Arc GPU: VAE decode + RIFE Vulkan interpolation
          │
          ▼
Intel Quick Sync: H.264 MP4
```

The A→B path blends endpoint conditions with a smoothstep schedule, applies action-specific motion warps, and
adds an exact progress cue to each prompt. Independent AI images are never simply cross-faded. After RIFE,
the first and last decoded frames are replaced with A and B again before encoding.

## Quality modes

| UI | Anchors | Intended use |
|---|---:|---|
| Fast | 4 | Quick experiments |
| Dynamic | 8 | Default; the best motion/time balance |
| High quality | 12 | More intermediate changes and higher prompt fidelity |

Video length is 2–10 seconds. The 180-second scheduler is a safety ceiling, not a target.

## Development

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[production,dev]"
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m ruff check .
```

The default `mock` engine runs without models and is useful for UI work:

```powershell
.\.venv\Scripts\python.exe -m npu_motion_studio
```

## Project map

- `src/npu_motion_studio/engines/openvino_lcm.py` — NPU generation, A/B locking, aspect-ratio handling
- `src/npu_motion_studio/dynamic_motion.py` — dance, build, drive, run, fly, transform, flow, camera timelines
- `src/npu_motion_studio/prompting.py` — offline Japanese translation and action classification
- `src/npu_motion_studio/engines/rife_vulkan.py` — Arc GPU frame interpolation
- `src/npu_motion_studio/engines/video_pipeline.py` — fallback flow and Quick Sync MP4 output
- `src/npu_motion_studio/web/` — build-free bilingual UI
- `MODEL_MANIFEST.json` — model and license boundaries

## Honest limitations

- Identity, hands, clothing, and vehicle details can drift between AI anchors.
- The engine can depict a machine transforming, but it does not guarantee mechanically correct part topology.
- Multi-person interaction and precise object hand-offs remain difficult.
- The included samples are real outputs from the test PC; results vary with prompts, images, heat, and drivers.

## Models, binaries, and licenses

The application code is MIT licensed. Downloaded models, OpenVINO, FFmpeg builds, and RIFE have their own
licenses. Model files and runtime binaries are excluded from Git. Review [MODEL_MANIFEST.json](MODEL_MANIFEST.json)
before redistribution or commercial use.

Contributions, benchmark results from other Intel NPU laptops, and weird A→B experiments are welcome.
