from __future__ import annotations

import argparse
from pathlib import Path

from huggingface_hub import snapshot_download

MODEL_ID = "OpenVINO/LCM_Dreamshaper_v7-int8-ov"
ALLOW_PATTERNS = (
    "README.md",
    "model_index.json",
    "scheduler/*",
    "text_encoder/*",
    "tokenizer/*",
    "unet/*",
    "vae_decoder/*",
    "vae_encoder/*",
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Download the optional NPU image model")
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    args.destination.mkdir(parents=True, exist_ok=True)
    path = snapshot_download(
        repo_id=MODEL_ID,
        local_dir=args.destination,
        allow_patterns=list(ALLOW_PATTERNS),
        max_workers=8,
    )
    print(f"モデル準備完了: {path}")


if __name__ == "__main__":
    main()
