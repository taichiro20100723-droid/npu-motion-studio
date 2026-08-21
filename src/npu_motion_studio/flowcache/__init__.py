"""OpenCV-free temporal motion primitives for FlowCache Diffusion."""

from npu_motion_studio.flowcache.fields import (
    DenseMotionField,
    bilinear_warp,
    correlated_noise_fields,
    disocclusion_mask,
    forward_backward_cycle_consistency_mask,
)
from npu_motion_studio.flowcache.motion import MotionKind, MotionRoute, route_motion
from npu_motion_studio.flowcache.planner import FlowCachePlan, plan_flowcache

__all__ = [
    "DenseMotionField",
    "FlowCachePlan",
    "MotionKind",
    "MotionRoute",
    "bilinear_warp",
    "correlated_noise_fields",
    "disocclusion_mask",
    "forward_backward_cycle_consistency_mask",
    "plan_flowcache",
    "route_motion",
]
