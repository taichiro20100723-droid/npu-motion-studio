from __future__ import annotations

import threading
import webbrowser

import uvicorn

from npu_motion_studio.config import Settings


def main() -> None:
    settings = Settings.load()
    url = f"http://{settings.host}:{settings.port}"
    if settings.open_browser:
        threading.Timer(1.0, lambda: webbrowser.open(url)).start()
    uvicorn.run(
        "npu_motion_studio.app:create_app",
        factory=True,
        host=settings.host,
        port=settings.port,
        log_level="info",
    )
