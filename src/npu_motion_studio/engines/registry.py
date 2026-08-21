from __future__ import annotations

from npu_motion_studio.engines.base import MotionEngine
from npu_motion_studio.engines.mock import MockMotionEngine
from npu_motion_studio.engines.openvino_lcm import OpenVINOLCMEngine
from npu_motion_studio.engines.openvino_preview import OpenVINOPreviewEngine


def build_engine_registry() -> dict[str, MotionEngine]:
    engines: tuple[MotionEngine, ...] = (
        MockMotionEngine(),
        OpenVINOLCMEngine(),
        OpenVINOPreviewEngine(),
    )
    return {engine.key: engine for engine in engines}
