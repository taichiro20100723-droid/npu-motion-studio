import json

from npu_motion_studio.hardware import HardwareDetector


def test_windows_shape_parser(monkeypatch) -> None:
    monkeypatch.setattr("platform.system", lambda: "Windows")
    payload = json.dumps(
        {
            "npu": ["Intel(R) AI Boost"],
            "gpu": "Intel Arc 140V",
            "processor": "Core Ultra",
        }
    )
    detector = HardwareDetector(runner=lambda _: payload)

    info = detector.detect()

    assert info.processor == "Core Ultra"
    assert info.npu_devices == ("Intel(R) AI Boost",)
    assert info.gpu_devices == ("Intel Arc 140V",)


def test_bad_hardware_output_is_safe(monkeypatch) -> None:
    monkeypatch.setattr("platform.system", lambda: "Windows")
    info = HardwareDetector(runner=lambda _: "not json").detect()
    assert info.npu_devices == ()
    assert info.gpu_devices == ()
