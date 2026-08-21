import numpy as np
from PIL import Image

from npu_motion_studio.flowcache.image_io import array_to_pil, pil_to_array


def test_pillow_boundary_normalizes_rgb_and_float_ranges() -> None:
    grayscale = Image.new("L", (2, 2), color=128)
    array = pil_to_array(grayscale)
    assert array.shape == (2, 2, 3)
    assert array.dtype == np.uint8

    result = array_to_pil(np.array([[-4.0, 128.4, 999.0]], dtype=np.float32))
    assert np.asarray(result).tolist() == [[0, 128, 255]]
