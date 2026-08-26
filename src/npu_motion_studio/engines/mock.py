from __future__ import annotations

import hashlib
import html
import math
import time
import uuid
from pathlib import Path

from npu_motion_studio.domain import MotionArtifact, MotionRequest
from npu_motion_studio.engines.base import EngineProbe, MotionEngine, ProgressCallback
from npu_motion_studio.scheduler import DeadlineScheduler


class MockMotionEngine(MotionEngine):
    key = "mock"

    def __init__(self, *, sleep: bool = True) -> None:
        self._sleep = sleep

    def probe(self) -> EngineProbe:
        return EngineProbe(
            name="内蔵デモ",
            available=True,
            detail="OpenVINOなしで画面を試せます（SVGプレビュー）",
            uses_npu=False,
        )

    def generate(
        self,
        request: MotionRequest,
        output_directory: Path,
        scheduler: DeadlineScheduler,
        progress: ProgressCallback,
    ) -> MotionArtifact:
        started = time.monotonic()
        stages = (
            ("image", 24, "絵を準備しています", 0.18),
            ("analysis", 46, "奥行きと主役を見つけています", 0.14),
            ("motion", 78, "動きを作っています", 0.24),
            ("encode", 94, "プレビューにまとめています", 0.12),
        )
        degraded = False
        notes: list[str] = ["これはNPUを使わないモック結果です"]
        for stage, percent, message, duration in stages:
            if not scheduler.can_start(duration):
                degraded = True
                notes.append(f"締切を守るため{stage}を短縮しました")
                continue
            progress(stage, percent, message)
            if self._sleep:
                time.sleep(duration)

        output_directory.mkdir(parents=True, exist_ok=True)
        artifact_path = output_directory / f"{uuid.uuid4().hex}.svg"
        artifact_path.write_text(self._render_svg(request), encoding="utf-8")
        progress("delivery", 100, "できました")
        return MotionArtifact(
            path=artifact_path,
            media_type="image/svg+xml",
            elapsed_seconds=time.monotonic() - started,
            degraded=degraded,
            notes=tuple(notes),
        )

    @staticmethod
    def _render_svg(request: MotionRequest) -> str:
        safe_prompt = html.escape(request.prompt.strip() or "言葉から生まれる景色")
        digest = hashlib.sha256(f"{request.prompt}:{request.mode}".encode()).digest()
        hue = int.from_bytes(digest[:2], "big") % 360
        hue2 = (hue + 75) % 360
        seconds = min(6.0, max(1.0, request.duration_seconds))
        amplitude = {"fast": 12, "fun": 24, "wow": 38}[request.mode]
        drift = math.ceil(seconds * 8)
        return f'''<svg xmlns="http://www.w3.org/2000/svg" width="768" height="432" viewBox="0 0 768 432" role="img" aria-label="{safe_prompt}">
  <defs>
    <linearGradient id="sky" x1="0" y1="0" x2="1" y2="1">
      <stop stop-color="hsl({hue} 72% 18%)"/>
      <stop offset="1" stop-color="hsl({hue2} 84% 54%)"/>
    </linearGradient>
    <filter id="glow"><feGaussianBlur stdDeviation="10"/></filter>
  </defs>
  <rect width="768" height="432" fill="url(#sky)"/>
  <g opacity=".45" filter="url(#glow)">
    <circle cx="150" cy="120" r="90" fill="hsl({hue2} 95% 70%)">
      <animate attributeName="cx" values="150;{150 + amplitude};150" dur="{seconds}s" repeatCount="indefinite"/>
    </circle>
    <circle cx="620" cy="300" r="125" fill="hsl({hue} 90% 65%)">
      <animate attributeName="cy" values="300;{300 - amplitude};300" dur="{seconds * .8:.2f}s" repeatCount="indefinite"/>
    </circle>
  </g>
  <g>
    <animateTransform attributeName="transform" type="translate" values="0 0;{-drift} -5;0 0" dur="{seconds}s" repeatCount="indefinite"/>
    <path d="M0 340 Q150 250 310 330 T768 290 V432 H0Z" fill="hsl({hue} 48% 14%)"/>
    <path d="M0 385 Q180 315 390 370 T768 335 V432 H0Z" fill="hsl({hue2} 55% 9%)"/>
  </g>
  <g transform="translate(384 215)">
    <circle r="68" fill="none" stroke="white" stroke-opacity=".72" stroke-width="2">
      <animate attributeName="r" values="60;76;60" dur="{seconds}s" repeatCount="indefinite"/>
      <animate attributeName="stroke-opacity" values=".3;.9;.3" dur="{seconds}s" repeatCount="indefinite"/>
    </circle>
    <path d="M-28 20 L0-34 L28 20 Z" fill="white" fill-opacity=".9"/>
  </g>
  <rect x="32" y="30" width="704" height="92" rx="18" fill="#050812" fill-opacity=".58"/>
  <text x="56" y="66" fill="white" font-family="'Yu Gothic UI',sans-serif" font-size="15" opacity=".7">NPU AI VIDEO / DEMO</text>
  <text x="56" y="101" fill="white" font-family="'Yu Gothic UI',sans-serif" font-size="25">{safe_prompt[:38]}</text>
</svg>'''
