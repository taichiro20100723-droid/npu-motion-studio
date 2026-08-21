from pathlib import Path

import pytest

from npu_motion_studio.config import Settings


def test_settings_environment_overrides(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    config = tmp_path / "config.json"
    config.write_text('{"port": 7000, "output_directory": "out"}', encoding="utf-8")
    monkeypatch.setenv("NMS_PORT", "7001")
    monkeypatch.setenv("NMS_OPEN_BROWSER", "false")

    settings = Settings.load(config)

    assert settings.port == 7001
    assert settings.open_browser is False
    assert settings.output_directory.is_absolute()


def test_settings_reject_invalid_port() -> None:
    with pytest.raises(ValueError, match="port"):
        Settings(port=0).validate()
