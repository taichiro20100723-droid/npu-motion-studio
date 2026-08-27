"""Build an audio-synchronised MV from local NPU Motion Studio clips.

The script is intentionally beginner-friendly: give it a song/video and an
output filename.  It creates an editable storyboard, asks the running local
app for each NPU clip, then joins the clips with the original audio.
"""

from __future__ import annotations

import argparse
import base64
import json
import subprocess
import sys
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import ProxyHandler, Request, build_opener

import imageio_ffmpeg

from npu_motion_studio.music_video import MusicCut, build_storyboard

# Corporate/browser proxy variables can make a localhost request wait forever
# on Windows.  The MV builder only talks to the local app, so bypass proxies.
_LOCAL_OPENER = build_opener(ProxyHandler({}))


def _post_json(url: str, payload: dict[str, object]) -> dict[str, object]:
    body = json.dumps(payload).encode("utf-8")
    request = Request(url, data=body, headers={"Content-Type": "application/json"}, method="POST")
    with _LOCAL_OPENER.open(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def _get_json(url: str) -> dict[str, object]:
    with _LOCAL_OPENER.open(url, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def _download(url: str, path: Path) -> None:
    with _LOCAL_OPENER.open(url, timeout=120) as response:
        path.write_bytes(response.read())


def _image_data_url(path: Path) -> str:
    mime = "image/png" if path.suffix.casefold() == ".png" else "image/jpeg"
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{encoded}"


def _run(command: list[str]) -> None:
    completed = subprocess.run(command, check=False, capture_output=True, text=True)
    if completed.returncode:
        detail = (completed.stderr or completed.stdout)[-1200:]
        raise RuntimeError(f"ffmpegに失敗しました: {detail}")


def _extract_audio(ffmpeg: str, source: Path, wav: Path) -> None:
    _run(
        [
            ffmpeg,
            "-y",
            "-i",
            str(source),
            "-vn",
            "-ac",
            "1",
            "-ar",
            "16000",
            "-c:a",
            "pcm_s16le",
            str(wav),
        ]
    )


def _wait_for_job(api_url: str, job_id: str, *, timeout: float = 900.0) -> dict[str, object]:
    started = time.monotonic()
    last_message = ""
    while time.monotonic() - started < timeout:
        status = _get_json(f"{api_url}/api/jobs/{job_id}")
        message = f"{status.get('progress', 0)}% {status.get('message', '')}"
        if message != last_message:
            print(message, flush=True)
            last_message = message
        state = status.get("state")
        if state == "completed":
            return status
        if state == "failed":
            raise RuntimeError(str(status.get("error") or "NPU生成に失敗しました"))
        time.sleep(1.5)
    raise TimeoutError(f"ジョブの待ち時間が長すぎます: {job_id}")


def _generate_clip(
    api_url: str,
    cut: MusicCut,
    destination: Path,
    *,
    mode: str,
    anchors: int,
    style_image_data_url: str | None = None,
) -> None:
    prompt = cut.prompt
    if len(prompt) > 480:
        # The app accepts 500 characters; keep both the scene and safety tail.
        prompt = f"{prompt[:300]} ... {prompt[-175:]}"
    payload = {
        "prompt": prompt,
        "creation_mode": "animate",
        "mode": mode,
        "duration_seconds": round(cut.duration_seconds, 3),
        "seamless_loop": False,
        "input_image_data_url": style_image_data_url,
        "preview_first": False,
        "upgrade_anchor_count": anchors,
        "glyph_mode": False,
    }
    try:
        created = _post_json(f"{api_url}/api/jobs", payload)
    except (HTTPError, URLError) as exc:
        raise RuntimeError(f"ローカルアプリに接続できません: {exc}") from exc
    status = _wait_for_job(api_url, str(created["id"]))
    artifact_url = status.get("artifact_url") or f"/api/jobs/{created['id']}/artifact"
    artifact = (
        f"{api_url}{artifact_url}"
        if str(artifact_url).startswith("/")
        else str(artifact_url)
    )
    _download(artifact, destination)


def _write_storyboard(path: Path, cuts: list[MusicCut]) -> None:
    path.write_text(
        json.dumps([cut.as_dict() for cut in cuts], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _join_clips(
    ffmpeg: str,
    clips: list[Path],
    source: Path,
    output: Path,
    duration: float,
) -> None:
    list_path = output.with_suffix(".concat.txt")
    lines = [f"file '{clip.resolve().as_posix().replace("'", "'\\''")}'" for clip in clips]
    list_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    try:
        base = [
            ffmpeg, "-y", "-f", "concat", "-safe", "0", "-i", str(list_path), "-i", str(source),
            "-map", "0:v:0", "-map", "1:a:0", "-t", f"{duration:.3f}",
            "-c:v", "h264_qsv", "-global_quality", "18", "-look_ahead", "1",
            "-c:a", "aac", "-b:a", "256k", "-movflags", "+faststart", str(output),
        ]
        completed = subprocess.run(base, check=False, capture_output=True, text=True)
        if completed.returncode:
            fallback = [
                ffmpeg, "-y", "-f", "concat", "-safe", "0", "-i", str(list_path), "-i", str(source),
                "-map", "0:v:0", "-map", "1:a:0", "-t", f"{duration:.3f}",
                "-c:v", "libx264", "-preset", "medium", "-crf", "18",
                "-c:a", "aac", "-b:a", "256k", "-movflags", "+faststart", str(output),
            ]
            _run(fallback)
    finally:
        list_path.unlink(missing_ok=True)


def _make_photo_clip(ffmpeg: str, image: Path, destination: Path, duration: float) -> None:
    """Turn a real, face-free school background into a gentle moving shot."""
    frames = max(2, round(duration * 24))
    vf = (
        "scale=768:768:force_original_aspect_ratio=decrease,"
        "pad=768:768:(ow-iw)/2:(oh-ih)/2,"
        f"zoompan=z='min(zoom+0.0008,1.12)':d={frames}:s=768x768:fps=24,"
        "format=yuv420p"
    )
    qsv = [
        ffmpeg,
        "-y",
        "-loop",
        "1",
        "-i",
        str(image),
        "-t",
        f"{duration:.3f}",
        "-vf",
        vf,
        "-c:v",
        "h264_qsv",
        "-global_quality",
        "18",
        "-movflags",
        "+faststart",
        str(destination),
    ]
    completed = subprocess.run(qsv, check=False, capture_output=True, text=True)
    if completed.returncode:
        _run(
            [
                ffmpeg,
                "-y",
                "-loop",
                "1",
                "-i",
                str(image),
                "-t",
                f"{duration:.3f}",
                "-vf",
                vf,
                "-c:v",
                "libx264",
                "-preset",
                "medium",
                "-crf",
                "18",
                "-movflags",
                "+faststart",
                str(destination),
            ]
        )


def _duration_from_wav(wav: Path) -> float:
    import wave

    with wave.open(str(wav), "rb") as source:
        return source.getnframes() / source.getframerate()


def main() -> int:
    parser = argparse.ArgumentParser(description="曲に合わせたNPU MVを作る")
    parser.add_argument("source", type=Path, help="音声入りの動画または音声ファイル")
    parser.add_argument("--output", type=Path, default=None, help="完成MP4の保存先")
    parser.add_argument("--work-dir", type=Path, default=None, help="カット素材の保存先")
    parser.add_argument("--api-url", default="http://127.0.0.1:7862")
    parser.add_argument("--cut-seconds", type=float, default=8.0)
    parser.add_argument("--mode", choices=("fast", "fun", "wow"), default="fun")
    parser.add_argument("--anchors", type=int, choices=(8, 12, 16, 20, 24), default=12)
    parser.add_argument("--lrc", type=Path, default=None, help="任意の歌詞タイミング(.lrc)")
    parser.add_argument("--limit", type=int, default=None, help="試作時は先頭Nカットだけ作る")
    parser.add_argument("--start", type=int, default=1, help="開始カット番号（1始まり）")
    parser.add_argument("--end", type=int, default=None, help="終了カット番号（含む）")
    parser.add_argument(
        "--style-image",
        type=Path,
        default=None,
        help="安全な基準画像。指定すると各カットがこの絵から変化します",
    )
    parser.add_argument(
        "--backgrounds",
        type=Path,
        default=None,
        help="顔のない背景写真フォルダー。カットごとに順番に使います",
    )
    parser.add_argument(
        "--photo-every",
        type=int,
        default=0,
        help="何カットごとに元写真をそのまま入れるか（0=全カットNPU）",
    )
    parser.add_argument("--reuse", action="store_true", help="既存のカットを再利用する")
    args = parser.parse_args()
    source = args.source.resolve()
    if not source.is_file():
        parser.error(f"入力ファイルが見つかりません: {source}")
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    work_dir = (args.work_dir or source.with_name(f"{source.stem}-npu-mv")).resolve()
    clips_dir = work_dir / "clips"
    work_dir.mkdir(parents=True, exist_ok=True)
    clips_dir.mkdir(parents=True, exist_ok=True)
    wav = work_dir / "audio.wav"
    _extract_audio(ffmpeg, source, wav)
    cuts = build_storyboard(wav, cut_seconds=args.cut_seconds, lrc_path=args.lrc)
    storyboard_path = work_dir / "storyboard.json"
    _write_storyboard(storyboard_path, cuts)
    if args.start < 1 or args.start > len(cuts):
        parser.error(f"--startは1〜{len(cuts)}の範囲で指定してください")
    selected = cuts[args.start - 1 : args.end] if args.end else cuts[args.start - 1 :]
    if args.limit:
        selected = selected[: args.limit]
    style_image_data_url = None
    if args.style_image:
        style_image = args.style_image.resolve()
        if not style_image.is_file():
            parser.error(f"基準画像が見つかりません: {style_image}")
        style_image_data_url = _image_data_url(style_image)
    background_data_urls: list[str] = []
    background_paths: list[Path] = []
    if args.backgrounds:
        background_dir = args.backgrounds.resolve()
        if not background_dir.is_dir():
            parser.error(f"背景写真フォルダーが見つかりません: {background_dir}")
        background_paths = sorted(
            path
            for path in background_dir.iterdir()
            if path.suffix.casefold() in (".jpg", ".jpeg", ".png", ".webp")
        )
        if not background_paths:
            parser.error("背景写真フォルダーにjpg/png画像がありません")
        background_data_urls = [_image_data_url(path) for path in background_paths]
    print(f"カット表を作成: {storyboard_path} ({len(cuts)}カット)")
    for cut in selected:
        destination = clips_dir / f"cut-{cut.index:02d}.mp4"
        if args.reuse and destination.is_file():
            print(f"再利用: {destination.name}")
            continue
        photo_paths = [
            path
            for path in background_paths
            if path.suffix.casefold() in (".jpg", ".jpeg")
        ]
        if args.photo_every and photo_paths and (cut.index - 1) % args.photo_every == 0:
            photo = photo_paths[((cut.index - 1) // args.photo_every) % len(photo_paths)]
            print(f"[{cut.index}/{len(selected)}] 学校写真を使用: {photo.name}")
            _make_photo_clip(ffmpeg, photo, destination, cut.duration_seconds)
            continue
        print(
            f"[{cut.index}/{len(selected)}] NPU生成: {cut.energy_band} / "
            f"{cut.start_seconds:.1f}-{cut.end_seconds:.1f}秒"
        )
        _generate_clip(
            args.api_url.rstrip("/"),
            cut,
            destination,
            mode=args.mode,
            anchors=args.anchors,
            style_image_data_url=(
                background_data_urls[(cut.index - 1) % len(background_data_urls)]
                if background_data_urls
                else style_image_data_url
            ),
        )
    if args.limit:
        print("試作カットの生成が完了しました。--limitを外すと全編を作れます。")
        return 0
    output = (args.output or source.with_name(f"{source.stem}-NPU-MV.mp4")).resolve()
    clip_paths = [clips_dir / f"cut-{cut.index:02d}.mp4" for cut in cuts]
    _join_clips(ffmpeg, clip_paths, source, output, _duration_from_wav(wav))
    print(f"完成: {output}")
    print(f"編集用カット表: {storyboard_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
