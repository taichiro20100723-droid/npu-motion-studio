import base64
import io

import numpy as np
from PIL import Image

from npu_motion_studio.motion_brush import brush_warp, decode_brush_mask, enforce_lock


def _mask_data_url() -> str:
    mask = Image.new("L", (20, 10), 0)
    mask.paste(255, (0, 0, 10, 10))
    buffer = io.BytesIO()
    mask.save(buffer, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buffer.getvalue()).decode()


def test_decode_brush_mask_preserves_image_area_on_canvas() -> None:
    mask = decode_brush_mask(
        _mask_data_url(), crop_box=(0, 128, 512, 384), output_size=(512, 256)
    )
    assert mask is not None
    assert mask.shape == (512, 512)
    assert mask[256, 80] > 0.9
    assert mask[256, 430] < 0.1
    assert mask[20, 80] < 0.1


def test_lock_restores_only_painted_pixels() -> None:
    generated = Image.new("RGB", (8, 8), "red")
    fixed = Image.new("RGB", (8, 8), "blue")
    lock = np.zeros((8, 8), dtype=np.float32)
    lock[:, :4] = 1.0
    result = np.asarray(enforce_lock(generated, fixed, lock))
    assert np.all(result[:, :4] == [0, 0, 255])
    assert np.all(result[:, 4:] == [255, 0, 0])


def test_red_motion_mask_moves_pixels_and_empty_mask_is_noop() -> None:
    source = np.zeros((32, 32, 3), dtype=np.uint8)
    source[10:20, 5:15] = 255
    image = Image.fromarray(source)
    mask = np.zeros((32, 32), dtype=np.float32)
    mask[7:23, 2:18] = 1.0
    moved = np.asarray(
        brush_warp(image, mask, vector_x=1.0, vector_y=0.0, phase=0.5, loop=False)
    )
    unchanged = np.asarray(
        brush_warp(image, None, vector_x=1.0, vector_y=0.0, phase=0.5, loop=False)
    )
    assert not np.array_equal(moved, source)
    assert np.array_equal(unchanged, source)
