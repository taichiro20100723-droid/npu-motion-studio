from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from npu_motion_studio.domain import MotionMode

RepairPass = Literal[
    "cycle-consistency",
    "disocclusion-mask",
    "external-inpaint",
    "external-interpolation",
]


@dataclass(frozen=True, slots=True)
class FlowCacheCosts:
    """Warm-start target costs; replace with measured values during calibration."""

    prompt_seconds: float = 0.12
    first_anchor_seconds: float = 1.2
    additional_anchor_seconds: float = 0.85
    base_motion_seconds: float = 0.35
    encode_seconds: float = 0.35
    delivery_seconds: float = 0.2
    cycle_seconds_per_pair: float = 0.05
    disocclusion_seconds_per_pair: float = 0.07
    inpaint_seconds_per_pair: float = 0.55
    interpolation_seconds: float = 0.9
    safety_seconds: float = 0.5


@dataclass(frozen=True, slots=True)
class PairRepairPlan:
    pair_index: int
    passes: tuple[RepairPass, ...]


@dataclass(frozen=True, slots=True)
class FlowCachePlan:
    deadline_seconds: float
    available_seconds: float
    anchor_count: int
    anchor_times: tuple[float, ...]
    pair_repairs: tuple[PairRepairPlan, ...]
    estimated_seconds: float
    deadline_feasible: bool
    degraded: bool
    fallback_transition: str
    notes: tuple[str, ...]


def _base_cost(anchor_count: int, costs: FlowCacheCosts) -> float:
    return (
        costs.prompt_seconds
        + costs.first_anchor_seconds
        + max(0, anchor_count - 1) * costs.additional_anchor_seconds
        + costs.base_motion_seconds
        + costs.encode_seconds
        + costs.delivery_seconds
    )


def _anchor_times(anchor_count: int, duration_seconds: float) -> tuple[float, ...]:
    if anchor_count == 1:
        return (0.0,)
    step = duration_seconds / (anchor_count - 1)
    return tuple(round(index * step, 4) for index in range(anchor_count))


def plan_flowcache(
    deadline_seconds: float,
    *,
    elapsed_seconds: float = 0.0,
    duration_seconds: float = 4.0,
    mode: MotionMode = "fun",
    costs: FlowCacheCosts | None = None,
) -> FlowCachePlan:
    """Choose anchors and repairs that fit the remaining hard deadline.

    The planner never claims feasibility when even the single-anchor survival path
    exceeds the measured budget. External inpaint and RIFE-like interpolation are
    optional repair passes, so missing backends do not affect the CPU fallback.
    """

    if deadline_seconds <= 0 or duration_seconds <= 0:
        raise ValueError("deadline_seconds and duration_seconds must be positive")
    if elapsed_seconds < 0:
        raise ValueError("elapsed_seconds must be non-negative")
    costs = costs or FlowCacheCosts()
    remaining = max(0.0, deadline_seconds - elapsed_seconds)
    usable = max(0.0, remaining - costs.safety_seconds)
    preferred_anchors = {"fast": 2, "fun": 3, "wow": 4}[mode]

    anchor_count = preferred_anchors
    while anchor_count > 1 and _base_cost(anchor_count, costs) > usable:
        anchor_count -= 1
    estimate = _base_cost(anchor_count, costs)
    feasible = estimate <= usable
    notes: list[str] = []
    if anchor_count < preferred_anchors:
        notes.append(f"締切に合わせてアンカーを{preferred_anchors}枚から{anchor_count}枚へ削減")
    if not feasible:
        notes.append("単一アンカーの安全経路も現在の実測予算を超過")

    pairs: list[PairRepairPlan] = []
    pair_count = max(0, anchor_count - 1)
    remaining_for_repairs = max(0.0, usable - estimate)
    enabled: list[RepairPass] = []

    for name, price in (
        ("cycle-consistency", costs.cycle_seconds_per_pair * pair_count),
        ("disocclusion-mask", costs.disocclusion_seconds_per_pair * pair_count),
    ):
        if pair_count and price <= remaining_for_repairs:
            enabled.append(name)  # type: ignore[arg-type]
            estimate += price
            remaining_for_repairs -= price

    if mode in {"fun", "wow"} and pair_count:
        inpaint_pairs = min(pair_count, int(remaining_for_repairs / costs.inpaint_seconds_per_pair))
    else:
        inpaint_pairs = 0
    if inpaint_pairs:
        estimate += inpaint_pairs * costs.inpaint_seconds_per_pair
        remaining_for_repairs -= inpaint_pairs * costs.inpaint_seconds_per_pair

    use_interpolation = (
        mode == "wow" and pair_count > 0 and costs.interpolation_seconds <= remaining_for_repairs
    )
    if use_interpolation:
        estimate += costs.interpolation_seconds

    for pair_index in range(pair_count):
        passes = list(enabled)
        if pair_index < inpaint_pairs:
            passes.append("external-inpaint")
        if use_interpolation:
            passes.append("external-interpolation")
        pairs.append(PairRepairPlan(pair_index, tuple(passes)))

    degraded = anchor_count < preferred_anchors or not feasible
    if inpaint_pairs < pair_count and mode in {"fun", "wow"}:
        notes.append("残り時間が少ない区間は外部inpaintを使わずCPU補修")
        degraded = True
    if mode == "wow" and not use_interpolation:
        notes.append("RIFE相当の補間を省略し、bilinear/parallaxへ切替")
        degraded = True

    fallback = "smart-cut" if not feasible or anchor_count == 1 else "bilinear-parallax"
    return FlowCachePlan(
        deadline_seconds=deadline_seconds,
        available_seconds=remaining,
        anchor_count=anchor_count,
        anchor_times=_anchor_times(anchor_count, duration_seconds),
        pair_repairs=tuple(pairs),
        estimated_seconds=round(estimate, 4),
        deadline_feasible=feasible,
        degraded=degraded,
        fallback_transition=fallback,
        notes=tuple(notes),
    )
