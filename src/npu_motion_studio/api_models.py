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

    @field_validator("input_image_data_url", "target_image_data_url")
    @classmethod
    def validate_data_url(cls, value: str | None) -> str | None:
        if value is None:
            return value
        if not value.startswith("data:image/") or ";base64," not in value[:100]:
            raise ValueError("input image must be a base64 image data URL")
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
