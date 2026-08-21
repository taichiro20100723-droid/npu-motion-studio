from __future__ import annotations

import base64
import hashlib
import io
import os
import subprocess
import threading
import time
import uuid
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter, ImageOps

from npu_motion_studio.domain import MotionArtifact, MotionRequest
from npu_motion_studio.dynamic_motion import frame_prompt, strength_for, warp_condition
from npu_motion_studio.engines.base import EngineProbe, MotionEngine, ProgressCallback
from npu_motion_studio.engines.rife_vulkan import RifeVulkanInterpolator
from npu_motion_studio.engines.video_pipeline import encode_mp4, interpolate_anchors
from npu_motion_studio.flowcache.motion import route_motion
from npu_motion_studio.prompting import (
    ActionKind,
    LocalPromptTranslator,
    classify_action,
    compact_prompt,
)
from npu_motion_studio.scheduler import DeadlineScheduler

MODEL_ID = "OpenVINO/LCM_Dreamshaper_v7-int8-ov"
MODEL_FOLDER_NAME = "LCM_Dreamshaper_v7-int8-ov"
TRANSLATION_MODEL_FOLDER = "opus-mt-ja-en"
REQUIRED_MODEL_FILES = (
    "model_index.json",
    "text_encoder/openvino_model.xml",
    "unet/openvino_model.xml",
    "vae_decoder/openvino_model.xml",
    "vae_encoder/openvino_model.xml",
)


def _default_runtime_root() -> Path:
    return Path(__file__).resolve().parents[3] / ".runtime"


def _model_directory() -> Path:
    configured = os.environ.get("NMS_MODEL_DIRECTORY")
    if configured:
        return Path(configured).expanduser()
    return _default_runtime_root() / "models" / MODEL_FOLDER_NAME


def _translation_directory() -> Path:
    configured = os.environ.get("NMS_TRANSLATION_MODEL_DIRECTORY")
    if configured:
        return Path(configured).expanduser()
    return _default_runtime_root() / "models" / TRANSLATION_MODEL_FOLDER


def _cache_directory() -> Path:
    configured = os.environ.get("NMS_COMPILE_CACHE_DIRECTORY")
    if configured:
        return Path(configured).expanduser()
    return _default_runtime_root() / "compile_cache"


@dataclass(frozen=True, slots=True)
class PreparedInput:
    canvas: Image.Image
    crop_box: tuple[int, int, int, int]
    output_size: tuple[int, int]


def _even(value: float) -> int:
    return max(2, round(value / 2) * 2)


def _prepare_input_image(image: Image.Image) -> PreparedInput:
    source = ImageOps.exif_transpose(image).convert("RGB")
    width, height = source.size
    if width >= height:
        output_width = 512
        output_height = min(512, _even(512 * height / width))
    else:
        output_height = 512
        output_width = min(512, _even(512 * width / height))

    background = ImageOps.fit(source, (512, 512), Image.Resampling.LANCZOS).filter(
        ImageFilter.GaussianBlur(radius=24)
    )
    foreground = source.resize((output_width, output_height), Image.Resampling.LANCZOS)
    left = (512 - output_width) // 2
    top = (512 - output_height) // 2
    background.paste(foreground, (left, top))
    return PreparedInput(
        canvas=background,
        crop_box=(left, top, left + output_width, top + output_height),
        output_size=(output_width, output_height),
    )


def _load_data_url_image(value: str) -> Image.Image:
    try:
        header, encoded = value.split(",", 1)
        if ";base64" not in header:
            raise ValueError
        raw = base64.b64decode(encoded, validate=True)
        image = Image.open(io.BytesIO(raw))
        image.load()
        return ImageOps.exif_transpose(image).convert("RGB")
    except Exception as exc:  # noqa: BLE001 - malformed user image is normalized here
        raise ValueError("入力画像を読み込めませんでした") from exc


def _decode_data_url(value: str) -> PreparedInput:
    return _prepare_input_image(_load_data_url_image(value))


