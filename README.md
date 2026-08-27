<div align="center">

# NPU AI Video

**Make still images move: robot → dog, sketch → product, ruin → city. Locally.**

[![Windows](https://img.shields.io/badge/Windows-11-0078D4?logo=windows11)](https://www.microsoft.com/windows/)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![OpenVINO](https://img.shields.io/badge/OpenVINO-2025.4-5C2D91)](https://github.com/openvinotoolkit/openvino)
[![License](https://img.shields.io/badge/code-MIT-4ce3d9)](LICENSE)

[日本語](README.ja.md) · [Architecture](docs/architecture.md) · [Benchmarks](docs/benchmarks.md) · [Intel Innovator submission pack](docs/intel-innovator-application.md)

</div>

![A giant robot physically transforms into a real Shiba Inu](examples/robot-to-dog/robot-to-dog.gif)

Most image-to-video tools animate one still. **NPU AI Video starts with two exact endpoints and creates
the impossible journey between them.** Drop in image A and image B, write one sentence—“metal armor folds into
orange fur”—and the app asks the NPU to draw a transformation timeline while the Arc GPU turns it into a smooth
MP4. No cloud upload, no node graph, and no server queue.

Use it for music-video transitions, short films, concept reveals, before/after shots, product transformations,
memes, and weird visual experiments. The included robot→dog clip is a real output from the app on one laptop.

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
- **A friendly first try** — pick a mode, tap a motion idea, and make a short clip without learning prompt jargon.
- **No hard 10-second limit** — quality modes can spend more time drawing better transitions.
- **Made for rapid experiments** — two images, one sentence, one Create button; the technical pipeline stays hidden.
- **Choose quality up front** — Small (8), Medium (12), or Large (20) NPU anchors are generated in one pass.
- **Motion Brush** — paint moving areas red, locked areas blue, and drag an arrow to direct the subject.
- **Overlapped hardware pipeline** — completed NPU intervals enter Arc RIFE while the NPU draws the next anchor,
  then Quick Sync finishes the MP4.
- **AI Character Stage** — lay ordinary characters out as a visual sheet, then let the NPU invent the strange
  in-between shapes naturally. The program does not decide a replacement glyph for each letter.
- **No prompt required** — the motion instruction is optional; an internal typography-aware transformation cue is
  used when the field is left blank.

[Watch a real Motion Brush robot→dog run](examples/motion-brush/robot-to-dog-motion-brush.mp4) — the robot was
painted red and directed to the right; the same brush data was used for the 12-anchor render.

## Two creation modes

### 1. Transform A → B (default)

<p align="center">
  <img src="examples/robot-to-dog/A-robot.png" width="42%" alt="A: giant robot">
  <strong>&nbsp;→&nbsp;</strong>
  <img src="examples/robot-to-dog/B-dog.png" width="42%" alt="B: real Shiba Inu">
</p>

The default experience. Pick two images and describe the process—not just the destination. The engine first
creates the selected Small, Medium, or Large anchor timeline in one pass. A/B stay locked at the ends.

Example prompt:

```text
A colossal steel battle robot transforms into a real Shiba Inu while sprinting toward the camera. Metal plates
fold into orange fur, mechanical legs become paws, and the final real dog runs joyfully through the same alley.
```

[Watch the 5-second MP4](examples/robot-to-dog/robot-to-dog.mp4) ·
[See eight sampled moments](examples/robot-to-dog/robot-to-dog-contact-sheet.png)

### 2. Animate one image

![Single-image loop demo](examples/showcase/one-image-loop.gif)

Use a prompt, one image, or both. With seamless loop enabled, the final frame returns to A.

### 3. Transform characters with AI

Choose **Transform text with AI**, enter source text such as `NPU MOTION`, and pick a mood hint. **Make character
sheet** lays the original characters out into a clean visual reference. Press **Create** and the local NPU
image-to-image pipeline morphs each character while preserving the sheet layout. The motion prompt is optional;
leave it blank for the built-in typography transformation cue, or add a short idea such as “turn into liquid light.”
You can also drop in your own character-sheet image, including a free-to-use asset, a photo you made, or an image
generated in another tool. The app sends that image to the local NPU as-is; check the license of any external asset.

### Music-video builder (experimental)

`scripts/make_music_video.py` cuts a song into roughly eight-second scenes, uses audio energy to vary motion, asks
the local NPU/Arc GPU pipeline for the animated cuts, and restores the original audio when joining the final MP4.
It automatically writes a large transformation chain (campus → classroom → library → stage) and dynamic xfade
transitions between cuts. An optional `.lrc` file adds lyric timing; without one, the builder still works from the
music's energy curve. The included safe recipe uses architecture and props instead of people because the local model
can occasionally ignore clothing instructions; real-person photos are never used as inputs.

```powershell
.\.venv\Scripts\python.exe scripts\make_music_video.py "song.mp4" `
  --backgrounds "face-free background folder" --photo-every 4
```

The included `make_waseda_saga_festival_mv.bat` is a one-double-click recipe for the local Waseda Saga festival
prototype. It uses only face-free school/campus backgrounds as references, keeps several real background-photo
shots, and generates the remaining festival visuals locally. Before publishing, confirm the school's permission and
the license for every photograph; the repository does not redistribute those photos.

## Measured on a Core Ultra 7 258V

Windows 11 · Intel AI Boost NPU · Intel Arc 140V · OpenVINO 2025.4.1.

| Workflow | NPU work | Arc GPU work | Total |
|---|---:|---:|---:|
| A→B Dynamic, 8 anchors, 4 sec / 96 frames | 7.94 sec | 1.97 sec RIFE | **11.61 sec** |
| Robot→dog High quality, 12 anchors, 5 sec / 120 frames | 15.25 sec | 3.99 sec RIFE | **20.69 sec** |
| One image Fast, 4 anchors, 3 sec / 47 frames | 3.13 sec | 1.27 sec RIFE | **5.80 sec** |
| High quality build sequence, 12 anchors, 5 sec | 11.11 sec | 2.42 sec RIFE | **15.39 sec** |
| v0.5 four-anchor robot→dog preview, 4 sec | 2.36 sec | 0.02 sec fast preview blend | **2.83 sec** |
| v0.5 approved robot→dog upgrade, 12 anchors, 4 sec | 15.46 sec | 8.23 sec RIFE, mostly overlapped | **18.05 sec** |

These are warm-run measurements from one laptop, not universal guarantees. The first NPU compilation can take
minutes; cached launches took roughly 6–7 seconds on the test machine.

## Quick start on Windows

Requirements: Windows 11, Python 3.12, an Intel Core Ultra NPU, an Intel Arc GPU, and current Intel drivers.

1. Download or clone this repository.
2. Double-click **`setup_windows.bat`** once. It downloads the optional AI runtime, image model, translator, and
   RIFE binary. Models are not stored in Git.
3. Double-click **`run_windows.bat`** whenever you want to create.
4. Choose A and B, optionally paint a Motion Brush, choose **Small**, **Medium**, or **Large**, and press **Create**.
   Medium (12 NPU frames) is the recommended starting point.

Everything listens on `127.0.0.1` only. Generated videos are stored under `.runtime/outputs/`.

## OpenVINO project submission

This repository is prepared for the [Intel Software Innovator Program for OpenVINO](https://www.intel.com/content/www/us/en/developer/community/edge-innovator-program.html).
The [submission pack](docs/intel-innovator-application.md) contains the project summary, device mapping, measured evidence, demo storyboard, and copy-ready application answers.

## How the pipeline works

```text
Japanese / English prompt
          │
          ▼
CPU: local translation + action timeline
          │
          ▼
NPU: selected 8 / 12 / 20 prompt-aware anchor images
          │
          ▼
Arc GPU: VAE decode + queued RIFE Vulkan intervals (overlapped with NPU)
          │
          ▼
Intel Quick Sync: H.264 MP4
```

The A→B path blends endpoint conditions with a smoothstep schedule, gives the NPU more freedom at the hybrid
midpoint, then increasingly protects the real B image near the end. Each anchor gets an exact progress cue and
an action-specific motion warp; independent AI images are never simply cross-faded. After RIFE, the first and
last decoded frames are replaced with A and B again before encoding.

## Quality controls

| UI | NPU anchors | Intended use |
|---|---:|---|
| Small | 8 | Fastest generation |
| Medium | 12 | Recommended balance |
| Large | 20 | Finer, higher-quality transformation timeline |

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
- Radical transformations can look surreal in the middle; mechanical part topology is not guaranteed.
- Multi-person interaction and precise object hand-offs remain difficult.
- The included samples are real outputs from the test PC; results vary with prompts, images, heat, and drivers.

## Models, binaries, and licenses

The application code is MIT licensed. Downloaded models, OpenVINO, FFmpeg builds, and RIFE have their own
licenses. Model files and runtime binaries are excluded from Git. Review [MODEL_MANIFEST.json](MODEL_MANIFEST.json)
before redistribution or commercial use.

Contributions, benchmark results from other Intel NPU laptops, and weird A→B experiments are welcome.
