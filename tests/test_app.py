import time
from pathlib import Path

from fastapi.testclient import TestClient

from npu_motion_studio.app import create_app
from npu_motion_studio.config import Settings


def make_client(tmp_path: Path) -> TestClient:
    settings = Settings(
        output_directory=tmp_path,
        open_browser=False,
        deadline_seconds=10,
    )
    return TestClient(create_app(settings))


def test_health_and_home(tmp_path: Path) -> None:
    with make_client(tmp_path) as client:
        assert client.get("/api/health").json()["status"] == "ok"
        home = client.get("/")
        assert home.status_code == 200
        assert "NPU Motion Studio" in home.text
        assert 'id="advancedSettings"' in home.text
        assert 'id="seamlessLoop" type="checkbox"' in home.text
        assert 'id="resultVideo" autoplay muted loop controls playsinline' in home.text
        assert 'id="resultImage"' in home.text
        assert 'name="creationMode" value="transition" checked' in home.text
        assert 'name="creationMode" value="animate"' in home.text
        assert 'id="targetImageInput"' in home.text
        assert 'id="langJa"' in home.text
        assert 'id="langEn"' in home.text
        assert 'id="overlayText"' not in home.text
        assert 'id="motionBrush"' in home.text
        assert 'id="brushCanvas"' in home.text
        assert 'id="upgradePanel"' in home.text
        assert 'id="anchorCount" type="range" min="8" max="24" step="4" value="12"' in home.text
        assert 'data-i18n="upgradeAction"' in home.text


def test_ui_shows_elapsed_time_and_guards_duplicate_submits(tmp_path: Path) -> None:
    with make_client(tmp_path) as client:
        script = client.get("/app.js")
        assert script.status_code == 200
        assert 'fetch("/api/health"' in script.text
        assert "health.deadline_seconds" not in script.text
        assert "state.resultElapsed.toFixed(1)" in script.text
        assert "秒以内をめざして" not in script.text
        assert "if (state.busy) return" in script.text
        assert 'startsWith("video/")' in script.text
        assert 'startsWith("image/")' in script.text
        assert 'state.creationMode === "animate" && elements.seamlessLoop.checked' in script.text
        assert "creation_mode: state.creationMode" in script.text
        assert "target_image_data_url: state.targetImageDataUrl" in script.text
        assert "overlay_text" not in script.text
        assert 'applyLanguage("ja")' in script.text
        assert 'selectCreationMode("transition")' in script.text
        assert "prompt: elements.prompt.value" in script.text
        assert "deadlineSeconds: 10" not in script.text
        assert "preview_first: true" in script.text
        assert "upgrade_anchor_count:" in script.text
        assert "motion_mask_data_url:" in script.text
        assert "/upgrade`" in script.text


def test_job_lifecycle_and_artifact(tmp_path: Path) -> None:
    with make_client(tmp_path) as client:
        response = client.post(
            "/api/jobs",
            json={"prompt": "ネオンの街", "mode": "fast", "duration_seconds": 2},
        )
        assert response.status_code == 202
        job = response.json()
        for _ in range(30):
            job = client.get(f"/api/jobs/{job['id']}").json()
            if job["state"] in {"completed", "failed"}:
                break
            time.sleep(0.05)
        assert job["state"] == "completed"
        artifact = client.get(job["artifact_url"])
        assert artifact.status_code == 200
        assert artifact.headers["content-type"].startswith("image/svg+xml")
        assert job["kind"] == "preview"
        assert job["upgrade_available"] is True

        upgraded = client.post(f"/api/jobs/{job['id']}/upgrade", json={"anchor_count": 24})
        assert upgraded.status_code == 202
        upgraded_job = upgraded.json()
        assert upgraded_job["kind"] == "upgrade"
        assert upgraded_job["source_job_id"] == job["id"]


def test_npu_frame_count_uses_safe_four_frame_steps(tmp_path: Path) -> None:
    with make_client(tmp_path) as client:
        invalid = client.post(
            "/api/jobs", json={"prompt": "走る犬", "upgrade_anchor_count": 15}
        )
        assert invalid.status_code == 422
        accepted = client.post(
            "/api/jobs", json={"prompt": "走る犬", "upgrade_anchor_count": 16}
        )
        assert accepted.status_code == 202
        assert accepted.json()["upgrade_anchor_count"] == 16


def test_job_requires_prompt_or_image(tmp_path: Path) -> None:
    with make_client(tmp_path) as client:
        response = client.post("/api/jobs", json={"prompt": ""})
        assert response.status_code == 422


def test_transition_requires_both_a_and_b(tmp_path: Path) -> None:
    image = (
        "data:image/png;base64,"
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII="
    )
    with make_client(tmp_path) as client:
        missing_b = client.post(
            "/api/jobs",
            json={"creation_mode": "transition", "input_image_data_url": image},
        )
        assert missing_b.status_code == 422
        assert "AとB" in missing_b.json()["detail"]

        accepted = client.post(
            "/api/jobs",
            json={
                "creation_mode": "transition",
                "prompt": "ロボットが車へ変形する",
                "input_image_data_url": image,
                "target_image_data_url": image,
            },
        )
        assert accepted.status_code == 202