def _prepare_transition_target(value: str, start: PreparedInput) -> Image.Image:
    source = _load_data_url_image(value)
    output_width, output_height = start.output_size
    background = ImageOps.fit(
        source, (output_width, output_height), Image.Resampling.LANCZOS
    ).filter(ImageFilter.GaussianBlur(radius=18))
    foreground = ImageOps.contain(
        source, (output_width, output_height), Image.Resampling.LANCZOS
    )
    left = (output_width - foreground.width) // 2
    top = (output_height - foreground.height) // 2
    background.paste(foreground, (left, top))

    canvas = ImageOps.fit(background, (512, 512), Image.Resampling.LANCZOS).filter(
        ImageFilter.GaussianBlur(radius=24)
    )
    crop_left, crop_top, _, _ = start.crop_box
    canvas.paste(background, (crop_left, crop_top))
    return canvas


def _array(image: Image.Image) -> np.ndarray:
    return np.ascontiguousarray(np.asarray(image.convert("RGB"), dtype=np.uint8))


def _cropped_array(image: Image.Image, crop_box: tuple[int, int, int, int]) -> np.ndarray:
    return _array(image.crop(crop_box))


def _seed(prompt: str, mode: str) -> int:
    digest = hashlib.blake2s(f"{prompt}:{mode}".encode(), digest_size=4).digest()
    return int.from_bytes(digest, "little")


def _transition_prompt(
    base_prompt: str,
    action: ActionKind,
    index: int,
    count: int,
) -> str:
    phase = index / max(1, count - 1)
    timed_action = compact_prompt(frame_prompt(base_prompt, action, index, count), max_words=48)
    return (
        f"{timed_action}, transition progress {round(phase * 100)} percent, "
        "one coherent subject, single scene, no split screen, no collage, no watermark"
    )


