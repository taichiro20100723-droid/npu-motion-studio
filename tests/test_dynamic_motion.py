import numpy as np
from PIL import Image

from npu_motion_studio.dynamic_motion import frame_prompt, strength_for, warp_condition
from npu_motion_studio.prompting import ActionKind


def test_dance_timeline_has_distinct_large_pose_instructions() -> None:
    prompts = [frame_prompt("same dancer", ActionKind.DANCE, index, 8) for index in range(8)]
    assert len(set(prompts)) == 8
    assert any("jump" in prompt for prompt in prompts)
    assert all("consistent face" in prompt for prompt in prompts)


def test_build_timeline_progresses_from_site_to_completed() -> None:
    first = frame_prompt("city block", ActionKind.BUILD, 0, 8)
    last = frame_prompt("city block", ActionKind.BUILD, 7, 8)
    assert "empty prepared construction site" in first
    assert "fully completed building" in last


def test_dynamic_mode_is_stronger_and_warp_changes_pixels() -> None:
    assert strength_for(ActionKind.DANCE, "fun", has_input_image=True) > strength_for(
        ActionKind.DANCE, "fast", has_input_image=True
    )
    array = np.zeros((64, 64, 3), dtype=np.uint8)
    array[20:44, 24:40] = 255
    image = Image.fromarray(array)
    warped = np.asarray(warp_condition(image, ActionKind.DANCE, 2, 8))
    assert not np.array_equal(array, warped)
