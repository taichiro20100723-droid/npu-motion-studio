import pytest

from npu_motion_studio.scheduler import DeadlineExceeded, DeadlineScheduler


class Clock:
    def __init__(self) -> None:
        self.now = 100.0

    def __call__(self) -> float:
        return self.now


def test_deadline_scheduler_tracks_remaining() -> None:
    clock = Clock()
    scheduler = DeadlineScheduler(10, clock=clock, safety_margin=0.1)
    clock.now += 3
    assert scheduler.elapsed == 3
    assert scheduler.remaining == 7
    assert scheduler.usable_remaining == 6
    assert scheduler.can_start(5.9)


def test_deadline_scheduler_rejects_expensive_stage() -> None:
    clock = Clock()
    scheduler = DeadlineScheduler(10, clock=clock, safety_margin=0.2)
    clock.now += 7.5
    with pytest.raises(DeadlineExceeded, match="motion"):
        scheduler.require("motion", 1.0)
