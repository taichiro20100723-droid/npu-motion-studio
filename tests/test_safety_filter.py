import numpy as np

from npu_motion_studio.safety_filter import has_exposed_torso


def test_plain_or_non_skin_frame_is_allowed() -> None:
    frame = np.zeros((128, 128, 3), dtype=np.uint8)
    assert not has_exposed_torso(frame)


def test_exposed_central_torso_is_rejected() -> None:
    frame = np.zeros((128, 128, 3), dtype=np.uint8)
    frame[48:120, 32:96] = (190, 125, 90)
    assert has_exposed_torso(frame)
