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
    anchor_count: int | None = None
    is_preview: bool = False
    upgrade_anchor_count: int = 12
    motion_mask_data_url: str | None = None
    lock_mask_data_url: str | None = None
    motion_vector_x: float = 0.0
    motion_vector_y: float = 0.0


@dataclass(frozen=True, slots=True)
class MotionArtifact:
    path: Path
    media_type: str
    elapsed_seconds: float
    degraded: bool = False
    notes: tuple[str, ...] = field(default_factory=tuple)
