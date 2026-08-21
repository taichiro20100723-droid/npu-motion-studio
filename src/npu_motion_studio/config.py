from __future__ import annotations

import json
import os
from dataclasses import dataclass, replace
from importlib.resources import files
from pathlib import Path
from typing import Any


def _as_bool(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True, slots=True)
class Settings:
    app_name: str = "NPU Motion Studio"
    host: str = "127.0.0.1"
    port: int = 7862
    engine: str = "mock"
    deadline_seconds: float = 180.0
    output_directory: Path = Path(".runtime/outputs")
    max_jobs: int = 30
    open_browser: bool = True

    @classmethod
    def load(cls, config_path: Path | None = None) -> Settings:
        source_root = Path(__file__).resolve().parents[2]
        in_source_checkout = (source_root / "pyproject.toml").is_file()
        base_directory = source_root if in_source_checkout else Path.cwd()
        values: dict[str, Any] = {}
        if config_path is not None:
            if config_path.exists():
                values = json.loads(config_path.read_text(encoding="utf-8"))
        else:
            source_config = source_root / "config" / "default.json"
            if source_config.exists():
                values = json.loads(source_config.read_text(encoding="utf-8"))
            else:
                bundled = files("npu_motion_studio").joinpath("default.json")
                values = json.loads(bundled.read_text(encoding="utf-8"))

        env_map: dict[str, tuple[str, Any]] = {
            "NMS_HOST": ("host", str),
            "NMS_PORT": ("port", int),
            "NMS_ENGINE": ("engine", str),
            "NMS_DEADLINE_SECONDS": ("deadline_seconds", float),
            "NMS_OUTPUT_DIRECTORY": ("output_directory", Path),
            "NMS_MAX_JOBS": ("max_jobs", int),
            "NMS_OPEN_BROWSER": ("open_browser", _as_bool),
        }
        for env_name, (field_name, converter) in env_map.items():
            if env_name in os.environ:
                values[field_name] = converter(os.environ[env_name])

        if "output_directory" in values:
            output = Path(values["output_directory"])
            values["output_directory"] = (
                output if output.is_absolute() else base_directory / output
            )

        settings = cls(**values)
        settings.validate()
        return settings

    def validate(self) -> None:
        if not 1 <= self.port <= 65535:
            raise ValueError("port must be between 1 and 65535")
        if not 1.0 <= self.deadline_seconds <= 1800.0:
            raise ValueError("deadline_seconds must be between 1 and 1800")
        if self.max_jobs < 1:
            raise ValueError("max_jobs must be positive")

    def with_overrides(self, **changes: Any) -> Settings:
        updated = replace(self, **changes)
        updated.validate()
        return updated
