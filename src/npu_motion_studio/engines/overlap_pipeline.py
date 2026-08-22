from __future__ import annotations

import time
from concurrent.futures import Future, ThreadPoolExecutor

from npu_motion_studio.engines.rife_vulkan import RifeVulkanInterpolator
from npu_motion_studio.engines.video_pipeline import RgbFrame


def _interval_counts(total_frames: int, pair_count: int) -> tuple[int, ...]:
    if pair_count < 1:
        return ()
    base, remainder = divmod(max(1, total_frames - 1), pair_count)
    return tuple(max(1, base + (1 if index < remainder else 0)) for index in range(pair_count))


class OverlappedRifePipeline:
    """Queue each finished NPU interval on Arc while the next anchor is drawn."""

    def __init__(
        self,
        rife: RifeVulkanInterpolator,
        *,
        pair_count: int,
        total_frames: int,
        fps: int,
    ) -> None:
        self.rife = rife
        self.fps = fps
        self._counts = _interval_counts(total_frames, pair_count)
        self._executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="arc-rife")
        self._futures: list[Future[tuple[list[RgbFrame], float]]] = []
        self._closed = False

    def submit(self, first: RgbFrame, second: RgbFrame) -> None:
        index = len(self._futures)
        if index >= len(self._counts):
            raise RuntimeError("more interpolation pairs than planned")
        output_count = self._counts[index] + 1
        self._futures.append(
            self._executor.submit(
                self.rife.interpolate,
                [first, second],
                duration_seconds=output_count / self.fps,
                fps=self.fps,
            )
        )

    @property
    def submitted_count(self) -> int:
        return len(self._futures)

    @property
    def planned_count(self) -> int:
        return len(self._counts)

    def finish(self) -> tuple[list[RgbFrame], float, float]:
        wait_started = time.perf_counter()
        segments: list[list[RgbFrame]] = []
        gpu_work_seconds = 0.0
        try:
            for future in self._futures:
                frames, elapsed = future.result()
                segments.append(frames)
                gpu_work_seconds += elapsed
        finally:
            self.close()
        wait_seconds = time.perf_counter() - wait_started
        if len(segments) != len(self._counts):
            raise RuntimeError("not all planned NPU intervals reached the GPU")
        combined: list[RgbFrame] = []
        for index, frames in enumerate(segments):
            combined.extend(frames if index == len(segments) - 1 else frames[:-1])
        expected = sum(self._counts) + 1
        if len(combined) < expected:
            combined.extend(combined[-1].copy() for _ in range(expected - len(combined)))
        return combined[:expected], gpu_work_seconds, wait_seconds

    def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        self._executor.shutdown(wait=False, cancel_futures=True)
