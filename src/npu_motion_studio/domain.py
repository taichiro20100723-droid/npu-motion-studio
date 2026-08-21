from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

MotionMode = Literal["fast", "fun", "wow"]
CreationMode = Literal["animate", "transition"]


@dataclass(frozen=True, slots=True)
class MotionRequest:
    prompt: str
    creation_mode: CreationMode = "animate"
    mode: MotionMode = "fun"
    duration_seconds: float = 4.0
    seamless_loop: bool = True
    input_image_data_url: str | None = None
    target_image_data_url: str | None = None


@dataclass(frozen=True, slots=True)
class MotionArtifact:
    path: Path
    media_type: str
    elapsed_seconds: float
    degraded: bool = False
    notes: tuple[str, ...] = field(default_factory=tuple)