class OpenVINOLCMEngine(MotionEngine):
    key = "openvino-lcm"

    def __init__(self) -> None:
        self.model_directory = _model_directory()
        self.cache_directory = _cache_directory()
        self.translator = LocalPromptTranslator(_translation_directory())
        self.rife = RifeVulkanInterpolator()
        self._pipeline_lock = threading.RLock()
        self._image_pipeline = None
        self._text_pipeline = None

    @property
    def ready(self) -> bool:
        return self._image_pipeline is not None and self._text_pipeline is not None

    def probe(self) -> EngineProbe:
        missing = [
            name for name in REQUIRED_MODEL_FILES if not (self.model_directory / name).is_file()
        ]
        if missing:
            return EngineProbe(
                "NPU + Arc Dynamic Motion",
                False,
                "モデルが未準備です。setup_windows.batを実行してください",
                False,
            )
        try:
            import cv2  # noqa: F401
            import imageio_ffmpeg  # noqa: F401
            import openvino as ov
            import openvino_genai  # noqa: F401

            devices = tuple(ov.Core().available_devices)
        except (ImportError, RuntimeError, OSError) as exc:
            return EngineProbe("NPU + Arc Dynamic Motion", False, f"実行環境不足: {exc}", False)
        has_npu = any(str(device).upper().startswith("NPU") for device in devices)
        has_gpu = any(str(device).upper().startswith("GPU") for device in devices)
        detail = "NPU画像生成 + Arc GPU補間"
        if not self.rife.available:
            detail += "（GPU補間は準備中、CPU補間で起動）"
        return EngineProbe("NPU + Arc Dynamic Motion", has_npu and has_gpu, detail, has_npu)

    def prepare(self) -> None:
        self._ensure_pipelines()
        self.translator.prepare()
        warmup_path = self.cache_directory / "video-encoder-warmup.mp4"
        blank = np.zeros((512, 512, 3), dtype=np.uint8)
        encode_mp4([blank, blank], warmup_path, fps=16)
        warmup_path.unlink(missing_ok=True)

    def _ensure_pipelines(self) -> tuple[object, object, float]:
        with self._pipeline_lock:
            if self._image_pipeline is not None and self._text_pipeline is not None:
                return self._image_pipeline, self._text_pipeline, 0.0
            import openvino_genai as ov_genai

            started = time.perf_counter()
            image_pipeline = ov_genai.Image2ImagePipeline(str(self.model_directory))
            image_pipeline.reshape(1, 512, 512, 1.0)
            npu_cache = self.cache_directory / "npu"
            npu_cache.mkdir(parents=True, exist_ok=True)
            config = {
                "DEVICE_PROPERTIES": {
                    "CPU": {},
                    "NPU": {"CACHE_DIR": str(npu_cache)},
                    "GPU": {},
                }
            }
            image_pipeline.compile("CPU", "NPU", "GPU", config=config)
            text_pipeline = ov_genai.Text2ImagePipeline(image_pipeline)
            self._image_pipeline = image_pipeline
            self._text_pipeline = text_pipeline
            return image_pipeline, text_pipeline, time.perf_counter() - started

    def generate(
        self,
        request: MotionRequest,
        output_directory: Path,
        scheduler: DeadlineScheduler,
        progress: ProgressCallback,
    ) -> MotionArtifact:
        import openvino as ov

        started = time.monotonic()
        is_transition = request.creation_mode == "transition"
        prompt_source = request.prompt or (
            "smooth cinematic transformation from the first image to the second image"
        )
        route = route_motion(prompt_source)
        action = classify_action(prompt_source)
        seed = _seed(request.prompt, request.mode)
        notes: list[str] = [
            f"NPU anchors / action={action.value} / route={route.kind.value}",
            (
                "AとBを固定し、途中だけをNPUで描画"
                if is_transition
                else "元画像を残しながら時間別の指示でNPU再描画"
            ),
        ]

        progress("analysis", 3, "日本語と動作を理解しています")
        translated_prompt = compact_prompt(self.translator.translate(prompt_source))
        if translated_prompt != request.prompt.strip():
            notes.append(f"日本語解釈: {translated_prompt}")

        progress("image", 7, "NPUとGPUを準備しています")
        image_pipeline, text_pipeline, compile_seconds = self._ensure_pipelines()
        if compile_seconds:
            notes.append(f"モデル準備 {compile_seconds:.2f}秒")

        desired = {"fast": 4, "fun": 8, "wow": 12}[request.mode]
        fps = {"fast": 16, "fun": 24, "wow": 24}[request.mode]
        inference_steps = {"fast": 4, "fun": 6, "wow": 8}[request.mode]
        has_input = bool(request.input_image_data_url)
        strength = strength_for(action, request.mode, has_input_image=has_input)
        crop_box = (0, 0, 512, 512)

        image_started = time.perf_counter()
        prepared: PreparedInput | None = None
        if request.input_image_data_url:
            prepared = _decode_data_url(request.input_image_data_url)
            base = prepared.canvas
            crop_box = prepared.crop_box
            notes.append(
                f"元画像を保持: {prepared.output_size[0]}x{prepared.output_size[1]} "
                "(変形・正方形クロップなし)"
            )
        else:
            progress("image", 10, "最初の絵をNPUで描いています")
            first_prompt = frame_prompt(translated_prompt, action, 0, desired)
            tensor = text_pipeline.generate(
                first_prompt,
                width=512,
                height=512,
                num_inference_steps=inference_steps,
                guidance_scale=1.0,
                rng_seed=seed,
            )
            base = Image.fromarray(tensor.data[0])

        anchors = [base]
        if is_transition:
            if prepared is None or request.target_image_data_url is None:
                raise ValueError("AとBの画像を2枚とも選んでください")
            target = _prepare_transition_target(request.target_image_data_url, prepared)
            transition_strength = {"fast": 0.52, "fun": 0.68, "wow": 0.78}[
                request.mode
            ]
            for index in range(1, desired - 1):
                estimated_finish = max(8.0, request.duration_seconds * 1.6)
                if not scheduler.can_start(4.0 + estimated_finish):
                    notes.append(f"安全上限のため中間画像を{len(anchors) - 1}枚で確定")
                    break
                phase = index / (desired - 1)
                eased = phase * phase * (3.0 - 2.0 * phase)
                condition = Image.blend(base, target, eased)
                condition = warp_condition(condition, ActionKind.TRANSFORM, index, desired)
                progress(
                    "image",
                    12 + round(56 * index / max(1, desired - 1)),
                    f"NPUでA→Bの途中 {index}/{desired - 2} を描いています",
                )
                tensor = image_pipeline.generate(
                    _transition_prompt(translated_prompt, action, index, desired),
                    ov.Tensor(_array(condition)[None]),
                    width=512,
                    height=512,
                    num_inference_steps=inference_steps,
                    strength=transition_strength,
                    guidance_scale=1.0,
                    rng_seed=seed,
                )
                anchors.append(Image.fromarray(tensor.data[0]))
            anchors.append(target)
            notes.append("端点固定: 先頭=A / 最終=B")
        else:
            evolving_actions = {"build", "transform", "flow"}
            while len(anchors) < desired:
                estimated_finish = max(8.0, request.duration_seconds * 1.6)
                if not scheduler.can_start(4.0 + estimated_finish):
                    notes.append(f"安全上限のためAIキーフレームを{len(anchors)}枚で確定")
                    break
                index = len(anchors)
                progress(
                    "image",
                    12 + round(56 * index / max(1, desired - 1)),
                    f"NPUで大きな動き {index + 1}/{desired} を描いています",
                )
                source = anchors[-1] if action.value in evolving_actions else base
                condition = warp_condition(source, action, index, desired)
                prompt = frame_prompt(translated_prompt, action, index, desired)
                tensor = image_pipeline.generate(
                    prompt,
                    ov.Tensor(_array(condition)[None]),
                    width=512,
                    height=512,
                    num_inference_steps=inference_steps,
                    strength=strength,
                    guidance_scale=1.0,
                    rng_seed=seed,
                )
                anchors.append(Image.fromarray(tensor.data[0]))
        image_seconds = time.perf_counter() - image_started

        if is_transition:
            arrays = [
                _cropped_array(
                    (
                        anchor
                        if index in {0, len(anchors) - 1}
                        else warp_condition(anchor, action, index, len(anchors))
                    ),
                    crop_box,
                )
                for index, anchor in enumerate(anchors)
            ]
        else:
            arrays = [
                _cropped_array(
                    anchor if index == 0 else warp_condition(anchor, action, index, len(anchors)),
                    crop_box,
                )
                for index, anchor in enumerate(anchors)
            ]
        interpolation_anchors = arrays
        loop_enabled = request.seamless_loop and not is_transition
        if loop_enabled and len(arrays) >= 2:
            interpolation_anchors = [*arrays, arrays[0]]
            notes.append("シームレスループ: 最後から最初へGPUで補間")
        progress("motion", 72, "Arc GPUで中間の動きを作っています")
        interpolation_backend = "CPU bidirectional DIS"
        flow_seconds = 0.0
        if self.rife.available and len(arrays) >= 2:
            try:
                frames, interpolation_seconds = self.rife.interpolate(
                    interpolation_anchors,
                    duration_seconds=request.duration_seconds,
                    fps=fps,
                )
                interpolation_backend = "Arc GPU RIFE Vulkan"
            except (RuntimeError, OSError, subprocess.SubprocessError) as exc:
                notes.append(f"GPU補間をCPUへ切替: {exc}")
                frames, flow_seconds, interpolation_seconds = interpolate_anchors(
                    interpolation_anchors,
                    duration_seconds=request.duration_seconds,
                    fps=fps,
                )
        else:
            frames, flow_seconds, interpolation_seconds = interpolate_anchors(
                interpolation_anchors,
                duration_seconds=request.duration_seconds,
                fps=fps,
            )
        if loop_enabled and len(frames) > 2:
            frames = frames[:-1]
            frames[-1] = arrays[0].copy()
        elif is_transition and len(frames) >= 2:
            frames[0] = arrays[0].copy()
            frames[-1] = arrays[-1].copy()

        progress("encode", 94, "滑らかなMP4に仕上げています")
        output_directory.mkdir(parents=True, exist_ok=True)
        output_path = output_directory / f"{uuid.uuid4().hex}.mp4"
        encode_seconds, codec = encode_mp4(frames, output_path, fps=fps)
        elapsed = time.monotonic() - started
        notes.extend(
            (
                (
                    f"NPUで{max(0, len(anchors) - 2)}枚の途中を描き、"
                    f"AからBへ{len(frames)}コマでつなぎました"
                    if is_transition
                    else f"NPUで{len(anchors)}枚を描き、Arc GPUで{len(frames)}コマに"
                    f"つなぎました{'（Aへ戻る）' if loop_enabled else ''}"
                ),
                f"AI anchors={len(anchors)} / {fps}fps / {len(frames)} frames",
                f"NPU画像 {image_seconds:.2f}秒",
                f"{interpolation_backend} {flow_seconds + interpolation_seconds:.2f}秒",
                f"MP4 {encode_seconds:.2f}秒 ({codec})",
            )
        )
        progress("delivery", 100, "できました")
        return MotionArtifact(
            path=output_path,
            media_type="video/mp4",
            elapsed_seconds=elapsed,
            degraded=len(anchors) < desired or interpolation_backend.startswith("CPU"),
            notes=tuple(notes),
        )
