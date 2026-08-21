from __future__ import annotations

import time
from collections.abc import Callable
from dataclasses import dataclass


class DeadlineExceeded(RuntimeError):
    """Raised when starting another stage would pass the deadline."""


@dataclass(frozen=True, slots=True)
class StageBudget:
    name: str
    seconds: float


DEFAULT_STAGES = (
    StageBudget("image", 4.5),
    StageBudget("analysis", 0.7),
    StageBudget("motion", 2.2),
    StageBudget("encode", 0.6),
    StageBudget("delivery", 0.5),
)


class DeadlineScheduler:
    def __init__(
        self,
        deadline_seconds: float,
        *,
        clock: Callable[[], float] = time.monotonic,
        safety_margin: float = 0.15,
    ) -> None:
        if deadline_seconds <= 0:
            raise ValueError("deadline_seconds must be positive")
        if not 0 <= safety_margin < 1:
            raise ValueError("safety_margin must be between 0 and 1")
        self.deadline_seconds = deadline_seconds
        self._clock = clock
        self.started_at = clock()
        self.ends_at = self.started_at + deadline_seconds
        self.safety_seconds = deadline_seconds * safety_margin

    @property
    def elapsed(self) -> float:
        return max(0.0, self._clock() - self.started_at)

    @property
    def remaining(self) -> float:
        return max(0.0, self.ends_at - self._clock())

    @property
    def usable_remaining(self) -> float:
        return max(0.0, self.remaining - self.safety_seconds)

    def can_start(self, estimated_seconds: float) -> bool:
        return estimated_seconds <= self.usable_remaining

    def require(self, stage: str, estimated_seconds: float) -> None:
        if not self.can_start(estimated_seconds):
            raise DeadlineExceeded(
                f"stage '{stage}' needs {estimated_seconds:.2f}s, "
                f"but only {self.usable_remaining:.2f}s remain"
            )

    def progress_percent(self) -> int:
        if self.deadline_seconds == 0:
            return 100
        return min(100, round((self.elapsed / self.deadline_seconds) * 100))
