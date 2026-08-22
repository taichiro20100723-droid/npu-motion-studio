import base64
import io

import numpy as np
from PIL import Image

from npu_motion_studio.engines.openvino_lcm import (
    SAFE_NEGATIVE_PROMPT,
    _cropped_array,
    _decode_data_url,
    _prepare_transition_target,
    _transition_prompt,
    _transition_strength,
)
from npu_motion_studio.prompting import ActionKind


def _data_url(image: Image.Image) -> str:
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    encoded = base64.b64encode(buffer.getvalue()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


def test_a_defines_output_aspect_and_b_is_not_stretched() -> None:
    start = _decode_data_url(_data_url(Image.new("RGB", (800, 400), "blue")))
    assert start.output_size == (512, 256)

    target_source = Image.new("RGB", (200, 400), "red")
    target = _prepare_transition_target(_data_url(target_source), start)
    target_crop = _cropped_array(target, start.crop_box)

    assert target_crop.shape == (256, 512, 3)
    # Portrait B remains a centered portrait instead of being stretched across A's wide frame.
    middle = target_crop[:, 192:320]
    assert np.mean(middle[..., 0]) > 245


def test_same_aspect_b_is_exact_at_the_last_frame() -> None:
    start = _decode_data_url(_data_url(Image.new("RGB", (640, 360), "blue")))
    target = _prepare_transition_target(
        _data_url(Image.new("RGB", (640, 360), (231, 19, 42))),
        start,
    )
    target_crop = _cropped_array(target, start.crop_box)
    assert np.max(np.abs(target_crop.astype(int) - np.array([231, 19, 42]))) == 0


def test_transition_prompt_keeps_the_requested_timed_action() -> None:
    prompt = _transition_prompt("a robot runs fast", ActionKind.RUN, 2, 8)
    assert "full-body running" in prompt
    assert "transition progress 29 percent" in prompt
    assert "both forms readable in one body" in prompt
    assert "opaque clothing" in prompt
    assert "bare breasts" in SAFE_NEGATIVE_PROMPT


def test_transform_prompt_describes_a_real_hybrid_instead_of_preserving_identity() -> None:
    prompt = _transition_prompt(
        "a steel robot transforms into a real Shiba Inu",
        ActionKind.TRANSFORM,
        5,
        12,
    )
    assert "Shiba Inu" in prompt
    assert "halfway hybrid" in prompt
    assert "identity remains recognizable" not in prompt


def test_transition_strength_protects_endpoints_and_frees_the_middle() -> None:
    early = _transition_strength("wow", 1 / 11)
    middle = _transition_strength("wow", 5 / 11)
    late = _transition_strength("wow", 10 / 11)
    assert early < middle
    assert late < middle
    assert abs(early - late) < 1e-9
