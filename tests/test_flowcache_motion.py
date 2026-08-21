import pytest

from npu_motion_studio.flowcache.motion import MotionKind, route_motion


@pytest.mark.parametrize(
    ("prompt", "expected"),
    [
        ("人物のポートレートが微笑む", MotionKind.PERSON),
        ("猫が草原を走る", MotionKind.ANIMAL),
        ("宇宙船とメカが高速で飛ぶ", MotionKind.VEHICLE),
        ("煙と炎が渦を巻く", MotionKind.FLUID),
        ("森と山の広い風景", MotionKind.LANDSCAPE),
        ("ロボットが変形して爆発する", MotionKind.TRANSFORM),
        ("猫が呼吸する完璧なループ", MotionKind.LOOP),
    ],
)
def test_motion_router_covers_supported_kinds(prompt: str, expected: MotionKind) -> None:
    route = route_motion(prompt)
    assert route.kind is expected
    assert route.matched_terms
    assert 0.0 < route.confidence <= 1.0


def test_motion_router_has_safe_landscape_fallback() -> None:
    route = route_motion("抽象的で静かな何か")
    assert route.kind is MotionKind.LANDSCAPE
    assert route.profile.preferred_transition == "parallax"
    assert route.confidence == 0.2


def test_motion_router_can_be_forced_by_ui() -> None:
    route = route_motion("車", force="loop")
    assert route.kind is MotionKind.LOOP
    assert route.confidence == 1.0
    assert route.profile.loop_safe
