from __future__ import annotations

from pathlib import Path

from npu_motion_studio.domain import MotionArtifact, MotionRequest
from npu_motion_studio.engines.base import EngineProbe, MotionEngine, ProgressCallback
from npu_motion_studio.scheduler import DeadlineScheduler


class OpenVINOPreviewEngine(MotionEngine):
    """Integration seam for the real NPU pipeline; generation is intentionally not faked."""

    key = "openvino-preview"

    def probe(self) -> EngineProbe:
        try:
            from openvino import Core  # type: ignore[import-not-found]

            devices = tuple(Core().available_devices)
        except (ImportError, RuntimeError, OSError):
            return EngineProbe("OpenVINO NPU（準備中）", False, "OpenVINOが未導入です", False)
        has_npu = any(str(device).upper().startswith("NPU") for device in devices)
        detail = (
            "NPUを検出しました。モデル接続は次の実装段階です"
            if has_npu
            else "NPUデバイスが見つかりません"
        )
        return EngineProbe("OpenVINO NPU（準備中）", False, detail, has_npu)

    def generate(
        self,
        request: MotionRequest,
        output_directory: Path,
        scheduler: DeadlineScheduler,
        progress: ProgressCallback,
    ) -> MotionArtifact:
        raise RuntimeError("OpenVINO engine is a documented integration seam, not implemented yet")
