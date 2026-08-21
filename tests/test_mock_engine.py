from pathlib import Path

from npu_motion_studio.domain import MotionRequest
from npu_motion_studio.engines.mock import MockMotionEngine
from npu_motion_studio.scheduler import DeadlineScheduler


def test_mock_engine_creates_safe_svg(tmp_path: Path) -> None:
    progress: list[tuple[str, int, str]] = []
    artifact = MockMotionEngine(sleep=False).generate(
        MotionRequest(prompt='<script>alert("x")</script>', mode="fun"),
        tmp_path,
        DeadlineScheduler(10),
        lambda *args: progress.append(args),
    )

    content = artifact.path.read_text(encoding="utf-8")
    assert artifact.media_type == "image/svg+xml"
    assert "<script>" not in content
    assert "&lt;script&gt;" in content
    assert progress[-1][0] == "delivery"
