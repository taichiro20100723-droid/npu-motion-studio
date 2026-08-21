from __future__ import annotations

from concurrent.futures import Future, ThreadPoolExecutor
from pathlib import Path

from npu_motion_studio.domain import MotionRequest
from npu_motion_studio.engines.base import MotionEngine
from npu_motion_studio.jobs import Job, JobStore
from npu_motion_studio.scheduler import DeadlineScheduler


class GenerationService:
    def __init__(
        self,
        engine: MotionEngine,
        store: JobStore,
        output_directory: Path,
        deadline_seconds: float,
    ) -> None:
        self.engine = engine
        self.store = store
        self.output_directory = output_directory.resolve()
        self.deadline_seconds = deadline_seconds
        self._executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="motion-engine")
        self._preparation: Future[None] | None = None

    def prepare_async(self) -> None:
        if self._preparation is None:
            self._preparation = self._executor.submit(self.engine.prepare)

    @property
    def ready(self) -> bool:
        if self._preparation is None:
            return self.engine.ready
        return self._preparation.done() and self._preparation.exception() is None

    @property
    def preparation_error(self) -> str | None:
        if self._preparation is None or not self._preparation.done():
            return None
        error = self._preparation.exception()
        return None if error is None else f"{type(error).__name__}: {error}"

    def submit(self, request: MotionRequest) -> Job:
        job = self.store.add(Job.create())
        self._executor.submit(self._run, job.id, request)
        return job

    def _run(self, job_id: str, request: MotionRequest) -> None:
        self.store.update(job_id, state="running", message="準備しています")
        scheduler = DeadlineScheduler(self.deadline_seconds)

        def progress(stage: str, percent: int, message: str) -> None:
            self.store.update(
                job_id,
                stage=stage,
                progress=max(0, min(100, percent)),
                message=message,
            )

        try:
            artifact = self.engine.generate(
                request,
                self.output_directory,
                scheduler,
                progress,
            )
            self.store.update(
                job_id,
                state="completed",
                stage="completed",
                progress=100,
                message="できました",
                artifact_path=artifact.path.resolve(),
                media_type=artifact.media_type,
                elapsed_seconds=round(artifact.elapsed_seconds, 3),
                degraded=artifact.degraded,
                notes=artifact.notes,
            )
        except Exception as exc:  # noqa: BLE001 - job failures are isolated from the web server
            self.store.update(
                job_id,
                state="failed",
                stage="failed",
                message="生成に失敗しました",
                error=f"{type(exc).__name__}: {exc}",
            )

    def shutdown(self) -> None:
        self._executor.shutdown(wait=False, cancel_futures=True)
