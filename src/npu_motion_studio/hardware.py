from __future__ import annotations

import json
import platform
import subprocess
from collections.abc import Callable
from dataclasses import asdict, dataclass


@dataclass(frozen=True, slots=True)
class HardwareInfo:
    operating_system: str
    processor: str
    npu_devices: tuple[str, ...]
    gpu_devices: tuple[str, ...]
    openvino_installed: bool
    openvino_devices: tuple[str, ...]
    npu_ready: bool

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


CommandRunner = Callable[[list[str]], str]


def _run_command(command: list[str]) -> str:
    completed = subprocess.run(
        command,
        check=False,
        capture_output=True,
        text=True,
        timeout=5,
        encoding="utf-8",
        errors="replace",
    )
    return completed.stdout.strip()


class HardwareDetector:
    def __init__(self, runner: CommandRunner = _run_command) -> None:
        self._runner = runner

    def detect(self) -> HardwareInfo:
        npu_devices: tuple[str, ...] = ()
        gpu_devices: tuple[str, ...] = ()
        processor = platform.processor() or "Unknown processor"

        if platform.system() == "Windows":
            npu_devices, gpu_devices, detected_processor = self._detect_windows()
            processor = detected_processor or processor

        openvino_installed, openvino_devices = self._detect_openvino()
        npu_ready = any(device.upper().startswith("NPU") for device in openvino_devices)
        return HardwareInfo(
            operating_system=f"{platform.system()} {platform.release()}".strip(),
            processor=processor,
            npu_devices=npu_devices,
            gpu_devices=gpu_devices,
            openvino_installed=openvino_installed,
            openvino_devices=openvino_devices,
            npu_ready=npu_ready,
        )

    def _detect_windows(self) -> tuple[tuple[str, ...], tuple[str, ...], str | None]:
        script = (
            "$ErrorActionPreference='SilentlyContinue';"
            "$n=@(Get-PnpDevice -PresentOnly -Class ComputeAccelerator | "
            "Where-Object Status -eq 'OK' | ForEach-Object FriendlyName);"
            "$g=@(Get-CimInstance Win32_VideoController | ForEach-Object Name);"
            "$p=(Get-CimInstance Win32_Processor | Select-Object -First 1 -ExpandProperty Name);"
            "@{npu=$n;gpu=$g;processor=$p}|ConvertTo-Json -Compress"
        )
        try:
            raw = self._runner(["powershell", "-NoProfile", "-Command", script])
            data = json.loads(raw) if raw else {}
        except (OSError, subprocess.SubprocessError, json.JSONDecodeError):
            return (), (), None

        def names(value: object) -> tuple[str, ...]:
            if isinstance(value, str):
                return (value,)
            if isinstance(value, list):
                return tuple(str(item) for item in value if item)
            return ()

        return names(data.get("npu")), names(data.get("gpu")), data.get("processor")

    @staticmethod
    def _detect_openvino() -> tuple[bool, tuple[str, ...]]:
        try:
            from openvino import Core  # type: ignore[import-not-found]

            return True, tuple(str(device) for device in Core().available_devices)
        except (ImportError, RuntimeError, OSError):
            return False, ()
