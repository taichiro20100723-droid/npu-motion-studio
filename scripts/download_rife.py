from __future__ import annotations

import argparse
import shutil
import tempfile
import urllib.request
import zipfile
from pathlib import Path

RELEASE_URL = (
    "https://github.com/nihui/rife-ncnn-vulkan/releases/download/20221029/"
    "rife-ncnn-vulkan-20221029-windows.zip"
)


def _safe_extract(archive: zipfile.ZipFile, destination: Path) -> None:
    destination = destination.resolve()
    for item in archive.infolist():
        target = (destination / item.filename).resolve()
        if destination not in target.parents and target != destination:
            raise ValueError(f"Unsafe archive member: {item.filename}")
    archive.extractall(destination)


def main() -> None:
    parser = argparse.ArgumentParser(description="Download RIFE Vulkan for Intel Arc GPU")
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    existing = next(args.destination.rglob("rife-ncnn-vulkan.exe"), None)
    if existing is not None:
        print(f"RIFE already ready: {existing}")
        return

    args.destination.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="nms-rife-download-") as temporary:
        archive_path = Path(temporary) / "rife.zip"
        request = urllib.request.Request(RELEASE_URL, headers={"User-Agent": "NPU-Motion-Studio"})
        with (
            urllib.request.urlopen(request, timeout=60) as response,
            archive_path.open("wb") as file,
        ):
            shutil.copyfileobj(response, file)
        with zipfile.ZipFile(archive_path) as archive:
            _safe_extract(archive, args.destination)

    executable = next(args.destination.rglob("rife-ncnn-vulkan.exe"), None)
    if executable is None:
        raise RuntimeError("RIFE executable was not found after extraction")
    print(f"RIFE ready: {executable}")


if __name__ == "__main__":
    main()
