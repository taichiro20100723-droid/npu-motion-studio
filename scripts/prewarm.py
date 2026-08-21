from __future__ import annotations

import argparse
import os
import time
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Compile and cache the NPU pipeline once")
    parser.add_argument("model", type=Path)
    parser.add_argument("cache", type=Path)
    args = parser.parse_args()
    os.environ["NMS_MODEL_DIRECTORY"] = str(args.model.resolve())
    os.environ["NMS_COMPILE_CACHE_DIRECTORY"] = str(args.cache.resolve())

    from npu_motion_studio.engines.openvino_lcm import OpenVINOLCMEngine

    engine = OpenVINOLCMEngine()
    probe = engine.probe()
    if not probe.available:
        raise SystemExit(f"NPUエンジンを準備できません: {probe.detail}")
    print("初回だけNPUモデルを最適化します。数分かかる場合があります。")
    started = time.perf_counter()
    _, _, compile_seconds = engine._ensure_pipelines()  # noqa: SLF001 - setup entry point
    print(f"NPU最適化完了: {compile_seconds or time.perf_counter() - started:.2f}秒")


if __name__ == "__main__":
    main()
