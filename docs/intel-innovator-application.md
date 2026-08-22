# Intel Software Innovator Program — submission pack

This file is a ready-to-copy application draft for the [Intel Software Innovator Program for OpenVINO](https://www.intel.com/content/www/us/en/developer/community/edge-innovator-program.html).
It is deliberately written from measured facts in this repository. Replace the fields marked `TODO` with your own name and contact details before submitting.

## Current form gate (verified 2026-08-23)

The current Intel Smartsheet form requires the applicant to confirm that they are **18 years of age or older**. It also requires a real mailing address, phone number, email address, and LinkedIn URL. If you are under 18, do not submit this form or claim eligibility; ask Intel whether a parent/guardian or another route is available.

## Applicant fields

- Name: `TODO — your name`
- Country/region: `Japan`
- Email: `TODO — your email`
- GitHub: https://github.com/taichiro20100723-droid/npu-motion-studio
- Project title: `NPU Motion Studio`
- Primary hardware: `Intel Core Ultra 7 258V / Intel AI Boost NPU / Intel Arc 140V GPU`

## Short project description

**NPU Motion Studio turns two still images into the impossible middle between them.** A user selects image A and image B, writes one sentence describing the transformation, and receives a local MP4. OpenVINO LCM generates prompt-aware anchor images on the Intel NPU; the Arc GPU decodes and interpolates the intervals; Intel Quick Sync encodes the final video. The result is a fast, private, beginner-friendly A→B motion tool for concept reveals, music-video transitions, product ideas, and visual experiments.

## Why this is an OpenVINO project

OpenVINO is not an optional label in this project. It is the runtime boundary that makes the hardware pipeline possible:

1. A local CPU text path translates Japanese prompts and extracts an action timeline.
2. OpenVINO LCM runs the image-generation UNet on the Intel AI Boost NPU.
3. OpenVINO VAE decoding is assigned to the Intel Arc GPU.
4. The generated intervals are queued to GPU interpolation while the NPU draws the next anchor.
5. Quick Sync produces the H.264 MP4 without sending images or prompts to a cloud service.

The application keeps these device choices behind a one-screen UI. A beginner sees only A, B, one sentence, a quality choice, and Create.

## What is technically different

- **Endpoint-first generation:** A and B are fixed as the first and last decoded frames. The AI is asked to draw the transformation, rather than merely pan across one still image.
- **Prompt-aware timeline:** the sentence is translated locally when needed, classified into motion profiles, and attached to each intermediate anchor.
- **Anchor/flow hybrid:** the NPU supplies semantic changes; motion warping and GPU interpolation supply temporal smoothness between those changes.
- **Overlapped execution:** completed intervals enter the Arc GPU queue while the NPU generates the next anchor.
- **Graceful quality control:** Small, Medium, and Large choose the anchor budget up front, so users trade time for transformation detail without learning model terminology.
- **Local-first design:** the default server listens on `127.0.0.1`; input images and prompts remain on the PC.

## Evidence and measured results

All numbers below are warm-run measurements on one Windows 11 laptop with Core Ultra 7 258V, Intel AI Boost NPU, Intel Arc 140V, and OpenVINO 2025.4.1. They are not universal guarantees.

| Workflow | NPU images | Output | Total |
|---|---:|---:|---:|
| A→B dynamic, 8 anchors | 8 | 4 sec / 96 frames | 11.61 sec |
| Robot→dog, high quality | 12 | 5 sec / 120 frames | 20.69 sec |
| One-image fast mode | 4 | 3 sec / 47 frames | 5.80 sec |
| Robot→dog fast preview | 4 | 4 sec | 2.83 sec |
| Robot→dog quality render | 12 | 4 sec | 18.05 sec |

The latest fast-preview result is useful in a demo because it shows the interaction loop: a user can inspect a 4-anchor result in about three seconds, then choose whether to spend more time on the 12-anchor render. The full methodology is in [`docs/benchmarks.md`](benchmarks.md).

## Demonstration plan (60–75 seconds)

Use the included non-sensitive robot→dog sample. Do not claim that the app is a full video-diffusion model; describe it as a prompt-aware NPU-anchor and GPU-interpolation hybrid.

| Time | Screen | Voiceover / caption |
|---:|---|---|
| 0–5 s | A robot image and a Shiba Inu image | “What if a robot could become a dog?” |
| 5–12 s | Type the prompt | “Describe the change, not just the destination.” |
| 12–18 s | Select Medium and press Create | “One button. Everything stays on this PC.” |
| 18–30 s | Device overlay/architecture card | “CPU handles language, NPU draws anchors, Arc GPU smooths the intervals, Quick Sync writes MP4.” |
| 30–43 s | Play the A→B result | “The first frame is A, the last frame is B; the middle is AI-generated.” |
| 43–52 s | Show the 2.83 s fast preview badge | “Preview quickly before spending time on quality.” |
| 52–64 s | Show the 12-anchor quality result | “More anchors make the transformation richer.” |
| 64–75 s | GitHub page and final clip | “NPU Motion Studio is local, open, and reproducible.” |

Suggested prompt:

```text
A colossal steel battle robot transforms into a real Shiba Inu while sprinting toward the camera. Metal plates fold into orange fur, mechanical legs become paws, and the final dog runs through the same alley.
```

## Copy-ready application answers

### What did you build?

I built NPU Motion Studio, a local Windows application that creates an A→B transformation video from two still images and one natural-language sentence. It uses OpenVINO LCM on the Intel NPU for semantic anchor generation, the Intel Arc GPU for decoding and interpolation, and Quick Sync for MP4 output. The interface hides the hardware complexity so a beginner can create a result with one button.

### What problem does it solve?

Most image-to-video tools animate one existing image. That is useful for camera movement, but it does not directly answer “show me the process of becoming something else.” NPU Motion Studio makes that process the primary object: robot→dog, sketch→product, ruin→city, or any pair of user-supplied endpoints. It also makes local Intel AI PC hardware useful for a creative workflow without cloud upload or a node graph.

### Why Intel hardware and OpenVINO?

The project is designed around heterogeneous execution. The NPU is efficient for repeated diffusion inference, the Arc GPU is well suited to image decode and temporal interpolation, and Quick Sync provides a hardware video path. OpenVINO provides one local runtime and device-selection boundary for these stages, so the application can expose a simple UI while still using the CPU, NPU, and GPU deliberately.

### What is novel or interesting?

The novelty is the combination of endpoint locking, prompt-aware intermediate anchors, and overlapped NPU/GPU work. The project does not pretend to be a general video-diffusion model. It is a compact, inspectable hybrid that makes a visually surprising transformation quickly and lets the user control the quality budget before generation.

### How can others reproduce it?

The repository contains the Windows setup script, source, tests, architecture notes, model manifest, benchmark methodology, and example inputs/outputs. Models are downloaded during setup and are not committed to Git. The default service is local-only. A compatible Intel Core Ultra NPU and Arc GPU are recommended; CPU fallback and mock engine paths are retained for development and testing.

### What would you improve next?

The next milestones are better hand/face consistency, stronger subject masks for Motion Brush, beat-aware timing, and a repeatable 30-input performance evaluation. These improvements keep the same OpenVINO device split while increasing the reliability of the generated middle.

## Links to include

- Repository: https://github.com/taichiro20100723-droid/npu-motion-studio
- Japanese README: https://github.com/taichiro20100723-droid/npu-motion-studio/blob/main/README.ja.md
- English README: https://github.com/taichiro20100723-droid/npu-motion-studio/blob/main/README.md
- Architecture: https://github.com/taichiro20100723-droid/npu-motion-studio/blob/main/docs/architecture.md
- Benchmarks: https://github.com/taichiro20100723-droid/npu-motion-studio/blob/main/docs/benchmarks.md
- A→B sample video: https://github.com/taichiro20100723-droid/npu-motion-studio/blob/main/examples/robot-to-dog/robot-to-dog.mp4
- Fast preview sample: https://github.com/taichiro20100723-droid/npu-motion-studio/blob/main/examples/robot-to-dog/robot-to-dog.gif

## Intel disclosure wording

Do not describe yourself as an Intel Software Innovator until Intel accepts the application. If accepted and you later publish a related post, follow Intel's disclosure guidance, for example:

```text
#IntelSoftwareInnovator I built NPU Motion Studio with OpenVINO on an Intel Core Ultra AI PC. This post describes my own measured experience; results vary by hardware and model settings.
```

## Final checklist before clicking Apply

- [ ] Replace the applicant fields at the top.
- [ ] Confirm that the current form's 18+ requirement applies to you.
- [ ] Prepare your real address, phone number, email address, and LinkedIn URL; these are transmitted to Intel by the form.
- [ ] Open every GitHub link in a private browser window and confirm it is public.
- [ ] Record the 60–75 second robot→dog demo using the included prompt.
- [ ] Show the actual application UI and the actual measured time; do not use an unverified claim.
- [ ] Add the demo URL to the application form.
- [ ] Submit the application at Intel's official page.
- [ ] Keep the confirmation email and prepare to explain the project in a short discovery call.

## What remains for the applicant

I can prepare the copy, structure, demo plan, README, architecture explanation, and benchmark presentation. Only you should enter your legal name, email, age/eligibility information, and consent to Intel's terms, and only you can press the final submission button or attend the discovery call.
