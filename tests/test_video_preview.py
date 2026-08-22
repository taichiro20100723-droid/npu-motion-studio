import numpy as np

from npu_motion_studio.engines.video_pipeline import interpolate_preview


def test_preview_interpolation_preserves_endpoints_and_count() -> None:
    first = np.zeros((8, 10, 3), dtype=np.uint8)
    second = np.full((8, 10, 3), 255, dtype=np.uint8)
    frames, elapsed = interpolate_preview([first, second], duration_seconds=2, fps=8)
    assert len(frames) == 16
    assert np.array_equal(frames[0], first)
    assert np.array_equal(frames[-1], second)
    assert 0 < frames[len(frames) // 2].mean() < 255
    assert elapsed >= 0
