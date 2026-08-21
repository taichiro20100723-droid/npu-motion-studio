from __future__ import annotations

import re
from enum import StrEnum
from pathlib import Path


class ActionKind(StrEnum):
    DANCE = "dance"
    BUILD = "build"
    DRIVE = "drive"
    RUN = "run"
    FLY = "fly"
    TRANSFORM = "transform"
    FLOW = "flow"
    CAMERA = "camera"


_ACTION_TERMS: dict[ActionKind, tuple[str, ...]] = {
    ActionKind.DANCE: ("ダンス", "踊", "舞う", "dance", "dancing"),
    ActionKind.BUILD: (
        "建て",
        "建って",
        "建築",
        "組み立て",
        "完成していく",
        "build",
        "construct",
        "assemble",
    ),
    ActionKind.DRIVE: ("走らせ", "走行", "運転", "ドリフト", "drive", "driving", "drift"),
    ActionKind.RUN: ("走", "駆け", "歩", "run", "running", "walk", "walking"),
    ActionKind.FLY: ("飛ぶ", "飛行", "浮遊", "fly", "flying", "floating"),
    ActionKind.TRANSFORM: ("変身", "変形", "進化", "崩壊", "爆発", "transform", "morph"),
    ActionKind.FLOW: ("流れる", "波", "炎", "煙", "雲", "flow", "wave", "fire", "smoke"),
    ActionKind.CAMERA: ("カメラ", "ズーム", "旋回", "camera", "zoom", "orbit"),
}

_FALLBACK_TERMS = (
    ("巨大ロボット", "giant robot"),
    ("ロボット", "robot"),
    ("未来都市", "futuristic city"),
    ("ネオン街", "neon city street"),
    ("ビル", "skyscraper"),
    ("建物", "building"),
    ("自動車", "car"),
    ("車", "car"),
    ("宇宙船", "spaceship"),
    ("電車", "train"),
    ("人物", "person"),
    ("女性", "woman"),
    ("男性", "man"),
    ("少女", "girl"),
    ("少年", "boy"),
    ("猫", "cat"),
    ("犬", "dog"),
    ("狐", "fox"),
    ("竜", "dragon"),
    ("雨", "rain"),
    ("夜", "night"),
    ("海", "ocean"),
    ("森", "forest"),
    ("街", "city"),
    ("踊る", "dancing"),
    ("ダンス", "dancing"),
    ("走る", "running fast"),
    ("走らせる", "driving fast"),
    ("建てる", "being constructed"),
    ("組み立てる", "being assembled"),
    ("変身する", "transforming"),
    ("左から右", "moving clearly from the left side to the right side"),
    ("高速", "at high speed with strong motion blur"),
    ("激しく", "energetic and intense motion"),
    ("大きく", "large clearly visible movement"),
    ("両手", "both arms"),
    ("両足", "both legs"),
    ("ジャンプ", "jumping high"),
    ("回転", "spinning"),
    ("基礎", "foundation stage"),
    ("骨組み", "structural frame stage"),
    ("外壁", "exterior wall stage"),
    ("完成", "final completed stage"),
    ("左右", "side-to-side movement"),
    ("揺れ", "strong camera shake"),
    ("ズーム", "camera zoom forward"),
    ("映画的", "cinematic"),
    ("写実的", "photorealistic"),
    ("アニメ", "anime"),
)


def contains_japanese(text: str) -> bool:
    return bool(re.search(r"[\u3040-\u30ff\u3400-\u9fff]", text))


def classify_action(text: str) -> ActionKind:
    normalized = text.casefold()
    vehicle_terms = ("車", "自動車", "バイク", "電車", "列車", "car", "vehicle", "train")
    vehicle_motion = ("走", "運転", "ドリフト", "drive", "driving", "race", "drift")
    if any(term in normalized for term in vehicle_terms) and any(
        term in normalized for term in vehicle_motion
    ):
        return ActionKind.DRIVE
    for action, terms in _ACTION_TERMS.items():
        if any(term.casefold() in normalized for term in terms):
            return action
    return ActionKind.CAMERA


def fallback_translate(text: str) -> str:
    parts = [english for japanese, english in _FALLBACK_TERMS if japanese in text]
    action = classify_action(text)
    if not parts:
        parts.append("a detailed cinematic scene")
    parts.append(
        {
            ActionKind.DANCE: "performing a clear energetic full-body dance",
            ActionKind.BUILD: "being visibly constructed step by step",
            ActionKind.DRIVE: "moving quickly across the scene",
            ActionKind.RUN: "running with clear full-body motion",
            ActionKind.FLY: "flying dynamically through the scene",
            ActionKind.TRANSFORM: "undergoing a dramatic visible transformation",
            ActionKind.FLOW: "flowing with strong organic motion",
            ActionKind.CAMERA: "with cinematic camera motion",
        }[action]
    )
    return ", ".join(dict.fromkeys(parts))


def compact_prompt(text: str, max_words: int = 30) -> str:
    """Keep the user's subject and the final action hints inside CLIP's short context."""

    words = text.replace("\n", " ").split()
    if len(words) <= max_words:
        return " ".join(words)
    tail_count = max(6, max_words // 3)
    head_count = max_words - tail_count
    return " ".join([*words[:head_count], *words[-tail_count:]])


class LocalPromptTranslator:
    """Offline Japanese-to-English translator with a deterministic fallback."""

    def __init__(self, model_directory: Path) -> None:
        self.model_directory = model_directory
        self._tokenizer = None
        self._model = None

    @property
    def available(self) -> bool:
        return (self.model_directory / "config.json").is_file()

    @property
    def ready(self) -> bool:
        return self._tokenizer is not None and self._model is not None

    def prepare(self) -> None:
        if self.ready or not self.available:
            return
        from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

        self._tokenizer = AutoTokenizer.from_pretrained(
            self.model_directory, local_files_only=True
        )
        self._model = AutoModelForSeq2SeqLM.from_pretrained(
            self.model_directory, local_files_only=True
        )
        self._model.eval()

    def translate(self, text: str) -> str:
        cleaned = text.strip()
        if not cleaned:
            return "a strange beautiful futuristic scene"
        if not contains_japanese(cleaned):
            return cleaned
        if not self.ready:
            return fallback_translate(cleaned)

        import torch

        encoded = self._tokenizer(
            [cleaned], return_tensors="pt", truncation=True, max_length=256
        )
        with torch.inference_mode():
            tokens = self._model.generate(
                **encoded,
                max_new_tokens=160,
                num_beams=4,
                renormalize_logits=True,
            )
        translated = self._tokenizer.batch_decode(tokens, skip_special_tokens=True)[0].strip()
        fallback = fallback_translate(cleaned)
        if not translated:
            return fallback
        return f"{translated}, {fallback}"
