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
        assert "NPU AI Video" in home.text
        assert 'id="advancedSettings"' in home.text
        assert 'id="seamlessLoop" type="checkbox"' in home.text
        assert 'id="resultVideo" autoplay muted loop controls playsinline' in home.text
        assert 'id="resultImage"' in home.text
        assert 'name="creationMode" value="transition" checked' in home.text
        assert 'name="creationMode" value="animate"' in home.text
        assert 'name="creationMode" value="glyph"' in home.text
        assert 'id="glyphEditor"' in home.text
        assert 'id="glyphImageDropzone"' in home.text
        assert 'id="glyphImageInput"' in home.text
        assert 'id="glyphResultExports"' in home.text
        assert 'id="targetImageInput"' in home.text
        assert 'id="langJa"' in home.text
        assert 'id="langEn"' in home.text
        assert 'id="jumpToCreator"' in home.text
        assert 'id="inspiration"' in home.text
        assert 'id="templateGrid"' in home.text
        assert 'data-template="robot"' in home.text
        assert 'data-template="neon"' in home.text
        assert 'data-template="glyph"' in home.text
        assert 'id="overlayText"' not in home.text
        assert 'id="motionBrush"' in home.text
        assert 'id="brushCanvas"' in home.text
        assert 'name="mode" value="fast"' in home.text
        assert 'name="mode" value="fun" checked' in home.text
        assert 'name="mode" value="wow"' in home.text
        assert 'id="upgradePanel"' not in home.text
        assert 'id="anchorCount"' not in home.text
        assert 'data-i18n="upgradeAction"' not in home.text


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
        assert 'state.creationMode === "transition" ? "transition" : "animate"' in script.text
        assert 'state.creationMode === "glyph"' in script.text
        assert (
            'target_image_data_url: state.creationMode === "transition" ? '
            'state.targetImageDataUrl : null'
        ) in script.text
        assert "overlay_text" not in script.text
        assert 'applyLanguage("ja")' in script.text
        assert 'selectCreationMode("transition")' in script.text
        assert "starterTemplates" in script.text
        assert "applyStarterTemplate" in script.text
        assert "scrollIntoView" in script.text
        assert "prompt: promptValue" in script.text
        assert 'glyph_mode: state.creationMode === "glyph"' in script.text
        assert "glyphCustomImageDataUrl" in script.text
        assert "character-sheet image" in script.text
        assert "deadlineSeconds: 10" not in script.text
        assert "preview_first: false" in script.text
        assert "upgrade_anchor_count:" in script.text
        assert "motion_mask_data_url:" in script.text
        assert "/upgrade`" not in script.text


def test_glyph_endpoint_serves_svg_text_and_font(tmp_path: Path) -> None:
    with make_client(tmp_path) as client:
        response = client.post("/api/glyphs", json={"text": "NPU MOTION", "style": "cyber"})
        assert response.status_code == 200
        data = response.json()
        assert data["glyph_id"]
        assert data["glyph_text"]
        assert "<svg" in data["svg"]
        assert "npu-character-sheet" in data["source_svg"]
        assert data["font_format"] == "ttf"
        assert client.get(data["svg_url"]).headers["content-type"].startswith("image/svg+xml")
        assert (
            client.get(data["source_svg_url"]).headers["content-type"].startswith("image/svg+xml")
        )
        assert client.get(data["text_url"]).status_code == 200
        assert client.get(data["font_url"]).headers["content-type"].startswith("font/ttf")


def test_job_lifecycle_and_artifact(tmp_path: Path) -> None:
    with make_client(tmp_path) as client:
        response = client.post(
            "/api/jobs",
            json={
                "prompt": "ネオンの街",
                "mode": "fast",
                "duration_seconds": 2,
                "preview_first": False,
                "upgrade_anchor_count": 8,
            },
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
        assert job["kind"] == "final"
        assert job["upgrade_available"] is False

        preview = client.post(
            "/api/jobs",
            json={"prompt": "ネオンの街", "preview_first": True},
        )
        assert preview.status_code == 202
        preview_job = preview.json()
        for _ in range(30):
            preview_job = client.get(f"/api/jobs/{preview_job['id']}").json()
            if preview_job["state"] in {"completed", "failed"}:
                break
            time.sleep(0.05)
        assert preview_job["kind"] == "preview"
        upgraded = client.post(f"/api/jobs/{preview_job['id']}/upgrade", json={"anchor_count": 24})
        assert upgraded.status_code == 202
        assert upgraded.json()["kind"] == "upgrade"


def test_npu_frame_count_uses_safe_four_frame_steps(tmp_path: Path) -> None:
    with make_client(tmp_path) as client:
        invalid = client.post(
            "/api/jobs",
            json={"prompt": "走る犬", "preview_first": True, "upgrade_anchor_count": 15},
        )
        assert invalid.status_code == 422
        accepted = client.post(
            "/api/jobs",
            json={"prompt": "走る犬", "preview_first": True, "upgrade_anchor_count": 16},
        )
        assert accepted.status_code == 202
        assert accepted.json()["upgrade_anchor_count"] == 16


def test_job_requires_prompt_or_image(tmp_path: Path) -> None:
    with make_client(tmp_path) as client:
        response = client.post("/api/jobs", json={"prompt": ""})
        assert response.status_code == 422


def test_glyph_job_accepts_empty_user_prompt(tmp_path: Path) -> None:
    image = (
        "data:image/png;base64,"
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII="
    )
    with make_client(tmp_path) as client:
        response = client.post(
            "/api/jobs",
            json={
                "prompt": "",
                "glyph_mode": True,
                "input_image_data_url": image,
                "creation_mode": "animate",
            },
        )
        assert response.status_code == 202


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
