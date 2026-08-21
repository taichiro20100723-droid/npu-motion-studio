from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
from numpy.typing import NDArray

RgbFrame = NDArray[np.uint8]


@dataclass(frozen=True, slots=True)
class VideoTimings:
    flow_seconds: float
    interpolation_seconds: float
    encode_seconds: float
    codec: str


def _require_cv2():
    try:
        import cv2
    except ImportError as exc:  # pragma: no cover - optional dependency boundary
        raise RuntimeError("OpenCVが未導入です。setup_windows.ps1を実行してください") from exc
    return cv2


def _compute_flow(source: RgbFrame, target: RgbFrame) -> NDArray[np.float32]:
    cv2 = _require_cv2()
    source_gray = cv2.cvtColor(source, cv2.COLOR_RGB2GRAY)
    target_gray = cv2.cvtColor(target, cv2.COLOR_RGB2GRAY)
    dis = cv2.DISOpticalFlow_create(cv2.DISOPTICAL_FLOW_PRESET_MEDIUM)
    dis.setUseSpatialPropagation(True)
    return np.asarray(dis.calc(source_gray, target_gray, None), dtype=np.float32)


def _remap(
    array: NDArray[np.generic], map_x: NDArray[np.float32], map_y: NDArray[np.float32]
) -> NDArray[np.float32]:
    cv2 = _require_cv2()
    return np.asarray(
        cv2.remap(
            array,
            map_x,
            map_y,
            interpolation=cv2.INTER_LINEAR,
            borderMode=cv2.BORDER_REFLECT_101,
        ),
        dtype=np.float32,
    )


def _cycle_confidence(
    flow_ab: NDArray[np.float32], flow_ba: NDArray[np.float32]
) -> tuple[NDArray[np.float32], NDArray[np.float32]]:
    height, width = flow_ab.shape[:2]
    grid_x, grid_y = np.meshgrid(
        np.arange(width, dtype=np.float32), np.arange(height, dtype=np.float32)
    )
    ba_at_b = _remap(flow_ba, grid_x + flow_ab[..., 0], grid_y + flow_ab[..., 1])
    ab_at_a = _remap(flow_ab, grid_x + flow_ba[..., 0], grid_y + flow_ba[..., 1])
    error_a = np.linalg.norm(flow_ab + ba_at_b, axis=2)
    error_b = np.linalg.norm(flow_ba + ab_at_a, axis=2)
    return (
        np.exp(-np.square(error_a / 4.0)).astype(np.float32),
        np.exp(-np.square(error_b / 4.0)).astype(np.float32),
    )


def _interpolate_pair(
    first: RgbFrame,
    second: RgbFrame,
    flow_ab: NDArray[np.float32],
    flow_ba: NDArray[np.float32],
    count: int,
) -> list[RgbFrame]:
    height, width = first.shape[:2]
    grid_x, grid_y = np.meshgrid(
        np.arange(width, dtype=np.float32), np.arange(height, dtype=np.float32)
    )
    confidence_a, confidence_b = _cycle_confidence(flow_ab, flow_ba)
    frames: list[RgbFrame] = []
    for index in range(count):
        t = index / count
        warp_a = _remap(
            first,
            grid_x - np.float32(t) * flow_ab[..., 0],
            grid_y - np.float32(t) * flow_ab[..., 1],
        )
        warp_b = _remap(
            second,
            grid_x - np.float32(1.0 - t) * flow_ba[..., 0],
            grid_y - np.float32(1.0 - t) * flow_ba[..., 1],
        )
        weight_a = np.float32(1.0 - t) * _remap(
            confidence_a,
            grid_x - np.float32(t) * flow_ab[..., 0],
            grid_y - np.float32(t) * flow_ab[..., 1],
        )
        weight_b = np.float32(t) * _remap(
            confidence_b,
            grid_x - np.float32(1.0 - t) * flow_ba[..., 0],
            grid_y - np.float32(1.0 - t) * flow_ba[..., 1],
        )
        weight_sum = weight_a + weight_b
        confidence_blend = (
            warp_a * weight_a[..., None] + warp_b * weight_b[..., None]
        ) / np.maximum(weight_sum, 1e-5)[..., None]
        fallback_blend = warp_a * np.float32(1.0 - t) + warp_b * np.float32(t)
        blended = np.where(
            (weight_sum > 0.08)[..., None], confidence_blend, fallback_blend
        )
        frames.append(np.clip(blended, 0, 255).astype(np.uint8))
    return frames


def interpolate_anchors(
    anchors: list[RgbFrame], *, duration_seconds: float, fps: int
) -> tuple[list[RgbFrame], float, float]:
    import time

    if not anchors:
        raise ValueError("at least one anchor is required")
    total_frames = max(2, round(duration_seconds * fps))
    if len(anchors) == 1:
        return [anchors[0].copy() for _ in range(total_frames)], 0.0, 0.0

    flow_started = time.perf_counter()
    flows = [
        (_compute_flow(first, second), _compute_flow(second, first))
        for first, second in zip(anchors[:-1], anchors[1:], strict=True)
    ]
    flow_seconds = time.perf_counter() - flow_started

    interpolation_started = time.perf_counter()
    pair_count = len(anchors) - 1
    base_count, remainder = divmod(total_frames, pair_count)
    frames: list[RgbFrame] = []
    for pair_index, ((first, second), (flow_ab, flow_ba)) in enumerate(
        zip(zip(anchors[:-1], anchors[1:], strict=True), flows, strict=True)
    ):
        count = base_count + (1 if pair_index < remainder else 0)
        frames.extend(_interpolate_pair(first, second, flow_ab, flow_ba, count))
    frames[-1] = anchors[-1].copy()
    return frames, flow_seconds, time.perf_counter() - interpolation_started


def encode_mp4(frames: list[RgbFrame], output: Path, *, fps: int) -> tuple[float, str]:
    import time

    if not frames:
        raise ValueError("at least one frame is required")
    try:
        import imageio_ffmpeg
    except ImportError as exc:  # pragma: no cover - optional dependency boundary
        raise RuntimeError("動画出力機能が未導入です。setup_windows.ps1を実行してください") from exc

    output.parent.mkdir(parents=True, exist_ok=True)
    height, width = frames[0].shape[:2]
    def write(codec: str, output_params: list[str], output_pixel_format: str) -> None:
        writer = imageio_ffmpeg.write_frames(
            str(output),
            (width, height),
            fps=fps,
            codec=codec,
            pix_fmt_in="rgb24",
            pix_fmt_out=output_pixel_format,
            output_params=output_params,
        )
        writer.send(None)
        try:
            for frame in frames:
                writer.send(np.ascontiguousarray(frame).tobytes())
        finally:
            writer.close()

    started = time.perf_counter()
    try:
        write(
            "h264_qsv",
            ["-preset", "veryfast", "-global_quality", "20", "-movflags", "+faststart"],
            "nv12",
        )
        codec = "Intel Quick Sync H.264"
    except (BrokenPipeError, OSError, RuntimeError):
        output.unlink(missing_ok=True)
        write(
            "libx264",
            ["-preset", "ultrafast", "-crf", "19", "-movflags", "+faststart"],
            "yuv420p",
        )
        codec = "libx264-ultrafast fallback"
    return time.perf_counter() - started, codec
