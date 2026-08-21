from __future__ import annotations

import os
import subprocess
import tempfile
import time
from pathlib import Path

import numpy as np
from PIL import Image

from npu_motion_studio.engines.video_pipeline import RgbFrame


def _runtime_root() -> Path:
    return Path(__file__).resolve().parents[3] / ".runtime"


class RifeVulkanInterpolator:
    """Portable RIFE runner that uses the Intel Arc GPU through Vulkan."""

    def __init__(self, tool_directory: Path | None = None) -> None:
        configured = os.environ.get("NMS_RIFE_DIRECTORY")
        self.tool_directory = (
            Path(configured)
            if configured
            else tool_directory or _runtime_root() / "tools" / "rife-ncnn-vulkan"
        )

    def _find(self, name: str) -> Path | None:
        if not self.tool_directory.is_dir():
            return None
        return next(self.tool_directory.rglob(name), None)

    @property
    def executable(self) -> Path | None:
        return self._find("rife-ncnn-vulkan.exe")

    @property
    def available(self) -> bool:
        return self.executable is not None

    def interpolate(
        self,
        anchors: list[RgbFrame],
        *,
        duration_seconds: float,
        fps: int,
    ) -> tuple[list[RgbFrame], float]:
        executable = self.executable
        if executable is None:
            raise RuntimeError("RIFE Vulkan is not installed")
        target_count = max(len(anchors), round(duration_seconds * fps))
        with tempfile.TemporaryDirectory(prefix="nms-rife-") as temporary:
            root = Path(temporary)
            input_directory = root / "input"
            output_directory = root / "output"
            input_directory.mkdir()
            output_directory.mkdir()
            for index, frame in enumerate(anchors):
                Image.fromarray(frame).save(input_directory / f"{index:08d}.png")

            command = [
                str(executable),
                "-i",
                str(input_directory),
                "-o",
                str(output_directory),
                "-n",
                str(target_count),
                "-m",
                "rife-v4.6",
                "-j",
                "2:3:2",
                "-f",
                "%08d.png",
            ]
            started = time.perf_counter()
            completed = subprocess.run(
                command,
                cwd=executable.parent,
                capture_output=True,
                text=True,
                timeout=180,
                check=False,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )
            elapsed = time.perf_counter() - started
            if completed.returncode != 0:
                detail = (completed.stderr or completed.stdout).strip()[-800:]
                raise RuntimeError(f"RIFE Vulkan failed ({completed.returncode}): {detail}")

            paths = sorted(output_directory.glob("*.png"))
            if len(paths) < 2:
                raise RuntimeError("RIFE Vulkan did not produce frames")
            frames = [
                np.ascontiguousarray(np.asarray(Image.open(path).convert("RGB"), dtype=np.uint8))
                for path in paths
            ]
            return frames, elapsed
