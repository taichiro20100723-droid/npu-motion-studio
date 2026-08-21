from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from npu_motion_studio.domain import MotionArtifact, MotionRequest
from npu_motion_studio.scheduler import DeadlineScheduler

ProgressCallback = Callable[[str, int, str], None]


@dataclass(frozen=True, slots=True)
class EngineProbe:
    name: str
    available: bool
    detail: str
    uses_npu: bool


class MotionEngine(ABC):
    key: str

    @property
    def ready(self) -> bool:
        return True

    def prepare(self) -> None:
        """Load expensive resources before the user can submit the first job."""
        return None

    @abstractmethod
    def probe(self) -> EngineProbe:
        raise NotImplementedError

    @abstractmethod
    def generate(
        self,
        request: MotionRequest,
        output_directory: Path,
        scheduler: DeadlineScheduler,
        progress: ProgressCallback,
    ) -> MotionArtifact:
        raise NotImplementedError
