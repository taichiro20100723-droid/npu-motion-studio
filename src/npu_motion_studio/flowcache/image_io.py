from __future__ import annotations

import numpy as np
from numpy.typing import NDArray
from PIL import Image


def pil_to_array(image: Image.Image) -> NDArray[np.uint8]:
    """Convert Pillow input to a contiguous RGB uint8 array."""

    return np.ascontiguousarray(np.asarray(image.convert("RGB"), dtype=np.uint8))


def array_to_pil(image: NDArray[np.generic]) -> Image.Image:
    """Convert an RGB/greyscale NumPy image, clipping floating point values."""

    array = np.asarray(image)
    if array.ndim not in (2, 3) or (array.ndim == 3 and array.shape[2] not in (1, 3, 4)):
        raise ValueError("image must be grayscale, RGB, or RGBA")
    if np.issubdtype(array.dtype, np.floating):
        array = np.rint(np.clip(array, 0.0, 255.0))
    return Image.fromarray(np.asarray(array, dtype=np.uint8))
