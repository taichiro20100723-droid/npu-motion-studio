from __future__ import annotations

import threading
import uuid
from collections import OrderedDict
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal

JobState = Literal["queued", "running", "completed", "failed"]


@dataclass(slots=True)
class Job:
    id: str
    state: JobState = "queued"
    stage: str = "queued"
    progress: int = 0
    message: str = "順番を待っています"
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    artifact_path: Path | None = None
    media_type: str | None = None
    elapsed_seconds: float | None = None
    degraded: bool = False
    notes: tuple[str, ...] = ()
    error: str | None = None
    kind: str = "final"
    upgrade_available: bool = False
    upgrade_anchor_count: int | None = None
    source_job_id: str | None = None

    @classmethod
    def create(
        cls,
        *,
        kind: str = "final",
        upgrade_anchor_count: int | None = None,
        source_job_id: str | None = None,
    ) -> Job:
        return cls(
            id=uuid.uuid4().hex,
            kind=kind,
            upgrade_anchor_count=upgrade_anchor_count,
            source_job_id=source_job_id,
        )

    def public_dict(self) -> dict[str, object]:
        data = asdict(self)
        data.pop("artifact_path")
        data["artifact_url"] = f"/api/jobs/{self.id}/artifact" if self.artifact_path else None
        return data


class JobStore:
    def __init__(self, max_jobs: int = 30) -> None:
        self._max_jobs = max_jobs
        self._jobs: OrderedDict[str, Job] = OrderedDict()
        self._lock = threading.RLock()

    def add(self, job: Job) -> Job:
        with self._lock:
            self._jobs[job.id] = job
            while len(self._jobs) > self._max_jobs:
                self._jobs.popitem(last=False)
        return job

    def get(self, job_id: str) -> Job | None:
        with self._lock:
            return self._jobs.get(job_id)

    def update(self, job_id: str, **changes: object) -> Job:
        with self._lock:
            job = self._jobs[job_id]
            for name, value in changes.items():
                if not hasattr(job, name):
                    raise AttributeError(name)
                setattr(job, name, value)
            return job
