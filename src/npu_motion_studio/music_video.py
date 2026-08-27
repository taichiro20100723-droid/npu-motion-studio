"""Audio-aware storyboard helpers for the local music-video workflow.

The module deliberately has no model dependency.  It creates an editable,
deterministic cut list from a WAV file so the same timing can be used by the
desktop app, the command-line builder, and future lyric/LRC input.
"""

from __future__ import annotations

import math
import re
import wave
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np


@dataclass(frozen=True, slots=True)
class MusicCut:
    index: int
    start_seconds: float
    end_seconds: float
    energy: float
    energy_band: str
    prompt: str
    lyric: str = ""

    @property
    def duration_seconds(self) -> float:
        return max(0.1, self.end_seconds - self.start_seconds)

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


# These scenes are object/architecture-led on purpose.  Avoiding human bodies
# is more reliable than trying to repair an unsafe frame after generation.
SCENES: tuple[str, ...] = (
    "a Japanese coastal high-school campus gate at golden hour, red running track, no people",
    "the school's courtyard with handmade cultural-festival banners, empty and quiet",
    "a bright school festival stage with colored lights and instruments, empty stage, no people",
    (
        "an empty science classroom prepared for a festival exhibit, circuit boards and glowing "
        "diagrams, no real people"
    ),
    (
        "aerial view of the coastal school and town at sunset, festival lights beginning to glow, "
        "no people visible"
    ),
    "a library aisle decorated with paper stars for the school festival, no people",
    "a gymnasium with handmade stalls and streamers, empty, no people",
    (
        "a close-up of school festival wristbands, paint, and colorful craft materials on a table, "
        "no people"
    ),
    (
        "the school entrance at blue hour with lanterns and a glowing festival poster, no people "
        "visible"
    ),
    "a close-up of a festival drum kit under blue stage lights, empty stage, no people",
    (
        "a rooftop view toward the sea with school pennants moving in the wind, no people visible"
    ),
    "a science display table with glowing diagrams and handmade labels, empty classroom, no people",
    (
        "festival confetti and colored paper shapes swirling through an empty classroom, no people"
    ),
    "a festival electric guitar and amplifier under warm stage lights, empty stage, no people",
    (
        "an empty auditorium with a single spotlight, handmade banners, and a polished floor, no "
        "people"
    ),
    "school club posters and chalk drawings transforming across a hallway, no people visible",
    "a table of decorated festival snacks and handmade price cards, no people",
    (
        "the school field and coastline under dramatic clouds, festival flags rippling, no people "
        "visible"
    ),
    "an empty festival stage with a large handmade banner and warm spotlights, no people",
    (
        "lanterns leading from the school gate toward the festival hall at night, no people visible"
    ),
    (
        "the school campus returning at dawn after the festival, warm windows and calm sea, no "
        "people visible"
    ),
)

SAFE_SUFFIX = (
    "cinematic album music-video shot, strong parallax and camera movement, "
    "dramatic but elegant lighting, highly detailed, abstract atmosphere, "
    "no people, no human figure, no face, no body, no skin, no nudity, no exposed body, "
    "no erotic imagery, no real-person likeness, no watermark"
)


def _read_wav(path: Path) -> tuple[int, np.ndarray]:
    with wave.open(str(path), "rb") as source:
        sample_rate = source.getframerate()
        channels = source.getnchannels()
        sample_width = source.getsampwidth()
        if sample_width != 2:
            raise ValueError("WAVは16-bit PCMにしてください")
        raw = source.readframes(source.getnframes())
    samples = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
    if channels > 1:
        samples = samples.reshape(-1, channels).mean(axis=1)
    return sample_rate, samples


def _parse_lrc(path: Path | None) -> list[tuple[float, str]]:
    if path is None or not path.is_file():
        return []
    timestamp = re.compile(r"\[(\d+):(\d+(?:\.\d+)?)\]")
    entries: list[tuple[float, str]] = []
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        stamps = timestamp.findall(line)
        text = timestamp.sub("", line).strip()
        for minutes, seconds in stamps:
            entries.append((int(minutes) * 60 + float(seconds), text))
    return sorted(entries)


def _lyric_for(entries: list[tuple[float, str]], start: float) -> str:
    active = [text for timestamp, text in entries if timestamp <= start and text]
    return active[-1] if active else ""


def build_storyboard(
    wav_path: Path,
    *,
    cut_seconds: float = 8.0,
    lrc_path: Path | None = None,
) -> list[MusicCut]:
    """Return fixed-duration cuts with an audio-energy motion hint.

    A lyric file is optional.  Without one, the same cut timing remains useful
    and is driven by the actual music's energy instead of inventing lyrics.
    """
    if cut_seconds <= 0:
        raise ValueError("カット秒数は0より大きくしてください")
    sample_rate, samples = _read_wav(wav_path)
    duration = len(samples) / sample_rate
    count = max(1, math.ceil(duration / cut_seconds))
    rms_values: list[float] = []
    for index in range(count):
        start = round(index * cut_seconds, 6)
        end = min(duration, (index + 1) * cut_seconds)
        left = int(start * sample_rate)
        right = max(left + 1, int(end * sample_rate))
        chunk = samples[left:right]
        rms_values.append(float(np.sqrt(np.mean(np.square(chunk)))))
    low, high = (
        np.percentile(rms_values, [25, 75])
        if len(rms_values) > 1
        else (rms_values[0], rms_values[0])
    )
    lyric_entries = _parse_lrc(lrc_path)
    cuts: list[MusicCut] = []
    for index, energy in enumerate(rms_values):
        start = index * cut_seconds
        end = min(duration, (index + 1) * cut_seconds)
        if energy >= high:
            band = "peak"
            movement = "rapid orbiting camera, energetic light pulses"
        elif energy <= low:
            band = "quiet"
            movement = "slow forward drift, gentle floating particles"
        else:
            band = "pulse"
            movement = "steady dolly movement, rhythmic light breathing"
        prompt = f"{SCENES[index % len(SCENES)]}, {movement}, {SAFE_SUFFIX}"
        cuts.append(
            MusicCut(
                index=index + 1,
                start_seconds=round(start, 3),
                end_seconds=round(end, 3),
                energy=round(energy, 6),
                energy_band=band,
                prompt=prompt,
                lyric=_lyric_for(lyric_entries, start),
            )
        )
    return cuts
