from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Protocol, runtime_checkable

import numpy as np
from numpy.typing import NDArray

from npu_motion_studio.flowcache.fields import BoolArray, FloatArray

ImageArray = NDArray[np.uint8] | FloatArray


@dataclass(frozen=True, slots=True)
class AnchorGenerationRequest:
    prompt: str
    negative_prompt: str = ""
    count: int = 2
    width: int = 512
    height: int = 512
    steps: int = 4
    seed: int = 0
    correlated_noise: FloatArray | None = field(default=None, repr=False, compare=False)
    initial_image: ImageArray | None = field(default=None, repr=False, compare=False)


@dataclass(frozen=True, slots=True)
class AnchorFrame:
    image: ImageArray = field(repr=False, compare=False)
    seed: int = 0
    metadata: dict[str, str | int | float] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class InpaintRequest:
    image: ImageArray = field(repr=False, compare=False)
    mask: BoolArray = field(repr=False, compare=False)
    prompt: str = ""
    max_seconds: float = 0.5


@dataclass(frozen=True, slots=True)
class InterpolationRequest:
    first: ImageArray = field(repr=False, compare=False)
    second: ImageArray = field(repr=False, compare=False)
    intermediate_count: int = 1
    max_seconds: float = 0.9


@runtime_checkable
class AnchorImageBackend(Protocol):
    """OpenVINO txt2img/img2img boundary; implementations own model compilation."""

    @property
    def backend_name(self) -> str: ...

    def generate_anchors(self, request: AnchorGenerationRequest) -> Sequence[AnchorFrame]: ...


@runtime_checkable
class InpaintRepairBackend(Protocol):
    """Optional OpenVINO inpaint boundary for disocclusion repair."""

    @property
    def backend_name(self) -> str: ...

    def inpaint(self, request: InpaintRequest) -> ImageArray: ...


@runtime_checkable
class FrameInterpolationBackend(Protocol):
    """Optional RIFE-compatible boundary; CPU bilinear motion remains the fallback."""

    @property
    def backend_name(self) -> str: ...

    def interpolate(self, request: InterpolationRequest) -> Sequence[ImageArray]: ...


@dataclass(frozen=True, slots=True)
class FlowCacheBackends:
    anchors: AnchorImageBackend
    inpaint: InpaintRepairBackend | None = None
    interpolation: FrameInterpolationBackend | None = None
