from __future__ import annotations

import wave
from pathlib import Path

import numpy as np

from npu_motion_studio.music_video import SAFE_SUFFIX, build_storyboard


def _write_wav(path: Path) -> None:
    sample_rate = 8_000
    first = (0.05 * np.sin(np.arange(sample_rate) * 2 * np.pi * 220 / sample_rate)).astype(
        np.float32
    )
    second = (0.4 * np.sin(np.arange(sample_rate) * 2 * np.pi * 220 / sample_rate)).astype(
        np.float32
    )
    samples = np.concatenate([first, second])
    with wave.open(str(path), "wb") as output:
        output.setnchannels(1)
        output.setsampwidth(2)
        output.setframerate(sample_rate)
        output.writeframes((samples * 32767).astype(np.int16).tobytes())


def test_storyboard_uses_audio_energy_and_safe_prompts(tmp_path: Path) -> None:
    wav_path = tmp_path / "song.wav"
    _write_wav(wav_path)
    cuts = build_storyboard(wav_path, cut_seconds=1.0)

    assert len(cuts) == 2
    assert cuts[0].energy < cuts[1].energy
    assert cuts[0].energy_band == "quiet"
    assert cuts[1].energy_band == "peak"
    assert "no nudity" in cuts[0].prompt
    assert "no people" in SAFE_SUFFIX


def test_storyboard_reads_optional_lrc(tmp_path: Path) -> None:
    wav_path = tmp_path / "song.wav"
    _write_wav(wav_path)
    lrc_path = tmp_path / "song.lrc"
    lrc_path.write_text("[00:00.00] start\n[00:01.00] peak", encoding="utf-8")

    cuts = build_storyboard(wav_path, cut_seconds=1.0, lrc_path=lrc_path)

    assert cuts[0].lyric == "start"
    assert cuts[1].lyric == "peak"
