from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator


class GenerateRequest(BaseModel):
    prompt: str = Field(default="", max_length=500)
    creation_mode: Literal["animate", "transition"] = "animate"
    mode: Literal["fast", "fun", "wow"] = "fun"
    duration_seconds: float = Field(default=4.0, ge=2.0, le=10.0)
    seamless_loop: bool = True
    input_image_data_url: str | None = Field(default=None, max_length=7_000_000)
    target_image_data_url: str | None = Field(default=None, max_length=7_000_000)
    preview_first: bool = True
    upgrade_anchor_count: int = Field(default=12, ge=8, le=24)
    motion_mask_data_url: str | None = Field(default=None, max_length=7_000_000)
    lock_mask_data_url: str | None = Field(default=None, max_length=7_000_000)
    motion_vector_x: float = Field(default=0.0, ge=-1.0, le=1.0)
    motion_vector_y: float = Field(default=0.0, ge=-1.0, le=1.0)

    @field_validator(
        "input_image_data_url",
        "target_image_data_url",
        "motion_mask_data_url",
        "lock_mask_data_url",
    )
    @classmethod
    def validate_data_url(cls, value: str | None) -> str | None:
        if value is None:
            return value
        if not value.startswith("data:image/") or ";base64," not in value[:100]:
            raise ValueError("input image must be a base64 image data URL")
        return value

    @field_validator("upgrade_anchor_count")
    @classmethod
    def validate_anchor_step(cls, value: int) -> int:
        if value % 4:
            raise ValueError("NPU画像枚数は8から24まで、4枚単位で選んでください")
        return value


class UpgradeRequest(BaseModel):
    anchor_count: int | None = Field(default=None, ge=8, le=24)

    @field_validator("anchor_count")
    @classmethod
    def validate_anchor_step(cls, value: int | None) -> int | None:
        if value is not None and value % 4:
            raise ValueError("NPU画像枚数は8から24まで、4枚単位で選んでください")
        return value


class JobResponse(BaseModel):
    id: str
    state: str
    stage: str
    progress: int
    message: str
    created_at: str
    artifact_url: str | None
    media_type: str | None
    elapsed_seconds: float | None
    degraded: bool
    notes: list[str] | tuple[str, ...]
    error: str | None
    kind: str
    upgrade_available: bool
    upgrade_anchor_count: int | None
    source_job_id: str | None
