"""Small, local preflight check for accidental exposed-chest inputs."""

from __future__ import annotations

import numpy as np


def _skin_mask(image: np.ndarray) -> np.ndarray:
    red = image[..., 0].astype(np.int16)
    green = image[..., 1].astype(np.int16)
    blue = image[..., 2].astype(np.int16)
    return (
        (red > 95)
        & (green > 35)
        & (blue > 20)
        & ((red - green) > 12)
        & ((red - blue) > 18)
        & (green >= blue)
    )


def has_exposed_torso(frame: np.ndarray) -> bool:
    """Return true when a central torso region contains unusually much skin."""
    source = np.ascontiguousarray(frame[..., :3], dtype=np.uint8)
    height, width = source.shape[:2]
    y0, y1 = round(height * 0.34), round(height * 0.96)
    x0, x1 = round(width * 0.16), round(width * 0.84)
    region = source[y0:y1, x0:x1]
    mask = _skin_mask(region)
    return not (mask.size == 0 or float(mask.mean()) < 0.075)
