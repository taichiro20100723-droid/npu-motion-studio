from __future__ import annotations

import unicodedata
from dataclasses import dataclass
from enum import StrEnum


class MotionKind(StrEnum):
    PERSON = "person"
    ANIMAL = "animal"
    VEHICLE = "vehicle"
    FLUID = "fluid"
    LANDSCAPE = "landscape"
    TRANSFORM = "transform"
    LOOP = "loop"


@dataclass(frozen=True, slots=True)
class MotionProfile:
    subject_motion: str
    camera_motion: str
    preferred_transition: str
    noise_correlation: float
    loop_safe: bool = False


@dataclass(frozen=True, slots=True)
class MotionRoute:
    kind: MotionKind
    confidence: float
    matched_terms: tuple[str, ...]
    profile: MotionProfile


_TERMS: dict[MotionKind, tuple[str, ...]] = {
    MotionKind.PERSON: (
        "人",
        "人物",
        "女の子",
        "男の子",
        "少女",
        "少年",
        "顔",
        "portrait",
        "person",
        "human",
        "woman",
        "man",
    ),
    MotionKind.ANIMAL: (
        "動物",
        "猫",
        "犬",
        "鳥",
        "魚",
        "竜",
        "ドラゴン",
        "animal",
        "cat",
        "dog",
        "bird",
        "dragon",
    ),
    MotionKind.VEHICLE: (
        "車",
        "電車",
        "列車",
        "飛行機",
        "宇宙船",
        "ロボット",
        "メカ",
        "vehicle",
        "car",
        "train",
        "aircraft",
        "spaceship",
        "mecha",
    ),
    MotionKind.FLUID: (
        "水",
        "海",
        "波",
        "川",
        "煙",
        "炎",
        "雲",
        "fluid",
        "water",
        "ocean",
        "wave",
        "smoke",
        "fire",
        "cloud",
    ),
    MotionKind.LANDSCAPE: (
        "風景",
        "山",
        "森",
        "街",
        "都市",
        "建物",
        "宇宙",
        "landscape",
        "mountain",
        "forest",
        "city",
        "building",
        "space",
    ),
    MotionKind.TRANSFORM: (
        "変身",
        "変形",
        "進化",
        "崩壊",
        "爆発",
        "transform",
        "morph",
        "evolve",
        "collapse",
        "explode",
    ),
    MotionKind.LOOP: (
        "ループ",
        "繰り返し",
        "往復",
        "呼吸",
        "点滅",
        "loop",
        "repeat",
        "boomerang",
        "breathe",
        "blink",
    ),
}

_PROFILES = {
    MotionKind.PERSON: MotionProfile("subtle-rigid", "portrait-dolly", "flow", 0.88),
    MotionKind.ANIMAL: MotionProfile("articulated", "follow", "flow", 0.82),
    MotionKind.VEHICLE: MotionProfile("rigid-fast", "tracking", "whip", 0.78),
    MotionKind.FLUID: MotionProfile("non-rigid", "slow-drift", "dissolve", 0.68),
    MotionKind.LANDSCAPE: MotionProfile("depth-layers", "ken-burns", "parallax", 0.9),
    MotionKind.TRANSFORM: MotionProfile("topology-change", "push-in", "flash-cut", 0.55),
    MotionKind.LOOP: MotionProfile("periodic", "orbit", "ping-pong", 0.94, loop_safe=True),
}

_TIE_PRIORITY = (
    MotionKind.LOOP,
    MotionKind.TRANSFORM,
    MotionKind.VEHICLE,
    MotionKind.ANIMAL,
    MotionKind.PERSON,
    MotionKind.FLUID,
    MotionKind.LANDSCAPE,
)


def route_motion(prompt: str, *, force: MotionKind | str | None = None) -> MotionRoute:
    """Route Japanese or English prompts to a deterministic motion strategy."""

    if force is not None:
        kind = MotionKind(force)
        return MotionRoute(kind, 1.0, (), _PROFILES[kind])

    normalized = unicodedata.normalize("NFKC", prompt).casefold()
    matches = {
        kind: tuple(term for term in terms if term.casefold() in normalized)
        for kind, terms in _TERMS.items()
    }
    scores = {
        kind: sum(1.0 + min(len(term), 12) / 12.0 for term in found)
        for kind, found in matches.items()
    }
    best_score = max(scores.values(), default=0.0)
    if best_score == 0.0:
        kind = MotionKind.LANDSCAPE
        return MotionRoute(kind, 0.2, (), _PROFILES[kind])

    kind = next(candidate for candidate in _TIE_PRIORITY if scores[candidate] == best_score)
    total_score = sum(scores.values())
    confidence = min(1.0, 0.45 + 0.55 * best_score / max(total_score, best_score))
    return MotionRoute(kind, round(confidence, 3), matches[kind], _PROFILES[kind])
