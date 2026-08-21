from __future__ import annotations

import argparse
from pathlib import Path

from huggingface_hub import snapshot_download

MODEL_ID = "Helsinki-NLP/opus-mt-ja-en"
ALLOW_PATTERNS = (
    "config.json",
    "generation_config.json",
    "pytorch_model.bin",
    "source.spm",
    "target.spm",
    "tokenizer_config.json",
    "vocab.json",
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Download the local Japanese translator")
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    args.destination.mkdir(parents=True, exist_ok=True)
    path = snapshot_download(
        repo_id=MODEL_ID,
        local_dir=args.destination,
        allow_patterns=list(ALLOW_PATTERNS),
        max_workers=6,
    )
    print(f"Translation model ready: {path}")


if __name__ == "__main__":
    main()
