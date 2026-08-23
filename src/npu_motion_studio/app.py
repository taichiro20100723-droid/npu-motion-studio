from __future__ import annotations

from contextlib import asynccontextmanager
from dataclasses import asdict
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from npu_motion_studio.api_models import (
    GenerateRequest,
    GlyphRequest,
    GlyphResponse,
    JobResponse,
    UpgradeRequest,
)
from npu_motion_studio.config import Settings
from npu_motion_studio.domain import MotionRequest
from npu_motion_studio.engines.registry import build_engine_registry
from npu_motion_studio.glyph_assets import create_glyph_assets, normalize_source
from npu_motion_studio.hardware import HardwareDetector
from npu_motion_studio.jobs import JobStore
from npu_motion_studio.service import GenerationService

PACKAGE_DIRECTORY = Path(__file__).resolve().parent
WEB_DIRECTORY = PACKAGE_DIRECTORY / "web"


def create_app(settings: Settings | None = None) -> FastAPI:
    resolved = settings or Settings.load()
    registry = build_engine_registry()
    if resolved.engine not in registry:
        raise ValueError(f"Unknown engine: {resolved.engine}. Choose from: {', '.join(registry)}")
    engine = registry[resolved.engine]
    probe = engine.probe()
    if not probe.available:
        raise RuntimeError(f"Engine '{resolved.engine}' is unavailable: {probe.detail}")

    store = JobStore(resolved.max_jobs)
    service = GenerationService(
        engine=engine,
        store=store,
        output_directory=resolved.output_directory,
        deadline_seconds=resolved.deadline_seconds,
    )
    hardware = HardwareDetector().detect()

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        service.prepare_async()
        yield
        service.shutdown()

    app = FastAPI(
        title=resolved.app_name,
        version="0.5.0",
        docs_url="/api/docs",
        redoc_url=None,
        lifespan=lifespan,
    )
    app.state.settings = resolved
    app.state.store = store
    app.state.service = service
    app.state.hardware = hardware

    @app.get("/api/health")
    def health() -> dict[str, object]:
        return {
            "status": "ok",
            "engine": resolved.engine,
            "engine_ready": service.ready,
            "engine_error": service.preparation_error,
            "deadline_seconds": resolved.deadline_seconds,
        }

    @app.get("/api/system")
    def system() -> dict[str, object]:
        return hardware.as_dict()

    @app.get("/api/engines")
    def engines() -> list[dict[str, object]]:
        return [
            {"key": key, **asdict(candidate.probe())}
            for key, candidate in registry.items()
        ]

    @app.post("/api/glyphs", response_model=GlyphResponse, status_code=200)
    def create_glyph(payload: GlyphRequest) -> dict[str, object]:
        assets = create_glyph_assets(resolved.output_directory, payload.text, payload.style)
        glyph_id = assets.svg_path.stem
        return {
            "glyph_id": glyph_id,
            "source_text": normalize_source(payload.text),
            "glyph_text": assets.glyph_text,
            "svg": assets.svg_text,
            "svg_url": f"/api/glyphs/{glyph_id}/svg",
            "source_svg": assets.source_svg_text,
            "source_svg_url": f"/api/glyphs/{glyph_id}/source",
            "text_url": f"/api/glyphs/{glyph_id}/text",
            "font_url": f"/api/glyphs/{glyph_id}/font" if assets.font_path else None,
            "font_format": assets.font_format,
        }

    @app.get("/api/glyphs/{glyph_id}/{asset_kind}")
    def glyph_asset(glyph_id: str, asset_kind: str) -> FileResponse:
        if len(glyph_id) != 20 or any(char not in "0123456789abcdef" for char in glyph_id):
            raise HTTPException(status_code=404, detail="グリフ素材が見つかりません")
        directory = resolved.output_directory.resolve() / "glyphs"
        candidates = {
            "svg": (directory / f"{glyph_id}.svg", "image/svg+xml"),
            "source": (directory / f"{glyph_id}-source.svg", "image/svg+xml"),
            "text": (directory / f"{glyph_id}.txt", "text/plain; charset=utf-8"),
        }
        if asset_kind == "font":
            matches = sorted(directory.glob(f"{glyph_id}-*.ttf"))
            candidate = (matches[0], "font/ttf") if matches else None
        else:
            candidate = candidates.get(asset_kind)
        if candidate is None or not candidate[0].is_file():
            raise HTTPException(status_code=404, detail="グリフ素材が見つかりません")
        return FileResponse(candidate[0], media_type=candidate[1], filename=candidate[0].name)

    @app.post("/api/jobs", response_model=JobResponse, status_code=202)
    def create_job(payload: GenerateRequest) -> dict[str, object]:
        if not service.ready:
            raise HTTPException(
                status_code=503,
                detail=(service.preparation_error or "NPUを準備しています。少し待ってください"),
            )
        if payload.creation_mode == "transition":
            if not payload.input_image_data_url or not payload.target_image_data_url:
                raise HTTPException(status_code=422, detail="AとBの画像を2枚とも選んでください")
        elif not payload.prompt.strip() and not payload.input_image_data_url:
            raise HTTPException(status_code=422, detail="文章を書くか画像を1枚選んでください")
        preview = payload.preview_first
        requested_mode = "fast" if preview else payload.mode
        requested_anchors = 4 if preview else payload.upgrade_anchor_count
        job = service.submit(
            MotionRequest(
                prompt=payload.prompt.strip(),
                creation_mode=payload.creation_mode,
                mode=requested_mode,
                duration_seconds=payload.duration_seconds,
                seamless_loop=payload.seamless_loop,
                input_image_data_url=payload.input_image_data_url,
                target_image_data_url=payload.target_image_data_url,
                anchor_count=requested_anchors,
                is_preview=preview,
                upgrade_anchor_count=payload.upgrade_anchor_count,
                motion_mask_data_url=payload.motion_mask_data_url,
                lock_mask_data_url=payload.lock_mask_data_url,
                motion_vector_x=payload.motion_vector_x,
                motion_vector_y=payload.motion_vector_y,
                glyph_mode=payload.glyph_mode,
            ),
            kind="preview" if preview else "final",
        )
        return job.public_dict()

    @app.post("/api/jobs/{job_id}/upgrade", response_model=JobResponse, status_code=202)
    def upgrade_job(job_id: str, payload: UpgradeRequest) -> dict[str, object]:
        try:
            job = service.upgrade(job_id, payload.anchor_count)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail="プレビューが見つかりません") from exc
        except ValueError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc
        return job.public_dict()

    @app.get("/api/jobs/{job_id}", response_model=JobResponse)
    def read_job(job_id: str) -> dict[str, object]:
        job = store.get(job_id)
        if job is None:
            raise HTTPException(status_code=404, detail="生成結果が見つかりません")
        return job.public_dict()

    @app.get("/api/jobs/{job_id}/artifact")
    def artifact(job_id: str) -> FileResponse:
        job = store.get(job_id)
        if job is None or job.artifact_path is None:
            raise HTTPException(status_code=404, detail="生成物がまだありません")
        candidate = job.artifact_path.resolve()
        output_root = resolved.output_directory.resolve()
        if candidate != output_root and output_root not in candidate.parents:
            raise HTTPException(status_code=403, detail="このファイルは配信できません")
        if not candidate.is_file():
            raise HTTPException(status_code=404, detail="生成物が見つかりません")
        return FileResponse(candidate, media_type=job.media_type, filename=candidate.name)

    app.mount("/", StaticFiles(directory=WEB_DIRECTORY, html=True), name="web")
    return app
