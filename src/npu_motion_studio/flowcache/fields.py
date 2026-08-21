from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Literal

import numpy as np
from numpy.typing import NDArray

FloatArray = NDArray[np.float32]
BoolArray = NDArray[np.bool_]
BorderMode = Literal["constant", "edge"]


@dataclass(frozen=True, slots=True)
class DenseMotionField:
    """A dense `(dx, dy)` correspondence field in pixel units.

    For correspondence operations, ``p + field[p]`` is the matching coordinate in
    the other image. For :func:`bilinear_warp`, the same vectors are interpreted as
    backward sampling offsets: output pixel ``p`` reads input coordinate ``p + field[p]``.
    Keeping the convention explicit avoids an OpenCV-specific flow representation.
    """

    vectors: FloatArray

    def __post_init__(self) -> None:
        vectors = np.asarray(self.vectors, dtype=np.float32)
        if vectors.ndim != 3 or vectors.shape[-1] != 2:
            raise ValueError("motion field must have shape (height, width, 2)")
        if vectors.shape[0] < 1 or vectors.shape[1] < 1:
            raise ValueError("motion field dimensions must be positive")
        if not np.isfinite(vectors).all():
            raise ValueError("motion field must contain only finite values")
        vectors = np.ascontiguousarray(vectors.copy())
        vectors.setflags(write=False)
        object.__setattr__(self, "vectors", vectors)

    @classmethod
    def zeros(cls, height: int, width: int) -> DenseMotionField:
        if height < 1 or width < 1:
            raise ValueError("height and width must be positive")
        return cls(np.zeros((height, width, 2), dtype=np.float32))

    @classmethod
    def from_components(
        cls,
        dx: NDArray[np.floating] | Sequence[Sequence[float]],
        dy: NDArray[np.floating] | Sequence[Sequence[float]],
    ) -> DenseMotionField:
        dx_array = np.asarray(dx, dtype=np.float32)
        dy_array = np.asarray(dy, dtype=np.float32)
        if dx_array.shape != dy_array.shape or dx_array.ndim != 2:
            raise ValueError("dx and dy must be two-dimensional arrays with equal shapes")
        return cls(np.stack((dx_array, dy_array), axis=-1))

    @property
    def height(self) -> int:
        return int(self.vectors.shape[0])

    @property
    def width(self) -> int:
        return int(self.vectors.shape[1])

    @property
    def dx(self) -> FloatArray:
        return self.vectors[..., 0]

    @property
    def dy(self) -> FloatArray:
        return self.vectors[..., 1]

    def scaled(self, factor: float) -> DenseMotionField:
        if not math.isfinite(factor):
            raise ValueError("factor must be finite")
        return DenseMotionField(self.vectors * np.float32(factor))


def _grid(height: int, width: int) -> tuple[FloatArray, FloatArray]:
    y, x = np.mgrid[:height, :width]
    return x.astype(np.float32), y.astype(np.float32)


def _bilinear_sample(
    values: NDArray[np.generic],
    x: FloatArray,
    y: FloatArray,
    *,
    border_mode: BorderMode,
    border_value: float,
) -> FloatArray:
    source = np.asarray(values, dtype=np.float32)
    if source.ndim not in (2, 3):
        raise ValueError("values must have shape (height, width) or (height, width, channels)")
    if x.shape != y.shape:
        raise ValueError("x and y sampling grids must have equal shapes")

    height, width = source.shape[:2]
    if border_mode == "edge":
        x = np.clip(x, 0.0, float(width - 1))
        y = np.clip(y, 0.0, float(height - 1))
    elif border_mode != "constant":
        raise ValueError(f"unsupported border mode: {border_mode}")

    x0 = np.floor(x).astype(np.int64)
    y0 = np.floor(y).astype(np.int64)
    x1 = x0 + 1
    y1 = y0 + 1
    wx = x - x0
    wy = y - y0
    neighbors = (
        (x0, y0, (1.0 - wx) * (1.0 - wy)),
        (x1, y0, wx * (1.0 - wy)),
        (x0, y1, (1.0 - wx) * wy),
        (x1, y1, wx * wy),
    )

    output_shape = x.shape + source.shape[2:]
    result = np.zeros(output_shape, dtype=np.float32)
    valid_weight = np.zeros(x.shape, dtype=np.float32)
    for sample_x, sample_y, weight in neighbors:
        valid = (
            (sample_x >= 0)
            & (sample_x < width)
            & (sample_y >= 0)
            & (sample_y < height)
        )
        safe_x = np.clip(sample_x, 0, width - 1)
        safe_y = np.clip(sample_y, 0, height - 1)
        expanded_weight = weight[..., None] if source.ndim == 3 else weight
        expanded_valid = valid[..., None] if source.ndim == 3 else valid
        result += source[safe_y, safe_x] * expanded_weight * expanded_valid
        valid_weight += weight * valid

    if border_mode == "constant":
        missing_weight = np.maximum(0.0, 1.0 - valid_weight)
        if source.ndim == 3:
            missing_weight = missing_weight[..., None]
        result += np.float32(border_value) * missing_weight
    return result


