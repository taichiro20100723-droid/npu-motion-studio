from __future__ import annotations

import base64
import io
import math

import numpy as np
from PIL import Image, ImageFilter


def decode_brush_mask(
    value: str | None,
    *,
    crop_box: tuple[int, int, int, int],
    output_size: tuple[int, int],
) -> np.ndarray | None:
    """Map a mask painted over the original image onto the 512px model canvas."""
    if not value:
        return None
    try:
        header, encoded = value.split(",", 1)
        if not header.startswith("data:image/") or ";base64" not in header:
            raise ValueError
        raw = base64.b64decode(encoded, validate=True)
        source = Image.open(io.BytesIO(raw)).convert("L")
        source.load()
    except Exception as exc:  # noqa: BLE001 - malformed browser input is normalized here
        raise ValueError("Motion Brushの塗り情報を読み込めませんでした") from exc

    resized = source.resize(output_size, Image.Resampling.BILINEAR)
    canvas = Image.new("L", (512, 512), 0)
    canvas.paste(resized, crop_box[:2])
    feathered = canvas.filter(ImageFilter.GaussianBlur(radius=5))
    return np.asarray(feathered, dtype=np.float32) / np.float32(255.0)


def brush_warp(
    image: Image.Image,
    move_mask: np.ndarray | None,
    *,
    vector_x: float,
    vector_y: float,
    phase: float,
    loop: bool,
) -> Image.Image:
    """Push only the painted subject, with a feathered deformation boundary."""
    if move_mask is None or float(move_mask.max(initial=0.0)) < 0.01:
        return image
    try:
        import cv2
    except ImportError as exc:  # pragma: no cover - production setup includes OpenCV
        raise RuntimeError("Motion BrushにはOpenCVが必要です") from exc

    vector_length = math.hypot(vector_x, vector_y)
    if vector_length < 0.03:
        vector_x, vector_y = 0.75, -0.22
        vector_length = math.hypot(vector_x, vector_y)
    unit_x, unit_y = vector_x / vector_length, vector_y / vector_length
    envelope = math.sin((2.0 if loop else 1.0) * math.pi * phase)
    distance = 112.0 * min(1.0, max(0.25, vector_length)) * envelope

    array = np.asarray(image.convert("RGB"), dtype=np.uint8)
    height, width = array.shape[:2]
    grid_x, grid_y = np.meshgrid(
        np.arange(width, dtype=np.float32), np.arange(height, dtype=np.float32)
    )
    map_x = grid_x - np.float32(unit_x * distance) * move_mask
    map_y = grid_y - np.float32(unit_y * distance) * move_mask
    warped = cv2.remap(
        array,
        map_x,
        map_y,
        interpolation=cv2.INTER_CUBIC,
        borderMode=cv2.BORDER_REFLECT_101,
    )
    return Image.fromarray(np.asarray(warped, dtype=np.uint8), mode="RGB")


def enforce_lock(
    generated: Image.Image,
    fixed_source: Image.Image,
    lock_mask: np.ndarray | None,
) -> Image.Image:
    """Restore blue-painted pixels after AI generation so backgrounds stay still."""
    if lock_mask is None or float(lock_mask.max(initial=0.0)) < 0.01:
        return generated
    alpha = np.clip(lock_mask[..., None], 0.0, 1.0)
    result = (
        np.asarray(fixed_source.convert("RGB"), dtype=np.float32) * alpha
        + np.asarray(generated.convert("RGB"), dtype=np.float32) * (1.0 - alpha)
    )
    return Image.fromarray(np.clip(result, 0, 255).astype(np.uint8), mode="RGB")
