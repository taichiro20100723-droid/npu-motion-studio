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


# The scene order is an automatic visual journey.  Each cut is deliberately
# far from the previous one so the NPU has a clear destination to morph toward.
# The finished school MV keeps people out of the image inputs.  The local LCM
# model can ignore clothing instructions, so props and spaces are used for the
# dramatic transformations instead of trying to repair an unsafe human frame.
SCENES: tuple[str, ...] = (
    (
        "a Japanese coastal high-school campus gate at golden hour, red running track, "
        "wide establishing shot"
    ),
    "the school gate cracking open into a surreal paper-festival corridor, handmade banners flying",
    (
        "a bright school festival stage with colored lights, drums, and electric guitars, "
        "empty stage"
    ),
    (
        "a science classroom exploding into a kinetic festival exhibit, circuit boards and glowing "
        "diagrams, glowing wires and mechanical parts, empty classroom"
    ),
    (
        "aerial view of the coastal school and town at sunset, festival lights beginning to glow, "
        "a huge cinematic pullback over the sea"
    ),
    (
        "a library aisle decorated with paper stars, books spiralling into a festival stage, "
        "floating porcelain festival masks on pedestals, no people"
    ),
    (
        "a gymnasium transforming into a glowing market of handmade stalls and streamers, "
        "handmade stalls and streamers assembling themselves, no people"
    ),
    (
        "a close-up of school festival wristbands, paint, and colorful craft materials on a table, "
        "the materials assembling themselves into a miniature city"
    ),
    (
        "the school entrance at blue hour with lanterns and a glowing festival poster, no people "
        "visible, poster becoming a portal"
    ),
    (
        "a close-up of a festival drum kit under blue stage lights, drumbeats bending the "
        "architecture"
    ),
    (
        "a rooftop view toward the sea with school pennants moving in the wind, the ocean rising "
        "into the sky"
    ),
    (
        "a science display table with glowing diagrams and handmade labels, equations turning into "
        "constellations"
    ),
    (
        "festival confetti and colored paper shapes swirling through a classroom, no people"
    ),
    (
        "a festival electric guitar and amplifier under warm stage lights, sound waves becoming "
        "neon ribbons"
    ),
    (
        "an auditorium with a single spotlight and handmade banners, an original expressionist "
        "scream mask emerging from the floor, not a reproduction of any artwork"
    ),
    (
        "school club posters and chalk drawings transforming across a hallway, ink becoming living "
        "color and light, no people visible"
    ),
    (
        "a table of decorated festival snacks and handmade price cards, the table launching into a "
        "colorful food-festival vortex"
    ),
    (
        "the school field and coastline under dramatic clouds, festival flags ripping through the "
        "sky, flags and ribbons whipping through the air, no people"
    ),
    (
        "a festival stage with a large handmade banner and warm spotlights, fictional AI-generated "
        "empty stage and banners pulsing with the music, no people"
    ),
    (
        "lanterns leading from the school gate toward the festival hall at night, the path folding "
        "through impossible space"
    ),
    (
        "the school campus returning at dawn after the festival, warm windows and calm sea, the "
        "whole night dissolving into sunrise"
    ),
)

SAFE_SUFFIX = (
    "cinematic album music-video shot, extreme dynamic transformation, strong parallax, "
    "whip-pan, orbiting camera, snap zoom, perspective warp, liquid morph, light burst, "
    "dramatic but elegant lighting, highly detailed, abstract atmosphere, "
    "no people, no human figure, no face, no body, no skin, no breasts, no cleavage, no bikini, "
    "no lingerie, no bare torso, no exposed skin, no nudity, no erotic imagery, no gore, "
    "no real-person likeness, no watermark"
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
        destination = SCENES[index % len(SCENES)]
        origin = SCENES[(index - 1) % len(SCENES)] if index else "a blank dark frame"
        transition = (
            f"current destination shot: {destination}; automatically transform from the previous "
            f"shot ({origin}) into it, make the change obvious and continuous, carry one visual "
            "motif across the cut"
        )
        prompt = f"{transition}, {movement}, {SAFE_SUFFIX}"
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