def bilinear_warp(
    image: NDArray[np.generic],
    sampling_field: DenseMotionField,
    *,
    border_mode: BorderMode = "edge",
    border_value: float = 0.0,
) -> FloatArray:
    """Warp an image without OpenCV using backward bilinear sampling.

    ``output[y, x] = image[y + dy, x + dx]``. The output is always ``float32`` so
    callers can blend it safely before converting back to an 8-bit image.
    """

    x, y = _grid(sampling_field.height, sampling_field.width)
    return _bilinear_sample(
        image,
        x + sampling_field.dx,
        y + sampling_field.dy,
        border_mode=border_mode,
        border_value=border_value,
    )


def forward_backward_cycle_consistency_mask(
    forward: DenseMotionField,
    backward: DenseMotionField,
    *,
    absolute_tolerance: float = 0.75,
    relative_tolerance: float = 0.05,
) -> BoolArray:
    """Return ``True`` where an A→B→A correspondence closes reliably."""

    if forward.vectors.shape != backward.vectors.shape:
        raise ValueError("forward and backward fields must have equal shapes")
    if absolute_tolerance < 0 or relative_tolerance < 0:
        raise ValueError("cycle tolerances must be non-negative")

    x, y = _grid(forward.height, forward.width)
    target_x = x + forward.dx
    target_y = y + forward.dy
    inside = (
        (target_x >= 0.0)
        & (target_x <= backward.width - 1)
        & (target_y >= 0.0)
        & (target_y <= backward.height - 1)
    )
    sampled_backward = _bilinear_sample(
        backward.vectors,
        target_x,
        target_y,
        border_mode="constant",
        border_value=0.0,
    )
    cycle_error = np.linalg.norm(forward.vectors + sampled_backward, axis=-1)
    motion_scale = np.linalg.norm(forward.vectors, axis=-1) + np.linalg.norm(
        sampled_backward, axis=-1
    )
    threshold = absolute_tolerance + relative_tolerance * motion_scale
    return np.asarray(inside & (cycle_error <= threshold), dtype=np.bool_)


def disocclusion_mask(
    forward: DenseMotionField,
    *,
    occupancy_threshold: float = 0.25,
) -> BoolArray:
    """Find target pixels not covered after bilinear forward splatting.

    The returned target-space mask is ``True`` for holes that an inpaint backend or
    a cheap edge-fill repair should handle.
    """

    if not 0.0 <= occupancy_threshold <= 1.0:
        raise ValueError("occupancy_threshold must be between 0 and 1")
    x, y = _grid(forward.height, forward.width)
    target_x = x + forward.dx
    target_y = y + forward.dy
    x0 = np.floor(target_x).astype(np.int64)
    y0 = np.floor(target_y).astype(np.int64)
    x1 = x0 + 1
    y1 = y0 + 1
    wx = target_x - x0
    wy = target_y - y0
    occupancy = np.zeros((forward.height, forward.width), dtype=np.float32)

    for sample_x, sample_y, weight in (
        (x0, y0, (1.0 - wx) * (1.0 - wy)),
        (x1, y0, wx * (1.0 - wy)),
        (x0, y1, (1.0 - wx) * wy),
        (x1, y1, wx * wy),
    ):
        valid = (
            (sample_x >= 0)
            & (sample_x < forward.width)
            & (sample_y >= 0)
            & (sample_y < forward.height)
        )
        np.add.at(occupancy, (sample_y[valid], sample_x[valid]), weight[valid])
    return np.asarray(occupancy < occupancy_threshold, dtype=np.bool_)


def correlated_noise_fields(
    count: int,
    shape: tuple[int, ...],
    *,
    correlation: float = 0.8,
    seed: int | None = None,
    motion_fields: Sequence[DenseMotionField] | None = None,
) -> FloatArray:
    """Create temporally correlated latent noise, optionally motion-warped.

    With no motion fields the expected pairwise correlation is ``correlation``.
    Supplying fields spatially transports the shared component before independent
    noise is mixed in. This is the FlowCache seam used by a future OpenVINO img2img
    backend; no diffusion runtime is required here.
    """

    if count < 1:
        raise ValueError("count must be positive")
    if len(shape) not in (2, 3) or any(dimension < 1 for dimension in shape):
        raise ValueError("shape must be (height, width) or (height, width, channels)")
    if not 0.0 <= correlation <= 1.0:
        raise ValueError("correlation must be between 0 and 1")
    if motion_fields is not None:
        if len(motion_fields) != count:
            raise ValueError("motion_fields must contain one field per noise sample")
        if any(field.vectors.shape[:2] != shape[:2] for field in motion_fields):
            raise ValueError("motion field sizes must match the noise spatial shape")

    rng = np.random.default_rng(seed)
    shared = rng.standard_normal(shape, dtype=np.float32)
    shared_weight = np.float32(math.sqrt(correlation))
    private_weight = np.float32(math.sqrt(1.0 - correlation))
    result = np.empty((count, *shape), dtype=np.float32)
    for index in range(count):
        shared_component = shared
        if motion_fields is not None:
            shared_component = bilinear_warp(shared, motion_fields[index], border_mode="edge")
        private = rng.standard_normal(shape, dtype=np.float32)
        result[index] = shared_weight * shared_component + private_weight * private
    return result
